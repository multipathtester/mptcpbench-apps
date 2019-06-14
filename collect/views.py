import datetime
import json
import pytz

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile, File
from django.db.transaction import atomic
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.defaulttags import register
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ipware.ip import get_ip

from . import forms, graph, models, query
from mptcpbench.benches.utils import get_bench_and_result_from_dict
from mptcpbench.benches.models import UndefinedBench
from mptcpbench.mptcpanalysis.tasks import analyze_trace, rewrite_pcap
from mptcpbench.msg.models import MsgDelayResult


# From http://stackoverflow.com/questions/8000022/
#      django-template-how-to-look-up-a-dictionary-value-with-a-variable
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@login_required
def index(request):
    return render(request, 'collect/index.html', {})


def sign_up(request):
    if request.method == "POST":
        form = forms.UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            login(request, new_user)
            # Redirect to the index page
            return index(request)
    else:
        form = forms.UserForm()

    return render(request, 'collect/sign_up.html', {'form': form})


def _check_required_fields_create_bench_test(test_dict):
    for field in ["bench", "client_analysis", "client_interfaces", "client_machine", "client_sysctl", "client_version",
                  "result", "start_time", "server_interfaces", "server_machine", "server_sysctl", "server_version",
                  "uuid"]:
        if field not in test_dict:
            raise Exception("Field " + field + " is missing")


# TODO to be modified
@atomic
def _create_bench_test(test_dict, bench, result_class):
    """ Create a new bench test based on metadata sent by the client, and return an identifier for the test """
    # This operation should be atomic to be both efficient with DB and consistent
    # Check if needed fields are there
    # TODO should we assume everything is known about the server with its URL?
    _check_required_fields_create_bench_test(test_dict)

    client_machine, _ = models.Machine.objects.get_or_create(**test_dict["client_machine"])
    client_sysctl, _ = models.Sysctl.get_or_create_sysctl_from_dict(test_dict["client_sysctl"])
    server_machine, _ = models.Machine.objects.get_or_create(**test_dict["server_machine"])
    server_sysctl, _ = models.Sysctl.get_or_create_sysctl_from_dict(test_dict["server_sysctl"])

    # We don't expect reusing the same results for two different tests
    result = models.Result(
        result_class.create_result_from_dict(test_dict["result"])
    )

    start_time = datetime.datetime.fromtimestamp(float(test_dict["start_time"]), tz=pytz.timezone("UTC"))

    # TODO need to be modified, to check if it is really a bench test
    test = models.BenchTest.objects.create(bench=bench, client_analysis=test_dict["client_analysis"],
                                           client_machine=client_machine, client_sysctl=client_sysctl,
                                           client_version=test_dict["client_version"], result=result.id,
                                           server_machine=server_machine, server_sysctl=server_sysctl,
                                           server_version=test_dict["server_version"], start_time=start_time,
                                           uuid=test_dict["uuid"])

    def get_or_create_interfaces(interfaces_attr, interfaces_key):
        interfaces = {}
        for interface_dict in test_dict[interfaces_key]:
            interface, interface_created = models.Interface.get_or_create_interface_from_dict(interface_dict)
            interfaces_attr.add(interface)
            interfaces[interface.name] = interface

        return interfaces

    client_interfaces = get_or_create_interfaces(test.client_interfaces, "client_interfaces")
    server_interfaces = get_or_create_interfaces(test.server_interfaces, "server_interfaces")

    if test.client_analysis:
        for mptcp_conn_id in test_dict["mptcp_conns"]:
            # Since TCP are linked to only one test, always create a new entry in DB
            models.MPTCPConnection.create_mptcp_conn_from_dict(test_dict["mptcp_conns"][mptcp_conn_id], mptcp_conn_id,
                                                               test, client_interfaces, server_interfaces)

    # We can now return an URL to store the trace
    test.client_trace = models.Trace.objects.create(is_client_trace=True, is_smartphone=False, is_undefined=False,
                                                    name=models.get_trace_path_from_test(test))
    test.server_trace = models.Trace.objects.create(is_client_trace=False, is_smartphone=False, is_undefined=False,
                                                    name=models.get_trace_path_from_test(test))
    test.save()
    return test, test.client_trace.name


def _check_required_fields_create_smartphone_test(test_dict):
    for field in ["bench", "config_name", "device_id", "result", "server_ip", "smartphone", "start_time"]:
        if field not in test_dict:
            raise Exception("Field " + field + " is missing")


