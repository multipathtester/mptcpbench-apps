from config.celery import app

from mptcpbench.connectivity.models import ConnectivityTest
from mptcpbench.iperf.models import IPerfTest
from mptcpbench.simplehttpget.models import SimpleHttpGetTest
from mptcpbench.stream.models import StreamTest
from .serializers import protocol_info_create


@app.task
def protocol_info_db(test_name, test_id):
    if test_name == "connectivity":
        test = ConnectivityTest.objects.get(id=test_id)
    elif test_name == "iperf":
        test = IPerfTest.objects.get(id=test_id)
    elif test_name == "simplehttpget":
        test = SimpleHttpGetTest.objects.get(id=test_id)
    elif test_name == "stream":
        test = StreamTest.objects.get(id=test_id)
    else:
        print("Unknown test name", test_name)
        return

    protocol_info_create(test.protocol_info, test)
