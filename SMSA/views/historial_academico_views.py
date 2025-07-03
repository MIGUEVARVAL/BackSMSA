from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from SMSA.models import HistorialAcademico, AsignaturaPlan
from SMSA.serializers.historial_academico_serializers import HistorialAcademicoSerializer, HistorialAcademicoByPlanEstudioSerializer, HistorialAcademicoGroupSerializer
from SMSA.serializers.tipologia_serializers import TipologiaSerializer

class HistorialAcademicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar el Historial Académico de los estudiantes.
    Permite listar, crear, actualizar y eliminar registros de historial académico.
    """
    queryset = HistorialAcademico.objects.all()
    serializer_class = HistorialAcademicoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()

        id = self.request.query_params.get('id', None)
        estudiante_id = self.request.query_params.get('estudiante_id', None)

        if id is not None:
            queryset = queryset.filter(id=id)
        if estudiante_id is not None:
            queryset = queryset.filter(estudiante_id=estudiante_id)

        queryset = queryset.order_by('fecha_creacion')

        return queryset
    
from rest_framework.response import Response

class HistorialAcademicoByPlanEstudioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HistorialAcademicoByPlanEstudioSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        plan_estudio_id = request.query_params.get('plan_estudio_id')
        estudiante_id = request.query_params.get('estudiante_id')
        if not plan_estudio_id or not estudiante_id:
            return Response([])

        # Buscar asignaturas del plan
        from SMSA.models import AsignaturaPlan, Tipologia
        asignatura_plans = AsignaturaPlan.objects.filter(plan_estudio_id=plan_estudio_id)
        tipologia_dict = {}
        for ap in asignatura_plans:
            tipologia_dict.setdefault(ap.tipologia_id, {
                'tipologia': ap.tipologia,
                'asignatura_ids': []
            })
            tipologia_dict[ap.tipologia_id]['asignatura_ids'].append(ap.asignatura_id)

        # Agrupar historiales por tipología
        result = []
        for tipologia_id, data in tipologia_dict.items():
            historiales = HistorialAcademico.objects.filter(
                estudiante_id=estudiante_id,
                asignatura_id__in=data['asignatura_ids']
            )
            if historiales.exists():
                result.append({
                    'tipologia': TipologiaSerializer(data['tipologia']).data,
                    'historialAcademico': HistorialAcademicoByPlanEstudioSerializer(
                        historiales, many=True, context={'plan_estudio': plan_estudio_id}
                    ).data
                })

        return Response(result)