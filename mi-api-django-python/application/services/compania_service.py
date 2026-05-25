import logging
from infrastructure.unit_of_work.django_unit_of_work import DjangoUnitOfWork

logger = logging.getLogger(__name__)

class CompaniaService:
    def __init__(self):
        self.uow = DjangoUnitOfWork()

    def get_all(self):
        return list(self.uow.companias.get_all())

    def get_by_id(self, id):
        return self.uow.companias.get_by_id(id)

    def create(self, data: dict):
        with self.uow:
            compania = self.uow.companias.create(data)
            compania.save()
            logger.info(f"Compañía creada: {compania.nombre}")
            return compania

    def update(self, id, data: dict):
        with self.uow:
            compania = self.uow.companias.get_by_id(id)
            if not compania:
                raise ValueError("Compañía no encontrada")
            updated = self.uow.companias.update(compania, data)
            updated.save()
            return updated

    def delete(self, id):
        with self.uow:
            compania = self.uow.companias.get_by_id(id)
            if not compania:
                raise ValueError("Compañía no encontrada")
            self.uow.companias.delete(compania)

    def create_con_empleados(self, data: dict):
        with self.uow:
            compania = self.uow.companias.create({
                'nombre': data['nombre'],
                'direccion': data['direccion'],
                'telefono': data['telefono'],
            })
            compania.save()
            logger.info(f"Compañía creada con empleados: {compania.nombre}")
            for emp_data in data['empleados']:
                empleado = self.uow.empleados.create({
                    **emp_data,
                    'compania': compania
                })
                empleado.save()
                logger.info(f"Empleado creado: {empleado.nombre}")
            return compania
