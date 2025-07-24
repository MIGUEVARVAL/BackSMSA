from rest_framework import serializers
from SMSA.models import AsignaturaPlan
from SMSA.serializers.tipologia_serializers import TipologiaSerializer
from SMSA.serializers.asignatura_serializers import AsignaturaSerializer
from SMSA.serializers.plan_estudio_serializers import PlanEstudioSerializer

class AsignaturaPlanSerializer(serializers.ModelSerializer):
    asignatura = AsignaturaSerializer(read_only=True)
    tipologia = TipologiaSerializer(read_only=True)

    class Meta:
        model = AsignaturaPlan
        fields = '__all__'
        read_only_fields = ('id', 'fecha_modificacion',)

class PlanesAsignaturaSerializer(serializers.ModelSerializer):
    plan_estudio = PlanEstudioSerializer(read_only=True)

    class Meta:
        model = AsignaturaPlan
        fields = '__all__'
        read_only_fields = ('id', 'fecha_modificacion',)
        