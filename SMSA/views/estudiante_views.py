from SMSA.models import Estudiante
from SMSA.serializers.estudiante_serializers import EstudianteSerializer
from rest_framework import viewsets, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
import pandas as pd
from io import TextIOWrapper

class UserPagination(PageNumberPagination):
    page_size = 20

class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = UserPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        id = self.request.query_params.get('id', None)
        codigo = self.request.query_params.get('codigo', None)
        nombre = self.request.query_params.get('nombre', None)
        apellido = self.request.query_params.get('apellido', None)

        if id is not None:
            queryset = queryset.filter(id=id)
        if codigo is not None:
            queryset = queryset.filter(codigo__startswith=codigo)
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)
        if apellido is not None:
            queryset = queryset.filter(apellido__icontains=apellido)

        return queryset
    
    def read_excel(file_path, sheet_name=None):
        # Leer el archivo sin encabezado
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        # Buscar la primera fila no vacía para usar como encabezado
        for idx, row in df.iterrows():
            if not row.isnull().all():
                df.columns = row
                df = df.iloc[idx + 1:].reset_index(drop=True)
                break
        return df
    
    @action(detail=False, methods=['post'], url_path='cargar-archivo')
    def cargar_archivo(self, request):
        archivo = request.FILES.get('archivo')
        facultad_id = request.data.get('facultad_id')
        if not archivo:
            return Response({'detail': 'No se envió ningún archivo.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            estudiantes_creados = 0
            errores = []
            if archivo.name.endswith('.xlsx') or archivo.name.endswith('.xls'):
                archivo.seek(0)
                df = self.read_excel(archivo.file, sheet_name=None)
            else:
                return Response({'detail': 'El archivo debe ser un archivo Excel (.xlsx o .xls).'}, status=status.HTTP_400_BAD_REQUEST)

            for index, row in df.iterrows():
                try:
                    if 'DOCUMENTO' not in row:
                        raise ValueError('Falta la columna DOCUMENTO')
                    # Aquí puedes agregar más validaciones de columnas
                    # Ejemplo de creación (ajusta los campos según tu modelo):
                    Estudiante.objects.create(
                        documento=row['DOCUMENTO'],
                    )
                    estudiantes_creados += 1
                except Exception as fila_error:
                    errores.append({'fila': index+1, 'error': str(fila_error)})

            resultado = {'estudiantes_creados': estudiantes_creados}
            if errores:
                resultado['errores'] = errores
            return Response(resultado, status=status.HTTP_201_CREATED if estudiantes_creados else status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)