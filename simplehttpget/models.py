from django.db import models

from mptcpbench.mptests.models import Test, Config, Result


class SimpleHttpGetConfig(Config):
    url = models.CharField(max_length=200)


class SimpleHttpGetTest(Test):
    config = models.ForeignKey(SimpleHttpGetConfig, models.CASCADE,
                               related_name="tests")


class SimpleHttpGetResult(Result):
    test = models.OneToOneField(SimpleHttpGetTest, models.CASCADE,
                                related_name="result")


""" ############################# DEPRECATED ############################## """

from mptcpbench.benches.models import Bench
from mptcpbench.collect.models import Result as OldResult


class SimpleHttpGetBench(Bench):
    """ SimpleHttpGet benchmark """
    file_name = models.CharField(max_length=200)
    server_url = models.CharField(max_length=200)

    name = "simple_http_get"


class SimpleHttpGetOldResult(OldResult):
    """ Additional results specific to the SimpleHttpGet bench """
    def create_result_from_dict(result_dict):
        netcfgs = result_dict.pop("netcfgs", None)
        result = SimpleHttpGetOldResult.objects.create(**result_dict)

        if netcfgs:
            Result.create_netcfgs(netcfgs, result)

        return result
