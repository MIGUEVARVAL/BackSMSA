import pandas as pd
from SMSA.models import Estudiante, Asignatura, HistorialAcademico, UnidadAcademica
from django.db import transaction

class loadNotasFinales:

    def __init__(self, archivo):
        # Variables para el manejo de errores
        self.errores = []
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        self.df_notas_finales, self.fila_dato = self.read_excel(archivo, sheet_name=1)
        self.df_notas_finales = self.clean_dataframe(self.df_notas_finales)


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
    
    def load_notas_finales(self):

        try:
            # Validar que el DataFrame se haya cargado correctamente
            if not hasattr(self, 'df_notas_finales') or self.df_notas_finales is None:
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
                'PERIODO', 'COD_PLAN', 'DOCUMENTO', 'COD_ASIGNATURA',
                'ASIGNATURA', 'CREDITOS_ASIGNATURA', 'COD_UAB_ASIGNATURA',
                'CALIFICACION_ALFABETICA', 'CALIFICACION_NUMERICA', 'VECES_VISTA'
            ]
            missing_columns = [col for col in required_columns if col not in self.df_notas_finales.columns]
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
            df = self.df_notas_finales[required_columns].copy()

            try:
                # Crear una lista para las UAB
                uab_dict = self.get_uab()

            except Exception as e:
                self.errores.append({
                    'codigo_error': '0002',
                    'tipo_error': 'ERROR_EXTRACCION_UAB',
                    'detalle': str(e)
                })
                return {
                    'exitoso': False,
                    'errores': self.errores,
                }

            # Crear o actualizar las asignaturas y sus notas finales
            resultado_historial = self.create_update_historial_academico(df, uab_dict)

            return resultado_historial

        except Exception as e:
            self.errores.append({
                'codigo_error': '0003',
                'tipo_error': 'ERROR_PROCESAMIENTO',
                'detalle': f'Error al procesar las notas finales: {str(e)}'
            })
            return {
                'exitoso': False,
                'errores': self.errores,
            }
    
    #Función para extraer las UAB
    def get_uab(self):
        uab_objs = UnidadAcademica.objects.all()
        uab_dict = {u.codigo: u for u in uab_objs}
        return uab_dict

    # Función parta crear o actualizar las asignaturas y sus notas finales
    def create_update_historial_academico(self, notas_finales, uab_dict):

        estudiantes_no_encontrados = []
        historiales_creados = 0
        historiales_actualizados = 0
        historiales_procesados = 0

        try:
                
            with transaction.atomic():
            
                # Se consulta al estudiante por su documento
                for index, nota in notas_finales.iterrows():
                    try:
                        if nota['DOCUMENTO'] in estudiantes_no_encontrados:
                            continue
                        estudiante = Estudiante.objects.filter(documento=nota['DOCUMENTO']).first()
                        if not estudiante:
                            estudiantes_no_encontrados.append(nota['DOCUMENTO'])
                            self.errores.append({
                                'codigo_error': '0005',
                                'tipo_error': 'ESTUDIANTE_NO_ENCONTRADO',
                                'detalle': f'Estudiante no encontrado con documento: {nota["DOCUMENTO"]} ubicado en la fila {self.fila_dato}'
                            })
                            continue  # Saltar a la siguiente nota si el estudiante no se encuentra

                        # Se consulta la UAB por su código
                        uab = uab_dict.get(nota['COD_UAB_ASIGNATURA'])

                        # Se consulta la asignatura por su código, de no existir, se crea
                        asignatura, created = Asignatura.objects.get_or_create(
                            codigo=nota['COD_ASIGNATURA'],
                            defaults={
                                'nombre': nota['ASIGNATURA'],
                                'creditos': nota['CREDITOS_ASIGNATURA'],
                                'uab': uab if uab else None,
                            }
                        )

                        historial = HistorialAcademico.objects.filter(
                            estudiante=estudiante,
                            asignatura=asignatura,
                            periodo=nota['PERIODO']
                        ).first()

                        # Se crea o actualiza el historial académico
                        defaults = {
                            'estado': nota['CALIFICACION_ALFABETICA'] if nota['CALIFICACION_ALFABETICA'] else 'EN CURSO',
                            'nota': nota['CALIFICACION_NUMERICA'] if pd.notna(nota['CALIFICACION_NUMERICA']) else None, 
                            'veces_vista': nota['VECES_VISTA']
                        }

                        historial, created = HistorialAcademico.objects.update_or_create(
                            estudiante=estudiante,
                            asignatura=asignatura,
                            periodo=nota['PERIODO'],
                            defaults=defaults
                        )

                        historiales_procesados += 1
                        if created:
                            historiales_creados += 1
                            print(f'Historial académico creado: {historial}')
                        else:
                            historiales_actualizados += 1
                            print(f'Historial académico actualizado: {historial}')

                    except Exception as e:
                        self.errores.append({
                            'codigo_error': '0004',
                            'tipo_error': 'ERROR_PROCESAMIENTO_NOTA',
                            'detalle': f'Error al procesar la fila {self.fila_dato} para el estudiante {nota["DOCUMENTO"]} con la asignatura {nota["ASIGNATURA"]}: {str(e)}'
                        })
            
            return {
                'exitoso': True,
                'errores': self.errores,
                'mensajeExito': f'Registros académicos procesados: {historiales_procesados}, creados: {historiales_creados}, actualizados: {historiales_actualizados}'
            }

        except Exception as e:
            error_transaccion = {
                'codigo_error': '0006',
                'tipo_error': 'ERROR_TRANSACCION_HISTORIAL',
                'detalle': f'Error en la transacción de historial académico: {str(e)}'
            }
            self.errores.append(error_transaccion)
            return {
                'exitoso': False,
                'errores': self.errores
            }