from .roles import es_rol_estudiantil


def rol_estudiantil(request):
    """Expone `rol_estudiantil` a las plantillas (True para Alumno/Tutor)."""
    return {'rol_estudiantil': es_rol_estudiantil(request.user)}
