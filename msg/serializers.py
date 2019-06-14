from rest_framework import serializers

from .models import MsgTest, MsgConfig, MsgResult, MsgDelay
from mptcpbench.mptests.models import Benchmark


class MsgConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MsgConfig
        fields = (
            "port",
            "url",
            "query_size",
            "response_size",
            "start_delay_query_response",
            "nb_msgs",
            "interval_time_ms",
            "timeout_sec",
        )


class MsgResultSerializer(serializers.ModelSerializer):
    delays = serializers.ListSerializer(child=serializers.IntegerField())

    class Meta:
        model = MsgResult
        fields = (
            "delays",
            "error_msg",
            "missed",
            "success",
        )


class MsgTestSerializer(serializers.ModelSerializer):
    benchmark_uuid = serializers.UUIDField()
    config = MsgConfigSerializer()
    result = MsgResultSerializer()

    class Meta:
        model = MsgTest
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
        config, _ = MsgConfig.objects.get_or_create(**config_data)
        test = MsgTest.objects.create(benchmark=benchmark, config=config,
                                      **validated_data)
        delays = result_data.pop("delays")
        result = MsgResult.objects.create(test=test, **result_data)
        for delay in delays:
            MsgDelay.objects.create(result=result, delay=delay)

        return test
