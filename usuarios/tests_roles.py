from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .roles import GRUPOS_ESTUDIANTILES, PERMISOS_ESTUDIANTILES


def _usuario(nombre, grupos=(), **extra):
    user = User.objects.create_user(username=nombre, email=nombre, password='x', **extra)
    for g in grupos:
        user.groups.add(Group.objects.get_or_create(name=g)[0])
    return user


class RolesAlumnoTutorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('crear_roles', verbosity=0)

    def _entrar(self, nombre, grupos=(), **extra):
        self.client.force_login(_usuario(nombre, grupos, **extra))

    # --- grupos ---
    def test_alumno_y_tutor_tienen_los_mismos_permisos(self):
        conjuntos = []
        for nombre in GRUPOS_ESTUDIANTILES:
            perms = {f"{p.content_type.app_label}.{p.codename}"
                     for p in Group.objects.get(name=nombre).permissions.select_related('content_type')}
            conjuntos.append(perms)
        self.assertEqual(conjuntos[0], conjuntos[1])
        self.assertEqual(conjuntos[0], set(PERMISOS_ESTUDIANTILES))

    def test_crear_roles_es_idempotente(self):
        call_command('crear_roles', verbosity=0)
        self.assertEqual(Group.objects.filter(name__in=GRUPOS_ESTUDIANTILES).count(), 2)

    # --- Alumno y Tutor ---
    def _verificar_rol_estudiantil(self, grupo):
        self._entrar(f'{grupo.lower()}@x.com', [grupo])

        # Dashboard: ve el panel, pero no los modulos administrativos
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        for oculto in ('alumno_list', 'cuentaacceso_list', 'boletacalificacion_list',
                       'programanivel_list', 'registroasistencia_list'):
            self.assertNotIn(reverse(oculto), html, f'{grupo} no deberia ver el enlace a {oculto}')
        for visible in ('cursomateria_list', 'publicaciontablon_list'):
            self.assertIn(reverse(visible), html, f'{grupo} deberia ver el enlace a {visible}')

        # Rutas permitidas
        for nombre in ('cursomateria_list', 'unidadacademica_list', 'leccionactividad_list',
                       'recursomaterial_list', 'publicaciontablon_list', 'comentariotablon_list'):
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 200, nombre)

        # Sin botones de gestion
        html = self.client.get(reverse('cursomateria_list')).content.decode()
        self.assertNotIn(reverse('cursomateria_create'), html)

        # Rutas bloqueadas (aunque escriba la URL a mano)
        for nombre in ('alumno_list', 'docente_list', 'cuentaacceso_list', 'rol_list',
                       'boletacalificacion_list', 'registroasistencia_list',
                       'programanivel_list', 'institucion_list',
                       'cursomateria_create', 'publicaciontablon_create'):
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 403, nombre)

    def test_alumno(self):
        self._verificar_rol_estudiantil('Alumno')

    def test_tutor(self):
        self._verificar_rol_estudiantil('Tutor')

    # --- otros roles no cambian ---
    def test_docente_sigue_igual(self):
        self._entrar('docente@x.com', ['Docente'])
        self.assertEqual(self.client.get(reverse('alumno_list')).status_code, 200)
        self.assertIn(reverse('alumno_list'), self.client.get(reverse('dashboard')).content.decode())

    def test_admin_institucion_sigue_igual(self):
        self._entrar('admin@x.com', ['Administrador_Institucion'], is_staff=True)
        self.assertEqual(self.client.get(reverse('alumno_list')).status_code, 200)
        self.assertIn(reverse('cuentaacceso_list'), self.client.get(reverse('dashboard')).content.decode())

    def test_superusuario_sigue_igual(self):
        self.client.force_login(User.objects.create_superuser('root', 'root@x.com', 'x'))
        self.assertEqual(self.client.get(reverse('rol_list')).status_code, 200)

    def test_rol_de_mayor_privilegio_gana(self):
        self._entrar('mixto@x.com', ['Alumno', 'Docente'])
        self.assertEqual(self.client.get(reverse('alumno_list')).status_code, 200)

    def test_anonimo_sigue_redirigiendo_al_login(self):
        r = self.client.get(reverse('cursomateria_list'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('login', r['Location'])
