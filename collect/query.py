import datetime
import pytz

from django.db.models import Case, Count, DateTimeField, DurationField, F, \
    IntegerField, Max, Min, Q, Sum, When
from django.http import Http404
from django.shortcuts import get_object_or_404

from . import models
from mptcpbench.msg.models import MsgBench, MsgOldResult, MsgDelayResult
from mptcpbench.simplehttpget.models import SimpleHttpGetBench, \
    SimpleHttpGetOldResult
from mptcpbench.siri.models import SiriBench, SiriResult, SiriDelayResult
from mptcpbench.mptcpanalysis.models import MPTCPConnection, MPTCPSubflow, \
    MPTCPSubflowFlow, MPTCPSubflowMatch, MPTCPSubflowFlowComplete, \
    MPTCPConnectionFlowBurst

""" Contains all code querying database """


def get_cell_ips_in_trace(trace, smartphone_test=None):
    if smartphone_test is not None:
        potential_cell_ips = models.NetcfgLine.objects.cell_ips(
            result__smartphonetest=smartphone_test
        )
    else:
        potential_cell_ips = models.NetcfgLine.objects.cell_ips()

    conns = MPTCPConnection.objects.filter(trace=trace)
    cell_sfs = MPTCPSubflow.objects.filter(conn__in=conns)
    cell_saddr = (cell_sfs.filter(saddr__in=potential_cell_ips)
                          .values('saddr'))
    cell_daddr = (cell_sfs.filter(daddr__in=potential_cell_ips)
                          .values('daddr'))

    cell_ips_set = set([c['saddr'] for c in cell_saddr] +
                       [c['daddr'] for c in cell_daddr])
    return list(cell_ips_set)


def _get_test_and_conns(**kwargs):
    if ('smartphone' in kwargs and kwargs['smartphone']) and \
         ('no_test' in kwargs and kwargs['no_test']):
        time_thres = datetime.datetime(2017, 1, 27, 16, 0, 0, 0, pytz.UTC)
        tests = models.NoTest.objects.valid(
            uploader_email__startswith=kwargs['config_id'] + "@",
            uploader_email__endswith=kwargs['server_ip'],
            trace__is_analyzed=True,
            time__gt=time_thres
        )
        trace_ids = [t.trace.id for t in tests]
        conns = MPTCPConnection.objects.filter(trace__id__in=trace_ids)
        if kwargs.get('return_all_tests', False):
            return tests, conns

        return tests[0], conns
    elif 'no_test' in kwargs and kwargs['no_test']:
        test = get_object_or_404(models.NoTest,
                                 uploader_email=kwargs['uploader_email'],
                                 id=kwargs['test_id'],
                                 trace__is_analyzed=True)
        conns = MPTCPConnection.objects.filter(trace__id=test.trace.id)
        return test, conns
    else:
        raise Http404


def get_view_results_details(**kwargs):
    test, conns = _get_test_and_conns(**kwargs)
    # Use aggregation system given by django
    # see https://docs.djangoproject.com/en/dev/topics/db/aggregation/
    count_conns_multipath = (conns.annotate(num_subflow=Count('mptcpsubflow'))
                                  .filter(num_subflow__gte=2)
                                  .count())
    # The following line seems quite complex, but we need to minimize the
    # impact on the DB to be scalable
    sff_res = (MPTCPSubflowFlow.objects.filter(conn__in=conns)
               .values('is_client_to_server')
               .annotate(nb_packets=Sum('packets'),
                         nb_bytes_data=Sum('bytes_data'),
                         nb_bytes=Sum('bytes')))
    sf_intermediate = (MPTCPSubflow.objects.filter(conn__in=conns)
                       .values('conn__id')
                       .annotate(nb_subflows=Count('subflow_id'))
                       .values('nb_subflows'))
    sfs = MPTCPSubflow.objects.filter(conn__in=conns)
    additional_sfs = sfs.exclude(subflow_id=0)
    unused_sfs = (sfs.annotate(carried_bytes=Sum(F('mptcpsubflowflow__bytes')))
                     .filter(carried_bytes=0))
    additional_unused_sfs = (
        additional_sfs.annotate(
            carried_bytes=Sum(F('mptcpsubflowflow__bytes'))
        ).filter(carried_bytes=0))
    cell_ips = models.NetcfgLine.objects.cell_ips()
    cellular_sfs = sfs.filter(saddr__in=cell_ips)
    cellular_unused_sfs = unused_sfs.filter(saddr__in=cell_ips)
    additional_cellular_sfs = additional_sfs.filter(saddr__in=cell_ips)
    additional_cellular_unused_sfs = (
        additional_cellular_sfs.annotate(
            carried_bytes=Sum(F('mptcpsubflowflow__bytes'))
        ).filter(carried_bytes=0))

    return (test, conns, count_conns_multipath, sff_res, sf_intermediate, sfs,
            additional_sfs, unused_sfs, additional_unused_sfs, cellular_sfs,
            cellular_unused_sfs, additional_cellular_sfs,
            additional_cellular_unused_sfs)


