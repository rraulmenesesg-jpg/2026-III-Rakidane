from django.core.exceptions import PermissionDenied
from django.urls import Resolver404, resolve

from .roles import URLS_PERMITIDAS_ESTUDIANTIL, es_rol_estudiantil


class RestriccionRolEstudiantilMiddleware:
    """
    Limita a Alumno/Tutor a una lista de rutas permitidas.

    Ocultar enlaces en el menu no protege nada (se puede escribir la URL a
    mano), por eso la restriccion real vive aqui. Solo afecta a usuarios con
    rol Alumno/Tutor; Docente, Administrador y superusuario no cambian.
    Debe ir despues de AuthenticationMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if es_rol_estudiantil(request.user):
            try:
                nombre = resolve(request.path_info).url_name
            except Resolver404:
                nombre = None  # que Django responda el 404 normal
            else:
                if nombre not in URLS_PERMITIDAS_ESTUDIANTIL:
                    raise PermissionDenied
        return self.get_response(request)
