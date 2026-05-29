import logging

from api.responses import validation_error
from api.security import can_modify_empleado, require_roles
from application.dtos.empleado_dto import DeleteManySerializer, EmpleadoBulkSerializer, EmpleadoPatchSerializer, EmpleadoSerializer
from application.services.empleado_service import EmpleadoService
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

empleado_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['nombre', 'apellido', 'correo', 'cargo', 'salario', 'compania_id'],
    properties={
        'nombre': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'apellido': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'correo': openapi.Schema(type=openapi.TYPE_STRING, example='empleado@mail.com'),
        'cargo': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'salario': openapi.Schema(type=openapi.TYPE_NUMBER, example=2500000),
        'compania_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
    },
) if openapi else EmpleadoSerializer

empleado_patch_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'nombre': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'apellido': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'correo': openapi.Schema(type=openapi.TYPE_STRING, example='empleado@mail.com'),
        'cargo': openapi.Schema(type=openapi.TYPE_STRING, example='string'),
        'salario': openapi.Schema(type=openapi.TYPE_NUMBER, example=2500000),
        'compania_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
    },
) if openapi else EmpleadoPatchSerializer

empleado_bulk_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['empleados'],
    properties={
        'empleados': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=empleado_schema,
        ),
    },
) if openapi else EmpleadoBulkSerializer

delete_many_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['ids'],
    properties={
        'ids': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        ),
    },
) if openapi else DeleteManySerializer


def empleado_to_dict(empleado, include_compania=False):
    data = {
        'id': empleado.id,
        'nombre': empleado.nombre,
        'apellido': empleado.apellido,
        'correo': empleado.correo,
        'cargo': empleado.cargo,
        'salario': str(empleado.salario),
        'compania_id': empleado.compania_id,
    }
    if include_compania:
        data['compania'] = empleado.compania.nombre
    return data


def envelope(page_data):
    return {
        'datos': [empleado_to_dict(e, include_compania=True) for e in page_data['datos']],
        'pagina': page_data['pagina'],
        'tamano': page_data['tamano'],
        'total': page_data['total'],
        'paginas': page_data['paginas'],
    }


