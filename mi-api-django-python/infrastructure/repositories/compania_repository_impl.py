from domain.entities.compania import Compania

class CompaniaRepository:
    def get_all(self):
        return Compania.objects.all()

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
