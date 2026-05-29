# API REST - Parte II

Proyecto Django + Django REST Framework con Onion Architecture, Repository Pattern y Unit of Work.

Esta entrega continua la API de companias y empleados agregando CRUD de colecciones, validaciones, pruebas, seguridad JWT por roles y autorizacion por politicas.

## Arquitectura

Flujo principal:

```text
Controller / Route -> Service -> Unit of Work -> Repository -> ORM -> DB
```

Capas:

- `domain/`: entidades, interfaces y reglas del dominio.
- `application/`: servicios, DTOs y casos de uso.
- `infrastructure/`: repositorios, Unit of Work, JWT y hashing.
- `api/`: controladores, rutas, seguridad HTTP y respuestas.

## CRUD de colecciones

Endpoints principales:

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/api/empleados/` | Listado paginado, filtrado y ordenado |
| `POST` | `/api/empleados/bulk/` | Creacion masiva de empleados en una transaccion |
| `PATCH` | `/api/empleados/{id}/` | Actualizacion parcial |
| `DELETE` | `/api/empleados/bulk-delete/` | Eliminacion multiple por ids |
| `POST` | `/api/companias/con-empleados/` | Caso transaccional compania + empleados |

### Paginacion, filtrado y ordenamiento

Ejemplo:

```http
GET /api/empleados/?pagina=1&tamano=10&orden=apellido&dir=asc&buscar=gomez
```

Respuesta:

```json
{
  "datos": [],
  "pagina": 1,
  "tamano": 10,
  "total": 0,
  "paginas": 0
}
```

## Programacion asincrona

### Mi tecnologia soporta async

Django soporta vistas async y metodos async del ORM (`aget`, `afirst`, iteracion async). Sin embargo, Django REST Framework sigue siendo mas comun en modo sincronico para `APIView`, por eso la API HTTP principal se mantiene sincronica y se deja evidencia de lectura asincrona en:

```text
application/services/async_empleado_service.py
```

Esta decision evita mezclar un controlador DRF sincronico con operaciones async de forma insegura. En una migracion completa a async se recomendaria usar vistas Django async puras o una capa ASGI compatible de extremo a extremo.

## Validaciones

Se usan serializers de DRF en la capa `application/dtos`.

Reglas:

- Campos obligatorios.
- Longitudes maximas.
- Correo valido.
- Salario mayor o igual a cero.
- Existencia de compania antes de crear/actualizar empleados.
- Correo unico para creacion masiva.

Formato uniforme de error:

```json
{
  "mensaje": "Error de validacion",
  "errores": [
    {"campo": "correo", "detalle": "Enter a valid email address."}
  ]
}
```

## Pruebas

Comando:

```bash
python manage.py test
```

La configuracion usa SQLite en memoria durante pruebas para no tocar la base PostgreSQL real.

Pruebas cubiertas:

- Registro, login y perfil con JWT.
- Listado paginado, filtrado y ordenado.
- Creacion masiva, PATCH y eliminacion multiple.
- Roles `ADMIN` y `USUARIO`.
- Politica `EsPropietarioDeCompania`.
- Validacion con respuesta `422`.
- Rollback transaccional cuando falla un empleado.
- Evidencia de servicio async.

Resultado verificado:

```text
Ran 7 tests
OK
```

## Seguridad

### Autenticacion con JWT

Endpoints:

| Metodo | Ruta | Proteccion |
|---|---|---|
| `POST` | `/api/auth/registro/` | Publica |
| `POST` | `/api/auth/login/` | Publica |
| `GET` | `/api/auth/perfil/` | Requiere token |

El token incluye claims:

```json
{
  "sub": 1,
  "correo": "admin@mail.com",
  "rol": "ADMIN",
  "compania_id": 1,
  "exp": 1735689600
}
```

La contrasena se guarda con hash usando los hashers de Django, nunca en texto plano.

### Autorizacion por roles

- `GET`: `ADMIN` o `USUARIO`.
- `POST`, `PUT`, `PATCH`: `ADMIN` o `USUARIO`.
- `DELETE` de companias: solo `ADMIN`.
- `POST /api/companias/con-empleados/`: solo `ADMIN`.
- Bulk create/delete de empleados: solo `ADMIN`.

### Autorizacion por politicas

Politica implementada:

```text
EsPropietarioDeCompania
```

Regla:

- `ADMIN` puede modificar cualquier empleado.
- `USUARIO` solo puede modificar empleados cuyo `compania_id` coincide con el `compania_id` del token.

Tambien se implementa `LimiteSalario`:

- Solo `ADMIN` puede asignar salarios mayores a `5.000.000`.

## Variables de entorno

Ver `.env.example`.

Variables principales:

- `SECRET_KEY`
- `JWT_SECRET`
- `JWT_EXP_MINUTES`
- `DB_ENGINE`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

## Comparacion ampliada con ASP.NET Core

| Concepto en ASP.NET Core | Equivalente en Django |
|---|---|
| Endpoints de coleccion (`IEnumerable/List`) | `APIView` devolviendo listas o envelope paginado |
| Paginacion (`Skip/Take`) | Slicing de `QuerySet`: `[inicio:fin]` |
| `async/await + Task<T>` | Vistas async y ORM async (`aget`, `afirst`) |
| DataAnnotations / FluentValidation | Serializers de DRF |
| xUnit / NUnit + Moq | `django.test.TestCase` + `APIClient` |
| `AddAuthentication().AddJwtBearer()` | Servicio JWT + validacion de `Authorization: Bearer` |
| `[Authorize(Roles="...")]` | `require_roles()` en capa API |
| `[Authorize(Policy="...")] + IAuthorizationHandler` | `can_modify_empleado()` como policy handler |
| `ClaimsPrincipal / Claims` | Payload JWT: `sub`, `correo`, `rol`, `compania_id`, `exp` |

## Conclusiones de la Parte II

La API queda mas cercana a un escenario productivo: no solo hace CRUD individual, sino operaciones sobre colecciones, valida entradas, protege endpoints sensibles, prueba el rollback del Unit of Work y aplica autorizacion por roles y por politicas sin romper Onion Architecture.
