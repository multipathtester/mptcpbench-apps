import numpy as np

from django.http import Http404

from bokeh.charts import BoxPlot, Donut
from bokeh.embed import components
from bokeh.plotting import figure

from . import query

""" Aggregation graphs """


def get_bokeh_duration(**kwargs):
    """ Fetching data """
    durations = query.get_graph_duration(**kwargs)
    if durations:
        durations.append(durations[-1])
    y_dur = np.linspace(0.0, 1.0, len(durations))
    """ Plotting """
    plot = figure(title="Duration of MPTCP Connections", x_axis_label="Time [s]", x_range=[durations[0], durations[-1]], x_axis_type="log",
                  y_axis_label="CDF")
    plot.line(durations, y_dur, line_width=2)

    return components(plot)


def get_bokeh_bytes(c2s, **kwargs):
    """ Fetching data """
    bytes = query.get_graph_flow_bytes(c2s, **kwargs)
    if bytes:
        bytes.append(bytes[-1])
    y_bytes = np.linspace(0.0, 1.0, len(bytes))
    """ Plotting """
    plot = figure(title="Bytes of MPTCP Connections", x_axis_label="Bytes", x_range=[bytes[0], bytes[-1]], x_axis_type="log",
                  y_axis_label="CDF")
    plot.line(bytes, y_bytes, line_width=2)

    return components(plot)


def get_bokeh_delay_mpjoin_mpcapable(**kwargs):
    """ Fetching data """
    delays = query.get_graph_delay_mpjoin_mpcapable(**kwargs)
    if delays:
        delays.append(delays[-1])
    y_delays = np.linspace(0.0, 1.0, len(delays))
    """ Plotting """
    plot = figure(title="CDF of additional subflow establishment delays", x_axis_label="Time between MP_JOIN and MP_CAP [s]",
                  x_range=[10**-3, delays[-1]], x_axis_type="log", y_axis_label="CDF")
    plot.line(delays, y_delays, line_width=2)

    return components(plot)


def get_bokeh_rtt_difference_sfs(c2s, min_rtt_samples=3, **kwargs):
    """ Fetching data """
    diffs = query.get_graph_rtt_difference_sfs(c2s, min_rtt_samples=min_rtt_samples, **kwargs)
    if diffs:
        diffs.append(diffs[-1])
    y_diffs = np.linspace(0.0, 1.0, len(diffs))
    """ Plotting """
    plot = figure(title="Difference of average RTT between worst and best subflows with at least " + str(min_rtt_samples) + " samples",
                  x_axis_label="Difference of average RTT [ms]", x_range=[float(diffs[0]), float(diffs[-1])], x_axis_type="log", y_axis_label="CDF")
    plot.line(diffs, y_diffs, line_width=2)

    return components(plot)


def get_bokeh_size_subflow_blocks(c2s, **kwargs):
    """ Fetching data """
    conn_flows, subflow_flows = query.get_graph_size_subflow_blocks(c2s, **kwargs)
    # Subflow flows has less data that conn_flows, since subflow_flows has filtered connection with only one subflow
    # First "optimise" conn_flows access using a dict
    nb_bursts_dict = {}
    for conn_flow in conn_flows:
        nb_bursts_dict[conn_flow['conn__id']] = conn_flow['nb_bursts']

    TINY = '0B-10KB'
    SMALL = '10KB-100KB'
    MEDIUM = '100KB-1MB'
    LARGE = '>=1MB'
    results = {TINY: [], SMALL: [], MEDIUM: [], LARGE: []}
    for subflow_flow in subflow_flows:
        total_bytes = subflow_flow['total_bytes']
        if total_bytes < 10000:
            key = TINY
        elif total_bytes < 100000:
            key = SMALL
        elif total_bytes < 1000000:
            key = MEDIUM
        else:
            key = LARGE

        try:
            results[key].append(nb_bursts_dict[subflow_flow['conn__id']])
        except Exception:
            # A connection without its subflows...
            pass

    """ Plotting """
    color = {TINY: 'red', SMALL: 'blue', MEDIUM: 'green', LARGE: 'orange'}
    ls = {TINY: 'dotted', SMALL: 'dashdot', MEDIUM: 'dashed', LARGE: 'solid'}
    plot = figure(title="Number of subflow blocks depending on the number of bytes carried by the connection",
                  x_axis_label="# of subflow blocks", x_range=[1, max(results[LARGE])], x_axis_type="log", y_axis_label="CDF")
    for key in [TINY, SMALL, MEDIUM, LARGE]:
        sample = np.array(sorted(results[key]))
        sorted_array = np.sort(sample)
        nb_conns = len(sorted_array)
        yvals = np.arange(len(sorted_array)) / float(len(sorted_array))
        if len(sorted_array) > 0:
            # Add a last point
            sorted_array = np.append(sorted_array, sorted_array[-1])
            yvals = np.append(yvals, 1.0)
            plot.line(sorted_array, yvals, line_width=2, line_color=color[key], line_dash=ls[key],
                      legend=key + ' (' + str(nb_conns) + ')')

    return components(plot)


