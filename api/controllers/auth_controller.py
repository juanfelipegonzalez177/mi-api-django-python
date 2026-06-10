from api.responses import validation_error
from api.security import get_authenticated_user
from application.dtos.auth_dto import LoginSerializer, RegistroSerializer
from application.services.auth_service import AuthService
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_yasg import openapi
    from drf_yasg.utils import swagger_auto_schema
except ImportError:
    openapi = None
    def swagger_auto_schema(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

try:
    from drf_spectacular.utils import extend_schema
except ImportError:
    def extend_schema(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

registro_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['nombre', 'correo', 'password'],
    properties={
        'nombre': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'correo': openapi.Schema(type=openapi.TYPE_STRING, example='usuario@mail.com'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, example='Usuario12345'),
        'rol': openapi.Schema(type=openapi.TYPE_STRING, example='USUARIO'),
        'compania_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
    },
) if openapi else RegistroSerializer

login_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['correo', 'password'],
    properties={
        'correo': openapi.Schema(type=openapi.TYPE_STRING, example='usuario@mail.com'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, example='Usuario12345'),
    },
) if openapi else LoginSerializer


def usuario_to_dict(usuario):
    return {
        'id': usuario.id,
        'nombre': usuario.nombre,
        'correo': usuario.correo,
        'rol': usuario.rol,
        'compania_id': usuario.compania_id,
    }


class RegistroView(APIView):
    serializer_class = RegistroSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = AuthService()

    @swagger_auto_schema(
        tags=['Autenticacion'],
        operation_summary='Registro',
        request_body=registro_schema,
        security=[],
    )
    @extend_schema(
        tags=['Autenticacion'],
        summary='Registro',
        request=RegistroSerializer,
        auth=[],
    )
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            usuario = self.service.registro(serializer.validated_data)
            return Response(usuario_to_dict(usuario), status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    serializer_class = LoginSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = AuthService()

    @swagger_auto_schema(
        tags=['Autenticacion'],
        operation_summary='Login',
        request_body=login_schema,
        security=[],
    )
    @extend_schema(
        tags=['Autenticacion'],
        summary='Login',
        request=LoginSerializer,
        auth=[],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            token, usuario = self.service.login(
                serializer.validated_data['correo'],
                serializer.validated_data['password'],
            )
            return Response({'access': token, 'usuario': usuario_to_dict(usuario)}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class PerfilView(APIView):
    serializer_class = RegistroSerializer

    @swagger_auto_schema(
        tags=['Autenticacion'],
        operation_summary='Perfil',
        security=[{'Bearer': []}],
    )
    @extend_schema(tags=['Autenticacion'], summary='Perfil')
    def get(self, request):
        try:
            usuario = get_authenticated_user(request)
            return Response(usuario_to_dict(usuario), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
