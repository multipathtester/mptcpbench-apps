from datetime import timedelta

from django.db.models import Max, Case, When, DurationField, Q, F, Count

from mptcpbench.connectivity.models import ConnectivityTest
from mptcpbench.mptests.models import Benchmark
from mptcpbench.simplehttpget.models import SimpleHttpGetTest
from mptcpbench.iperf.models import IPerfInterval
from mptcpbench.stream.models import StreamDelay
from .highcharts_helper import line_chart_dict
from .chartkick_helper import bar_chart_dict


def get_valid_benchmark_multipath():
    return Benchmark.objects.filter(mobile__isnull=True)


def get_connectivity_barchart():
    data_raw = ConnectivityTest.objects.filter(
        benchmark__in=get_valid_benchmark_multipath()
    )
    data_raw_2 = data_raw.filter(result__success=True).values('config__url').annotate(
        count=Count('*')
    ).values('config__url', 'count')
    data_raw = data_raw.values('config__url').annotate(
        count=Count('*')
    ).values('config__url', 'count')
    data_all = {}
    data_ok = {}
    for line in data_raw:
        data_all[line['config__url']] = line['count']
    for line in data_raw_2:
        data_ok[line['config__url']] = line['count']
    return [
        bar_chart_dict("Total test of connectivity", data_all),
        bar_chart_dict("Succeded test of connectivity", data_ok)
    ]


def get_simplehttpget_duration_cdf(server_name=None):
    url = "traffic.multipath-quic.org:443/10MB"
    if server_name is not None:
        url = server_name + "." + url

    data_raw = SimpleHttpGetTest.objects.filter(
        benchmark__in=get_valid_benchmark_multipath(),
        result__success=True,
        config__url__contains=url,
    ).values('benchmark__id', 'protocol', 'config__url', 'duration')

    data_dict = {"MPQUIC": [], "MPTCP": [], "QUIC v4": [], "QUIC v6": []}
    mpquic_dict = {}
    ratio_dict = {"MPTCP/MPQUIC": [], "QUIC v4/MPQUIC": [], "QUIC v6/MPQUIC": []}

    for line in data_raw:
        if line['protocol'] == "MPQUIC":
            key = "MPQUIC"
            mpquic_dict[line['benchmark__id']] = line['duration']
        elif line['protocol'] == "MPTCP":
            key = "MPTCP"
        elif line['protocol'] == "QUIC" and line['config__url'].startswith("https://v4."):
            key = "QUIC v4"
        elif line['protocol'] == "QUIC" and line['config__url'].startswith("https://v6."):
            key = "QUIC v6"
        else:
            continue

        data_dict[key].append(line['duration'])

    # Second pass, for ratio
    for line in data_raw:
        if line['protocol'] == "MPTCP":
            key = "MPTCP/MPQUIC"
        elif line['protocol'] == "QUIC" and line['config__url'].startswith("https://v4."):
            key = "QUIC v4/MPQUIC"
        elif line['protocol'] == "QUIC" and line['config__url'].startswith("https://v6."):
            key = "QUIC v6/MPQUIC"
        else:
            # Skip MPQUIC ones
            continue

        mpquic_dur = mpquic_dict.get(line['benchmark__id'], None)
        if mpquic_dur and mpquic_dur.total_seconds() > 0.0:
            cur_dur = line['duration'].total_seconds()
            ratio_dict[key].append(cur_dur / mpquic_dur.total_seconds())

    cdfs = [{"name": k, "data": [
        (((i + 1.0) / len(data_dict[k])), x.total_seconds()) for i, x in enumerate(sorted(data_dict[k]))]} for k in data_dict.keys()]
    title = "Bulk download of 10 MB"
    if server_name:
        title += " (" + server_name + ")"

    ratio_cdfs = [{"name": k, "data": [
        (((i + 1.0) / len(ratio_dict[k])), x) for i, x in enumerate(sorted(ratio_dict[k]))
    ]} for k in ratio_dict.keys()]
    title_ratio = title + " ratios"
    return [
        line_chart_dict(title, cdfs, xtitle="CDF", ytitle="Duration (s)"),
        line_chart_dict(title_ratio, ratio_cdfs, xtitle="CDF",
                        ytitle="Duration ratio", ytype="logarithmic"),
    ]

