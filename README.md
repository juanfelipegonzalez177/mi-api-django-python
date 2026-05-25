# API REST - Companias y Empleados
## Django + Onion Architecture

---

## Tecnología usada
- Python 3.11
- Django 5.2
- Django REST Framework
- PostgreSQL
- drf-yasg (Swagger)

---

## Arquitectura
Este proyecto implementa **Onion Architecture** con las siguientes capas:

//Controller → Service → UnitOfWork → Repository → ORM///
### Capas:
- `domain/` — Entidades del negocio (Compania, Empleado)
- `application/` — Servicios y DTOs
- `infrastructure/` — Repositorios y Unit of Work
- `api/` — Controladores y rutas

---

## ORM usado
Django ORM con soporte para transacciones atómicas mediante `transaction.atomic()`

---

## Instalación

```bash
# Clonar el repositorio
git clone <url>

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Cargar datos iniciales
python manage.py shell
>>> from infrastructure.database.seed_data import run
>>> run()

# Correr servidor
python manage.py runserver
```

---

## Endpoints

### Compañías
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /api/companias/ | Listar todas |
| GET | /api/companias/{id}/ | Obtener por ID |
| POST | /api/companias/ | Crear compañía |
| PUT | /api/companias/{id}/ | Actualizar compañía |
| DELETE | /api/companias/{id}/ | Eliminar compañía |
| GET | /api/companias/{id}/empleados/ | Empleados de una compañía |
| POST | /api/companias/con-empleados/ | Crear compañía con empleados (transaccional) |

### Empleados
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /api/empleados/ | Listar todos |
| GET | /api/empleados/{id}/ | Obtener por ID |
| POST | /api/empleados/ | Crear empleado |
| PUT | /api/empleados/{id}/ | Actualizar empleado |
| DELETE | /api/empleados/{id}/ | Eliminar empleado |

---

## Unit of Work
Se implementó `AbstractUnitOfWork` y `DjangoUnitOfWork` usando `transaction.atomic()` de Django.

Garantiza que si una operación falla dentro de una transacción, se hace **rollback** de todos los cambios.

---

## Logging
El proyecto registra en `app.log`:
- Creación de entidades
- Transacciones exitosas
- Errores
- Rollbacks

---

## Swagger
Documentación interactiva disponible en:http://127.0.0.1:8000/swagger/

---

## Prueba de Rollback
Se puede demostrar enviando dos empleados con el mismo correo al endpoint transaccional:

```json
POST /api/companias/con-empleados/
{
  "nombre": "Tech SAS",
  "direccion": "Calle 1",
  "telefono": "3000000000",
  "empleados": [
    {"nombre": "Juan", "apellido": "Perez", "correo": "repetido@mail.com", "cargo": "Dev", "salario": 2000000},
    {"nombre": "Ana", "apellido": "Gomez", "correo": "repetido@mail.com", "cargo": "QA", "salario": 2500000}
  ]
}
```

Si falla un empleado, no se guarda ni la compañía ni ningún empleado.

---

## Uso de IA
Se utilizó inteligencia artificial (Claude) como apoyo para:
- Revisión de arquitectura
- Generación de código base
- Corrección de errores
- Documentación