from domain.entities.compania import Compania
from domain.interfaces.compania_repository import AbstractCompaniaRepository
from django.db.models import Q


class CompaniaRepository(AbstractCompaniaRepository):
    def get_all(self):
        return Compania.objects.all()

    def list_filtered(self, buscar=None, orden='id', direccion='asc'):
        campos_orden = {'id', 'nombre', 'direccion', 'telefono', 'fecha_creacion'}
        queryset = Compania.objects.all()
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(direccion__icontains=buscar) |
                Q(telefono__icontains=buscar)
            )
        orden = orden if orden in campos_orden else 'id'
        if direccion == 'desc':
            orden = f'-{orden}'
        return queryset.order_by(orden)

    def get_by_id(self, id):
        return Compania.objects.filter(pk=id).first()

    def create(self, data: dict):
        return Compania(**data)

    def update(self, instance, data: dict):
        for key, value in data.items():
            setattr(instance, key, value)
        return instance

    def delete(self, instance):
        instance.delete()

    def find_by_condition(self, **kwargs):
        return Compania.objects.filter(**kwargs)
