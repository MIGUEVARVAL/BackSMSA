import pandas as pd
from SMSA.models import Estudiante, Asignatura, AsignaturaPlan, Tipologia, HistorialAcademico, PlanEstudio, UnidadAcademica
from django.db import transaction

class loadNotasFinales:

    def __init__(self, archivo):
        # archivo: archivo recibido desde el frontend (request.FILES['archivo'])
        self.df_notas_finales = self.read_excel(archivo, sheet_name=1)


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
    
    def load_notas_finales(self):
        # Filtrar las columnas relevantes
        df_notas_finales = self.df_notas_finales[[
            'PERIODO', 'COD_PLAN', 'DOCUMENTO', 'COD_ASIGNATURA', 'ASIGNATURA',
            'COD_TIPOLOGIA', 'TIPOLOGIA', 'CREDITOS_ASIGNATURA', 'COD_UAB_ASIGNATURA',
            'CALIFICACION_ALFABETICA', 'CALIFICACION_NUMERICA', 'VECES_VISTA'
            ]].copy()
        
        # Crear una lista para las tipologías únicas
        tipologias_unicas = df_notas_finales[['COD_TIPOLOGIA', 'TIPOLOGIA']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las tipologías en la base de datos
        tipologias_objs = self.create_tipologias(tipologias_unicas)
        tipologias_dict = {t.codigo: t for t in tipologias_objs}
        # Crear una lista para los estudiantes únicos
        planes_dict = self.get_planes_estudio()
        # Crear una lista para las UAB
        uab_dict = self.get_uab()

        # Crear o actualizar las asignaturas y sus notas finales
        self.create_update_historial_academico(df_notas_finales.to_dict(orient='records'), uab_dict, tipologias_dict, planes_dict)
    

    # Función para crear o actualizar las tipologías
    def create_tipologias(self, tipologias):
        tipologias_objs = []
        with transaction.atomic():
            for tipologia in tipologias:
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
        return tipologias_objs
    
    # Función para extraer los planes de estudio
    def get_planes_estudio(self):
        planes_objs = PlanEstudio.objects.all()
        planes_dict = {p.codigo: p for p in planes_objs}
        return planes_dict
    
    #Función para extraer las UAB
    def get_uab(self):
        uab_objs = UnidadAcademica.objects.all()
        uab_dict = {u.codigo: u for u in uab_objs}
        return uab_dict

    # Función parta crear o actualizar las asignaturas y sus notas finales
    def create_update_historial_academico(self, notas_finales, uab_dict, tipologias_dict, planes_dict):
        # Se consulta al estudiante por su documento
        for nota in notas_finales:
            estudiante = Estudiante.objects.filter(documento=nota['DOCUMENTO']).first()
            if not estudiante:
                print(f'Estudiante no encontrado: {nota["DOCUMENTO"]}')
                continue
            
            # Se consulta el plan de estudio por su código
            plan_estudio = planes_dict.get(nota['COD_PLAN'])
            if not plan_estudio:
                print(f'Plan de estudio no encontrado: {nota["COD_PLAN"]}')
                continue
            
            # Se consulta la UAB por su código
            uab = uab_dict.get(nota['COD_UAB_ASIGNATURA'])
            if not uab:
                print(f'UAB no encontrada: {nota["COD_UAB_ASIGNATURA"]}')

            # Se consulta la asignatura por su código, de no existir, se crea
            asignatura, created = Asignatura.objects.get_or_create(
                codigo=nota['COD_ASIGNATURA'],
                defaults={
                    'nombre': nota['ASIGNATURA'],
                    'creditos': nota['CREDITOS_ASIGNATURA'],
                    'uab': uab,
                    'parametrizacion': False,
                    'descripcion': '',
                }
            )

            #Asociar la asignatura al plan de estudio y tipología
            asignatura_plan, created = AsignaturaPlan.objects.get_or_create(
                asignatura=asignatura,
                plan_estudio=plan_estudio,
                tipologia=tipologias_dict.get(nota['COD_TIPOLOGIA']),
                defaults={
                    'parametrizacion': False
                }
            )
            
            # Se crea o actualiza el historial académico
            defaults = {
                'estado': nota['CALIFICACION_ALFABETICA'],
                'veces_vista': nota['VECES_VISTA'],
            }
            # Solo asignar 'nota' si no es NaN
            if pd.notna(nota['CALIFICACION_NUMERICA']):
                defaults['nota'] = nota['CALIFICACION_NUMERICA']

            historial, created = HistorialAcademico.objects.update_or_create(
                estudiante=estudiante,
                asignatura=asignatura,
                semestre=nota['PERIODO'],
                defaults=defaults
            )
            
            if created:
                print(f'Historial académico creado: {historial}')
            else:
                print(f'Historial académico actualizado: {historial}')
        
