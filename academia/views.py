from django import forms
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import (
    EstadoInscripcion, TipoActividad, TipoRecurso,
    ProgramaNivel, GrupoSeccion, CursoMateria,
    InscripcionCurso, UnidadAcademica, LeccionActividad, RecursoMaterial
)


# --- MIXINS REUTILIZABLES ---
class BootstrapFormMixin:
    """Aplica clases de Bootstrap 5 a los campos y usa datetime-local en fechas."""

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                css = 'form-check-input'
            elif isinstance(widget, forms.Select):
                css = 'form-select'
            else:
                css = 'form-control'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {css}".strip()
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 4)
            if isinstance(field, forms.DateTimeField):
                field.widget = forms.DateTimeInput(
                    format='%Y-%m-%dT%H:%M',
                    attrs={'type': 'datetime-local', 'class': 'form-control'},
                )
                field.input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
        return form


class BorradoSeguroMixin:
    """Si el registro está protegido por otros (on_delete=PROTECT), avisa en vez de dar error 500."""

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.warning(
                self.request,
                'No se puede eliminar este registro porque está siendo utilizado por otros registros.'
            )
            return redirect(self.get_success_url())


# --- ESTADO INSCRIPCION ---
class EstadoInscripcionListView(ListView):
    model = EstadoInscripcion
    ordering = ['nombre_estado']

class EstadoInscripcionDetailView(DetailView):
    model = EstadoInscripcion

class EstadoInscripcionCreateView(BootstrapFormMixin, CreateView):
    model = EstadoInscripcion
    fields = ['nombre_estado']
    template_name = 'academia/nuevo_estado_inscripcion.html'
    success_url = reverse_lazy('estadoinscripcion_list')

class EstadoInscripcionUpdateView(BootstrapFormMixin, UpdateView):
    model = EstadoInscripcion
    fields = ['nombre_estado']
    template_name = 'academia/editar_estado_inscripcion.html'
    success_url = reverse_lazy('estadoinscripcion_list')

class EstadoInscripcionDeleteView(BorradoSeguroMixin, DeleteView):
    model = EstadoInscripcion
    success_url = reverse_lazy('estadoinscripcion_list')


# --- TIPO ACTIVIDAD ---
class TipoActividadListView(ListView):
    model = TipoActividad
    ordering = ['nombre_tipo']

class TipoActividadDetailView(DetailView):
    model = TipoActividad

class TipoActividadCreateView(BootstrapFormMixin, CreateView):
    model = TipoActividad
    fields = ['nombre_tipo']
    template_name = 'academia/nuevo_tipo_actividad.html'
    success_url = reverse_lazy('tipoactividad_list')

class TipoActividadUpdateView(BootstrapFormMixin, UpdateView):
    model = TipoActividad
    fields = ['nombre_tipo']
    template_name = 'academia/editar_tipo_actividad.html'
    success_url = reverse_lazy('tipoactividad_list')

class TipoActividadDeleteView(BorradoSeguroMixin, DeleteView):
    model = TipoActividad
    success_url = reverse_lazy('tipoactividad_list')


# --- TIPO RECURSO ---
class TipoRecursoListView(ListView):
    model = TipoRecurso
    ordering = ['nombre_tipo']

class TipoRecursoDetailView(DetailView):
    model = TipoRecurso

class TipoRecursoCreateView(BootstrapFormMixin, CreateView):
    model = TipoRecurso
    fields = ['nombre_tipo']
    template_name = 'academia/nuevo_tipo_recurso.html'
    success_url = reverse_lazy('tiporecurso_list')

class TipoRecursoUpdateView(BootstrapFormMixin, UpdateView):
    model = TipoRecurso
    fields = ['nombre_tipo']
    template_name = 'academia/editar_tipo_recurso.html'
    success_url = reverse_lazy('tiporecurso_list')

class TipoRecursoDeleteView(BorradoSeguroMixin, DeleteView):
    model = TipoRecurso
    success_url = reverse_lazy('tiporecurso_list')


# --- PROGRAMA NIVEL ---
class ProgramaNivelListView(ListView):
    model = ProgramaNivel
    queryset = ProgramaNivel.objects.select_related('id_institucion').order_by('nombre_nivel')

class ProgramaNivelDetailView(DetailView):
    model = ProgramaNivel
    queryset = ProgramaNivel.objects.select_related('id_institucion')

