from SMSA.serializers.user_serializers import UserSerializer
from SMSA.models import User
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

class UserPagination(PageNumberPagination):
    page_size = 20

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = UserPagination

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    #Consultar por filtros
    def get_queryset(self):
        
        queryset = super().get_queryset()
        queryset = queryset.filter(is_superuser=False)  # Excluir superusuarios

        id = self.request.query_params.get('id', None)
        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)
        cargo = self.request.query_params.get('cargo', None)
        nivel_permisos = self.request.query_params.get('nivel_permisos', None)
        nivel_permisos_gt = self.request.query_params.get('nivel_permisos__gt', None)
        
        if id is not None:
            queryset = queryset.filter(id=id)
        if username is not None:
            queryset = queryset.filter(username__startswith=username)
        if email is not None:
            queryset = queryset.filter(email__startswith=email)
        if first_name is not None:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name is not None:
            queryset = queryset.filter(last_name__icontains=last_name)
        if cargo is not None:
            queryset = queryset.filter(cargo__icontains=cargo)
        if nivel_permisos is not None:
            queryset = queryset.filter(nivel_permisos=nivel_permisos)
        if nivel_permisos_gt is not None:
            queryset = queryset.filter(nivel_permisos__gt=nivel_permisos_gt)

        return queryset