import logging
from infrastructure.unit_of_work.django_unit_of_work import DjangoUnitOfWork

logger = logging.getLogger(__name__)

class EmpleadoService:
    def __init__(self):
        self.uow = DjangoUnitOfWork()

    def get_all(self):
        return list(self.uow.empleados.get_all())

    def get_by_id(self, id):
        return self.uow.empleados.get_by_id(id)

    def get_by_compania(self, compania_id):
        return list(self.uow.empleados.find_by_compania(compania_id))

    def create(self, data: dict):
        with self.uow:
            empleado = self.uow.empleados.create(data)
            empleado.save()
            logger.info(f"Empleado creado: {empleado.nombre}")
            return empleado

    def update(self, id, data: dict):
        with self.uow:
            empleado = self.uow.empleados.get_by_id(id)
            if not empleado:
                raise ValueError("Empleado no encontrado")
            updated = self.uow.empleados.update(empleado, data)
            updated.save()
            return updated

    def delete(self, id):
        with self.uow:
            empleado = self.uow.empleados.get_by_id(id)
            if not empleado:
                raise ValueError("Empleado no encontrado")
            self.uow.empleados.delete(empleado)
