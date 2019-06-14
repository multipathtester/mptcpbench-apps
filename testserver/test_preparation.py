from datetime import datetime, timedelta
import os
import psutil
import pytz
import subprocess
from shutil import chown, move

from django.conf import settings
from django.core.exceptions import SuspiciousOperation

from . import models, simple_http_get
from .tasks import kill_simple_http_get

# FIXME to be moved or computed
# TODO should be run on behalf of tcpdump, not quentin :-)
GROUP = "tcpdump"
USER = "quentin"
SERVER_TAG = "4694764687serverHHOJ9ZJMZ908P2KLNKQs"
SIMPLE_HTTP_GET_TIMEOUT = 20
TCPDUMP_SNAPLEN = 100


class BusyError(Exception):
    pass


def get_net_sysctl():
    cmd = ["sysctl", "net.ipv4", "net.mptcp"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    output = proc.stdout.read().decode("UTF-8")

    sysctl_dict = {}
    for line in output.splitlines():
        key, value = line.split(" = ")
        sysctl_dict[key] = value

    return sysctl_dict


def _get_formatted_datetime(timestamp):
    return (str(datetime.fromtimestamp(float(timestamp), tz=pytz.timezone("UTC"))).replace(":", "_")
                                                                                  .replace(".", "_")
                                                                                  .replace(" ", "_"))


def _get_capture_name(test_dict, media_root):
    check_directory_exists(os.path.join(media_root, SERVER_TAG))
    check_directory_exists(os.path.join(media_root, SERVER_TAG, test_dict["client_tag"]))
    # Should be compliant with the naming given by the collect server
    return os.path.join(SERVER_TAG, test_dict["client_tag"], test_dict["uuid"] + ".pcap")


def _write_tcpdump_pid_to_file(pid):
    pid_file = open("tcpdump.pid", "w")
    pid_file.write(str(pid))
    pid_file.close()


def check_no_test_running():
    pid_file = open("tcpdump.pid", "r")
    pid = int(pid_file.read())
    if psutil.pid_exists(pid):
        raise BusyError("An experience is already running")


def check_directory_exists(directory):
    """ Check if the directory exists, and create it if needed
        If directory is a file, exit the program
    """
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise Exception(directory + " is a file...")
    else:
        # Allow user processes to modify content of directory
        os.makedirs(directory, mode=0o777)
        chown(directory, user=USER, group=GROUP)


def _check_non_existing_trace(name, full_path):
    qs = models.PendingTrace.objects.filter(name=name, full_path=full_path)
    if qs.count() != 0:
        raise SuspiciousOperation("Test with trace already exists")


def start_capture_pcap_trace(test_dict):
    check_directory_exists(settings.MEDIA_ROOT)
    capture_name = _get_capture_name(test_dict, settings.MEDIA_ROOT)
    full_capture_path = os.path.join(settings.MEDIA_ROOT, capture_name)
    # Record expected name for collect server
    _check_non_existing_trace(capture_name, full_capture_path)
    pending_trace = models.PendingTrace.objects.create(name=capture_name, full_path=full_capture_path)
    # This may seem weird, but it is better to directly have a secure solution (avoid celery as root to kill it)
    cmd = ["runuser", "-l", USER, "-c", "/usr/sbin/tcpdump -i any -s " + str(TCPDUMP_SNAPLEN) + " -w " +
                                        full_capture_path + " 'tcp' & echo $! > /tmp/tcpdump.pid"]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return pending_trace


def launch_simple_http_get(test_dict):
    # TODO should check if config is ok (or needed)
    nginx_config_path = os.path.abspath("nginx.conf")
    http_version = test_dict["bench"]["config"].get("http_version", "1")
    port_number = simple_http_get.launch_nginx_server(nginx_config_path, http_version)
    pending_trace = start_capture_pcap_trace(test_dict)
    kill_time = datetime.now() + timedelta(seconds=SIMPLE_HTTP_GET_TIMEOUT)
    kill_simple_http_get.apply_async(args=[pending_trace], eta=kill_time)
    return {"port": port_number, "timeout": SIMPLE_HTTP_GET_TIMEOUT}


def launch_test(test_dict):
    bench_name = None
    if test_dict["bench"]["name"] == "simple_http_get":
        bench_name = test_dict["bench"]["name"]
        return launch_simple_http_get(test_dict)

    if bench_name is None:
        raise SuspiciousOperation("Bench " + str(test_dict["bench"]["name"]) + " is unknown")
