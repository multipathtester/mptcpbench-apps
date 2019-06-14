from datetime import timedelta, datetime

from django.db.models import Count, Max, Case, When, Q, F, DurationField, \
    IntegerField, Sum, DateTimeField

from mptcpbench.mptests.models import MobileBenchmark, Benchmark
from mptcpbench.stream.models import StreamTest
from mptcpbench.mptcpinfos.models import MPTCPSubflowInfo
from mptcpbench.quicinfos.models import QUICPathInfo

from .chartkick_helper import bar_chart_dict
from .highcharts_helper import line_chart_dict, scatter_chart_dict


def get_valid_benchmark_mobile(version_operator=None, version=None,
                               only_mobility=False):
    valid_mobile = MobileBenchmark.objects.annotate(
        test_count=Count(Case(
            When(
                Q(benchmark__streamtest__result__success=True),
                then=1
            ),
            default=0,
            output_field=IntegerField()
        ))
    ).filter(test_count=2)
    if version:
        if version_operator == "lt":
            valid_mobile = valid_mobile.filter(
                benchmark__software_version__lt=version
            )
        elif version_operator == "eq":
            valid_mobile = valid_mobile.filter(
                benchmark__software_version__startswith=version
            )
        elif version_operator == "gte":
            valid_mobile = valid_mobile.filter(
                benchmark__software_version__gte=version
            )
    if only_mobility:
        valid_mobile = valid_mobile.filter(benchmark__user_interrupted=False)
    return Benchmark.objects.filter(mobile__in=valid_mobile)


