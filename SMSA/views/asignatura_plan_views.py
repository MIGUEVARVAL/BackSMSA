from SMSA.serializers.asignatura_plan_serializers import AsignaturaPlanSerializer
from SMSA.models import AsignaturaPlan
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class AsignaturaPlanViewSet(viewsets.ModelViewSet):
    queryset = AsignaturaPlan.objects.all()
    serializer_class = AsignaturaPlanSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = None  

    def get_queryset(self):
        queryset = super().get_queryset()

        asignatura_id = self.request.query_params.get('asignatura_id', None)
        plan_estudio_id = self.request.query_params.get('plan_estudio_id', None)
        tipologia_id = self.request.query_params.get('tipologia_id', None)

        if asignatura_id is not None:
            queryset = queryset.filter(asignatura__id=asignatura_id)
        if plan_estudio_id is not None:
            queryset = queryset.filter(plan_estudio__id=plan_estudio_id)
        if tipologia_id is not None:
            queryset = queryset.filter(tipologia__id=tipologia_id)
             

        return queryset