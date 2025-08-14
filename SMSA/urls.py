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
from SMSA.views.plan_estudio_acuerdo_views import PlanEstudioAcuerdosViewSet
from SMSA.views.asignatura_plan_views import AsignaturaPlanViewSet, PlanesAsignaturaViewSet
from SMSA.views.tipologia_views import TipologiaViewSet
from SMSA.views.historial_academico_views import HistorialAcademicoViewSet, HistorialAcademicoByPlanEstudioViewSet
from SMSA.views.seguimiento_views import SeguimientoViewSet
from SMSA.views.historico_seguimiento_views import HistoricoSeguimientoViewSet
from SMSA.views.asignatura_views import AsignaturaViewSet

router = routers.DefaultRouter()

router.register('api/cargas-masivas', CargasMasivasViewSet, 'cargas-masivas')

router.register('api/user', UserViewSet, 'user')
router.register('api/facultad', FacultadViewSet, 'facultad')
router.register('api/estudiante', EstudianteViewSet, 'estudiante')
router.register('api/plan-estudio', PlanEstudioViewSet, 'plan-estudio')
router.register('api/plan-estudio-acuerdo', PlanEstudioAcuerdosViewSet, 'plan-estudio-acuerdo')
router.register('api/asignatura', AsignaturaViewSet, 'asignatura')
router.register('api/asignatura-plan', AsignaturaPlanViewSet, 'asignatura-plan')
router.register('api/planes-asignatura', PlanesAsignaturaViewSet, 'planes-asignatura')
router.register('api/tipologia', TipologiaViewSet, 'tipologia')
router.register('api/historial-academico', HistorialAcademicoViewSet, 'historial-academico')
router.register('api/historial-academico-by-plan-estudio', HistorialAcademicoByPlanEstudioViewSet, 'historial-academico-by-plan-estudio')
router.register('api/estrategia', SeguimientoViewSet, 'estrategia')
router.register('api/historico-seguimiento', HistoricoSeguimientoViewSet, 'historico-seguimiento')

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls