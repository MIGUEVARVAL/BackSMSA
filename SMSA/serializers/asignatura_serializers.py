from rest_framework import serializers
from SMSA.models import Asignatura
from SMSA.serializers.unidad_academica_serializers import UnidadAcademicaSerializer

class AsignaturaSerializer(serializers.ModelSerializer):
    uab = UnidadAcademicaSerializer()

    class Meta:
        model = Asignatura
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion', 'fecha_modificacion',)
