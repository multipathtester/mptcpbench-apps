import datetime

from django.db.models import Count

from mptcpbench.mptests.models import Benchmark, MobileBenchmark
from .chartkick_helper import bar_chart_dict, line_chart_dict
# from .highcharts_helper import line_chart_dict


def get_benchmark_by_date():
    data_raw = Benchmark.objects.extra(
        {'rcv_date': "date(rcv_time)"}
    ).order_by('rcv_date').values('rcv_date').annotate(count=Count('id'))
    data = []
    nxt_date = None
    for line in data_raw:
        cur_date = line['rcv_date']
        while nxt_date and nxt_date != cur_date:
             data.append((str(nxt_date), 0))
             nxt_date += datetime.timedelta(days=1)

        data.append((str(cur_date), line['count']))
        nxt_date = cur_date + datetime.timedelta(days=1)

    return [
        line_chart_dict("Number of benchmarks per day", data,
                        ytitle="# Benchmarks"),
    ]


def get_unique_device_by_date():
    data_raw = Benchmark.objects.extra(
        {'rcv_date': "date(rcv_time)"}
    ).order_by('rcv_date').values(
        'rcv_date', 'device_uuid'
    ).distinct().values('rcv_date').annotate(
        count=Count('device_uuid', distinct=True)
    )
    data = []
    nxt_date = None
    for line in data_raw:
        cur_date = line['rcv_date']
        while nxt_date and nxt_date != cur_date:
             data.append((str(nxt_date), 0))
             nxt_date += datetime.timedelta(days=1)

        data.append((str(cur_date), line['count']))
        nxt_date = cur_date + datetime.timedelta(days=1)

    return [
        line_chart_dict("Number of unique devices per day", data,
                        ytitle="# Unique Devices"),
    ]


def get_benchmark_by_server_name():
    data_raw = Benchmark.objects.values('server_name').annotate(
        count=Count('id')
    )
    data = {}
    for line in data_raw:
        data[line['server_name']] = line['count']
    return [
        bar_chart_dict("Number of benchmarks per test server", data)
    ]

def get_mobile_benchmark_by_server_name():
    data_raw = MobileBenchmark.objects.values('benchmark__server_name').annotate(
        count=Count('id')
    )
    data = {}
    for line in data_raw:
        data[line['benchmark__server_name']] = line['count']
    return [
        bar_chart_dict("Number of mobile benchmarks per test server", data)
    ]