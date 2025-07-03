from rest_framework import serializers
from SMSA.models import HistorialAcademico
from SMSA.serializers.asignatura_serializers import AsignaturaSerializer
from SMSA.serializers.tipologia_serializers import TipologiaSerializer

class HistorialAcademicoSerializer(serializers.ModelSerializer):
    asignatura = AsignaturaSerializer(read_only=True)

    class Meta:
        model = HistorialAcademico
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion', 'fecha_modificacion')

class HistorialAcademicoByPlanEstudioSerializer(serializers.ModelSerializer):
    asignatura = AsignaturaSerializer(read_only=True)
    tipologia = serializers.SerializerMethodField()

    class Meta:
        model = HistorialAcademico
        fields = '__all__'  # O especifica los campos que necesitas + 'tipologia'

    def get_tipologia(self, obj):
        # El plan_estudio debe venir en el contexto
        plan_estudio = self.context.get('plan_estudio')
        if not plan_estudio:
            return None
        from SMSA.models import AsignaturaPlan
        asignatura_plan = AsignaturaPlan.objects.filter(
            asignatura=obj.asignatura,
            plan_estudio=plan_estudio
        ).first()
        if asignatura_plan and asignatura_plan.tipologia:
            return TipologiaSerializer(asignatura_plan.tipologia).data
        return None
    
class HistorialAcademicoGroupSerializer(serializers.Serializer):
    tipologia = TipologiaSerializer()
    historialAcademico = HistorialAcademicoByPlanEstudioSerializer(many=True)