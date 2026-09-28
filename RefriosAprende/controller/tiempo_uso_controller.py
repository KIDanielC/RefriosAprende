"""Controlador de Tiempo de Uso: registra cuánto tiempo real pasa un aprendiz con la
pantalla de un curso abierta, para poder comparar horas acumuladas vs. la duración
estimada del curso (Reportes del instructor)."""
from model.dao.tiempo_uso_curso_dao import TiempoUsoCursoDAO


class TiempoUsoController:
    def __init__(self):
        self._dao = TiempoUsoCursoDAO()

    def iniciar_sesion_curso(self, id_usuario: int, id_curso: int) -> int:
        return self._dao.crear(id_usuario, id_curso)

    def actualizar_sesion_curso(self, id_registro: int, duracion_segundos: int) -> None:
        self._dao.actualizar_duracion(id_registro, duracion_segundos)

    def horas_acumuladas(self, id_usuario: int, id_curso: int) -> float:
        return self._dao.horas_por_usuario_y_curso(id_usuario, id_curso)
