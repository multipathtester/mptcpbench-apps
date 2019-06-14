from datetime import datetime
import os
import uuid

from django.db import models
from django.utils.timezone import make_aware
from django.contrib.postgres.fields import JSONField

from .managers import NoTestManager, SmartphoneTestManager, NetcfgLineManager
from mptcpbench.benches.models import Bench


class Machine(models.Model):
    """ An participating host to tests """
    host_os = models.CharField(max_length=200)
    mptcp_version = models.CharField(max_length=200)
    tag = models.CharField(max_length=200, primary_key=True)


class Sysctl(models.Model):
    """ Sysctl networking configuration """
    # Please keep this in alphabetical order
    """ TCP sysctls """
    # TODO add maybe more sysctls, need to determine which ones to add
    net_ipv4_tcp_autocorking = models.PositiveSmallIntegerField()
    net_ipv4_tcp_congestion_control = models.CharField(max_length=16)
    net_ipv4_tcp_dsack = models.PositiveSmallIntegerField()
    net_ipv4_tcp_early_retrans = models.PositiveSmallIntegerField()
    net_ipv4_tcp_fack = models.PositiveSmallIntegerField()
    net_ipv4_tcp_fin_timeout = models.PositiveSmallIntegerField()
    net_ipv4_tcp_frto = models.PositiveSmallIntegerField()
    net_ipv4_tcp_keepalive_intvl = models.PositiveSmallIntegerField()
    net_ipv4_tcp_keepalive_probes = models.PositiveSmallIntegerField()
    net_ipv4_tcp_keepalive_time = models.PositiveIntegerField()
    net_ipv4_tcp_limit_output_bytes = models.PositiveIntegerField()
    net_ipv4_tcp_low_latency = models.PositiveSmallIntegerField()
    net_ipv4_tcp_moderate_rcvbuf = models.PositiveSmallIntegerField()
    net_ipv4_tcp_no_metrics_save = models.PositiveSmallIntegerField()
    net_ipv4_tcp_probe_interval = models.PositiveIntegerField()
    net_ipv4_tcp_probe_threshold = models.PositiveIntegerField()
    net_ipv4_tcp_reordering = models.PositiveSmallIntegerField()
    net_ipv4_tcp_retries1 = models.PositiveSmallIntegerField()
    net_ipv4_tcp_retries2 = models.PositiveSmallIntegerField()
    # Sysctl net_ipv4_tcp_rmem cut in three parts, cleaner in DB
    net_ipv4_tcp_rmem_min = models.PositiveIntegerField()
    net_ipv4_tcp_rmem_default = models.PositiveIntegerField()
    net_ipv4_tcp_rmem_max = models.PositiveIntegerField()
    net_ipv4_tcp_slow_start_after_idle = models.PositiveSmallIntegerField()
    net_ipv4_tcp_syn_retries = models.PositiveSmallIntegerField()
    net_ipv4_tcp_synack_retries = models.PositiveSmallIntegerField()
    # Sysctl net_ipv4_tcp_wmem cut in three parts, cleaner in DB
    net_ipv4_tcp_wmem_min = models.PositiveIntegerField()
    net_ipv4_tcp_wmem_default = models.PositiveIntegerField()
    net_ipv4_tcp_wmem_max = models.PositiveIntegerField()

    """ Multipath TCP sysctls """
    net_mptcp_mptcp_binder_gateways = models.PositiveSmallIntegerField(default=0)
    net_mptcp_mptcp_checksum = models.PositiveSmallIntegerField()
    net_mptcp_mptcp_debug = models.PositiveSmallIntegerField()
    net_mptcp_mptcp_enabled = models.PositiveSmallIntegerField()
    net_mptcp_mptcp_path_manager = models.CharField(max_length=16)
    net_mptcp_mptcp_scheduler = models.CharField(max_length=16)
    net_mptcp_mptcp_syn_retries = models.PositiveSmallIntegerField()

    def get_or_create_sysctl_from_dict(sysctl_dict):
        test_sysctl = Sysctl()
        processed_sysctl_dict = {}
        for key in sysctl_dict:
            # Be as compatible as possible
            processed_key = key.replace(".", "_")
            if hasattr(test_sysctl, processed_key):
                if processed_key == "net_mptcp_mptcp_binder_gateways" and sysctl_dict[key] == "":
                    processed_sysctl_dict[processed_key] = 0
                else:
                    processed_sysctl_dict[processed_key] = sysctl_dict[key]
            elif processed_key in ["net_ipv4_tcp_rmem", "net_ipv4_tcp_wmem"]:
                # Two special cases: net_ipv4_tcp_rmem and net_ipv4_tcp_wmem
                try:
                    min_val, default_val, max_val = sysctl_dict[key].split()
                    processed_sysctl_dict[processed_key + "_min"] = min_val
                    processed_sysctl_dict[processed_key + "_default"] = default_val
                    processed_sysctl_dict[processed_key + "_max"] = max_val
                except ValueError:
                    print("Sysctl key", key, "with unexpected format")

        return Sysctl.objects.get_or_create(**processed_sysctl_dict)


