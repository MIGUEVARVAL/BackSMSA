import pandas as pd
from SMSA.models import Estudiante, PlanEstudio
from django.db import transaction

class loadEstudiantesActivos:
    def __init__(self, archivo):
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        # Hoja donde se encuentran las relaciones entre materia, plan y tipología
        self.df_estudiantes_activos = self.read_excel(archivo, sheet_name=1)


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
    
    def load_estudiantes_activos(self):
        """
        Carga estudiantes activos desde un archivo Excel.
        
        :param archivo: Archivo Excel con los datos de los estudiantes.
        :return: Número de estudiantes cargados exitosamente.
        """
        df = self.df_estudiantes_activos.copy()

        print(df.columns)
        
        # Validar columnas requeridas
        required_columns = [
            'ACCESO', 'SUBACCESO', 'T_DOCUMENTO', 'DOCUMENTO',
            'NOMBRE_LEGAL', 'PUNTAJE_ADMISION',
            'PBM_CALCULADO', 'APERTURA', 'CONVOCATORIA', 'GENERO',
            'FECHA_NACIMIENTO', 'USUARIO', 'CORREO_PERSONAL',
            'TELEFONO1', 'PAPA', 'AVANCE_CARRERA', 'NUMERO_MATRICULAS',
            'VICTIMAS_DEL_CONFLICTO', 'DISCAPACIDAD', 'COD_PLAN'
            ]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f'La columna {col} es requerida en el archivo.')

        estudiantes_cargados = 0
        

        with transaction.atomic():
            for index, row in df.iterrows():
                acceso = row['ACCESO']
                subacceso = row['SUBACCESO']
                tipo_documento = row['T_DOCUMENTO']
                documento = row['DOCUMENTO']
                nombre = row['NOMBRE_LEGAL']
                puntaje_admision = row['PUNTAJE_ADMISION']
                pbm = row['PBM_CALCULADO']
                apertura = row['APERTURA']
                convocatoria = row['CONVOCATORIA']
                genero = row['GENERO']
                fecha_nacimiento = row['FECHA_NACIMIENTO']
                correo_institucional = row['USUARIO']
                correo_alterno = row['CORREO_PERSONAL']
                telefono = row['TELEFONO1']
                papa = row['PAPA']
                avance_carrera = row['AVANCE_CARRERA']
                numero_matriculas = row['NUMERO_MATRICULAS']
                victima_conflicto = row['VICTIMAS_DEL_CONFLICTO']
                discapacidad = row['DISCAPACIDAD']
                plan_estudio_codigo = row['COD_PLAN']

                # Verificar si el estudiante ya existe
                # Construir los valores por defecto solo si no son nulos
                defaults = {}
                if pd.notna(acceso): defaults['acceso'] = acceso
                if pd.notna(subacceso): defaults['subacceso'] = subacceso
                if pd.notna(tipo_documento): defaults['tipo_documento'] = tipo_documento
                if pd.notna(nombre): defaults['nombre'] = nombre
                if pd.notna(puntaje_admision): defaults['puntaje_admision'] = puntaje_admision
                if pd.notna(pbm): defaults['pbm'] = int(pbm)
                if pd.notna(apertura): defaults['apertura'] = apertura
                if pd.notna(convocatoria): defaults['convocatoria'] = convocatoria
                if pd.notna(genero): defaults['genero'] = genero
                if pd.notna(fecha_nacimiento): defaults['fecha_nacimiento'] = fecha_nacimiento
                if pd.notna(correo_institucional): defaults['correo_institucional'] = correo_institucional
                if pd.notna(correo_alterno): defaults['correo_alterno'] = correo_alterno
                if pd.notna(telefono): defaults['telefono'] = telefono
                if pd.notna(papa): defaults['papa'] = float(papa)
                if pd.notna(avance_carrera): defaults['avance_carrera'] = float(avance_carrera)
                if pd.notna(numero_matriculas): defaults['numero_matriculas'] = int(numero_matriculas)
                if pd.notna(victima_conflicto): defaults['victima_conflicto'] = victima_conflicto
                if pd.notna(discapacidad): defaults['discapacidad'] = discapacidad

                estudiante, created = Estudiante.objects.get_or_create(
                    documento=documento,
                    defaults=defaults
                )

                if created:
                    estudiantes_cargados += 1
                else:
                    # Validar si hubo alguna modificación
                    campos_actualizables = defaults
                    modificado = False
                    for campo, valor in campos_actualizables.items():
                        if getattr(estudiante, campo) != valor:
                            setattr(estudiante, campo, valor)
                            modificado = True
                    if not modificado:
                        continue  # No hubo cambios, pasar al siguiente estudiante

                # Asignar plan de estudio si se proporciona (para nuevos)
                if created and pd.notna(plan_estudio_codigo):
                    try:
                        plan_estudio = PlanEstudio.objects.get(codigo=plan_estudio_codigo)
                        estudiante.plan_estudio = plan_estudio
                    except PlanEstudio.DoesNotExist:
                        raise ValueError(f'El plan de estudio {plan_estudio_codigo} no existe.')

                estudiante.save()
                print('Estudiante cargado:', estudiante.nombre)

        return estudiantes_cargados