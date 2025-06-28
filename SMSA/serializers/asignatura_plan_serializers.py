from rest_framework import serializers
from SMSA.models import AsignaturaPlan
from SMSA.serializers.tipologia_serializers import TipologiaSerializer
from SMSA.serializers.asignatura_serializers import AsignaturaSerializer

class AsignaturaPlanSerializer(serializers.ModelSerializer):
    asignatura = AsignaturaSerializer(read_only=True)
    tipologia = TipologiaSerializer(read_only=True)

    class Meta:
        model = AsignaturaPlan
        fields = '__all__'
        read_only_fields = ('id', 'fecha_modificacion',)
