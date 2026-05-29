from domain.entities.empleado import Empleado
from domain.interfaces.empleado_repository import AbstractEmpleadoRepository
from django.db.models import Q


class EmpleadoRepository(AbstractEmpleadoRepository):
    def get_all(self):
        return Empleado.objects.select_related('compania').all()

    def list_filtered(self, buscar=None, orden='id', direccion='asc', compania_id=None):
        campos_orden = {'id', 'nombre', 'apellido', 'correo', 'cargo', 'salario', 'compania_id'}
        queryset = Empleado.objects.select_related('compania').all()
        if compania_id:
            queryset = queryset.filter(compania_id=compania_id)
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(apellido__icontains=buscar) |
                Q(correo__icontains=buscar) |
                Q(cargo__icontains=buscar)
            )
        orden = orden if orden in campos_orden else 'id'
        if direccion == 'desc':
            orden = f'-{orden}'
        return queryset.order_by(orden)

    def get_by_id(self, id):
        return Empleado.objects.filter(pk=id).first()

    def get_by_correo(self, correo):
        return Empleado.objects.filter(correo=correo).first()

    def create(self, data: dict):
        return Empleado(**data)

    def update(self, instance, data: dict):
        for key, value in data.items():
            setattr(instance, key, value)
        return instance

    def delete(self, instance):
        instance.delete()

    def find_by_compania(self, compania_id):
        return Empleado.objects.filter(compania_id=compania_id)
