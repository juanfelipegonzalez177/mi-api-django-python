from rest_framework import serializers


class RegistroSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=True, max_length=100)
    correo = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    rol = serializers.ChoiceField(required=False, choices=['ADMIN', 'USUARIO'])
    compania_id = serializers.IntegerField(required=False, allow_null=True)


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
