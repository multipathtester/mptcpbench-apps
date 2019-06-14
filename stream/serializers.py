from rest_framework import serializers

from .models import StreamTest, StreamConfig, StreamResult, StreamDelay
from mptcpbench.mptests.models import Benchmark
from mptcpbench.mptests.tasks import protocol_info_db


class StreamConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamConfig
        fields = (
            "url",
            "port",
            "upload_chunk_size",
            "download_chunk_size",
            "upload_interval_time",
            "download_interval_time",
            "duration",
        )

    def to_representation(self, obj):
        """ XXX Strangely, redefining this format duration fields as float
            fields. Because it seems easier to process it as a float field,
            let's redefine it here.
        """
        return {
            "url": obj.url,
            "port": obj.port,
            "upload_chunk_size": obj.upload_chunk_size,
            "download_chunk_size": obj.download_chunk_size,
            "upload_interval_time": obj.upload_interval_time,
            "download_interval_time": obj.download_interval_time,
            "duration": obj.duration,
        }


class StreamDelaySerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamDelay
        fields = (
            "time",
            "delay",
        )


class StreamResultSerializer(serializers.ModelSerializer):
    upload_delays = serializers.ListSerializer(child=StreamDelaySerializer())
    download_delays = serializers.ListSerializer(child=StreamDelaySerializer())

    class Meta:
        model = StreamResult
        fields = (
            "upload_delays",
            "download_delays",
            "error_msg",
            "success",
        )

    def to_representation(self, obj):
        return {
            "error_msg": obj.error_msg,
            "success": obj.success,
        }


class StreamTestSerializer(serializers.ModelSerializer):
    benchmark_uuid = serializers.UUIDField()
    config = StreamConfigSerializer()
    result = StreamResultSerializer()

    class Meta:
        model = StreamTest
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
        config, _ = StreamConfig.objects.get_or_create(**config_data)
        test = StreamTest.objects.create(benchmark=benchmark, config=config,
                                         **validated_data)
        upload_delays_data = result_data.pop("upload_delays")
        download_delays_data = result_data.pop("download_delays")
        result = StreamResult.objects.create(test=test, **result_data)
        for udd in upload_delays_data:
            StreamDelay.objects.create(result=result, upload=True, **udd)
        for ddd in download_delays_data:
            StreamDelay.objects.create(result=result, upload=False, **ddd)
        protocol_info_db.delay("stream", test.id)
        return test

    def to_representation(self, obj):
        up_delays = []
        down_delays = []
        for d in obj.result.ordered_delays:
            if d.upload:
                up_delays.append((d.time, d.delay))
            else:
                down_delays.append((d.time, d.delay))
        return {
            "config": StreamConfigSerializer(obj.config).data,
            "result": StreamResultSerializer(obj.result).data,
            "graphs": [
                {
                    "x_label": "Time",
                    "y_label": "Delay",
                    "data": [
                        {
                            "label": "Upload delays (ms)",
                            "values": up_delays,
                        },
                    ],
                },
                {
                    "x_label": "Time",
                    "y_label": "Delay",
                    "data": [
                        {
                            "label": "Download delays (ms)",
                            "values": down_delays,
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
