from SMSA.serializers.historico_seguimiento_serializers import HistoricoSeguimientoSerializer
from SMSA.models import HistoricoSeguimiento
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 20

class HistoricoSeguimientoViewSet(viewsets.ModelViewSet):
    queryset = HistoricoSeguimiento.objects.all()
    serializer_class = HistoricoSeguimientoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = Pagination

    def perform_create(self, serializer):
        # Asignar automáticamente el usuario autenticado
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()

        seguimiento_id = self.request.query_params.get('estrategia_id', None)
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        estudiante_id = self.request.query_params.get('estudiante_id', None)

        if seguimiento_id is not None:
            queryset = queryset.filter(seguimiento__id=seguimiento_id)
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(fecha__range=[fecha_inicio, fecha_fin])
        if estudiante_id is not None:
            queryset = queryset.filter(seguimiento__estudiante__id=estudiante_id)

        return queryset