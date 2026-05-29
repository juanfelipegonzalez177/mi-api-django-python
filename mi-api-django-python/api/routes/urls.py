from django.urls import path
from api.controllers.companias_controller import CompaniasView, CompaniaDetailView, CompaniaConEmpleadosView
from api.controllers.empleados_controller import EmpleadosView, EmpleadoDetailView, EmpleadosPorCompaniaView

urlpatterns = [
    path('api/companias/', CompaniasView.as_view()),
    path('api/companias/con-empleados/', CompaniaConEmpleadosView.as_view()),
    path('api/companias/<int:id>/', CompaniaDetailView.as_view()),
    path('api/companias/<int:id>/empleados/', EmpleadosPorCompaniaView.as_view()),
    path('api/empleados/', EmpleadosView.as_view()),
    path('api/empleados/<int:id>/', EmpleadoDetailView.as_view()),
]
