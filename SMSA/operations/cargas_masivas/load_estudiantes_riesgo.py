import pandas as pd
from SMSA.models import Estudiante, PlanEstudio, Facultad
from django.db import transaction

class loadEstudiantesRiesgo:
    def __init__(self, archivo):
        # Variables para el manejo de errores
        self.errores = []
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        # Hoja donde se encuentran las relaciones entre materia, plan y tipología
        self.df_estudiantes_riesgo, self.fila_dato = self.read_excel(archivo, sheet_name=1)
        self.df_estudiantes_riesgo = self.clean_dataframe(self.df_estudiantes_riesgo)


    @staticmethod
    def read_excel(file_obj, sheet_name=None):
        # Leer el archivo sin encabezado
        df = pd.read_excel(file_obj, sheet_name=sheet_name, header=None)
        fila = 0
        # Buscar la primera fila no vacía para usar como encabezado
        for idx, row in df.iterrows():
            if not row.isnull().all():
                df.columns = row
                df = df.iloc[idx + 1:].reset_index(drop=True)
                fila = idx + 2
                break
        return df, fila

    def clean_dataframe(self, df):
        """
        Limpia el DataFrame, reemplazando valores NaN/None por None (nulo de Python)
        y eliminando espacios en blanco innecesarios en los campos de texto.
        """
        if df is None or df.empty:
            return df

        # Reemplazar todos los valores NaN por None
        df = df.where(
            pd.notnull(df), None
        )

        # Limpiar espacios en blanco en columnas de tipo texto
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )

        return df
    
    def load_estudiantes_riesgo(self):
        
        """
        Carga estudiantes activos desde un archivo Excel.
        
        :param archivo: Archivo Excel con los datos de los estudiantes.
        :return: Número de estudiantes cargados exitosamente.
        """

        try:

            # Validar que el DataFrame se haya cargado correctamente
            if not hasattr(self, 'df_estudiantes_activos') or self.df_estudiantes_activos is None:
                return {
                    'exitoso': False,
                    'errores': self.errores,
                }
            
            def convertir_a_booleano(valor):
                    """Convierte valores de texto a booleano"""
                    if pd.isna(valor) or valor is None:
                        return None
                    if isinstance(valor, str):
                        valor_upper = valor.strip().upper()
                        if valor_upper in ['SI', 'SÍ', 'YES', 'TRUE', '1', 'S', 'Y']:
                            return True
                        elif valor_upper in ['NO', 'FALSE', '0', 'N']:
                            return False
                        else:
                            return None
                    return bool(valor)
            
            # Validar columnas requeridas
            required_columns = [
                "FACULTAD", "CÓDIGO DEL PLAN", "PLAN DE ESTUDIOS", "ACCESO",
                "SUBACCESO", "TIPO DE DOCUMENTO", "DOCUMENTO", "NOMBRE LEGAL ESTUDIANTE", "APELLIDO LEGAL ESTUDIANTE",
                "PUNTAJE DE ADMISIÓN", "PBM", "APERTURA", "GENERO", "CORREO INSTITUCIONAL",
                "CORREO ALTERNATIVO", "TELÉFONO", "PAPA", "AVANCE DE CARRERA",
                "NÚMERO DE MATRÍCULAS", "SEMESTRES CANCELADOS", "RESERVAS DE CUPO", "MATRÍCULA EN EL PERIODO ACTIVO",
                "CUPO CRÉDITOS", "CRÉDITOS PENDIENTES", "CRÉDITOS DISPONIBLES"
            ]

            missing_columns = [col for col in required_columns if col not in self.df_estudiantes_riesgo.columns]
            if missing_columns:
                self.errores.append({
                    'codigo_error': '0001',
                    'tipo_error': 'COLUMNA_FALTANTE',
                    'detalle': f'Faltan las siguientes columnas requeridas: {", ".join(missing_columns)}'
                })
                return {
                    'exitoso': False,
                    'errores': self.errores,
                }
            
            # Filtrar las columnas relevantes
            df = self.df_estudiantes_riesgo[required_columns].copy()
            
            # Validar que haya datos después del filtro
            if df.empty:
                self.errores.append({
                    'codigo_error': '0002',
                    'tipo_error': 'DATOS_FALTANTES',
                    'detalle': 'No se encontraron datos válidos después del filtrado.'
                })
                return {
                    'exitoso': False,
                    'errores': self.errores,
                }

            estudiantes_cargados = 0
            estudiantes_creados = 0
            estudiantes_actualizados = 0

            try:
                with transaction.atomic():
                    for index, row in df.iterrows():

                        try:

                            # Validar datos requeridos
                            if pd.isna(row['T_DOCUMENTO']) or pd.isna(row['DOCUMENTO']) or pd.isna(row['NOMBRES_LEGAL']):
                                self.errores.append({
                                    'codigo_error': '0003',
                                    'tipo_error': 'DATO_REQUERIDO_FALTANTE',
                                    'detalle': f'Faltan datos requeridos en la fila {index + self.fila_dato}: T_DOCUMENTO, DOCUMENTO o NOMBRES_LEGAL. Estudiante no cargado.',
                                })
                                continue

                            plan_estudio_codigo = row["CÓDIGO DEL PLAN"]
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
                            matricula_periodo_activo = convertir_a_booleano(row["MATRÍCULA EN EL PERIODO ACTIVO"])
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
                            if pd.notna(matricula_periodo_activo): defaults['activo'] = matricula_periodo_activo
                            if pd.notna(cupo_creditos): defaults['cupo_creditos'] = int(cupo_creditos)
                            if pd.notna(creditos_pendientes): defaults['creditos_pendientes'] = int(creditos_pendientes)    
                            if pd.notna(creditos_disponibles): defaults['creditos_disponibles'] = int(creditos_disponibles)

                            estudiante, created = Estudiante.objects.get_or_create(
                                documento=documento,
                                defaults=defaults
                            )

                            if created:
                                estudiantes_creados += 1
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
                                estudiantes_actualizados += 1
                            
                            if plan_estudio_codigo:
                                plan_estudio = PlanEstudio.objects.get(codigo=plan_estudio_codigo)
                                if plan_estudio:
                                    estudiante.plan_estudio = plan_estudio
                                else:
                                    self.errores.append({
                                        'codigo_error': '0004',
                                        'tipo_error': 'PLAN_ESTUDIO_NO_ENCONTRADO',
                                        'detalle': f'El plan de estudio {plan_estudio_codigo} para el estudiante con documento {documento} ubicado en la fila {index + self.fila_dato} no existe.'
                                    })
                            else:
                                self.errores.append({
                                    'codigo_error': '0004',
                                    'tipo_error': 'PLAN_ESTUDIO_FALTANTE',
                                    'detalle': f'El estudiante con documento {documento} ubicado en la fila {index + self.fila_dato} no tiene un plan de estudio asignado.'
                                })
                            estudiante.save()
                            estudiantes_cargados += 1
                        except Exception as e:
                            self.errores.append({
                                'codigo_error': '0005',
                                'tipo_error': 'ERROR_ESTUDIANTES_ESTUDIO_DESERCION',
                                'detalle': f'Error al cargar el estudiante ubicado en la fila {index + self.fila_dato}: {str(e)}',
                            })
                            return {
                                'exitoso': False,
                                'errores': self.errores,
                            }
                return {
                'exitoso': True,
                'mensajeExito': f'Estudiantes cargados exitosamente: {estudiantes_cargados} de {len(df)}, Creados: {estudiantes_creados}, Actualizados: {estudiantes_actualizados}',
                'errores': self.errores
                }
            except Exception as e:
                self.errores.append({
                    'codigo_error': '0006',
                    'tipo_error': 'ERROR_TRANSACCION',
                    'detalle': f'Error al procesar la transacción: {str(e)}',
                })
                return {
                    'exitoso': False,
                    'errores': self.errores,
                }
        except Exception as e:
            self.errores.append({
                'codigo_error': '0007',
                'tipo_error': 'ERROR_INESPERADO',
                'detalle': f'Error inesperado al cargar los estudiantes: {str(e)}',
            })
            return {
                'exitoso': False,
                'errores': self.errores,
            }

    

