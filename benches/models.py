from django.db import models


class Bench(models.Model):
    """ A benchmark, or an experience """
    name = "Override this value"


class UndefinedBench(Bench):
    """ Undefined benchmark, used when wanting to analyze traces without the
        benchmark stuff
    """
    name = "undefined"
