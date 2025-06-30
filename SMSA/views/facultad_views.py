from SMSA.models import Facultad
from SMSA.serializers.facultad_serializers import FacultadSerializer
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

class FacultadPagination(PageNumberPagination):
    page_size = 20

class FacultadViewSet(viewsets.ModelViewSet):
    queryset = Facultad.objects.all()
    serializer_class = FacultadSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = FacultadPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        id = self.request.query_params.get('id', None)
        codigo = self.request.query_params.get('codigo', None)
        nombre = self.request.query_params.get('nombre', None)

        if id is not None:
            queryset = queryset.filter(id=id)
        if codigo is not None:
            queryset = queryset.filter(codigo__startswith=codigo)
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)   

        queryset = queryset.order_by('codigo')
            
        return queryset
