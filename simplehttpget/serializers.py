from rest_framework import serializers

from .models import SimpleHttpGetTest, SimpleHttpGetConfig, SimpleHttpGetResult
from mptcpbench.mptests.models import Benchmark
from mptcpbench.mptests.tasks import protocol_info_db


class SimpleHttpGetConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleHttpGetConfig
        fields = (
            "url",
        )


class SimpleHttpGetResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleHttpGetResult
        fields = (
            "error_msg",
            "success",
        )


class SimpleHttpGetTestSerializer(serializers.ModelSerializer):
    benchmark_uuid = serializers.UUIDField()
    config = SimpleHttpGetConfigSerializer()
    result = SimpleHttpGetResultSerializer()

    class Meta:
        model = SimpleHttpGetTest
        fields = (
            "benchmark_uuid",
            "protocol_info",
            "config",
            "result",
            "order",
            "start_time",
            "wait_time",
            "duration",
            "wifi_bytes_received",
            "wifi_bytes_sent",
            "cell_bytes_received",
            "cell_bytes_sent",
            "multipath_service",
            "protocol",
        )

    def create(self, validated_data):
        benchmark_uuid = validated_data.pop('benchmark_uuid')
        config_data = validated_data.pop("config")
        result_data = validated_data.pop("result")
        benchmark = Benchmark.objects.get(uuid=benchmark_uuid)
        config, _ = SimpleHttpGetConfig.objects.get_or_create(**config_data)
        test = SimpleHttpGetTest.objects.create(benchmark=benchmark,
                                                config=config,
                                                **validated_data)
        SimpleHttpGetResult.objects.create(test=test, **result_data)
        protocol_info_db.delay("simplehttpget", test.id)
        return test

    def to_representation(self, obj):
        infos = obj.protocol_info
        rcv_bytes_data = []
        cid = None
        for info in infos:
            cids_dict = info.get("Connections", {})
            if len(cids_dict) == 0:
                continue
            if not cid:
                cid = list(cids_dict)[0]
            cid_dict = cids_dict.get(cid, {})
            streams_dict = cid_dict.get("Streams", {})
            stream_dict = streams_dict.get("3", {})
            if len(stream_dict) == 0:
                continue
            rcv_bytes = int(stream_dict["BytesRead"])
            timestamp = info["Time"]
            rcv_bytes_data.append((timestamp, rcv_bytes))

        return {
            "config": SimpleHttpGetConfigSerializer(obj.config).data,
            "result": SimpleHttpGetResultSerializer(obj.result).data,
            "graphs": [
                {
                    "x_label": "Time",
                    "y_label": "Bytes",
                    "data": [
                        {
                            "label": "Bytes received",
                            "values": rcv_bytes_data,
                        },
                    ],
                },
            ],
            "order": obj.order,
            "start_time": obj.start_time,
            "wait_time": obj.wait_time,
            "duration": obj.duration,
            "wifi_bytes_received": obj.wifi_bytes_received,
            "wifi_bytes_sent": obj.wifi_bytes_sent,
            "cell_bytes_received": obj.cell_bytes_received,
            "cell_bytes_sent": obj.cell_bytes_sent,
            "multipath_service": obj.multipath_service,
            "protocol": obj.protocol,
        }