def get_stream_graphs(**kwargs):
    valid_benchmark = get_valid_benchmark_mobile(**kwargs)
    streams = StreamTest.objects.filter(benchmark__in=valid_benchmark).annotate(
        max_up_delay=Max(Case(
            When(
                Q(result__delays__upload=True),
                then=F('result__delays__delay')
            ),
            default=timedelta(0),
            output_field=DurationField()
        )),
        max_down_delay=Max(Case(
            When(
                Q(result__delays__upload=False),
                then=F('result__delays__delay')
            ),
            default=timedelta(0),
            output_field=DurationField()
        )),
        max_up_time=Max(Case(
            When(
                Q(result__delays__upload=True),
                then=F('result__delays__time')
            ),
            default=datetime.fromtimestamp(0),
            output_field=DateTimeField()
        )),
        max_down_time=Max(Case(
            When(
                Q(result__delays__upload=False),
                then=F('result__delays__time')
            ),
            default=datetime.fromtimestamp(0),
            output_field=DateTimeField()
        )),
        count_up_delay=Sum(Case(
            When(
                Q(result__delays__upload=True),
                then=1
            ),
            default=0,
            output_field=IntegerField()
        )),
        count_down_delay=Sum(Case(
            When(
                Q(result__delays__upload=False),
                then=1
            ),
            default=0,
            output_field=IntegerField()
        )),
    )

    mptcp_streams = streams.filter(protocol="MPTCP").order_by("benchmark__id")
    mptcp_streams = mptcp_streams.values(
        'max_up_delay',
        'max_down_delay',
        'count_up_delay',
        'count_down_delay',
        'max_up_time',
        'max_down_time',
        'result__success',
        'benchmark__id',
        'rcv_time',
        'id',
    )

    mpquic_streams = streams.filter(
        protocol="MPQUIC").order_by("benchmark__id")
    mpquic_streams = mpquic_streams.values(
        'max_up_delay',
        'max_down_delay',
        'count_up_delay',
        'count_down_delay',
        'max_up_time',
        'max_down_time',
        'result__success',
        'benchmark__id',
        'id',
    )

    # XXX Django ORM trick to load add the results before playing with
    for mp in mptcp_streams:
        break

    for mp in mpquic_streams:
        break

    upload = {"MPTCP": 0, "MPQUIC": 0}
    download = {"MPTCP": 0, "MPQUIC": 0}
    up_val = {"MPTCP": [], "MPQUIC": []}
    down_val = {"MPTCP": [], "MPQUIC": []}
    delay_ratio = {"Upload stream": [], "Download stream": []}
    count_ratio = {"Upload stream": [], "Download stream": []}
    compare_proto = {"Upload stream": [], "Download stream": []}
    compare_self = {"MPTCP": [], "MPQUIC": []}
    benches_ok = []
    for i in range(len(mpquic_streams)):
        mptcp = mptcp_streams[i]
        mpquic = mpquic_streams[i]
        mptcp_up = mptcp['max_up_delay']
        mpquic_up = mpquic['max_up_delay']
        mptcp_down = mptcp['max_down_delay']
        mpquic_down = mpquic['max_down_delay']
        count_up_mptcp, count_down_mptcp = mptcp['count_up_delay'], mptcp['count_down_delay']
        count_up_mpquic, count_down_mpquic = mpquic['count_up_delay'], mpquic['count_down_delay']
        last_up_mptcp, last_down_mptcp = mptcp['max_up_time'], mptcp['max_down_time']
        last_up_mpquic, last_down_mpquic = mpquic['max_up_time'], mpquic['max_down_time']

        if mptcp_up is None or mpquic_up is None or mptcp_down is None or \
                mpquic_down is None or mptcp_up <= timedelta(0) or \
                mpquic_up <= timedelta(0) or mptcp_down <= timedelta(0) or \
                mpquic_down <= timedelta(0) or count_up_mptcp <= 5 or \
                count_up_mpquic <= 5 or count_down_mptcp <= 5 or \
                count_down_mpquic <= 5 or not mptcp['result__success'] or \
                not mpquic['result__success']:
            continue

        # We perform a correction when the difference >= 10 requests
        # AND there is a difference >= 1 second with the last request replied
        up_ratio = count_up_mpquic - count_up_mptcp
        up_time_ratio = last_up_mpquic - last_up_mptcp
        down_ratio = count_down_mpquic - count_down_mptcp
        down_time_ratio = last_down_mpquic - last_down_mptcp

        if up_ratio >= 10 and up_time_ratio >= timedelta(seconds=1):
            mptcp_up += up_time_ratio
        elif up_ratio <= -10 and up_time_ratio <= timedelta(seconds=-1):
            mpquic_up += abs(up_time_ratio)

        if down_ratio >= 10 and down_time_ratio >= timedelta(seconds=1):
            mptcp_down += down_time_ratio
        elif down_ratio <= -10 and down_time_ratio <= timedelta(seconds=-1):
            mpquic_down += abs(down_time_ratio)

        if mptcp_up < mpquic_up:
            upload["MPTCP"] += 1
        elif mptcp_up > mpquic_up:
            upload["MPQUIC"] += 1

        up_val["MPTCP"].append(mptcp_up)
        up_val["MPQUIC"].append(mpquic_up)
        benches_ok.append(mpquic["benchmark__id"])

        if mptcp_down < mpquic_down:
            download["MPTCP"] += 1
        elif mptcp_down > mpquic_down:
            download["MPQUIC"] += 1

        down_val["MPTCP"].append(mptcp_down)
        down_val["MPQUIC"].append(mpquic_down)

        compare_proto["Upload stream"].append((mptcp_up.total_seconds() * 1000.0, mpquic_up.total_seconds() * 1000.0))
        compare_proto["Download stream"].append((mptcp_down.total_seconds() * 1000.0, mpquic_down.total_seconds() * 1000.0))
        compare_self["MPTCP"].append((mptcp_up.total_seconds() * 1000.0 , mptcp_down.total_seconds() * 1000.0))
        compare_self["MPQUIC"].append((mpquic_up.total_seconds() * 1000.0, mpquic_down.total_seconds() * 1000.0))

        delay_ratio["Upload stream"].append((mptcp_up / mpquic_up, mptcp_up, mpquic_up, mptcp['rcv_time'].isoformat(), mptcp['benchmark__id']))
        delay_ratio["Download stream"].append((mptcp_down / mpquic_down, mptcp_down, mpquic_down, mptcp['rcv_time'].isoformat(), mptcp['benchmark__id']))
        count_ratio["Upload stream"].append(up_ratio)
        count_ratio["Download stream"].append(down_ratio)

    print(benches_ok)
    up_cdfs = [
        {
            "name": "MPTCP",
            "data": [(
                ((i + 1.0) / len(up_val["MPTCP"])),
                x.total_seconds() * 1000.0,
            ) for i, x in enumerate(sorted(up_val["MPTCP"]))],
        },
        {
            "name": "MPQUIC",
            "data": [(
                ((i + 1.0) / len(up_val["MPQUIC"])),
                x.total_seconds() * 1000.0,
            ) for i, x in enumerate(sorted(up_val["MPQUIC"]))],
        },
    ]

    mptcp_cdfs = [
        {
            "name": "Upload",
            "data": [(
                ((i + 1.0) / len(up_val["MPTCP"])),
                x.total_seconds() * 1000.0,
            ) for i, x in enumerate(sorted(up_val["MPTCP"]))],
        },
        {
            "name": "Download",
            "data": [(
                ((i + 1.0) / len(down_val["MPTCP"])),
                x.total_seconds() * 1000.0,
            ) for i, x in enumerate(sorted(down_val["MPTCP"]))],
        },
    ]

    quic_cdfs = [
        {
            "name": "Upload",
            "data": [(
                ((i + 1.0) / len(up_val["MPQUIC"])),
                x.total_seconds() * 1000.0,
            ) for i, x in enumerate(sorted(up_val["MPQUIC"]))],
        },
        {
            "name": "Download",
            "data": [(
                ((i + 1.0) / len(down_val["MPQUIC"])),
                x.total_seconds() * 1000.0,
            ) for i, x in enumerate(sorted(down_val["MPQUIC"]))],
        },
    ]

    up_proto_scatter = [
        {
            "name": "Upload stream",
            "data": compare_proto["Upload stream"],
        },
    ]

    down_proto_scatter = [
        {
            "name": "Download stream",
            "data": compare_proto["Download stream"],
        },
    ]

    mptcp_self_scatter = [
        {
            "name": "MPTCP",
            "data": compare_self["MPTCP"],
        },
    ]

    mpquic_self_scatter = [
        {
            "name": "MPQUIC",
            "data": compare_self["MPQUIC"],
        },
    ]

    down_cdfs = [
        {
            "name": "MPTCP",
            "data": [(
                ((i + 1.0) / len(up_val["MPTCP"])),
                x.total_seconds() * 1000.0
            ) for i, x in enumerate(sorted(down_val["MPTCP"]))],
        },
        {
            "name": "MPQUIC",
            "data": [(
                ((i + 1.0) / len(up_val["MPQUIC"])),
                x.total_seconds() * 1000.0
            ) for i, x in enumerate(sorted(down_val["MPQUIC"]))],
        },
    ]

    delay_ratio_cdfs = [
        {"name": k, "data": [
            {
                "x": ((i + 1.0) / len(delay_ratio[k])),
                "y": x[0],
                "mptcp": x[1].total_seconds(),
                "mpquic": x[2].total_seconds(),
                "when": x[3],
                "benchmark_id": x[4],
            } for i, x in enumerate(sorted(delay_ratio[k], key=lambda item: item[0]))]}
        for k in delay_ratio.keys()]

    count_ratio_cdfs = [
        {"name": k, "data": [
            (((i + 1.0) / len(count_ratio[k])), x) for i, x in enumerate(sorted(count_ratio[k]))]}
        for k in count_ratio.keys()]

    return [
        bar_chart_dict("Stream upload (lower max delay wins)", upload,
                       ytitle="Benchmark where one protocol is better"),
        bar_chart_dict("Stream download (lower max delay wins)", download,
                       ytitle="Benchmark where one protocol is better"),
        scatter_chart_dict("Upload stream", up_proto_scatter,
                           xtitle="MPTCP", ytitle="MPQUIC", xtype="logarithmic", ytype="logarithmic"),
        scatter_chart_dict("Download stream", down_proto_scatter,
                           xtitle="MPTCP", ytitle="MPQUIC", xtype="logarithmic", ytype="logarithmic"),
        scatter_chart_dict("MPTCP", mptcp_self_scatter,
                           xtitle="Upload", ytitle="Download", xtype="logarithmic", ytype="logarithmic"),
        scatter_chart_dict("MPQUIC", mpquic_self_scatter,
                           xtitle="Upload", ytitle="Download", xtype="logarithmic", ytype="logarithmic"),
        line_chart_dict("Max stream upload delays (with correction)", up_cdfs,
                        xtitle="CDF", ytitle="Max delay (ms)",
                        ytype="logarithmic"),
        line_chart_dict("Max stream download delays (with correction)",
                        down_cdfs, xtitle="CDF", ytitle="Max delay (ms)",
                        ytype="logarithmic"),
        line_chart_dict("Max MPTCP stream delays",
                        mptcp_cdfs, xtitle="CDF", ytitle="Max delay (ms)",
                        ytype="logarithmic"),
        line_chart_dict("Max MPQUIC stream delays",
                        quic_cdfs, xtitle="CDF", ytitle="Max delay (ms)",
                        ytype="logarithmic"),
        line_chart_dict("Delay ratio", delay_ratio_cdfs, xtitle="CDF",
                        ytitle="Ratio between max delay MPTCP and MPQUIC",
                        ytype="logarithmic",
                        tooltip_header="CDF: {point.x:.6f}<br>",
                        tooltip_point="Ratio: {point.y:.6f}<br>MPTCP: {point.mptcp:.6f}<br>MPQUIC: {point.mpquic:.6f}<br>When: {point.when}<br>Benchmark ID: {point.benchmark_id}<br>"),
        line_chart_dict("Count request difference", count_ratio_cdfs,
                        xtitle="CDF", ytitle="Delta requests MPQUIC - MPTCP"),
    ]


