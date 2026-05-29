import logging
from infrastructure.unit_of_work.django_unit_of_work import DjangoUnitOfWork

logger = logging.getLogger(__name__)

class CompaniaService:
    def __init__(self):
        self.uow = DjangoUnitOfWork()

    def get_all(self):
        return list(self.uow.companias.get_all())

    def list_paginated(self, params: dict):
        pagina = max(int(params.get('pagina', 1)), 1)
        tamano = min(max(int(params.get('tamano', 10)), 1), 100)
        queryset = self.uow.companias.list_filtered(
            buscar=params.get('buscar'),
            orden=params.get('orden', 'id'),
            direccion=params.get('dir', 'asc'),
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

    def patch(self, id, data: dict):
        with self.uow:
            compania = self.uow.companias.get_by_id(id)
            if not compania:
                raise ValueError("Compania no encontrada")
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
