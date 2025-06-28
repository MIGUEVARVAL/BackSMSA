from rest_framework import serializers
from SMSA.models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        #Campos de solo lectura
        read_only_fields = ('id', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        # Check if password field is present in validated_data
        if 'password' in validated_data:
            print('Password field is present in validated_data')
            # Encrypt the new password
            validated_data['password'] = make_password(validated_data['password'])
        
        # Actualizar los campos del modelo con validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Guardar el modelo actualizado en la base de datos
        instance.save()
        
        return instance