class ProgramaNivelCreateView(BootstrapFormMixin, CreateView):
    model = ProgramaNivel
    fields = ['id_institucion', 'nombre_nivel', 'clave_programa', 'duracion_periodos']
    template_name = 'academia/nuevo_programa.html'
    success_url = reverse_lazy('programanivel_list')

class ProgramaNivelUpdateView(BootstrapFormMixin, UpdateView):
    model = ProgramaNivel
    fields = ['id_institucion', 'nombre_nivel', 'clave_programa', 'duracion_periodos']
    template_name = 'academia/editar_programa.html'
    success_url = reverse_lazy('programanivel_list')

class ProgramaNivelDeleteView(BorradoSeguroMixin, DeleteView):
    model = ProgramaNivel
    success_url = reverse_lazy('programanivel_list')


# --- GRUPO SECCION ---
class GrupoSeccionListView(ListView):
    model = GrupoSeccion
    queryset = GrupoSeccion.objects.select_related('id_sede', 'id_docente_titular').order_by('-ciclo_escolar', 'nombre_grupo')

class GrupoSeccionDetailView(DetailView):
    model = GrupoSeccion
    queryset = GrupoSeccion.objects.select_related('id_sede', 'id_docente_titular')

class GrupoSeccionCreateView(BootstrapFormMixin, CreateView):
    model = GrupoSeccion
    fields = ['id_sede', 'id_docente_titular', 'nombre_grupo', 'grado_semestre', 'ciclo_escolar', 'capacidad_maxima']
    template_name = 'academia/nuevo_grupo.html'
    success_url = reverse_lazy('gruposeccion_list')

class GrupoSeccionUpdateView(BootstrapFormMixin, UpdateView):
    model = GrupoSeccion
    fields = ['id_sede', 'id_docente_titular', 'nombre_grupo', 'grado_semestre', 'ciclo_escolar', 'capacidad_maxima']
    template_name = 'academia/editar_grupo.html'
    success_url = reverse_lazy('gruposeccion_list')

class GrupoSeccionDeleteView(BorradoSeguroMixin, DeleteView):
    model = GrupoSeccion
    success_url = reverse_lazy('gruposeccion_list')


# --- CURSO MATERIA ---
class CursoMateriaListView(ListView):
    model = CursoMateria
    queryset = CursoMateria.objects.select_related('id_grupo', 'id_docente').order_by('nombre_materia')

class CursoMateriaDetailView(DetailView):
    model = CursoMateria
    queryset = CursoMateria.objects.select_related('id_grupo', 'id_docente')

class CursoMateriaCreateView(BootstrapFormMixin, CreateView):
    model = CursoMateria
    fields = ['id_grupo', 'id_docente', 'nombre_materia', 'clave_materia', 'creditos', 'sala_aula', 'horario_resumen']
    template_name = 'academia/nuevo_curso.html'
    success_url = reverse_lazy('cursomateria_list')

class CursoMateriaUpdateView(BootstrapFormMixin, UpdateView):
    model = CursoMateria
    fields = ['id_grupo', 'id_docente', 'nombre_materia', 'clave_materia', 'creditos', 'sala_aula', 'horario_resumen']
    template_name = 'academia/editar_curso.html'
    success_url = reverse_lazy('cursomateria_list')

class CursoMateriaDeleteView(BorradoSeguroMixin, DeleteView):
    model = CursoMateria
    success_url = reverse_lazy('cursomateria_list')


# --- INSCRIPCION CURSO ---
class InscripcionCursoListView(ListView):
    model = InscripcionCurso
    queryset = InscripcionCurso.objects.select_related(
        'id_alumno', 'id_curso__id_grupo', 'id_estado_inscripcion'
    ).order_by('-fecha_inscripcion')

class InscripcionCursoDetailView(DetailView):
    model = InscripcionCurso
    queryset = InscripcionCurso.objects.select_related(
        'id_alumno', 'id_curso__id_grupo', 'id_estado_inscripcion'
    )

class InscripcionCursoCreateView(BootstrapFormMixin, CreateView):
    model = InscripcionCurso
    fields = ['id_alumno', 'id_curso', 'id_estado_inscripcion', 'progreso_porcentaje']
    template_name = 'academia/nuevo_inscripcion.html'
    success_url = reverse_lazy('inscripcioncurso_list')

