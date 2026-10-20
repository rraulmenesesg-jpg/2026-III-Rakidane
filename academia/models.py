import uuid
from django.db import models

# --- CATÁLOGOS REUTILIZABLES ---
class EstadoInscripcion(models.Model):
    id_estado_inscripcion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_estado = models.CharField(max_length=50, unique=True, help_text="Cursando, Aprobado, Reprobado, Dado de Baja")

    class Meta:
        db_table = 'estado_inscripcion'

    def __str__(self):
        return self.nombre_estado


class TipoActividad(models.Model):
    id_tipo_actividad = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_tipo = models.CharField(max_length=50, unique=True, help_text="Tarea, Examen, Proyecto, Foro, Cuestionario")

    class Meta:
        db_table = 'tipo_actividad'

    def __str__(self):
        return self.nombre_tipo


class TipoRecurso(models.Model):
    id_tipo_recurso = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_tipo = models.CharField(max_length=50, unique=True, help_text="PDF, Video, Enlace Web, Documento, Imagen")

    class Meta:
        db_table = 'tipo_recurso'

    def __str__(self):
        return self.nombre_tipo


# --- TABLAS PRINCIPALES ---
class ProgramaNivel(models.Model):
    id_programa = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_institucion = models.ForeignKey('institucion.Institucion', on_delete=models.CASCADE, null=True, blank=True, db_column='id_institucion')
    nombre_nivel = models.CharField(max_length=100, help_text="Ej: Primaria, Secundaria, Licenciatura en Sistemas")
    clave_programa = models.CharField(max_length=30, blank=True, null=True)
    duracion_periodos = models.IntegerField(default=1)

    class Meta:
        db_table = 'programa_nivel'

    def __str__(self):
        return self.nombre_nivel


class GrupoSeccion(models.Model):
    id_grupo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_sede = models.ForeignKey('institucion.Sede', on_delete=models.CASCADE, db_column='id_sede')
    id_docente_titular = models.ForeignKey('usuarios.Docente', on_delete=models.SET_NULL, null=True, blank=True, db_column='id_docente_titular')
    nombre_grupo = models.CharField(max_length=50, help_text="Ej: Grupo 101-A")
    grado_semestre = models.CharField(max_length=20, blank=True, null=True)
    ciclo_escolar = models.CharField(max_length=30, default='2025-2026')
    capacidad_maxima = models.IntegerField(default=35)

    class Meta:
        db_table = 'grupo_seccion'

    def __str__(self):
        return f"{self.nombre_grupo} - {self.ciclo_escolar}"


class CursoMateria(models.Model):
    id_curso = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_grupo = models.ForeignKey(GrupoSeccion, on_delete=models.CASCADE, db_column='id_grupo')
    id_docente = models.ForeignKey('usuarios.Docente', on_delete=models.SET_NULL, null=True, blank=True, db_column='id_docente')
    nombre_materia = models.CharField(max_length=100)
    clave_materia = models.CharField(max_length=30, blank=True, null=True)
    creditos = models.IntegerField(default=5)
    sala_aula = models.CharField(max_length=50, blank=True, null=True)
    horario_resumen = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = 'curso_materia'

    def __str__(self):
        return f"{self.nombre_materia} ({self.id_grupo.nombre_grupo})"


class InscripcionCurso(models.Model):
    id_inscripcion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_alumno = models.ForeignKey('usuarios.Alumno', on_delete=models.CASCADE, db_column='id_alumno')
    id_curso = models.ForeignKey(CursoMateria, on_delete=models.CASCADE, db_column='id_curso')
    id_estado_inscripcion = models.ForeignKey(EstadoInscripcion, on_delete=models.PROTECT, db_column='id_estado_inscripcion', null=True, blank=True)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    progreso_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'inscripcion_curso'
        unique_together = (('id_alumno', 'id_curso'),)

    def __str__(self):
        return f"{self.id_alumno} → {self.id_curso}"


class UnidadAcademica(models.Model):
    id_unidad = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_curso = models.ForeignKey(CursoMateria, on_delete=models.CASCADE, db_column='id_curso')
    numero_unidad = models.IntegerField(default=1)
    titulo_unidad = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'unidad_academica'

    def __str__(self):
        return f"Unidad {self.numero_unidad}: {self.titulo_unidad}"


class LeccionActividad(models.Model):
    id_leccion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_unidad = models.ForeignKey(UnidadAcademica, on_delete=models.CASCADE, db_column='id_unidad')
    id_tipo_actividad = models.ForeignKey(TipoActividad, on_delete=models.PROTECT, db_column='id_tipo_actividad', null=True, blank=True)
    titulo = models.CharField(max_length=150)
    descripcion_instrucciones = models.TextField(blank=True, null=True)
    puntaje_maximo = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    fecha_apertura = models.DateTimeField(blank=True, null=True)
    fecha_limite = models.DateTimeField(blank=True, null=True)
    estado_publicacion = models.CharField(max_length=30, default='borrador')

    class Meta:
        db_table = 'leccion_actividad'

    def __str__(self):
        return self.titulo


class RecursoMaterial(models.Model):
    id_recurso = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_leccion = models.ForeignKey(LeccionActividad, on_delete=models.CASCADE, db_column='id_leccion')
    id_tipo_recurso = models.ForeignKey(TipoRecurso, on_delete=models.PROTECT, db_column='id_tipo_recurso', null=True, blank=True)
    nombre_recurso = models.CharField(max_length=150, blank=True, null=True)
    url_archivo = models.TextField()

    class Meta:
        db_table = 'recurso_material'

    def __str__(self):
        return self.nombre_recurso or self.url_archivo