def _get_conns(**kwargs):
    _, conns = _get_test_and_conns(**kwargs)
    return conns


def get_graph_duration(**kwargs):
    conns = _get_conns(**kwargs)
    durations_raw = (conns.exclude(duration=datetime.timedelta(0))
                          .order_by('duration')
                          .values('duration'))
    return [x['duration'].total_seconds() for x in durations_raw]


def get_graph_flow_bytes(c2s, **kwargs):
    conns = _get_conns(**kwargs)
    bytes_raw = (conns.exclude(duration=datetime.timedelta(0))
                      .filter(mptcpconnectionflow__is_client_to_server=c2s)
                      .values('mptcpconnectionflow__bytes_mptcptrace')
                      .order_by('mptcpconnectionflow__bytes_mptcptrace'))
    return [x['mptcpconnectionflow__bytes_mptcptrace'] for x in bytes_raw]


def get_graph_delay_mpjoin_mpcapable(**kwargs):
    conns = _get_conns(**kwargs)
    subflows = (MPTCPSubflowMatch.objects.select_related()
                .filter(subflow__conn__in=conns)
                .exclude(subflow__subflow_id=0))
    # F expressions to make it easy:
    # https://docs.djangoproject.com/ja/1.10/ref/models/
    # expressions/#f-expressions
    delays_raw = (
        subflows.annotate(delay=(F('start_time') - F('conn__start_time')))
                .order_by('delay')
                .values('delay'))
    return [x['delay'].total_seconds() for x in delays_raw]


def get_graph_rtt_difference_sfs(c2s, min_rtt_samples=3, **kwargs):
    conns = _get_conns(**kwargs)
    subflows = (MPTCPSubflowFlowComplete.objects.filter(conn__in=conns)
                .filter(is_client_to_server=c2s)
                .filter(rtt_samples__gte=min_rtt_samples))
    # The first values() specifies on which values the group by takes place
    prepare_query = (subflows.values('conn__id')
                             .annotate(max_rtt=Max('rtt_avg'),
                                       min_rtt=Min('rtt_avg'),
                                       nb_subflows=Count('rtt_avg')))
    # The last values() allows to get the requested fields
    raw_diffs = (prepare_query.filter(nb_subflows__gte=2)
                              .annotate(diff_rtt=(F('max_rtt') - F('min_rtt')))
                              .order_by('diff_rtt')
                              .values('diff_rtt'))
    return [x['diff_rtt'] for x in raw_diffs if x['diff_rtt'] > 0]


def get_graph_size_subflow_blocks(c2s, **kwargs):
    conns = _get_conns(**kwargs)
    # Seems we reach the limit of the ORM system... Do it into two queries
    conn_flows = (MPTCPConnectionFlowBurst.objects.filter(conn__in=conns)
                  .filter(is_client_to_server=c2s)
                  .values('conn__id')
                  .annotate(nb_bursts=Count('*'))
                  .values('conn__id', 'nb_bursts'))
    subflow_flows = (MPTCPSubflowFlow.objects.filter(conn__in=conns)
                     .filter(is_client_to_server=c2s)
                     .values('conn__id')
                     .annotate(nb_subflows=Count('*'))
                     .filter(nb_subflows__gte=2)
                     .values('conn__id')
                     .annotate(total_bytes=Sum('bytes_data'))
                     .values('conn__id', 'total_bytes'))
    return conn_flows, subflow_flows


