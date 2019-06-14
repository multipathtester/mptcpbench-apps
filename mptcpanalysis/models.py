from datetime import datetime, timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _

from mptcpbench.collect.models import Trace
from mptcpbench.mptcp_analysis_scripts.common import ADD_ADDRS, RM_ADDRS, C2S,\
    S2C, SOCKS_DADDR, SOCKS_PORT, TCP_COMPLETE, BURSTS, RETRANS_DSS, DURATION,\
    IS_REINJ, REINJ_ORIG, REINJ_ORIG_TIMESTAMP, TIMESTAMP_RETRANS


def validate_port_number(value):
    """ Validator for TCP port """
    if value > 65535:
        raise ValidationError(_('%(value)s is not a valid TCP port'),
                              params={'value': value},)


def validate_positive_float(value):
    """ Validator for positive float """
    if value < 0.0:
        raise ValidationError(_('%(value)s is not a positive float'),
                              params={'value': value},)


class MPTCPConnection(models.Model):
    """
        A MPTCP connection with its global information (i.e., not flow-based)
    """
    trace = models.ForeignKey(Trace)
    conn_id = models.PositiveIntegerField()
    duration = models.DurationField()
    start_time = models.DurationField()
    max_idle_time = models.DurationField(default=timedelta(0))
    max_idle_time_payload = models.DurationField(default=timedelta(0))
    socks_daddr = models.GenericIPAddressField(null=True, blank=True)
    socks_port = models.PositiveIntegerField(validators=[validate_port_number],
                                             null=True, blank=True)

    class Meta:
        # Ensure key in database to avoid inconsistent states
        unique_together = (("conn_id", "trace"),)


