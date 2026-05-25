import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from application.services.compania_service import CompaniaService

logger = logging.getLogger(__name__)

class CompaniasView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompaniaService()

    def get(self, request):
        companias = self.service.get_all()
        data = [{
            'id': c.id,
            'nombre': c.nombre,
            'direccion': c.direccion,
            'telefono': c.telefono,
            'fecha_creacion': c.fecha_creacion
        } for c in companias]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            compania = self.service.create(request.data)
            return Response({'id': compania.id, 'nombre': compania.nombre}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creando compañía: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CompaniaDetailView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompaniaService()

    def get(self, request, id):
        compania = self.service.get_by_id(id)
        if not compania:
            return Response({'error': 'No encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'id': compania.id, 'nombre': compania.nombre, 'direccion': compania.direccion, 'telefono': compania.telefono})

    def put(self, request, id):
        try:
            compania = self.service.update(id, request.data)
            return Response({'id': compania.id, 'nombre': compania.nombre})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            self.service.delete(id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class CompaniaConEmpleadosView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompaniaService()

    def post(self, request):
        try:
            compania = self.service.create_con_empleados(request.data)
            return Response({'id': compania.id, 'nombre': compania.nombre}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error en transacción: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
