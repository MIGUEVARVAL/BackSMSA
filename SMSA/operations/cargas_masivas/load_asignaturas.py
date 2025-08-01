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
        df_asignaturas_plan = self.df_asignaturas_plan[['COD_ASIGNATURA', 'COD_PLAN', 'COD_TIPOLOGIA', 'TIPOLOGIA', 'PERIDO DE OFERTA']].copy()
        df_asignaturas = self.df_asignaturas[['COD_FACULTAD', 'FACULTAD', 'COD_UAB', 'UAB', 'COD_ASIGNATURA', 'ASIGNATURA', 'CREDITOS', 'PERIODO', 'NUM_SEMANAS', 'HORAS_TEORICAS', 'HORAS_PRACTICAS', 'MININANSISTENCIA', 'ASIG_VALIDABLE']].copy()
        # Normalizar el valor de la columna TIPOLOGIA
        df_asignaturas_plan.loc[df_asignaturas_plan['TIPOLOGIA'] == 'FUND. OPTATIVA', 'TIPOLOGIA'] = 'FUNDAMENTACIÓN OPTATIVA'
        df_asignaturas_plan.loc[df_asignaturas_plan['TIPOLOGIA'] == 'FUND. OBLIGATORIA', 'TIPOLOGIA'] = 'FUNDAMENTACIÓN OBLIGATORIA'
        # Crear una lista para las tipologías únicas
        tipologias_unicas = df_asignaturas_plan[['COD_TIPOLOGIA', 'TIPOLOGIA']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las tipologías en la base de datos
        tipologias_objs = self.create_tipologias(tipologias_unicas)
        # Crear una lista para las facultades únicas
        facultades_unicas = df_asignaturas[['COD_FACULTAD', 'FACULTAD']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las facultades en la base de datos
        facultades_objs = self.create_update_facultades(facultades_unicas)
        facultades_dict = {f.codigo: f for f in facultades_objs}
        # Crear una lista para las UAB
        uab_unicas = df_asignaturas[['COD_FACULTAD', 'COD_UAB', 'UAB']].drop_duplicates().to_dict(orient='records')
        # Crear o actualizar las UAB en la base de datos
        uab_objs = self.create_update_uab(uab_unicas, facultades_dict)
        uab_dict = {u.codigo: u for u in uab_objs}
        # Crear una lista para los planes de estudio
        planes_objs = self.get_planes_estudio()
        planes_dict = {p.codigo: p for p in planes_objs}
        # Crear una lista para las asignaturas
        asignaturas_unicas = df_asignaturas.drop_duplicates().to_dict(orient='records')
        df_asignaturas_plan_unicas = df_asignaturas_plan.drop_duplicates(subset=['COD_ASIGNATURA', 'COD_PLAN', 'COD_TIPOLOGIA', 'TIPOLOGIA']).copy()
        # Crear o actualizar las asignaturas en la base de datos
        asignaturas_objs = self.create_update_asignaturas_plan(asignaturas_unicas, uab_dict, tipologias_objs, planes_dict, df_asignaturas_plan_unicas)

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
        print("Tipologías procesadas:")
        for t in tipologias_objs:
            print(f"- {t.codigo}: {t.nombre}")
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
    def create_update_uab(self, df_uab, facultades_dict):
        uab_objs = []
        with transaction.atomic():
            for uab in df_uab:
                facultad_obj = facultades_dict.get(uab['COD_FACULTAD'])
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
    def create_update_asignaturas_plan(self, asignaturas_unicas, uab_dict, tipologias_objs, planes_dict, df_asignaturas_plan_unicas):
        asignaturas_objs = []
        try:
            with transaction.atomic():
                for asignatura in asignaturas_unicas:
                    uab_obj = uab_dict.get(asignatura['COD_UAB'])
                    if not uab_obj:
                        print(f'UAB no encontrada para la asignatura: {asignatura["ASIGNATURA"]}')
                        continue
                    # Normalizar valores antes de procesar
                    for key in ['NUM_SEMANAS', 'HORAS_TEORICAS', 'HORAS_PRACTICAS', 'MININANSISTENCIA']:
                        if pd.isna(asignatura[key]):
                            asignatura[key] = None
                    # Normalizar el valor de ASIG_VALIDABLE
                    asignatura['ASIG_VALIDABLE'] = True if asignatura['ASIG_VALIDABLE'] == 'SI' else False
                    obj = Asignatura.objects.filter(codigo=asignatura['COD_ASIGNATURA']).first()
                    if obj:
                        campos_actualizar = self._asignatura_necesita_actualizacion(obj, asignatura, uab_obj)
                        if campos_actualizar:
                            for campo, valor in campos_actualizar.items():
                                setattr(obj, campo, valor)
                            obj.save()
                            print(f'Asignatura actualizada: {obj.codigo}')
                        else:
                            print(f'Asignatura sin cambios: {obj.codigo}')
                    else:
                        campos = {
                            'codigo': asignatura['COD_ASIGNATURA'],
                            'nombre': asignatura['ASIGNATURA'],
                            'creditos': asignatura['CREDITOS'],
                            'uab': uab_obj,
                            'numero_semanas': asignatura['NUM_SEMANAS'],
                            'horas_teoricas': asignatura['HORAS_TEORICAS'],
                            'horas_practicas': asignatura['HORAS_PRACTICAS'],
                            'asistencia_minima': asignatura['MININANSISTENCIA'],
                            'validable': asignatura['ASIG_VALIDABLE'],
                            'periodo': asignatura['PERIODO']
                        }

                        # Mejorar la conversión de NaN a None
                        for k, v in campos.items():
                            if pd.isna(v):
                                campos[k] = None
                            elif k in ['numero_semanas', 'horas_teoricas', 'horas_practicas', 'asistencia_minima'] and v is not None:
                                # Convertir a entero si es un campo numérico
                                try:
                                    campos[k] = int(float(v)) if v != '' else None
                                except (ValueError, TypeError):
                                    campos[k] = None

                        obj = Asignatura.objects.create(**campos)
                        print(f'Asignatura creada: {obj}')
                    asignaturas_objs.append(obj)
                    # Procesar relaciones con planes de estudio y tipologías
                    for _, row in df_asignaturas_plan_unicas.iterrows():
                        if row['COD_ASIGNATURA'] == asignatura['COD_ASIGNATURA']:
                            plan_obj = planes_dict.get(row['COD_PLAN'])
                            tipologia_obj = None
                            for t in tipologias_objs:
                                if t.codigo == row['COD_TIPOLOGIA'] and t.nombre == row['TIPOLOGIA']:
                                    tipologia_obj = t
                                    break
                            if plan_obj and tipologia_obj:
                                asignatura_plan = AsignaturaPlan.objects.filter(
                                    asignatura=obj,
                                    plan_estudio=plan_obj
                                ).first()
                                if asignatura_plan:
                                    if asignatura_plan.tipologia != tipologia_obj:
                                        asignatura_plan.tipologia = tipologia_obj
                                        asignatura_plan.save()
                                        print(f'AsignaturaPlan actualizada (tipología cambiada): {asignatura_plan}')
                                    else:
                                        print(f'AsignaturaPlan sin cambios: {asignatura_plan}')
                                else:
                                    asignatura_plan = AsignaturaPlan.objects.create(
                                        asignatura=obj,
                                        plan_estudio=plan_obj,
                                        tipologia=tipologia_obj
                                    )
                                    print(f'AsignaturaPlan creada: {asignatura_plan}')
                            else:
                                print(f'Plan de estudio o tipología no encontrada para la asignatura: {asignatura["ASIGNATURA"]} - Plan: {row["COD_PLAN"]}, Tipología: {row["COD_TIPOLOGIA"]}')
        except Exception as e:
            print(f'Error al procesar las asignaturas: {e}')
            raise e              
        print(f'Total de asignaturas procesadas: {len(asignaturas_objs)}')
        return asignaturas_objs
    
    def _asignatura_necesita_actualizacion(self, obj, datos_nuevos, uab_obj):
        """Verifica si la asignatura necesita actualización"""
        campos_comparar = [
            ('uab', uab_obj),
            ('periodo', datos_nuevos['PERIODO']),
            ('numero_semanas', datos_nuevos['NUM_SEMANAS']),
            ('horas_teoricas', datos_nuevos['HORAS_TEORICAS']),
            ('horas_practicas', datos_nuevos['HORAS_PRACTICAS']),
            ('asistencia_minima', datos_nuevos['MININANSISTENCIA']),
            ('validable', datos_nuevos['ASIG_VALIDABLE'])
        ]
        
        campos_actualizar = {}
        for campo, valor_nuevo in campos_comparar:
            # Validar si el valor es None o NaN
            if valor_nuevo is None or pd.isna(valor_nuevo):
                continue  # No actualizar si el valor nuevo es nulo o NaN
            
            try:
                valor_actual = getattr(obj, campo)
                
                # Comparar valores manejando casos especiales
                if pd.isna(valor_actual) and pd.isna(valor_nuevo):
                    continue  # Ambos son NaN, no hay cambio
                elif pd.isna(valor_actual) or pd.isna(valor_nuevo):
                    # Uno es NaN y el otro no, hay cambio
                    campos_actualizar[campo] = None if pd.isna(valor_nuevo) else valor_nuevo
                elif valor_actual != valor_nuevo:
                    # Ambos son valores válidos pero diferentes
                    campos_actualizar[campo] = valor_nuevo
                    
            except AttributeError:
                print(f"Campo {campo} no existe en el modelo Asignatura")
            except Exception as e:
                print(f"Error comparando campo {campo}: {e}")
        
        return campos_actualizar

    def get_planes_estudio(self):
        planes = PlanEstudio.objects.all()
        return planes
        