def get_bokeh_overhead(c2s, **kwargs):
    """ Fetching data """
    # TODO
    pass


def get_bokeh_bytes_by_ip(c2s, sent, **kwargs):
    """ Fetching data """
    raw_results = query.get_graph_bytes_by_ip(c2s, sent, **kwargs)
    aggregate_attr = 'subflow__saddr' if (c2s and sent) or (not c2s and not sent) else 'subflow__daddr'

    # Two passes on results
    total_bytes = 0
    for elem in raw_results:
        total_bytes += elem['bytes_data__sum']

    results = []
    for elem in raw_results:
        results.append({'label': elem[aggregate_attr] + ' ' + '{:0.2f}'.format(100.0 * elem['bytes_data__sum'] / total_bytes) + '%',
                        'value': elem['bytes_data__sum']})

    """ Plotting """
    sent_text = "sent over" if sent else "received on"
    c2s_text = "client to server" if c2s else "server to client"
    plot = Donut(results, title="Number of bytes " + sent_text + " IP address in " + c2s_text + " flow", label="label", values="value")

    return components(plot)


""" Calling graphs """


def get_bokeh_script_and_div(graph_type, **kwargs):
    if graph_type == "duration":
        return get_bokeh_duration(**kwargs)
    elif graph_type == "mptcptrace_bytes_c2s":
        return get_bokeh_bytes(True, **kwargs)
    elif graph_type == "mptcptrace_bytes_s2c":
        return get_bokeh_bytes(False, **kwargs)
    elif graph_type == "delay_mpjoin_mpcapable":
        return get_bokeh_delay_mpjoin_mpcapable(**kwargs)
    elif graph_type == "rtt_difference_sfs_c2s":
        return get_bokeh_rtt_difference_sfs(True, **kwargs)
    elif graph_type == "rtt_difference_sfs_s2c":
        return get_bokeh_rtt_difference_sfs(False, **kwargs)
    elif graph_type == "size_subflow_blocks_c2s":
        return get_bokeh_size_subflow_blocks(True, **kwargs)
    elif graph_type == "size_subflow_blocks_s2c":
        return get_bokeh_size_subflow_blocks(False, **kwargs)
    elif graph_type == "bytes_by_ip_c2s_sent":
        return get_bokeh_bytes_by_ip(True, True, **kwargs)
    elif graph_type == "bytes_by_ip_c2s_received":
        return get_bokeh_bytes_by_ip(True, False, **kwargs)
    elif graph_type == "bytes_by_ip_s2c_sent":
        return get_bokeh_bytes_by_ip(False, True, **kwargs)
    elif graph_type == "bytes_by_ip_s2c_received":
        return get_bokeh_bytes_by_ip(False, False, **kwargs)
    else:
        print("Unknown graph_type: " + str(graph_type))
        raise Http404


""" Smartphone graphs """


def _get_values_labels_valnames_title(exp, data_name, server_ips):
    if exp == "simple_http_get":
        exp_name = "Simple HTTP GET"
    elif exp == "siri":
        exp_name = "Siri"
    elif exp == "msg":
        exp_name = "Instant Messaging"
    else:
        raise NotImplementedError("Unknown exp " + exp)

    if data_name == "time":
        VALUES = "Completion Time [s]"
        TITLE = exp_name + " Completion Time for servers " + str(server_ips)
    elif data_name == "perc_cellular":
        VALUES = "Bytes over cellular [%]"
        TITLE = exp_name + " Percentage of bytes over cellular for server " + str(server_ips)
    elif data_name == "perc_pkt_cellular":
        VALUES = "Packets over cellular [%]"
        TITLE = exp_name + " Percentage of packets over cellular for server " + str(server_ips)
    elif data_name == "open_cellular":
        VALUES = "Time cellular open [%]"
        TITLE = exp_name + " Percentage of time cellular is open for server " + str(server_ips)
    elif data_name == "delays":
        VALUES = "Delays [ms]"
        TITLE = exp_name + " Delays for server " + str(server_ips)
    elif data_name == "max_delay":
        VALUES = "Max Delay [ms]"
        TITLE = exp_name + " Max Delay for server " + str(server_ips)
    elif data_name == "missed":
        VALUES = "Missed [#]"
        TITLE = exp_name + " Missed requests for server " + str(server_ips)
    elif data_name == "cell_energy_total":
        VALUES = "Energy [J]"
        TITLE = exp_name + " Total cellular energy consumption"
    elif data_name == "cell_mean_power":
        VALUES = "Power [mW]"
        TITLE = exp_name + " Mean cellular power consumption"
    else:
        raise NotImplementedError("Unknown data_name " + data_name)

    LABELS = "Configuration"
    labels_valnames = [("0", "No Backup"), ("1", "Backup"), ("2", "IETF Backup"), ("3", "MultiMob")]

    return VALUES, LABELS, labels_valnames, TITLE


