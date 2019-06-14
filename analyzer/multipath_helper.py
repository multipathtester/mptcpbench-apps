from .multipath_graphs import get_simplehttpget_duration_cdf, \
    get_iperf_bandwidth_cdf, get_stream_max_delay_cdf, get_simplehttpget_v4v6_duration_cdf, get_connectivity_barchart


def get_multipath_stats():
    return {
        'charts': get_simplehttpget_duration_cdf() +
        get_connectivity_barchart() +
        get_simplehttpget_duration_cdf(server_name="fr") +
        get_simplehttpget_duration_cdf(server_name="ca") +
        get_simplehttpget_duration_cdf(server_name="jp") +
        get_simplehttpget_v4v6_duration_cdf() +
        get_simplehttpget_v4v6_duration_cdf(server_name="fr") +
        get_simplehttpget_v4v6_duration_cdf(server_name="ca", marker=False) +
        get_simplehttpget_v4v6_duration_cdf(server_name="jp") +
        get_iperf_bandwidth_cdf() + get_iperf_bandwidth_cdf(server_name="fr") +
        get_iperf_bandwidth_cdf(server_name="ca") +
        get_iperf_bandwidth_cdf(server_name="jp") +
        get_stream_max_delay_cdf() +
        get_stream_max_delay_cdf(server_name="fr") +
        get_stream_max_delay_cdf(server_name="ca") +
        get_stream_max_delay_cdf(server_name="jp"),
    }
