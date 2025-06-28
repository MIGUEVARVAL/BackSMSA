from rest_framework import routers
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from SMSA.views.token_views import CustomTokenObtainPairView
from SMSA.views.cargas_masivas_views import CargasMasivasViewSet
from SMSA.views.user_views import UserViewSet
from SMSA.views.facultad_views import FacultadViewSet
from SMSA.views.estudiante_views import EstudianteViewSet
from SMSA.views.plan_estudio_views import PlanEstudioViewSet
from SMSA.views.asignatura_plan_views import AsignaturaPlanViewSet
from SMSA.views.tipologia_views import TipologiaViewSet

router = routers.DefaultRouter()

router.register('api/cargas-masivas', CargasMasivasViewSet, 'cargas-masivas')

router.register('api/user', UserViewSet, 'user')
router.register('api/facultad', FacultadViewSet, 'facultad')
router.register('api/estudiante', EstudianteViewSet, 'estudiante')
router.register('api/plan-estudio', PlanEstudioViewSet, 'plan-estudio')
router.register('api/asignatura-plan', AsignaturaPlanViewSet, 'asignatura-plan')
router.register('api/tipologia', TipologiaViewSet, 'tipologia')


urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls