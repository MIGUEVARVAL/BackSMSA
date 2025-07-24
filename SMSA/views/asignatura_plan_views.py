from SMSA.serializers.asignatura_plan_serializers import AsignaturaPlanSerializer, PlanesAsignaturaSerializer
from SMSA.models import AsignaturaPlan
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from SMSA.serializers.tipologia_serializers import TipologiaSerializer
from rest_framework.response import Response

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

class PlanesAsignaturaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AsignaturaPlan.objects.all()
    serializer_class = PlanesAsignaturaSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = None  

    def list(self, request, *args, **kwargs):

        asignatura_id = request.query_params.get('asignatura_id', None)

        if asignatura_id is None:
            return Response({"detail": "Debe proporcionar el parámetro 'asignatura_id'."}, status=400)

        queryset = self.get_queryset().filter(asignatura__id=asignatura_id)
        tipologias = queryset.values_list('tipologia', flat=True).distinct()

        result = []
        for tipologia_id in tipologias:
            planes = queryset.filter(tipologia__id=tipologia_id)
            tipologia_data = TipologiaSerializer(planes.first().tipologia).data if planes.exists() else None
            planes_data = self.get_serializer(planes, many=True).data
            result.append({
                "tipologia": tipologia_data,
                "planes": planes_data
            })

        return Response(result)

