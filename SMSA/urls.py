from rest_framework import routers
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from SMSA.views.token_views import CustomTokenObtainPairView
from SMSA.views.user_views import UserViewSet
from SMSA.views.facultad_views import FacultadViewSet


router = routers.DefaultRouter()

router.register('api/user', UserViewSet, 'user')
router.register('api/facultad', FacultadViewSet, 'facultad')

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls