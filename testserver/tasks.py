from __future__ import absolute_import


import http
import json
import os
import signal

from config.celery import app
from . import settings, simple_http_get

def upload_trace(pending_trace):
    print("Uploading trace " + pending_trace.name)
    os.remove(pending_trace.full_path)
    pending_trace.delete()
    print("Trace " + pending_trace.name + " deleted")


def kill_tcpdump(pending_trace):
    """ Return True if tcpdump is killed """
    tcpdump_pid_file = open("/tmp/tcpdump.pid")
    tcpdump_pid = int(tcpdump_pid_file.read())
    tcpdump_pid_file.close()
    try:
        os.kill(tcpdump_pid, signal.SIGTERM)
        print("Killed PID " + str(tcpdump_pid))
        return True
    except ProcessLookupError:
        # Process already killed, nothing to do
        return False


@app.task
def kill_simple_http_get(pending_trace):
    nginx_config_path = os.path.abspath("nginx.conf")
    if kill_tcpdump(pending_trace):
        try:
            test_server_connection = http.client.HTTPConnection(settings.TEST_SERVER_URL)
            json_to_send = json.dumps({"name": pending_trace.name})
            test_server_connection.request("POST", "/test_server/stop_nginx_server/", body=json_to_send,
                                           headers={"Content-type": "application/json"})
            test_server_connection.close()
        except Exception as e:
            print(e)
            print("Cannot stop nginx")
        simple_http_get.stop_nginx_server(nginx_config_path)
        upload_trace(pending_trace)
