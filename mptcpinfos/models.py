from django.db import models


class MPTCPTestInfo(models.Model):
    # This is just a link between abstract tests and MPTCPConnectionInfo
    pass


class MPTCPConnectionInfo(models.Model):
    test_info = models.ForeignKey(MPTCPTestInfo, models.CASCADE,
                                  related_name="conns")
    time = models.DateTimeField()
    conn_id = models.PositiveIntegerField()
    flags = models.IntegerField()
    rxbytes = models.BigIntegerField()
    txbytes = models.BigIntegerField()
    subflowcount = models.PositiveSmallIntegerField()
    switchcount = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = (("test_info", "time", "conn_id"))


class MPTCPSubflowInfo(models.Model):
    conn = models.ForeignKey(MPTCPConnectionInfo, models.CASCADE,
                             related_name="subflows")
    subflow_id = models.PositiveSmallIntegerField()
    # Because of mobility, a path might not be assigned to any address...
    dst_ip = models.GenericIPAddressField(blank=True, null=True)
    src_ip = models.GenericIPAddressField(blank=True, null=True)
    interfaceindex = models.PositiveSmallIntegerField()
    isexpensive = models.BooleanField()
    rxbytes = models.BigIntegerField()
    txbytes = models.BigIntegerField()
    switches = models.PositiveSmallIntegerField()
    tcpi_last_outif = models.PositiveSmallIntegerField()

    tcpi_cell_rxbytes = models.BigIntegerField()
    tcpi_cell_rxpackets = models.BigIntegerField()
    tcpi_cell_txbytes = models.BigIntegerField()
    tcpi_cell_txpackets = models.BigIntegerField()
    tcpi_flags = models.IntegerField()  # Hope this would not have any issue...
    tcpi_if_cell = models.BooleanField()
    tcpi_if_wifi = models.BooleanField()
    tcpi_if_wifi_awdl = models.BooleanField()
    tcpi_if_wifi_infra = models.BooleanField()
    tcpi_if_wired = models.BooleanField()
    tcpi_options = models.PositiveSmallIntegerField()
    tcpi_rcv_mss = models.PositiveIntegerField()
    tcpi_rcv_nxt = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_rcv_space = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_rcv_wscale = models.PositiveSmallIntegerField()
    tcpi_rto = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_rttbest = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_rttcur = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_rttvar = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_rxbytes = models.BigIntegerField()
    tcpi_rxduplicatebytes = models.BigIntegerField()
    tcpi_rxoutoforderbytes = models.BigIntegerField()
    tcpi_rxpackets = models.BigIntegerField()
    tcpi_snd_bw = models.BigIntegerField()
    tcpi_snd_cwnd = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_snd_mss = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_snd_nxt = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_snd_sbbytes = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_snd_ssthresh = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_snd_wnd = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_snd_wscale = models.PositiveSmallIntegerField()
    tcpi_srtt = models.BigIntegerField()  # Shame on Django it does not provide unsigned integer...
    tcpi_state = models.PositiveSmallIntegerField()
    tcpi_synrexmits = models.PositiveSmallIntegerField()
    tcpi_txbytes = models.BigIntegerField()
    tcpi_txpackets = models.BigIntegerField()
    tcpi_txretransmitbytes = models.BigIntegerField()
    tcpi_txretransmitpackets = models.BigIntegerField()
    tcpi_txunacked = models.BigIntegerField()
    tcpi_wifi_rxbytes = models.BigIntegerField()
    tcpi_wifi_rxpackets = models.BigIntegerField()
    tcpi_wifi_txbytes = models.BigIntegerField()
    tcpi_wifi_txpackets = models.BigIntegerField()
    tcpi_wired_rxbytes = models.BigIntegerField()
    tcpi_wired_rxpackets = models.BigIntegerField()
    tcpi_wired_txbytes = models.BigIntegerField()
    tcpi_wired_txpackets = models.BigIntegerField()

    class Meta:
        unique_together = (("conn", "subflow_id"))
