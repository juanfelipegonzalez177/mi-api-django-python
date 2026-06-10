import logging
from infrastructure.unit_of_work.django_unit_of_work import DjangoUnitOfWork

logger = logging.getLogger(__name__)

class EmpleadoService:
    def __init__(self):
        self.uow = DjangoUnitOfWork()

    def get_all(self):
        return list(self.uow.empleados.get_all())

    def list_paginated(self, params: dict):
        pagina = max(int(params.get('pagina', 1)), 1)
        tamano = min(max(int(params.get('tamano', 10)), 1), 100)
        queryset = self.uow.empleados.list_filtered(
            buscar=params.get('buscar'),
            orden=params.get('orden', 'id'),
            direccion=params.get('dir', 'asc'),
            compania_id=params.get('compania_id'),
        )
        total = queryset.count()
        inicio = (pagina - 1) * tamano
        fin = inicio + tamano
        return {
            'datos': list(queryset[inicio:fin]),
            'pagina': pagina,
            'tamano': tamano,
            'total': total,
            'paginas': (total + tamano - 1) // tamano,
        }

    def get_by_id(self, id):
        return self.uow.empleados.get_by_id(id)

    def get_by_compania(self, compania_id):
        return list(self.uow.empleados.find_by_compania(compania_id))

    def create(self, data: dict):
        with self.uow:
            if not self.uow.companias.get_by_id(data['compania_id']):
                raise ValueError("Compania no encontrada")
            empleado = self.uow.empleados.create(data)
            empleado.save()
            logger.info(f"Empleado creado: {empleado.nombre}")
            return empleado

    def bulk_create(self, empleados_data: list):
        with self.uow:
            empleados = []
            correos = [empleado['correo'] for empleado in empleados_data]
            if len(correos) != len(set(correos)):
                raise ValueError("Hay correos duplicados en la solicitud")
            for data in empleados_data:
                if not self.uow.companias.get_by_id(data['compania_id']):
                    raise ValueError("Compania no encontrada")
                if self.uow.empleados.get_by_correo(data['correo']):
                    raise ValueError("El correo ya existe")
                empleado = self.uow.empleados.create(data)
                empleado.save()
                empleados.append(empleado)
            return empleados

    def update(self, id, data: dict):
        with self.uow:
            empleado = self.uow.empleados.get_by_id(id)
            if not empleado:
                raise ValueError("Empleado no encontrado")
            if not self.uow.companias.get_by_id(data['compania_id']):
                raise ValueError("Compania no encontrada")
            updated = self.uow.empleados.update(empleado, data)
            updated.save()
            return updated

    def patch(self, id, data: dict):
        with self.uow:
            empleado = self.uow.empleados.get_by_id(id)
            if not empleado:
                raise ValueError("Empleado no encontrado")
            if 'compania_id' in data and not self.uow.companias.get_by_id(data['compania_id']):
                raise ValueError("Compania no encontrada")
            updated = self.uow.empleados.update(empleado, data)
            updated.save()
            return updated

    def delete_many(self, ids: list):
        with self.uow:
            empleados = [self.uow.empleados.get_by_id(id) for id in ids]
            if any(empleado is None for empleado in empleados):
                raise ValueError("Uno o mas empleados no existen")
            for empleado in empleados:
                self.uow.empleados.delete(empleado)
            return len(empleados)

    def delete(self, id):
        with self.uow:
            empleado = self.uow.empleados.get_by_id(id)
            if not empleado:
                raise ValueError("Empleado no encontrado")
            self.uow.empleados.delete(empleado)
