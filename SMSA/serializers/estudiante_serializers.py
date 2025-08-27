from rest_framework import serializers
from SMSA.serializers.plan_estudio_serializers import PlanEstudioSerializer
from SMSA.models import Estudiante
from datetime import date

class EstudianteSerializer(serializers.ModelSerializer):
    plan_estudio = PlanEstudioSerializer(read_only=True)
    edad = serializers.SerializerMethodField()

    class Meta:
        model = Estudiante
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion', )

    def get_edad(self, obj):
        if obj.fecha_nacimiento:
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
        return None