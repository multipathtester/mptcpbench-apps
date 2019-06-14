from datetime import timedelta, datetime
import pytz

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.utils import timezone

from mptcpbench.mptests.tests import create_benchmark
from .models import NetConnectivity

import json


class PostNetConnectivityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()

    def test_post_wifi_connectivity_ok(self):
        nc_dict = [
            {
                "benchmark_uuid": str(self.benchmark.uuid),
                "wifi_ips": [
                    {"ip": "10.0.1.2"},
                    {"ip": "2001:db8::1"},
                ],
                "network_type": "wifi",
                "timestamp": "2018-01-16T11:41:40.744000+0100",
                "wifi_network_name": "A nice WiFi SSID",
                "wifi_bssid": "00:11:22:33:44:55",
            },
        ]
        nc_json = json.dumps(nc_dict)
        response = self.client.post(reverse("netconnectivities:create"), nc_json, content_type="application/json")
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check that an instance of ConnectivityTest exists
        self.assertEqual(NetConnectivity.objects.count(), 1)
        nc = NetConnectivity.objects.all()[0]
        self.assertEqual(nc.benchmark, self.benchmark)
        self.assertEqual(nc.network_type, NetConnectivity.WIFI)
        self.assertEqual(nc.timestamp, datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(nc.wifi_network_name, "A nice WiFi SSID")
        self.assertEqual(nc.wifi_bssid, "00:11:22:33:44:55")
        self.assertEqual(nc.ipaddress_set.count(), 2)
        self.assertEqual(set([x.ip for x in nc.ipaddress_set.all()]), set(["10.0.1.2", "2001:db8::1"]))
        for ipa in nc.ipaddress_set.all():
            self.assertEqual(ipa.interface, NetConnectivity.WIFI)

    def test_post_cell_connectivity_ok(self):
        nc_dict = [
            {
                "benchmark_uuid": str(self.benchmark.uuid),
                "cell_ips": [
                    {"ip": "7.5.3.1"},
                ],
                "network_type": "cell",
                "timestamp": "2018-01-16T11:41:40.744000+0100",
                "cell_network_name": "A nice cellular operator",
                "cell_code": "CTRadioAccessTechnologyCDMAEVDORev0",
                "cell_code_description": "EVD0 (2G)",
                "cell_iso_country_code": "BE",
                "cell_operator_code": "206-10",
            },
        ]
        nc_json = json.dumps(nc_dict)
        response = self.client.post(reverse("netconnectivities:create"), nc_json, content_type="application/json")
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check that an instance of ConnectivityTest exists
        self.assertEqual(NetConnectivity.objects.count(), 1)
        nc = NetConnectivity.objects.all()[0]
        self.assertEqual(nc.benchmark, self.benchmark)
        self.assertEqual(nc.network_type, NetConnectivity.CELL)
        self.assertEqual(nc.timestamp, datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(nc.cell_network_name, "A nice cellular operator")
        self.assertEqual(nc.cell_code, "CTRadioAccessTechnologyCDMAEVDORev0")
        self.assertEqual(nc.cell_code_description, "EVD0 (2G)")
        self.assertEqual(nc.cell_iso_country_code, "BE")
        self.assertEqual(nc.cell_operator_code, "206-10")
        self.assertEqual(nc.ipaddress_set.count(), 1)
        self.assertEqual(set([x.ip for x in nc.ipaddress_set.all()]), set(["7.5.3.1"]))
        for ipa in nc.ipaddress_set.all():
            self.assertEqual(ipa.interface, NetConnectivity.CELL)

    def test_post_wificell_connectivity_ok(self):
        nc_dict = [
            {
                "benchmark_uuid": str(self.benchmark.uuid),
                "cell_ips": [
                    {"ip": "7.5.3.1"},
                ],
                "network_type": "wificell",
                "timestamp": "2018-01-16T11:41:40.744000+0100",
                "cell_network_name": "A nice cellular operator",
                "cell_code": "CTRadioAccessTechnologyCDMAEVDORev0",
                "cell_code_description": "EVD0 (2G)",
                "cell_iso_country_code": "BE",
                "cell_operator_code": "206-10",
                "wifi_ips": [
                    {"ip": "10.0.1.2"},
                    {"ip": "2001:db8::1"},
                ],
                "wifi_network_name": "A nice WiFi SSID",
                "wifi_bssid": "00:11:22:33:44:55",
            },
        ]
        nc_json = json.dumps(nc_dict)
        response = self.client.post(reverse("netconnectivities:create"), nc_json, content_type="application/json")
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check that an instance of ConnectivityTest exists
        self.assertEqual(NetConnectivity.objects.count(), 1)
        nc = NetConnectivity.objects.all()[0]
        self.assertEqual(nc.benchmark, self.benchmark)
        self.assertEqual(nc.network_type, NetConnectivity.WIFICELL)
        self.assertEqual(nc.timestamp, datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(nc.cell_network_name, "A nice cellular operator")
        self.assertEqual(nc.cell_code, "CTRadioAccessTechnologyCDMAEVDORev0")
        self.assertEqual(nc.cell_code_description, "EVD0 (2G)")
        self.assertEqual(nc.cell_iso_country_code, "BE")
        self.assertEqual(nc.cell_operator_code, "206-10")
        self.assertEqual(nc.ipaddress_set.count(), 3)
        self.assertEqual(set([x.ip for x in nc.ipaddress_set.filter(interface=NetConnectivity.CELL)]), set(["7.5.3.1"]))
        self.assertEqual(nc.wifi_network_name, "A nice WiFi SSID")
        self.assertEqual(nc.wifi_bssid, "00:11:22:33:44:55")
        self.assertEqual(set([x.ip for x in nc.ipaddress_set.filter(interface=NetConnectivity.WIFI)]), set(["10.0.1.2", "2001:db8::1"]))

    def test_post_wificell_connectivity_missing(self):
        nc_dict = [
            {
                "benchmark_uuid": str(self.benchmark.uuid),
                "cell_ips": [
                    {"ip": "7.5.3.1"},
                ],
                "network_type": "wificell",
                "timestamp": "2018-01-16T11:41:40.744000+0100",
                "cell_network_name": "A nice cellular operator",
                "cell_code": "CTRadioAccessTechnologyCDMAEVDORev0",
                "cell_code_description": "EVD0 (2G)",
                "cell_iso_country_code": "BE",
                "cell_operator_code": "206-10",
                "wifi_ips": [
                    {"ip": "10.0.1.2"},
                    {"ip": "2001:db8::1"},
                ],
                "wifi_network_name": "A nice WiFi SSID",
                "wifi_bssid": "00:11:22:33:44:55",
            },
        ]
        for k in nc_dict[0].keys():
            poped_data = nc_dict[0].pop(k)
            nc_json = json.dumps(nc_dict)
            response = self.client.post(reverse("netconnectivities:create"), nc_json, content_type="application/json")
            # Check that the response is 400 BAD_REQUEST
            self.assertEqual(response.status_code, 400)
            # Check that no instance of NetConnectivity exists
            self.assertEqual(NetConnectivity.objects.count(), 0)
            nc_dict[0][k] = poped_data

    def test_post_unknown_connectivity_ko(self):
        nc_dict = [
            {
                "benchmark_uuid": str(self.benchmark.uuid),
                "cell_ips": [
                    {"ip": "7.5.3.1"},
                ],
                "network_type": "bloup",
                "timestamp": "2018-01-16T11:41:40.744000+0100",
                "cell_network_name": "A nice cellular operator",
                "cell_code": "CTRadioAccessTechnologyCDMAEVDORev0",
                "cell_code_description": "EVD0 (2G)",
                "cell_iso_country_code": "BE",
                "cell_operator_code": "206-10",
                "wifi_ips": [
                    {"ip": "10.0.1.2"},
                    {"ip": "2001:db8::1"},
                ],
                "wifi_network_name": "A nice WiFi SSID",
                "wifi_bssid": "00:11:22:33:44:55",
            },
        ]
        nc_json = json.dumps(nc_dict)
        response = self.client.post(reverse("netconnectivities:create"), nc_json, content_type="application/json")
        # Check that the response is 400 BAD_REQUEST
        self.assertEqual(response.status_code, 400)
        # Check that no instance of NetConnectivity exists
        self.assertEqual(NetConnectivity.objects.count(), 0)