# The graph functions, to format the data
def _boxplot_init_results(**kwargs):
    return {kwargs['VALUES']: [], kwargs['LABELS']: []}


def _cdf_init_results(**kwargs):
    return {}


def _boxplot_graph_data(config, config_name, data, graph_data, **kwargs):
    for d in data:
        graph_data[kwargs['LABELS']].append(config_name)
        graph_data[kwargs['VALUES']].append(d)


def _cdf_graph_data(config, config_name, data, graph_data, **kwargs):
    if config_name not in graph_data:
        graph_data[config_name] = []

    for d in data:
        graph_data[config_name].append(d)


def _get_boxplot(graph_data, VALUES, LABELS, TITLE, **kwargs):
    plot = BoxPlot(graph_data, values=VALUES, label=LABELS, color=LABELS, title=TITLE, plot_width=1000, legend=False)
    plot.xaxis.major_label_text_font = "26pt"
    plot.yaxis.major_label_text_font = "26pt"
    plot.xaxis.axis_label_text_font_size = "30pt"
    plot.yaxis.axis_label_text_font_size = "30pt"
    # plot.legend.label_text_font_size = "22pt"

    return plot


def _get_cdf(graph_data, VALUES, LABELS, TITLE, **kwargs):
    count = 0
    colors = {"No Backup": 'orange', "Backup": 'blue', "IETF Backup": 'green', "MultiMob": 'red'}
    lds = {"No Backup": 'dotdash', "Backup": 'dashed', "IETF Backup": 'dotted', "MultiMob": 'solid'}
    plot = figure(title=TITLE, x_axis_label=VALUES, x_axis_type=kwargs.get("x_axis_type", "linear"), y_axis_label="CDF", plot_width=1000)
    for key in sorted(graph_data.keys()):
        sample = np.array(sorted(graph_data[key]))
        if len(sample) == 0:
            continue
        xvals = np.sort(sample)
        nb_data = len(xvals)
        yvals = np.arange(1, len(xvals) + 1) / float(len(xvals))
        # Add a last point
        xvals = np.insert(xvals, 0, xvals[0])
        yvals = np.insert(yvals, 0, 0.0)
        plot.line(xvals, yvals, line_width=2, line_color=colors[key], line_dash=lds[key],
                  legend=key + ' (' + str(nb_data) + ')')
        count += 1

    plot.xaxis.major_label_text_font = "22pt"
    plot.yaxis.major_label_text_font = "22pt"
    plot.xaxis.axis_label_text_font_size = "30pt"
    plot.yaxis.axis_label_text_font_size = "30pt"
    plot.legend.label_text_font_size = "22pt"
    plot.legend.location = "bottom_right"

    return plot


def _get_cdf_log(graph_data, VALUES, LABELS, TITLE, **kwargs):
    kwargs['x_axis_type'] = "log"
    return _get_cdf(graph_data, VALUES, LABELS, TITLE, **kwargs)


def _get_graph_funcs(graph_name):
    if graph_name == "boxplot":
        return _boxplot_init_results, _boxplot_graph_data, _get_boxplot
    elif graph_name == "cdf":
        return _cdf_init_results, _cdf_graph_data, _get_cdf
    elif graph_name == "cdf_log":
        return _cdf_init_results, _cdf_graph_data, _get_cdf_log
    else:
        raise NotImplementedError("Unknown graph_name " + graph_name)


def get_bokeh_smartphone_graph(exp, data_name, server_ips, graph_name, select_name):
    VALUES, LABELS, labels_valnames, TITLE = _get_values_labels_valnames_title(exp, data_name, server_ips)
    kwargs = {'VALUES': VALUES, 'LABELS': LABELS}
    init_func, graph_data_func, plot_func = _get_graph_funcs(graph_name)
    graph_data = query.get_graph_data_smartphone(exp, data_name, server_ips, labels_valnames, init_func, graph_data_func, select_name, **kwargs)
    plot = plot_func(graph_data, VALUES, LABELS, TITLE, **{})

    return components(plot)


""" Calling smartphone graphs """


def get_bokeh_script_and_div_smartphone(exp, data_name, server_name, graph_name, select_name):
    MPTCP_1 = ["5.196.169.232", "2001:41d0:8:aa1:1::1"]
    MPTCP_2 = ["5.196.169.233", "2001:41d0:8:aa1:2::1"]

    if server_name == "mptcp_1":
        server_ips = MPTCP_1
    elif server_name == "mptcp_2":
        server_ips = MPTCP_2
    elif server_name == "all":
        server_ips = MPTCP_1 + MPTCP_2
    else:
        print("Unknown server: " + str(server_name))
        raise Http404

    return get_bokeh_smartphone_graph(exp, data_name, server_ips, graph_name, select_name)