def get_graph_bytes_by_ip(c2s, sent, **kwargs):
    conns = _get_conns(**kwargs)
    subflow_flows = (MPTCPSubflowFlow.objects.select_related()
                     .filter(conn__in=conns)
                     .filter(is_client_to_server=c2s))
    aggregate_attr = 'subflow__saddr' if (c2s and sent) or (
        not c2s and not sent) else 'subflow__daddr'
    return (subflow_flows.values(aggregate_attr)
                         .annotate(Sum('bytes_data')))


""" Smartphone queries """


SIMPLE_HTTP_GET_PORT = 80
SIRI_PORT = 8080
MSG_PORT = 8000


def _get_data_handover_conns(conns):
    handover_conns = []
    all_sfs = MPTCPSubflowFlow.objects.filter(conn__in=conns)
    for c in conns:
        sfs = all_sfs.filter(
            conn=c, is_client_to_server=False).order_by('subflow_id')
        if len(sfs) <= 1:
            continue
        la_0 = sfs[0].time_last_ack_tcp
        for i in range(1, len(sfs)):
            if sfs[i].time_last_ack_tcp > la_0 and \
                 sfs[i].time_last_payload_tcp > la_0:
                handover_conns.append(c)
                break

    return handover_conns


def _get_valid_traces(server_ips, select_name, server_port):
    """ Return traces having at least one connection to server_ips on server_port """
    # Well, the bypass mode of Shadowsocks does not always bypass correctly :'(
    bypassed = MPTCPConnection.objects.filter(
        mptcpsubflow__dport=server_port, mptcpsubflow__daddr__in=server_ips)
    others = MPTCPConnection.objects.filter(
        socks_port=server_port, socks_daddr__in=server_ips)
    conns = bypassed | others

    if select_name == "valid":
        pass
    elif select_name == "valid-correct_server":
        pass
    elif select_name == "static":
        dhc = _get_data_handover_conns(conns)
        conns = conns.exclude(id__in=[c.id for c in dhc])
    elif select_name == "mobile":
        dhc = _get_data_handover_conns(conns)
        conns = conns.filter(id__in=[c.id for c in dhc])
    else:
        raise NotImplementedError("Unknown select_name " + select_name)
    conns = conns.values('trace_id', 'id')
    return [c['trace_id'] for c in conns], [c['id'] for c in conns]


def _get_valid_traces_simple_http_get(server_ips, select_name):
    """ Return traces having at least one connection to the simple http get server """
    return _get_valid_traces(server_ips, select_name, SIMPLE_HTTP_GET_PORT)


def _get_valid_traces_siri(server_ips, select_name):
    """ Return traces having at least one connection to the siri server """
    return _get_valid_traces(server_ips, select_name, SIRI_PORT)


def _get_valid_traces_msg(server_ips, select_name):
    """ Return traces having at least one connection to the msg server """
    return _get_valid_traces(server_ips, select_name, MSG_PORT)


