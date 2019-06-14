from django.db import models

from mptcpbench.mptests.models import Test, Config, Result


class ConnectivityConfig(Config):
    port = models.PositiveIntegerField()
    url = models.CharField(max_length=200)


class ConnectivityTest(Test):
    config = models.ForeignKey(ConnectivityConfig, models.CASCADE,
                               related_name="tests")


class ConnectivityResult(Result):
    test = models.OneToOneField(ConnectivityTest, models.CASCADE,
                                related_name="result")


class ConnectivityDelay(models.Model):
    result = models.ForeignKey(ConnectivityResult, models.CASCADE,
                               related_name="delays")
    delay = models.FloatField()  # In milliseconds


""" ############################# DEPRECATED ############################## """

from mptcpbench.benches.models import Bench
from mptcpbench.collect.models import Result as OldResult


class ConnectivityBench(Bench):
    """ QUIC Connectivity benchmark """
    port = models.PositiveIntegerField()
    url = models.CharField(max_length=200)

    name = "connectivity"


class ConnectivityOldResult(OldResult):
    """ Additional results specific to the Connectivity bench """
    success = models.BooleanField()

    def create_result_from_dict(result_dict):
        result = ConnectivityOldResult.objects.create(**result_dict)

        return result
