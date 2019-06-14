from django.db import models

from mptcpbench.benches.models import Bench
from mptcpbench.collect.models import Result


class YoutubeStreamingBench(Bench):
    """ Youtube Streaming traffic benchmark """
    # Unofficially assumed to have 11 characters, but we never know
    video_id = models.CharField(max_length=30)
    video_type = models.CharField(max_length=8)  # Currently up to "webmdash"
    duration = models.PositiveIntegerField()  # In seconds
    video_itag = models.PositiveSmallIntegerField()
    video_framerate = models.PositiveSmallIntegerField()
    video_codec = models.CharField(max_length=50)
    video_size = models.CharField(max_length=11)
    video_quality = models.CharField(max_length=6)
    video_vquality = models.CharField(max_length=6)
    video_url = models.CharField(max_length=100)
    video_bytes_rate = models.PositiveIntegerField()
    audio_itag = models.PositiveSmallIntegerField()
    audio_bitrate = models.PositiveIntegerField()
    audio_codec = models.CharField(max_length=50)
    audio_url = models.CharField(max_length=100)
    audio_bytes_rate = models.PositiveIntegerField()
    playout_buffer_sec = models.PositiveSmallIntegerField()
    maxtime = models.PositiveSmallIntegerField()

    name = "youtube_streaming"


class YoutubeStreamingResult(Result):
    """ Additional results specific to the YoutubeStreaming bench """
    result = models.CharField(max_length=4)  # OK or FAIL
    download_time = models.DurationField()
    nb_stalls = models.PositiveSmallIntegerField()
    avg_stall_duration = models.DurationField()
    total_stall_time = models.DurationField()
    initial_prebuf_time = models.DurationField()
    video_download_rate = models.PositiveIntegerField()
    video_total_bytes = models.PositiveIntegerField()
    video_download_time = models.DurationField()
    video_cdn_ip = models.GenericIPAddressField()
    video_conn_time = models.DurationField()
    video_bitrate_iqr = models.PositiveIntegerField()
    audio_download_rate = models.PositiveIntegerField()
    audio_total_bytes = models.PositiveIntegerField()
    audio_download_time = models.DurationField()
    audio_cdn_ip = models.GenericIPAddressField()
    audio_conn_time = models.DurationField()
    first_conn_time = models.DurationField()
    startup_time = models.DurationField()
    max_bytes_rate = models.PositiveIntegerField()
    error_code = models.PositiveSmallIntegerField()
    error_msg = models.CharField(max_length=28)  # DNS_RESOLUTION_CONTENT_ERROR

    def create_result_from_dict(result_dict):
        netcfgs = result_dict.pop("netcfgs")
        result = YoutubeStreamingResult.objects.create(**result_dict)

        if netcfgs:
            Result.create_netcfgs(netcfgs, result)

        return result
