import logging

from application.dtos.empleado_dto import EmpleadoSerializer
from application.services.empleado_service import EmpleadoService
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


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


class EmpleadosView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmpleadoService()

    def get(self, request):
        empleados = self.service.get_all()
        data = [empleado_to_dict(e, include_compania=True) for e in empleados]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EmpleadoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            empleado = self.service.create(serializer.validated_data)
            return Response(empleado_to_dict(empleado), status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creando empleado: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmpleadoDetailView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmpleadoService()

    def get(self, request, id):
        empleado = self.service.get_by_id(id)
        if not empleado:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(empleado_to_dict(empleado), status=status.HTTP_200_OK)

    def put(self, request, id):
        serializer = EmpleadoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            empleado = self.service.update(id, serializer.validated_data)
            return Response(empleado_to_dict(empleado), status=status.HTTP_200_OK)
        except ValueError as e:
            status_code = status.HTTP_404_NOT_FOUND if 'no encontrado' in str(e).lower() else status.HTTP_400_BAD_REQUEST
            return Response({'error': str(e)}, status=status_code)

    def delete(self, request, id):
        try:
            self.service.delete(id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class EmpleadosPorCompaniaView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmpleadoService()

    def get(self, request, id):
        empleados = self.service.get_by_compania(id)
        data = [empleado_to_dict(e) for e in empleados]
        return Response(data, status=status.HTTP_200_OK)
