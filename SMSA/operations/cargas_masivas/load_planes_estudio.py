import pandas as pd
from SMSA.models import Tipologia, Asignatura, PlanEstudio, Facultad, Sede
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
    
    def load_planes_estudio(self):
        try:
            # Filtrar las columnas relevantes
            df_planes_estudio = self.df_planes_estudio[['COD_SEDE', 'SEDE', 'SNIES', 'COD_PLAN', 'DESC_PLAN', 'NIVEL', 'TIPO_NIVEL', 'PLAN_ACTIVO', 'COD_FACULTAD', 'FACULTAD', 'PLAN_REFORMADO', 'PUNTOS', 'PER_INI_EXTINCION', 'PER_EXT_DEFINITIVA']].copy()
            # Crear una lista para las sedes únicas
            sedes_unicas = df_planes_estudio[['COD_SEDE', 'SEDE']].drop_duplicates().to_dict(orient='records')
            # Crear o actualizar las sedes en la base de datos
            sedes_objs = self.create_update_sedes(sedes_unicas)
            # Crear una lista para las facultades únicas
            facultades_unicas = df_planes_estudio[['COD_SEDE','COD_FACULTAD', 'FACULTAD']].drop_duplicates().to_dict(orient='records')
            # Crear o actualizar las facultades en la base de datos
            facultades_objs = self.create_update_facultades(facultades_unicas, sedes_objs)
            # Crear una lista para los planes de estudio únicos
            planes_unicos = df_planes_estudio.drop_duplicates().to_dict(orient='records')
            # Crear o actualizar los planes de estudio en la base de datos
            planes_objs = self.create_update_planes(planes_unicos, facultades_objs)
            return planes_objs
        except Exception as e:
            print(f'Error al procesar los planes de estudio: {e}')
            raise e


    # Función para crear o actualizar las sedes
    def create_update_sedes(self, sedes):
        sedes_objs = []
        with transaction.atomic():
            for sede in sedes:
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
        return sedes_objs

    # Función para crear o actualizar las facultades
    def create_update_facultades(self, facultades, sedes_objs):
        facultades_objs = []
        with transaction.atomic():
            for facultad in facultades:
                sede_obj = next((s for s in sedes_objs if s.codigo == facultad['COD_SEDE']), None)
                if not sede_obj:
                    print(f'Sede no encontrada para la facultad: {facultad}')
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
        return facultades_objs
    
    # Función para crear o actualizar los planes de estudio
    def create_update_planes(self, planes, facultades_objs):
        planes_objs = []
        # Filtrar las facultades cuyo nombre no contiene el carácter '('
        facultades_objs = [f for f in facultades_objs if '(' not in f.nombre]
        print(f'Facultades filtradas: {[f.nombre for f in facultades_objs]}')
        with transaction.atomic():
            for plan in planes:
                facultad_obj = next((f for f in facultades_objs if f.codigo == plan['COD_FACULTAD']), None)
                if not facultad_obj:
                    print(f'Facultad no encontrada para el plan: {plan}')
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
                planes_objs.append(obj)
        return planes_objs