class MPTCPConnectionAddAddress(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    is_from_client = models.BooleanField()
    advertised_addr = models.GenericIPAddressField()
    sent_time = models.DateTimeField()


class MPTCPConnectionFlow(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    is_client_to_server = models.BooleanField()
    bytes_mptcptrace = models.BigIntegerField()
    reinj_bytes = models.BigIntegerField()
    reinj_pc = models.FloatField(validators=[validate_positive_float])
    time_last_ack_tcp = models.DurationField()
    time_last_payload_tcp = models.DurationField()

    class Meta:
        # Two per connection, one per flow
        unique_together = (("conn", "is_client_to_server"),)


class MPTCPConnectionFlowBurst(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    is_client_to_server = models.BooleanField()
    subflow_id = models.PositiveIntegerField()
    bytes = models.BigIntegerField()
    packets = models.BigIntegerField()
    duration = models.DurationField()
    start_time = models.DateTimeField()


class MPTCPConnectionFlowRetransDSS(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    is_client_to_server = models.BooleanField()
    delta = models.DurationField()
    subflow_id = models.PositiveIntegerField()
    dss = models.BigIntegerField()
    delta_from_first_sending = models.DurationField()
    delta_from_last_retrans = models.DurationField()
    delta_from_last_remote_packet = models.DurationField()


class MPTCPConnectionRemoveAddress(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    is_from_client = models.BooleanField()
    kernel_subflow_id = models.PositiveIntegerField()
    sent_time = models.DateTimeField()


class MPTCPConnectionFlowRTT(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    is_client_to_server = models.BooleanField()
    rtt_25p = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_75p = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_90p = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_95p = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_97p = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_98p = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_99p = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_avg = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_max = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_median = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_min = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_samples = models.PositiveIntegerField()
    rtt_stdev = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        # Two per connection, one per flow
        unique_together = (("conn", "is_client_to_server"),)


class MPTCPSubflow(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    subflow_id = models.PositiveIntegerField()
    daddr = models.GenericIPAddressField()
    dport = models.PositiveIntegerField(validators=[validate_port_number])
    interface = models.CharField(max_length=16)  # XXX Currently dummy
    saddr = models.GenericIPAddressField()
    sport = models.PositiveIntegerField(validators=[validate_port_number])
    type = models.CharField(max_length=4)
    wscaledst = models.PositiveSmallIntegerField()
    wscalesrc = models.PositiveSmallIntegerField()

    class Meta:
        # A subflow id is unique within a given connection
        unique_together = (("conn", "subflow_id"),)


class MPTCPSubflowFlow(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    subflow = models.ForeignKey(MPTCPSubflow)
    is_client_to_server = models.BooleanField()
    bytes = models.BigIntegerField()
    bytes_data = models.BigIntegerField()
    bytes_retrans = models.BigIntegerField()
    bytes_tcpip_hdr = models.BigIntegerField()
    nb_ack = models.BigIntegerField()
    nb_fin = models.PositiveIntegerField()
    nb_rst = models.PositiveIntegerField()
    nb_syn = models.PositiveIntegerField()
    packets = models.BigIntegerField()
    packets_outoforder = models.BigIntegerField()
    packets_retrans = models.BigIntegerField()
    reinjected_orig_bytes = models.BigIntegerField()
    reinjected_orig_packets = models.BigIntegerField()
    time_fin_ack_tcp = models.DurationField()
    time_first_ack = models.FloatField()
    time_first_payload = models.FloatField()
    time_last_ack_tcp = models.DurationField()
    time_last_payload = models.FloatField()
    time_last_payload_tcp = models.DurationField()
    time_last_payload_with_retrans_tcp = models.DurationField()

    class Meta:
        # Only two per subflow, one for each flow
        unique_together = (("subflow", "is_client_to_server"),)


class MPTCPSubflowFlowComplete(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    subflow = models.ForeignKey(MPTCPSubflow)
    is_client_to_server = models.BooleanField()
    maximum_in_flight_size = models.BigIntegerField()
    minimum_in_flight_size = models.BigIntegerField()
    nb_flow_control = models.BigIntegerField()
    nb_network_duplicate = models.BigIntegerField()
    nb_reordering = models.BigIntegerField()
    nb_rtx_fr = models.BigIntegerField()
    nb_rtx_rto = models.BigIntegerField()
    nb_unknown = models.BigIntegerField()
    nb_unnecessary_rtx_fr = models.BigIntegerField()
    nb_unnecessary_rtx_rto = models.BigIntegerField()
    rtt_avg = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_max = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_min = models.DecimalField(max_digits=10, decimal_places=3)
    rtt_samples = models.BigIntegerField()
    rtt_stdev = models.DecimalField(max_digits=10, decimal_places=3)
    segment_size_max = models.PositiveIntegerField()
    segment_size_min = models.PositiveIntegerField()

    class Meta:
        # Only two per subflow, one for each flow
        unique_together = (("subflow", "is_client_to_server"),)


class MPTCPSubflowFlowIsReinjection(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    subflow = models.ForeignKey(MPTCPSubflow)
    is_client_to_server = models.BooleanField()
    sent_time = models.DurationField()
    bytes = models.PositiveIntegerField()


class MPTCPSubflowFlowReinjectedOrig(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    subflow = models.ForeignKey(MPTCPSubflow)
    is_client_to_server = models.BooleanField()
    end_seq = models.BigIntegerField()
    begin_seq = models.BigIntegerField()
    times_reinjected = models.PositiveIntegerField()


class MPTCPSubflowFlowReinjectedOrigTimestamp(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    subflow = models.ForeignKey(MPTCPSubflow)
    is_client_to_server = models.BooleanField()
    sent_time = models.DurationField()


class MPTCPSubflowFlowTimestampRetrans(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    subflow = models.ForeignKey(MPTCPSubflow)
    is_client_to_server = models.BooleanField()
    delta = models.DurationField()
    time_from_first_sending = models.DurationField()
    time_from_last_retrans = models.DurationField()
    time_from_last_remote_packet = models.DurationField()


class MPTCPSubflowSOCKSInfo(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    subflow = models.OneToOneField(MPTCPSubflow, primary_key=True)
    socks_daddr = models.GenericIPAddressField()
    socks_port = models.PositiveIntegerField(validators=[validate_port_number])


class MPTCPSubflowMatch(models.Model):
    conn = models.ForeignKey(MPTCPConnection)
    subflow = models.OneToOneField(MPTCPSubflow, primary_key=True)
    tcp_conn_id = models.BigIntegerField()
    backup = models.BooleanField()
    duration = models.DurationField()
    start_time = models.DurationField()


""" All the logic about inserting data in the DB is below """


def _create_add_addrs_from_dict(add_addrs, mptcp_connection):
    for add_addr in add_addrs:
        MPTCPConnectionAddAddress.objects.create(
            conn=mptcp_connection,
            is_from_client=bool(add_addr[0]),
            advertised_addr=add_addr[1],
            sent_time=make_aware(datetime.fromtimestamp(float(add_addr[2])))
        )


def _create_rm_addrs_from_dict(rm_addrs, mptcp_connection):
    for rm_addr in rm_addrs:
        MPTCPConnectionRemoveAddress.objects.create(
            conn=mptcp_connection,
            is_from_client=bool(rm_addr[0]),
            kernel_subflow_id=rm_addr[1],
            sent_time=make_aware(datetime.fromtimestamp(float(rm_addr[2])))
        )


def _create_mptcp_connection_flow_rtt_from_dict(flow_dict, mptcp_connection,
                                                is_client_to_server):
    MPTCPConnectionFlowRTT.objects.create(
        conn=mptcp_connection,
        is_client_to_server=is_client_to_server,
        rtt_25p=flow_dict["rtt_25p"],
        rtt_75p=flow_dict["rtt_75p"],
        rtt_90p=flow_dict["rtt_90p"],
        rtt_95p=flow_dict["rtt_95p"],
        rtt_97p=flow_dict["rtt_97p"],
        rtt_98p=flow_dict["rtt_98p"],
        rtt_99p=flow_dict["rtt_99p"],
        rtt_avg=flow_dict["rtt_avg"],
        rtt_max=flow_dict["rtt_max"],
        rtt_median=flow_dict["rtt_median"],
        rtt_min=flow_dict["rtt_min"],
        rtt_samples=flow_dict["rtt_samples"],
        rtt_stdev=flow_dict["rtt_stdev"]
    )


def _create_mptcp_connection_flow_burst_from_dict(bursts, mptcp_connection,
                                                  is_client_to_server):
    for burst in bursts:
        MPTCPConnectionFlowBurst.objects.create(
            conn=mptcp_connection,
            is_client_to_server=is_client_to_server,
            subflow_id=burst[0],
            bytes=burst[1],
            packets=burst[2],
            duration=timedelta(seconds=float(burst[3])),
            start_time=make_aware(datetime.fromtimestamp(float(burst[4])))
        )


def _create_mptcp_connection_flow_retrans_dss_from_dict(retrans_dss,
                                                        mptcp_connection,
                                                        is_client_to_server):
    for dss in retrans_dss:
        MPTCPConnectionFlowRetransDSS.objects.create(
            conn=mptcp_connection,
            is_client_to_server=is_client_to_server,
            delta=dss[0],
            subflow_id=dss[1],
            dss=dss[2],
            delta_from_first_sending=dss[3],
            delta_from_last_retrans=dss[4],
            delta_from_last_remote_packet=dss[5]
        )


def _create_mptcp_connection_flow_from_dict(flow_dict, is_client_to_server,
                                            mptcp_connection):
    bursts = flow_dict.pop(BURSTS)
    retrans_dss = flow_dict.pop(RETRANS_DSS)
    MPTCPConnectionFlow.objects.create(
        conn=mptcp_connection,
        is_client_to_server=is_client_to_server,
        bytes_mptcptrace=flow_dict["bytes_mptcptrace"],
        reinj_bytes=flow_dict["reinj_bytes"],
        reinj_pc=flow_dict["reinj_pc"],
        time_last_ack_tcp=flow_dict["time_last_ack_tcp"],
        time_last_payload_tcp=flow_dict["time_last_payload_tcp"]
    )
    if "rtt_25p" in flow_dict:
        _create_mptcp_connection_flow_rtt_from_dict(
            flow_dict, mptcp_connection, is_client_to_server)

    _create_mptcp_connection_flow_burst_from_dict(
        bursts, mptcp_connection, is_client_to_server)
    _create_mptcp_connection_flow_retrans_dss_from_dict(
        retrans_dss, mptcp_connection, is_client_to_server)


def _create_mptcp_subflow_flow_complete_from_dict(flow_dict, mptcp_connection,
                                                  mptcp_subflow,
                                                  is_client_to_server):
    MPTCPSubflowFlowComplete.objects.create(
        conn=mptcp_connection,
        subflow=mptcp_subflow,
        is_client_to_server=is_client_to_server,
        maximum_in_flight_size=flow_dict["maximum_in_flight_size"],
        minimum_in_flight_size=flow_dict["minimum_in_flight_size"],
        nb_flow_control=flow_dict["nb_flow_control"],
        nb_network_duplicate=flow_dict["nb_network_duplicate"],
        nb_reordering=flow_dict["nb_reordering"],
        nb_rtx_fr=flow_dict["nb_rtx_fr"],
        nb_rtx_rto=flow_dict["nb_rtx_rto"],
        nb_unknown=flow_dict["nb_unknown"],
        nb_unnecessary_rtx_fr=flow_dict["nb_unnecessary_rtx_fr"],
        nb_unnecessary_rtx_rto=flow_dict["nb_unnecessary_rtx_rto"],
        rtt_avg=flow_dict["rtt_avg"],
        rtt_max=flow_dict["rtt_max"],
        rtt_min=flow_dict["rtt_min"],
        rtt_samples=flow_dict["rtt_samples"],
        rtt_stdev=flow_dict["rtt_stdev"],
        segment_size_max=flow_dict["segment_size_max"],
        segment_size_min=flow_dict["segment_size_min"]
    )


def _create_mptcp_subflow_flow_is_reinjection_from_dict(reinjections,
                                                        mptcp_connection,
                                                        mptcp_subflow,
                                                        is_client_to_server):
    for reinjection_time, reinjected_bytes in reinjections.items():
        MPTCPSubflowFlowIsReinjection.objects.create(
            conn=mptcp_connection,
            subflow=mptcp_subflow,
            is_client_to_server=is_client_to_server,
            sent_time=timedelta(seconds=float(reinjection_time)),
            bytes=reinjected_bytes
        )


def _create_mptcp_subflow_flow_reinjected_orig_from_dict(reinjected_orig,
                                                         mptcp_connection,
                                                         mptcp_subflow,
                                                         is_client_to_server):
    for reinject_seqs, times in reinjected_orig.items():
        MPTCPSubflowFlowReinjectedOrig.objects.create(
            conn=mptcp_connection,
            subflow=mptcp_subflow,
            is_client_to_server=is_client_to_server,
            end_seq=reinject_seqs[0],
            begin_seq=reinject_seqs[1],
            times_reinjected=times
        )


def _create_mptcp_subflow_flow_reinjected_orig_timestamp_from_dict(
    reinjected_orig_timestamps, mptcp_connection, mptcp_subflow,
        is_client_to_server):
    for timestamp in reinjected_orig_timestamps:
        MPTCPSubflowFlowReinjectedOrigTimestamp.objects.create(
            conn=mptcp_connection,
            subflow=mptcp_subflow,
            is_client_to_server=is_client_to_server,
            sent_time=timedelta(seconds=float(timestamp))
        )


def _create_mptcp_subflow_flow_timestamp_retrans_from_dict(
     timestamp_retrans, mptcp_connection, mptcp_subflow, is_client_to_server):
    for timestamps in timestamp_retrans:
        MPTCPSubflowFlowTimestampRetrans.objects.create(
            conn=mptcp_connection,
            subflow=mptcp_subflow,
            is_client_to_server=is_client_to_server,
            delta=timestamps[0],
            time_from_first_sending=timestamps[1],
            time_from_last_retrans=timestamps[2],
            time_from_last_remote_packet=timestamps[3]
        )


def _create_mptcp_subflow_flow_from_dict(flow_dict, is_client_to_server,
                                         is_tcp_complete, mptcp_connection,
                                         mptcp_subflow):
    MPTCPSubflowFlow.objects.create(
        conn=mptcp_connection,
        subflow=mptcp_subflow,
        is_client_to_server=is_client_to_server,
        bytes=flow_dict["bytes"],
        bytes_data=flow_dict["bytes_data"],
        bytes_retrans=flow_dict["bytes_retrans"],
        bytes_tcpip_hdr=flow_dict["bytes_tcpip_hdr"],
        nb_ack=flow_dict["nb_ack"],
        nb_fin=flow_dict["nb_fin"],
        nb_rst=flow_dict["nb_rst"],
        nb_syn=flow_dict["nb_syn"],
        packets=flow_dict["packets"],
        packets_outoforder=flow_dict["packets_outoforder"],
        packets_retrans=flow_dict["packets_retrans"],
        reinjected_orig_bytes=flow_dict["reinjected_orig_bytes"],
        reinjected_orig_packets=flow_dict["reinjected_orig_packets"],
        time_fin_ack_tcp=flow_dict["time_fin_ack_tcp"],
        time_first_ack=flow_dict["time_first_ack"],
        time_first_payload=flow_dict["time_first_payload"],
        time_last_ack_tcp=flow_dict["time_last_ack_tcp"],
        time_last_payload=flow_dict["time_last_payload"],
        time_last_payload_tcp=flow_dict["time_last_payload_tcp"],
        time_last_payload_with_retrans_tcp=flow_dict[
            "time_last_payload_with_retrans_tcp"]
    )
    if is_tcp_complete:
        _create_mptcp_subflow_flow_complete_from_dict(
            flow_dict, mptcp_connection, mptcp_subflow, is_client_to_server)

    _create_mptcp_subflow_flow_is_reinjection_from_dict(
        flow_dict[IS_REINJ], mptcp_connection, mptcp_subflow,
        is_client_to_server)
    _create_mptcp_subflow_flow_reinjected_orig_from_dict(
        flow_dict[REINJ_ORIG], mptcp_connection, mptcp_subflow,
        is_client_to_server)
    _create_mptcp_subflow_flow_reinjected_orig_timestamp_from_dict(
        flow_dict[REINJ_ORIG_TIMESTAMP], mptcp_connection, mptcp_subflow,
        is_client_to_server)
    _create_mptcp_subflow_flow_timestamp_retrans_from_dict(
        flow_dict[TIMESTAMP_RETRANS], mptcp_connection, mptcp_subflow,
        is_client_to_server)


def create_mptcp_connections_from_dict(analysis_dict, test, trace):
    for conn_id in analysis_dict:
        mptcp_conn_dict = analysis_dict[conn_id]
        add_addrs = mptcp_conn_dict.attr.pop(ADD_ADDRS)
        rm_addrs = mptcp_conn_dict.attr.pop(RM_ADDRS)
        mptcp_client2server_flow_dict = mptcp_conn_dict.attr.pop(C2S)
        mptcp_server2client_flow_dict = mptcp_conn_dict.attr.pop(S2C)
        mptcp_conn_dict.attr["duration"] = timedelta(
            seconds=mptcp_conn_dict.attr["duration"])
        if SOCKS_DADDR not in mptcp_conn_dict.attr:
            mptcp_conn_dict.attr[SOCKS_DADDR] = None
            mptcp_conn_dict.attr[SOCKS_PORT] = None

        mca = mptcp_conn_dict.attr
        mptcp_connection = MPTCPConnection.objects.create(
            trace=trace,
            conn_id=conn_id,
            duration=mca["duration"],
            start_time=mca["start_time"],
            max_idle_time=mca["max_idle_time"],
            max_idle_time_payload=mca["max_idle_time_payload"],
            socks_daddr=mca["socks_daddr"],
            socks_port=mca["socks_port"]
        )
        _create_add_addrs_from_dict(add_addrs, mptcp_connection)
        _create_rm_addrs_from_dict(rm_addrs, mptcp_connection)
        _create_mptcp_connection_flow_from_dict(
            mptcp_client2server_flow_dict, True, mptcp_connection)
        _create_mptcp_connection_flow_from_dict(
            mptcp_server2client_flow_dict, False, mptcp_connection)

        for subflow_id, subflow in mptcp_conn_dict.flows.items():
            sa = subflow.attr
            sa["tcp_conn_id"] = subflow.subflow_id
            mptcp_subflow = MPTCPSubflow.objects.create(
                conn=mptcp_connection,
                subflow_id=subflow_id,
                daddr=sa["daddr"],
                dport=sa["dport"],
                interface=sa["interface"],
                saddr=sa["saddr"],
                sport=sa["sport"],
                type=sa["type"],
                wscaledst=sa["wscaledst"],
                wscalesrc=sa["wscalesrc"]
            )
            if DURATION in sa:
                sa["duration"] = timedelta(seconds=sa["duration"])
                backup = bool(sa.get("backup", False))
                MPTCPSubflowMatch.objects.create(
                    conn=mptcp_connection,
                    subflow=mptcp_subflow,
                    tcp_conn_id=sa["tcp_conn_id"],
                    backup=backup,
                    duration=sa["duration"],
                    start_time=sa["start_time"]
                )

                if SOCKS_DADDR in sa:
                    MPTCPSubflowSOCKSInfo.objects.create(
                        conn=mptcp_connection,
                        subflow=mptcp_subflow,
                        socks_daddr=sa["socks_daddr"],
                        socks_port=sa["socks_port"]
                    )

                _create_mptcp_subflow_flow_from_dict(
                    sa[C2S], True, sa[TCP_COMPLETE], mptcp_connection,
                    mptcp_subflow)
                _create_mptcp_subflow_flow_from_dict(
                    sa[S2C], False, sa[TCP_COMPLETE], mptcp_connection,
                    mptcp_subflow)
