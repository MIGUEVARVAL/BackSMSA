# Generated by Django 5.2.3 on 2025-06-29 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SMSA', '0006_alter_estudiante_matricula_periodo_activo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estudiante',
            name='nombre',
        ),
        migrations.AddField(
            model_name='estudiante',
            name='apellidos',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='estudiante',
            name='nombres',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
