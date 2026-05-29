from domain.entities.usuario import Usuario
from domain.interfaces.usuario_repository import AbstractUsuarioRepository


class UsuarioRepository(AbstractUsuarioRepository):
    def get_by_id(self, id):
        return Usuario.objects.filter(pk=id).first()

    def get_by_correo(self, correo):
        return Usuario.objects.filter(correo=correo).first()

    def create(self, data: dict):
        return Usuario(**data)
