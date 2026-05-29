from django.urls import path
from api.controllers.auth_controller import LoginView, PerfilView, RegistroView
from api.controllers.companias_controller import CompaniasView, CompaniaDetailView, CompaniaConEmpleadosView
from api.controllers.empleados_controller import EmpleadoBulkDeleteView, EmpleadoBulkView, EmpleadosView, EmpleadoDetailView, EmpleadosPorCompaniaView

urlpatterns = [
    path('api/auth/registro/', RegistroView.as_view()),
    path('api/auth/login/', LoginView.as_view()),
    path('api/auth/perfil/', PerfilView.as_view()),
    path('api/companias/', CompaniasView.as_view()),
    path('api/companias/con-empleados/', CompaniaConEmpleadosView.as_view()),
    path('api/companias/<int:id>/', CompaniaDetailView.as_view()),
    path('api/companias/<int:id>/empleados/', EmpleadosPorCompaniaView.as_view()),
    path('api/empleados/', EmpleadosView.as_view()),
    path('api/empleados/bulk/', EmpleadoBulkView.as_view()),
    path('api/empleados/bulk-delete/', EmpleadoBulkDeleteView.as_view()),
    path('api/empleados/<int:id>/', EmpleadoDetailView.as_view()),
]
