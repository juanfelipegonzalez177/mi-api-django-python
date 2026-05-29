import logging

from application.dtos.compania_dto import CompaniaConEmpleadosSerializer, CompaniaSerializer
from application.services.compania_service import CompaniaService
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


def compania_to_dict(compania):
    return {
        'id': compania.id,
        'nombre': compania.nombre,
        'direccion': compania.direccion,
        'telefono': compania.telefono,
        'fecha_creacion': compania.fecha_creacion,
    }


class CompaniasView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompaniaService()

    def get(self, request):
        companias = self.service.get_all()
        return Response([compania_to_dict(c) for c in companias], status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CompaniaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            compania = self.service.create(serializer.validated_data)
            return Response(compania_to_dict(compania), status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creando compania: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CompaniaDetailView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompaniaService()

    def get(self, request, id):
        compania = self.service.get_by_id(id)
        if not compania:
            return Response({'error': 'Compania no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(compania_to_dict(compania), status=status.HTTP_200_OK)

    def put(self, request, id):
        serializer = CompaniaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            compania = self.service.update(id, serializer.validated_data)
            return Response(compania_to_dict(compania), status=status.HTTP_200_OK)
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
        serializer = CompaniaConEmpleadosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            compania = self.service.create_con_empleados(serializer.validated_data)
            return Response(compania_to_dict(compania), status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error en transaccion: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
