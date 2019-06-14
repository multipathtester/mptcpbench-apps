from . import models
from django.test import Client, TestCase, TransactionTestCase

import json
import urllib


class PostTestResultTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_result_test(self):
        # Create the JSON
        json_dict = {
            "bench": {
                "config": {
                    "file_name": "random_10MB",
                    "server_url": "multipath-tcp.org",
                },
                "name": "simple_http_get",
            },
            "client_analysis": False,
            "client_interfaces": [
                {
                    "name": "eth0",
                    "is_active": True,
                    "is_backup": False,
                    "ips": [
                        {
                            "type": "ipv4",
                            "addr": "192.168.1.1",
                        },
                        {
                            "type": "ipv6",
                            "addr": "::1",
                        },
                    ],
                },
                {
                    "name": "wlan0",
                    "is_active": True,
                    "is_backup": False,
                    "ips": [
                        {
                            "type": "ipv4",
                            "addr": "1.2.3.4",
                        },
                        {
                            "type": "ipv6",
                            "addr": "2001::1",
                        },
                    ],
                },
                {
                    "name": "rmnet0",
                    "is_active": True,
                    "is_backup": True,
                    "ips": [
                        {
                            "type": "ipv4",
                            "addr": "2.2.3.4",
                        },
                        {
                            "type": "ipv6",
                            "addr": "2001:db8::1",
                        },
                    ],
                }
            ],
            "client_machine": {
                "host_os": "Linux superGator 4.2.0-30-generic #36-Ubuntu SMP Fri Feb 26 00:58:07 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux",
                "mptcp_version": "0.90",
                "tag": "123456789azertyuiopmlkjhgfdsqwxcvbn",
            },
            "client_sysctl": {
                "net.ipv4.tcp_abort_on_overflow": "0",
                "net.ipv4.tcp_adv_win_scale": "1",
                "net.ipv4.tcp_allowed_congestion_control": "cubic reno",
                "net.ipv4.tcp_app_win": "31",
                "net.ipv4.tcp_autocorking": "1",
                "net.ipv4.tcp_available_congestion_control": "cubic reno",
                "net.ipv4.tcp_base_mss": "1024",
                "net.ipv4.tcp_challenge_ack_limit": "100",
                "net.ipv4.tcp_congestion_control": "cubic",
                "net.ipv4.tcp_dsack": "1",
                "net.ipv4.tcp_early_retrans": "1",
                "net.ipv4.tcp_ecn": "2",
                "net.ipv4.tcp_fack": "1",
                "net.ipv4.tcp_fastopen": "1",
                "net.ipv4.tcp_fastopen_key": "00000000-00000000-00000000-00000000",
                "net.ipv4.tcp_fin_timeout": "30",
                "net.ipv4.tcp_frto": "2",
                "net.ipv4.tcp_fwmark_accept": "0",
                "net.ipv4.tcp_invalid_ratelimit": "500",
                "net.ipv4.tcp_keepalive_intvl": "75",
                "net.ipv4.tcp_keepalive_probes": "9",
                "net.ipv4.tcp_keepalive_time": "1200",
                "net.ipv4.tcp_limit_output_bytes": "131072",
                "net.ipv4.tcp_low_latency": "0",
                "net.ipv4.tcp_max_orphans": "16384",
                "net.ipv4.tcp_max_reordering": "300",
                "net.ipv4.tcp_max_syn_backlog": "4096",
                "net.ipv4.tcp_max_tw_buckets": "5000",
                "net.ipv4.tcp_mem": "91959        122613  183918",
                "net.ipv4.tcp_min_tso_segs": "2",
                "net.ipv4.tcp_moderate_rcvbuf": "1",
                "net.ipv4.tcp_mtu_probing": "1",
                "net.ipv4.tcp_no_metrics_save": "1",
                "net.ipv4.tcp_notsent_lowat": "-1",
                "net.ipv4.tcp_orphan_retries": "0",
                "net.ipv4.tcp_probe_interval": "600",
                "net.ipv4.tcp_probe_threshold": "8",
                "net.ipv4.tcp_reordering": "3",
                "net.ipv4.tcp_retrans_collapse": "1",
                "net.ipv4.tcp_retries1": "3",
                "net.ipv4.tcp_retries2": "15",
                "net.ipv4.tcp_rfc1337": "0",
                "net.ipv4.tcp_rmem": "4096        87380   67108864",
                "net.ipv4.tcp_sack": "1",
                "net.ipv4.tcp_slow_start_after_idle": "1",
                "net.ipv4.tcp_stdurg": "0",
                "net.ipv4.tcp_syn_retries": "6",
                "net.ipv4.tcp_synack_retries": "5",
                "net.ipv4.tcp_syncookies": "1",
                "net.ipv4.tcp_thin_dupack": "0",
                "net.ipv4.tcp_thin_linear_timeouts": "0",
                "net.ipv4.tcp_timestamps": "1",
                "net.ipv4.tcp_tso_win_divisor": "3",
                "net.ipv4.tcp_tw_recycle": "0",
                "net.ipv4.tcp_tw_reuse": "1",
                "net.ipv4.tcp_window_scaling": "1",
                "net.ipv4.tcp_wmem": "4096        65536   67108864",
                "net.ipv4.tcp_workaround_signed_windows": "0",
                "net.ipv4.udp_mem": "91959        122613  183918",
                "net.ipv4.udp_rmem_min": "4096",
                "net.ipv4.udp_wmem_min": "4096",
                "net.ipv4.xfrm4_gc_thresh": "32768",
                "net.mptcp.mptcp_binder_gateways": "",
                "net.mptcp.mptcp_checksum": "1",
                "net.mptcp.mptcp_debug": "0",
                "net.mptcp.mptcp_enabled": "1",
                "net.mptcp.mptcp_path_manager": "fullmesh",
                "net.mptcp.mptcp_scheduler": "default",
                "net.mptcp.mptcp_syn_retries": "3",
            },
            "client_version": "0.1-beta-test",
            "result": {
                "run_time": "21.968741",
            },
            "server_interfaces": [
                {
                    "name": "eth0",
                    "is_active": True,
                    "is_backup": False,
                    "ips": [
                        {
                            "type": "ipv4",
                            "addr": "192.168.1.1",
                        },
                        {
                            "type": "ipv6",
                            "addr": "::1",
                        },
                    ],
                },
            ],
            "server_machine": {
                "host_os": "Linux superServor 4.1.0-mptcp #59 SMP Thu Dec 24 10:57:44 CET 2015 x86_64 GNU/Linux",
                "mptcp_version": "0.90",
                "tag": "4694764687serverHHOJ9ZJMZ908P2KLNKQs",
            },
            "server_sysctl": {
                "net.ipv4.tcp_abort_on_overflow": "0",
                "net.ipv4.tcp_adv_win_scale": "1",
                "net.ipv4.tcp_allowed_congestion_control": "cubic reno",
                "net.ipv4.tcp_app_win": "31",
                "net.ipv4.tcp_autocorking": "1",
                "net.ipv4.tcp_available_congestion_control": "cubic reno",
                "net.ipv4.tcp_base_mss": "1024",
                "net.ipv4.tcp_challenge_ack_limit": "100",
                "net.ipv4.tcp_congestion_control": "cubic",
                "net.ipv4.tcp_dsack": "1",
                "net.ipv4.tcp_early_retrans": "1",
                "net.ipv4.tcp_ecn": "2",
                "net.ipv4.tcp_fack": "1",
                "net.ipv4.tcp_fastopen": "1",
                "net.ipv4.tcp_fastopen_key": "00000000-00000000-00000000-00000000",
                "net.ipv4.tcp_fin_timeout": "30",
                "net.ipv4.tcp_frto": "2",
                "net.ipv4.tcp_fwmark_accept": "0",
                "net.ipv4.tcp_invalid_ratelimit": "500",
                "net.ipv4.tcp_keepalive_intvl": "75",
                "net.ipv4.tcp_keepalive_probes": "9",
                "net.ipv4.tcp_keepalive_time": "1200",
                "net.ipv4.tcp_limit_output_bytes": "131072",
                "net.ipv4.tcp_low_latency": "0",
                "net.ipv4.tcp_max_orphans": "16384",
                "net.ipv4.tcp_max_reordering": "300",
                "net.ipv4.tcp_max_syn_backlog": "4096",
                "net.ipv4.tcp_max_tw_buckets": "5000",
                "net.ipv4.tcp_mem": "91959        122613  183918",
                "net.ipv4.tcp_min_tso_segs": "2",
                "net.ipv4.tcp_moderate_rcvbuf": "1",
                "net.ipv4.tcp_mtu_probing": "1",
                "net.ipv4.tcp_no_metrics_save": "1",
                "net.ipv4.tcp_notsent_lowat": "-1",
                "net.ipv4.tcp_orphan_retries": "0",
                "net.ipv4.tcp_probe_interval": "600",
                "net.ipv4.tcp_probe_threshold": "8",
                "net.ipv4.tcp_reordering": "3",
                "net.ipv4.tcp_retrans_collapse": "1",
                "net.ipv4.tcp_retries1": "3",
                "net.ipv4.tcp_retries2": "15",
                "net.ipv4.tcp_rfc1337": "0",
                "net.ipv4.tcp_rmem": "4096        87380   67108864",
                "net.ipv4.tcp_sack": "1",
                "net.ipv4.tcp_slow_start_after_idle": "1",
                "net.ipv4.tcp_stdurg": "0",
                "net.ipv4.tcp_syn_retries": "6",
                "net.ipv4.tcp_synack_retries": "5",
                "net.ipv4.tcp_syncookies": "1",
                "net.ipv4.tcp_thin_dupack": "0",
                "net.ipv4.tcp_thin_linear_timeouts": "0",
                "net.ipv4.tcp_timestamps": "1",
                "net.ipv4.tcp_tso_win_divisor": "3",
                "net.ipv4.tcp_tw_recycle": "0",
                "net.ipv4.tcp_tw_reuse": "1",
                "net.ipv4.tcp_window_scaling": "1",
                "net.ipv4.tcp_wmem": "4096        65536   67108864",
                "net.ipv4.tcp_workaround_signed_windows": "0",
                "net.ipv4.udp_mem": "91959        122613  183918",
                "net.ipv4.udp_rmem_min": "4096",
                "net.ipv4.udp_wmem_min": "4096",
                "net.ipv4.xfrm4_gc_thresh": "32768",
                "net.mptcp.mptcp_binder_gateways": "",
                "net.mptcp.mptcp_checksum": "1",
                "net.mptcp.mptcp_debug": "0",
                "net.mptcp.mptcp_enabled": "1",
                "net.mptcp.mptcp_path_manager": "fullmesh",
                "net.mptcp.mptcp_scheduler": "server",
                "net.mptcp.mptcp_syn_retries": "3",
            },
            "server_version": "0.1-beta-test",
            "start_time": "1457621750.239237",
            "uuid": "123e4567-e89b-12d3-a456-426655440000",
        }
        json_to_send = json.dumps(json_dict)
        response = self.client.post("/collect/save_test/", json_to_send, content_type="application/json")
        json_response = json.loads(response.content.decode("UTF-8"))
        # Check that the response is 200 OK.
        # print(json_response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.BenchTest.objects.all().count(), 1)
        self.assertEqual(models.Interface.objects.all().count(), 3)  # Because server use a already present interface
        test = models.BenchTest.objects.all()[0]
        self.assertEqual(models.Interface.objects.filter(client_tests=test).count(), 3)
        self.assertEqual(models.Interface.objects.filter(server_tests=test).count(), 1)
        # self.assertEqual(models.MPTCPConnection.objects.all().count(), 1)
        # self.assertEqual(models.MPTCPSubflow.objects.all().count(), 2)
        # mptcp_connection = models.MPTCPConnection.objects.all()[0]
        # self.assertEqual(models.MPTCPSubflow.objects.filter(mptcp_conn=mptcp_connection).count(), 2)

        # params = urllib.parse.urlencode(json_response)
        # response_client_upload = self.client.post("/collect/upload_client_trace/?" + params, open("mptcp-dump_20150405_002006.pcap", 'rb').read(), content_type="application/octet-stream")
        # response_client_upload_dict = json.loads(response_client_upload.content.decode("UTF-8"))
        # self.assertEqual(response_client_upload_dict, {"result": "OK"})
        # response_server_upload = self.client.post("/collect/upload_server_trace/?" + params, open("mptcp-dump_20150405_002006.pcap", 'rb').read(), content_type="application/octet-stream")
        # response_server_upload_dict = json.loads(response_server_upload.content.decode("UTF-8"))
        # self.assertEqual(response_server_upload_dict, {"result": "OK"})
        # # Don't think test should be queried again
        # test = models.Test.objects.all()[0]


    def test_post_result_smartphone_test(self):
        # Create the JSON
        json_dict = {
            "bench": {
                "config": {
                    "file_name": "random_10MB",
                    "server_url": "multipath-tcp.org",
                },
                "name": "simple_http_get",
            },
            "config_name": "MPTCP",
            "device_id": "1234567890abcdef",
            "result": {
                "run_time": "21.968741",
            },
            "server_ip": "1.2.3.4",
            "smartphone": "true",
            "start_time": "1457621750.239237",
        }
        json_to_send = json.dumps(json_dict)
        response = self.client.post("/collect/save_test/", json_to_send, content_type="application/json")
        # json_response = json.loads(response.content.decode("UTF-8"))
        # Check that the response is 200 OK.
        # print(json_response)
        self.assertEqual(response.status_code, 200)

    # def test_celery(self):
        # pass
        # from .tasks import analyze_trace
        # result = analyze_trace.delay("Super testor", True)

        # XXX It seems with a test database, this will always timeout...
        # print(result.get(timeout=5))


    # def test_get_next_experiments(self):
        # response = self.client.get("/collect/get_next_experiments/")
        # json_response = json.loads(response.content.decode("UTF-8"))
