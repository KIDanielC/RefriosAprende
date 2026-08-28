"""Entidad Progreso: avance de un aprendiz dentro de un curso."""

NO_INICIADO = "NO_INICIADO"
EN_PROGRESO = "EN_PROGRESO"
COMPLETADO = "COMPLETADO"


class Progreso:
    def __init__(
        self,
        id_progreso: int,
        id_usuario: int,
        id_curso: int,
        porcentaje_avance: float,
        estado: str,
        fecha_actualizacion: str,
    ):
        self.id_progreso = id_progreso
        self.id_usuario = id_usuario
        self.id_curso = id_curso
        self.porcentaje_avance = porcentaje_avance
        self.estado = estado
        self.fecha_actualizacion = fecha_actualizacion

    def __repr__(self):
        return f"Progreso(id_curso={self.id_curso}, avance={self.porcentaje_avance:.0f}%, estado='{self.estado}')"
