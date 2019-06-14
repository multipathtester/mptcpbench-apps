from __future__ import absolute_import

from datetime import timedelta
import os

from django.conf import settings

from . import models, query


def _process_cell_energy_estimation_output(trace, output_filepath):
    """ Store the results of output_filepath to test_id, and delete the file
        output_filepath
    """
    output_file = open(output_filepath)
    lines = output_file.readlines()
    first_line = True
    for line in lines:
        if first_line:
            first_line = False
        else:
            split_line = line.split(';')
            state, energy, duration = split_line
            if state == "LTE_PROMOTION":
                lte_promotion_energy = float(energy)
                lte_promotion_time = timedelta(seconds=float(duration))
            elif state == "RRC_CRX":
                rrc_crx_energy = float(energy)
                rrc_crx_time = timedelta(seconds=float(duration))
            elif state == "RRC_IDLE":
                rrc_idle_energy = float(energy)
                rrc_idle_time = timedelta(seconds=float(duration))
            elif state == "RRC_SHORT_DRX":
                rrc_short_drx_energy = float(energy)
                rrc_short_drx_time = timedelta(seconds=float(duration))
            elif state == "RRC_LONG_DRX":
                rrc_long_drx_energy = float(energy)
                rrc_long_drx_time = timedelta(seconds=float(duration))
            elif state == "TOTAL":
                total_energy = float(energy)
                total_time = timedelta(seconds=float(duration))

    # We expect the file is correct, so error should never happen
    models.CellEnergy.objects.create(
        lte_promotion_energy=lte_promotion_energy,
        lte_promotion_time=lte_promotion_time,
        rrc_crx_energy=rrc_crx_energy, rrc_crx_time=rrc_crx_time,
        rrc_idle_energy=rrc_idle_energy, rrc_idle_time=rrc_idle_time,
        rrc_short_drx_energy=rrc_short_drx_energy,
        rrc_short_drx_time=rrc_short_drx_time,
        rrc_long_drx_energy=rrc_long_drx_energy,
        rrc_long_drx_time=rrc_long_drx_time,
        total_energy=total_energy, total_time=total_time, trace=trace)

    # Close the file and delete it
    output_file.close()
    try:
        os.remove(output_filepath)
    except Exception:
        pass


def _cell_energy_estimation(trace, trace_name, trace_path):
    smartphone_test = None
    if trace.is_client_trace and not trace.is_undefined:
        smartphone_test = models.SmartphoneTest.objects.get(client_trace=trace)

    cell_ips = query.get_cell_ips_in_trace(trace,
                                           smartphone_test=smartphone_test)
    cell_ips_str = ','.join(cell_ips)
    if not cell_ips_str:
        # Give an empty argument
        cell_ips_str = ","
    output_filepath = os.path.join(
        settings.MEDIA_ROOT,
        os.path.basename(trace_name) + "_cell_energy"
    )
    err = os.system('cell_energy_estimator ' +
                    os.path.join(settings.MEDIA_ROOT, trace_path) +
                    ' ' +
                    output_filepath +
                    ' ' +
                    cell_ips_str)

    if not err == 0:
        print("An error occured for " + trace_name)
        return

    _process_cell_energy_estimation_output(trace, output_filepath)
