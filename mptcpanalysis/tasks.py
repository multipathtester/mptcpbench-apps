from __future__ import absolute_import

import glob
import os
import shutil
import subprocess
import traceback

from django.conf import settings
from django.db.transaction import atomic

from config.celery import app
from mptcpbench.collect.models import TraceAnalysisError
from mptcpbench.collect.tasks import _cell_energy_estimation
from mptcpbench.mptcp_analysis_scripts import mptcp
from . import models


def _launch_analyze(full_trace_path):
    DEVNULL = "/dev/null"
    analysis_dict, _, _, _, _ = mptcp.process_trace(full_trace_path, DEVNULL,
                                                    DEVNULL, DEVNULL, DEVNULL,
                                                    DEVNULL, DEVNULL, DEVNULL,
                                                    DEVNULL, False, False,
                                                    return_dict=True)

    return analysis_dict


def _create_mptcp_connections(analysis_dict, test, trace):
    models.create_mptcp_connections_from_dict(analysis_dict, test, trace)
    trace.is_analyzed = True
    trace.save()


def _update_mptcp_connections(analysis_dict, test, trace):
    """ Only update the field client_to_server if trace.is_client_trace, else
        server_to_client
    """

    raise NotImplementedError("_update_mptcp_connections")

    interfaces = test.client_interfaces.all() if trace.is_client_trace else \
        test.server_interfaces.all()
    for mptcp_conn_key in analysis_dict:
        models.MPTCPConnection.update_mptcp_conn_from_dict(
            analysis_dict[mptcp_conn_key],
            mptcp_conn_key,
            test,
            trace,
            interfaces
        )

    trace.is_analyzed = True
    trace.save()


@atomic
def _update_database(analysis_dict, trace):
    # Select for update to avoid race condition, with atomic decorator for
    # the critical part
    if trace.is_undefined:
        # This is ok for passive smartphone traces
        test = models.NoTest.objects.select_for_update().get(id=trace.test.id)
        return _create_mptcp_connections(analysis_dict, test, trace)

    if trace.is_smartphone:
        if trace.is_client_trace:
            trace = models.Trace.objects.select_related(
                'smartphone_client_test').get(name=trace.name,
                                              is_client_trace=True)
            other_trace = models.Trace.objects.get(
                name=trace.name, is_client_trace=False)
            test = models.SmartphoneTest.objects.select_for_update(
            ).select_related().get(id=trace.smartphone_client_test.id)
        else:
            trace = models.Trace.objects.select_related(
                'smartphone_server_test').get(name=trace.name,
                                              is_client_trace=False)
            other_trace = models.Trace.objects.get(
                name=trace.name, is_client_trace=True)
            test = models.SmartphoneTest.objects.select_for_update(
            ).select_related().get(id=trace.smartphone_server_test.id)
    else:
        if trace.is_client_trace:
            trace = models.Trace.objects.select_related(
                'client_test').get(name=trace.name, is_client_trace=True)
            other_trace = models.Trace.objects.get(
                name=trace.name, is_client_trace=False)
            test = models.BenchTest.objects.select_for_update(
            ).select_related().get(id=trace.client_test.id)
        else:
            trace = models.Trace.objects.select_related(
                'server_test').get(name=trace.name, is_client_trace=False)
            other_trace = models.Trace.objects.get(
                name=trace.name, is_client_trace=True)
            test = models.BenchTest.objects.select_for_update().get(
                id=trace.server_test.id
            )

    if other_trace.is_analyzed:
        _update_mptcp_connections(analysis_dict, test, trace)
    else:
        _create_mptcp_connections(analysis_dict, test, trace)


def _run_pcapfix(trace_path, trace_name, link_type):
    full_trace_path = os.path.join(str(settings.MEDIA_ROOT), trace_path)
    fixed_trace_path = os.path.join(os.path.dirname(
        full_trace_path), 'fixed_' + os.path.basename(full_trace_path))
    os.system('pcapfix -t ' + str(link_type) + ' -o ' +
              fixed_trace_path + ' ' + full_trace_path)
    # Dirty patch fix for an bug in pcapfix... It can add garbage characters
    # (like "A?") at the end of full_trace_path
    available_outputs = glob.glob(fixed_trace_path + "*")
    if len(available_outputs) == 1:
        fixed_trace_path = available_outputs[0]
    shutil.move(fixed_trace_path, full_trace_path)


@app.task
def analyze_trace(trace_path, trace_name, is_client_trace, is_undefined,
                  is_smartphone, pcapfix_link_type):
    # Fix the trace before analyzing it, if requested
    if pcapfix_link_type:
        _run_pcapfix(trace_path, trace_name, pcapfix_link_type)

    # The trace must be first registered before starting to analyze it
    trace = models.Trace.objects.get(
        name=trace_name, is_client_trace=is_client_trace,
        is_undefined=is_undefined, is_smartphone=is_smartphone
    )
    print("Will analyze the trace " +
          os.path.join(settings.MEDIA_ROOT, trace_path) +
          " with is_client_trace " +
          str(trace.is_client_trace) +
          " and is_undefined " +
          str(trace.is_undefined) +
          " and is_smartphone " +
          str(trace.is_smartphone))
    try:
        analysis_dict = _launch_analyze(
            os.path.join(settings.MEDIA_ROOT, trace_path))
        _update_database(analysis_dict, trace)
        if (is_smartphone and is_client_trace) or (is_smartphone and
                                                   is_undefined):
            _cell_energy_estimation(trace, trace_name, trace_path)
    except Exception:
        # Store error in DB for further processing
        TraceAnalysisError.objects.create(trace=trace,
                                          error=traceback.format_exc())


@app.task
def rewrite_pcap(trace_path):
    rewritten_path = os.path.join(settings.MEDIA_ROOT, os.path.dirname(
        trace_path),
        "rewritten_" + os.path.splitext(os.path.basename(trace_path))[0] +
        ".pcap")
    cmd = ["tcpdump", "-r",
           os.path.join(settings.MEDIA_ROOT, trace_path), "-w", rewritten_path]
    if subprocess.call(cmd) != 0:
        return "Error when rewritting the trace: tcpdump error"

    try:
        shutil.move(rewritten_path, os.path.join(
            settings.MEDIA_ROOT, trace_path))
    except Exception as e:
        return "Error when rewritting the trace: " + str(e)

    return "OK"
