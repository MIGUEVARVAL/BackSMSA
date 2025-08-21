import pandas as pd
from SMSA.models import PlanEstudio, Facultad, Sede
from django.db import transaction

class loadPlanesEstudio:

    def __init__(self, archivo):
        # Variables para el manejo de errores
        self.errores = []
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        # Hoja donde se encuentran la información de los planes de estudio
        self.df_planes_estudio, self.fila_dato = self.read_excel(archivo, sheet_name=1)
        # Limpiar el DataFrame de planes de estudio
        self.df_planes_estudio = self.clean_dataframe(self.df_planes_estudio)

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

    def load_planes_estudio(self):
        try:
            # Validar que el DataFrame se haya cargado correctamente
            if not hasattr(self, 'df_planes_estudio') or self.df_planes_estudio is None:
                return {
                    'exitoso': False,
                    'errores': self.errores,
                }
            
            # Validar columnas requeridas
            columnas_requeridas = ['COD_SEDE', 'SEDE', 'SNIES', 'COD_PLAN', 'DESC_PLAN', 
                                'NIVEL', 'TIPO_NIVEL', 'PLAN_ACTIVO', 'COD_FACULTAD', 
                                'FACULTAD', 'PLAN_REFORMADO', 'PUNTOS', 
                                'PER_INI_EXTINCION', 'PER_EXT_DEFINITIVA']
            
            columnas_faltantes = [col for col in columnas_requeridas if col not in self.df_planes_estudio.columns]
            
            if columnas_faltantes:
                self.errores.append({
                    'codigo_error': '0001',
                    'tipo_error': 'COLUMNAS_FALTANTES',
                    'detalle': 'Faltan las siguientes columnas en el archivo: ' + ', '.join(columnas_faltantes)
                })
                return {
                    'exitoso': False,
                    'errores': self.errores,
                }
            
            # Filtrar las columnas relevantes
            df_planes_estudio = self.df_planes_estudio[columnas_requeridas].copy()
            
            # Validar que haya datos después del filtro
            if df_planes_estudio.empty:
                self.errores.append({
                    'codigo_error': '0002',
                    'tipo_error': 'DATOS_VACIOS',
                    'detalle': 'No hay datos válidos para procesar \n Verifique que el archivo contenga datos en las columnas requeridas',
                })
                return {
                    'exitoso': False,
                    'errores': self.errores
                }

            # Crear una lista para las sedes únicas
            sedes_unicas = df_planes_estudio[['COD_SEDE', 'SEDE']].drop_duplicates().to_dict(orient='records')
            
            # Crear o actualizar las sedes en la base de datos
            resultado_sedes = self.create_update_sedes(sedes_unicas)
            if not resultado_sedes['exitoso']:
                return resultado_sedes
            
            sedes_objs = resultado_sedes['objetos']
            
            # Crear una lista para las facultades únicas
            facultades_unicas = df_planes_estudio[['COD_SEDE','COD_FACULTAD', 'FACULTAD']].drop_duplicates().to_dict(orient='records')
            
            # Crear o actualizar las facultades en la base de datos
            resultado_facultades = self.create_update_facultades(facultades_unicas, sedes_objs)
            if not resultado_facultades['exitoso']:
                return resultado_facultades
            
            facultades_objs = resultado_facultades['objetos']
            
            # Crear una lista para los planes de estudio únicos
            planes_unicos = df_planes_estudio.drop_duplicates().to_dict(orient='records')
        
            # Crear o actualizar los planes de estudio en la base de datos
            resultado_planes = self.create_update_planes(planes_unicos, facultades_objs)
            
            return resultado_planes
            
        except Exception as e:
            self.errores.append({
                'codigo_error': '0002',
                'tipo_error': 'ERROR_PROCESAMIENTO',
                'detalle': f'Error al procesar los planes de estudio: {str(e)}'
            })
            return {
                'exitoso': False,
                'errores': self.errores
            }

    def create_update_sedes(self, sedes):
        sedes_objs = []
        
        try:
            with transaction.atomic():
                for idx, sede in enumerate(sedes):
                    # Validar datos requeridos
                    if not sede.get('COD_SEDE') or not sede.get('SEDE'):
                        self.errores.append({
                            'codigo_error': '0003',
                            'tipo_error': 'DATOS_SEDE_INCOMPLETOS',
                            'detalle': f'Código o nombre de la sede es obligatorio, error detectado para la sede con código {sede["COD_SEDE"]} y nombre {sede["SEDE"]}'
                        })
                        continue
                    
                    obj = Sede.objects.filter(codigo=sede['COD_SEDE']).first()
                    if obj:
                        if obj.nombre != sede['SEDE']:
                            obj.nombre = sede['SEDE']
                            obj.save()
                            print(f'Sede actualizada: {obj}')
                        else:
                            print(f'Sede sin cambios: {obj}')
                    else:
                        obj = Sede.objects.create(
                            codigo=sede['COD_SEDE'],
                            nombre=sede['SEDE']
                        )
                        print(f'Sede creada: {obj}')
                    sedes_objs.append(obj)
            
            return {
                'exitoso': True,
                'objetos': sedes_objs
            }
            
        except Exception as e:
            error_transaccion = {
                'codigo_error': '0003',
                'tipo_error': 'ERROR_TRANSACCION_SEDES',
                'detalle': f'Error en la transacción de sedes: {str(e)} \n Valide que los campos "COD_SEDE" y "SEDE" no estén vacíos',
            }
            self.errores.append(error_transaccion)
            return {
                'exitoso': False,
                'errores': self.errores
            }

    def create_update_facultades(self, facultades, sedes_objs):
        facultades_objs = []
        
        try:
            with transaction.atomic():
                for facultad in facultades:
                    sede_obj = next((s for s in sedes_objs if s.codigo == facultad['COD_SEDE']), None)
                    if not sede_obj:
                        self.errores.append({
                            'codigo_error': '0004',
                            'tipo_error': 'DATOS_FACULTAD_INCOMPLETOS',
                            'detalle': f'Sede no encontrada para la facultad con código {facultad.get("COD_FACULTAD")}',
                        })
                        continue
                        
                    # Validar datos requeridos
                    if not facultad.get('COD_FACULTAD') or not facultad.get('FACULTAD'):
                        self.errores.append({
                            'codigo_error': '0004',
                            'tipo_error': 'DATOS_FACULTAD_INCOMPLETOS',
                            'detalle': f'Código o nombre de la facultad es obligatorio, error detectado para la facultad con código {facultad.get("COD_FACULTAD")} y nombre {facultad.get("FACULTAD")}',
                        })
                        continue
                    
                    obj = Facultad.objects.filter(codigo=facultad['COD_FACULTAD']).first()
                    if obj:
                        if obj.nombre != facultad['FACULTAD'] or obj.sede != sede_obj:
                            obj.nombre = facultad['FACULTAD']
                            obj.sede = sede_obj
                            obj.save()
                            print(f'Facultad actualizada: {obj}')
                        else:
                            print(f'Facultad sin cambios: {obj}')
                    else:
                        obj = Facultad.objects.create(
                            codigo=facultad['COD_FACULTAD'],
                            nombre=facultad['FACULTAD'],
                            sede=sede_obj
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

    def create_update_planes(self, planes, facultades_objs):
        
        # Filtrar las facultades cuyo nombre no contiene el carácter '('
        facultades_objs = [f for f in facultades_objs if '(' not in f.nombre]

        planes_procesados = 0
        
        try:
            with transaction.atomic():
                
                for idx, plan in enumerate(planes):
                    try:
                        facultad_obj = next((f for f in facultades_objs if f.codigo == plan['COD_FACULTAD']), None)
                        if not facultad_obj:
                            self.errores.append({
                                'codigo_error': '0005',
                                'tipo_error': 'FACULTAD_NO_ENCONTRADA',
                                'detalle': f'Facultad no encontrada para el plan de estudio con código {plan.get("COD_PLAN")} ubicado en la fila {idx + self.fila_dato}. (Hay casos en los que se duplica el plan para diferentes facultades como los son las que se cargan como PAET por ejemplo 6038, 7068....)',
                            })
                            continue

                        print(f'Procesando plan de estudio: {plan.get("COD_PLAN")} - {plan.get("DESC_PLAN")}')
                        # Validar datos requeridos
                        if not plan.get('COD_PLAN') or not plan.get('DESC_PLAN') or not plan.get('NIVEL') or not plan.get('PLAN_ACTIVO'):
                            self.errores.append({
                                'codigo_error': '0006',
                                'tipo_error': 'ERROR_PLAN',
                                'detalle': f'Error al procesar plan de estudio con código {plan.get("COD_PLAN")} ubicado en la fila {idx + self.fila_dato}: Código, nombre, nivel y estado son obligatorios',
                            })
                            continue

                        obj, created = PlanEstudio.objects.update_or_create(
                            codigo=plan.get('COD_PLAN'),
                            defaults={
                                'nombre': plan.get('DESC_PLAN') or None,
                                'nivel': plan.get('NIVEL') or None,
                                'activo': True if str(plan.get('PLAN_ACTIVO', '')).strip().upper() == 'SI' else False,
                                'facultad': facultad_obj,
                                'tipo_nivel': plan.get('TIPO_NIVEL') or None,
                                'snies': plan.get('SNIES') or None,
                                'plan_reformado': True if str(plan.get('PLAN_REFORMADO', '')).strip().upper() == 'SI' else False,
                                'puntos': plan.get('PUNTOS') if pd.notnull(plan.get('PUNTOS')) else None,
                                'inicio_extincion': plan.get('PER_INI_EXTINCION') if pd.notnull(plan.get('PER_INI_EXTINCION')) else None,
                                'extincion_definitiva': plan.get('PER_EXT_DEFINITIVA') if pd.notnull(plan.get('PER_EXT_DEFINITIVA')) else None
                            }
                        )
                        if created:
                            print(f'Plan de estudio creado: {obj}')
                        else:
                            print(f'Plan de estudio actualizado: {obj}')
                        planes_procesados += 1
                        
                    except Exception as e:
                        self.errores.append({
                            'codigo_error': '0006',
                            'tipo_error': 'ERROR_PLAN',
                            'detalle': f'Error al procesar plan de estudio con código {plan.get("COD_PLAN")} ubicado en la fila {idx + self.fila_dato}: {str(e)}',
                        })

            return {
                'exitoso': True,
                'errores': self.errores,
                'mensajeExito': f'Se procesaron correctamente un total de {planes_procesados} planes de estudio',
            }

        except Exception as e:
            error_transaccion = {
                'codigo_error': '0006',
                'tipo_error': 'ERROR_TRANSACCION_PLANES',
                'detalle': f'Error en la transacción de planes: {str(e)}'
            }
            self.errores.append(error_transaccion)
            return {
                'exitoso': False,
                'errores': self.errores
            }
