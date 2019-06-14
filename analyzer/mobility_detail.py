from datetime import timedelta, datetime

from django.db.models import Count, Max, Min, Case, When, Q, F, DurationField, \
    IntegerField, Sum, DateTimeField, Prefetch, BigIntegerField

from mptcpbench.stream.models import StreamTest
from mptcpbench.mptcpinfos.models import MPTCPSubflowInfo, MPTCPConnectionInfo
from .mobility_graphs import get_valid_benchmark_mobile

from mptcpbench.netconnectivities.models import NetConnectivity

def get_mobility_detail():
    benchs = get_valid_benchmark_mobile(version_operator="gte", version="2.2.4")
    print(benchs.count())
    print(NetConnectivity.objects.filter(benchmark__in=benchs).distinct('cell_network_name').count())
    print(NetConnectivity.objects.filter(benchmark__in=benchs).distinct('wifi_network_name').count())
    tests = StreamTest.objects.filter(benchmark__in=benchs)
    mptcp = tests.filter(protocol="MPTCP")
    max_wifi_set = mptcp.values('id').annotate(
        max_tx_wifi=Max(Case(
            When(
                Q(mptcp_test_info__conns__subflows__isexpensive=False) & Q(mptcp_test_info__conns__conn_id=1),
                then=F('mptcp_test_info__conns__subflows__tcpi_wifi_txpackets')
            ),
            default=0,
            output_field=IntegerField()
        )),
        max_rx_wifi=Max(Case(
            When(
                Q(mptcp_test_info__conns__subflows__isexpensive=False) & Q(mptcp_test_info__conns__conn_id=1),
                then=F('mptcp_test_info__conns__subflows__tcpi_wifi_rxpackets')
            ),
            default=0,
            output_field=IntegerField()
        )),
        max_wifi_tx_nxt=Max(Case(
            When(
                Q(mptcp_test_info__conns__subflows__isexpensive=False) & Q(mptcp_test_info__conns__conn_id=1) & Q(mptcp_test_info__conns__subflows__tcpi_wifi_txpackets__gt=0),
                then=F('mptcp_test_info__conns__subflows__tcpi_snd_nxt')
            ),
            default=0,
            output_field=BigIntegerField()
        )),
        max_wifi_rx_nxt=Max(Case(
            When(
                Q(mptcp_test_info__conns__subflows__isexpensive=False) & Q(mptcp_test_info__conns__conn_id=1) & Q(mptcp_test_info__conns__subflows__tcpi_wifi_rxpackets__gt=0),
                then=F('mptcp_test_info__conns__subflows__tcpi_rcv_nxt')
            ),
            default=0,
            output_field=BigIntegerField()
        ))
    )
    q_statement = Q()
    q_statement_rx = Q()
    q_statement_tx_next = Q()
    q_statement_rx_next = Q()
    exclude_ids = []
    for pair in max_wifi_set:
        if pair['max_tx_wifi'] == 0:
            exclude_ids.append(pair['id'])
        else:
            q_statement |= (Q(id=pair['id']) &
                            Q(mptcp_test_info__conns__conn_id=1) &
                            Q(mptcp_test_info__conns__subflows__tcpi_wifi_txpackets=pair['max_tx_wifi']))
            q_statement_rx |= (Q(id=pair['id']) &
                               Q(mptcp_test_info__conns__conn_id=1) &
                               Q(mptcp_test_info__conns__subflows__tcpi_wifi_rxpackets=pair['max_rx_wifi']))
            q_statement_tx_next |= (Q(id=pair['id']) &
                                    Q(mptcp_test_info__conns__conn_id=1) &
                                    Q(mptcp_test_info__conns__subflows__tcpi_snd_nxt=pair['max_wifi_tx_nxt']))
            q_statement_rx_next |= (Q(id=pair['id']) &
                                    Q(mptcp_test_info__conns__conn_id=1) &
                                    Q(mptcp_test_info__conns__subflows__tcpi_rcv_nxt=pair['max_wifi_rx_nxt']))

    mptcp = mptcp.exclude(id__in=exclude_ids).annotate(
        start_cell=Min(Case(
            When(
                Q(mptcp_test_info__conns__subflows__isexpensive=True,
                  mptcp_test_info__conns__conn_id=1,
                  mptcp_test_info__conns__subflows__tcpi_cell_txpackets__gt=0),
                then=F('mptcp_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        )),
        stop_wifi=Min(Case(
            When(
                q_statement,
                then=F('mptcp_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        )),
        stop_wifi_rx=Min(Case(
            When(
                q_statement_rx,
                then=F('mptcp_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        )),
        stop_wifi_tx_next=Min(Case(
            When(
                q_statement_tx_next,
                then=F('mptcp_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        )),
        stop_wifi_rx_next=Min(Case(
            When(
                q_statement_rx_next,
                then=F('mptcp_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        ))
    ).exclude(
        # Was cellular actually available (issue with v6 WiFi and v4 cellular)
        start_cell__gte=datetime(2400, 1, 1)
    ).exclude(
        # Was the connection actually using WiFi at all?
        stop_wifi__gte=datetime(2400, 1, 1)
    ).exclude(
        # This is strange...
        duration=timedelta(0)
    )
    handover_data = mptcp
    mptcp = mptcp.values('id', 'start_time', 'start_cell', 'stop_wifi', 'duration', 'stop_wifi_rx', 'stop_wifi_rx_next', 'stop_wifi_tx_next')

    import matplotlib.pyplot as plt
    from matplotlib.ticker import Locator
    import numpy as np

    class MinorSymLogLocator(Locator):
        """
        Dynamically find minor tick positions based on the positions of
        major ticks for a symlog scaling.
        """
        def __init__(self, linthresh):
            """
            Ticks will be placed between the major ticks.
            The placement is linear for x between -linthresh and linthresh,
            otherwise its logarithmically
            """
            self.linthresh = linthresh

        def __call__(self):
            'Return the locations of the ticks'
            majorlocs = self.axis.get_majorticklocs()

            # iterate through minor locs
            minorlocs = []

            # handle the lowest part
            for i in range(1, len(majorlocs)):
                majorstep = majorlocs[i] - majorlocs[i-1]
                if abs(majorlocs[i-1] + majorstep/2) < self.linthresh:
                    ndivs = 10
                else:
                    ndivs = 9
                minorstep = majorstep / ndivs
                locs = np.arange(majorlocs[i-1], majorlocs[i], minorstep)[1:]
                minorlocs.extend(locs)

            return self.raise_if_exceeds(np.array(minorlocs))

        def tick_values(self, vmin, vmax):
            raise NotImplementedError('Cannot get tick locations for a '
                                      '%s type.' % type(self))

    # Figure 1: absolute values
    f = plt.figure(figsize=(4.5,3))
    ax = f.add_subplot(111)
    x_val = [(x['stop_wifi'] - x['start_cell']).total_seconds() for x in mptcp]
    x_val = sorted(x_val)
    y_val = [(i + 1.0) / len(x_val) * 100.0 for i, _ in enumerate(x_val)]
    ax.plot(x_val, y_val, label='w.r.t. last Wi-Fi packet sent', lw=2, ls='-')
    x_val_rx = [(x['stop_wifi_rx'] - x['start_cell']).total_seconds() for x in mptcp]
    x_val_rx = sorted(x_val_rx)
    y_val_rx = [(i + 1.0) / len(x_val_rx) * 100.0 for i, _ in enumerate(x_val_rx)]
    ax.plot(x_val_rx, y_val_rx, label='w.r.t. last Wi-Fi packet received', lw=2, ls='--')
    x_val_tx_nxt = [(x['stop_wifi_tx_next'] - x['start_cell']).total_seconds() for x in mptcp]
    x_val_tx_nxt = sorted(x_val_tx_nxt)
    y_val_tx_nxt = [(i + 1.0) / len(x_val_tx_nxt) * 100.0 for i, _ in enumerate(x_val_tx_nxt)]
    # ax.plot(x_val_tx_nxt, y_val_tx_nxt, label='Compared to last WiFi TX progress')
    x_val_rx_nxt = [(x['stop_wifi_rx_next'] - x['start_cell']).total_seconds() for x in mptcp]
    x_val_rx_nxt = sorted(x_val_rx_nxt)
    y_val_rx_nxt = [(i + 1.0) / len(x_val_rx_nxt) * 100.0 for i, _ in enumerate(x_val_rx_nxt)]
    # ax.plot(x_val_rx_nxt, y_val_rx_nxt, label='Compared to last WiFi RX progress')
    plt.legend()
    ax.set_xlabel('Delta Time with First Phone Cellular Packet (s)')
    ax.set_ylabel('CDF')
    ax.set_xscale("symlog")
    ax.minorticks_on()
    xaxis = plt.gca().xaxis
    xaxis.set_minor_locator(MinorSymLogLocator(1e-1))
    plt.grid(True, which='both')
    plt.tight_layout()
    plt.savefig('handover_duration.png', transparent=True, dpi=300)
    plt.savefig('handover_duration.pdf')
    plt.close('all')
    # Figure 2: relative values
    plt.figure()
    x_val = [(x['stop_wifi'] - x['start_cell']).total_seconds() * 100.0 / x['duration'].total_seconds() for x in mptcp]
    x_val = sorted(x_val)
    y_val = [(i + 1.0) / len(x_val) * 100.0 for i, _ in enumerate(x_val)]
    plt.plot(x_val, y_val, label='Compared to last WiFi packet sent ' + str(len(x_val)))
    x_val_rx = [(x['stop_wifi_rx'] - x['start_cell']).total_seconds() * 100.0 / x['duration'].total_seconds() for x in mptcp]
    x_val_rx = sorted(x_val_rx)
    y_val_rx = [(i + 1.0) / len(x_val_rx) * 100.0 for i, _ in enumerate(x_val_rx)]
    plt.plot(x_val_rx, y_val_rx, label='Compared to last WiFi packet received')
    x_val_tx_nxt = [(x['stop_wifi_tx_next'] - x['start_cell']).total_seconds() * 100.0 / x['duration'].total_seconds() for x in mptcp]
    x_val_tx_nxt = sorted(x_val_tx_nxt)
    y_val_tx_nxt = [(i + 1.0) / len(x_val_tx_nxt) * 100.0 for i, _ in enumerate(x_val_tx_nxt)]
    plt.plot(x_val_tx_nxt, y_val_tx_nxt, label='Compared to last WiFi TX progress')
    x_val_rx_nxt = [(x['stop_wifi_rx_next'] - x['start_cell']).total_seconds() * 100.0 / x['duration'].total_seconds() for x in mptcp]
    x_val_rx_nxt = sorted(x_val_rx_nxt)
    y_val_rx_nxt = [(i + 1.0) / len(x_val_rx_nxt) * 100.0 for i, _ in enumerate(x_val_rx_nxt)]
    plt.plot(x_val_rx_nxt, y_val_rx_nxt, label='Compared to last WiFi RX progress')
    plt.legend()
    plt.xlabel('Handover time duration relative to the test (%)')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.savefig('handover_duration_perc.pdf')
    plt.close('all')
    get_handover_reason(handover_data)


def get_handover_reason(handover_data):
    # Only keep upload connections so far, considerably increases performance
    handover_data = handover_data.select_related("mptcp_test_info").prefetch_related(
        Prefetch(
            "mptcp_test_info__conns",
            queryset=MPTCPConnectionInfo.objects.filter(conn_id=1)
        )
    )
    result = {"RTT Threshold": 0, "Under RTO": 0, "RTO Threshold": 0, "Other": 0}
    for m in handover_data:
        # The cellular starts at start_cell: why?
        # Reason 1: RTT Threshold over 600 ms
        conn_points = m.mptcp_test_info.conns.filter(time=m.start_cell)
        if len(conn_points) != 1:
            continue
        conn_point = conn_points[0]
        wifi_points = MPTCPSubflowInfo.objects.filter(conn=conn_point, isexpensive=False)
        if len(wifi_points) != 1:
            continue
        wifi_point = wifi_points[0]
        if wifi_point.tcpi_srtt >= 600:
            result["RTT Threshold"] += 1
            continue

        # Reason 2: under RTO retransmission
        previous_conn_points = m.mptcp_test_info.conns.filter(time__lt=m.start_cell)
        if len(previous_conn_points) == 0:
            continue
        previous_conn_point = previous_conn_points.latest('time')
        previous_wifi_points = MPTCPSubflowInfo.objects.filter(isexpensive=False, conn=previous_conn_point)
        if len(previous_wifi_points) == 0:
            continue
        previous_wifi_point = previous_wifi_points[0]
        if previous_wifi_point.tcpi_txretransmitpackets < wifi_point.tcpi_txretransmitpackets:
            result["Under RTO"] += 1
            continue

        # Reason 3: RTO threshold too high
        if wifi_point.tcpi_rto >= 1500:
            result["RTO Threshold"] += 1
            continue

        # Reason 4: probably WiFi Assist did something, be we are not sure...
        result["Other"] += 1

    import matplotlib.pyplot as plt
    labels = []
    sizes = []
    for l in result.keys():
        labels.append(l)
        sizes.append(result[l])

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, startangle=90, autopct='%1.1f%%')
    ax1.axis('equal')
    plt.tight_layout()
    plt.savefig("handover_reason.pdf")
    plt.close('all')

def get_quic_mobility_detail():
    benchs = get_valid_benchmark_mobile(version_operator="gte", version="2.2.4")
    tests = StreamTest.objects.filter(benchmark__in=benchs)
    quic = tests.filter(protocol="MPQUIC")
    max_wifi_set = quic.values('id').annotate(
        max_tx_wifi=Max(Case(
            When(
                Q(quic_test_info__conns__paths__interface_name__startswith="en"),
                then=F('quic_test_info__conns__paths__sent_packets')
            ),
            default=0,
            output_field=IntegerField()
        )),
        max_rx_wifi=Max(Case(
            When(
                Q(quic_test_info__conns__paths__interface_name__startswith="en"),
                then=F('quic_test_info__conns__paths__received_packets')
            ),
            default=0,
            output_field=IntegerField()
        )),
        max_wifi_tx_nxt=Max(Case(
            When(
                Q(quic_test_info__conns__paths__interface_name__startswith="en") & Q(quic_test_info__conns__paths__sent_packets__gt=0),
                then=F('quic_test_info__conns__paths__least_unacked_packet_number')
            ),
            default=0,
            output_field=BigIntegerField()
        )),
        max_wifi_rx_nxt=Max(Case(
            When(
                Q(quic_test_info__conns__paths__interface_name__startswith="en") & Q(quic_test_info__conns__paths__received_packets__gt=0),
                then=F('quic_test_info__conns__paths__last_received_packet_number')
            ),
            default=0,
            output_field=BigIntegerField()
        ))
    )
    q_statement = Q()
    q_statement_rx = Q()
    q_statement_tx_next = Q()
    q_statement_rx_next = Q()
    exclude_ids = []
    for pair in max_wifi_set:
        if pair['max_tx_wifi'] == 0:
            exclude_ids.append(pair['id'])
        else:
            q_statement |= (Q(id=pair['id']) &
                            Q(quic_test_info__conns__paths__sent_packets=pair['max_tx_wifi']))
            q_statement_rx |= (Q(id=pair['id']) &
                               Q(quic_test_info__conns__paths__received_packets=pair['max_rx_wifi']))
            q_statement_tx_next |= (Q(id=pair['id']) &
                                    Q(quic_test_info__conns__paths__least_unacked_packet_number=pair['max_wifi_tx_nxt']))
            q_statement_rx_next |= (Q(id=pair['id']) &
                                    Q(quic_test_info__conns__paths__last_received_packet_number=pair['max_wifi_rx_nxt']))

    quic = quic.exclude(id__in=exclude_ids).annotate(
        start_cell=Min(Case(
            When(
                Q(quic_test_info__conns__paths__interface_name__startswith="pdp",
                  quic_test_info__conns__paths__sent_packets__gt=0),
                then=F('quic_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        )),
        stop_wifi=Min(Case(
            When(
                q_statement,
                then=F('quic_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        )),
        stop_wifi_rx=Min(Case(
            When(
                q_statement_rx,
                then=F('quic_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        )),
        stop_wifi_tx_next=Min(Case(
            When(
                q_statement_tx_next,
                then=F('quic_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        )),
        stop_wifi_rx_next=Min(Case(
            When(
                q_statement_rx_next,
                then=F('quic_test_info__conns__time')
            ),
            default=datetime(2500, 1, 1),
            output_field=DateTimeField()
        ))
    ).exclude(
        # Was cellular actually available (issue with v6 WiFi and v4 cellular)
        start_cell__gte=datetime(2400, 1, 1)
    ).exclude(
        # Was the connection actually using WiFi at all?
        stop_wifi__gte=datetime(2400, 1, 1)
    ).exclude(
        # This is strange...
        duration=timedelta(0)
    )
    handover_data = quic
    quic = quic.values('id', 'start_time', 'start_cell', 'stop_wifi', 'duration', 'stop_wifi_rx', 'stop_wifi_rx_next', 'stop_wifi_tx_next')

    import matplotlib.pyplot as plt
    from matplotlib.ticker import Locator
    import numpy as np

    class MinorSymLogLocator(Locator):
        """
        Dynamically find minor tick positions based on the positions of
        major ticks for a symlog scaling.
        """
        def __init__(self, linthresh):
            """
            Ticks will be placed between the major ticks.
            The placement is linear for x between -linthresh and linthresh,
            otherwise its logarithmically
            """
            self.linthresh = linthresh

        def __call__(self):
            'Return the locations of the ticks'
            majorlocs = self.axis.get_majorticklocs()

            # iterate through minor locs
            minorlocs = []

            # handle the lowest part
            for i in range(1, len(majorlocs)):
                majorstep = majorlocs[i] - majorlocs[i-1]
                if abs(majorlocs[i-1] + majorstep/2) < self.linthresh:
                    ndivs = 10
                else:
                    ndivs = 9
                minorstep = majorstep / ndivs
                locs = np.arange(majorlocs[i-1], majorlocs[i], minorstep)[1:]
                minorlocs.extend(locs)

            return self.raise_if_exceeds(np.array(minorlocs))

        def tick_values(self, vmin, vmax):
            raise NotImplementedError('Cannot get tick locations for a '
                                      '%s type.' % type(self))

    # Figure 1: absolute values
    ax = plt.subplot(111)
    x_val = [(x['stop_wifi'] - x['start_cell']).total_seconds() for x in quic]
    x_val = sorted(x_val)
    y_val = [(i + 1.0) / len(x_val) * 100.0 for i, _ in enumerate(x_val)]
    ax.plot(x_val, y_val, label='Compared to last WiFi packet sent ' + str(len(x_val)))
    x_val_rx = [(x['stop_wifi_rx'] - x['start_cell']).total_seconds() for x in quic]
    x_val_rx = sorted(x_val_rx)
    y_val_rx = [(i + 1.0) / len(x_val_rx) * 100.0 for i, _ in enumerate(x_val_rx)]
    ax.plot(x_val_rx, y_val_rx, label='Compared to last WiFi packet received')
    x_val_tx_nxt = [(x['stop_wifi_tx_next'] - x['start_cell']).total_seconds() for x in quic]
    x_val_tx_nxt = sorted(x_val_tx_nxt)
    y_val_tx_nxt = [(i + 1.0) / len(x_val_tx_nxt) * 100.0 for i, _ in enumerate(x_val_tx_nxt)]
    ax.plot(x_val_tx_nxt, y_val_tx_nxt, label='Compared to last WiFi TX progress')
    x_val_rx_nxt = [(x['stop_wifi_rx_next'] - x['start_cell']).total_seconds() for x in quic]
    x_val_rx_nxt = sorted(x_val_rx_nxt)
    y_val_rx_nxt = [(i + 1.0) / len(x_val_rx_nxt) * 100.0 for i, _ in enumerate(x_val_rx_nxt)]
    ax.plot(x_val_rx_nxt, y_val_rx_nxt, label='Compared to last WiFi RX progress')
    plt.legend()
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('CDF')
    ax.set_xscale("symlog")
    ax.minorticks_on()
    xaxis = plt.gca().xaxis
    xaxis.set_minor_locator(MinorSymLogLocator(1e-1))
    plt.grid(True, which='both')
    plt.savefig('quic_handover_duration.pdf')
    plt.close('all')
    # Figure 2: relative values
    plt.figure()
    x_val = [(x['stop_wifi'] - x['start_cell']).total_seconds() * 100.0 / x['duration'].total_seconds() for x in quic]
    x_val = sorted(x_val)
    y_val = [(i + 1.0) / len(x_val) * 100.0 for i, _ in enumerate(x_val)]
    plt.plot(x_val, y_val, label='Compared to last WiFi packet sent ' + str(len(x_val)))
    x_val_rx = [(x['stop_wifi_rx'] - x['start_cell']).total_seconds() * 100.0 / x['duration'].total_seconds() for x in quic]
    x_val_rx = sorted(x_val_rx)
    y_val_rx = [(i + 1.0) / len(x_val_rx) * 100.0 for i, _ in enumerate(x_val_rx)]
    plt.plot(x_val_rx, y_val_rx, label='Compared to last WiFi packet received')
    x_val_tx_nxt = [(x['stop_wifi_tx_next'] - x['start_cell']).total_seconds() * 100.0 / x['duration'].total_seconds() for x in quic]
    x_val_tx_nxt = sorted(x_val_tx_nxt)
    y_val_tx_nxt = [(i + 1.0) / len(x_val_tx_nxt) * 100.0 for i, _ in enumerate(x_val_tx_nxt)]
    plt.plot(x_val_tx_nxt, y_val_tx_nxt, label='Compared to last WiFi TX progress')
    x_val_rx_nxt = [(x['stop_wifi_rx_next'] - x['start_cell']).total_seconds() * 100.0 / x['duration'].total_seconds() for x in quic]
    x_val_rx_nxt = sorted(x_val_rx_nxt)
    y_val_rx_nxt = [(i + 1.0) / len(x_val_rx_nxt) * 100.0 for i, _ in enumerate(x_val_rx_nxt)]
    plt.plot(x_val_rx_nxt, y_val_rx_nxt, label='Compared to last WiFi RX progress')
    plt.legend()
    plt.xlabel('Handover time duration relative to the test (%)')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.savefig('quic_handover_duration_perc.pdf')
    plt.close('all')