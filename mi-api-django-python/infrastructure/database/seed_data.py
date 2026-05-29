from domain.entities.compania import Compania
from domain.entities.empleado import Empleado


def run():
    # Limpiar datos previos
    Empleado.objects.all().delete()
    Compania.objects.all().delete()

    # Crear 3 compañías
    c1 = Compania.objects.create(
        nombre="Tech Solutions",
        direccion="Calle 1",
        telefono="3001111111"
    )
    c2 = Compania.objects.create(
        nombre="Innova SAS",
        direccion="Calle 2",
        telefono="3002222222"
    )
    c3 = Compania.objects.create(
        nombre="Digital Corp",
        direccion="Calle 3",
        telefono="3003333333"
    )

    # Crear 10 empleados distribuidos
    empleados = [
        ("Juan", "Perez", "juan@mail.com", "Developer", 2500000, c1),
        ("Ana", "Gomez", "ana@mail.com", "QA", 2300000, c1),
        ("Luis", "Torres", "luis@mail.com", "DevOps", 2800000, c1),
        ("Maria", "Lopez", "maria@mail.com", "Developer", 2500000, c2),
        ("Carlos", "Ruiz", "carlos@mail.com", "Designer", 2200000, c2),
        ("Sofia", "Mora", "sofia@mail.com", "PM", 3000000, c2),
        ("Diego", "Castro", "diego@mail.com", "Developer", 2500000, c3),
        ("Laura", "Diaz", "laura@mail.com", "QA", 2300000, c3),
        ("Pedro", "Vargas", "pedro@mail.com", "DevOps", 2800000, c3),
        ("Valentina", "Reyes", "vale@mail.com", "Designer", 2200000, c3),
    ]

    for nombre, apellido, correo, cargo, salario, compania in empleados:
        Empleado.objects.create(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            cargo=cargo,
            salario=salario,
            compania=compania
        )

    print("Seed data creado: 3 compañías y 10 empleados")