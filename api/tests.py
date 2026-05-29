import inspect

from application.services.async_empleado_service import AsyncEmpleadoReadService
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from domain.entities.usuario import Usuario
from infrastructure.security.jwt_service import JwtService
from rest_framework.test import APIClient


class ApiParteIITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.compania = Compania.objects.create(
            nombre='Tech SAS',
            direccion='Calle 1',
            telefono='3001111111',
        )
        self.otra_compania = Compania.objects.create(
            nombre='Otra SAS',
            direccion='Calle 2',
            telefono='3002222222',
        )
        self.admin = Usuario.objects.create(
            nombre='Admin',
            correo='admin@test.com',
            password_hash=make_password('Admin12345'),
            rol='ADMIN',
            compania=self.compania,
        )
        self.usuario = Usuario.objects.create(
            nombre='Usuario',
            correo='usuario@test.com',
            password_hash=make_password('Usuario12345'),
            rol='USUARIO',
            compania=self.compania,
        )
        self.otro_usuario = Usuario.objects.create(
            nombre='Otro',
            correo='otro@test.com',
            password_hash=make_password('Usuario12345'),
            rol='USUARIO',
            compania=self.otra_compania,
        )
        self.empleado = Empleado.objects.create(
            nombre='Ana',
            apellido='Gomez',
            correo='ana@example.com',
            cargo='QA',
            salario=2500000,
            compania=self.compania,
        )
        self.otro_empleado = Empleado.objects.create(
            nombre='Luis',
            apellido='Perez',
            correo='luis@example.com',
            cargo='Dev',
            salario=2800000,
            compania=self.otra_compania,
        )

    def auth(self, usuario):
        token = JwtService().create_token(usuario)
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_auth_registro_login_y_perfil(self):
        response = self.client.post('/api/auth/registro/', {
            'nombre': 'Nuevo',
            'correo': 'nuevo@test.com',
            'password': 'Nuevo12345',
            'rol': 'USUARIO',
            'compania_id': self.compania.id,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(Usuario.objects.get(correo='nuevo@test.com').password_hash, 'Nuevo12345')

        login = self.client.post('/api/auth/login/', {
            'correo': 'nuevo@test.com',
            'password': 'Nuevo12345',
        }, format='json')
        self.assertEqual(login.status_code, 200)
        self.assertIn('access', login.data)

        perfil = self.client.get('/api/auth/perfil/', HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        self.assertEqual(perfil.status_code, 200)
        self.assertEqual(perfil.data['correo'], 'nuevo@test.com')

    def test_listado_paginado_filtrado_y_ordenado(self):
        response = self.client.get(
            '/api/empleados/?pagina=1&tamano=1&orden=apellido&dir=asc&buscar=gomez',
            **self.auth(self.admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['datos'][0]['apellido'], 'Gomez')

    def test_bulk_patch_y_delete_multiple(self):
        bulk = self.client.post('/api/empleados/bulk/', {
            'empleados': [
                {
                    'nombre': 'Carlos',
                    'apellido': 'Ruiz',
                    'correo': 'carlos@example.com',
                    'cargo': 'Designer',
                    'salario': '2200000.00',
                    'compania_id': self.compania.id,
                },
                {
                    'nombre': 'Sofia',
                    'apellido': 'Mora',
                    'correo': 'sofia@example.com',
                    'cargo': 'PM',
                    'salario': '3000000.00',
                    'compania_id': self.compania.id,
                },
            ],
        }, format='json', **self.auth(self.admin))
        self.assertEqual(bulk.status_code, 201)
        ids = [empleado['id'] for empleado in bulk.data]

        patch = self.client.patch(
            f'/api/empleados/{ids[0]}/',
            {'cargo': 'Lead Designer'},
            format='json',
            **self.auth(self.admin),
        )
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.data['cargo'], 'Lead Designer')

        delete_many = self.client.delete(
            '/api/empleados/bulk-delete/',
            {'ids': ids},
            format='json',
            **self.auth(self.admin),
        )
        self.assertEqual(delete_many.status_code, 200)
        self.assertEqual(delete_many.data['eliminados'], 2)

    def test_roles_y_politica_de_propiedad(self):
        sin_token = self.client.get('/api/empleados/')
        self.assertEqual(sin_token.status_code, 401)

        delete_compania = self.client.delete(f'/api/companias/{self.compania.id}/', **self.auth(self.usuario))
        self.assertEqual(delete_compania.status_code, 403)

        propio = self.client.patch(
            f'/api/empleados/{self.empleado.id}/',
            {'cargo': 'QA Senior'},
            format='json',
            **self.auth(self.usuario),
        )
        self.assertEqual(propio.status_code, 200)

        ajeno = self.client.patch(
            f'/api/empleados/{self.otro_empleado.id}/',
            {'cargo': 'QA Senior'},
            format='json',
            **self.auth(self.usuario),
        )
        self.assertEqual(ajeno.status_code, 403)

    def test_validacion_estandarizada(self):
        response = self.client.post('/api/empleados/', {
            'nombre': '',
            'apellido': 'Ruiz',
            'correo': 'correo-malo',
            'cargo': 'Designer',
            'salario': '-1',
            'compania_id': self.compania.id,
        }, format='json', **self.auth(self.admin))
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data['mensaje'], 'Error de validacion')
        self.assertGreaterEqual(len(response.data['errores']), 2)

    def test_rollback_transaccional(self):
        response = self.client.post('/api/companias/con-empleados/', {
            'nombre': 'Rollback SAS',
            'direccion': 'Calle 9',
            'telefono': '3009999999',
            'empleados': [
                {
                    'nombre': 'Uno',
                    'apellido': 'Prueba',
                    'correo': 'duplicado@example.com',
                    'cargo': 'Dev',
                    'salario': '2000000.00',
                },
                {
                    'nombre': 'Dos',
                    'apellido': 'Prueba',
                    'correo': 'duplicado@example.com',
                    'cargo': 'QA',
                    'salario': '2100000.00',
                },
            ],
        }, format='json', **self.auth(self.admin))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Compania.objects.filter(nombre='Rollback SAS').exists())
        self.assertFalse(Empleado.objects.filter(correo='duplicado@example.com').exists())

    def test_evidencia_servicio_async(self):
        self.assertTrue(inspect.iscoroutinefunction(AsyncEmpleadoReadService.get_by_id))
        self.assertTrue(inspect.iscoroutinefunction(AsyncEmpleadoReadService.list_by_compania))