class InscripcionCursoUpdateView(BootstrapFormMixin, UpdateView):
    model = InscripcionCurso
    fields = ['id_estado_inscripcion', 'progreso_porcentaje']
    template_name = 'academia/editar_inscripcion.html'
    success_url = reverse_lazy('inscripcioncurso_list')

class InscripcionCursoDeleteView(BorradoSeguroMixin, DeleteView):
    model = InscripcionCurso
    success_url = reverse_lazy('inscripcioncurso_list')


# --- UNIDAD ACADEMICA ---
class UnidadAcademicaListView(ListView):
    model = UnidadAcademica
    queryset = UnidadAcademica.objects.select_related('id_curso__id_grupo').order_by('id_curso__nombre_materia', 'numero_unidad')

class UnidadAcademicaDetailView(DetailView):
    model = UnidadAcademica
    queryset = UnidadAcademica.objects.select_related('id_curso__id_grupo')

class UnidadAcademicaCreateView(BootstrapFormMixin, CreateView):
    model = UnidadAcademica
    fields = ['id_curso', 'numero_unidad', 'titulo_unidad', 'descripcion']
    template_name = 'academia/nuevo_unidad.html'
    success_url = reverse_lazy('unidadacademica_list')

class UnidadAcademicaUpdateView(BootstrapFormMixin, UpdateView):
    model = UnidadAcademica
    fields = ['id_curso', 'numero_unidad', 'titulo_unidad', 'descripcion']
    template_name = 'academia/editar_unidad.html'
    success_url = reverse_lazy('unidadacademica_list')

class UnidadAcademicaDeleteView(BorradoSeguroMixin, DeleteView):
    model = UnidadAcademica
    success_url = reverse_lazy('unidadacademica_list')


# --- LECCION ACTIVIDAD ---
class LeccionActividadListView(ListView):
    model = LeccionActividad
    queryset = LeccionActividad.objects.select_related('id_unidad', 'id_tipo_actividad').order_by('id_unidad__numero_unidad', 'titulo')

class LeccionActividadDetailView(DetailView):
    model = LeccionActividad
    queryset = LeccionActividad.objects.select_related('id_unidad', 'id_tipo_actividad')

class LeccionActividadCreateView(BootstrapFormMixin, CreateView):
    model = LeccionActividad
    fields = ['id_unidad', 'id_tipo_actividad', 'titulo', 'descripcion_instrucciones', 'puntaje_maximo', 'fecha_apertura', 'fecha_limite', 'estado_publicacion']
    template_name = 'academia/nuevo_leccion.html'
    success_url = reverse_lazy('leccionactividad_list')

class LeccionActividadUpdateView(BootstrapFormMixin, UpdateView):
    model = LeccionActividad
    fields = ['id_unidad', 'id_tipo_actividad', 'titulo', 'descripcion_instrucciones', 'puntaje_maximo', 'fecha_apertura', 'fecha_limite', 'estado_publicacion']
    template_name = 'academia/editar_leccion.html'
    success_url = reverse_lazy('leccionactividad_list')

class LeccionActividadDeleteView(BorradoSeguroMixin, DeleteView):
    model = LeccionActividad
    success_url = reverse_lazy('leccionactividad_list')


# --- RECURSO MATERIAL ---
class RecursoMaterialListView(ListView):
    model = RecursoMaterial
    queryset = RecursoMaterial.objects.select_related('id_leccion', 'id_tipo_recurso').order_by('nombre_recurso')

class RecursoMaterialDetailView(DetailView):
    model = RecursoMaterial
    queryset = RecursoMaterial.objects.select_related('id_leccion', 'id_tipo_recurso')

class RecursoMaterialCreateView(BootstrapFormMixin, CreateView):
    model = RecursoMaterial
    fields = ['id_leccion', 'id_tipo_recurso', 'nombre_recurso', 'url_archivo']
    template_name = 'academia/nuevo_recurso.html'
    success_url = reverse_lazy('recursomaterial_list')

class RecursoMaterialUpdateView(BootstrapFormMixin, UpdateView):
    model = RecursoMaterial
    fields = ['id_leccion', 'id_tipo_recurso', 'nombre_recurso', 'url_archivo']
    template_name = 'academia/editar_recurso.html'
    success_url = reverse_lazy('recursomaterial_list')

class RecursoMaterialDeleteView(BorradoSeguroMixin, DeleteView):
    model = RecursoMaterial
    success_url = reverse_lazy('recursomaterial_list')
