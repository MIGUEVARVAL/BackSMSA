import pandas as pd
from SMSA.models import Tipologia, Asignatura, PlanEstudio, UnidadAcademica, Facultad, AsignaturaPlan
from django.db import transaction

class loadAsignaturas:

    def __init__(self, archivo):
        # Variables para el manejo de errores
        self.errores = []
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        # Hoja donde se encuentran las relaciones entre materia, plan y tipología
        self.df_asignaturas_plan = self.read_excel(archivo, sheet_name=2)
        self.df_asignaturas_plan = self.clean_dataframe(self.df_asignaturas_plan)
        # Hoja donde se encuentran las asignaturas
        self.df_asignaturas = self.read_excel(archivo, sheet_name=1)
        self.df_asignaturas = self.clean_dataframe(self.df_asignaturas)

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

    def clean_dataframe(self, df):
        """
        Limpia el DataFrame de planes de estudio, reemplazando valores NaN/None por None (nulo de Python)
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
    
    def load_asignaturas(self):

        try:
            # Validar que el DataFrame se haya cargado correctamente
            if not all([
                hasattr(self, 'df_asignaturas_plan') and self.df_asignaturas_plan is not None and not self.df_asignaturas_plan.empty,
                hasattr(self, 'df_asignaturas') and self.df_asignaturas is not None and not self.df_asignaturas.empty
            ]):
                self.errores.append({
                    'codigo_error': '0001',
                    'tipo_error': 'ERROR_CARGA_DATOS',
                    'detalle': 'No se pudieron cargar los DataFrames de asignaturas. Verifique que el archivo tenga las hojas correctas con datos válidos.'
                })
                return {
                    'exitoso': False,
                    'errores': self.errores
                }
            
            # Validar columnas requeridas
            required_columns_plan = ['COD_ASIGNATURA', 'COD_PLAN', 'COD_TIPOLOGIA', 'TIPOLOGIA', 'PERIDO DE OFERTA']
            required_columns_asignatura = ['COD_FACULTAD', 'FACULTAD', 'COD_UAB', 'UAB', 'COD_ASIGNATURA', 'ASIGNATURA', 'CREDITOS', 'PERIODO', 'NUM_SEMANAS', 'HORAS_TEORICAS', 'HORAS_PRACTICAS', 'MININANSISTENCIA', 'ASIG_VALIDABLE']
            missing_columns_plan = [col for col in required_columns_plan if col not in self.df_asignaturas_plan.columns]
            missing_columns_asignatura = [col for col in required_columns_asignatura if col not in self.df_asignaturas.columns]

            if missing_columns_plan:
                self.errores.append({
                    'codigo_error': '0002',
                    'tipo_error': 'COLUMNA_FALTANTE',
                    'detalle': f'Faltan las siguientes columnas en la hoja de asignaturas donde se encuentra el plan y la tipología: {", ".join(missing_columns_plan)}'
                })

            if missing_columns_asignatura:
                self.errores.append({
                    'codigo_error': '0002',
                    'tipo_error': 'COLUMNA_FALTANTE',
                    'detalle': f'Faltan las siguientes columnas en la hoja donde se encuentra la información de las asignaturas: {", ".join(missing_columns_asignatura)}'
                })

            # Filtrar las columnas relevantes
            df_asignaturas_plan = self.df_asignaturas_plan[required_columns_plan].copy()
            df_asignaturas = self.df_asignaturas[required_columns_asignatura].copy()

            # Validar que haya datos después del filtro
            if df_asignaturas_plan.empty or df_asignaturas.empty:
                self.errores.append({
                    'codigo_error': '0003',
                    'tipo_error': 'DATOS_VACIOS',
                    'detalle': 'No se encontraron datos válidos en las hojas de asignaturas.'
                })
                return {
                    'exitoso': False,
                    'errores': self.errores
                }

            # Normalizar el valor de la columna TIPOLOGIA
            df_asignaturas_plan.loc[df_asignaturas_plan['TIPOLOGIA'] == 'FUND. OPTATIVA', 'TIPOLOGIA'] = 'FUNDAMENTACIÓN OPTATIVA'
            df_asignaturas_plan.loc[df_asignaturas_plan['TIPOLOGIA'] == 'FUND. OBLIGATORIA', 'TIPOLOGIA'] = 'FUNDAMENTACIÓN OBLIGATORIA'
            # Crear una lista para las tipologías únicas
            tipologias_unicas = df_asignaturas_plan[['COD_TIPOLOGIA', 'TIPOLOGIA']].drop_duplicates().to_dict(orient='records')
            # Crear o actualizar las tipologías en la base de datos
            resultado_tipologias = self.create_tipologias(tipologias_unicas)
            if not resultado_tipologias['exitoso']:
                return resultado_tipologias
            tipologias_objs = resultado_tipologias['objetos']

            # Crear una lista para las facultades únicas
            facultades_unicas = df_asignaturas[['COD_FACULTAD', 'FACULTAD']].drop_duplicates().to_dict(orient='records')
            # Crear o actualizar las facultades en la base de datos
            resultado_facultades = self.create_update_facultades(facultades_unicas)
            if not resultado_facultades['exitoso']:
                return resultado_facultades
            facultades_dict = {f.codigo: f for f in resultado_facultades['objetos']}

            # Crear una lista para las UAB
            uab_unicas = df_asignaturas[['COD_FACULTAD', 'COD_UAB', 'UAB']].drop_duplicates().to_dict(orient='records')
            # Crear o actualizar las UAB en la base de datos
            resultado_uab = self.create_update_uab(uab_unicas, facultades_dict)
            if not resultado_uab['exitoso']:
                return resultado_uab
            uab_dict = {u.codigo: u for u in resultado_uab['objetos']}

            # Crear un diccionario para los planes de estudio
            resultado_planes = self.get_planes_estudio()
            if not resultado_planes['exitoso']:
                return resultado_planes
            planes_dict = {p.codigo: p for p in resultado_planes['objetos']}

            # Para asignaturas
            df_asignaturas_clean = df_asignaturas.dropna(subset=['COD_ASIGNATURA']).copy()
            df_asignaturas_clean = df_asignaturas_clean[df_asignaturas_clean['COD_ASIGNATURA'].notna()]
            
            # Para asignaturas_plan
            df_asignaturas_plan_clean = df_asignaturas_plan.dropna(subset=['COD_ASIGNATURA', 'COD_PLAN']).copy()
            df_asignaturas_plan_clean = df_asignaturas_plan_clean[
                (df_asignaturas_plan_clean['COD_ASIGNATURA'].notna()) & 
                (df_asignaturas_plan_clean['COD_PLAN'].notna())
            ]

            # Validar que haya datos después del filtro
            if df_asignaturas_clean.empty or df_asignaturas_plan_clean.empty:
                self.errores.append({
                    'codigo_error': '0003',
                    'tipo_error': 'DATOS_VACIOS',
                    'detalle': 'No se encontraron datos válidos en las hojas de asignaturas después de filtrar filas vacías.'
                })
                return {
                    'exitoso': False,
                    'errores': self.errores
                }

            # Crear una lista para las asignaturas
            asignaturas_unicas = df_asignaturas_clean.drop_duplicates().to_dict(orient='records')
            df_asignaturas_plan_unicas = df_asignaturas_plan_clean.drop_duplicates(
                subset=['COD_ASIGNATURA', 'COD_PLAN', 'COD_TIPOLOGIA', 'TIPOLOGIA']
            ).copy()
            
            # Crear o actualizar las asignaturas en la base de datos
            resultado_asignaturas = self.create_update_asignaturas_plan(asignaturas_unicas, uab_dict, tipologias_objs, planes_dict, df_asignaturas_plan_unicas)
            return resultado_asignaturas

        except Exception as e:
            self.errores.append({
                'codigo_error': '0002',
                'tipo_error': 'ERROR_PROCESAMIENTO',
                'detalle': f'Error al procesar las asignaturas: {str(e)}'
            })
            return {
                'exitoso': False,
                'errores': self.errores
            }

    # Función para crear o actualizar las tipologías
    def create_tipologias(self, tipologias):
        tipologias_objs = []

        try:
            with transaction.atomic():
                for tipologia in tipologias:
                    # Validar datos requeridos
                    if not tipologia.get('COD_TIPOLOGIA') or not tipologia.get('TIPOLOGIA'):
                        self.errores.append({
                            'codigo_error': '0004',
                            'tipo_error': 'DATOS_INCOMPLETOS_TIPOLOGIAS',
                            'detalle': F'Código o nombre faltante para la tipología con código {tipologia.get("COD_TIPOLOGIA")} o nombre {tipologia.get("TIPOLOGIA")}'
                        })
                        continue

                    obj = Tipologia.objects.filter(
                        codigo=tipologia['COD_TIPOLOGIA'],
                        nombre=tipologia['TIPOLOGIA']
                    ).first()
                    if not obj:
                        obj = Tipologia.objects.create(
                            codigo=tipologia['COD_TIPOLOGIA'],
                            nombre=tipologia['TIPOLOGIA']
                        )
                        print(f'Tipología creada: {obj}')
                    tipologias_objs.append(obj)
            print("Tipologías procesadas:")
            for t in tipologias_objs:
                print(f"- {t.codigo}: {t.nombre}")
            
            return {
                'exitoso': True,
                'objetos': tipologias_objs
            }
            
        except Exception as e:
            self.errores.append({
                'codigo_error': '0004',
                'tipo_error': 'ERROR_TRANSACCION_TIPOLOGIAS',
                'detalle': f'Error en la transacción de tipologías: {str(e)} \n Valide que los campos "COD_TIPOLOGIA" y "TIPOLOGIA" no estén vacíos',
            })
            return {
                'exitoso': False,
                'errores': self.errores
            }

    # Función para crear o actualizar las facultades
    def create_update_facultades(self, facultades):
        facultades_objs = []
        try:
            with transaction.atomic():
                for facultad in facultades:

                    if not facultad.get('COD_FACULTAD') or not facultad.get('FACULTAD'):
                        self.errores.append({
                            'codigo_error': '0004',
                            'tipo_error': 'DATOS_FACULTAD_INCOMPLETOS',
                            'detalle': f'Código o nombre de la facultad es obligatorio, error detectado para la facultad con código {facultad.get("COD_FACULTAD")} y nombre {facultad.get("FACULTAD")}',
                        })
                        continue

                    obj = Facultad.objects.filter(codigo=facultad['COD_FACULTAD']).first()
                    if obj:
                        if obj.nombre != facultad['FACULTAD']:
                            obj.nombre = facultad['FACULTAD']
                            obj.save()
                            print(f'Facultad actualizada: {obj}')
                        else:
                            print(f'Facultad sin cambios: {obj}')
                    else:
                        obj = Facultad.objects.create(
                            codigo=facultad['COD_FACULTAD'],
                            nombre=facultad['FACULTAD']
                        )
                        print(f'Facultad creada: {obj}')
                    facultades_objs.append(obj)
            
            return {
                'exitoso': True,
                'objetos': facultades_objs
            }
        
        except Exception as e:
            error_transaccion = {
                'codigo_error': '0004',
                'tipo_error': 'ERROR_TRANSACCION_FACULTADES',
                'detalle': f'Error en la transacción de facultades: {str(e)}',
            }
            self.errores.append(error_transaccion)
            return {
                'exitoso': False,
                'errores': self.errores
            }
    
    # Función para crear o actualizar las uab
    def create_update_uab(self, df_uab, facultades_dict):
        uab_objs = []

        try:
            with transaction.atomic():
                for uab in df_uab:
                    facultad_obj = facultades_dict.get(uab['COD_FACULTAD'])
                    if not facultad_obj:
                        self.errores.append({
                            'codigo_error': '0004',
                            'tipo_error': 'FACULTAD_NO_ENCONTRADA',
                            'detalle': f'No se encontró la facultad con código {uab["COD_FACULTAD"]} para la UAB con código {uab["COD_UAB"]}. Asegúrese de que la facultad exista antes de crear la UAB.',
                        })
                        continue

                    if not uab.get('COD_UAB') or not uab.get('UAB'):
                        self.errores.append({
                            'codigo_error': '0004',
                            'tipo_error': 'DATOS_UAB_INCOMPLETOS',
                            'detalle': f'Código o nombre de la UAB es obligatorio, error detectado para la UAB con código {uab.get("COD_UAB")} y nombre {uab.get("UAB")}',
                        })
                        continue

                    obj = UnidadAcademica.objects.filter(codigo=uab['COD_UAB']).first()
                    if obj:
                        if obj.nombre != uab['UAB'] or obj.facultad != facultad_obj:
                            obj.nombre = uab['UAB']
                            obj.facultad = facultad_obj
                            obj.save()
                            print(f'UAB actualizada: {obj}')
                        else:
                            print(f'UAB sin cambios: {obj}')
                    else:
                        obj = UnidadAcademica.objects.create(
                            codigo=uab['COD_UAB'],
                            nombre=uab['UAB'],
                            facultad=facultad_obj
                        )
                        print(f'UAB creada: {obj}')
                    uab_objs.append(obj)

            return {
                'exitoso': True,
                'objetos': uab_objs
            }
        
        except Exception as e:
            self.errores.append({
                'codigo_error': '0004',
                'tipo_error': 'ERROR_TRANSACCION_UAB',
                'detalle': f'Error en la transacción de UAB: {str(e)} \n Valide que los campos "COD_FACULTAD", "COD_UAB" y "UAB" no estén vacíos',
            })
            return {
                'exitoso': False,
                'errores': self.errores
            }
    
    # Función para obtener los planes de estudio
    def get_planes_estudio(self):
        try:
            planes = PlanEstudio.objects.all()
            return {
                'exitoso': True,
                'objetos': planes
            }
        except Exception as e:
            self.errores.append({
                'codigo_error': '0005',
                'tipo_error': 'ERROR_OBTENER_PLANES',
                'detalle': f'Error al obtener los planes de estudio: {str(e)}'
            })
            return {
                'exitoso': False,
                'errores': self.errores
            }

    # Función para crear o actualizar las asignaturas
    def create_update_asignaturas_plan(self, asignaturas_unicas, uab_dict, tipologias_objs, planes_dict, df_asignaturas_plan_unicas):
        asignaturas_procesadas = 0

        try:
            with transaction.atomic():
                for asignatura in asignaturas_unicas:
                    uab_obj = uab_dict.get(asignatura['COD_UAB'])
                    if not uab_obj:
                        self.errores.append({
                            'codigo_error': '0005',
                            'tipo_error': 'UAB_NO_ENCONTRADA',
                            'detalle': f'No se encontró la UAB con código {asignatura["COD_UAB"]} para la asignatura con código {asignatura["COD_ASIGNATURA"]}. Asegúrese de que la UAB exista antes de crear la asignatura.',
                        })
                        continue

                    # Normalizar valores antes de procesar
                    for key in ['NUM_SEMANAS', 'HORAS_TEORICAS', 'HORAS_PRACTICAS', 'MININANSISTENCIA']:
                        if pd.isna(asignatura[key]):
                            asignatura[key] = None

                    # Normalizar el valor de ASIG_VALIDABLE
                    asignatura['ASIG_VALIDABLE'] = True if asignatura['ASIG_VALIDABLE'] == 'SI' else False
                    
                    # Validar datos requeridos
                    if not asignatura.get('COD_ASIGNATURA') or not asignatura.get('ASIGNATURA') or asignatura.get('CREDITOS') is None:
                        self.errores.append({
                            'codigo_error': '0005',
                            'tipo_error': 'DATOS_INCOMPLETOS_ASIGNATURAS',
                            'detalle': f'Código, nombre o créditos faltante para la asignatura con código {asignatura.get("COD_ASIGNATURA")} y nombre {asignatura.get("ASIGNATURA")} '
                        })
                        continue

                    obj = Asignatura.objects.filter(codigo=asignatura['COD_ASIGNATURA']).first()
                    if obj:
                        campos_actualizar = self._asignatura_necesita_actualizacion(obj, asignatura, uab_obj)
                        if campos_actualizar:
                            for campo, valor in campos_actualizar.items():
                                setattr(obj, campo, valor)
                            obj.save()
                            print(f'Asignatura actualizada: {obj.codigo}')
                        else:
                            print(f'Asignatura sin cambios: {obj.codigo}')
                    else:
                        campos = {
                            'codigo': asignatura['COD_ASIGNATURA'],
                            'nombre': asignatura['ASIGNATURA'],
                            'creditos': asignatura['CREDITOS'],
                            'uab': uab_obj,
                            'numero_semanas': asignatura['NUM_SEMANAS'],
                            'horas_teoricas': asignatura['HORAS_TEORICAS'],
                            'horas_practicas': asignatura['HORAS_PRACTICAS'],
                            'asistencia_minima': asignatura['MININANSISTENCIA'],
                            'validable': asignatura['ASIG_VALIDABLE'],
                            'periodo': asignatura['PERIODO']
                        }

                        # Mejorar la conversión de NaN a None
                        for k, v in campos.items():
                            if pd.isna(v):
                                campos[k] = None
                            elif k in ['numero_semanas', 'horas_teoricas', 'horas_practicas', 'asistencia_minima'] and v is not None:
                                # Convertir a entero si es un campo numérico
                                try:
                                    campos[k] = int(float(v)) if v != '' else None
                                except (ValueError, TypeError):
                                    campos[k] = None

                        obj = Asignatura.objects.create(**campos)
                        print(f'Asignatura creada: {obj}')
                    asignaturas_procesadas += 1

                    # Procesar relaciones con planes de estudio y tipologías
                    relaciones_encontradas = 0
                    for _, row in df_asignaturas_plan_unicas.iterrows():
                        if row['COD_ASIGNATURA'] == asignatura['COD_ASIGNATURA']:
                            relaciones_encontradas += 1
                            
                            plan_obj = planes_dict.get(row['COD_PLAN'])
                            if not plan_obj:
                                self.errores.append({
                                    'codigo_error': '0005',
                                    'tipo_error': 'PLAN_NO_ENCONTRADO',
                                    'detalle': f'Plan {row["COD_PLAN"]} no encontrado para asignatura {asignatura["COD_ASIGNATURA"]}'
                                })
                                continue

                            tipologia_obj = None
                            for t in tipologias_objs:
                                if t.codigo == row['COD_TIPOLOGIA'] and t.nombre == row['TIPOLOGIA']:
                                    tipologia_obj = t
                                    break
                            
                            if not tipologia_obj:
                                self.errores.append({
                                    'codigo_error': '0005',
                                    'tipo_error': 'TIPOLOGIA_NO_ENCONTRADA',
                                    'detalle': f'Tipología {row["COD_TIPOLOGIA"]}-{row["TIPOLOGIA"]} no encontrada para asignatura {asignatura["COD_ASIGNATURA"]}'
                                })
                                continue

                            # Crear o actualizar AsignaturaPlan
                            asignatura_plan, created = AsignaturaPlan.objects.get_or_create(
                                asignatura=obj,
                                plan_estudio=plan_obj,
                                defaults={'tipologia': tipologia_obj}
                            )
                            
                            if not created and asignatura_plan.tipologia != tipologia_obj:
                                asignatura_plan.tipologia = tipologia_obj
                                asignatura_plan.save()
                                print(f'AsignaturaPlan actualizada: {asignatura_plan}')
                            elif created:
                                print(f'AsignaturaPlan creada: {asignatura_plan}')
                            else:
                                print(f'AsignaturaPlan sin cambios: {asignatura_plan}')

                    if relaciones_encontradas == 0:
                        self.errores.append({
                            'codigo_error': '0005',
                            'tipo_error': 'SIN_RELACIONES_PLAN',
                            'detalle': f'No se encontraron relaciones plan-tipología para la asignatura {asignatura["COD_ASIGNATURA"]}'
                        })

            return {
                'exitoso': True,
                'errores': self.errores,
                'mensajeExito': f'Se procesaron {asignaturas_procesadas} asignaturas correctamente. ({len(asignaturas_unicas)} asignaturas totales)',
            }
        except Exception as e:
            self.errores.append({
                'codigo_error': '0005',
                'tipo_error': 'ERROR_TRANSACCION_ASIGNATURAS',
                'detalle': f'Error al procesar las asignaturas: {e}'
            })
            return {
                'exitoso': False,
                'errores': self.errores
            }

    def _asignatura_necesita_actualizacion(self, obj, datos_nuevos, uab_obj):
        """Verifica si la asignatura necesita actualización"""
        campos_comparar = [
            ('uab', uab_obj),
            ('periodo', datos_nuevos['PERIODO']),
            ('numero_semanas', datos_nuevos['NUM_SEMANAS']),
            ('horas_teoricas', datos_nuevos['HORAS_TEORICAS']),
            ('horas_practicas', datos_nuevos['HORAS_PRACTICAS']),
            ('asistencia_minima', datos_nuevos['MININANSISTENCIA']),
            ('validable', datos_nuevos['ASIG_VALIDABLE'])
        ]
        
        campos_actualizar = {}
        for campo, valor_nuevo in campos_comparar:
            # Validar si el valor es None o NaN
            if valor_nuevo is None or pd.isna(valor_nuevo):
                continue  # No actualizar si el valor nuevo es nulo o NaN
            
            try:
                valor_actual = getattr(obj, campo)
                
                # Comparar valores manejando casos especiales
                if pd.isna(valor_actual) and pd.isna(valor_nuevo):
                    continue  # Ambos son NaN, no hay cambio
                elif pd.isna(valor_actual) or pd.isna(valor_nuevo):
                    # Uno es NaN y el otro no, hay cambio
                    campos_actualizar[campo] = None if pd.isna(valor_nuevo) else valor_nuevo
                elif valor_actual != valor_nuevo:
                    # Ambos son valores válidos pero diferentes
                    campos_actualizar[campo] = valor_nuevo
                    
            except AttributeError:
                self.errores.append({
                    'codigo_error': '0006',
                    'tipo_error': 'ERROR_COMPARACION_CAMPOS',
                    'detalle': f'Error al comparar el campo {campo} para la asignatura con código {obj.codigo}. El campo no existe en el modelo Asignatura.',
                })
            except Exception as e:
                self.errores.append({
                    'codigo_error': '0006',
                    'tipo_error': 'ERROR_COMPARACION_CAMPOS',
                    'detalle': f'Error al comparar el campo {campo} para la asignatura con código {obj.codigo}: {e}',
                })

        return campos_actualizar

    