def _get_valid_tests(benchs, config, server_ips, valid_traces, time_threshold):
    test = (models.SmartphoneTest.objects.valid(bench__in=benchs, client_trace__is_analyzed=True, client_trace__in=valid_traces,
                                                start_time__gt=time_threshold, config_name=config, server_ip__in=server_ips,
                                                start_time__lt=datetime.datetime(2017, 3, 23, 0, 0, 0, 0, pytz.UTC)))

    print("Valid:", test.count())
    # Check if there are actually two interfaces available at the beginning
    test = test.annotate(nb_ifs=Count(Case(When(result__netcfgline__order=0, then=1), output_field=IntegerField(),)),
                         nb_non_ifs=Count(Case(When(result__netcfgline__order=0, result__netcfgline__ip_address="0.0.0.0/0", then=1),
                                               output_field=IntegerField())),
                         nb_bridges=Count(Case(When(result__netcfgline__order=0, result__netcfgline__interface="bridge0", then=1),
                                               output_field=IntegerField())),
                         nb_tuns=Count(Case(When(result__netcfgline__order=0, result__netcfgline__interface="tun0", then=1),
                                            output_field=IntegerField())),
                         ).filter(nb_ifs__gte=2)
    print("Filter ifs:", test.count())

    # Now count the number of distinct interfaces we have at the beginning of the test
    res = models.Result.objects.filter(smartphonetest__in=test)
    netfgs = (models.NetcfgLine.objects.filter(result__in=res, order=0)
                                       .values('result__smartphonetest', 'result_id')
                                       .annotate(nb_ifs=Count('interface', distinct=True)))

    nb_distinct_ifs = {}
    for n in netfgs:
        nb_distinct_ifs[n['result__smartphonetest']] = n['nb_ifs']

    test = test.values('id', 'nb_ifs', 'nb_non_ifs', 'nb_bridges', 'nb_tuns')
    possibly_valid_tests = {}
    for t in test:
        # Interfaces with IP at 0.0.0.0/0 are not usable interfaces
        # 3 because we should have the tun0 interface
        if t['nb_bridges'] == 0 and t['nb_tuns'] and nb_distinct_ifs[t['id']] - t['nb_non_ifs'] >= 3:
            # Remove here the tun0 interface
            possibly_valid_tests[t['id']
                                 ] = nb_distinct_ifs[t['id']] - t['nb_non_ifs'] - 1

    # Also remove subflows that tried to be established, but didn't
    last_check = (MPTCPConnection.objects.filter(trace__smartphone_client_test__in=possibly_valid_tests.keys())
                  .values('id')
                  .annotate(nb_non_established=Count(Case(When(mptcpsubflow__daddr__in=server_ips,
                                                               mptcpsubflowmatch__duration=datetime.timedelta(
                                                                   0),
                                                               then=1),
                                                          When(mptcpsubflow__daddr__in=server_ips,
                                                               mptcpsubflow__wscaledst=0,
                                                               then=1),
                                                          output_field=IntegerField())),
                            nb_tuns=Count(Case(When(mptcpsubflow__saddr="26.26.26.1", then=1),
                                               output_field=IntegerField())))
                  .values('trace__smartphone_client_test__id', 'nb_non_established', 'nb_tuns'))

    sum_check = {}
    for l in last_check:
        if l['nb_tuns'] == 0:
            sum_check[l['trace__smartphone_client_test__id']] = sum_check.get(
                l['trace__smartphone_client_test__id'], 0) + l['nb_non_established']

    valid_tests = []
    for conn_id, nb_non_established in sum_check.items():
        if possibly_valid_tests[conn_id] - nb_non_established >= 2:
            valid_tests.append(conn_id)

    return valid_tests


def _get_valid_tests_simple_http_get(config, server_ips, valid_traces, time_threshold=datetime.datetime(2017, 1, 27, 16, 0, 0, 0, pytz.UTC),
                                     time_threshold_active_backup=datetime.datetime(2017, 1, 27, 0, 0, 0, 0, pytz.UTC)):
    # Time threshold to allow ignoring bad tests
    # First IP is identifier, i.e. IPV4 addr
    simple_http_get_benchs = SimpleHttpGetBench.objects.filter(
        server_url__contains=server_ips[0])
    time_threshold_config = time_threshold_active_backup if config == "3" else time_threshold
    return _get_valid_tests(simple_http_get_benchs, config, server_ips, valid_traces, time_threshold_config)


def _get_valid_tests_siri(config, server_ips, valid_traces, time_threshold=datetime.datetime(2017, 1, 27, 16, 0, 0, 0, pytz.UTC),
                          time_threshold_active_backup=datetime.datetime(2017, 1, 27, 0, 0, 0, 0, pytz.UTC)):
    # Time threshold to allow ignoring bad tests
    siri_benchs = SiriBench.objects.all()
    time_threshold_config = time_threshold_active_backup if config == "3" else time_threshold
    return _get_valid_tests(siri_benchs, config, server_ips, valid_traces, time_threshold_config)


def _get_valid_tests_msg(config, server_ips, valid_traces, time_threshold=datetime.datetime(2017, 1, 27, 0, 0, 0, 0, pytz.UTC)):
    msg_benchs = MsgBench.objects.all()
    return _get_valid_tests(msg_benchs, config, server_ips, valid_traces, time_threshold)


def _get_cell_ips(valid_tests):
    cell_ips_query = (models.NetcfgLine.objects.filter(result__smartphonetest__in=valid_tests, order=0, interface="rmnet0")
                                               .exclude(ip_address="0.0.0.0/0")
                                               .values('result__smartphonetest', 'ip_address'))
    cell_ips = []
    for c in cell_ips_query:
        cell_ips.append(c['ip_address'].split('/')[0])

    return cell_ips


