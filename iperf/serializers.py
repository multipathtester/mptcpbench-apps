from rest_framework import serializers

from .models import IPerfTest, IPerfConfig, IPerfResult, IPerfInterval
from mptcpbench.mptests.models import Benchmark
from mptcpbench.mptests.tasks import protocol_info_db


class IPerfConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPerfConfig
        fields = (
            "download",
            "duration",
            "port",
            "url",
        )


class IPerfIntervalSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPerfInterval
        fields = (
            "intervalInSec",
            "transferredLastSecond",
            "globalBandwidth",
            "retransmittedLastSecond",
        )


class IPerfResultSerializer(serializers.ModelSerializer):
    intervals = serializers.ListSerializer(child=IPerfIntervalSerializer())

    class Meta:
        model = IPerfResult
        fields = (
            "intervals",
            "error_msg",
            "success",
            "total_retrans",
            "total_sent",
        )


class IPerfTestSerializer(serializers.ModelSerializer):
    benchmark_uuid = serializers.UUIDField()
    config = IPerfConfigSerializer()
    result = IPerfResultSerializer()

    class Meta:
        model = IPerfTest
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
        config, _ = IPerfConfig.objects.get_or_create(**config_data)
        test = IPerfTest.objects.create(benchmark=benchmark, config=config,
                                        **validated_data)
        intervals_data = result_data.pop("intervals")
        result = IPerfResult.objects.create(test=test, **result_data)
        for i_data in intervals_data:
            IPerfInterval.objects.create(result=result, **i_data)
        protocol_info_db.delay("iperf", test.id)

        return test

    def to_representation(self, obj):
        infos = obj.protocol_info
        data_dict = {}
        cid = None
        for info in infos:
            cids_dict = info.get("Connections", {})
            if len(cids_dict) == 0:
                continue
            if not cid:
                cid = list(cids_dict)[0]
            cid_dict = cids_dict.get(cid, {})
            paths_dict = cid_dict.get("Paths", {})
            for path_id in list(paths_dict):
                path_dict = paths_dict[path_id]
                if path_id not in data_dict:
                    label = "Path " + path_id
                    if_name = str(path_dict.get("InterfaceName", ""))
                    if if_name:
                        if if_name.startswith("en") or \
                                if_name.startswith("wlan"):
                            label += " (WiFi)"
                        elif if_name.startswith("pdp_ip") or \
                                if_name.startswith("rmnet"):
                            label += " (Cellular)"
                        else:
                            label += " (" + if_name + ")"
                    label += " Congestion Window"
                    data_dict[path_id] = {
                        "label": label,
                        "values": [],
                    }

                cwin = int(path_dict["CongestionWindow"])
                timestamp = info["Time"]
                data_dict[path_id]["values"].append((timestamp, cwin))

        data_list = []
        for path_id in sorted(list(data_dict)):
            # In MPQUIC, don't log path 0
            if int(path_id) == 0 and len(data_dict) > 1:
                continue
            data_list.append(data_dict[path_id])

        return {
            "config": IPerfConfigSerializer(obj.config).data,
            "result": IPerfResultSerializer(obj.result).data,
            "graphs": [
                {
                    "x_label": "Time",
                    "y_label": "Bytes",
                    "data": data_list,
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
