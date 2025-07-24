from rest_framework import serializers
from SMSA.models import UnidadAcademica

class UnidadAcademicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadAcademica
        fields = '__all__'
        read_only_fields = ('id',)