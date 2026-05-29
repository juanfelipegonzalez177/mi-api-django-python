# Evidencia de uso de IA - Parte II

## Prompt 7 - CRUD de colecciones

Consulta: como agregar bulk insert, PATCH, eliminacion multiple, paginacion, filtrado y ordenamiento en Django REST Framework respetando Onion Architecture y Unit of Work.

Aplicacion: se agregaron endpoints `/api/empleados/bulk/`, `/api/empleados/bulk-delete/`, `PATCH /api/empleados/{id}/` y listados con envelope paginado.

## Prompt 8 - Programacion asincrona

Consulta: si Django con Django ORM es sincronico o asincronico y como manejar async con Unit of Work.

Aplicacion: se documento que DRF `APIView` se mantiene sincronico en esta solucion, y se agrego evidencia de servicio async con ORM async en `application/services/async_empleado_service.py`.

## Prompt 9 - Validaciones

Consulta: mecanismo recomendado en Django/DRF para validar DTOs.

Aplicacion: serializers DRF en `application/dtos`, con respuesta uniforme `422`.

## Prompt 10 - Pruebas

Consulta: pruebas unitarias e integracion en Django.

Aplicacion: `django.test.TestCase` y `APIClient`, con 7 pruebas cubriendo endpoints, seguridad, validacion y rollback.

## Prompt 11 - JWT por roles

Consulta: implementar registro, login, JWT y proteccion por roles en Django.

Aplicacion: entidad `Usuario`, hash de contrasena, token JWT y `require_roles()`.

## Prompt 12 - JWT por politicas

Consulta: diferencia entre roles y policies, y como aplicar ownership.

Aplicacion: politica `EsPropietarioDeCompania`, donde un usuario solo modifica empleados de su propia compania; `ADMIN` queda exento.