@atomic
def _create_smartphone_test(test_dict, bench, result_class):
    """ Create a new smartphone test based on metadata sent by the client, and return an identifier for the test """
    # This operation should be atomic to be both efficient with DB and consistent
    # Check if needed fields are there
    _check_required_fields_create_smartphone_test(test_dict)
    result = models.Result(
        result_class.create_result_from_dict(test_dict["result"])
    )

    start_time = datetime.datetime.fromtimestamp(float(test_dict["start_time"]), tz=pytz.timezone('Europe/Brussels'))

    test = models.SmartphoneTest.objects.create(bench=bench, config_name=test_dict["config_name"],
                                                device_id=test_dict["device_id"], received_time=timezone.now(),
                                                result=result.id, server_ip=test_dict["server_ip"],
                                                start_time=start_time)

    # If a proto_info field is present, insert it
    if "proto_info" in test_dict:
        proto_info = models.ProtoInfo.objects.create(data=test_dict["proto_info"], test=test)
        proto_info.save()

    # It this test is part of a test group, record it
    if "group_start_time" in test_dict:
        group_start_time = datetime.datetime.fromtimestamp(float(test_dict["group_start_time"]), tz=pytz.timezone('Europe/Brussels'))
        test_group = models.SmartphoneTestGroup.objects.create(start_time=group_start_time, test=test)
        test_group.save()

    # We can now return an URL to store the trace
    test.client_trace = models.Trace.objects.create(is_client_trace=True, is_smartphone=True, is_undefined=False,
                                                    name=models.get_trace_path_from_test(test))
    test.server_trace = models.Trace.objects.create(is_client_trace=False, is_smartphone=True, is_undefined=False,
                                                    name=models.get_trace_path_from_test(test))
    test.save()
    return test, test.client_trace.name


def _create_no_test(test_dict, bench):
    # TODO probably more data to be processed here later
    test_dict.pop("bench", None)

    trace_user_name = test_dict.pop("trace_user_name", None)
    is_smartphone = test_dict.pop("smartphone", False) in ['true', 'True', 'TRUE']
    # uploader_email MUST be in test_dict
    test = models.NoTest.objects.create(bench=bench, time=timezone.now(), **test_dict)
    # By default, a trace is considered as a client trace, but can be changed later
    test.trace = models.Trace.objects.create(is_client_trace=is_smartphone, is_smartphone=is_smartphone,
                                             is_undefined=True, user_name=trace_user_name,
                                             name=models.get_trace_path_from_test(test))
    test.save()
    return test, test.trace.name


def _create_test(test_dict):
    # First determine which type of test we have
    bench_in_dict = "bench" in test_dict
    if not bench_in_dict:
        bench, _ = UndefinedBench.objects.get_or_create()
        return _create_no_test(test_dict, bench)

    # It's a bench test
    bench_dict = test_dict["bench"]
    bench_cl, result_cl = get_bench_and_result_from_dict(bench_dict)
    bench_config = bench_dict.get("config", {})
    bench, _ = bench_cl.objects.get_or_create(**bench_config)

    # Is it a smartphone test?
    if test_dict.get("smartphone", False):
        return _create_smartphone_test(test_dict, bench, result_cl)

    return _create_bench_test(test_dict, bench, result_cl)


# TODO to be adapted to accept other than bench tests
# It is not meant to be used in a browser, so no csrf token here
@csrf_exempt
def save_test(request):
    """ Action of server when client visits /save_test/ """
    if request.method == "POST":
        try:
            body_unicode = request.body.decode('utf-8')
            test_dict = json.loads(body_unicode)
            _, trace_store_path = _create_test(test_dict)
            return JsonResponse({'store_path': trace_store_path})
        except Exception as e:
            print(e)
            return JsonResponse({}, status=400)

    # Else, silently ignore it

    return JsonResponse({})


