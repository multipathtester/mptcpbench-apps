from datetime import datetime
import pytz

from django.db import models


class NoTestManager(models.Manager):
    def valid(self, **kwargs):
        # First exclude bad tests
        bad_start_time = datetime(2017, 2, 10, 0, 0, 0, 0, pytz.UTC)
        bad_end_time = datetime(2017, 2, 20, 16, 10, 0, 0, pytz.UTC)
        res = self.exclude(time__gt=bad_start_time, time__lt=bad_end_time)
        # Remove the bad smartphone
        res = res.exclude(time__gt=bad_end_time,
                          uploader_email__contains="@775bfe285db2f8a2.")
        # Remove the micro-benchmarks
        start_microbench = datetime(2017, 3, 2, 12, 0, 0, 0, pytz.UTC)
        res = res.exclude(time__gt=start_microbench,
                          uploader_email__contains="@2b9fc181746ece7.")
        res = res.exclude(time__gt=start_microbench,
                          uploader_email__contains="@ff490fb530640063.")

        return res.filter(**kwargs)


class SmartphoneTestManager(models.Manager):
    def valid(self, **kwargs):
        # First exclude bad tests
        bad_start_time = datetime(2017, 2, 10, 0, 0, 0, 0, pytz.UTC)
        bad_end_time = datetime(2017, 2, 20, 16, 10, 0, 0, pytz.UTC)
        res = self.exclude(start_time__gt=bad_start_time,
                           start_time__lt=bad_end_time)
        # Remove a bad smartphone
        res = res.exclude(start_time__gt=bad_end_time,
                          device_id="775bfe285db2f8a2")
        # Micro-benchs
        micro_start_time = datetime(2017, 3, 2, 12, 0, 0, 0, pytz.UTC)
        micro_end_time = datetime(2017, 3, 8, 8, 0, 0, 0, pytz.UTC)
        res = res.exclude(
            start_time__gt=micro_start_time,
            start_time__lt=micro_end_time,
            device_id__in=["2b9fc181746ece7", "ff490fb530640063"]
        )
        micro_wifi_start_time = datetime(2017, 3, 11, 17, 0, 0, 0, pytz.UTC)
        micro_wifi_end_time = datetime(2017, 3, 15, 14, 0, 0, 0, pytz.UTC)
        res = res.exclude(
            start_time__gt=micro_wifi_start_time,
            start_time__lt=micro_wifi_end_time,
            device_id__in=["2b9fc181746ece7", "ff490fb530640063"]
        )
        # Those are mainly because the implementation (test or kernel) was
        # buggy at some time...
        res = res.exclude(
            id__in=[2918, 5294, 5281, 5248, 5465, 3604, 3140, 5672]
        )

        return res.filter(**kwargs)


class NetcfgLineManager(models.Manager):
    def cell_ips(self, **kwargs):
        # First select all NetcfgLines of interest (with interface rmnet0)
        res = self.filter(interface="rmnet0", **kwargs)
        # Don't consider ANY addr
        res = res.exclude(ip_address="0.0.0.0/0")
        # Only consider ip_address field
        res = res.values('ip_address')
        # Prevent having twice the same IP in the list
        cell_ips_set = set([c['ip_address'].split('/')[0] for c in res])
        return list(cell_ips_set)
