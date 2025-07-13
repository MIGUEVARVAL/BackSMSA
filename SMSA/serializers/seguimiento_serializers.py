from rest_framework import serializers
from SMSA.models import Seguimiento

class SeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguimiento
        fields = '__all__'
        read_only_fields = ('id','fecha')