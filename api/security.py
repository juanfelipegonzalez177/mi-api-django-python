from application.services.auth_service import AuthService
from infrastructure.security.jwt_service import JwtService
from rest_framework import status
from rest_framework.response import Response


def get_authenticated_user(request):
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        raise PermissionError('Token requerido')
    token = header.replace('Bearer ', '', 1).strip()
    payload = JwtService().decode_token(token)
    return AuthService().get_usuario_from_payload(payload)


def require_roles(request, roles):
    try:
        usuario = get_authenticated_user(request)
    except Exception as exc:
        return None, Response({'error': str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

    if usuario.rol not in roles:
        return usuario, Response({'error': 'No tiene permisos para esta accion'}, status=status.HTTP_403_FORBIDDEN)
    return usuario, None


def can_modify_empleado(usuario, empleado):
    if usuario.rol == 'ADMIN':
        return True
    return usuario.compania_id and usuario.compania_id == empleado.compania_id
