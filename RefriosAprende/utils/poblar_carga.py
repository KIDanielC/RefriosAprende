"""Genera datos de carga para medir tiempos de respuesta bajo distintos volúmenes, sobre
una base de datos APARTE (nunca refrios.db real). Usa los controladores reales, igual que
utils/poblar_escenarios_prueba.py, para que los datos generados equivalgan a los que deja
un uso real de la aplicación.

Volúmenes:
  pequeno  -> 10 usuarios, 4 cursos, 20 resultados (el orden de magnitud de las pruebas de
              funcionamiento del taller).
  mediano  -> 50 usuarios, 15 cursos, 500 resultados.
  grande   -> 200 usuarios, 40 cursos, 5000 resultados.

Uso (desde la raíz de RefriosAprende):
    py -m utils.poblar_carga mediano C:\\ruta\\bd_carga_mediana.db
    py -m utils.poblar_carga grande C:\\ruta\\bd_carga_grande.db

Advertencia: el volumen "grande" pasa por bcrypt (200 veces) y por el flujo completo de
presentar una evaluación (5000 veces), así que puede tardar varios minutos. Es intencional:
mide el mismo costo que pagaría un uso real.
"""
import os
import sys
import time

VOLUMENES = {
    "pequeno": {"usuarios": 10, "cursos": 4, "resultados": 20},
    "mediano": {"usuarios": 50, "cursos": 15, "resultados": 500},
    "grande": {"usuarios": 200, "cursos": 40, "resultados": 5000},
}


def poblar(nombre_volumen: str, ruta_bd: str) -> dict:
    if nombre_volumen not in VOLUMENES:
        raise ValueError(f"Volumen desconocido: '{nombre_volumen}'. Usa uno de: {', '.join(VOLUMENES)}")

    # Apunta la app a la base de datos de carga ANTES de que cualquier controlador abra una
    # conexión, para no tocar jamás la base real de desarrollo.
    import config.settings as settings_module
    settings_module.DATABASE_PATH = ruta_bd
    import database.connection as connection_module
    connection_module.DATABASE_PATH = ruta_bd
    connection_module.ConexionBD._instancia = None

    from controller.contenido_controller import ContenidoController
    from controller.curso_controller import CursoController
    from controller.evaluacion_controller import EvaluacionController
    from controller.inscripcion_controller import InscripcionController
    from controller.usuario_controller import UsuarioController
    from model.dao.rol_dao import RolDAO

    os.makedirs(os.path.dirname(os.path.abspath(ruta_bd)) or ".", exist_ok=True)
    especificacion = VOLUMENES[nombre_volumen]
    inicio = time.perf_counter()

    rol_admin = RolDAO().obtener_por_nombre("ADMINISTRADOR")
    rol_aprendiz = RolDAO().obtener_por_nombre("APRENDIZ")
    uc = UsuarioController()
    admin = uc.crear_usuario(
        "Administrador de Carga", "9999999999", "admin.carga@refrios.local", "admin.carga",
        "ClaveCarga1", rol_admin.id_rol,
    )

    aprendices = [
        uc.crear_usuario(
            f"Aprendiz de Carga {i + 1}", f"800{i:07d}", f"aprendiz.carga{i + 1}@refrios.local",
            f"aprendiz.carga{i + 1}", "ClaveCarga1", rol_aprendiz.id_rol,
        )
        for i in range(especificacion["usuarios"])
    ]

    cc = CursoController()
    cursos = []
    for i in range(especificacion["cursos"]):
        curso_creado = cc.crear_curso(f"Curso de Carga {i + 1}", "Curso generado para medir rendimiento.", admin.id_usuario)
        cursos.append(
            cc.actualizar_curso(
                curso_creado.id_curso, curso_creado.nombre_curso, curso_creado.descripcion,
                admin.id_usuario, "ACTIVO",
            )
        )

    contenido_controlador = ContenidoController()
    evaluacion_controlador = EvaluacionController()
    inscripcion_controlador = InscripcionController()

    evaluaciones_por_curso = {}
    for curso in cursos:
        contenido_controlador.crear_contenido_texto(
            curso.id_curso, "Contenido de carga", "Texto de ejemplo para medir rendimiento. " * 10,
        )
        evaluacion = evaluacion_controlador.crear_evaluacion_final(
            curso.id_curso, "Evaluación de carga", 3.0, especificacion["resultados"]
        )
        evaluacion_controlador.crear_pregunta(
            evaluacion.id_evaluacion, "¿Cuál opción es correcta?", [("Correcta", True), ("Incorrecta", False)],
        )
        evaluaciones_por_curso[curso.id_curso] = evaluacion

    resultados_generados = 0
    indice = 0
    while resultados_generados < especificacion["resultados"]:
        aprendiz = aprendices[indice % len(aprendices)]
        curso = cursos[indice % len(cursos)]
        evaluacion = evaluaciones_por_curso[curso.id_curso]

        inscripcion_controlador.matricular(aprendiz.id_usuario, curso.id_curso)
        pregunta = evaluacion_controlador.listar_preguntas(evaluacion.id_evaluacion)[0]
        evaluacion_controlador.presentar_evaluacion(
            aprendiz.id_usuario, evaluacion, {pregunta.id_pregunta: pregunta.opcion_correcta().id_opcion},
        )
        resultados_generados += 1
        indice += 1

    resumen = {
        "volumen": nombre_volumen,
        "usuarios": especificacion["usuarios"] + 1,
        "cursos": especificacion["cursos"],
        "resultados": resultados_generados,
        "segundos": round(time.perf_counter() - inicio, 1),
        "ruta_bd": ruta_bd,
        "usuario_admin": admin.usuario,
    }
    print(f"Listo: {resumen}")
    return resumen


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: py -m utils.poblar_carga <pequeno|mediano|grande> <ruta_bd_destino>")
        sys.exit(2)
    poblar(sys.argv[1], sys.argv[2])