def _get_graph_data(server_ips, labels_valnames, init_func, data_func, graph_data_func, server_port, valid_traces_func, valid_tests_func, select_name, **kwargs):
    graph_data = init_func(**kwargs)
    # Check for traces and connections doing the right test
    valid_traces, valid_conns = valid_traces_func(server_ips, select_name)
    # There is an oneliner in Python 3.5, but let's stay safe
    kwargs['server_ips'] = server_ips
    kwargs['server_port'] = server_port
    kwargs['valid_traces'] = valid_traces
    kwargs['valid_conns'] = valid_conns
    for config, config_name in labels_valnames:
        if select_name == "valid-correct_server":
            if config == "3":
                valid_server_ips = ["5.196.169.233"]
            else:
                valid_server_ips = ["5.196.169.232"]
        else:
            valid_server_ips = server_ips

        valid_tests = valid_tests_func(config, valid_server_ips, valid_traces)
        data = data_func(config, config_name, valid_tests, **kwargs)
        graph_data_func(config, config_name, data, graph_data, **kwargs)

    return graph_data


def _get_simple_http_get_time(config, config_name, valid_tests, **kwargs):
    time_results = (SimpleHttpGetOldResult.objects.filter(smartphonetest__id__in=valid_tests)
                                                  .values('run_time'))
    return [t['run_time'].total_seconds() for t in time_results]


def _get_perc_cellular(config, config_name, valid_tests, **kwargs):
    cell_ips = _get_cell_ips(valid_tests)
    conn_ids = (MPTCPSubflowMatch.objects.select_related()
                .filter(conn__trace__smartphone_client_test__in=valid_tests)
                .filter(conn__id__in=kwargs['valid_conns'])
                .filter(Q(subflow__daddr__in=kwargs['server_ips']) |
                        Q(subflow__saddr__in=kwargs['server_ips']))
                .values('conn_id'))
    if len(conn_ids) == 0:
        # Avoid AttributeError: 'SQLCompiler' object has no attribute 'col_count'
        return []

    results_total_bytes = (MPTCPSubflowFlow.objects.filter(conn__id__in=conn_ids)
                           .values('conn__id')
                           .annotate(sum_bytes=Sum('bytes'))
                           .values('conn__id', 'sum_bytes'))

    results_cell_bytes = (MPTCPSubflow.objects.filter(conn__id__in=conn_ids)
                          .filter(Q(saddr__in=cell_ips) | Q(daddr__in=cell_ips))
                          .values('conn__id')
                          .annotate(sum_bytes=Sum('mptcpsubflowflow__bytes'))
                          .values('conn__id', 'sum_bytes'))

    cell_bytes = {}
    for r in results_cell_bytes:
        cell_bytes[r['conn__id']] = cell_bytes.get(
            r['conn__id'], 0) + r['sum_bytes']

    return [100.0 * cell_bytes.get(r['conn__id'], 0) / r['sum_bytes'] for r in results_total_bytes if r['sum_bytes'] > 0]


def _get_perc_pkt_cellular(config, config_name, valid_tests, **kwargs):
    cell_ips = _get_cell_ips(valid_tests)
    conn_ids = (MPTCPSubflowMatch.objects.select_related()
                .filter(conn__trace__smartphone_client_test__in=valid_tests)
                .filter(conn__id__in=kwargs['valid_conns'])
                .filter(Q(subflow__daddr__in=kwargs['server_ips']) |
                        Q(subflow__saddr__in=kwargs['server_ips']))
                .values('conn_id'))
    if len(conn_ids) == 0:
        # Avoid AttributeError: 'SQLCompiler' object has no attribute 'col_count'
        return []

    results_total_pkts = (MPTCPSubflowFlow.objects.filter(conn__id__in=conn_ids)
                          .values('conn__id')
                          .annotate(sum_pkts=Sum('packets'))
                          .values('conn__id', 'sum_pkts'))

    results_cell_pkts = (MPTCPSubflow.objects.filter(conn__id__in=conn_ids)
                         .filter(Q(saddr__in=cell_ips) | Q(daddr__in=cell_ips))
                         .values('conn__id')
                         .annotate(sum_pkts=Sum('mptcpsubflowflow__packets'))
                         .values('conn__id', 'sum_pkts'))

    cell_pkts = {}
    for r in results_cell_pkts:
        cell_pkts[r['conn__id']] = cell_pkts.get(
            r['conn__id'], 0) + r['sum_pkts']

    return [100.0 * cell_pkts.get(r['conn__id'], 0) / r['sum_pkts'] for r in results_total_pkts if r['sum_pkts'] > 0]


