from infrastructure.security.jwt_service import JwtService
from infrastructure.security.password_hasher import PasswordHasher
from infrastructure.unit_of_work.django_unit_of_work import DjangoUnitOfWork


class AuthService:
    def __init__(self):
        self.uow = DjangoUnitOfWork()
        self.hasher = PasswordHasher()
        self.jwt = JwtService()

    def registro(self, data: dict):
        with self.uow:
            if self.uow.usuarios.get_by_correo(data['correo']):
                raise ValueError('El correo ya esta registrado')
            compania_id = data.get('compania_id')
            if compania_id and not self.uow.companias.get_by_id(compania_id):
                raise ValueError('Compania no encontrada')
            usuario = self.uow.usuarios.create({
                'nombre': data['nombre'],
                'correo': data['correo'],
                'password_hash': self.hasher.hash(data['password']),
                'rol': data.get('rol', 'USUARIO'),
                'compania_id': compania_id,
            })
            usuario.save()
            return usuario

    def login(self, correo: str, password: str):
        usuario = self.uow.usuarios.get_by_correo(correo)
        if not usuario or not self.hasher.verify(password, usuario.password_hash):
            raise ValueError('Credenciales invalidas')
        return self.jwt.create_token(usuario), usuario

    def get_usuario_from_payload(self, payload: dict):
        usuario = self.uow.usuarios.get_by_id(payload['sub'])
        if not usuario:
            raise ValueError('Usuario no encontrado')
        return usuario
