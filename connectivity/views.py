from django.views.generic import ListView

from rest_framework.generics import CreateAPIView
from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from rest_framework.response import Response
from rest_framework import status

from .models import ConnectivityOldResult
from .serializers import ConnectivityTestSerializer


class ConnectivityTestCreateView(CreateAPIView):
    serializer_class = ConnectivityTestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConnectivityResultListView(LoginRequiredMixin, SuperuserRequiredMixin,
                                 ListView):
    model = ConnectivityOldResult
    paginate_by = 20
    ordering = '-smartphonetest__start_time'
    queryset = ConnectivityOldResult.objects.select_related(
        'smartphonetest', 'smartphonetest__bench__connectivitybench')