def _get_open_cellular(config, config_name, valid_tests, **kwargs):
    cell_ips = _get_cell_ips(valid_tests)
    conn_ids = (MPTCPSubflowMatch.objects.select_related()
                .filter(conn__trace__smartphone_client_test__in=valid_tests)
                .filter(conn__id__in=kwargs['valid_conns'])
                .filter(Q(subflow__daddr__in=kwargs['server_ips']) |
                        Q(subflow__saddr__in=kwargs['server_ips']))
                .values('conn_id'))
    if len(conn_ids) == 0:
        # Avoid AttributeError: 'SQLCompiler' object has no attribute 'col_count'
        return []

    results = (conn_ids.annotate(cell_time=Max(Case(When(subflow__saddr__in=cell_ips, then=F('duration')),
                                                    When(subflow__daddr__in=cell_ips, then=F(
                                                        'duration')),
                                                    default=datetime.timedelta(0), output_field=DurationField())),
                                 cell_start=Min(Case(When(subflow__saddr__in=cell_ips, then=F('start_time')),
                                                     When(subflow__daddr__in=cell_ips, then=F(
                                                         'start_time')),
                                                     output_field=DateTimeField())),
                                 is_valid=Max(Case(When(subflow__saddr__in=cell_ips, then=F('subflow__conn__mptcpsubflowflow__nb_rst')),
                                                   When(subflow__daddr__in=cell_ips, then=F(
                                                       'subflow__conn__mptcpsubflowflow__nb_rst')),
                                                   When(subflow__saddr__in=cell_ips, then=F(
                                                       'subflow__conn__mptcpsubflowflow__nb_fin')),
                                                   When(subflow__daddr__in=cell_ips, then=F(
                                                       'subflow__conn__mptcpsubflowflow__nb_fin')),
                                                   output_field=IntegerField())))
               .values('conn_id', 'cell_time', 'cell_start', 'is_valid'))
    # Also take into account cases where no FIN/RST seen
    results_dict = {}
    for r in results:
        if r['conn_id'] in results_dict and r['is_valid'] > 0:
            results_dict[r['conn_id']] = max(r['cell_time'], results_dict.get(
                r['conn_id'][0], datetime.timedelta(0))), True
        else:
            if r['is_valid']:
                results_dict[r['conn_id']] = r['cell_time'], True
            else:
                results_dict[r['conn_id']] = r['cell_start'], False

    conn_results = (MPTCPConnection.objects.select_related()
                    .filter(id__in=conn_ids)
                    .annotate(conn_start_time=Min(F('mptcpsubflowmatch__start_time')),
                              conn_end_time=Max(F('mptcpsubflowmatch__start_time') +
                                                F('mptcpsubflowmatch__duration')))
                    .values('id', 'conn_start_time', 'conn_end_time'))
    conn_results_dict = {}
    for cr in conn_results:
        conn_results_dict[cr['id']
                          ] = cr['conn_start_time'], cr['conn_end_time']

    to_return = []

    for conn_id, cell_info in results_dict.items():
        cell_time, is_duration = cell_info
        conn_start_time, conn_end_time = conn_results_dict[conn_id]
        if cell_time is None:
            cell_time = datetime.timedelta(0)
        elif not is_duration:
            # cell_time is actually cell_start
            cell_time = conn_end_time - cell_time

        to_return.append(100.0 * cell_time / (conn_end_time - conn_start_time))

    return to_return


def _get_siri_delays(config, config_name, valid_tests, **kwargs):
    siri_results = SiriResult.objects.filter(
        smartphonetest__id__in=valid_tests)
    delays = SiriDelayResult.objects.filter(
        result__in=siri_results).values('delay')
    return [d['delay'] for d in delays]


