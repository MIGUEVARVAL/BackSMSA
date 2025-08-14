from SMSA.serializers.plan_estudio_acuerdo_serializers import PlanEstudioAcuerdosSerializer
from SMSA.models import PlanEstudioAcuerdos
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class PlanEstudioAcuerdosViewSet(viewsets.ModelViewSet):
    queryset = PlanEstudioAcuerdos.objects.all()
    serializer_class = PlanEstudioAcuerdosSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = None  # No pagination for this viewset

    def get_queryset(self):
        queryset = super().get_queryset()
        titulo = self.request.query_params.get('titulo', None)
        plan_estudio = self.request.query_params.get('plan_estudio', None)

        if titulo is not None:
            queryset = queryset.filter(titulo__icontains=titulo)

        if plan_estudio is not None:
            queryset = queryset.filter(plan_estudio=plan_estudio)

        queryset = queryset.order_by('-vigente', '-fecha_creacion')

        return queryset