from datetime import datetime
import re

from .models import QUICTestInfo, QUICPathInfo, QUICConnectionInfo, \
    QUICFlowControlInfo

# The following code is used to convert CamelCase into snake_case
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def convert(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def snake_case_dict(dict_in):
    dict_out = {}
    for k in dict_in.keys():
        dict_out[convert(k)] = dict_in[k]
    return dict_out


# This is not really a serializer, but it will do the job
def quic_infos_create(protocol_info_dict, test):
    # This is because Test is abstract...
    quic_test_info = QUICTestInfo.objects.create()
    test.quic_test_info = quic_test_info
    test.save()

    for time_dict in protocol_info_dict:
        # We have a dict with time + a key for each connection
        time = time_dict.pop("Time")
        conns_dict = time_dict["Connections"]
        for conn_id in conns_dict.keys():
            conn_dict = conns_dict[conn_id]
            # OpenStreams is actually provided by Streams, so drop it
            conn_dict.pop("OpenStreams", None)
            paths_dict = conn_dict.pop("Paths")
            streams_dict = conn_dict.pop("Streams")
            conn_flow_control_dict = conn_dict.pop("ConnFlowControl")
            conn = QUICConnectionInfo.objects.create(
                test_info=quic_test_info,
                time=time,
                conn_id=conn_id,
                **(snake_case_dict(conn_dict))
            )
            QUICFlowControlInfo.objects.create(
                conn=conn,
                is_conn_flow_control=True,
                stream_id=-1,
                **(snake_case_dict(conn_flow_control_dict))
            )
            for stream_id in streams_dict.keys():
                stream_dict = streams_dict[stream_id]
                QUICFlowControlInfo.objects.create(
                    conn=conn,
                    is_conn_flow_control=False,
                    stream_id=stream_id,
                    **(snake_case_dict(stream_dict))
                )

            for path_id in paths_dict.keys():
                path_dict = paths_dict[path_id]
                # LocalAddr and RemoteAddr needs special processing
                loc_addr_dict = path_dict.pop("LocalAddr")
                rem_addr_dict = path_dict.pop("RemoteAddr")
                loc_ip, loc_port = loc_addr_dict["IP"], loc_addr_dict["Port"]
                rem_ip, rem_port = rem_addr_dict["IP"], rem_addr_dict["Port"]
                QUICPathInfo.objects.create(
                    conn=conn,
                    path_id=path_id,
                    local_ip=loc_ip,
                    local_port=loc_port,
                    remote_ip=rem_ip,
                    remote_port=rem_port,
                    **(snake_case_dict(path_dict))
                )
