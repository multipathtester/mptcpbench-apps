from rest_framework import serializers

from .models import NetConnectivity, IPAddress
from mptcpbench.mptests.models import Benchmark


class IPAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPAddress
        fields = (
            "ip",
        )


class NetConnectivitySerializer(serializers.ModelSerializer):
    benchmark_uuid = serializers.UUIDField()
    wifi_ips = serializers.ListSerializer(child=IPAddressSerializer(),
                                          required=False)
    cell_ips = serializers.ListSerializer(child=IPAddressSerializer(),
                                          required=False)

    class Meta:
        model = NetConnectivity
        fields = (
            "benchmark_uuid",
            "wifi_ips",
            "cell_ips",
            "network_type",
            "timestamp",
            "wifi_network_name",
            "wifi_bssid",
            "cell_network_name",
            "cell_code",
            "cell_code_description",
            "cell_iso_country_code",
            "cell_operator_code",
        )

    def validate(self, data):
        data = super().validate(data)
        nt = data['network_type']
        if nt not in [NetConnectivity.WIFI, NetConnectivity.CELL,
                      NetConnectivity.WIFICELL, NetConnectivity.CELLWIFI]:
            raise serializers.ValidationError('Unknown network_type.')
        if nt == NetConnectivity.WIFI or nt == NetConnectivity.WIFICELL or \
                nt == NetConnectivity.CELLWIFI:
            for f in [f for f in self.Meta.fields if f.startswith('wifi_')]:
                if f not in data:
                    raise serializers.ValidationError(
                        f + ' required with WiFi connectivity.')
        if nt == NetConnectivity.CELL or nt == NetConnectivity.WIFICELL or \
                nt == NetConnectivity.CELLWIFI:
            for f in [f for f in self.Meta.fields if f.startswith('cell_')]:
                if f not in data:
                    raise serializers.ValidationError(
                        f + ' required with cellular connectivity.')
        return data

    def create(self, validated_data):
        benchmark_uuid_data = validated_data.pop('benchmark_uuid')
        benchmark = Benchmark.objects.get(uuid=benchmark_uuid_data)
        wifi_ips_data = []
        if 'wifi_ips' in validated_data:
            wifi_ips_data = validated_data.pop('wifi_ips')
        cellular_ips_data = []
        if 'cell_ips' in validated_data:
            cellular_ips_data = validated_data.pop('cell_ips')
        nc = NetConnectivity.objects.create(benchmark=benchmark,
                                            **validated_data)
        for wid in wifi_ips_data:
            IPAddress.objects.create(net_connectivity=nc,
                                     interface=NetConnectivity.WIFI, **wid)
        for cid in cellular_ips_data:
            IPAddress.objects.create(net_connectivity=nc,
                                     interface=NetConnectivity.CELL, **cid)

    def to_representation(self, obj):
        return_dict = {
            "network_type": obj.network_type,
            "timestamp": obj.timestamp,
        }
        if obj.network_type in [NetConnectivity.WIFI, NetConnectivity.WIFICELL,
                                NetConnectivity.CELLWIFI]:
            return_dict.update({
                "wifi_network_name": obj.wifi_network_name,
                "wifi_bssid": obj.wifi_bssid,
            })
        if obj.network_type in [NetConnectivity.CELL, NetConnectivity.WIFICELL,
                                NetConnectivity.CELLWIFI]:
            return_dict.update({
                "cell_network_name": obj.cell_network_name,
                "cell_code": obj.cell_code,
                "cell_code_description": obj.cell_code_description,
                "cell_iso_country_code": obj.cell_iso_country_code,
                "cell_operator_code": obj.cell_operator_code,
            })

        return return_dict


class NetConnectivityListSerializer(serializers.ListSerializer):
    child = NetConnectivitySerializer()
