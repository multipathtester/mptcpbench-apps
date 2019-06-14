from mptcpbench.benches.models import UndefinedBench
from mptcpbench.connectivity.models import ConnectivityBench, \
    ConnectivityOldResult
from mptcpbench.iperf.models import IPerfBench, IPerfOldResult
from mptcpbench.msg.models import MsgBench, MsgOldResult
from mptcpbench.simplehttpget.models import SimpleHttpGetBench, \
    SimpleHttpGetOldResult
from mptcpbench.siri.models import SiriBench, SiriResult
from mptcpbench.youtubestreaming.models import YoutubeStreamingBench, \
    YoutubeStreamingResult


matcher = {
    UndefinedBench.name: (UndefinedBench, None),
    SimpleHttpGetBench.name: (SimpleHttpGetBench, SimpleHttpGetOldResult),
    SiriBench.name: (SiriBench, SiriResult),
    MsgBench.name: (MsgBench, MsgOldResult),
    YoutubeStreamingBench.name: (YoutubeStreamingBench,
                                 YoutubeStreamingResult),
    ConnectivityBench.name: (ConnectivityBench, ConnectivityOldResult),
    IPerfBench.name: (IPerfBench, IPerfOldResult),
}


def get_bench_and_result_from_dict(bench_dict):
    if "name" not in bench_dict:
        raise Exception("Bench dict has no name")

    bench_name = bench_dict["name"]
    return matcher[bench_name]
