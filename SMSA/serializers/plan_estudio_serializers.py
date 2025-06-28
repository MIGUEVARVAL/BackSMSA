from rest_framework import serializers
from SMSA.models import PlanEstudio
from SMSA.serializers.facultad_serializers import FacultadSerializer

class PlanEstudioSerializer(serializers.ModelSerializer):
    facultad = FacultadSerializer(read_only=True)

    class Meta:
        model = PlanEstudio
        fields = '__all__'
        read_only_fields = ('id', 'codigo',)
