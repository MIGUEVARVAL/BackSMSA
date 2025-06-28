from rest_framework import serializers
from SMSA.models import Asignatura

class AsignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignatura
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion', 'fecha_modificacion',)
