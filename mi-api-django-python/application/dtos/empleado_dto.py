from dataclasses import dataclass
from rest_framework import serializers


@dataclass
class EmpleadoCreateDTO:
    nombre: str
    apellido: str
    correo: str
    cargo: str
    salario: float
    compania_id: int


class EmpleadoSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=True, max_length=100)
    apellido = serializers.CharField(required=True, max_length=100)
    correo = serializers.EmailField(required=True)
    cargo = serializers.CharField(required=True, max_length=100)
    salario = serializers.DecimalField(required=True, max_digits=12, decimal_places=2, min_value=0)
    compania_id = serializers.IntegerField(required=True)