import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from application.services.empleado_service import EmpleadoService

logger = logging.getLogger(__name__)

class EmpleadosView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmpleadoService()

    def get(self, request):
        empleados = self.service.get_all()
        data = [{
            'id': e.id,
            'nombre': e.nombre,
            'apellido': e.apellido,
            'correo': e.correo,
            'cargo': e.cargo,
            'salario': str(e.salario),
            'compania_id': e.compania_id,
            'compania': e.compania.nombre
        } for e in empleados]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            empleado = self.service.create(request.data)
            return Response({'id': empleado.id, 'nombre': empleado.nombre}, status=status.HTTP_201_CREATED)
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
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'id': empleado.id,
            'nombre': empleado.nombre,
            'apellido': empleado.apellido,
            'correo': empleado.correo,
            'cargo': empleado.cargo,
            'salario': str(empleado.salario),
            'compania_id': empleado.compania_id
        })

    def put(self, request, id):
        try:
            empleado = self.service.update(id, request.data)
            return Response({'id': empleado.id, 'nombre': empleado.nombre})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

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
        data = [{
            'id': e.id,
            'nombre': e.nombre,
            'apellido': e.apellido,
            'correo': e.correo,
            'cargo': e.cargo,
            'salario': str(e.salario)
        } for e in empleados]
        return Response(data, status=status.HTTP_200_OK)
