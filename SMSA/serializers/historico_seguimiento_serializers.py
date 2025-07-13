from rest_framework import serializers
from SMSA.models import HistoricoSeguimiento
from SMSA.serializers.user_serializers import UserSerializer

class HistoricoSeguimientoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = HistoricoSeguimiento
        fields = '__all__'
        read_only_fields = ('id', 'fecha') 