def get_simplehttpget_v4v6_duration_cdf(server_name=None, **kwargs):
    url = "traffic.multipath-quic.org:443/10MB"
    if server_name is not None:
        url = server_name + "." + url

    data_raw = SimpleHttpGetTest.objects.filter(
        benchmark__in=get_valid_benchmark_multipath(),
        result__success=True,
        config__url__contains=url,
    ).values('benchmark__id', 'protocol', 'config__url', 'duration')

    v6_data_dict = {}
    v4_data_dict = {}

    # Collect data with bench ID
    for line in data_raw:
        data_dict = None
        if line['protocol'] == "QUIC" and line['config__url'].startswith("https://v4."):
            v4_data_dict[line['benchmark__id']] = line['duration'].total_seconds()
        elif line['protocol'] == "QUIC" and line['config__url'].startswith("https://v6."):
            v6_data_dict[line['benchmark__id']] = line['duration'].total_seconds()
        else:
            # Skip MPQUIC ones
            continue

    data = []
    for k in v6_data_dict.keys():
        if k in v4_data_dict:
            ratio = v4_data_dict[k] / v6_data_dict[k]
            if server_name == "ca" and ratio > 1.0:
                print(ratio, k)
            data.append(ratio)

    cdfs = [{"name": "Duration QUIC IPv4/IPv6", "data": [
        (((i + 1.0) / len(data)), x) for i, x in enumerate(sorted(data))
    ]}]
    title = "IPv4/IPV6 ratio comparison of bulk download of 10 MB"
    if server_name:
        title += " (" + server_name + ")"

    return [
        line_chart_dict(title, cdfs, xtitle="CDF", ytitle="Duration ratio", ytype="logarithmic", **kwargs),
    ]


def get_iperf_bandwidth_cdf(server_name=None):
    url = "traffic.multipath-quic.org:5201"
    if server_name is not None:
        url = server_name + "." + url

    data_raw = IPerfInterval.objects.filter(
        intervalInSec="6-7",
        result__test__benchmark__in=get_valid_benchmark_multipath(),
        result__success=True,
        result__test__config__url__contains=url,
    ).values('result__test__benchmark__id', 'result__test__protocol', 'result__test__config__url', 'globalBandwidth')

    data_dict = {"MPQUIC": [], "MPTCP": [], "QUIC v4": [], "QUIC v6": []}
    mpquic_dict = {}
    ratio_dict = {"MPTCP/MPQUIC": [], "QUIC v4/MPQUIC": [], "QUIC v6/MPQUIC": []}

    for line in data_raw:
        if line['result__test__protocol'] == "MPQUIC":
            key = "MPQUIC"
            mpquic_dict[line['result__test__benchmark__id']] = line['globalBandwidth'] * 8 / 1000000.0
        elif line['result__test__protocol'] == "MPTCP":
            key = "MPTCP"
        elif line['result__test__protocol'] == "QUIC" and line['result__test__config__url'].startswith("v4."):
            key = "QUIC v4"
        elif line['result__test__protocol'] == "QUIC" and line['result__test__config__url'].startswith("v6."):
            key = "QUIC v6"
        else:
            continue

        data_dict[key].append(line['globalBandwidth'] * 8 / 1000000.0)

    # Second pass, for ratio
    for line in data_raw:
        if line['result__test__protocol'] == "MPTCP":
            key = "MPTCP/MPQUIC"
        elif line['result__test__protocol'] == "QUIC" and line['result__test__config__url'].startswith("v4."):
            key = "QUIC v4/MPQUIC"
        elif line['result__test__protocol'] == "QUIC" and line['result__test__config__url'].startswith("v6."):
            key = "QUIC v6/MPQUIC"
        else:
            # Skip MPQUIC ones
            continue

        mpquic_bw = mpquic_dict.get(line['result__test__benchmark__id'], None)
        if mpquic_bw and mpquic_bw > 0.0:
            cur_bw = line['globalBandwidth'] * 8 / 1000000.0
            ratio_dict[key].append(cur_bw / mpquic_bw)

    cdfs = [{"name": k, "data": [
        (((i + 1.0) / len(data_dict[k])), x) for i, x in enumerate(sorted(data_dict[k]))]} for k in data_dict.keys()]
    title = "IPerf upload bandwidth"
    if server_name:
        title += " (" + server_name + ")"

    ratio_cdfs = [{"name": k, "data": [
        (((i + 1.0) / len(ratio_dict[k])), x) for i, x in enumerate(sorted(ratio_dict[k]))
    ]} for k in ratio_dict.keys()]
    title_ratio = title + " ratios"
    return [
        line_chart_dict(title, cdfs, xtitle="CDF", ytitle="Goodput (Mbps)"),
        line_chart_dict(title_ratio, ratio_cdfs, xtitle="CDF",
                        ytitle="Goodput ratio", ytype="logarithmic"),
    ]


