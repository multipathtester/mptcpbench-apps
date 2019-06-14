from datetime import datetime
from pytz import timezone

from .models import MPTCPTestInfo, MPTCPSubflowInfo, MPTCPConnectionInfo


# This is not really a serializer, but it will do the job
def mptcp_infos_create(protocol_info_dict, test):
    # This is because Test is abstract...
    mptcp_test_info = MPTCPTestInfo.objects.create()
    test.mptcp_test_info = mptcp_test_info
    test.save()
    tz = timezone(test.benchmark.tz)

    for time_dict in protocol_info_dict:
        # We have a dict with time + a key for each connection
        time = datetime.fromtimestamp(time_dict.pop("time"), tz=tz)
        for conn_id in time_dict.keys():
            conn_dict = time_dict[conn_id]
            # Remove the time in the conn_dict, as it is not used...
            conn_dict.pop("time", None)
            # Keep subflows info here
            subflows_dict = conn_dict.pop("subflows")
            mptcp_conn_info = MPTCPConnectionInfo.objects.create(
                test_info=mptcp_test_info,
                time=time,
                conn_id=conn_id,
                **conn_dict
            )
            # And now save subflow info
            for subflow_id in subflows_dict.keys():
                subflow_dict = subflows_dict[subflow_id]
                if "tcp_last_outif" in subflow_dict:
                    # Fix typo in client app
                    subflow_dict["tcpi_last_outif"] = subflow_dict.pop("tcp_last_outif")

                MPTCPSubflowInfo.objects.create(conn=mptcp_conn_info,
                                                subflow_id=subflow_id,
                                                **subflow_dict)
