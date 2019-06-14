from django.db import models

from mptcpbench.mptests.models import Benchmark


class NetConnectivity(models.Model):
    NONE = 'none'
    WIFI = 'wifi'
    CELL = 'cell'
    WIFICELL = 'wificell'
    CELLWIFI = 'cellwifi'

    TYPE_CHOICES = (
        (NONE, 'None'),
        (WIFI, 'WiFi'),
        (CELL, 'Cellular'),
        (WIFICELL, 'WiFi + Cellular'),
        (CELLWIFI, 'Cellular + WiFi'),
    )

    benchmark = models.ForeignKey(Benchmark, models.CASCADE)
    network_type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    timestamp = models.DateTimeField()
    wifi_network_name = models.CharField(max_length=100, blank=True, null=True)
    wifi_bssid = models.CharField(max_length=17, blank=True, null=True)
    cell_network_name = models.CharField(max_length=100, blank=True, null=True)
    cell_code = models.CharField(max_length=35, blank=True, null=True)
    cell_code_description = models.CharField(max_length=10, blank=True,
                                             null=True)
    cell_iso_country_code = models.CharField(max_length=3,  # To be sure
                                             blank=True, null=True)
    cell_operator_code = models.CharField(max_length=10,  # To be sure
                                          blank=True, null=True)


class IPAddress(models.Model):
    INTERFACE_CHOICES = (
        (NetConnectivity.WIFI, 'WiFi'),
        (NetConnectivity.CELL, 'Cellular')
    )

    net_connectivity = models.ForeignKey(NetConnectivity, models.CASCADE)
    ip = models.GenericIPAddressField(protocol='both')
    interface = models.CharField(max_length=4, choices=INTERFACE_CHOICES)
