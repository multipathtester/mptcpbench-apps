from datetime import timedelta, datetime
import pytz

from django.core.urlresolvers import reverse
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from mptcpbench.mptests.tests import create_benchmark, get_quic_info
from .models import IPerfTest, IPerfConfig, IPerfResult, IPerfInterval

import json


class PostIPerfTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_post_iperf_ok(self):
        test_dict = {
            'benchmark_uuid': str(self.benchmark.uuid),
            'order': '0',
            'protocol_info': get_quic_info(),
            'start_time': "2018-01-16T11:41:40.744000+0100",
            'wait_time': '5.0',
            'duration': '37.421521',
            'wifi_bytes_received': 45,
            'wifi_bytes_sent': 78,
            'cell_bytes_received': 33,
            'cell_bytes_sent': 25,
            'multipath_service': 'aggregate',
            'protocol': 'QUIC',
            'config': {
                "download": True,
                "duration": 2,
                "port": 8008,
                "url": "superman.com",
            },
            'result': {
                'intervals': [
                    {
                        'intervalInSec': "0-1",
                        'transferredLastSecond': 20000,
                        'globalBandwidth': 20000,
                        'retransmittedLastSecond': 10,
                    },
                    {
                        'intervalInSec': "1-2",
                        'transferredLastSecond': 22000,
                        'globalBandwidth': 21000,
                        'retransmittedLastSecond': 770,
                    },
                ],
                'total_sent': 42000,
                'total_retrans': 780,
                'success': 'True',
            },
        }
        test_json = json.dumps(test_dict)
        send_time = timezone.now()
        response = self.client.post(reverse("iperf:create_test"), test_json, content_type="application/json")
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check that an instance of ConnectivityTest exists
        self.assertEqual(IPerfTest.objects.count(), 1)
        test = IPerfTest.objects.all()[0]
        self.assertEqual(test.benchmark, self.benchmark)
        self.assertEqual(test.order, 0)
        self.assertEqual(test.start_time, datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(test.wait_time, timedelta(seconds=5.0))
        self.assertEqual(test.duration, timedelta(seconds=37.421521))
        self.assertEqual(test.wifi_bytes_received, 45)
        self.assertEqual(test.wifi_bytes_sent, 78)
        self.assertEqual(test.cell_bytes_received, 33)
        self.assertEqual(test.cell_bytes_sent, 25)
        self.assertEqual(test.multipath_service, 'aggregate')
        self.assertEqual(test.protocol, "QUIC")
        self.assertEqual(test.config.download, True)
        self.assertEqual(test.config.duration, 2)
        self.assertEqual(test.config.port, 8008)
        self.assertEqual(test.config.url, "superman.com")
        self.assertEqual(test.result.intervals.count(), 2)
        self.assertEqual(max([x.transferredLastSecond for x in test.result.intervals.all()]), 22000)
        self.assertEqual(min([x.transferredLastSecond for x in test.result.intervals.all()]), 20000)
        self.assertEqual(max([x.globalBandwidth for x in test.result.intervals.all()]), 21000)
        self.assertEqual(min([x.globalBandwidth for x in test.result.intervals.all()]), 20000)
        self.assertEqual(max([x.retransmittedLastSecond for x in test.result.intervals.all()]), 770)
        self.assertEqual(min([x.retransmittedLastSecond for x in test.result.intervals.all()]), 10)
        self.assertEqual([x.intervalInSec for x in test.result.intervals.all()], ['0-1', '1-2'])
        self.assertEqual(test.result.success, True)
        self.assertEqual(test.result.total_sent, 42000)
        self.assertEqual(test.result.total_retrans, 780)
        self.assertTrue(test.quic_test_info is not None)
        self.assertTrue(timedelta(seconds=0) <= test.rcv_time - send_time <= timedelta(seconds=1))

    def test_post_iperf_missing(self):
        test_dict = {
            'benchmark_uuid': str(self.benchmark.uuid),
            'order': '0',
            'protocol_info': get_quic_info(),
            'start_time': "2018-01-16T11:41:40.744000+0100",
            'wait_time': '5.0',
            'duration': '37.421521',
            'wifi_bytes_received': 45,
            'wifi_bytes_sent': 78,
            'cell_bytes_received': 33,
            'cell_bytes_sent': 25,
            'protocol': 'QUIC',
            'config': {
                "download": True,
                "duration": 2,
                "port": 8008,
                "url": "superman.com",
            },
            'result': {
                'intervals': [
                    {
                        'intervalInSec': "0-1",
                        'transferredLastSecond': 20000,
                        'globalBandwidth': 20000,
                        'retransmittedLastSecond': 10,
                    },
                    {
                        'intervalInSec': "1-2",
                        'transferredLastSecond': 22000,
                        'globalBandwidth': 21000,
                        'retransmittedLastSecond': 770,
                    },
                ],
                'total_sent': 42000,
                'total_retrans': 780,
                'success': 'True',
            },
        }
        for k in test_dict.keys():
            poped_data = test_dict.pop(k)
            test_json = json.dumps(test_dict)
            response = self.client.post(reverse("iperf:create_test"), test_json, content_type="application/json")
            # Check that the response is 400 BAD_REQUEST
            self.assertEqual(response.status_code, 400)
            # Check that no instance of ConnectivityTest exists
            self.assertEqual(IPerfTest.objects.count(), 0)
            test_dict[k] = poped_data


class GetIPerfTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()
        config = IPerfConfig.objects.create(
            download=True,
            duration=2,
            port=8008,
            url="superman.com",
        )
        test = IPerfTest.objects.create(
            benchmark=self.benchmark,
            config=config,
            order=0,
            protocol_info=[
                {
                    "Time": "2018-02-12T15:47:32.519422Z",
                    "Connections": {
                        "9df47356d2fd833b": {
                            "Paths": {
                                "0": {
                                    "CongestionWindow": 40972,
                                },
                                "1": {
                                    "CongestionWindow": 40972,
                                },
                                "2": {
                                    "CongestionWindow": 40972,
                                    "InterfaceName": "en0"
                                },
                            },
                        },
                    }
                },
                {
                    "Time": "2018-02-12T15:47:35.686581Z",
                    "Connections": {
                        "9df47356d2fd833b": {
                            "Paths": {
                                "0": {
                                    "CongestionWindow": 10240000,
                                },
                                "1": {
                                    "CongestionWindow": 10240000,
                                },
                                "2": {
                                    "CongestionWindow": 10240000,
                                    "InterfaceName": "en0",
                                },
                                "3": {
                                    "CongestionWindow": 10240000,
                                    "InterfaceName": "pdp_ip0"
                                },
                            },
                        },
                    },
                },
            ],
            start_time=datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc),
            wait_time="5.0",
            duration="37.421521",
            wifi_bytes_received=45,
            wifi_bytes_sent=78,
            cell_bytes_received=33,
            cell_bytes_sent=25,
            multipath_service='aggregate',
            protocol='MPQUIC',
        )
        result = IPerfResult.objects.create(
            test=test,
            success=True,
            total_sent=501450,
            total_retrans=1234,
        )
        IPerfInterval.objects.create(
            result=result,
            intervalInSec="0-1",
            transferredLastSecond=200000,
            globalBandwidth=200000,
            retransmittedLastSecond=0,
        )
        IPerfInterval.objects.create(
            result=result,
            intervalInSec="1-2",
            transferredLastSecond=301450,
            globalBandwidth=260725,
            retransmittedLastSecond=1234,
        )

    def test_get_iperf_test(self):
        response = self.client.get(reverse("mptests:list_tests", kwargs={'benchmark_uuid': str(self.benchmark.uuid)}))
        json_response = json.loads(response.content.decode("UTF-8"))
        self.assertTrue('iperf' in json_response)
        iperfs_json = json_response['iperf']
        self.assertEqual(len(iperfs_json), 1)
        expected_json = {
            'start_time': '2018-01-16T10:41:40.744000Z',
            'wait_time': '5.0',
            'cell_bytes_received': 33,
            'order': 0,
            'graphs': [
                {
                    'y_label': 'Bytes',
                    'x_label': 'Time',
                    'data': [
                        {
                            'label': 'Path 1 Congestion Window',
                            'values': [
                                ['2018-02-12T15:47:32.519422Z', 40972],
                                ['2018-02-12T15:47:35.686581Z', 10240000],
                            ]
                        },
                        {
                            'label': 'Path 2 (WiFi) Congestion Window',
                            'values': [
                                ['2018-02-12T15:47:32.519422Z', 40972],
                                ['2018-02-12T15:47:35.686581Z', 10240000],
                            ]
                        },
                        {
                            'label': 'Path 3 (Cellular) Congestion Window',
                            'values': [
                                ['2018-02-12T15:47:35.686581Z', 10240000],
                            ]
                        },
                    ],
                },
            ],
            'config': {
                'download': True,
                'url': 'superman.com',
                'port': 8008,
                'duration': 2,
            },
            'result': {
                'error_msg': None,
                'intervals': [
                    {
                        'transferredLastSecond': 200000,
                        'globalBandwidth': 200000,
                        'intervalInSec': '0-1',
                        'retransmittedLastSecond': 0,
                    },
                    {
                        'transferredLastSecond': 301450,
                        'globalBandwidth': 260725,
                        'intervalInSec': '1-2',
                        'retransmittedLastSecond': 1234,
                    }
                ],
                'total_retrans': 1234,
                'total_sent': 501450,
                'success': True,
            },
            'protocol': 'MPQUIC',
            'cell_bytes_sent': 25,
            'wifi_bytes_received': 45,
            'duration': '37.421521',
            'multipath_service': 'aggregate',
            'wifi_bytes_sent': 78,
        }
        self.assertDictEqual(expected_json, iperfs_json[0])
