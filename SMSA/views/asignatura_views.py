from SMSA.models import Asignatura
from SMSA.serializers.asignatura_serializers import AsignaturaSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 20

class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = Pagination  

    def get_queryset(self):
        queryset = super().get_queryset()

        codigo = self.request.query_params.get('codigo', None)
        nombre = self.request.query_params.get('nombre', None)
        uab = self.request.query_params.get('uab', None)

        if codigo is not None:
            queryset = queryset.filter(codigo__startswith=codigo)
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)
        if uab is not None:
            queryset = queryset.filter(uab__id=uab)

        return queryset
    
    