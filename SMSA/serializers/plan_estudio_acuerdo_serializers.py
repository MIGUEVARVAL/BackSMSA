from rest_framework import serializers
from SMSA.models import PlanEstudioAcuerdos

class PlanEstudioAcuerdosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanEstudioAcuerdos
        fields = '__all__'