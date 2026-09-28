"""Entidad EntregaTaller: archivo que un aprendiz sube para un taller, con su calificación."""

PENDIENTE = "PENDIENTE"
APROBADO = "APROBADO"
RECHAZADO = "RECHAZADO"


class EntregaTaller:
    def __init__(
        self,
        id_entrega: int,
        id_taller: int,
        id_usuario: int,
        ruta_archivo: str,
        nombre_archivo_original: str,
        estado: str,
        comentario_instructor: str,
        fecha_entrega: str,
        fecha_calificacion: str,
        nombre_usuario: str = None,
    ):
        self.id_entrega = id_entrega
        self.id_taller = id_taller
        self.id_usuario = id_usuario
        self.ruta_archivo = ruta_archivo
        self.nombre_archivo_original = nombre_archivo_original
        self.estado = estado
        self.comentario_instructor = comentario_instructor
        self.fecha_entrega = fecha_entrega
        self.fecha_calificacion = fecha_calificacion
        self.nombre_usuario = nombre_usuario

    def aprobada(self) -> bool:
        return self.estado == APROBADO

    def pendiente(self) -> bool:
        return self.estado == PENDIENTE

    def __repr__(self):
        return f"EntregaTaller(id_entrega={self.id_entrega}, id_taller={self.id_taller}, estado='{self.estado}')"
