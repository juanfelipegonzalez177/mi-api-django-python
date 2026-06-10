from django.db import models

from domain.entities.compania import Compania


class Usuario(models.Model):
    ADMIN = 'ADMIN'
    USUARIO = 'USUARIO'

    ROLES = [
        (ADMIN, 'Admin'),
        (USUARIO, 'Usuario'),
    ]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, choices=ROLES, default=USUARIO)
    compania = models.ForeignKey(
        Compania,
        on_delete=models.SET_NULL,
        related_name='usuarios',
        null=True,
        blank=True,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios'
        managed = True

    def __str__(self):
        return f'{self.nombre} ({self.rol})'
