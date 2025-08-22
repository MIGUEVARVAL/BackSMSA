from SMSA.operations.cargas_masivas.load_planes_estudio import loadPlanesEstudio
from SMSA.operations.cargas_masivas.load_asignaturas import loadAsignaturas
from SMSA.operations.cargas_masivas.load_estudiantes_activos import loadEstudiantesActivos
from SMSA.operations.cargas_masivas.load_estudiantes_riesgo import loadEstudiantesRiesgo
from SMSA.operations.cargas_masivas.load_notas_finales import loadNotasFinales
from SMSA.operations.cargas_masivas.load_cancelaciones import loadCancelaciones

from rest_framework import viewsets, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action


class CargasMasivasViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def validaciones_iniciales(self, archivo):
        errores = []
        
        if not archivo:
            errores.append({
                'codigo_error': '0001',
                'tipo_error': 'ARCHIVO_FALTANTE',
                'detalle': 'No se envió ningún archivo',
            })

        # Validar tamaño del archivo (ejemplo: máximo 10MB)
        if archivo.size > 10 * 1024 * 1024:  # 10MB
            errores.append({
                'codigo_error': '0002',
                'tipo_error': 'ARCHIVO_MUY_GRANDE',
                'detalle': 'El archivo es demasiado grande (>10MB), el archivo compartido tiene un tamaño de {size} bytes'.format(size=archivo.size),
            })

        # Validar tipo de archivo
        if hasattr(archivo, 'name'):
            file_name = archivo.name.lower()
            if not (file_name.endswith('.xlsx') or file_name.endswith('.xls')):
                errores.append({
                    'codigo_error': '0003',
                    'tipo_error': 'FORMATO_ARCHIVO_INVALIDO',
                    'detalle': 'Formato de archivo no válido, se esperaba un archivo Excel (.xlsx o .xls)'
                })
        
        return errores


    @action(detail=False, methods=['post'], url_path='planes-estudio')
    def cargar_planes_estudio(self, request):
        errores = []
        try:
            archivo = request.FILES.get('file')
            
            # Validaciones del archivo
            errores = self.validaciones_iniciales(archivo)
            if errores:
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                cargador = loadPlanesEstudio(archivo)
            except Exception as e:
                errores.append({
                    'codigo_error': '0004',
                    'tipo_error': 'ERROR_INICIALIZACION',
                    'detalle': f'Error al inicializar el cargador de planes de estudio: {str(e)} \n Asegúrese de que el archivo tenga el formato correcto y contenga las hojas necesarias.',
                })
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)

            resultado = cargador.load_planes_estudio()

            if resultado.get('exitoso', False):
                return Response(resultado, status=status.HTTP_200_OK)
            else:
                return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            # Error no controlado
            errores.append({
                'codigo_error': '0005',
                'tipo_error': 'ERROR_INESPERADO',
                'detalle': f'Error inesperado al procesar el archivo: {str(e)}',
            })
            return Response({
                'errores': errores,
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='parametrizacion-asignaturas')
    def cargar_asignaturas(self, request):
        errores = []
        try:
            archivo = request.FILES.get('file')
            
            # Validaciones del archivo
            errores = self.validaciones_iniciales(archivo)
            if errores:
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                cargador = loadAsignaturas(archivo)
            except Exception as e:
                errores.append({
                    'codigo_error': '0004',
                    'tipo_error': 'ERROR_INICIALIZACION',
                    'detalle': f'Error al inicializar el cargador de asignaturas: {str(e)} \n Asegúrese de que el archivo tenga el formato correcto y contenga las hojas necesarias.',
                })
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)

            resultado = cargador.load_asignaturas()

            if resultado.get('exitoso', False):
                return Response(resultado, status=status.HTTP_200_OK)
            else:
                return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Error no controlado
            errores.append({
                'codigo_error': '0005',
                'tipo_error': 'ERROR_INESPERADO',
                'detalle': f'Error inesperado al procesar el archivo: {str(e)}',
            })
            return Response({
                'errores': errores,
            }, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='estudiantes-activos')
    def cargar_estudiantes_activos(self, request):
        errores = []
        try:
            archivo = request.FILES.get('file')
            
            # Validaciones del archivo
            errores = self.validaciones_iniciales(archivo)
            if errores:
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                cargador = loadEstudiantesActivos(archivo)
            except Exception as e:
                errores.append({
                    'codigo_error': '0004',
                    'tipo_error': 'ERROR_INICIALIZACION',
                    'detalle': f'Error al inicializar el cargador de estudiantes activos: {str(e)} \n Asegúrese de que el archivo tenga el formato correcto y contenga las hojas necesarias.',
                })
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)

            resultado = cargador.load_estudiantes_activos()

            if resultado.get('exitoso', False):
                return Response(resultado, status=status.HTTP_200_OK)
            else:
                return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Error no controlado
            errores.append({
                'codigo_error': '0005',
                'tipo_error': 'ERROR_INESPERADO',
                'detalle': f'Error inesperado al procesar el archivo: {str(e)}',
            })
            return Response({
                'errores': errores,
            }, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='estudiantes-riesgo')
    def cargar_estudiantes_riesgo(self, request):
        errores = []
        try:
            archivo = request.FILES.get('file')
            
            # Validaciones del archivo
            errores = self.validaciones_iniciales(archivo)
            if errores:
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                cargador = loadEstudiantesRiesgo(archivo)
            except Exception as e:
                errores.append({
                    'codigo_error': '0004',
                    'tipo_error': 'ERROR_INICIALIZACION',
                    'detalle': f'Error al inicializar el cargador de estudiantes en riesgo: {str(e)} \n Asegúrese de que el archivo tenga el formato correcto y contenga las hojas necesarias.',
                })
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)

            resultado = cargador.load_estudiantes_riesgo()

            if resultado.get('exitoso', False):
                return Response(resultado, status=status.HTTP_200_OK)
            else:
                return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Error no controlado
            errores.append({
                'codigo_error': '0005',
                'tipo_error': 'ERROR_INESPERADO',
                'detalle': f'Error inesperado al procesar el archivo: {str(e)}',
            })
            return Response({
                'errores': errores,
            }, status=status.HTTP_400_BAD_REQUEST)
            
    
    @action(detail=False, methods=['post'], url_path='notas-finales')
    def cargar_notas_finales(self, request):
        errores = []
        try:
            archivo = request.FILES.get('file')
            
            # Validaciones del archivo
            errores = self.validaciones_iniciales(archivo)
            if errores:
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                cargador = loadNotasFinales(archivo)
            except Exception as e:
                errores.append({
                    'codigo_error': '0004',
                    'tipo_error': 'ERROR_INICIALIZACION',
                    'detalle': f'Error al inicializar el cargador de notas finales: {str(e)} \n Asegúrese de que el archivo tenga el formato correcto y contenga las hojas necesarias.',
                })
                return Response({
                    'errores': errores,
                }, status=status.HTTP_400_BAD_REQUEST)

            resultado = cargador.load_notas_finales()

            if resultado.get('exitoso', False):
                return Response(resultado, status=status.HTTP_200_OK)
            else:
                return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Error no controlado
            errores.append({
                'codigo_error': '0005',
                'tipo_error': 'ERROR_INESPERADO',
                'detalle': f'Error inesperado al procesar el archivo: {str(e)}',
            })
            return Response({
                'errores': errores,
            }, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='cancelaciones')
    def cargar_cancelaciones(self, request):
        archivo = request.FILES.get('file')
        if not archivo:
            return Response({'detail': 'No se envió ningún archivo.'}, status=400)
        try:
            cargador = loadCancelaciones(archivo)
            cargador.load_cancelaciones()
            return Response({'detail': 'Cancelaciones cargadas exitosamente.'}, status=200)
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=500)