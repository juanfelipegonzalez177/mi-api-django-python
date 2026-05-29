import inspect

from api.controllers.companias_controller import CompaniaConEmpleadosView, CompaniaDetailView, CompaniasView
from api.controllers.empleados_controller import EmpleadoDetailView, EmpleadosPorCompaniaView, EmpleadosView
from django.test import TestCase
from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from rest_framework.test import APIClient


class ApiEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.compania = Compania.objects.create(
            nombre='Tech SAS',
            direccion='Calle 1',
            telefono='3001111111',
        )
        self.empleado = Empleado.objects.create(
            nombre='Ana',
            apellido='Gomez',
            correo='ana@example.com',
            cargo='QA',
            salario=2500000,
            compania=self.compania,
        )

    def test_companias_crud(self):
        list_response = self.client.get('/api/companias/')
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)

        create_response = self.client.post('/api/companias/', {
            'nombre': 'Innova SAS',
            'direccion': 'Calle 2',
            'telefono': '3002222222',
        }, format='json')
        self.assertEqual(create_response.status_code, 201)
        compania_id = create_response.data['id']

        detail_response = self.client.get(f'/api/companias/{compania_id}/')
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data['nombre'], 'Innova SAS')

        update_response = self.client.put(f'/api/companias/{compania_id}/', {
            'nombre': 'Innova Actualizada',
            'direccion': 'Calle 3',
            'telefono': '3003333333',
        }, format='json')
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data['nombre'], 'Innova Actualizada')

        delete_response = self.client.delete(f'/api/companias/{compania_id}/')
        self.assertEqual(delete_response.status_code, 204)

    def test_empleados_crud(self):
        create_response = self.client.post('/api/empleados/', {
            'nombre': 'Luis',
            'apellido': 'Perez',
            'correo': 'luis@example.com',
            'cargo': 'Developer',
            'salario': '2800000.00',
            'compania_id': self.compania.id,
        }, format='json')
        self.assertEqual(create_response.status_code, 201)
        empleado_id = create_response.data['id']

        list_response = self.client.get('/api/empleados/')
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 2)

        detail_response = self.client.get(f'/api/empleados/{empleado_id}/')
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data['correo'], 'luis@example.com')

        update_response = self.client.put(f'/api/empleados/{empleado_id}/', {
            'nombre': 'Luis',
            'apellido': 'Perez',
            'correo': 'luis.actualizado@example.com',
            'cargo': 'Lead Developer',
            'salario': '3000000.00',
            'compania_id': self.compania.id,
        }, format='json')
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data['cargo'], 'Lead Developer')

        delete_response = self.client.delete(f'/api/empleados/{empleado_id}/')
        self.assertEqual(delete_response.status_code, 204)

    def test_empleados_por_compania(self):
        response = self.client.get(f'/api/companias/{self.compania.id}/empleados/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['correo'], 'ana@example.com')

    def test_validacion_rechaza_compania_inexistente_en_empleado(self):
        response = self.client.post('/api/empleados/', {
            'nombre': 'Carlos',
            'apellido': 'Ruiz',
            'correo': 'carlos@example.com',
            'cargo': 'Designer',
            'salario': '2200000.00',
            'compania_id': 99999,
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Empleado.objects.count(), 1)

    def test_crear_compania_con_empleados_hace_rollback_si_falla_un_empleado(self):
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
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Compania.objects.filter(nombre='Rollback SAS').exists())
        self.assertFalse(Empleado.objects.filter(correo='duplicado@example.com').exists())


class ProjectModeTests(TestCase):
    def test_views_are_synchronous(self):
        views = [
            CompaniasView.get,
            CompaniasView.post,
            CompaniaDetailView.get,
            CompaniaDetailView.put,
            CompaniaDetailView.delete,
            CompaniaConEmpleadosView.post,
            EmpleadosView.get,
            EmpleadosView.post,
            EmpleadoDetailView.get,
            EmpleadoDetailView.put,
            EmpleadoDetailView.delete,
            EmpleadosPorCompaniaView.get,
        ]

        for view in views:
            self.assertFalse(inspect.iscoroutinefunction(view))
