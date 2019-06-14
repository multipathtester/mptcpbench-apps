from datetime import timedelta, datetime
import pytz

from django.core.urlresolvers import reverse
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from mptcpbench.mptests.tests import create_benchmark, get_quic_info
from .models import StreamTest, StreamConfig, StreamResult, StreamDelay

import json


class PostStreamTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_post_stream_ok(self):
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
                'url': "https://superman.com:5202",
                'port': "5202",
                'upload_chunk_size': 2000,
                'download_chunk_size': 2000,
                'duration': '14.0',
                'upload_interval_time': "0.1",
                'download_interval_time': "0.1",
            },
            'result': {
                'success': 'True',
                'error_msg': "Exiting client main with error InternalError: deadline exceeded",
                'upload_delays': [
                    {"time": "2018-01-16T11:41:40.744000+0100", "delay": "0.050500"},
                    {"time": "2018-01-16T11:41:40.844000+0100", "delay": "0.020900"},
                ],
                'download_delays': [
                    {"time": "2018-01-16T11:41:40.744000+0100", "delay": "0.050900"},
                    {"time": "2018-01-16T11:41:40.844000+0100", "delay": "0.020500"},
                ],
            },
        }
        test_json = json.dumps(test_dict)
        send_time = timezone.now()
        response = self.client.post(reverse("stream:create_test"), test_json, content_type="application/json")
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check that an instance of ConnectivityTest exists
        self.assertEqual(StreamTest.objects.count(), 1)
        test = StreamTest.objects.all()[0]
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
        self.assertEqual(test.config.url, "https://superman.com:5202")
        self.assertEqual(test.config.port, 5202),
        self.assertEqual(test.config.upload_chunk_size, 2000)
        self.assertEqual(test.config.download_chunk_size, 2000)
        self.assertEqual(test.config.duration, timedelta(seconds=14.0))
        self.assertEqual(test.config.upload_interval_time, timedelta(seconds=0.1))
        self.assertEqual(test.config.download_interval_time, timedelta(seconds=0.1))
        self.assertEqual(test.result.success, True)
        self.assertEqual(test.result.error_msg, "Exiting client main with error InternalError: deadline exceeded")
        self.assertEqual(test.result.delays.count(), 4)
        self.assertEqual(test.result.delays.filter(upload=True).count(), 2)
        self.assertEqual(test.result.delays.filter(upload=False).count(), 2)
        self.assertEqual(max([x.delay for x in test.result.delays.filter(upload=True)]), timedelta(seconds=0.050500))
        self.assertEqual(min([x.delay for x in test.result.delays.filter(upload=True)]), timedelta(seconds=0.020900))
        self.assertEqual(max([x.delay for x in test.result.delays.filter(upload=False)]), timedelta(seconds=0.050900))
        self.assertEqual(min([x.delay for x in test.result.delays.filter(upload=False)]), timedelta(seconds=0.020500))
        self.assertTrue(test.quic_test_info is not None)
        self.assertTrue(timedelta(seconds=0) <= test.rcv_time - send_time <= timedelta(seconds=1))

    def test_post_stream_missing(self):
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
                'url': "https://superman.com:5202",
                'port': "5202",
                'upload_chunk_size': 2000,
                'download_chunk_size': 2000,
                'duration': '14.0',
                'upload_interval_time': "0.1",
                'download_interval_time': "0.1",
            },
            'result': {
                'success': 'True',
                'error_msg': "Exiting client main with error InternalError: deadline exceeded",
                'upload_delays': [
                    {"time": "2018-01-16T11:41:40.744000+0100", "delay": "0.050500"},
                    {"time": "2018-01-16T11:41:40.844000+0100", "delay": "0.020900"},
                ],
                'download_delays': [
                    {"time": "2018-01-16T11:41:40.744000+0100", "delay": "0.050900"},
                    {"time": "2018-01-16T11:41:40.844000+0100", "delay": "0.020500"},
                ],
            },
        }
        for k in test_dict.keys():
            poped_data = test_dict.pop(k)
            test_json = json.dumps(test_dict)
            response = self.client.post(reverse("stream:create_test"), test_json, content_type="application/json")
            # Check that the response is 400 BAD_REQUEST
            self.assertEqual(response.status_code, 400)
            # Check that no instance of ConnectivityTest exists
            self.assertEqual(StreamTest.objects.count(), 0)
            test_dict[k] = poped_data


class GetStreamTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.benchmark = create_benchmark()
        config = StreamConfig.objects.create(
            url="superman.com",
            port=1234,
            upload_chunk_size=2000,
            download_chunk_size=2000,
            upload_interval_time="0.1",
            download_interval_time="0.1",
            duration="2.0",
        )
        test = StreamTest.objects.create(
            benchmark=self.benchmark,
            config=config,
            order=0,
            protocol_info=[
                {
                    "Time": "2018-02-12T15:47:32.519422Z",
                    "Connections": {},
                },
                {
                    "Time": "2018-02-12T15:47:35.686581Z",
                    "Connections": {},
                },
            ],
            start_time=datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc),
            wait_time="5.0",
            duration="1.234",
            wifi_bytes_received=45,
            wifi_bytes_sent=78,
            cell_bytes_received=33,
            cell_bytes_sent=25,
            multipath_service='aggregate',
            protocol='QUIC',
        )
        result = StreamResult.objects.create(
            test=test,
            error_msg="Exiting client main with error InternalError: deadline exceeded",
            success=True,
        )
        StreamDelay.objects.create(
            result=result,
            time=datetime(2018, 1, 16, 10, 41, 47, 744000, tzinfo=pytz.utc),
            delay="0.1234",
            upload=True,
        )
        StreamDelay.objects.create(
            result=result,
            time=datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc),
            delay="0.2345",
            upload=True,
        )
        StreamDelay.objects.create(
            result=result,
            time=datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc),
            delay="0.0123",
            upload=False,
        )
        StreamDelay.objects.create(
            result=result,
            time=datetime(2018, 1, 16, 10, 41, 47, 744000, tzinfo=pytz.utc),
            delay="0.3456",
            upload=False,
        )

    def test_get_stream_list(self):
        response = self.client.get(reverse("mptests:list_tests", kwargs={'benchmark_uuid': str(self.benchmark.uuid)}))
        json_response = json.loads(response.content.decode("UTF-8"))
        self.assertTrue('stream' in json_response)
        streams_json = json_response['stream']
        self.assertEqual(len(streams_json), 1)
        expected_json = {
            'wifi_bytes_sent': 78,
            'wait_time': '5.0',
            'order': 0,
            'duration': '1.234',
            'graphs': [
                {
                    'x_label': 'Time',
                    'y_label': 'Delay',
                    'data': [
                        {
                            'values': [
                                ['2018-01-16T10:41:40.744000Z', '0.2345'],
                                ['2018-01-16T10:41:47.744000Z', '0.1234'],
                            ],
                            'label': 'Upload delays (ms)',
                        },
                    ],
                },
                {
                    'x_label': 'Time',
                    'y_label': 'Delay',
                    'data': [
                        {
                            'values': [
                                ['2018-01-16T10:41:40.744000Z', '0.0123'],
                                ['2018-01-16T10:41:47.744000Z', '0.3456'],
                            ],
                            'label': 'Download delays (ms)',
                        },
                    ],
                },
            ],
            'protocol': 'QUIC',
            'result': {
                'error_msg': 'Exiting client main with error InternalError: deadline exceeded',
                'success': True,
            },
            'multipath_service': 'aggregate',
            'cell_bytes_received': 33,
            'start_time': '2018-01-16T10:41:40.744000Z',
            'cell_bytes_sent': 25,
            'wifi_bytes_received': 45,
            'config': {
                'download_chunk_size': 2000,
                'upload_interval_time': '0.1',
                'download_interval_time': '0.1',
                'url': 'superman.com',
                'port': 1234,
                'upload_chunk_size': 2000,
                'duration': '2.0',
            },
        }
        self.assertDictEqual(expected_json, streams_json[0])
