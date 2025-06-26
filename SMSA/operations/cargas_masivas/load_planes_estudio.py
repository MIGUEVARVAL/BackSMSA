import pandas as pd
from SMSA.models import Tipologia, Asignatura, PlanEstudio, Facultad
from django.db import transaction

class loadPlanesEstudio:

    def __init__(self, archivo):
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        # Hoja donde se encuentran la información de los planes de estudio
        self.df_planes_estudio = self.read_excel(archivo, sheet_name=1)


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
    
    def get_planes_estudio(self):
        try:
            # Filtrar las columnas relevantes
            df_planes_estudio = self.df_planes_estudio[['COD_PLAN', 'DESC_PLAN', 'NIVEL', 'TIPO_NIVEL', 'PLAN_ACTIVO', 'COD_FACULTAD', 'FACULTAD']].copy()
            # Crear una lista para las facultades únicas
            facultades_unicas = df_planes_estudio[['COD_FACULTAD', 'FACULTAD']].drop_duplicates().to_dict(orient='records')
            # Crear o actualizar las facultades en la base de datos
            facultades_objs = self.create_update_facultades(facultades_unicas)
            # Crear una lista para los planes de estudio únicos
            planes_unicos = df_planes_estudio.drop_duplicates().to_dict(orient='records')
            # Crear o actualizar los planes de estudio en la base de datos
            planes_objs = self.create_update_planes(planes_unicos, facultades_objs)
            return planes_objs
        except Exception as e:
            print(f'Error al procesar los planes de estudio: {e}')
            raise e

    # Función para crear o actualizar las facultades
    def create_update_facultades(self, facultades):
        facultades_objs = []
        with transaction.atomic():
            for facultad in facultades:
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
        return facultades_objs
    
    # Función para crear o actualizar los planes de estudio
    def create_update_planes(self, planes, facultades_objs):
        planes_objs = []
        with transaction.atomic():
            for plan in planes:
                facultad_obj = next((f for f in facultades_objs if f.codigo == plan['COD_FACULTAD']), None)
                if not facultad_obj:
                    print(f'Facultad no encontrada para el plan: {plan}')
                    continue
                
                obj = PlanEstudio.objects.filter(codigo=plan['COD_PLAN']).first()
                plan_activo_bool = True if str(plan['PLAN_ACTIVO']).strip().upper() == 'SI' else False
                if obj:
                    if (obj.nombre != plan['DESC_PLAN'] or
                        obj.nivel != plan['NIVEL'] or
                        obj.tipo_nivel != plan['TIPO_NIVEL'] or
                        obj.activo != plan['PLAN_ACTIVO']):
                        obj.nombre = plan['DESC_PLAN']
                        obj.nivel = plan['NIVEL']
                        obj.tipo_nivel = plan['TIPO_NIVEL']
                        obj.activo = plan_activo_bool
                        obj.facultad = facultad_obj
                        obj.save()
                        print(f'Plan de estudio actualizado: {obj}')
                    else:
                        print(f'Plan de estudio sin cambios: {obj}')
                else:
                    obj = PlanEstudio.objects.create(
                        codigo=plan['COD_PLAN'],
                        nombre=plan['DESC_PLAN'],
                        nivel=plan['NIVEL'],
                        tipo_nivel=plan['TIPO_NIVEL'],
                        activo=plan_activo_bool,
                        facultad=facultad_obj
                    )
                    print(f'Plan de estudio creado: {obj}')
                planes_objs.append(obj)
        return planes_objs