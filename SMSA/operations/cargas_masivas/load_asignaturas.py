import pandas as pd
from SMSA.models import Tipologia, Asignatura, PlanEstudio, UnidadAcademica, Facultad, AsignaturaPlan
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
    
    def load_asignaturas(self):
        # Filtrar las columnas relevantes
        df_asignaturas_plan = self.df_asignaturas_plan[['COD_ASIGNATURA', 'COD_PLAN', 'COD_TIPOLOGIA', 'TIPOLOGIA']].copy()
        df_asignaturas = self.df_asignaturas[['COD_FACULTAD', 'FACULTAD', 'COD_UAB', 'UAB', 'COD_ASIGNATURA', 'ASIGNATURA', 'CREDITOS']].copy()
        # Crear una lista para las tipologías únicas
        tipologias_unicas = df_asignaturas_plan[['COD_TIPOLOGIA', 'TIPOLOGIA']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las tipologías en la base de datos
        tipologias_objs = self.create_update_tipologias(tipologias_unicas)
        # Crear una lista para las facultades únicas
        facultades_unicas = df_asignaturas[['COD_FACULTAD', 'FACULTAD']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las facultades en la base de datos
        facultades_objs = self.create_update_facultades(facultades_unicas)
        # Crear una lista para las UAB
        uab_unicas = df_asignaturas[['COD_FACULTAD', 'COD_UAB', 'UAB']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las UAB en la base de datos
        uab_objs = self.create_update_uab(uab_unicas, facultades_objs)
        # Crear una lista para los planes de estudio
        planes_objs = self.get_planes_estudio()
        # Crear una lista para las asignaturas
        asignaturas_unicas = df_asignaturas[['COD_ASIGNATURA', 'ASIGNATURA', 'COD_UAB', 'CREDITOS']].drop_duplicates().to_dict(orient='records')
        df_asignaturas_plan_unicas = df_asignaturas_plan.drop_duplicates(subset=['COD_ASIGNATURA', 'COD_PLAN', 'COD_TIPOLOGIA', 'TIPOLOGIA']).copy()
        # Crear o actualizar las asignaturas en la base de datos
        asignaturas_objs = self.create_update_asignaturas_plan(asignaturas_unicas, uab_objs, tipologias_objs, planes_objs, df_asignaturas_plan_unicas)

    # Función para crear o actualizar las tipologías
    def create_update_tipologias(self, tipologias):
        tipologias_objs = []
        with transaction.atomic():
            for tipologia in tipologias:
                obj = Tipologia.objects.filter(
                    codigo=tipologia['COD_TIPOLOGIA'],
                    nombre=tipologia['TIPOLOGIA']
                ).first()
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
    
    # Función para crear o actualizar las uab
    def create_update_uab(self, df_uab, facultades_objs):
        uab_objs = []
        with transaction.atomic():
            for uab in df_uab:
                facultad_obj = next((f for f in facultades_objs if f.codigo == uab['COD_FACULTAD']), None)
                if not facultad_obj:
                    print(f'Facultad no encontrada para la UAB: {uab["UAB"]}')
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
        return uab_objs
    
    # Función para crear o actualizar las asignaturas
    def create_update_asignaturas_plan(self, df_asignaturas, uab_objs, tipologias_objs, planes_objs, df_asignaturas_plan):
        asignaturas_objs = []
        with transaction.atomic():
            for asignatura in df_asignaturas:
                uab_obj = next((u for u in uab_objs if u.codigo == asignatura['COD_UAB']), None)
                if not uab_obj:
                    print(f'UAB no encontrada para la asignatura: {asignatura["ASIGNATURA"]}')
                    continue
                obj = Asignatura.objects.filter(codigo=asignatura['COD_ASIGNATURA']).first()
                if obj:
                    if obj.nombre != asignatura['ASIGNATURA'] or obj.uab != uab_obj:
                        obj.nombre = asignatura['ASIGNATURA']
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
                # Ahora procesamos las relaciones con los planes de estudio y las tipologías
                for index, row in df_asignaturas_plan.iterrows():
                    if row['COD_ASIGNATURA'] == asignatura['COD_ASIGNATURA']:
                        plan_obj = next((p for p in planes_objs if p.codigo == row['COD_PLAN']), None)
                        tipologia_obj = next((t for t in tipologias_objs if (t.codigo == row['COD_TIPOLOGIA'] and t.nombre == row['TIPOLOGIA'])), None)
                        if plan_obj and tipologia_obj:
                            # Buscar si ya existe una relación AsignaturaPlan para la asignatura y el plan (sin importar tipología)
                            asignatura_plan = AsignaturaPlan.objects.filter(
                                asignatura=obj,
                                plan_estudio=plan_obj
                            ).first()
                            if asignatura_plan:
                                # Si la tipología es diferente, actualiza
                                if asignatura_plan.tipologia != tipologia_obj:
                                    asignatura_plan.tipologia = tipologia_obj
                                    asignatura_plan.save()
                                    print(f'AsignaturaPlan actualizada (tipología cambiada): {asignatura_plan}')
                                else:
                                    print(f'AsignaturaPlan sin cambios: {asignatura_plan}')
                            else:
                                # Si no existe, crea la relación
                                asignatura_plan = AsignaturaPlan.objects.create(
                                    asignatura=obj,
                                    plan_estudio=plan_obj,
                                    tipologia=tipologia_obj
                                )
                                print(f'AsignaturaPlan creada: {asignatura_plan}')
                        else:
                            print(f'Plan de estudio o tipología no encontrada para la asignatura: {asignatura["ASIGNATURA"]} - Plan: {row["COD_PLAN"]}, Tipología: {row["COD_TIPOLOGIA"]}')
        # Devolver la lista de asignaturas creadas o actualizadas
        print(f'Total de asignaturas procesadas: {len(asignaturas_objs)}')
            
        return asignaturas_objs
    
    def get_planes_estudio(self):
        planes = PlanEstudio.objects.all()
        return planes
        