class EmpleadosView(APIView):
    serializer_class = EmpleadoSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmpleadoService()

    @swagger_auto_schema(tags=['Empleados'], operation_summary='Listar empleados', security=[{'Bearer': []}])
    @extend_schema(tags=['Empleados'], summary='Listar empleados')
    def get(self, request):
        _, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        data = self.service.list_paginated(request.query_params)
        return Response(envelope(data), status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Empleados'], operation_summary='Crear empleado', request_body=empleado_schema, security=[{'Bearer': []}])
    @extend_schema(tags=['Empleados'], summary='Crear empleado', request=EmpleadoSerializer)
    def post(self, request):
        _, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        serializer = EmpleadoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            empleado = self.service.create(serializer.validated_data)
            return Response(empleado_to_dict(empleado), status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creando empleado: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmpleadoBulkView(APIView):
    serializer_class = EmpleadoBulkSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmpleadoService()

    @swagger_auto_schema(tags=['Empleados'], operation_summary='Crear empleados masivamente', request_body=empleado_bulk_schema, security=[{'Bearer': []}])
    @extend_schema(tags=['Empleados'], summary='Crear empleados masivamente', request=EmpleadoBulkSerializer)
    def post(self, request):
        _, error = require_roles(request, ['ADMIN'])
        if error:
            return error
        serializer = EmpleadoBulkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            empleados = self.service.bulk_create(serializer.validated_data['empleados'])
            return Response([empleado_to_dict(e) for e in empleados], status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmpleadoBulkDeleteView(APIView):
    serializer_class = DeleteManySerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmpleadoService()

    @swagger_auto_schema(tags=['Empleados'], operation_summary='Eliminar empleados masivamente', request_body=delete_many_schema, security=[{'Bearer': []}])
    @extend_schema(tags=['Empleados'], summary='Eliminar empleados masivamente', request=DeleteManySerializer)
    def delete(self, request):
        _, error = require_roles(request, ['ADMIN'])
        if error:
            return error
        serializer = DeleteManySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            deleted = self.service.delete_many(serializer.validated_data['ids'])
            return Response({'eliminados': deleted}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmpleadoDetailView(APIView):
    serializer_class = EmpleadoSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmpleadoService()

    @swagger_auto_schema(tags=['Empleados'], operation_summary='Detalle empleado', security=[{'Bearer': []}])
    @extend_schema(tags=['Empleados'], summary='Detalle empleado')
    def get(self, request, id):
        _, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        empleado = self.service.get_by_id(id)
        if not empleado:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(empleado_to_dict(empleado), status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Empleados'], operation_summary='Actualizar empleado', request_body=empleado_schema, security=[{'Bearer': []}])
    @extend_schema(tags=['Empleados'], summary='Actualizar empleado', request=EmpleadoSerializer)
    def put(self, request, id):
        usuario, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        empleado_actual = self.service.get_by_id(id)
        if not empleado_actual:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if not can_modify_empleado(usuario, empleado_actual):
            return Response({'error': 'Politica EsPropietarioDeCompania denegada'}, status=status.HTTP_403_FORBIDDEN)

        serializer = EmpleadoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if usuario.rol != 'ADMIN' and serializer.validated_data.get('salario', 0) > 5000000:
            return Response({'error': 'Politica LimiteSalario denegada'}, status=status.HTTP_403_FORBIDDEN)

        try:
            empleado = self.service.update(id, serializer.validated_data)
            return Response(empleado_to_dict(empleado), status=status.HTTP_200_OK)
        except ValueError as e:
            status_code = status.HTTP_404_NOT_FOUND if 'no encontrado' in str(e).lower() else status.HTTP_400_BAD_REQUEST
            return Response({'error': str(e)}, status=status_code)

    @swagger_auto_schema(tags=['Empleados'], operation_summary='Actualizar parcialmente empleado', request_body=empleado_patch_schema, security=[{'Bearer': []}])
    @extend_schema(tags=['Empleados'], summary='Actualizar parcialmente empleado', request=EmpleadoPatchSerializer)
    def patch(self, request, id):
        usuario, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        empleado_actual = self.service.get_by_id(id)
        if not empleado_actual:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if not can_modify_empleado(usuario, empleado_actual):
            return Response({'error': 'Politica EsPropietarioDeCompania denegada'}, status=status.HTTP_403_FORBIDDEN)

        serializer = EmpleadoPatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(validation_error(serializer), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if usuario.rol != 'ADMIN' and serializer.validated_data.get('salario', 0) > 5000000:
            return Response({'error': 'Politica LimiteSalario denegada'}, status=status.HTTP_403_FORBIDDEN)

        try:
            empleado = self.service.patch(id, serializer.validated_data)
            return Response(empleado_to_dict(empleado), status=status.HTTP_200_OK)
        except ValueError as e:
            status_code = status.HTTP_404_NOT_FOUND if 'no encontrado' in str(e).lower() else status.HTTP_400_BAD_REQUEST
            return Response({'error': str(e)}, status=status_code)

    @swagger_auto_schema(tags=['Empleados'], operation_summary='Eliminar empleado', security=[{'Bearer': []}])
    @extend_schema(tags=['Empleados'], summary='Eliminar empleado')
    def delete(self, request, id):
        usuario, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        empleado = self.service.get_by_id(id)
        if not empleado:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        if usuario.rol != 'ADMIN' and not can_modify_empleado(usuario, empleado):
            return Response({'error': 'Politica EsPropietarioDeCompania denegada'}, status=status.HTTP_403_FORBIDDEN)
        try:
            self.service.delete(id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class EmpleadosPorCompaniaView(APIView):
    serializer_class = EmpleadoSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmpleadoService()

    @swagger_auto_schema(tags=['Empleados'], operation_summary='Empleados por compania', security=[{'Bearer': []}])
    @extend_schema(tags=['Empleados'], summary='Empleados por compania')
    def get(self, request, id):
        _, error = require_roles(request, ['ADMIN', 'USUARIO'])
        if error:
            return error
        empleados = self.service.get_by_compania(id)
        data = [empleado_to_dict(e) for e in empleados]
        return Response(data, status=status.HTTP_200_OK)
