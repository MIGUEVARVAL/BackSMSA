from SMSA.serializers.user_serializers import UserSerializer
from SMSA.models import User
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

class UserPagination(PageNumberPagination):
    page_size = 20  # Cambia este valor según lo que necesites

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    #Consultar por filtros
    def get_queryset(self):
        queryset = super().get_queryset()
        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)

        id = self.request.query_params.get('id', None)
        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)
        if id is not None:
            queryset = queryset.filter(id=id)
        if username is not None:
            queryset = queryset.filter(username=username)
        if email is not None:
            queryset = queryset.filter(email=email)

        return queryset