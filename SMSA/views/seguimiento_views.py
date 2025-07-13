from SMSA.serializers.seguimiento_serializers import SeguimientoSerializer
from SMSA.models import Seguimiento
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

class UserPagination(PageNumberPagination):
    page_size = 40

class SeguimientoViewSet(viewsets.ModelViewSet):
    queryset = Seguimiento.objects.all()
    serializer_class = SeguimientoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        estudiante_id = self.request.query_params.get('estudiante', None)
        titulo = self.request.query_params.get('titulo', None)
        fecha_inicio = self.request.query_params.get('fechaInicio', None)
        fecha_fin = self.request.query_params.get('fechaFin', None)

        if estudiante_id:
            queryset = queryset.filter(estudiante__id=estudiante_id)
        if titulo:
            queryset = queryset.filter(titulo__icontains=titulo)
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(fecha__range=[fecha_inicio, fecha_fin])
        
        return queryset