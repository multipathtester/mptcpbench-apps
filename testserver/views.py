import json
import os

from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse, JsonResponse

from . import models, simple_http_get, test_preparation

def index(request):
    return HttpResponse("Hello, world. You're at the test_server index.")


def _check_required_fields_launch_test(test_dict):
    for field in ["bench", "client_tag", "uuid"]:
        if field not in test_dict:
            raise SuspiciousOperation("Field " + field + " is missing in request")


def _check_required_bench_field_launch_test(bench_dict):
    for field in ["config", "name"]:
        if field not in bench_dict:
            raise SuspiciousOperation("Field " + field + " is missing in bench dict")


def _launch_test(test_dict):
    _check_required_fields_launch_test(test_dict)
    _check_required_bench_field_launch_test(test_dict["bench"])
    test_preparation.check_no_test_running()

    sysctl_dict = test_preparation.get_net_sysctl()
    bench_dict = test_preparation.launch_test(test_dict)

    return JsonResponse({
        "bench": bench_dict,
        "server_sysctl": sysctl_dict,
    })


def launch_test(request):
    """ Client should send the following type of request (JSON):
        {
            "bench": {
                "config": {
                    ...
                },
                "name": "bench_name"
            },
            "client_tag": "123456789azertyuiopmlkjhgfdsqwxcvbn",
            "uuid": : "123e4567-e89b-12d3-a456-426655440000",
        }
    """
    # TODO The client tag could be used later to authenticate the client
    if request.method == "POST":
        try:
            body_unicode = request.body.decode('utf-8')
            test_dict = json.loads(body_unicode)
            return _launch_test(test_dict)
        except test_preparation.BusyError:
            return JsonResponse({"result": "server_busy"})
        except Exception as e:
            print(e)
            return JsonResponse({}, status=400)

    # Else, silently ignore it
    return JsonResponse({})


def stop_nginx_server(request):
    if request.method == "POST":
        try:
            body_unicode = request.body.decode('utf-8')
            name_dict = json.loads(body_unicode)
            print(name_dict)
            qs = models.PendingTrace.objects.filter(name=name_dict["name"])
            if qs.count() != 0:
                nginx_config_path = os.path.abspath("nginx.conf")
                simple_http_get.stop_nginx_server(nginx_config_path)
        except test_preparation.BusyError:
            return JsonResponse({"result": "server_busy"})
        except Exception as e:
            print(e)
            return JsonResponse({}, status=400)

    # Else, silently ignore it
    return JsonResponse({})
