from rest_framework import serializers
from SMSA.models import Facultad

class FacultadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facultad
        fields = '__all__'
        