def get_stream_max_delay_cdf(server_name=None):
    url = "traffic.multipath-quic.org:8080"
    if server_name:
        url = server_name + "." + url

    raw_data = StreamDelay.objects.filter(
        result__test__benchmark__in=get_valid_benchmark_multipath(),
        result__success=True,
        result__test__config__url__contains=url,
    ).values('result__test__benchmark__id', 'result__test__id', 'result__test__protocol', 'result__test__config__url').annotate(
        max_up_delay=Max(Case(
            When(
                Q(upload=True),
                then=F('delay')
            ),
            default=timedelta(0),
            output_field=DurationField()
        )),
        max_down_delay=Max(Case(
            When(
                Q(upload=False),
                then=F('delay')
            ),
            default=timedelta(0),
            output_field=DurationField()
        )),
    )

    up_val = {"MPTCP": [], "MPQUIC": [], "QUIC v4": [], "QUIC v6": []}
    down_val = {"MPTCP": [], "MPQUIC": [], "QUIC v4": [], "QUIC v6": []}
    mpquic_dict_up = {}
    mpquic_dict_down = {}
    ratio_dict_up = {"MPTCP/MPQUIC": [], "QUIC v4/MPQUIC": [], "QUIC v6/MPQUIC": []}
    ratio_dict_down = {"MPTCP/MPQUIC": [], "QUIC v4/MPQUIC": [], "QUIC v6/MPQUIC": []}
    for line in raw_data:
        if line['result__test__protocol'] == "MPTCP":
            key = "MPTCP"
        elif line['result__test__protocol'] == "MPQUIC":
            key = "MPQUIC"
            mpquic_dict_up[line['result__test__benchmark__id']] = line['max_up_delay']
            mpquic_dict_down[line['result__test__benchmark__id']] = line['max_down_delay']
        elif line['result__test__protocol'] == "QUIC" and line['result__test__config__url'].startswith("v4."):
            key = "QUIC v4"
        elif line['result__test__protocol'] == "QUIC" and line['result__test__config__url'].startswith("v6."):
            key = "QUIC v6"
        else:
            continue

        up_val[key].append(line['max_up_delay'])
        down_val[key].append(line['max_down_delay'])

    # Second pass, for ratio
    for line in raw_data:
        if line['result__test__protocol'] == "MPTCP":
            key = "MPTCP/MPQUIC"
        elif line['result__test__protocol'] == "QUIC" and line['result__test__config__url'].startswith("v4."):
            key = "QUIC v4/MPQUIC"
        elif line['result__test__protocol'] == "QUIC" and line['result__test__config__url'].startswith("v6."):
            key = "QUIC v6/MPQUIC"
        else:
            # Skip MPQUIC ones
            continue

        mpquic_up = mpquic_dict_up.get(line['result__test__benchmark__id'], None)
        if mpquic_up and mpquic_up.total_seconds() > 0.0:
            cur_up = line['max_up_delay']
            ratio_dict_up[key].append(cur_up.total_seconds() / mpquic_up.total_seconds())

        mpquic_down = mpquic_dict_down.get(line['result__test__benchmark__id'], None)
        if mpquic_down and mpquic_down.total_seconds() > 0.0:
            cur_down = line['max_down_delay']
            ratio_dict_down[key].append(cur_down.total_seconds() / mpquic_down.total_seconds())

    up_cdfs = [{"name": k, "data": [(((i + 1.0) / len(up_val[k])),
                                     x.total_seconds() * 1000.0)
                for i, x in enumerate(sorted(up_val[k]))]} for k in up_val.keys()]

    down_cdfs = [{"name": k, "data": [(((i + 1.0) / len(down_val[k])),
                                       x.total_seconds() * 1000.0)
                 for i, x in enumerate(sorted(down_val[k]))]} for k in down_val.keys()]

    title_up = "Max stream upload delays"
    title_down = "Max stream download delays"
    if server_name:
        title_up += " (" + server_name + ")"
        title_down += " (" + server_name + ")"

    up_cdfs_ratio = [{"name": k, "data": [(((i + 1.0) / len(ratio_dict_up[k])), x)
                     for i, x in enumerate(sorted(ratio_dict_up[k]))]} for k in ratio_dict_up.keys()]
    down_cdfs_ratio = [{"name": k, "data": [(((i + 1.0) / len(ratio_dict_down[k])), x)
                       for i, x in enumerate(sorted(ratio_dict_down[k]))]} for k in ratio_dict_down.keys()]
    title_up_ratio = title_up + " ratios"
    title_down_ratio = title_down + " ratios"

    return [
        line_chart_dict(title_up, up_cdfs, xtitle="CDF",
                        ytitle="Max delay (ms)", ytype="logarithmic"),
        line_chart_dict(title_up_ratio, up_cdfs_ratio, xtitle="CDF",
                        ytitle="Max delay ratio", ytype="logarithmic"),
        line_chart_dict(title_down, down_cdfs, xtitle="CDF",
                        ytitle="Max delay (ms)", ytype="logarithmic"),
        line_chart_dict(title_down_ratio, down_cdfs_ratio, xtitle="CDF",
                        ytitle="Max delay ratio", ytype="logarithmic"),
    ]
