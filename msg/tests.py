from datetime import timedelta, datetime
import pytz

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.utils import timezone

from mptcpbench.mptests.tests import create_benchmark
from .models import MsgTest

import json


class PostMsgTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()

    def test_post_msg_ok(self):
        test_dict = {
            'benchmark_uuid': str(self.benchmark.uuid),
            'order': '0',
            'protocol_info': {"Coucou": 4},
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
                "port": 8008,
                "url": "superman.com",
                "query_size": 2500,
                "response_size": 750,
                "start_delay_query_response": 0,
                "nb_msgs": 75,
                "interval_time_ms": 200,
                "timeout_sec": 30,
            },
            'result': {
                'delays': [75, 130, 20, 78, 41, 10, 95, 69, 77, 790],
                'missed': 65,
                'success': 'True',
            },
        }
        test_json = json.dumps(test_dict)
        send_time = timezone.now()
        response = self.client.post(reverse("msg:create_test"), test_json, content_type="application/json")
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check that an instance of ConnectivityTest exists
        self.assertEqual(MsgTest.objects.count(), 1)
        test = MsgTest.objects.all()[0]
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
        self.assertEqual(test.config.port, 8008)
        self.assertEqual(test.config.url, "superman.com")
        self.assertEqual(test.config.query_size, 2500)
        self.assertEqual(test.config.response_size, 750)
        self.assertEqual(test.config.start_delay_query_response, 0)
        self.assertEqual(test.config.nb_msgs, 75)
        self.assertEqual(test.config.interval_time_ms, 200)
        self.assertEqual(test.config.timeout_sec, 30)
        self.assertEqual(test.result.msgdelay_set.count(), 10)
        self.assertEqual(max([x.delay for x in test.result.msgdelay_set.all()]), 790)
        self.assertEqual(min([x.delay for x in test.result.msgdelay_set.all()]), 10)
        self.assertEqual(test.result.missed, 65)
        self.assertEqual(test.result.success, True)
        self.assertEqual(test.protocol_info, {"Coucou": 4})
        self.assertTrue(timedelta(seconds=0) <= test.rcv_time - send_time <= timedelta(seconds=1))

    def test_post_msg_missing(self):
        test_dict = {
            'benchmark_uuid': str(self.benchmark.uuid),
            'order': '0',
            'protocol_info': {"Coucou": 4},
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
                "port": 8008,
                "url": "superman.com",
                "query_size": 2500,
                "response_size": 750,
                "start_delay_query_response": 0,
                "nb_msgs": 75,
                "interval_time_ms": 200,
                "timeout_sec": 30,
            },
            'result': {
                'delays': [75, 130, 20, 78, 41, 10, 95, 69, 77, 790],
                'missed': 65,
                'success': 'True',
            },
        }
        for k in test_dict.keys():
            poped_data = test_dict.pop(k)
            test_json = json.dumps(test_dict)
            response = self.client.post(reverse("msg:create_test"), test_json, content_type="application/json")
            # Check that the response is 400 BAD_REQUEST
            self.assertEqual(response.status_code, 400)
            # Check that no instance of ConnectivityTest exists
            self.assertEqual(MsgTest.objects.count(), 0)
            test_dict[k] = poped_data
