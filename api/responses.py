def validation_error(serializer):
    errores = []
    for campo, detalles in serializer.errors.items():
        for detalle in detalles:
            errores.append({'campo': campo, 'detalle': str(detalle)})
    return {'mensaje': 'Error de validacion', 'errores': errores}
