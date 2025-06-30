from rest_framework import serializers
from SMSA.serializers.plan_estudio_serializers import PlanEstudioSerializer
from SMSA.models import Estudiante

class EstudianteSerializer(serializers.ModelSerializer):
    plan_estudio = PlanEstudioSerializer(read_only=True)
    
    class Meta:
        model = Estudiante
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion', )