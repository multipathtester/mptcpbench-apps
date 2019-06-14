from django.db import models

from mptcpbench.mptests.models import Test, Config, Result


class StreamConfig(Config):
    url = models.CharField(max_length=200)
    port = models.PositiveIntegerField()
    upload_chunk_size = models.PositiveIntegerField()
    download_chunk_size = models.PositiveIntegerField()
    upload_interval_time = models.DurationField()
    download_interval_time = models.DurationField()
    duration = models.DurationField()


class StreamTest(Test):
    config = models.ForeignKey(StreamConfig, models.CASCADE,
                               related_name="tests")


class StreamResult(Result):
    test = models.OneToOneField(StreamTest, models.CASCADE,
                                related_name="result")


class StreamDelay(models.Model):
    result = models.ForeignKey(StreamResult, models.CASCADE,
                               related_name="delays")
    time = models.DateTimeField()
    delay = models.DurationField()
    upload = models.BooleanField()  # True = upload, False = download
