from dataclasses import dataclass
from typing import List
from rest_framework import serializers


@dataclass
class CompaniaCreateDTO:
    nombre: str
    direccion: str
    telefono: str


@dataclass
class EmpleadoEnCompaniaDTO:
    nombre: str
    apellido: str
    correo: str
    cargo: str
    salario: float


@dataclass
class CompaniaConEmpleadosDTO:
    nombre: str
    direccion: str
    telefono: str
    empleados: List[EmpleadoEnCompaniaDTO]


class EmpleadoEnCompaniaSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=True, max_length=100)
    apellido = serializers.CharField(required=True, max_length=100)
    correo = serializers.EmailField(required=True)
    cargo = serializers.CharField(required=True, max_length=100)
    salario = serializers.DecimalField(required=True, max_digits=12, decimal_places=2, min_value=0)


class CompaniaSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=True, max_length=200)
    direccion = serializers.CharField(required=True, max_length=200)
    telefono = serializers.CharField(required=True, max_length=20)


class CompaniaPatchSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=False, max_length=200)
    direccion = serializers.CharField(required=False, max_length=200)
    telefono = serializers.CharField(required=False, max_length=20)


class CompaniaConEmpleadosSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=True, max_length=200)
    direccion = serializers.CharField(required=True, max_length=200)
    telefono = serializers.CharField(required=True, max_length=20)
    empleados = EmpleadoEnCompaniaSerializer(many=True, required=True)