def _upload_trace(request, store_path, is_client_trace=False, is_undefined=False, is_smartphone=False, pcapfix_link_type=None):
    if request.method == "POST":
        if store_path:
            qs = models.Trace.objects.filter(is_client_trace=is_client_trace, name=store_path, is_undefined=is_undefined)
            print(qs, is_client_trace, store_path, is_undefined, is_smartphone)
            # Very unlikeky
            if qs.count() >= 1:
                qs.filter(is_smartphone=is_smartphone)
                print(qs, is_client_trace, store_path, is_undefined, is_smartphone)

            if qs.count() == 1:
                trace = qs[0]
                if not trace.file:
                    trace.file.save(trace.name, ContentFile(request.body))
                    # XXX Don't adapt trace.name to trace.file.name to avoid loosing the reference to the trace
                    # The real name can  still be found with trace.file.name
                    analyze_trace.delay(trace.file.name, trace.name, trace.is_client_trace,
                                        trace.is_undefined, trace.is_smartphone, pcapfix_link_type)
                    return JsonResponse({"result": "OK"})

    return JsonResponse({})


@csrf_exempt
def upload_client_trace(request, store_path):
    """ Action of server when client visits /upload_client_trace/ """
    return _upload_trace(request, store_path, is_client_trace=True, pcapfix_link_type=113)


@csrf_exempt
def upload_server_trace(request, store_path):
    """ Action of server when client visits /upload_server_trace/ """
    return _upload_trace(request, store_path, is_client_trace=False)


@csrf_exempt
def upload_undefined_trace(request, store_path):
    """ Action of server when client visits /upload_undefined_trace/ """
    return _upload_trace(request, store_path, is_undefined=True)


@csrf_exempt
def upload_smartphone_trace(request, store_path):
    """ This is called when a smartphone wants to send passive capture """
    return _upload_trace(request, store_path, is_undefined=True, is_smartphone=True, is_client_trace=True, pcapfix_link_type=113)


def get_next_experiments(request):
    """ Action of server when client visits /get_next_experiments/ """
    # TODO Need here to interact with test servers to prepare experiments ?
    response = [
        {
            "config": {
                "file_name": "random_10MB",
                "server_url": "multipath-tcp.org",
            },
            "name": "simple_http_get",
        }
    ]

    return JsonResponse(response, safe=False)


def get_public_ip(request):
    """ Action of server when client visits /get_public_ip/ """
    ip = get_ip(request)
    ip = ip if ip is not None else ""

    return JsonResponse({"public_ip": ip})


@login_required
def no_test_results(request, uploader_email):
    """ Action of server when client visits /no_test_results/<uploader_email>/ """
    if not request.user.is_superuser and not request.user.email == uploader_email:
        raise PermissionDenied

    test_list = models.NoTest.objects.filter(uploader_email=uploader_email)
    context = {
        'test_list': test_list,
        'uploader_email': uploader_email,
    }
    return render(request, 'collect/no_test_results.html', context)


def _results_details(**kwargs):
    (test, conns, count_conns_multipath, sff_res, sf_intermediate, sfs, additional_sfs, unused_sfs,
        additional_unused_sfs, cellular_sfs, cellular_unused_sfs, additional_cellular_sfs,
        additional_cellular_unused_sfs) = query.get_view_results_details(**kwargs)

    for e in sff_res:
        if e.pop('is_client_to_server'):
            c2s = e
        else:
            s2c = e

    # Two passes, not ideal but in Django, it's not possible to group by an aggregated field :-(
    sf_count = {}
    for sf_nb in sf_intermediate:
        sf_count[sf_nb['nb_subflows']] = sf_count.get(sf_nb['nb_subflows'], 0) + 1

    sf_count_list = []
    for sf_nb in sorted(sf_count.keys()):
        sf_count_list.append({'nb_sf': sf_nb, 'nb_conns': sf_count[sf_nb], 'perc_conns': '{:0.2f}'.format(100.0 * sf_count[sf_nb] / len(conns))})

    context = {
        'test': test,
        'count_conns': len(conns),
        'count_conns_multipath': count_conns_multipath,
        'perc_multipath_conns': '{0:.2f}'.format(100. * count_conns_multipath / len(conns)) if len(conns) else 'N/A',
        'count_sfs': len(sfs),
        'count_additional_sfs': len(additional_sfs),
        'perc_unused_sfs': '{0:.2f}'.format(100. * len(unused_sfs) / len(sfs)) if len(sfs) else 'N/A',
        'perc_additional_unused_sfs': '{0:.2f}'.format(100. * len(additional_unused_sfs) / len(additional_sfs)) if len(additional_sfs) else 'N/A',
        'count_cell_sfs': len(cellular_sfs),
        'count_additional_cell_sfs': len(additional_cellular_sfs),
        'perc_unused_cell_sfs': '{0:.2f}'.format(100. * len(cellular_unused_sfs) / len(cellular_sfs)) if len(cellular_sfs) else 'N/A',
        'perc_unused_additional_cell_sfs': ('{0:.2f}'.format(100. * len(additional_cellular_unused_sfs) / len(additional_cellular_sfs))
                                            if len(additional_cellular_sfs) else 'N/A'),
        'c2s': c2s,
        's2c': s2c,
        'sf_count_list': sf_count_list,
    }
    return context


