from datetime import timedelta, datetime
import pytz

from django.core.urlresolvers import reverse
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from mptcpbench.mptests.tests import create_benchmark, get_quic_info
from .models import SimpleHttpGetTest, SimpleHttpGetConfig, SimpleHttpGetResult

import json


class PostSimpleHttpGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_post_simplehttpget_ok(self):
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
                'url': "https://superman.com:443/superFile",
            },
            'result': {
                'success': 'True',
            },
        }
        test_json = json.dumps(test_dict)
        send_time = timezone.now()
        response = self.client.post(reverse("simplehttpget:create_test"), test_json, content_type="application/json")
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check that an instance of ConnectivityTest exists
        self.assertEqual(SimpleHttpGetTest.objects.count(), 1)
        test = SimpleHttpGetTest.objects.all()[0]
        self.assertEqual(test.benchmark, self.benchmark)
        self.assertEqual(test.order, 0)
        self.assertEqual(test.start_time, datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(test.wait_time, timedelta(seconds=5.0))
        self.assertEqual(test.duration, timedelta(seconds=37.421521))
        self.assertEqual(test.wifi_bytes_received, 45)
        self.assertEqual(test.wifi_bytes_sent, 78)
        self.assertEqual(test.cell_bytes_received, 33)
        self.assertEqual(test.cell_bytes_sent, 25)
        self.assertEqual(test.multipath_service, "aggregate")
        self.assertEqual(test.protocol, "QUIC")
        self.assertEqual(test.config.url, "https://superman.com:443/superFile")
        self.assertEqual(test.result.success, True)
        self.assertTrue(test.quic_test_info is not None)
        self.assertTrue(timedelta(seconds=0) <= test.rcv_time - send_time <= timedelta(seconds=1))

    def test_post_simplehttpget_missing(self):
        test_dict = {
            'benchmark_uuid': str(self.benchmark.uuid),
            'order': '0',
            'start_time': "2018-01-16T11:41:40.744000+0100",
            'wait_time': '5.0',
            'duration': '37.421521',
            'wifi_bytes_received': 45,
            'wifi_bytes_sent': 78,
            'cell_bytes_received': 33,
            'cell_bytes_sent': 25,
            'multipath_service': 'aggregate',
            'protocol': 'QUIC',
            'protocol_info': get_quic_info(),
            'config': {
                'url': "https://superman.com:443/superFile",
            },
            'result': {
                'success': 'True',
            },
        }
        for k in test_dict.keys():
            poped_data = test_dict.pop(k)
            test_json = json.dumps(test_dict)
            response = self.client.post(reverse("simplehttpget:create_test"), test_json, content_type="application/json")
            # Check that the response is 400 BAD_REQUEST
            self.assertEqual(response.status_code, 400)
            # Check that no instance of ConnectivityTest exists
            self.assertEqual(SimpleHttpGetTest.objects.count(), 0)
            test_dict[k] = poped_data


class GetSimpleHttpGetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()
        config = SimpleHttpGetConfig.objects.create(
            url="superman.com",
        )
        test = SimpleHttpGetTest.objects.create(
            benchmark=self.benchmark,
            config=config,
            order=0,
            protocol_info=[
                {
                    "Time": "2018-02-12T15:47:32.519422Z",
                    "Connections": {
                        "9df47356d2fd833b": {
                            "Streams": {
                                "3": {
                                    "BytesRead": 40972,
                                },
                            },
                        },
                    }
                },
                {
                    "Time": "2018-02-12T15:47:35.686581Z",
                    "Connections": {
                        "9df47356d2fd833b": {
                            "Streams": {
                                "3": {
                                    "BytesRead": 10240000,
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
            protocol='QUIC',
        )
        SimpleHttpGetResult.objects.create(
            test=test,
            success=True,
        )

    def test_get_simplehttpget_list(self):
        response = self.client.get(reverse("mptests:list_tests", kwargs={'benchmark_uuid': str(self.benchmark.uuid)}))
        json_response = json.loads(response.content.decode("UTF-8"))
        self.assertTrue('simplehttpget' in json_response)
        simplehttpget_json = json_response['simplehttpget']
        self.assertEqual(len(simplehttpget_json), 1)
        expected_json = {
            'graphs': [
                {
                    'y_label': 'Bytes',
                    'x_label': 'Time',
                    'data': [
                        {
                            'values': [
                                ['2018-02-12T15:47:32.519422Z', 40972],
                                ['2018-02-12T15:47:35.686581Z', 10240000],
                            ],
                            'label': 'Bytes received',
                        },
                    ],
                },
            ],
            'wifi_bytes_received': 45,
            'wait_time': '5.0',
            'wifi_bytes_sent': 78,
            'config': {
                'url': 'superman.com',
            },
            'protocol': 'QUIC',
            'result': {
                'success': True,
                'error_msg': None,
            },
            'cell_bytes_sent': 25,
            'cell_bytes_received': 33,
            'order': 0,
            'multipath_service': 'aggregate',
            'duration': '37.421521',
            'start_time': '2018-01-16T10:41:40.744000Z',
        }
        self.assertTrue(expected_json in simplehttpget_json)
