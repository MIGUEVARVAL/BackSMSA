import pandas as pd
from SMSA.models import Estudiante, PlanEstudio, Facultad
from django.db import transaction

class loadEstudiantesRiesgo:
    def __init__(self, archivo):
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        # Hoja donde se encuentran las relaciones entre materia, plan y tipología
        self.df_estudiantes_riesgo = self.read_excel(archivo, sheet_name=1)


    @staticmethod
    def read_excel(file_obj, sheet_name=None):
        # Leer el archivo sin encabezado
        df = pd.read_excel(file_obj, sheet_name=sheet_name, header=None)
        # Buscar la primera fila no vacía para usar como encabezado
        for idx, row in df.iterrows():
            if not row.isnull().all():
                df.columns = row
                df = df.iloc[idx + 1:].reset_index(drop=True)
                break
        return df
    
    def load_estudiantes_riesgo(self):
        
        """
        Carga estudiantes activos desde un archivo Excel.
        
        :param archivo: Archivo Excel con los datos de los estudiantes.
        :return: Número de estudiantes cargados exitosamente.
        """
        df = self.df_estudiantes_riesgo.copy()
        
        # Validar columnas requeridas
        required_columns = [
            "FACULTAD", "CÓDIGO DEL PLAN", "PLAN DE ESTUDIOS", "ACCESO",
            "SUBACCESO", "TIPO DE DOCUMENTO", "DOCUMENTO", "NOMBRE LEGAL ESTUDIANTE", "APELLIDO LEGAL ESTUDIANTE",
            "PUNTAJE DE ADMISIÓN", "PBM", "APERTURA", "GENERO", "CORREO INSTITUCIONAL",
            "CORREO ALTERNATIVO", "TELÉFONO", "PAPA", "AVANCE DE CARRERA",
            "NÚMERO DE MATRÍCULAS", "SEMESTRES CANCELADOS", "RESERVAS DE CUPO", "MATRÍCULA EN EL PERIODO ACTIVO",
            "CUPO CRÉDITOS", "CRÉDITOS PENDIENTES", "CRÉDITOS DISPONIBLES"
        ]
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f'La columna {col} es requerida en el archivo.')

        estudiantes_cargados = 0
        

        with transaction.atomic():
            for index, row in df.iterrows():
                nombre_facultad = row["FACULTAD"]
                plan_estudio_codigo = row["CÓDIGO DEL PLAN"]
                plan_estudio_nombre = row["PLAN DE ESTUDIOS"]
                acceso = row["ACCESO"]
                subacceso = row["SUBACCESO"]
                tipo_documento = row["TIPO DE DOCUMENTO"]
                documento = row["DOCUMENTO"]
                nombres = row["NOMBRE LEGAL ESTUDIANTE"]
                apellidos = row["APELLIDO LEGAL ESTUDIANTE"]
                puntaje_admision = row["PUNTAJE DE ADMISIÓN"]
                pbm = row["PBM"]
                apertura = row["APERTURA"]
                genero = row["GENERO"]
                correo_institucional = row["CORREO INSTITUCIONAL"]
                correo_alterno = row["CORREO ALTERNATIVO"]
                telefono = row["TELÉFONO"]
                papa = row["PAPA"]
                avance_carrera = row["AVANCE DE CARRERA"]
                numero_matriculas = row["NÚMERO DE MATRÍCULAS"]
                semestres_cancelados = row["SEMESTRES CANCELADOS"]
                reservas_cupo = row["RESERVAS DE CUPO"]
                matricula_periodo_activo = row["MATRÍCULA EN EL PERIODO ACTIVO"]
                cupo_creditos = row["CUPO CRÉDITOS"]
                creditos_pendientes = row["CRÉDITOS PENDIENTES"]
                creditos_disponibles = row["CRÉDITOS DISPONIBLES"]

                # Construir defaults con todos los campos
                defaults = {}
                if pd.notna(acceso): defaults['acceso'] = acceso
                if pd.notna(subacceso): defaults['subacceso'] = subacceso
                if pd.notna(tipo_documento): defaults['tipo_documento'] = tipo_documento
                if pd.notna(nombres): defaults['nombres'] = str(nombres).upper()
                if pd.notna(apellidos): defaults['apellidos'] = str(apellidos).upper()
                if pd.notna(puntaje_admision): defaults['puntaje_admision'] = float(puntaje_admision)
                if pd.notna(pbm): defaults['pbm'] = int(pbm)
                if pd.notna(apertura): defaults['apertura'] = apertura
                if pd.notna(genero): defaults['genero'] = genero
                if pd.notna(correo_institucional): defaults['correo_institucional'] = correo_institucional
                if pd.notna(correo_alterno): defaults['correo_alterno'] = correo_alterno
                if pd.notna(telefono): defaults['telefono'] = telefono
                if pd.notna(papa): defaults['papa'] = float(papa)
                if pd.notna(avance_carrera): defaults['avance_carrera'] = avance_carrera
                if pd.notna(numero_matriculas): defaults['numero_matriculas'] = int(numero_matriculas)
                if pd.notna(semestres_cancelados): defaults['semestres_cancelados'] = int(semestres_cancelados)
                if pd.notna(reservas_cupo): defaults['reserva_cupo'] = int(reservas_cupo)
                if pd.notna(matricula_periodo_activo): defaults['matricula_periodo_activo'] = matricula_periodo_activo
                if pd.notna(cupo_creditos): defaults['cupo_creditos'] = int(cupo_creditos)
                if pd.notna(creditos_pendientes): defaults['creditos_pendientes'] = int(creditos_pendientes)    
                if pd.notna(creditos_disponibles): defaults['creditos_disponibles'] = int(creditos_disponibles)

                # Verificar si el estudiante ya existe
                estudiante = Estudiante.objects.filter(documento=documento).first()
                if estudiante is None:
                    # Crear: usar todos los campos
                    estudiante, created = Estudiante.objects.update_or_create(
                        documento=documento,
                        defaults=defaults
                    )
                    if created:
                        estudiantes_cargados += 1
                else:
                    # Solo actualizar los campos permitidos
                    for campo, valor in defaults.items():
                        if getattr(estudiante, campo) != valor:
                            setattr(estudiante, campo, valor)
                    estudiante.save()

                # Asignar plan de estudio si se proporciona
                if estudiante and pd.notna(plan_estudio_codigo):
                    try:
                        facultad = Facultad.objects.filter(nombre=nombre_facultad).first()
                        if not facultad:
                            print(f"Facultad '{nombre_facultad}' no encontrada para el estudiante {documento}.")
                            continue
                        plan_estudio, _ = PlanEstudio.objects.get_or_create(
                            codigo=plan_estudio_codigo,
                            defaults={
                                'nombre': plan_estudio_nombre,
                                'facultad': facultad
                            }
                        )
                        estudiante.plan_estudio = plan_estudio
                        estudiante.save()
                    except Exception as e:
                        print(f"Error asignando plan de estudio al estudiante {documento}: {e}")
                        continue

                print('Estudiante cargado:', estudiante.nombres, estudiante.apellidos)
                
        return estudiantes_cargados

    

