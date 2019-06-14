from django.db import models

from mptcpbench.benches.models import Bench
from mptcpbench.collect.models import Result


class SiriBench(Bench):
    """ Siri-like traffic benchmark """
    server_port = models.PositiveIntegerField()
    query_size = models.PositiveIntegerField()
    response_size = models.PositiveIntegerField()
    delay_query_response = models.PositiveIntegerField()
    min_payload_size = models.PositiveIntegerField()
    max_payload_size = models.PositiveIntegerField()
    interval_time_ms = models.PositiveIntegerField()
    nb_packets_bursts = models.PositiveIntegerField()
    time_between_bursts_ms = models.PositiveIntegerField()
    time_test_ms = models.PositiveIntegerField()

    name = "siri"


class SiriResult(Result):
    """ Additional results specific to the Siri bench """
    missed = models.PositiveIntegerField()

    def create_result_from_dict(result_dict):
        delays = result_dict.pop("delays")
        netcfgs = result_dict.pop("netcfgs")
        result = SiriResult.objects.create(**result_dict)

        for delay in delays:
            SiriDelayResult.objects.create(result=result, delay=delay)

        if netcfgs:
            Result.create_netcfgs(netcfgs, result)

        return result


class SiriDelayResult(models.Model):
    result = models.ForeignKey(SiriResult)
    delay = models.PositiveIntegerField()
