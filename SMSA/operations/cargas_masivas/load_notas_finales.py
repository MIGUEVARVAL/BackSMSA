import pandas as pd
from SMSA.models import Estudiante, Asignatura, AsignaturaPlan, Tipologia, HistorialAcademico
from django.db import transaction

class loadNotasFinales:

    def __init__(self, archivo):
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        # Hoja donde se encuentran las relaciones entre materia, plan y tipología
        self.df_asignaturas_plan = self.read_excel(archivo, sheet_name=2)
        # Hoja donde se encuentran las asignaturas
        self.df_asignaturas = self.read_excel(archivo, sheet_name=1)


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
    
    
        
