from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .mobility_helper import get_mobile_stats
from .benchmark_helper import get_benchmark_stats
from .multipath_helper import get_multipath_stats
from .mobility_detail import get_mobility_detail, get_quic_mobility_detail


@login_required
def mobility_info(request):
    if not request.user.is_superuser:
        raise Http404

    version_operator = request.GET.get("version_operator", None)
    version = request.GET.get("version", None)
    only_mobility = request.GET.get("only_mobility", None) is not None
    data_dict = get_mobile_stats(version_operator=version_operator,
                                 version=version,
                                 only_mobility=only_mobility)
    return render(request, 'analyzer/mobility.html', data_dict)


@login_required
def benchmark_info(request):
    if not request.user.is_superuser:
        raise Http404

    data_dict = get_benchmark_stats()
    return render(request, 'analyzer/benchmark.html', data_dict)


@login_required
def multipath_info(request):
    if not request.user.is_superuser:
        raise Http404

    data_dict = get_multipath_stats()
    return render(request, 'analyzer/multipath.html', data_dict)


@login_required
def mobility_detail(request):
    if not request.user.is_superuser:
        raise Http404

    data_dict = get_mobility_detail()
    return render(request, 'analyzer/mobility.html', {})

@login_required
def quic_mobility_detail(request):
    if not request.user.is_superuser:
        raise Http404

    data_dict = get_quic_mobility_detail()
    return render(request, 'analyzer/mobility.html', {})
