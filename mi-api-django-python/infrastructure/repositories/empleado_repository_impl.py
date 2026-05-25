from domain.entities.empleado import Empleado

class EmpleadoRepository:
    def get_all(self):
        return Empleado.objects.select_related('compania').all()

    def get_by_id(self, id):
        return Empleado.objects.filter(pk=id).first()

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
