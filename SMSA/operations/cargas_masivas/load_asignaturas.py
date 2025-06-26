import pandas as pd
from SMSA.models import Tipologia, Asignatura, PlanEstudio, UnidadAcademica
from django.db import transaction

class loadAsignaturas:

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
    
    def get_asignaturas(self):
        # Filtrar las columnas relevantes
        df_asignaturas_plan = self.df_asignaturas_plan[['COD_ASIGNATURA', 'COD_PLAN', 'COD_TIPOLOGIA', 'TIPOLOGIA']].copy()
        df_asignaturas = self.df_asignaturas[['COD_UAB', 'UAB', 'COD_ASIGNATURA', 'ASIGNATURA', 'CREDITOS']].copy()
        # Crear una lista para las tipologías únicas
        tipologias_unicas = df_asignaturas_plan[['COD_TIPOLOGIA', 'TIPOLOGIA']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las tipologías en la base de datos
        tipologias_objs = self.create_update_tipologias(tipologias_unicas)
        # Crear una lista para las UAB
        uab_unicas = df_asignaturas[['COD_UAB', 'UAB']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las UAB en la base de datos
        uab_objs = self.create_update_uab(uab_unicas)
        # Crear una lista para las asignaturas
        asignaturas_unicas = df_asignaturas[['COD_ASIGNATURA', 'ASIGNATURA', 'COD_UAB', 'UAB', 'CREDITOS']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las asignaturas en la base de datos
        asignaturas_objs = self.create_update_asignaturas(asignaturas_unicas, uab_objs)

    # Función para crear o actualizar las tipologías
    def create_update_tipologias(self, tipologias):
        tipologias_objs = []
        with transaction.atomic():
            for tipologia in tipologias:
                obj = Tipologia.objects.filter(codigo=tipologia['COD_TIPOLOGIA']).first()
                if obj:
                    if obj.nombre != tipologia['TIPOLOGIA']:
                        obj.nombre = tipologia['TIPOLOGIA']
                        obj.save()
                        print(f'Tipología actualizada: {obj}')
                    else:
                        print(f'Tipología sin cambios: {obj}')
                else:
                    obj = Tipologia.objects.create(
                        codigo=tipologia['COD_TIPOLOGIA'],
                        nombre=tipologia['TIPOLOGIA']
                    )
                    print(f'Tipología creada: {obj}')
                tipologias_objs.append(obj)
        return tipologias_objs
    
    # Función para crear o actualizar las uab
    def create_update_uab(self, df_uab):
        uab_objs = []
        with transaction.atomic():
            for uab in df_uab:
                obj = UnidadAcademica.objects.filter(codigo=uab['COD_UAB']).first()
                if obj:
                    if obj.nombre != uab['UAB']:
                        obj.nombre = uab['UAB']
                        obj.save()
                        print(f'UAB actualizada: {obj}')
                    else:
                        print(f'UAB sin cambios: {obj}')
                else:
                    obj = UnidadAcademica.objects.create(
                        codigo=uab['COD_UAB'],
                        nombre=uab['UAB']
                    )
                    print(f'UAB creada: {obj}')
                uab_objs.append(obj)
        return uab_objs
    
    # Función para crear o actualizar las asignaturas
    def create_update_asignaturas(self, df_asignaturas, uab_objs):
        asignaturas_objs = []
        with transaction.atomic():
            for asignatura in df_asignaturas:
                uab_obj = next((u for u in uab_objs if u.codigo == asignatura['COD_UAB']), None)
                if not uab_obj:
                    print(f'UAB no encontrada para la asignatura: {asignatura["ASIGNATURA"]}')
                    continue
                obj = Asignatura.objects.filter(codigo=asignatura['COD_ASIGNATURA']).first()
                if obj:
                    if obj.nombre != asignatura['ASIGNATURA'] or obj.creditos != asignatura['CREDITOS'] or obj.uab != uab_obj:
                        obj.nombre = asignatura['ASIGNATURA']
                        obj.creditos = asignatura['CREDITOS']
                        obj.uab = uab_obj
                        obj.save()
                        print(f'Asignatura actualizada: {obj}')
                    else:
                        print(f'Asignatura sin cambios: {obj}')
                else:
                    obj = Asignatura.objects.create(
                        codigo=asignatura['COD_ASIGNATURA'],
                        nombre=asignatura['ASIGNATURA'],
                        creditos=asignatura['CREDITOS'],
                        uab=uab_obj
                    )
                    print(f'Asignatura creada: {obj}')
                asignaturas_objs.append(obj)
        return asignaturas_objs
    
