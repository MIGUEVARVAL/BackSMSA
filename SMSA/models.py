from django.db import models
from django.contrib.auth.models import User,AbstractUser

class User(AbstractUser):
    cargo = models.CharField(max_length=100, blank=True, null=True)
    nivel_permisos = models.IntegerField(default=0, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Cambia el related_name para evitar conflictos
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Cambia el related_name para evitar conflictos
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

class Facultad(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.nombre

class UnidadAcademica(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=15, unique=True)
    facultad = models.ForeignKey(Facultad, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre

class PlanEstudio(models.Model):
    codigo = models.CharField(max_length=45, unique=True)
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=45)
    tipo_nivel = models.CharField(max_length=45, blank=True, null=True)
    activo = models.BooleanField(default=True)
    facultad = models.ForeignKey(Facultad, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre


class Estudiante(models.Model):
    acceso = models.CharField(max_length=45, blank=True, null=True)
    subacceso = models.CharField(max_length=45, blank=True, null=True)
    tipo_documento = models.CharField(max_length=45, blank=True, null=True)
    documento = models.CharField(max_length=15, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    puntaje_admision = models.FloatField(blank=True, null=True)
    pbm = models.IntegerField(blank=True, null=True)
    apertura = models.CharField(max_length=20, blank=True, null=True)
    genero = models.CharField(max_length=100, blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    correo_institucional = models.EmailField(blank=True, null=True)
    correo_alterno = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=45, blank=True, null=True)
    papa = models.FloatField(blank=True, null=True)
    avance_carrera = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    numero_matriculas = models.IntegerField(blank=True, null=True)
    semestres_cancelados = models.IntegerField(default=0, blank=True, null=True)
    reserva_cupo = models.IntegerField(default=0, blank=True, null=True)
    matricula_periodo_activo = models.CharField(max_length=10, default='NO', blank=True, null=True)
    plan_estudio = models.ForeignKey(PlanEstudio, on_delete=models.PROTECT, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    cupo_creditos = models.IntegerField(default=0, blank=True, null=True)
    creditos_pendientes = models.IntegerField(default=0, blank=True, null=True)
    creditos_disponibles = models.IntegerField(default=0, blank=True, null=True)
    


class Tipologia(models.Model):
    codigo = models.CharField(max_length=2)
    nombre = models.CharField(max_length=45)

    def __str__(self):
        return self.nombre


class Asignatura(models.Model):
    codigo = models.CharField(max_length=45, unique=True)
    nombre = models.CharField(max_length=150)
    creditos = models.IntegerField()
    uab = models.ForeignKey(UnidadAcademica, on_delete=models.PROTECT, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.nombre


class AsignaturaPlan(models.Model):
    tipologia = models.ForeignKey(Tipologia, on_delete=models.PROTECT)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    plan_estudio = models.ForeignKey(PlanEstudio, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.asignatura.nombre} - {self.plan_estudio.nombre} ({self.tipologia.nombre})"

    class Meta:
        unique_together = ('tipologia', 'asignatura', 'plan_estudio')


class HistorialAcademico(models.Model):
    semestre = models.CharField(max_length=45)
    estado = models.CharField(max_length=45)
    nota = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    veces_vista = models.IntegerField(default=0, blank=True, null=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    tipo_cancelacion = models.CharField(max_length=45, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} ({self.semestre})"
    
class Seguimiento(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} ({self.fecha})"
    
class HistoricoSeguimiento(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)
    seguimiento = models.ForeignKey(Seguimiento, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} ({self.fecha})"
