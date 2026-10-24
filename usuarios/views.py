import time
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from .models import (
    RolCuenta, EstadoMatricula, ParentescoTutor, CuentaAcceso,
    Docente, Alumno, TutorPadre, SupervisionTutor
)
from .forms import RegistroPublicoForm


# --- LOGOUT PERSONALIZADO (Evita error 403 CSRF en GET) ---
class CustomLogoutView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


# --- REGISTRO PÚBLICO ---
class RegistroPublicoView(FormView):
    template_name = 'usuarios/registro.html'
    form_class = RegistroPublicoForm
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('alumno_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


# --- ROL CUENTA ---
class RolCuentaListView(ListView):
    model = RolCuenta
    template_name = 'usuarios/Roles/rolcuenta_list.html'
    context_object_name = 'roles'

class RolCuentaDetailView(DetailView):
    model = RolCuenta
    template_name = 'usuarios/Roles/rolcuenta_detail.html'
    context_object_name = 'rol'

class RolCuentaCreateView(CreateView):
    model = RolCuenta
    fields = ['nombre_rol', 'descripcion']
    template_name = 'usuarios/Roles/nuevo_rolcuenta.html'
    success_url = '/usuarios/roles/'

class RolCuentaUpdateView(UpdateView):
    model = RolCuenta
    fields = ['nombre_rol', 'descripcion']
    template_name = 'usuarios/Roles/editar_rolcuenta.html'
    success_url = '/usuarios/roles/'

class RolCuentaDeleteView(DeleteView):
    model = RolCuenta
    template_name = 'usuarios/Roles/rolcuenta_confirm_delete.html'
    success_url = '/usuarios/roles/'


# --- ESTADO MATRICULA ---
class EstadoMatriculaListView(ListView):
    model = EstadoMatricula
    template_name = 'usuarios/Estado_matricula/estadomatricula_list.html'

class EstadoMatriculaDetailView(DetailView):
    model = EstadoMatricula
    template_name = 'usuarios/Estado_matricula/estadomatricula_detail.html'

class EstadoMatriculaCreateView(CreateView):
    model = EstadoMatricula
    fields = ['nombre_estado', 'descripcion']
    template_name = 'usuarios/Estado_matricula/nuevo_estadomatricula.html'
    success_url = '/usuarios/estados-matricula/'

class EstadoMatriculaUpdateView(UpdateView):
    model = EstadoMatricula
    fields = ['nombre_estado', 'descripcion']
    template_name = 'usuarios/Estado_matricula/editar_estadomatricula.html'
    success_url = '/usuarios/estados-matricula/'

class EstadoMatriculaDeleteView(DeleteView):
    model = EstadoMatricula
    template_name = 'usuarios/Estado_matricula/estadomatricula_confirm_delete.html'
    success_url = '/usuarios/estados-matricula/'


# --- PARENTESCO TUTOR ---
class ParentescoTutorListView(ListView):
    model = ParentescoTutor
    template_name = 'usuarios/Parentesco/parentesco_list.html'

class ParentescoTutorDetailView(DetailView):
    model = ParentescoTutor
    template_name = 'usuarios/Parentesco/parentesco_detail.html'

class ParentescoTutorCreateView(CreateView):
    model = ParentescoTutor
    fields = ['nombre_parentesco']
    template_name = 'usuarios/Parentesco/nuevo_parentesco.html'
    success_url = '/usuarios/parentescos/'

class ParentescoTutorUpdateView(UpdateView):
    model = ParentescoTutor
    fields = ['nombre_parentesco']
    template_name = 'usuarios/Parentesco/editar_parentesco.html'
    success_url = '/usuarios/parentescos/'

class ParentescoTutorDeleteView(DeleteView):
    model = ParentescoTutor
    template_name = 'usuarios/Parentesco/parentesco_confirm_delete.html'
    success_url = '/usuarios/parentescos/'


# --- CUENTA ACCESO ---
@method_decorator(never_cache, name='dispatch')
class CuentaAccesoListView(ListView):
    model = CuentaAcceso
    template_name = 'usuarios/Cuenta_acceso/cuentaacceso_list.html'
    context_object_name = 'cuentas'

    def get_queryset(self):
        return CuentaAcceso.objects.select_related('id_rol').all().order_by('-id_cuenta')


class CuentaAccesoDetailView(DetailView):
    model = CuentaAcceso
    template_name = 'usuarios/Cuenta_acceso/cuentaacceso_detail.html'
    context_object_name = 'cuenta'


@method_decorator(never_cache, name='dispatch')
class CuentaAccesoCreateView(CreateView):
    model = CuentaAcceso
    fields = ['email', 'id_rol', 'proveedor_sso', 'esta_activo']
    template_name = 'usuarios/Cuenta_acceso/nuevo_cuentaacceso.html'

    def get_success_url(self):
        return f'/usuarios/cuentas/?t={int(time.time())}'

    def form_valid(self, form):
        response = super().form_valid(form)
        cuenta = form.instance
        self._sincronizar_estado_y_rol(cuenta)
        return response

    def _sincronizar_estado_y_rol(self, cuenta):
        User = get_user_model()
        email_clean = cuenta.email.strip().lower()

        user_obj = getattr(cuenta, 'usuario', None)
        if not user_obj:
            user_obj = User.objects.filter(email__iexact=email_clean).first() or \
                       User.objects.filter(username__iexact=email_clean).first()

        if user_obj:
            user_obj.is_active = cuenta.esta_activo
            
            nombre_rol = ""
            if hasattr(cuenta.id_rol, 'nombre_rol'):
                nombre_rol = cuenta.id_rol.nombre_rol
            elif cuenta.id_rol:
                nombre_rol = str(cuenta.id_rol)

            nombre_rol_clean = nombre_rol.lower().strip()

            mapa_roles = {
                'superadmin': 'Administrador_Institucion',
                'super admin': 'Administrador_Institucion',
                'admin institucion': 'Administrador_Institucion',
                'administrador institucion': 'Administrador_Institucion',
                'admin': 'Administrador_Institucion',
                'docente': 'Docente',
                'tutor': 'Tutor',
                'alumno': 'Alumno',
            }

            nombre_grupo = mapa_roles.get(nombre_rol_clean)
            user_obj.groups.clear()
            
            if nombre_grupo:
                grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
                user_obj.groups.add(grupo)

            # Lógica para Superadmin y Staff
            if 'superadmin' in nombre_rol_clean or 'super admin' in nombre_rol_clean:
                user_obj.is_staff = True
                user_obj.is_superuser = True
            elif nombre_grupo == 'Administrador_Institucion':
                user_obj.is_staff = True
                user_obj.is_superuser = False
            else:
                user_obj.is_staff = False
                user_obj.is_superuser = False

            user_obj.save()


@method_decorator(never_cache, name='dispatch')
class CuentaAccesoUpdateView(UpdateView):
    model = CuentaAcceso
    fields = ['email', 'id_rol', 'proveedor_sso', 'esta_activo']
    template_name = 'usuarios/Cuenta_acceso/editar_cuentaacceso.html'

    def get_success_url(self):
        return f'/usuarios/cuentas/?t={int(time.time())}'

    def form_valid(self, form):
        response = super().form_valid(form)
        cuenta = form.instance
        self._sincronizar_estado_y_rol(cuenta)
        return response

    def _sincronizar_estado_y_rol(self, cuenta):
        User = get_user_model()
        email_clean = cuenta.email.strip().lower()

        user_obj = getattr(cuenta, 'usuario', None)
        if not user_obj:
            user_obj = User.objects.filter(email__iexact=email_clean).first() or \
                       User.objects.filter(username__iexact=email_clean).first()

        if user_obj:
            user_obj.is_active = cuenta.esta_activo
            
            nombre_rol = ""
            if hasattr(cuenta.id_rol, 'nombre_rol'):
                nombre_rol = cuenta.id_rol.nombre_rol
            elif cuenta.id_rol:
                nombre_rol = str(cuenta.id_rol)

            nombre_rol_clean = nombre_rol.lower().strip()

            mapa_roles = {
                'superadmin': 'Administrador_Institucion',
                'super admin': 'Administrador_Institucion',
                'admin institucion': 'Administrador_Institucion',
                'administrador institucion': 'Administrador_Institucion',
                'admin': 'Administrador_Institucion',
                'docente': 'Docente',
                'tutor': 'Tutor',
                'alumno': 'Alumno',
            }

            nombre_grupo = mapa_roles.get(nombre_rol_clean)
            user_obj.groups.clear()
            
            if nombre_grupo:
                grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
                user_obj.groups.add(grupo)

            # Lógica para Superadmin y Staff
            if 'superadmin' in nombre_rol_clean or 'super admin' in nombre_rol_clean:
                user_obj.is_staff = True
                user_obj.is_superuser = True
            elif nombre_grupo == 'Administrador_Institucion':
                user_obj.is_staff = True
                user_obj.is_superuser = False
            else:
                user_obj.is_staff = False
                user_obj.is_superuser = False

            user_obj.save()


class CuentaAccesoDeleteView(DeleteView):
    model = CuentaAcceso
    template_name = 'usuarios/Cuenta_acceso/cuentaacceso_confirm_delete.html'
    
    def get_success_url(self):
        return f'/usuarios/cuentas/?t={int(time.time())}'

    def form_valid(self, form):
        cuenta = self.get_object()
        # Buscar y eliminar el usuario de auth_user asociado antes de eliminar la cuenta
        User = get_user_model()
        email_clean = cuenta.email.strip().lower()
        
        user_obj = getattr(cuenta, 'usuario', None) or \
                   User.objects.filter(email__iexact=email_clean).first() or \
                   User.objects.filter(username__iexact=email_clean).first()
        
        if user_obj:
            user_obj.delete()

        return super().form_valid(form)


# --- DOCENTE ---
class DocenteListView(ListView):
    model = Docente
    template_name = 'usuarios/Docentes/docente_list.html'
    context_object_name = 'docentes'

class DocenteDetailView(DetailView):
    model = Docente
    template_name = 'usuarios/Docentes/docente_detail.html'
    context_object_name = 'docente'

class DocenteCreateView(CreateView):
    model = Docente
    fields = [
        'id_cuenta', 'nombres', 'apellido_paterno', 'apellido_materno',
        'numero_empleado', 'cedula_profesional', 'curp_dni', 'fecha_nacimiento',
        'genero', 'telefono_movil', 'departamento', 'especialidad_academica', 'foto_perfil_url'
    ]
    template_name = 'usuarios/Docentes/nuevo_docente.html'
    success_url = '/usuarios/docentes/'

class DocenteUpdateView(UpdateView):
    model = Docente
    fields = [
        'nombres', 'apellido_paterno', 'apellido_materno', 'numero_empleado',
        'cedula_profesional', 'curp_dni', 'fecha_nacimiento', 'genero',
        'telefono_movil', 'departamento', 'especialidad_academica', 'foto_perfil_url'
    ]
    template_name = 'usuarios/Docentes/editar_docente.html'
    success_url = '/usuarios/docentes/'

class DocenteDeleteView(DeleteView):
    model = Docente
    template_name = 'usuarios/Docentes/docente_confirm_delete.html'
    success_url = '/usuarios/docentes/'


# --- ALUMNO ---
class AlumnoListView(ListView):
    model = Alumno
    template_name = 'usuarios/Alumnos/alumno_list.html'
    context_object_name = 'alumnos'

class AlumnoDetailView(DetailView):
    model = Alumno
    template_name = 'usuarios/Alumnos/alumno_detail.html'
    context_object_name = 'alumno'

class AlumnoCreateView(CreateView):
    model = Alumno
    fields = [
        'id_cuenta', 'id_sede', 'id_estado_matricula', 'nombres', 'apellido_paterno',
        'apellido_materno', 'matricula_expediente', 'curp_dni', 'fecha_nacimiento',
        'genero', 'telefono_personal', 'direccion_domicilio', 'foto_perfil_url'
    ]
    template_name = 'usuarios/Alumnos/nuevo_alumno.html'
    success_url = '/usuarios/alumnos/'

class AlumnoUpdateView(UpdateView):
    model = Alumno
    fields = [
        'id_sede', 'id_estado_matricula', 'nombres', 'apellido_paterno',
        'apellido_materno', 'matricula_expediente', 'curp_dni', 'fecha_nacimiento',
        'genero', 'telefono_personal', 'direccion_domicilio', 'foto_perfil_url'
    ]
    template_name = 'usuarios/Alumnos/editar_alumno.html'
    success_url = '/usuarios/alumnos/'

class AlumnoDeleteView(DeleteView):
    model = Alumno
    template_name = 'usuarios/Alumnos/alumno_confirm_delete.html'
    success_url = '/usuarios/alumnos/'


# --- TUTOR PADRE ---
class TutorPadreListView(ListView):
    model = TutorPadre
    template_name = 'usuarios/Tutores_Padres/tutorpadre_list.html'
    context_object_name = 'tutores'

class TutorPadreDetailView(DetailView):
    model = TutorPadre
    template_name = 'usuarios/Tutores_Padres/tutorpadre_detail.html'
    context_object_name = 'tutor'

class TutorPadreCreateView(CreateView):
    model = TutorPadre
    fields = [
        'id_cuenta', 'id_parentesco', 'nombres', 'apellido_paterno',
        'apellido_materno', 'telefono_contacto', 'telefono_emergencia', 'ocupacion'
    ]
    template_name = 'usuarios/Tutores_Padres/nuevo_tutor.html'
    success_url = '/usuarios/tutores/'

class TutorPadreUpdateView(UpdateView):
    model = TutorPadre
    fields = [
        'id_parentesco', 'nombres', 'apellido_paterno', 'apellido_materno',
        'telefono_contacto', 'telefono_emergencia', 'ocupacion'
    ]
    template_name = 'usuarios/Tutores_Padres/editar_tutor.html'
    success_url = '/usuarios/tutores/'

class TutorPadreDeleteView(DeleteView):
    model = TutorPadre
    template_name = 'usuarios/Tutores_Padres/tutorpadre_confirm_delete.html'
    success_url = '/usuarios/tutores/'


# --- SUPERVISION TUTOR ---
class SupervisionTutorListView(ListView):
    model = SupervisionTutor
    template_name = 'usuarios/supervisiontutor_list.html'

class SupervisionTutorDetailView(DetailView):
    model = SupervisionTutor
    template_name = 'usuarios/supervisiontutor_detail.html'

class SupervisionTutorCreateView(CreateView):
    model = SupervisionTutor
    fields = ['id_tutor', 'id_alumno', 'es_contacto_principal']
    template_name = 'usuarios/nuevo_supervisiontutor.html'
    success_url = '/usuarios/supervisiones/'

class SupervisionTutorUpdateView(UpdateView):
    model = SupervisionTutor
    fields = ['id_tutor', 'id_alumno', 'es_contacto_principal']
    template_name = 'usuarios/editar_supervisiontutor.html'
    success_url = '/usuarios/supervisiones/'

class SupervisionTutorDeleteView(DeleteView):
    model = SupervisionTutor
    template_name = 'usuarios/supervisiontutor_confirm_delete.html'
    success_url = '/usuarios/supervisiones/'