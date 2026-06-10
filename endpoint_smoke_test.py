import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from rest_framework.test import APIClient

from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from domain.entities.usuario import Usuario


client = APIClient()
prefix = f"codex_{int(time.time())}"
usuarios = []
companias = []
empleados = []
resultados = []


def auth(token):
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def check(nombre, response, esperados):
    ok = response.status_code in esperados
    resultados.append((nombre, response.status_code, sorted(esperados), ok))
    print(f"{'OK' if ok else 'FAIL'} | {response.status_code} | {nombre}", flush=True)
    if not ok:
        raise AssertionError(
            f"{nombre}: {response.status_code}, esperado {esperados}, "
            f"respuesta={getattr(response, 'data', None)}"
        )
    return response


try:
    admin = check(
        "POST /api/auth/registro/ admin",
        client.post(
            "/api/auth/registro/",
            {
                "nombre": "Admin Temporal",
                "correo": f"{prefix}_admin@test.com",
                "password": "Admin12345",
                "rol": "ADMIN",
            },
            format="json",
        ),
        {201},
    ).data
    usuarios.append(admin["id"])

    token_admin = check(
        "POST /api/auth/login/ admin",
        client.post(
            "/api/auth/login/",
            {"correo": f"{prefix}_admin@test.com", "password": "Admin12345"},
            format="json",
        ),
        {200},
    ).data["access"]
    admin_headers = auth(token_admin)

    check("GET /api/auth/perfil/", client.get("/api/auth/perfil/", **admin_headers), {200})
    check("GET /api/companias/ sin token", client.get("/api/companias/"), {401})

    compania = check(
        "POST /api/companias/",
        client.post(
            "/api/companias/",
            {
                "nombre": f"{prefix} Compania A",
                "direccion": "Calle 123",
                "telefono": "3000000000",
            },
            format="json",
            **admin_headers,
        ),
        {201},
    ).data
    companias.append(compania["id"])

    usuario = check(
        "POST /api/auth/registro/ usuario",
        client.post(
            "/api/auth/registro/",
            {
                "nombre": "Usuario Temporal",
                "correo": f"{prefix}_usuario@test.com",
                "password": "Usuario12345",
                "rol": "USUARIO",
                "compania_id": compania["id"],
            },
            format="json",
        ),
        {201},
    ).data
    usuarios.append(usuario["id"])

    token_usuario = check(
        "POST /api/auth/login/ usuario",
        client.post(
            "/api/auth/login/",
            {"correo": f"{prefix}_usuario@test.com", "password": "Usuario12345"},
            format="json",
        ),
        {200},
    ).data["access"]
    usuario_headers = auth(token_usuario)

    check("GET /api/companias/", client.get("/api/companias/", **admin_headers), {200})
    check(
        "GET /api/companias/{id}/",
        client.get(f"/api/companias/{compania['id']}/", **admin_headers),
        {200},
    )
    check(
        "PATCH /api/companias/{id}/",
        client.patch(
            f"/api/companias/{compania['id']}/",
            {"telefono": "3111111111"},
            format="json",
            **admin_headers,
        ),
        {200},
    )
    check(
        "PUT /api/companias/{id}/",
        client.put(
            f"/api/companias/{compania['id']}/",
            {
                "nombre": f"{prefix} Compania A Put",
                "direccion": "Carrera 45",
                "telefono": "3222222222",
            },
            format="json",
            **admin_headers,
        ),
        {200},
    )
    check(
        "DELETE /api/companias/{id}/ usuario",
        client.delete(f"/api/companias/{compania['id']}/", **usuario_headers),
        {403},
    )

    check(
        "POST /api/empleados/ invalido",
        client.post(
            "/api/empleados/",
            {
                "nombre": "",
                "apellido": "Bad",
                "correo": "correo-malo",
                "cargo": "QA",
                "salario": "-1",
                "compania_id": compania["id"],
            },
            format="json",
            **admin_headers,
        ),
        {422},
    )

    empleado = check(
        "POST /api/empleados/",
        client.post(
            "/api/empleados/",
            {
                "nombre": "Ana",
                "apellido": "Temporal",
                "correo": f"{prefix}_ana@test.com",
                "cargo": "QA",
                "salario": "2500000.00",
                "compania_id": compania["id"],
            },
            format="json",
            **admin_headers,
        ),
        {201},
    ).data
    empleados.append(empleado["id"])

    check(
        "GET /api/empleados/",
        client.get(f"/api/empleados/?buscar={prefix}", **admin_headers),
        {200},
    )
    check(
        "GET /api/empleados/{id}/",
        client.get(f"/api/empleados/{empleado['id']}/", **admin_headers),
        {200},
    )
    check(
        "GET /api/companias/{id}/empleados/",
        client.get(f"/api/companias/{compania['id']}/empleados/", **admin_headers),
        {200},
    )
    check(
        "PATCH /api/empleados/{id}/",
        client.patch(
            f"/api/empleados/{empleado['id']}/",
            {"cargo": "QA Senior"},
            format="json",
            **usuario_headers,
        ),
        {200},
    )
    check(
        "PATCH /api/empleados/{id}/ salario usuario",
        client.patch(
            f"/api/empleados/{empleado['id']}/",
            {"salario": "6000000.00"},
            format="json",
            **usuario_headers,
        ),
        {403},
    )
    check(
        "PUT /api/empleados/{id}/",
        client.put(
            f"/api/empleados/{empleado['id']}/",
            {
                "nombre": "Ana Maria",
                "apellido": "Temporal",
                "correo": f"{prefix}_ana_put@test.com",
                "cargo": "QA Lead",
                "salario": "3000000.00",
                "compania_id": compania["id"],
            },
            format="json",
            **admin_headers,
        ),
        {200},
    )

    bulk = check(
        "POST /api/empleados/bulk/",
        client.post(
            "/api/empleados/bulk/",
            {
                "empleados": [
                    {
                        "nombre": "Bulk1",
                        "apellido": "Temporal",
                        "correo": f"{prefix}_bulk1@test.com",
                        "cargo": "Dev",
                        "salario": "2000000.00",
                        "compania_id": compania["id"],
                    },
                    {
                        "nombre": "Bulk2",
                        "apellido": "Temporal",
                        "correo": f"{prefix}_bulk2@test.com",
                        "cargo": "Dev",
                        "salario": "2100000.00",
                        "compania_id": compania["id"],
                    },
                ]
            },
            format="json",
            **admin_headers,
        ),
        {201},
    ).data
    bulk_ids = [item["id"] for item in bulk]
    empleados.extend(bulk_ids)

    check(
        "DELETE /api/empleados/bulk-delete/",
        client.delete(
            "/api/empleados/bulk-delete/",
            {"ids": bulk_ids},
            format="json",
            **admin_headers,
        ),
        {200},
    )
    empleados = [empleado_id for empleado_id in empleados if empleado_id not in bulk_ids]

    compania_con_empleados = check(
        "POST /api/companias/con-empleados/",
        client.post(
            "/api/companias/con-empleados/",
            {
                "nombre": f"{prefix} Compania B",
                "direccion": "Av 10",
                "telefono": "3333333333",
                "empleados": [
                    {
                        "nombre": "Trans1",
                        "apellido": "Temporal",
                        "correo": f"{prefix}_trans1@test.com",
                        "cargo": "Dev",
                        "salario": "2300000.00",
                    },
                    {
                        "nombre": "Trans2",
                        "apellido": "Temporal",
                        "correo": f"{prefix}_trans2@test.com",
                        "cargo": "QA",
                        "salario": "2400000.00",
                    },
                ],
            },
            format="json",
            **admin_headers,
        ),
        {201},
    ).data
    companias.append(compania_con_empleados["id"])

    check(
        "DELETE /api/empleados/{id}/",
        client.delete(f"/api/empleados/{empleado['id']}/", **admin_headers),
        {204},
    )
    empleados = [empleado_id for empleado_id in empleados if empleado_id != empleado["id"]]

    for compania_id in list(companias):
        check(
            f"DELETE /api/companias/{compania_id}/",
            client.delete(f"/api/companias/{compania_id}/", **admin_headers),
            {204},
        )
        companias.remove(compania_id)
finally:
    Empleado.objects.filter(id__in=empleados).delete()
    Compania.objects.filter(id__in=companias).delete()
    Usuario.objects.filter(id__in=usuarios).delete()

print(f"TOTAL_OK {sum(1 for item in resultados if item[3])} DE {len(resultados)}", flush=True)
print(
    "TEMPORALES_RESTANTES",
    Compania.objects.filter(nombre__startswith="codex_").count(),
    Empleado.objects.filter(correo__startswith="codex_").count(),
    Usuario.objects.filter(correo__startswith="codex_").count(),
    flush=True,
)
