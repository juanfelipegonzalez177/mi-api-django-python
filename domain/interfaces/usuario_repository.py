from abc import ABC, abstractmethod


class AbstractUsuarioRepository(ABC):
    @abstractmethod
    def get_by_id(self, id): ...

    @abstractmethod
    def get_by_correo(self, correo): ...

    @abstractmethod
    def create(self, data: dict): ...
