from django.db.models import Max, Prefetch

from ipware import get_client_ip
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_multiple_model.views import ObjectMultipleModelAPIView

from .models import ClientIP, MobileBenchmark, Benchmark, Location
from .serializers import BenchmarkSerializer
from mptcpbench.connectivity.models import ConnectivityTest
from mptcpbench.connectivity.serializers import ConnectivityTestSerializer
from mptcpbench.iperf.models import IPerfTest
from mptcpbench.iperf.serializers import IPerfTestSerializer
from mptcpbench.netconnectivities.models import NetConnectivity
from mptcpbench.simplehttpget.models import SimpleHttpGetTest
from mptcpbench.simplehttpget.serializers import SimpleHttpGetTestSerializer
from mptcpbench.stream.models import StreamTest, StreamDelay
from mptcpbench.stream.serializers import StreamTestSerializer


class BenchmarkCreateView(CreateAPIView):
    serializer_class = BenchmarkSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            benchmark = serializer.save()
            client_ip, is_routable = get_client_ip(request)
            ClientIP.objects.create(
                benchmark=benchmark,
                ip=client_ip,
                routable=is_routable)
            return Response({'uuid': benchmark.uuid},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BenchmarkListView(ListAPIView):
    serializer_class = BenchmarkSerializer

    def get_queryset(self):
        device_uuid = self.kwargs['device_uuid']
        return Benchmark.objects.filter(
            device_uuid=device_uuid,
        ).prefetch_related(
            "mobile",
            Prefetch(
                'location_set',
                queryset=Location.objects.order_by('timestamp'),
                to_attr='locations',
            ),
            Prefetch(
                'netconnectivity_set',
                queryset=NetConnectivity.objects.order_by('timestamp'),
                to_attr='netconnectivities',
            ),
        )


class TestListView(ObjectMultipleModelAPIView):
    def get_querylist(self):
        benchmark_uuid = self.kwargs['benchmark_uuid']
        benchmark = Benchmark.objects.get(uuid=benchmark_uuid)

        querylist = (
            {
                'queryset': ConnectivityTest.objects.filter(
                    benchmark=benchmark,
                ).prefetch_related(
                    'config',
                    'result',
                    'result__delays'
                ),
                'serializer_class': ConnectivityTestSerializer,
                'label': 'connectivity',
            },
            {
                'queryset': SimpleHttpGetTest.objects.filter(
                    benchmark=benchmark,
                ).prefetch_related(
                    'config',
                    'result',
                ),
                'serializer_class': SimpleHttpGetTestSerializer,
                'label': 'simplehttpget',
            },
            {
                'queryset': IPerfTest.objects.filter(
                    benchmark=benchmark,
                ).prefetch_related(
                    'config',
                    'result',
                    'result__intervals',
                ),
                'serializer_class': IPerfTestSerializer,
                'label': 'iperf',
            },
            {
                'queryset': StreamTest.objects.filter(
                    benchmark=benchmark,
                ).prefetch_related(
                    'config',
                    'result',
                    Prefetch(
                        'result__delays',
                        queryset=StreamDelay.objects.order_by('time'),
                        to_attr='ordered_delays'
                    ),
                ),
                'serializer_class': StreamTestSerializer,
                'label': 'stream',
            },
        )

        return querylist


class MaxWifiDistanceView(APIView):
    def get(self, request, format=None):
        queryset = MobileBenchmark.objects.order_by(
            '-wifi_bytes_distance'
        ).values(
            'wifi_bytes_distance',
            'wifi_bssid_switches',
        ).first()
        return Response(queryset)