class IPAddress(models.Model):
    """ An classical IP address, needed as a class to allow to link several IPs to several interfaces """
    ip_address = models.GenericIPAddressField(protocol="both")


class Interface(models.Model):
    """ A network interface """
    name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)
    is_backup = models.BooleanField(default=False)
    ips = models.ManyToManyField(IPAddress)

    def _is_already_in_database(processed_interface_dict, ip_vals):
        """ Return True, i if the database has an Interface i with attributes matching exactly the given arguments
            If False, the second argument in not determined (either a failed candidate_interface or None)
        """
        candidate_interfaces = Interface.objects.filter(**processed_interface_dict)

        for ip in ip_vals:
            candidate_interfaces = candidate_interfaces.filter(ips__ip_address=ip)

        if candidate_interfaces.count() > 1:
            for candidate_interface in candidate_interfaces.all():
                if candidate_interface.ips.count() == len(ip_vals):
                    return True, candidate_interface

            return False, None
        elif candidate_interfaces.count() == 1:
            return candidate_interfaces[0].ips.count() == len(ip_vals), candidate_interfaces[0]
        else:
            return False, None

    def get_or_create_interface_from_dict(interface_dict):
        ip_dicts = []
        processed_interface_dict = {}
        interface = Interface()
        for key in interface_dict:
            if key == "ips":
                ip_dicts = interface_dict[key]
            elif hasattr(interface, key):
                processed_interface_dict[key] = interface_dict[key]

        ip_vals = [x["addr"] for x in ip_dicts]

        # In order to avoid putting too much data in DB, try to reuse existing interfaces and IPs
        in_db, return_interface = Interface._is_already_in_database(processed_interface_dict, ip_vals)
        if in_db:
            return return_interface, False

        interface = Interface.objects.create(**processed_interface_dict)
        for ip in ip_vals:
            ip_address, ip_address_created = IPAddress.objects.get_or_create(ip_address=ip)
            interface.ips.add(ip_address)

        interface.save()
        return interface, True


class Result(models.Model):
    """ Hook to allow defining child classes for different bench results """
    run_time = models.DurationField()

    def create_result_from_dict(result_dict):
        # This should be never reached
        raise Exception("create_result_from_dict must be overriden")

    def create_netcfgs(netcfgs, result):
        for order in range(len(netcfgs)):
            timestamp = netcfgs[order]["timestamp"]
            for netcfg_elem in netcfgs[order]["lines"]:
                NetcfgLine.objects.create(
                    result=result,
                    interface=netcfg_elem["interface"],
                    ip_address=netcfg_elem["ip"],
                    order=order,
                    timestamp=make_aware(datetime.fromtimestamp(
                        float(timestamp)))
                )


class NetcfgLine(models.Model):
    """ By default, only records up interfaces at a given time """
    result = models.ForeignKey(Result)
    interface = models.CharField(max_length=16)
    ip_address = models.CharField(max_length=43)  # Worst case: IPv6 with 8 * 4 hex + 7 ':' + 1 '/' + 3 prefix (up to '128') = 43
    order = models.PositiveIntegerField()
    timestamp = models.DateTimeField()

    objects = NetcfgLineManager()


def get_trace_path_from_test(test):
    if isinstance(test, BenchTest):
        return os.path.join(test.server_machine.tag, test.client_machine.tag, test.uuid + ".pcap")
    elif isinstance(test, SmartphoneTest):
        return os.path.join(test.server_ip, test.device_id,
                            test.bench.name + "_" + test.config_name + "_" + test.start_time.strftime("%Y%m%d%H%M%S%f") + ".pcap")

    # NoTest
    return os.path.join(test.uploader_email, test.time.strftime("%Y%m%d"), str(uuid.uuid1()) + ".pcap")


def get_trace_path_from_trace(instance, filename):
    if instance.is_undefined:
        if instance.is_smartphone:
            test = instance.test
            directory = "passive_smartphone_traces"
            name_prefix = "passive_"
        else:
            test = instance.test
            directory = "undefined_traces"
            name_prefix = "undefined_"
    elif instance.is_smartphone:
        if instance.is_client_trace:
            test = instance.smartphone_client_test
            directory = "smartphone_client_traces"
            name_prefix = "client_"
        else:
            test = instance.smartphone_server_traces
            directory = "smartphone_server_traces"
            name_prefix = "server_"
    else:
        if instance.is_client_trace:
            test = instance.client_test
            directory = "client_traces"
            name_prefix = "client_"
        else:
            test = instance.server_test
            directory = "server_traces"
            name_prefix = "server_"

    path_from_test = get_trace_path_from_test(test)
    processed_path = os.path.join(os.path.dirname(path_from_test), name_prefix + os.path.basename(path_from_test))
    return os.path.join(directory, processed_path)


