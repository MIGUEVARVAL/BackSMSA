import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackSMSA.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='mivargasv')  # O usa .get(id=...) si prefieres

# Modifica los campos que necesites
user.nivel_permisos = 1  # Ejemplo de campo personalizado

user.save()  # Guarda los cambios en la base de datos