@login_required
def no_test_results_details(request, uploader_email, test_id):
    """ Action of server when client visits /no_test_results/<uploader_email>/<test_id>/ """
    if not request.user.is_superuser and not request.user.email == uploader_email:
        raise PermissionDenied

    kwargs = {
        'no_test': True,
        'uploader_email': uploader_email,
        'test_id': test_id,
    }

    return render(request, 'collect/no_test_results_details.html', _results_details(**kwargs))


@login_required
def smartphone_passive_results_details(request, config_id, server_ip):
    if not request.user.is_superuser:
        raise PermissionDenied

    kwargs = {
        'no_test': True,
        'smartphone': True,
        'config_id': config_id,
        'server_ip': server_ip,
    }
    return render(request, 'collect/no_test_results_details.html', _results_details(**kwargs))


@login_required
def smartphone_results_graphs(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    return render(request, 'collect/smartphone_results_graphs.html', {})


def _get_graph(request, **kwargs):
    if request.method == "POST":
        graph_type = request.POST.get("graph_type", None)
        if graph_type:
            try:
                script, div = graph.get_bokeh_script_and_div(graph_type, **kwargs)
                return HttpResponse(json.dumps({'script': script, 'div': div}), content_type="application/json")
            except Exception as e:
                print(e)
                raise Http404


@login_required
def get_graph(request, uploader_email, test_id):
    if not request.user.is_superuser and not request.user.email == uploader_email:
        raise PermissionDenied

    kwargs = {
        'no_test': True,
        'uploader_email': uploader_email,
        'test_id': test_id,
    }
    return _get_graph(request, **kwargs)


@login_required
def get_graph_smartphone_passive(request, config_id, server_ip):
    if not request.user.is_superuser:
        raise PermissionDenied

    kwargs = {
        'no_test': True,
        'smartphone': True,
        'config_id': config_id,
        'server_ip': server_ip,
    }
    return _get_graph(request, **kwargs)


@login_required
def get_graph_smartphone(request):
    if not request.user.is_superuser:
        raise Http404

    if request.method == "POST":
        exp = request.POST.get("exp", None)
        data_name = request.POST.get("data_name", None)
        server_name = request.POST.get("server_name", None)
        graph_name = request.POST.get("graph_name", None)
        select_name = request.POST.get("select_name", None)
        script, div = graph.get_bokeh_script_and_div_smartphone(exp, data_name, server_name, graph_name, select_name)
        return HttpResponse(json.dumps({'script': script, 'div': div}), content_type="application/json")


@login_required
def get_msg_result(request, test_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    test = get_object_or_404(models.SmartphoneTest, id=test_id)
    msgres = test.result.msgresult
    delays = MsgDelayResult.objects.filter(result=msgres).order_by('id')
    return_dict = {"result_id": test.result.id, "proto_info": json.dumps(test.protoinfo.data, indent=4, sort_keys=True), "delays": delays}
    return render(request, 'collect/msg_result.html', return_dict)


def _process_file_upload(request):
    params = {
        "trace_user_name": request.FILES['trace']._name,
        "uploader_email": request.user.email,
    }
    test, _ = _create_test(params)
    test.trace.file.save(test.trace.name, File(request.FILES['trace'].file))
    if request.FILES['trace']._name.endswith(".pcapng"):
        msg = rewrite_pcap.delay(test.trace.file.name)
        if not msg.get() == "OK":
            return msg
    analyze_trace.delay(test.trace.file.name, test.trace.name, False, True, False)
    return "OK"


@login_required
def no_test_upload(request):
    if request.method == "POST" and request.FILES.get("trace", False):
        # Check if request is usable or not
        if 'trace' not in request.FILES:
            return JsonResponse({"result": "Error, no trace provided"})

        if request.FILES['trace']._name.endswith(".pcap") or request.FILES['trace']._name.endswith(".pcapng"):
            msg = _process_file_upload(request)

        return JsonResponse({"result": msg})

    return render(request, 'collect/no_test_upload.html', {})