class Trace(models.Model):
    """ A PCAP trace """
    name = models.CharField(max_length=200)
    user_name = models.CharField(max_length=200)
    is_analyzed = models.BooleanField(default=False)
    is_client_trace = models.BooleanField()
    is_smartphone = models.BooleanField()
    is_undefined = models.BooleanField()
    file = models.FileField(upload_to=get_trace_path_from_trace, max_length=200)

    class Meta:
        # Only two traces (client and server) can have the same name
        unique_together = (("name", "is_client_trace"),)


class TraceAnalysisError(models.Model):
    """ Log all errors raised while analysis a trace """
    trace = models.OneToOneField(Trace, primary_key=True)
    error = models.CharField(max_length=2048)


class Test(models.Model):
    """
        A test instance, cannot be instantiated as it
        To find the true subtype of a test, one can use a trace;
        trace.is_undefined is True <--> trace comes from NoTest, with notest.trace == trace
        trace_is_undefined is False <--> trace comes from BenchTest
    """
    bench = models.ForeignKey(Bench, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class BenchTest(Test):
    """ A test generated by the benchmark tool """
    client_analysis = models.BooleanField(default=True)
    client_interfaces = models.ManyToManyField(Interface, related_name="client_tests")
    client_machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="client_tests")
    client_sysctl = models.ForeignKey(Sysctl, on_delete=models.CASCADE, related_name="client_tests")
    client_trace = models.OneToOneField(Trace, models.CASCADE, blank=True, null=True, related_name="client_test")
    client_version = models.CharField(max_length=200)
    result = models.OneToOneField(Result, on_delete=models.CASCADE)
    server_interfaces = models.ManyToManyField(Interface, related_name="server_tests")
    server_machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="server_tests")
    server_sysctl = models.ForeignKey(Sysctl, on_delete=models.CASCADE, related_name="server_tests")
    server_trace = models.OneToOneField(Trace, models.CASCADE, blank=True, null=True, related_name="server_test")
    server_version = models.CharField(max_length=200)
    start_time = models.DateTimeField('starting time')
    uuid = models.UUIDField(primary_key=True, editable=False)

    class Meta:
        # Between two machines, only one test at a time
        unique_together = (("client_machine", "server_machine", "start_time"))


class SmartphoneTest(Test):
    """ An active test ran by smartphone """
    client_trace = models.OneToOneField(Trace, models.CASCADE, blank=True, null=True, related_name="smartphone_client_test")
    config_name = models.CharField(max_length=20)
    device_id = models.CharField(max_length=36)
    received_time = models.DateTimeField()
    result = models.OneToOneField(Result)
    server_ip = models.GenericIPAddressField(protocol="both")
    server_trace = models.OneToOneField(Trace, models.CASCADE, blank=True, null=True, related_name="smartphone_server_test")
    start_time = models.DateTimeField()

    objects = SmartphoneTestManager()


class ProtoInfo(models.Model):
    """ Protocol information for a particular test """
    data = JSONField()
    test = models.OneToOneField(SmartphoneTest, models.CASCADE, primary_key=True)


class SmartphoneTestGroup(models.Model):
    """ Is a test part of a larger group? """
    start_time = models.DateTimeField()
    test = models.OneToOneField(SmartphoneTest, models.CASCADE, primary_key=True)


class NoTest(Test):
    """ A test which is not actually one, used when a trace is uploaded just to be analyzed """
    time = models.DateTimeField()
    trace = models.OneToOneField(Trace, models.CASCADE, blank=True, null=True, related_name="test")
    uploader_email = models.EmailField()

    # Custom model manager
    objects = NoTestManager()


class CellEnergy(models.Model):
    """ Cellular energy estimation for a test """
    lte_promotion_energy = models.FloatField()
    lte_promotion_time = models.DurationField()
    rrc_crx_energy = models.FloatField()
    rrc_crx_time = models.DurationField()
    rrc_idle_energy = models.FloatField()
    rrc_idle_time = models.DurationField()
    rrc_short_drx_energy = models.FloatField()
    rrc_short_drx_time = models.DurationField()
    rrc_long_drx_energy = models.FloatField()
    rrc_long_drx_time = models.DurationField()
    total_energy = models.FloatField()
    total_time = models.DurationField()
    trace = models.OneToOneField(Trace, models.CASCADE)
