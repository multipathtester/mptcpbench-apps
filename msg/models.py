from django.db import models

from mptcpbench.mptests.models import Test, Config, Result


class MsgConfig(Config):
    port = models.PositiveIntegerField()
    url = models.CharField(max_length=200)
    query_size = models.PositiveIntegerField()
    response_size = models.PositiveIntegerField()
    start_delay_query_response = models.PositiveIntegerField()
    nb_msgs = models.PositiveIntegerField()
    interval_time_ms = models.PositiveIntegerField()
    timeout_sec = models.PositiveIntegerField()


class MsgTest(Test):
    config = models.ForeignKey(MsgConfig, models.CASCADE, related_name="tests")


class MsgResult(Result):
    test = models.OneToOneField(MsgTest, models.CASCADE, related_name="result")
    missed = models.PositiveIntegerField()


class MsgDelay(models.Model):
    result = models.ForeignKey(MsgResult, models.CASCADE)
    delay = models.PositiveIntegerField()


""" ############################# DEPRECATED ############################## """

from mptcpbench.benches.models import Bench
from mptcpbench.collect.models import Result as OldResult


class MsgBench(Bench):
    """ Instant Messaging-like traffic benchmark """
    server_port = models.PositiveIntegerField()
    query_size = models.PositiveIntegerField()
    response_size = models.PositiveIntegerField()
    start_delay_query_response = models.PositiveIntegerField()
    nb_msgs = models.PositiveIntegerField()
    interval_time_ms = models.PositiveIntegerField()
    timeout_sec = models.PositiveIntegerField()

    name = "msg"


class MsgOldResult(OldResult):
    """ Additional results specific to the Msg bench """
    missed = models.PositiveIntegerField()

    def create_result_from_dict(result_dict):
        delays = result_dict.pop("delays")
        netcfgs = result_dict.pop("netcfgs")
        result = MsgOldResult.objects.create(**result_dict)

        for delay in delays:
            MsgDelayResult.objects.create(result=result, delay=delay)

        if netcfgs:
            OldResult.create_netcfgs(netcfgs, result)

        return result


class MsgDelayResult(models.Model):
    result = models.ForeignKey(MsgOldResult)
    delay = models.PositiveIntegerField()
