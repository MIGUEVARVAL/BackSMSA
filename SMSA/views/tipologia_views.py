from SMSA.serializers.tipologia_serializers import TipologiaSerializer
from SMSA.models import Tipologia
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class TipologiaViewSet(viewsets.ModelViewSet):
    queryset = Tipologia.objects.all()
    serializer_class = TipologiaSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()

        id = self.request.query_params.get('id', None)
        codigo = self.request.query_params.get('codigo', None)
        nombre = self.request.query_params.get('nombre', None)
        order_by = self.request.query_params.get('orderBy', None)
        order_direction = self.request.query_params.get('orderDirection', None)

        if id is not None:
            queryset = queryset.filter(id=id)
        if codigo is not None:
            queryset = queryset.filter(codigo__startswith=codigo)
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)
        if order_by is not None:
            if order_direction == 'DESC':
                queryset = queryset.order_by(f'-{order_by}')
            else:
                queryset = queryset.order_by(order_by)

        return queryset