def get_cell_packet_graphs(**kwargs):
    valid_benchmark = get_valid_benchmark_mobile(**kwargs)
    streams = StreamTest.objects.filter(benchmark__in=valid_benchmark)
    mptcp_streams = streams.filter(
        protocol="MPTCP", result__success=True,
        # Due to bugs in MPTCP info before...
        benchmark__software_version__gte="2.2.3",
    ).order_by("benchmark__id")
    mptcp_subflows_max_val = MPTCPSubflowInfo.objects.filter(
        conn__test_info__streamtest__in=mptcp_streams,
    ).order_by('conn__test_info__id').values('conn__test_info__id', 'conn__conn_id', 'conn__test_info__streamtest__benchmark__id').annotate(
        Max('tcpi_cell_txpackets'),
        Max('tcpi_cell_rxpackets'),
        Max('tcpi_wifi_txpackets'),
        Max('tcpi_wifi_rxpackets'),
    )

    mpquic_streams = streams.filter(
        protocol="MPQUIC", result__success=True,
    ).order_by("benchmark__id")

    mpquic_max_val = QUICPathInfo.objects.filter(
        conn__test_info__streamtest__in=mpquic_streams,
    ).order_by('conn__test_info__id').values('conn__test_info__id', 'path_id', 'interface_name').annotate(
        Max('sent_packets'),
        Max('received_packets'),
    )

    cell_perc = {
        "MPTCP snd": [], "MPTCP rcv": [],
        "MPQUIC snd": [], "MPQUIC rcv": [],
    }
    cell_packets = {
        "MPTCP snd": [], "MPTCP rcv": [],
        "MPQUIC snd": [], "MPQUIC rcv": [],
    }

    # We should count both connections together, and not separated
    benchmark_stats = {}

    for val in mptcp_subflows_max_val:
        if val['conn__test_info__streamtest__benchmark__id'] not in benchmark_stats:
            benchmark_stats[val['conn__test_info__streamtest__benchmark__id']] = {}

        res = benchmark_stats[val['conn__test_info__streamtest__benchmark__id']]
        res['cell_snd'] = res.get('cell_snd', 0) + val['tcpi_cell_txpackets__max']
        res['cell_rcv'] = res.get('cell_rcv', 0) + val['tcpi_cell_rxpackets__max']
        res['wifi_snd'] = res.get('wifi_snd', 0) + val['tcpi_wifi_txpackets__max']
        res['wifi_rcv'] = res.get('wifi_rcv', 0) + val['tcpi_wifi_rxpackets__max']

    for bid in benchmark_stats.keys():
        bs = benchmark_stats[bid]

        if bs['cell_snd'] + bs['wifi_snd'] == 0 or \
                bs['cell_rcv'] + bs['wifi_rcv'] == 0:
            # Avoid division by zero
            continue

        cell_packets["MPTCP snd"].append(bs['cell_snd'])
        cell_packets["MPTCP rcv"].append(bs['cell_rcv'])
        cell_perc["MPTCP snd"].append(bs['cell_snd'] * 100.0 / (
            bs['cell_snd'] + bs['wifi_snd']))
        cell_perc["MPTCP rcv"].append(bs['cell_rcv'] * 100.0 / (
            bs['cell_rcv'] + bs['wifi_rcv']))

    # Processing of QUIC is slightly more complicated
    test_info_id = None
    cell_pkt_sent = 0
    wifi_pkt_sent = 0
    cell_pkt_rcv = 0
    wifi_pkt_rcv = 0
    for val in mpquic_max_val:
        if val.get('interface_name', None) is None:
            continue

        if test_info_id is not None and test_info_id != val['conn__test_info__id'] \
                and cell_pkt_sent + wifi_pkt_sent > 0 and cell_pkt_rcv + wifi_pkt_rcv > 0:
            cell_perc["MPQUIC snd"].append(
                cell_pkt_sent * 100.0 / (cell_pkt_sent + wifi_pkt_sent))
            cell_perc["MPQUIC rcv"].append(
                cell_pkt_rcv * 100.0 / (cell_pkt_rcv + wifi_pkt_rcv))
            cell_packets["MPQUIC snd"].append(cell_pkt_sent)
            cell_packets["MPQUIC rcv"].append(cell_pkt_rcv)

        if test_info_id != val['conn__test_info__id']:
            cell_pkt_sent = 0
            wifi_pkt_sent = 0
            cell_pkt_rcv = 0
            wifi_pkt_rcv = 0

        if 'en' in val['interface_name']:
            wifi_pkt_sent += val['sent_packets__max']
            wifi_pkt_rcv += val['received_packets__max']
        elif 'pdp_ip' in val['interface_name']:
            cell_pkt_sent += val['sent_packets__max']
            cell_pkt_rcv += val['received_packets__max']

        test_info_id = val['conn__test_info__id']

    # Don't forget to record last one
    if test_info_id is not None:
        cell_perc["MPQUIC snd"].append(
            cell_pkt_sent * 100.0 / (cell_pkt_sent + wifi_pkt_sent))
        cell_perc["MPQUIC rcv"].append(
            cell_pkt_rcv * 100.0 / (cell_pkt_rcv + wifi_pkt_rcv))
        cell_packets["MPQUIC snd"].append(cell_pkt_sent)
        cell_packets["MPQUIC rcv"].append(cell_pkt_rcv)

    cell_perc_data = [
        {
            "name": key,
            "data": [(
                ((i + 1.0) / len(cell_perc[key])),
                x,
            ) for i, x in enumerate(sorted(cell_perc[key]))]
        } for key in cell_perc.keys()
    ]

    cell_packets_data = [
        {
            "name": key,
            "data": [(
                ((i + 1.0) / len(cell_packets[key])),
                x,
            ) for i, x in enumerate(sorted(cell_packets[key]))]
        } for key in cell_packets.keys()
    ]

    return [
        line_chart_dict("Percentage of packets on cellular", cell_perc_data,
                        xtitle="CDF", ytitle="Packets over cellular (%)"),
        line_chart_dict("Packets on cellular", cell_packets_data, xtitle="CDF",
                        ytitle="Packets over cellular", ytype="logarithmic"),
    ]
