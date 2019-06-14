import uuid as uuid_lib

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from mptcpbench.mptcpinfos.models import MPTCPTestInfo
from mptcpbench.quicinfos.models import QUICTestInfo


class Benchmark(models.Model):
    uuid = models.UUIDField(
        db_index=True,
        default=uuid_lib.uuid4,
        editable=False)
    start_time = models.DateTimeField()
    duration = models.DurationField()
    tz = models.CharField('Timezone', max_length=32)
    ping_med = models.FloatField()  # In milliseconds
    ping_std = models.FloatField()  # In milliseconds
    wifi_bytes_received = models.PositiveIntegerField()
    wifi_bytes_sent = models.PositiveIntegerField()
    cell_bytes_received = models.PositiveIntegerField()
    cell_bytes_sent = models.PositiveIntegerField()
    multipath_service = models.CharField(max_length=11)
    server_name = models.CharField(max_length=20)
    platform = models.CharField(max_length=20)
    platform_version_name = models.CharField(max_length=30)
    platform_version_code = models.CharField(max_length=50)
    device_uuid = models.UUIDField()
    device_model = models.CharField(max_length=50)
    device_model_code = models.CharField(max_length=20)
    software_name = models.CharField(max_length=20)
    software_version = models.CharField(max_length=40)
    user_interrupted = models.BooleanField(default=False)
    rcv_time = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        # Avoid duplicates
        unique_together = (("start_time", "device_uuid"))


class MobileBenchmark(models.Model):
    benchmark = models.OneToOneField(Benchmark, models.CASCADE,
                                     related_name='mobile')
    wifi_bytes_distance = models.FloatField()
    wifi_bytes_lost_time = models.DateTimeField()
    wifi_system_distance = models.FloatField()
    wifi_system_lost_time = models.DateTimeField()
    wifi_bssid_switches = models.IntegerField(default=0)
    wifi_multiple_ssid = models.BooleanField(default=False)


class UDPProbe(models.Model):
    mobile_benchmark = models.ForeignKey(MobileBenchmark, models.CASCADE)
    time = models.DateTimeField()
    delay = models.DurationField()
    is_wifi = models.BooleanField()  # Otherwise, cellular


class Location(models.Model):
    benchmark = models.ForeignKey(Benchmark, models.CASCADE)
    lat = models.FloatField('Latitude')
    lon = models.FloatField('Longitude')
    timestamp = models.DateTimeField()
    acc = models.FloatField('Accuracy')
    alt = models.FloatField('Altitude')
    speed = models.FloatField()


class ClientIP(models.Model):
    benchmark = models.OneToOneField(Benchmark, models.CASCADE)
    ip = models.GenericIPAddressField(protocol="both")
    routable = models.BooleanField()


class Config(models.Model):
    class Meta:
        abstract = True


class Test(models.Model):
    benchmark = models.ForeignKey(Benchmark)
    config = models.OneToOneField(Config, models.CASCADE)
    order = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    wait_time = models.DurationField()
    duration = models.DurationField()
    wifi_bytes_received = models.PositiveIntegerField()
    wifi_bytes_sent = models.PositiveIntegerField()
    cell_bytes_received = models.PositiveIntegerField()
    cell_bytes_sent = models.PositiveIntegerField()
    multipath_service = models.CharField(max_length=11)
    protocol = models.CharField(max_length=20)
    protocol_info = JSONField()
    rcv_time = models.DateTimeField(default=timezone.now, editable=False)
    mptcp_test_info = models.OneToOneField(MPTCPTestInfo, models.CASCADE,
                                           blank=True, null=True)
    quic_test_info = models.OneToOneField(QUICTestInfo, models.CASCADE,
                                          blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = (("benchmark", "order"))


class Result(models.Model):
    test = models.OneToOneField(Test, models.CASCADE)
    success = models.BooleanField()
    error_msg = models.CharField(max_length=800, blank=True, null=True)  # To be sure

    class Meta:
        abstract = True
