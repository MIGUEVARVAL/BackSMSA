import pandas as pd
from SMSA.models import Estudiante, Asignatura, AsignaturaPlan, Tipologia, HistorialAcademico
from django.db import transaction

class loadCancelaciones:

    def __init__(self, archivo):
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        self.df_cancelaciones = self.read_excel(archivo, sheet_name=1)


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
    
    def load_cancelaciones(self):

        # Se recorre el DataFrame y se verifica si la tipologia ya existe en la base de datos y se actualiza o de lo contrario se crea
        for index, row in self.df_cancelaciones.iterrows():

            with transaction.atomic():

                # Se consulta el estudiante por su documento
                try:
                    estudiante = Estudiante.objects.get(documento=row['DOCUMENTO'])
                except Estudiante.DoesNotExist:
                    continue
                
                # Se consulta la asignatura por su código
                try:
                    asignatura = Asignatura.objects.get(codigo=row['COD_ASIGNATURA'])
                except Asignatura.DoesNotExist:
                    continue   

                # Se crea el historial académico
                try:
                    historial_academico, created = HistorialAcademico.objects.get_or_create(
                        estudiante=estudiante,
                        asignatura=asignatura,
                        semestre=row['PERIODO'], 
                        defaults={
                            'tipo_cancelacion': row['TIPO_CANCELACION'],
                            'estado': 'CN'
                        }
                    )
                    print(f'Historial académico creado para {estudiante.documento} - {asignatura.codigo}')
                except Exception as e:
                    print(f'Error al crear o actualizar el historial académico: {e}')