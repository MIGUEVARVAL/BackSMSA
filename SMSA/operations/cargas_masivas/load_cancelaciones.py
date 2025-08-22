import pandas as pd
from SMSA.models import Estudiante, Asignatura, HistorialAcademico
from django.db import transaction

class loadCancelaciones:

    def __init__(self, archivo):
        # Variables para el manejo de errores
        self.errores = []
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        self.df_cancelaciones, self.fila_dato = self.read_excel(archivo, sheet_name=1)
        self.df_cancelaciones = self.clean_dataframe(self.df_cancelaciones)

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
    
    def load_cancelaciones(self):

        estudiantes_no_encontrados = []

        if self.df_cancelaciones.empty:
            self.errores.append({
                'codigo_error': '0003',
                'tipo_error': 'DATOS_VACIOS',
                'detalle': 'No hay datos de cancelaciones para procesar'
            })
            return {
                'exitoso': False,
                'errores': self.errores
            }
        
        print(self.df_cancelaciones.head())

        historiales_creados = 0
        historiales_actualizados = 0
        historiales_procesados = 0

        try:
            with transaction.atomic():

                for index, row in self.df_cancelaciones.iterrows():
                    try:
                        # Validar que el estudiante no haya sido marcado previamente como no encontrado
                        if row["DOCUMENTO"] in estudiantes_no_encontrados:
                            continue
                        # Se consulta el estudiante por su documento
                        estudiante = Estudiante.objects.get(documento=row['DOCUMENTO'])
                        if not estudiante:
                            self.errores.append({
                                'codigo_error': '0005',
                                'tipo_error': 'ESTUDIANTE_NO_ENCONTRADO',
                                'detalle': f'Estudiante no encontrado con documento: {row["DOCUMENTO"]} ubicado en la fila {index + self.fila_dato}'
                            })
                            estudiantes_no_encontrados.append(row["DOCUMENTO"])
                            continue  # Saltar a la siguiente nota si el estudiante no se encuentra
                        
                        # Se consulta la asignatura por su código
                        asignatura = Asignatura.objects.get(codigo=row['COD_ASIGNATURA'])
                        if not asignatura:
                            self.errores.append({
                                'codigo_error': '0006',
                                'tipo_error': 'ASIGNATURA_NO_ENCONTRADA',
                                'detalle': f'Asignatura no encontrada con código: {row["COD_ASIGNATURA"]} ubicado en la fila {index + self.fila_dato}'
                            })
                            continue  # Saltar a la siguiente nota si la asignatura no se encuentra

                        
                        historial_academico, created = HistorialAcademico.objects.update_or_create(
                            estudiante=estudiante,
                            asignatura=asignatura,
                            periodo=row['PERIODO'], 
                            defaults={
                                'tipo_cancelacion': row['TIPO_CANCELACION'],
                                'estado': 'CN'
                            }
                        )
                        if created:
                            historiales_creados += 1
                            print(f'Historial académico creado para {estudiante.documento} - {asignatura.codigo}')
                        else:
                            historiales_actualizados += 1
                            print(f'Historial académico actualizado para {estudiante.documento} - {asignatura.codigo}')
                        historiales_procesados += 1
                    
                    except Exception as e:
                        self.errores.append({
                            'codigo_error': '0004',
                            'tipo_error': 'ERROR_PROCESAMIENTO_CANCELACION',
                            'detalle': f'Error al procesar la fila {index + self.fila_dato} para el estudiante {row["DOCUMENTO"]} con la asignatura {row["COD_ASIGNATURA"]}: {str(e)}'
                        })

            return {
                'exitoso': True,
                'errores': self.errores,
                'mensajeExito': f'Cancelaciones procesadas: {historiales_procesados}, creados: {historiales_creados}, actualizados: {historiales_actualizados}'
            }

        except Exception as e:
            error_transaccion = {
                'codigo_error': '0006',
                'tipo_error': 'ERROR_TRANSACCION_CANCELACIONES',
                'detalle': f'Error en la transacción de cancelaciones: {str(e)}'
            }
            self.errores.append(error_transaccion)
            return {
                'exitoso': False,
                'errores': self.errores
            }
