import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackSMSA.settings')
django.setup()

from django.contrib.auth import get_user_model
from SMSA.models import Tipologia, HistorialAcademico, Asignatura, AsignaturaPlan

HistorialAcademico.objects.all().delete()
AsignaturaPlan.objects.all().delete()
Asignatura.objects.all().delete()
Tipologia.objects.all().delete()

