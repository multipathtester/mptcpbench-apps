from datetime import timedelta, datetime
import pytz

from django.core.urlresolvers import reverse
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from mptcpbench.mptests.tests import create_benchmark, get_mptcp_info, \
    get_quic_info
from .models import ConnectivityTest, ConnectivityResult, ConnectivityDelay, \
    ConnectivityConfig

import json


class PostConnectivityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_post_connectivity_ok(self):
        test_dict = {
            'benchmark_uuid': str(self.benchmark.uuid),
            'order': '0',
            'protocol_info': get_mptcp_info(),
            'start_time': "2018-01-16T11:41:40.744000+0100",
            'wait_time': '5.0',
            'duration': '37.421521',
            'wifi_bytes_received': 45,
            'wifi_bytes_sent': 78,
            'cell_bytes_received': 33,
            'cell_bytes_sent': 25,
            'multipath_service': 'aggregate',
            'protocol': 'MPTCP',
            'config': {
                'url': "superman.com",
                'port': '443',
            },
            'result': {
                'delays': ['25.876', '150.112', '75.844'],
                'success': 'True',
            },
        }
        test_json = json.dumps(test_dict)
        send_time = timezone.now()
        response = self.client.post(reverse("connectivity:create_test"), test_json, content_type="application/json")
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check that an instance of ConnectivityTest exists
        self.assertEqual(ConnectivityTest.objects.count(), 1)
        test = ConnectivityTest.objects.all()[0]
        self.assertEqual(test.benchmark, self.benchmark)
        self.assertEqual(test.order, 0)
        self.assertEqual(test.start_time, datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(test.wait_time, timedelta(seconds=5.0))
        self.assertEqual(test.duration, timedelta(seconds=37.421521))
        self.assertEqual(test.wifi_bytes_received, 45)
        self.assertEqual(test.wifi_bytes_sent, 78)
        self.assertEqual(test.cell_bytes_received, 33)
        self.assertEqual(test.cell_bytes_sent, 25)
        self.assertEqual(test.protocol, "MPTCP")
        self.assertEqual(test.config.url, "superman.com")
        self.assertEqual(test.config.port, 443)
        self.assertEqual(test.result.delays.count(), 3)
        self.assertEqual(max([d.delay for d in test.result.delays.all()]), 150.112)
        self.assertEqual(min([d.delay for d in test.result.delays.all()]), 25.876)
        self.assertEqual(test.result.success, True)
        self.assertTrue(test.mptcp_test_info is not None)
        self.assertTrue(timedelta(seconds=0) <= test.rcv_time - send_time <= timedelta(seconds=1))

    def test_post_connectivity_missing(self):
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
                'url': "superman.com",
                'port': '443',
            },
            'result': {
                'delays': ['25.876', '150.112', '75.844'],
                'success': 'True',
            },
        }
        for k in test_dict.keys():
            poped_data = test_dict.pop(k)
            test_json = json.dumps(test_dict)
            response = self.client.post(reverse("connectivity:create_test"), test_json, content_type="application/json")
            # Check that the response is 400 BAD_REQUEST
            self.assertEqual(response.status_code, 400)
            # Check that no instance of ConnectivityTest exists
            self.assertEqual(ConnectivityTest.objects.count(), 0)
            test_dict[k] = poped_data


class GetConnectivityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()
        config = ConnectivityConfig.objects.create(
            url="superman.com",
            port=443,
        )
        test = ConnectivityTest.objects.create(
            benchmark=self.benchmark,
            config=config,
            order=0,
            protocol_info=get_quic_info(),
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
        result = ConnectivityResult.objects.create(
            test=test,
            success=True,
        )
        ConnectivityDelay.objects.create(
            result=result,
            delay=25.876,
        )
        ConnectivityDelay.objects.create(
            result=result,
            delay=150.112,
        )
        ConnectivityDelay.objects.create(
            result=result,
            delay=75.844,
        )

    def test_get_connectivity_list(self):
        response = self.client.get(reverse("mptests:list_tests", kwargs={'benchmark_uuid': str(self.benchmark.uuid)}))
        json_response = json.loads(response.content.decode("UTF-8"))
        self.assertTrue('connectivity' in json_response)
        connectivities_json = json_response['connectivity']
        self.assertEqual(len(connectivities_json), 1)
        expected_json = {
            'result': {
                'success': True,
                'delays': [25.876, 150.112, 75.844],
                'error_msg': None,
            },
            'cell_bytes_sent': 25,
            'cell_bytes_received': 33,
            'protocol': 'QUIC',
            'config': {
                'url': 'superman.com',
                'port': 443,
            },
            'start_time': '2018-01-16T10:41:40.744000Z',
            'wifi_bytes_received': 45,
            'wait_time': '5.0',
            'order': 0,
            'multipath_service': 'aggregate',
            'duration': '37.421521',
            'wifi_bytes_sent': 78,
        }
        self.assertTrue(expected_json in connectivities_json)
