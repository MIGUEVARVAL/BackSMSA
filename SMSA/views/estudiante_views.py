from SMSA.models import Estudiante
from SMSA.serializers.estudiante_serializers import EstudianteSerializer
from rest_framework import viewsets, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination

class UserPagination(PageNumberPagination):
    page_size = 40

class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = UserPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        id = self.request.query_params.get('id', None)
        codigoFacultad = self.request.query_params.get('codigoFacultad', None)
        documento = self.request.query_params.get('documento')
        nombres = self.request.query_params.get('nombres', None)
        apellidos = self.request.query_params.get('apellidos', None)
        login = self.request.query_params.get('login')
        plan = self.request.query_params.get('programa')
        acceso = self.request.query_params.get('acceso')
        subacceso = self.request.query_params.get('subacceso')
        estado = self.request.query_params.get('estado')
        matriculas = self.request.query_params.get('matriculas')
        papa_min = self.request.query_params.get('papaMin')
        papa_max = self.request.query_params.get('papaMax')
        avance_min = self.request.query_params.get('avanceMin')
        avance_max = self.request.query_params.get('avanceMax')
        orderBy = self.request.query_params.get('orderBy')
        orderDirection = self.request.query_params.get('orderDirection')
        estudianteRiesgo = self.request.query_params.get('estudianteRiesgo', None)

        if codigoFacultad is not None:
            queryset = queryset.filter(plan_estudio__facultad__codigo=codigoFacultad)
        if documento:
            queryset = queryset.filter(documento__icontains=documento)
        if nombres:
            queryset = queryset.filter(nombres__icontains=nombres)
        if apellidos:
            queryset = queryset.filter(apellidos__icontains=apellidos)
        if login:
            queryset = queryset.filter(correo_institucional__icontains=login)
        if plan:
            queryset = queryset.filter(plan_estudio__nombre__icontains=plan)
        if acceso:
            queryset = queryset.filter(acceso=acceso)
        if subacceso:
            queryset = queryset.filter(subacceso=subacceso)
        if estado:
            queryset = queryset.filter(matricula_periodo_activo=estado)
        if matriculas:
            queryset = queryset.filter(numero_matriculas=matriculas)
        if papa_min:
            queryset = queryset.filter(papa__gte=papa_min)
        if papa_max:
            queryset = queryset.filter(papa__lte=papa_max)
        if avance_min:
            queryset = queryset.filter(avance_carrera__gte=avance_min)
        if avance_max:
            queryset = queryset.filter(avance_carrera__lte=avance_max)
        if estudianteRiesgo is not None:
            if estudianteRiesgo.lower() == 'true':
                queryset = queryset.filter(estudiante_riesgo=True)
            elif estudianteRiesgo.lower() == 'false':
                queryset = queryset.filter(estudiante_riesgo=False)
        if orderBy:
            if orderDirection == "DESC":
                orderBy = f"-{orderBy}"  
            queryset = queryset.order_by(orderBy)
        else:
            queryset = queryset.order_by('-estudiante_riesgo')  # Orden por defecto
        

        return queryset
    
    