from django.db import models

from mptcpbench.mptests.models import Test, Config, Result


class IPerfConfig(Config):
    download = models.BooleanField()
    duration = models.PositiveIntegerField()  # In seconds
    port = models.PositiveIntegerField()
    url = models.CharField(max_length=200)


class IPerfTest(Test):
    config = models.ForeignKey(IPerfConfig, models.CASCADE,
                               related_name="tests")


class IPerfResult(Result):
    test = models.OneToOneField(IPerfTest, models.CASCADE,
                                related_name="result")
    total_retrans = models.PositiveIntegerField()
    total_sent = models.PositiveIntegerField()


class IPerfInterval(models.Model):
    result = models.ForeignKey(IPerfResult, models.CASCADE,
                               related_name="intervals")
    intervalInSec = models.CharField(max_length=10)
    transferredLastSecond = models.PositiveIntegerField()
    globalBandwidth = models.PositiveIntegerField()
    retransmittedLastSecond = models.PositiveIntegerField()


""" ############################# DEPRECATED ############################## """

from mptcpbench.benches.models import Bench
from mptcpbench.collect.models import Result as OldResult


class IPerfBench(Bench):
    """ IPerf benchmark """
    duration = models.PositiveIntegerField()  # In seconds
    url = models.CharField(max_length=200)

    name = "iperf"


class IPerfOldResult(OldResult):
    """ Additional results specific to the IPerf bench """
    total_retrans = models.PositiveIntegerField()
    total_sent = models.PositiveIntegerField()

    def create_result_from_dict(result_dict):
        intervals = result_dict.pop("intervals")
        result = IPerfOldResult.objects.create(**result_dict)

        for interval_dict in intervals:
            IPerfIntervalResult.objects.create(result=result, **interval_dict)

        return result


class IPerfIntervalResult(models.Model):
    result = models.ForeignKey(IPerfOldResult)
    intervalInSec = models.CharField(max_length=10)
    transferredLastSecond = models.PositiveIntegerField()
    globalBandwidth = models.PositiveIntegerField()
    retransmittedLastSecond = models.PositiveIntegerField()
