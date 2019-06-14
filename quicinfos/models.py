from django.db import models


class QUICTestInfo(models.Model):
    # This is just a link between abstract tests and QUICConnectionInfo
    pass


class QUICConnectionInfo(models.Model):
    test_info = models.ForeignKey(QUICTestInfo, models.CASCADE,
                                  related_name="conns")
    time = models.DateTimeField()
    conn_id = models.CharField(max_length=16)  # 8 bytes in hexadecimal
    num_incoming_streams = models.IntegerField()
    num_outgoing_streams = models.IntegerField()
    max_path_id = models.IntegerField()
    num_active_paths = models.IntegerField()

    class Meta:
        unique_together = (("test_info", "time", "conn_id"))


class QUICFlowControlInfo(models.Model):
    conn = models.ForeignKey(QUICConnectionInfo, models.CASCADE,
                             related_name="flow_controls")
    is_conn_flow_control = models.BooleanField(default=False)
    stream_id = models.CharField(max_length=16)  # Because it is encoded as a string...
    bytes_sent = models.BigIntegerField()
    retransmitted_bytes = models.BigIntegerField()
    sending_window = models.BigIntegerField()
    last_window_update_time = models.DateTimeField()
    bytes_read = models.BigIntegerField()
    highest_received_byte = models.BigIntegerField()
    receive_window = models.BigIntegerField()
    receive_window_increment = models.BigIntegerField()
    max_receive_window_increment = models.BigIntegerField()

    class Meta:
        unique_together = (("conn", "is_conn_flow_control", "stream_id"))


class QUICPathInfo(models.Model):
    conn = models.ForeignKey(QUICConnectionInfo, models.CASCADE,
                             related_name="paths")
    path_id = models.CharField(max_length=16)  # Because it is encoded as a string...
    smoothed_rtt = models.BigIntegerField()  # Encoded in nanoseconds
    last_activity_time = models.DateTimeField()
    last_received_packet_number = models.BigIntegerField()
    least_unacked_packet_number = models.BigIntegerField()
    largest_acked_packet = models.BigIntegerField()
    largest_received_packet_with_ack = models.BigIntegerField()
    bytes_in_flight = models.BigIntegerField()
    rto_count = models.IntegerField()
    tlp_count = models.IntegerField()
    last_lost_time = models.DateTimeField()
    last_sent_time = models.DateTimeField()
    sent_packets = models.BigIntegerField()
    retransmissions = models.BigIntegerField()
    losses = models.BigIntegerField()
    largest_observed_packet_number = models.BigIntegerField()
    lower_limit_packet_number = models.BigIntegerField()
    largest_observed_receive_time = models.DateTimeField()
    ack_send_delay = models.BigIntegerField()  # Encoded in nanoseconds
    packets_received_since_last_ack = models.IntegerField()
    retransmittable_packets_received_since_last_ack = models.IntegerField()
    received_packets = models.BigIntegerField()
    congestion_window = models.BigIntegerField()
    # Because of mobility, a path might not be assigned to any address...
    local_port = models.PositiveIntegerField(blank=True, null=True)
    local_ip = models.GenericIPAddressField(blank=True, null=True)
    remote_port = models.PositiveIntegerField(blank=True, null=True)
    remote_ip = models.GenericIPAddressField(blank=True, null=True)
    rto_timeout = models.BigIntegerField()  # Encoded in nanoseconds
    interface_name = models.CharField(max_length=10)

    class Meta:
        unique_together = (("conn", "path_id"))
