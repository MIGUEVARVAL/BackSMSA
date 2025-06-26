from rest_framework import serializers
from SMSA.models import Estudiante

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion', )