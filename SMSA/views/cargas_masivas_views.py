from SMSA.operations.cargas_masivas.load_planes_estudio import loadPlanesEstudio
from SMSA.operations.cargas_masivas.load_asignaturas import loadAsignaturas
from SMSA.operations.cargas_masivas.load_estudiantes_activos import loadEstudiantesActivos

from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action


class CargasMasivasViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='planes-estudio')
    def cargar_planes_estudio(self, request):
        archivo = request.FILES.get('file')
        if not archivo:
            return Response({'detail': 'No se envió ningún archivo.'}, status=400)
        try:
            cargador = loadPlanesEstudio(archivo)
            cargador.load_planes_estudio()
            return Response({'detail': 'Planes de estudio cargados exitosamente.'}, status=200)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
        
    @action(detail=False, methods=['post'], url_path='parametrizacion-asignaturas')
    def cargar_asignaturas(self, request):
        archivo = request.FILES.get('file')
        if not archivo:
            return Response({'detail': 'No se envió ningún archivo.'}, status=400)
        try:
            cargador = loadAsignaturas(archivo)
            cargador.load_asignaturas()
            return Response({'detail': 'Asignaturas cargadas exitosamente.'}, status=200)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
        
    @action(detail=False, methods=['post'], url_path='estudiantes-activos')
    def cargar_estudiantes_activos(self, request):
        archivo = request.FILES.get('file')
        if not archivo:
            return Response({'detail': 'No se envió ningún archivo.'}, status=400)
        try:
            cargador = loadEstudiantesActivos(archivo)
            cargador.load_estudiantes_activos()
            return Response({'detail': 'Estudiantes activos cargados exitosamente.'}, status=200)
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=500)
    