from django.test import Client, TestCase

import json


class LaunchingTestTest(TestCase):
    def setUp(self):
        self.client = Client()

    # def test_launching_test(self):
    #     json_dict = {
    #         "bench": {
    #             "config": {
    #                 "file_name": "random_10MB",
    #                 "http_version": "1",
    #                 "server_url": "multipath-tcp.org",
    #             },
    #             "name": "simple_http_get",
    #         },
    #         "client_tag": "123456789azertyuiopmlkjhgfdsqwxcvbn",
    #         "uuid": "123e4567-e89b-12d3-a456-426655440000",
    #     }
    #     json_to_send = json.dumps(json_dict)
        # print(json_to_send)
        # response = self.client.post("/test_server/launch_test/", json_to_send, content_type="application/json")
        # json_response = json.loads(response.content.decode("UTF-8"))
        # print(json_response)
