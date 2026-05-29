from django.db import models

class Compania(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=300)
    telefono = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'companias'
        managed = True

    def __str__(self):
        return self.nombre