"""
Definicion central de los roles Alumno y Tutor.

Ambos roles tienen los mismos permisos (solo consulta de contenido academico
y tablon, mas comentarios en el tablon). Todo lo que dependa de "que ve un
alumno o tutor" debe leerse de aqui para que el menu, las rutas permitidas
y los permisos del grupo no se desincronicen.
"""

GRUPO_ALUMNO = 'Alumno'
GRUPO_TUTOR = 'Tutor'
GRUPOS_ESTUDIANTILES = (GRUPO_ALUMNO, GRUPO_TUTOR)

# Si un usuario tiene alguno de estos grupos, NO se le aplica la restriccion
# de Alumno/Tutor (el rol de mayor privilegio manda).
GRUPOS_PERSONAL = ('Docente', 'Administrador_Institucion')

# Permisos (app_label.codename) que reciben los grupos Alumno y Tutor.
# No se incluyen boletas, asistencias ni entregas: esas listas todavia no se
# filtran por usuario y mostrarian datos de todos los alumnos.
PERMISOS_ESTUDIANTILES = (
    'academia.view_cursomateria',
    'academia.view_unidadacademica',
    'academia.view_leccionactividad',
    'academia.view_recursomaterial',
    'comunicacion.view_publicaciontablon',
    'comunicacion.view_comentariotablon',
    'comunicacion.add_comentariotablon',
    'comunicacion.change_comentariotablon',
    'comunicacion.delete_comentariotablon',
)

# Nombres de URL a los que puede entrar un Alumno/Tutor. Todo lo demas
# responde 403 (ver usuarios/middleware.py).
URLS_PERMITIDAS_ESTUDIANTIL = frozenset({
    'dashboard', 'login', 'logout',
    'cursomateria_list', 'cursomateria_detail',
    'unidadacademica_list', 'unidadacademica_detail',
    'leccionactividad_list', 'leccionactividad_detail',
    'recursomaterial_list', 'recursomaterial_detail',
    'publicaciontablon_list', 'publicaciontablon_detail',
    'comentariotablon_list', 'comentariotablon_detail',
    'comentariotablon_create', 'comentariotablon_update', 'comentariotablon_delete',
})


def es_rol_estudiantil(user):
    """True si el usuario es Alumno/Tutor y no tiene un rol de mayor privilegio."""
    if not user.is_authenticated or user.is_superuser or user.is_staff:
        return False
    cache = getattr(user, '_es_rol_estudiantil', None)
    if cache is None:
        grupos = set(user.groups.values_list('name', flat=True))
        cache = bool(grupos & set(GRUPOS_ESTUDIANTILES)) and not (grupos & set(GRUPOS_PERSONAL))
        user._es_rol_estudiantil = cache
    return cache
