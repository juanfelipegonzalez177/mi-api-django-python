import logging

from api.responses import validation_error
from api.security import require_roles
from application.dtos.compania_dto import CompaniaConEmpleadosSerializer, CompaniaPatchSerializer, CompaniaSerializer
from application.services.compania_service import CompaniaService
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

logger = logging.getLogger(__name__)

compania_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['nombre', 'direccion', 'telefono'],
    properties={
        'nombre': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'direccion': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'telefono': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
    },
) if openapi else CompaniaSerializer

compania_patch_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'nombre': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'direccion': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'telefono': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
    },
) if openapi else CompaniaPatchSerializer

compania_con_empleados_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['nombre', 'direccion', 'telefono', 'empleados'],
    properties={
        'nombre': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'direccion': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'telefono': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'empleados': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'nombre': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
                    'apellido': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
                    'correo': openapi.Schema(type=openapi.TYPE_STRING, example='empleado@mail.com'),
                    'cargo': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
                    'salario': openapi.Schema(type=openapi.TYPE_NUMBER, example=2500000),
                },
            ),
        ),
    },
) if openapi else CompaniaConEmpleadosSerializer


def compania_to_dict(compania):
    return {
        'id': compania.id,
        'nombre': compania.nombre,
        'direccion': compania.direccion,
        'telefono': compania.telefono,
        'fecha_creacion': compania.fecha_creacion,
    }


def envelope(page_data):
    return {
        'datos': [compania_to_dict(c) for c in page_data['datos']],
        'pagina': page_data['pagina'],
        'tamano': page_data['tamano'],
        'total': page_data['total'],
        'paginas': page_data['paginas'],
    }


class CompaniasView(APIView):
    serializer_class = CompaniaSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompaniaService()

    @swagger_auto_schema(tags=['Companias'], operation_summary='Listar companias', security=[{'Bearer': []}])
    @extend_schema(tags=['Companias'], summary='Listar companias')
    def get(self, request):
        _, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        page_data = self.service.list_paginated(request.query_params)
        return Response(envelope(page_data), status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Companias'], operation_summary='Crear compania', request_body=compania_schema, security=[{'Bearer': []}])
    @extend_schema(tags=['Companias'], summary='Crear compania', request=CompaniaSerializer)
    def post(self, request):
        _, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        serializer = CompaniaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            compania = self.service.create(serializer.validated_data)
            return Response(compania_to_dict(compania), status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creando compania: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CompaniaDetailView(APIView):
    serializer_class = CompaniaSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompaniaService()

    @swagger_auto_schema(tags=['Companias'], operation_summary='Detalle compania', security=[{'Bearer': []}])
    @extend_schema(tags=['Companias'], summary='Detalle compania')
    def get(self, request, id):
        _, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        compania = self.service.get_by_id(id)
        if not compania:
            return Response({'error': 'Compania no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(compania_to_dict(compania), status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Companias'], operation_summary='Actualizar compania', request_body=compania_schema, security=[{'Bearer': []}])
    @extend_schema(tags=['Companias'], summary='Actualizar compania', request=CompaniaSerializer)
    def put(self, request, id):
        _, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        serializer = CompaniaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            compania = self.service.update(id, serializer.validated_data)
            return Response(compania_to_dict(compania), status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(tags=['Companias'], operation_summary='Actualizar parcialmente compania', request_body=compania_patch_schema, security=[{'Bearer': []}])
    @extend_schema(tags=['Companias'], summary='Actualizar parcialmente compania', request=CompaniaPatchSerializer)
    def patch(self, request, id):
        _, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        serializer = CompaniaPatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            compania = self.service.patch(id, serializer.validated_data)
            return Response(compania_to_dict(compania), status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(tags=['Companias'], operation_summary='Eliminar compania', security=[{'Bearer': []}])
    @extend_schema(tags=['Companias'], summary='Eliminar compania')
    def delete(self, request, id):
        _, error = require_roles(request, ['ADMIN'])
        if error:
            return error
        try:
            self.service.delete(id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class CompaniaConEmpleadosView(APIView):
    serializer_class = CompaniaConEmpleadosSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompaniaService()

    @swagger_auto_schema(tags=['Companias'], operation_summary='Crear compania con empleados', request_body=compania_con_empleados_schema, security=[{'Bearer': []}])
    @extend_schema(tags=['Companias'], summary='Crear compania con empleados', request=CompaniaConEmpleadosSerializer)
    def post(self, request):
        _, error = require_roles(request, ['ADMIN'])
        if error:
            return error
        serializer = CompaniaConEmpleadosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            compania = self.service.create_con_empleados(serializer.validated_data)
            return Response(compania_to_dict(compania), status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error en transaccion: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