def _get_msg_delays(config, config_name, valid_tests, **kwargs):
    msg_results = MsgOldResult.objects.filter(
        smartphonetest__id__in=valid_tests)
    delays = MsgDelayResult.objects.filter(
        result__in=msg_results).values('delay')
    return [d['delay'] for d in delays]


def _get_siri_max_delay(config, config_name, valid_tests, **kwargs):
    results = (SiriResult.objects.filter(smartphonetest__id__in=valid_tests)
                                 .annotate(max_delay=Max('siridelayresult__delay'))
                                 .values('max_delay'))
    return [r['max_delay'] for r in results if r['max_delay'] is not None]


def _get_msg_max_delay(config, config_name, valid_tests, **kwargs):
    results = (MsgOldResult.objects.filter(smartphonetest__id__in=valid_tests)
                                   .annotate(max_delay=Max('msgdelayresult__delay'))
                                   .values('max_delay'))
    return [r['max_delay'] for r in results if r['max_delay'] is not None]


def _get_siri_missed(config, config_name, valid_tests, **kwargs):
    results = (SiriResult.objects.filter(smartphonetest__id__in=valid_tests)
                                 .values('missed'))
    return [r['missed'] for r in results]


def _get_msg_missed(config, config_name, valid_tests, **kwargs):
    results = (MsgOldResult.objects.filter(smartphonetest__id__in=valid_tests)
                                   .values('missed'))
    return [r['missed'] for r in results]


def _get_cell_energy_consumption(config, config_name, valid_tests, **kwargs):
    traces = models.Trace.objects.filter(
        smartphone_client_test__in=valid_tests)
    cell_consumptions = (models.CellEnergy.objects.filter(trace__in=traces)
                                                  .values('total_energy'))
    return [c['total_energy'] for c in cell_consumptions]


def _get_cell_mean_power(config, config_name, valid_tests, **kwargs):
    traces = models.Trace.objects.filter(
        smartphone_client_test__in=valid_tests)
    cell_consumptions = (models.CellEnergy.objects.filter(trace__in=traces)
                                                  .values('total_energy', 'total_time'))
    return [1000.0 * c['total_energy'] / (c['total_time'].total_seconds()) for c in cell_consumptions]


def get_graph_data_smartphone(exp, data, server_ips, labels_valnames, init_func, graph_data_func, select_name, **kwargs):
    # Assign graph_func to the corresponding function defined above
    if data == "time":
        data_func = _get_simple_http_get_time if exp == "simple_http_get" else None
    elif data == "perc_cellular":
        data_func = _get_perc_cellular
    elif data == "perc_pkt_cellular":
        data_func = _get_perc_pkt_cellular
    elif data == "open_cellular":
        data_func = _get_open_cellular
    elif data == "delays":
        data_func = _get_siri_delays if exp == "siri" else _get_msg_delays if exp == "msg" else None
    elif data == "max_delay":
        data_func = _get_siri_max_delay if exp == "siri" else _get_msg_max_delay if exp == "msg" else None
    elif data == "missed":
        data_func = _get_siri_missed if exp == "siri" else _get_msg_missed if exp == "msg" else None
    elif data == "cell_energy_total":
        data_func = _get_cell_energy_consumption
    elif data == "cell_mean_power":
        data_func = _get_cell_mean_power
    else:
        raise NotImplementedError(
            "Data " + data + " for exp " + exp + " not supported")

    if exp == "simple_http_get":
        server_port, valid_traces_func, valid_tests_func = SIMPLE_HTTP_GET_PORT, _get_valid_traces_simple_http_get, _get_valid_tests_simple_http_get
    elif exp == "siri":
        server_port, valid_traces_func, valid_tests_func = SIRI_PORT, _get_valid_traces_siri, _get_valid_tests_siri
    elif exp == "msg":
        server_port, valid_traces_func, valid_tests_func = MSG_PORT, _get_valid_traces_msg, _get_valid_tests_msg
    else:
        raise NotImplementedError("Unknown exp " + exp)

    return _get_graph_data(server_ips, labels_valnames, init_func, data_func, graph_data_func, server_port,
                           valid_traces_func, valid_tests_func, select_name, **kwargs)
