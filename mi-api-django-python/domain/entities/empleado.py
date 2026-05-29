from django.db import models
from domain.entities.compania import Compania

class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    cargo = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=12, decimal_places=2)
    compania = models.ForeignKey(
        Compania,
        on_delete=models.CASCADE,
        related_name='empleados'
    )

    class Meta:
        db_table = 'empleados'
        managed = True

    def __str__(self):
        return f"{self.nombre} {self.apellido}"