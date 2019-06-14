from .mobility_graphs import get_stream_graphs, get_cell_packet_graphs


def get_mobile_stats(version_operator=None, version=None, only_mobility=False):
    return {
        "charts": get_stream_graphs(version_operator=version_operator,
                                    version=version,
                                    only_mobility=only_mobility) +
        get_cell_packet_graphs(version_operator=version_operator,
                               version=version, only_mobility=only_mobility),
    }
