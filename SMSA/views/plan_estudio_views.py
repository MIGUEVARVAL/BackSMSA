from SMSA.models import PlanEstudio
from SMSA.serializers.plan_estudio_serializers import PlanEstudioSerializer
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

class PlanEstudioPagination(PageNumberPagination):
    page_size = 20

class PlanEstudioViewSet(viewsets.ModelViewSet):
    queryset = PlanEstudio.objects.all()
    serializer_class = PlanEstudioSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = PlanEstudioPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        id = self.request.query_params.get('id', None)
        codigo = self.request.query_params.get('codigo', None)
        nombre = self.request.query_params.get('nombre', None)
        nivel = self.request.query_params.get('nivel', None)
        tipo_nivel = self.request.query_params.get('tipo_nivel', None)
        activo = self.request.query_params.get('activo', None)
        facultad_id = self.request.query_params.get('facultad_id', None)
        order_by = self.request.query_params.get('orderBy', None)
        order_direction = self.request.query_params.get('orderDirection', None)

        if id is not None:
            queryset = queryset.filter(id=id)
        if codigo is not None:
            queryset = queryset.filter(codigo__startswith=codigo)
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)
        if nivel is not None:
            queryset = queryset.filter(nivel__icontains=nivel)
        if tipo_nivel is not None:
            queryset = queryset.filter(tipo_nivel__icontains=tipo_nivel)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        if facultad_id is not None:
            queryset = queryset.filter(facultad__id=facultad_id)
        if order_by is not None:
            if order_direction == 'DESC':
                queryset = queryset.order_by(f'-{order_by}')
            else:
                queryset = queryset.order_by(order_by)


        return queryset