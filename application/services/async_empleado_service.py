from domain.entities.empleado import Empleado


class AsyncEmpleadoReadService:
    async def get_by_id(self, id):
        return await Empleado.objects.select_related('compania').filter(pk=id).afirst()

    async def list_by_compania(self, compania_id):
        queryset = Empleado.objects.filter(compania_id=compania_id).order_by('apellido')
        return [empleado async for empleado in queryset]
