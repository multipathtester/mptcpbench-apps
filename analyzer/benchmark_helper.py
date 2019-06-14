from .benchmark_graphs import get_benchmark_by_date, \
    get_benchmark_by_server_name, get_unique_device_by_date, get_mobile_benchmark_by_server_name
from mptcpbench.mptests.models import Benchmark


def get_unique_device_count():
    return Benchmark.objects.values('device_uuid').distinct().count()


def get_unique_device_per_server_count():
    raw = Benchmark.objects.values('server_name', 'device_uuid').distinct()
    data = {}
    for line in raw:
        data[line['server_name']] = data.get(line['server_name'], 0) + 1

    return [{'server_name': k, 'count': data[k]} for k in data.keys()]


def get_benchmark_stats():
    return {
        'charts': get_benchmark_by_date() + get_unique_device_by_date() +
        get_benchmark_by_server_name() + get_mobile_benchmark_by_server_name(),
        'device_count': get_unique_device_count(),
        'device_count_server': get_unique_device_per_server_count(),
    }
