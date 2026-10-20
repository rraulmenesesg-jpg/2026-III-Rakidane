from django.test import TestCase
from django.urls import reverse

from institucion.models import Institucion, Sede
from usuarios.models import Alumno, Docente
from .models import (
    EstadoInscripcion, TipoActividad, TipoRecurso,
    ProgramaNivel, GrupoSeccion, CursoMateria,
    InscripcionCurso, UnidadAcademica, LeccionActividad, RecursoMaterial,
)


class AcademiaRutasTests(TestCase):
    """Smoke test: cada modelo debe poder listarse, verse, editarse y eliminarse sin errores."""

    @classmethod
    def setUpTestData(cls):
        institucion = Institucion.objects.create(nombre_institucion='Instituto Demo')
        sede = Sede.objects.create(id_institucion=institucion, nombre_sede='Campus Central')
        docente = Docente.objects.create(nombres='Ana', apellido_paterno='López')
        alumno = Alumno.objects.create(nombres='Luis', apellido_paterno='Pérez', matricula_expediente='A001')

        estado = EstadoInscripcion.objects.create(nombre_estado='Cursando')
        tipo_act = TipoActividad.objects.create(nombre_tipo='Tarea')
        tipo_rec = TipoRecurso.objects.create(nombre_tipo='PDF')
        programa = ProgramaNivel.objects.create(id_institucion=institucion, nombre_nivel='Licenciatura en Sistemas')
        grupo = GrupoSeccion.objects.create(id_sede=sede, id_docente_titular=docente, nombre_grupo='101-A')
        curso = CursoMateria.objects.create(id_grupo=grupo, id_docente=docente, nombre_materia='Programación')
        inscripcion = InscripcionCurso.objects.create(id_alumno=alumno, id_curso=curso, id_estado_inscripcion=estado)
        unidad = UnidadAcademica.objects.create(id_curso=curso, titulo_unidad='Introducción')
        leccion = LeccionActividad.objects.create(id_unidad=unidad, id_tipo_actividad=tipo_act, titulo='Tarea 1')
        recurso = RecursoMaterial.objects.create(
            id_leccion=leccion, id_tipo_recurso=tipo_rec, nombre_recurso='Guía', url_archivo='https://example.com/guia.pdf'
        )

        cls.objetos = {
            'estadoinscripcion': estado,
            'tipoactividad': tipo_act,
            'tiporecurso': tipo_rec,
            'programanivel': programa,
            'gruposeccion': grupo,
            'cursomateria': curso,
            'inscripcioncurso': inscripcion,
            'unidadacademica': unidad,
            'leccionactividad': leccion,
            'recursomaterial': recurso,
        }

    def test_list_detail_create_update_delete_cargan(self):
        for nombre, obj in self.objetos.items():
            with self.subTest(modelo=nombre):
                self.assertEqual(self.client.get(reverse(f'{nombre}_list')).status_code, 200)
                self.assertEqual(self.client.get(reverse(f'{nombre}_create')).status_code, 200)
                for accion in ('detail', 'update', 'delete'):
                    url = reverse(f'{nombre}_{accion}', args=[obj.pk])
                    self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_crear_programa(self):
        respuesta = self.client.post(reverse('programanivel_create'), {
            'nombre_nivel': 'Secundaria', 'clave_programa': 'SEC', 'duracion_periodos': 3,
        })
        self.assertRedirects(respuesta, reverse('programanivel_list'))
        self.assertTrue(ProgramaNivel.objects.filter(nombre_nivel='Secundaria').exists())

    def test_editar_leccion_con_fechas(self):
        leccion = self.objetos['leccionactividad']
        respuesta = self.client.post(reverse('leccionactividad_update', args=[leccion.pk]), {
            'id_unidad': leccion.id_unidad_id, 'id_tipo_actividad': leccion.id_tipo_actividad_id,
            'titulo': 'Tarea 1 editada', 'puntaje_maximo': '90.00',
            'fecha_apertura': '2026-11-01T08:00', 'fecha_limite': '2026-11-15T23:59',
            'estado_publicacion': 'publicado',
        })
        self.assertRedirects(respuesta, reverse('leccionactividad_list'))
        leccion.refresh_from_db()
        self.assertEqual(leccion.titulo, 'Tarea 1 editada')
        self.assertIsNotNone(leccion.fecha_limite)

    def test_eliminar_catalogo_en_uso_no_da_error(self):
        estado = self.objetos['estadoinscripcion']  # protegido por InscripcionCurso (PROTECT)
        respuesta = self.client.post(reverse('estadoinscripcion_delete', args=[estado.pk]), follow=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(EstadoInscripcion.objects.filter(pk=estado.pk).exists())

    def test_eliminar_programa(self):
        programa = self.objetos['programanivel']
        self.client.post(reverse('programanivel_delete', args=[programa.pk]))
        self.assertFalse(ProgramaNivel.objects.filter(pk=programa.pk).exists())
