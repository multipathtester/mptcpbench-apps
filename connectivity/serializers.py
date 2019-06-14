from rest_framework import serializers

from .models import ConnectivityTest, ConnectivityConfig, ConnectivityResult, \
    ConnectivityDelay
from mptcpbench.mptests.models import Benchmark
from mptcpbench.mptests.tasks import protocol_info_db


class ConnectivityConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectivityConfig
        fields = (
            "url",
            "port",
        )


class ConnectivityResultSerializer(serializers.ModelSerializer):
    delays = serializers.ListSerializer(child=serializers.FloatField())

    class Meta:
        model = ConnectivityResult
        fields = (
            "delays",
            "error_msg",
            "success",
        )

    def to_representation(self, obj):
        delays_raw = [d.delay for d in obj.delays.all()]
        return {
            "delays": delays_raw,
            'error_msg': obj.error_msg,
            "success": obj.success,
        }


class ConnectivityTestSerializer(serializers.ModelSerializer):
    benchmark_uuid = serializers.UUIDField()
    config = ConnectivityConfigSerializer()
    result = ConnectivityResultSerializer()

    class Meta:
        model = ConnectivityTest
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
        config, _ = ConnectivityConfig.objects.get_or_create(**config_data)
        test = ConnectivityTest.objects.create(benchmark=benchmark,
                                               config=config, **validated_data)
        delays_data = result_data.pop("delays")
        result = ConnectivityResult.objects.create(test=test, **result_data)
        for d in delays_data:
            ConnectivityDelay.objects.create(result=result, delay=d)
        protocol_info_db.delay("connectivity", test.id)
        return test

    def to_representation(self, obj):
        return {
            "config": ConnectivityConfigSerializer(obj.config).data,
            "result": ConnectivityResultSerializer(obj.result).data,
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
