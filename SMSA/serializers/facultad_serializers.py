from rest_framework import serializers
from SMSA.models import Facultad
from django.contrib.auth.hashers import make_password

class FacultadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facultad
        fields = '__all__'
        