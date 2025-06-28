from rest_framework import serializers
from SMSA.models import Tipologia

class TipologiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipologia
        fields = '__all__'
        read_only_fields = ('id',)
