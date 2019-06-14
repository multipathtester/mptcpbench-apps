from rest_framework import serializers

from .models import Benchmark, Location, MobileBenchmark, UDPProbe
from mptcpbench.netconnectivities.serializers import NetConnectivitySerializer
from mptcpbench.mptcpinfos.serializers import mptcp_infos_create
from mptcpbench.quicinfos.serializers import quic_infos_create


# This is not really a serializer...
def protocol_info_create(protocol_info, test):
    if test.protocol == "MPTCP" and test.mptcp_test_info is None:
        mptcp_infos_create(protocol_info, test)
    elif (test.protocol == "QUIC" or test.protocol == "MPQUIC") and \
            test.quic_test_info is None:
        quic_infos_create(protocol_info, test)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = (
            'lon',
            'lat',
            'timestamp',
            'acc',
            'alt',
            'speed',
        )


class UDPProbeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UDPProbe
        fields = (
            'time',
            'delay',
        )


class MobileBenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileBenchmark
        fields = (
            'wifi_bytes_distance',
            'wifi_bytes_lost_time',
            'wifi_system_distance',
            'wifi_system_lost_time',
            'wifi_bssid_switches',
            'wifi_multiple_ssid',
        )


class BenchmarkSerializer(serializers.ModelSerializer):
    locations = serializers.ListSerializer(child=LocationSerializer())
    wifi_probes = serializers.ListSerializer(child=UDPProbeSerializer(), required=False)
    cell_probes = serializers.ListSerializer(child=UDPProbeSerializer(), required=False)
    mobile = MobileBenchmarkSerializer(required=False)

    class Meta:
        model = Benchmark
        fields = (
            'locations',
            'mobile',
            'wifi_probes',
            'cell_probes',
            'start_time',
            'duration',
            'tz',
            'ping_med',
            'ping_std',
            'wifi_bytes_received',
            'wifi_bytes_sent',
            'cell_bytes_received',
            'cell_bytes_sent',
            'multipath_service',
            'server_name',
            'platform',
            'platform_version_name',
            'platform_version_code',
            'device_uuid',
            'device_model',
            'device_model_code',
            'software_name',
            'software_version',
            'user_interrupted',
        )

    def create(self, validated_data):
        locations_data = validated_data.pop('locations')
        mobile_data = validated_data.pop('mobile', None)
        wifi_probes = validated_data.pop('wifi_probes', [])
        cell_probes = validated_data.pop('cell_probes', [])
        benchmark = Benchmark.objects.create(**validated_data)
        for loc in locations_data:
            Location.objects.create(benchmark=benchmark, **loc)

        if mobile_data is not None:
            mb = MobileBenchmark.objects.create(benchmark=benchmark,
                                                **mobile_data)
            for wp in wifi_probes:
                UDPProbe.objects.create(mobile_benchmark=mb, is_wifi=True,
                                        **wp)
            for cp in cell_probes:
                UDPProbe.objects.create(mobile_benchmark=mb, is_wifi=False,
                                        **cp)

        return benchmark

    def to_representation(self, obj):
        return_dict = {
            'start_time': obj.start_time,
            'duration': obj.duration,
            'tz': obj.tz,
            'ping_med': obj.ping_med,
            'ping_std': obj.ping_std,
            'wifi_bytes_received': obj.wifi_bytes_received,
            'wifi_bytes_sent': obj.wifi_bytes_sent,
            'cell_bytes_received': obj.cell_bytes_received,
            'cell_bytes_sent': obj.cell_bytes_sent,
            'multipath_service': obj.multipath_service,
            'server_name': obj.server_name,
            'platform': obj.platform,
            'platform_version_name': obj.platform_version_name,
            'platform_version_code': obj.platform_version_code,
            'device_model': obj.device_model,
            'device_model_code': obj.device_model_code,
            'software_name': obj.software_name,
            'software_version': obj.software_version,
            'user_interrupted': obj.user_interrupted,
            'uuid': obj.uuid,
        }
        try:
            return_dict['mobile'] = MobileBenchmarkSerializer(obj.mobile).data
        except MobileBenchmark.DoesNotExist:
            # Not a mobile test
            pass

        try:
            return_dict['location'] = LocationSerializer(obj.locations[0]).data
        except IndexError:
            # No locations
            pass

        try:
            return_dict['netconnectivity'] = NetConnectivitySerializer(
                obj.netconnectivities[0]
            ).data
        except IndexError:
            # No NetConnectivity
            pass

        return return_dict
