from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

from usuarios.models import CuentaAcceso
from usuarios.roles import GRUPOS_ESTUDIANTILES, PERMISOS_ESTUDIANTILES


class Command(BaseCommand):
    help = (
        "Crea/actualiza los grupos Alumno y Tutor con los mismos permisos "
        "(idempotente). Con --asignar-usuarios tambien agrega a cada grupo a "
        "los usuarios cuya CuentaAcceso tenga ese rol."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--asignar-usuarios', action='store_true',
            help="Agrega a su grupo a los usuarios con rol Alumno/Tutor (no quita otros grupos).",
        )

    def handle(self, *args, **options):
        permisos = []
        for etiqueta in PERMISOS_ESTUDIANTILES:
            app_label, codename = etiqueta.split('.')
            try:
                permisos.append(Permission.objects.get(
                    content_type__app_label=app_label, codename=codename))
            except Permission.DoesNotExist:
                raise CommandError(
                    f"No existe el permiso {etiqueta}. Corre 'python manage.py migrate' primero."
                )

        for nombre in GRUPOS_ESTUDIANTILES:
            grupo, creado = Group.objects.get_or_create(name=nombre)
            grupo.permissions.set(permisos)
            self.stdout.write(self.style.SUCCESS(
                f"Grupo {nombre}: {'creado' if creado else 'actualizado'} con {len(permisos)} permisos"
            ))

        if options['asignar_usuarios']:
            User = get_user_model()
            asignados = 0
            for nombre in GRUPOS_ESTUDIANTILES:
                grupo = Group.objects.get(name=nombre)
                for cuenta in CuentaAcceso.objects.filter(id_rol__nombre_rol__iexact=nombre):
                    user = User.objects.filter(email__iexact=cuenta.email.strip()).first() or \
                           User.objects.filter(username__iexact=cuenta.email.strip()).first()
                    if user and not user.groups.filter(pk=grupo.pk).exists():
                        user.groups.add(grupo)
                        asignados += 1
            self.stdout.write(self.style.SUCCESS(f"Usuarios agregados a su grupo: {asignados}"))
