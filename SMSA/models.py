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
    
class Sede(models.Model):
    codigo = models.CharField(max_length=15, unique=True) # Código único de la sede
    nombre = models.CharField(max_length=100) # Nombre de la sede

    def __str__(self):
        return self.nombre

class Facultad(models.Model):
    codigo = models.CharField(max_length=15, unique=True) # Código único de la facultad
    nombre = models.CharField(max_length=100) # Nombre de la facultad
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT, blank=True, null=True) # Relación con la sede a la que pertenece

    def __str__(self):
        return self.nombre

class UnidadAcademica(models.Model):
    codigo = models.CharField(max_length=15, unique=True) # Código único de la unidad académica
    nombre = models.CharField(max_length=100) # Nombre de la unidad académica
    facultad = models.ForeignKey(Facultad, on_delete=models.PROTECT) # Relación con la facultad a la que pertenece

    def __str__(self):
        return self.nombre

class PlanEstudio(models.Model):
    codigo = models.CharField(max_length=45, unique=True) # Código único del plan de estudio
    nombre = models.CharField(max_length=100) # Nombre del plan de estudio
    nivel = models.CharField(max_length=45) # Nivel del plan de estudio (pregrado, posgrado, etc.) )
    tipo_nivel = models.CharField(max_length=45, blank=True, null=True) # Tipo de nivel (pregrado, maestría, doctorado, etc.)
    activo = models.BooleanField(default=True) # Indica si el plan de estudio está activo
    facultad = models.ForeignKey(Facultad, on_delete=models.PROTECT) # Relación con la facultad a la que pertenece
    descripcion = models.TextField(blank=True, null=True) # Descripción del plan de estudio
    snies = models.CharField(max_length=45, blank=True, null=True) # Código SNIES del plan de estudio
    plan_reformado = models.BooleanField(default=False, blank=True, null=True) # Indica si el plan de estudio ha sido reformado
    puntos = models.IntegerField(default=0, blank=True, null=True) # Puntos del plan de estudio (Solo para posgrado)
    inicio_extincion = models.CharField(max_length=15, blank=True, null=True) # Fecha de inicio de la extinción del plan de estudio en caso de que aplique
    extincion_definitiva = models.CharField(max_length=15, blank=True, null=True) # Fecha de extinción definitiva del plan de estudio en caso de que aplique

    def __str__(self):
        return self.nombre
    
class PlanEstudioAcuerdos(models.Model):
    titulo = models.CharField(max_length=200) # Título del acuerdo
    link = models.URLField(max_length=1000, blank=True, null=True) # Enlace al documento del acuerdo
    vigente = models.BooleanField(default=True) # Indica si el acuerdo está vigente
    plan_estudio = models.ForeignKey(PlanEstudio, on_delete=models.CASCADE) # Relación con el plan de estudio
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True) # Fecha de creación del acuerdo

    def __str__(self):
        return f"{self.plan_estudio.nombre} - {self.titulo}"

class Estudiante(models.Model):
    acceso = models.CharField(max_length=45, blank=True, null=True) 
    subacceso = models.CharField(max_length=45, blank=True, null=True)
    tipo_documento = models.CharField(max_length=45, blank=True, null=True)
    documento = models.CharField(max_length=15, unique=True)
    nombres = models.CharField(max_length=100, blank=True, null=True)
    apellidos = models.CharField(max_length=100, blank=True, null=True)
    puntaje_admision = models.FloatField(blank=True, null=True)
    pbm = models.IntegerField(blank=True, null=True)
    apertura = models.CharField(max_length=20, blank=True, null=True)
    convocatoria = models.CharField(max_length=20, blank=True, null=True)
    genero = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    correo_institucional = models.EmailField(blank=True, null=True)
    correo_alterno = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=45, blank=True, null=True)
    papa = models.FloatField(blank=True, null=True)
    avance_carrera = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    numero_matriculas = models.IntegerField(blank=True, null=True)
    semestres_cancelados = models.IntegerField(default=0, blank=True, null=True)
    reserva_cupo = models.IntegerField(default=0, blank=True, null=True)
    victima_conflicto = models.BooleanField(default=False, blank=True, null=True)
    discapacidad = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True, blank=True, null=True)
    plan_estudio = models.ForeignKey(PlanEstudio, on_delete=models.PROTECT, blank=True, null=True)
    cupo_creditos = models.IntegerField(default=0, blank=True, null=True)
    creditos_pendientes = models.IntegerField(default=0, blank=True, null=True)
    creditos_disponibles = models.IntegerField(default=0, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, blank=True, null=True)

class Tipologia(models.Model):
    codigo = models.CharField(max_length=2)
    nombre = models.CharField(max_length=45)

    def __str__(self):
        return self.nombre


class Asignatura(models.Model):
    codigo = models.CharField(max_length=45, unique=True)
    nombre = models.CharField(max_length=150)
    creditos = models.IntegerField()
    numero_semanas = models.IntegerField(default=1, blank=True, null=True)
    nivel = models.CharField(max_length=100, blank=True, null=True)
    horas_teoricas = models.IntegerField(default=0, blank=True, null=True)
    horas_practicas = models.IntegerField(default=0, blank=True, null=True)
    asistencia_minima = models.IntegerField(default=0, blank=True, null=True)
    validable = models.BooleanField(default=True, blank=True, null=True)    
    descripcion = models.TextField(blank=True, null=True) 
    objetivos = models.TextField(blank=True, null=True)
    contenido = models.TextField(blank=True, null=True)
    referencias = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=100, blank=True, null=True)
    fecha_aprobacion = models.DateField(blank=True, null=True)
    acta_aprobacion = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, blank=True, null=True)
    activo = models.BooleanField(default=True)
    uab = models.ForeignKey(UnidadAcademica, on_delete=models.PROTECT, blank=True, null=True) # Relación con la unidad académica a la que pertenece
    def __str__(self):
        return self.nombre


class AsignaturaPlan(models.Model):
    tipologia = models.ForeignKey(Tipologia, on_delete=models.PROTECT)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    plan_estudio = models.ForeignKey(PlanEstudio, on_delete=models.SET_NULL, blank=True, null=True)
    parametrizacion = models.BooleanField(default=True, blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.asignatura.nombre} - {self.plan_estudio.nombre} ({self.tipologia.nombre})"

    class Meta:
        unique_together = ('tipologia', 'asignatura', 'plan_estudio')


class HistorialAcademico(models.Model):
    estado = models.CharField(max_length=45)
    nota = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    veces_vista = models.IntegerField(default=0, blank=True, null=True)
    tipo_cancelacion = models.CharField(max_length=45, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, blank=True, null=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=10, blank=True, null=True) # Periodo académico del historial

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} ({self.periodo})"

class Seguimiento(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.estudiante} - ({self.fecha})"
    
class HistoricoSeguimiento(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)
    seguimiento = models.ForeignKey(Seguimiento, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titulo} - ({self.fecha})"
