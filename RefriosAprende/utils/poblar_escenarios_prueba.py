"""Script de un solo uso: puebla la base de datos real con aprendices, cursos y escenarios
variados (graduado, reprobado, en riesgo, sin actividad...), usando los mismos controladores
que usa la interfaz, para servir como evidencia de pruebas de funcionamiento reales del
software en el "taller" (la monografía).

No arma una base de datos aparte: corre contra database/refrios.db, la misma que ya usa la
aplicación, con los mismos controladores y las mismas reglas de negocio que tocaría un usuario
real haciendo clic en la interfaz (matricular, ver contenidos, presentar una evaluación,
calificar un taller).

Uso (desde la raíz de RefriosAprende):
    py -m utils.poblar_escenarios_prueba
"""
import os

from config.settings import DATABASE_PATH, CONTENIDOS_DIR
from controller.contenido_controller import ContenidoController
from controller.curso_controller import CursoController
from controller.evaluacion_controller import EvaluacionController
from controller.inscripcion_controller import InscripcionController
from controller.progreso_controller import ProgresoController
from controller.taller_controller import TallerController
from controller.tiempo_uso_controller import TiempoUsoController
from controller.usuario_controller import DatosInvalidosError, UsuarioController

PASSWORD_DEMO = "Aprendiz123"
ID_ROL_APRENDIZ = 2

usuarios = UsuarioController()
cursos = CursoController()
contenidos = ContenidoController()
evaluaciones = EvaluacionController()
inscripciones = InscripcionController()
progreso = ProgresoController()
talleres = TallerController()
tiempo_uso = TiempoUsoController()

_ARCHIVO_ENTREGA_DEMO = None
if os.path.isdir(CONTENIDOS_DIR):
    for _nombre in os.listdir(CONTENIDOS_DIR):
        if _nombre.lower().endswith((".png", ".jpg", ".jpeg", ".pdf")):
            _ARCHIVO_ENTREGA_DEMO = os.path.join(CONTENIDOS_DIR, _nombre)
            break

resumen = []


def log(mensaje):
    print(mensaje)


def crear_o_reutilizar_aprendiz(nombre_completo, documento, correo, usuario_login):
    for existente in usuarios.listar_usuarios():
        if existente.usuario == usuario_login:
            return existente
    try:
        return usuarios.crear_usuario(
            nombre_completo, documento, correo, usuario_login, PASSWORD_DEMO, ID_ROL_APRENDIZ
        )
    except DatosInvalidosError as error:
        raise RuntimeError(f"No se pudo crear a {nombre_completo}: {error}") from error


def obtener_o_crear_curso(nombre_curso, id_instructor, categoria, duracion_horas=None):
    existente = next((c for c in cursos.listar_cursos() if c.nombre_curso == nombre_curso), None)
    if existente is None:
        existente = cursos.crear_curso(nombre_curso, f"Curso práctico: {nombre_curso.lower()}.", id_instructor, categoria)
    if existente.estado != "ACTIVO" or existente.id_instructor != id_instructor:
        # Tambien reasigna el instructor si el curso ya existia con uno inactivo o sin rol
        # de administrador (no se podria iniciar sesion con esa cuenta para mostrar el
        # reporte en la monografia).
        existente = cursos.actualizar_curso(
            existente.id_curso, existente.nombre_curso, existente.descripcion, id_instructor, "ACTIVO", categoria
        )
    if duracion_horas is not None:
        from controller.guia_aprendizaje_controller import GuiaAprendizajeController
        guia_ctrl = GuiaAprendizajeController()
        if guia_ctrl.obtener_guia(existente.id_curso) is None:
            guia_ctrl.guardar_guia(
                existente.id_curso,
                {
                    "objetivo_general": f"Formar al aprendiz en {nombre_curso.lower()}.",
                    "procedimiento_paso_a_paso": "Seguir el procedimiento descrito en cada contenido del curso.",
                    "normas_seguridad": "Usar guantes y gafas de protección; verificar presión antes de manipular el sistema.",
                },
                str(duracion_horas),
            )
    return existente


def asegurar_contenidos(id_curso, titulos_y_textos):
    existentes = contenidos.listar_por_curso(id_curso)
    if existentes:
        return existentes
    creados = []
    for titulo, texto in titulos_y_textos:
        creados.append(contenidos.crear_contenido_texto(id_curso, titulo, texto))
    return creados


def asegurar_evaluacion(id_curso, titulo, preguntas_def, nota_minima=3.5, intentos=2):
    existente = evaluaciones.obtener_evaluacion_final(id_curso)
    if existente is not None:
        return existente
    evaluacion = evaluaciones.crear_evaluacion_final(id_curso, titulo, nota_minima, intentos)
    for enunciado, opciones in preguntas_def:
        evaluaciones.crear_pregunta(evaluacion.id_evaluacion, enunciado, opciones)
    return evaluaciones.obtener_evaluacion_final(id_curso)


def asegurar_taller(id_curso, titulo, descripcion):
    existentes = talleres.listar_por_curso(id_curso)
    if existentes:
        return existentes[0]
    return talleres.crear_taller(id_curso, titulo, descripcion)


def matricular_si_falta(id_usuario, id_curso):
    ya_matriculado = any(c.id_curso == id_curso for c in inscripciones.listar_cursos_matriculados(id_usuario))
    if not ya_matriculado:
        inscripciones.matricular(id_usuario, id_curso)


def backdatear_matricula(id_usuario, id_curso, dias_atras):
    """Ajusta la fecha de matrícula hacia el pasado para simular un aprendiz que lleva
    varios días inscrito sin avanzar (así se puede probar el semáforo de riesgo sin
    esperar los días reales)."""
    import sqlite3

    con = sqlite3.connect(DATABASE_PATH)
    con.execute(
        "UPDATE inscripciones SET fecha_inscripcion = datetime('now', 'localtime', ? || ' days') "
        "WHERE id_usuario = ? AND id_curso = ?",
        (f"-{dias_atras}", id_usuario, id_curso),
    )
    con.commit()
    con.close()


def ver_contenidos(id_usuario, lista_contenidos, cuantos):
    for contenido in lista_contenidos[:cuantos]:
        progreso.registrar_contenido_visto(id_usuario, contenido)


def registrar_horas(id_usuario, id_curso, horas):
    id_registro = tiempo_uso.iniciar_sesion_curso(id_usuario, id_curso)
    tiempo_uso.actualizar_sesion_curso(id_registro, int(horas * 3600))


def presentar_evaluacion_bien(id_usuario, evaluacion):
    preguntas_lista = evaluaciones.listar_preguntas(evaluacion.id_evaluacion)
    respuestas = {p.id_pregunta: p.opcion_correcta().id_opcion for p in preguntas_lista}
    return evaluaciones.presentar_evaluacion(id_usuario, evaluacion, respuestas)


def presentar_evaluacion_mal(id_usuario, evaluacion):
    preguntas_lista = evaluaciones.listar_preguntas(evaluacion.id_evaluacion)
    respuestas = {}
    for p in preguntas_lista:
        correcta = p.opcion_correcta()
        incorrecta = next((o for o in p.opciones if o.id_opcion != correcta.id_opcion), correcta)
        respuestas[p.id_pregunta] = incorrecta.id_opcion
    return evaluaciones.presentar_evaluacion(id_usuario, evaluacion, respuestas)


def entregar_taller(id_usuario, taller, aprobar=None, comentario=""):
    if _ARCHIVO_ENTREGA_DEMO is None:
        log("  (sin archivo de muestra disponible para la entrega del taller, se omite)")
        return
    entrega = talleres.subir_entrega(taller.id_taller, id_usuario, _ARCHIVO_ENTREGA_DEMO)
    if aprobar is not None:
        talleres.calificar_entrega(entrega.id_entrega, aprobar, comentario)
    progreso.recalcular_progreso(id_usuario, taller.id_curso)


# ============================================================================================
# 1. Aprendices
# ============================================================================================
log("== Creando aprendices ==")
camila = crear_o_reutilizar_aprendiz("Camila Torres", "1098234501", "camila.torres@refrios.local", "camila.torres")
julian = crear_o_reutilizar_aprendiz("Julián Restrepo", "1098234502", "julian.restrepo@refrios.local", "julian.restrepo")
valentina = crear_o_reutilizar_aprendiz("Valentina Ríos", "1098234503", "valentina.rios@refrios.local", "valentina.rios")
santiago = crear_o_reutilizar_aprendiz("Santiago Morales", "1098234504", "santiago.morales@refrios.local", "santiago.morales")
mariana = crear_o_reutilizar_aprendiz("Mariana Gómez", "1098234505", "mariana.gomez@refrios.local", "mariana.gomez")
esteban = crear_o_reutilizar_aprendiz("Esteban Cárdenas", "1098234506", "esteban.cardenas@refrios.local", "esteban.cardenas")
laura = crear_o_reutilizar_aprendiz("Laura Jiménez", "1098234507", "laura.jimenez@refrios.local", "laura.jimenez")
andres = crear_o_reutilizar_aprendiz("Andrés Felipe Soto", "1098234508", "andres.soto@refrios.local", "andres.soto")
gabriela = next(u for u in usuarios.listar_usuarios() if u.usuario == "Gaby.123")
log(f"  8 aprendices nuevos listos (contraseña demo: {PASSWORD_DEMO}). Se reutiliza también a Gabriela (Gaby.123).")

id_admin_1 = next(u.id_usuario for u in usuarios.listar_usuarios() if u.usuario == "admin")
id_admin_2 = next(u.id_usuario for u in usuarios.listar_usuarios() if u.usuario == "Danrodriguez95")

# ============================================================================================
# 2. Cursos nuevos (4) + completar los que estaban vacíos
# ============================================================================================
log("== Preparando cursos ==")

curso_fugas = obtener_o_crear_curso("Diagnóstico de Fugas en Sistemas de Refrigeración", id_admin_1, "Diagnóstico", 20)
asegurar_contenidos(curso_fugas.id_curso, [
    ("1. Tipos de fuga y dónde buscarlas", "Las fugas más comunes ocurren en las conexiones tipo O-ring, el sello del compresor y el condensador. Antes de usar cualquier equipo, hacer una inspección visual buscando residuos de aceite."),
    ("2. Uso del detector electrónico de fugas", "El detector electrónico se pasa lentamente (2 cm/s) a lo largo de cada conexión. Una alarma sostenida indica fuga; una intermitente puede ser solo viento o falsa alarma."),
    ("3. Prueba con lámpara UV y tinte trazador", "El tinte fluorescente se inyecta junto al aceite del sistema. Tras circular el sistema unos minutos, se revisa con lámpara UV: el punto de fuga brilla en amarillo-verde."),
])
eval_fugas = asegurar_evaluacion(curso_fugas.id_curso, "Evaluación final — Diagnóstico de fugas", [
    ("¿Qué indica una alarma sostenida del detector electrónico?", [("Una fuga real", True), ("Que el equipo está descargado", False)]),
    ("¿Para qué sirve el tinte trazador UV?", [("Para limpiar el sistema", False), ("Para localizar visualmente el punto de fuga", True)]),
    ("¿Dónde ocurren más comúnmente las fugas?", [("En las conexiones tipo O-ring y el sello del compresor", True), ("En el cableado eléctrico", False)]),
])

curso_carga = obtener_o_crear_curso("Carga y Recuperación de Refrigerante", id_admin_1, "Refrigerantes", 16)
asegurar_contenidos(curso_carga.id_curso, [
    ("1. Equipo de recuperación", "La máquina de recuperación extrae el refrigerante del sistema antes de cualquier intervención, por normativa ambiental: nunca se debe liberar refrigerante a la atmósfera."),
    ("2. Cálculo de la carga correcta", "La cantidad de refrigerante a cargar viene en la etiqueta del vehículo, normalmente en gramos. Cargar de más sube la presión de descarga y reduce el rendimiento del A/C."),
    ("3. Verificación final con el manómetro", "Tras cargar, se verifican las presiones de baja y alta contra la tabla del refrigerante usado, con el motor encendido y el A/C en máximo."),
])
eval_carga = asegurar_evaluacion(curso_carga.id_curso, "Evaluación final — Carga y recuperación", [
    ("¿Por qué se debe recuperar el refrigerante antes de intervenir?", [("Por estética", False), ("Por normativa ambiental, para no liberarlo a la atmósfera", True)]),
    ("¿Dónde se encuentra la cantidad correcta de carga?", [("En la etiqueta del vehículo", True), ("Se calcula siempre igual para todos los autos", False)]),
    ("¿Qué pasa si se carga de más refrigerante?", [("Sube la presión de descarga y baja el rendimiento", True), ("No pasa nada", False)]),
])

curso_electricidad = obtener_o_crear_curso("Electricidad Automotriz Aplicada al Aire Acondicionado", id_admin_2, "Electricidad", 24)
asegurar_contenidos(curso_electricidad.id_curso, [
    ("1. El embrague electromagnético del compresor", "El embrague conecta y desconecta el compresor del motor según la señal del módulo de control. Un embrague que no engancha suele ser falla de bobina o de relé."),
    ("2. Sensores de presión", "El sensor de alta y baja presión corta la señal al compresor si detecta una presión fuera de rango, para protegerlo de daño."),
    ("3. Diagnóstico con multímetro", "Se mide continuidad en la bobina del embrague y voltaje en el conector del sensor de presión antes de reemplazar cualquier pieza."),
])

curso_mantenimiento = obtener_o_crear_curso("Mantenimiento Preventivo de Compresores", id_admin_2, "Mantenimiento", 18)
asegurar_contenidos(curso_mantenimiento.id_curso, [
    ("1. Revisión del nivel de aceite", "El compresor necesita una cantidad exacta de aceite para lubricar sus partes internas; revisar el nivel en cada mantenimiento mayor."),
    ("2. Tensión de la correa", "Una correa floja genera ruido y reduce la eficiencia del compresor; una muy tensa acorta la vida del rodamiento."),
    ("3. Señales de desgaste", "Ruido metálico, vibración excesiva o manchas de aceite alrededor del compresor son señales de que necesita revisión antes de fallar por completo."),
])

# Cursos ya existentes que estaban vacíos: se completan con contenido real y se aseguran
# con un instructor administrador activo (los que traían antes podían estar inactivos).
curso_refrios = obtener_o_crear_curso("Refrios", id_admin_1, "Refrigerantes")
cont_refrios = asegurar_contenidos(curso_refrios.id_curso, [
    ("Refrigerantes usados en A/C automotriz", "El R134a fue el estándar durante años; los modelos recientes usan R1234yf, que exige herramientas y procedimientos propios por ser levemente inflamable."),
    ("Compatibilidad entre refrigerantes", "Nunca se debe mezclar R134a con R1234yf en el mismo sistema: dañan los sellos y pueden generar una reacción peligrosa."),
])
eval_refrios = asegurar_evaluacion(curso_refrios.id_curso, "Evaluación final — Refrigerantes", [
    ("¿Qué refrigerante reemplazó al R134a en modelos recientes?", [("R1234yf", True), ("R22", False)]),
    ("¿Se pueden mezclar R134a y R1234yf?", [("Sí, sin problema", False), ("No, dañan los sellos y es peligroso", True)]),
])
taller_refrios = asegurar_taller(curso_refrios.id_curso, "Identificación de refrigerante en un vehículo real", "Fotografiar la etiqueta de refrigerante de un vehículo real y anotar el tipo y la cantidad indicada.")

curso_motobombas = obtener_o_crear_curso("MotoBombas", id_admin_1, "Mantenimiento")
cont_motobombas = asegurar_contenidos(curso_motobombas.id_curso, [
    ("Principio de funcionamiento de una motobomba", "Una motobomba combina un motor eléctrico o de combustión con una bomba centrífuga, usada para mover refrigerante o agua en pruebas de banco."),
    ("Mantenimiento básico", "Revisar sellos, rodamientos y el estado de las mangueras de succión antes de cada uso prolongado."),
    ("Fallas comunes", "Pérdida de cebado, ruido en rodamientos y fugas por el sello mecánico son las fallas más frecuentes reportadas en taller."),
])
eval_motobombas = asegurar_evaluacion(curso_motobombas.id_curso, "Evaluación final — MotoBombas", [
    ("¿Qué combina una motobomba?", [("Un motor y una bomba centrífuga", True), ("Solo una bomba manual", False)]),
    ("¿Qué se debe revisar antes de un uso prolongado?", [("Sellos, rodamientos y mangueras", True), ("Solo el color de la pintura", False)]),
    ("¿Cuál es una falla común reportada en taller?", [("Pérdida de cebado", True), ("Exceso de brillo", False)]),
], intentos=2)

curso_vacio = obtener_o_crear_curso("Aprender a generar vacio de compresor", id_admin_2, "Diagnóstico")
cont_vacio = asegurar_contenidos(curso_vacio.id_curso, [
    ("Por qué se hace vacío antes de cargar", "El vacío retira el aire y la humedad del sistema; la humedad mezclada con refrigerante forma ácidos que dañan el compresor desde adentro."),
    ("Tiempo mínimo recomendado", "Se recomienda mantener el vacío al menos 30 minutos y verificar que la presión se mantenga estable unos minutos tras apagar la bomba, como prueba de que no hay fugas."),
])
taller_vacio = asegurar_taller(curso_vacio.id_curso, "Registro de una prueba de vacío", "Entregar la fotografía o el PDF del manómetro mostrando el vacío alcanzado y el tiempo sostenido.")

log("  8 cursos activos listos, con contenidos y evaluación (algunos con taller).")

# ============================================================================================
# 3. Escenarios
# ============================================================================================
log("== Aplicando escenarios ==")

# Escenario 1: GRADUADA (ve todo, aprueba evaluación, sin taller en este curso)
matricular_si_falta(camila.id_usuario, curso_fugas.id_curso)
cont_fugas_lista = contenidos.listar_por_curso(curso_fugas.id_curso)
ver_contenidos(camila.id_usuario, cont_fugas_lista, len(cont_fugas_lista))
presentar_evaluacion_bien(camila.id_usuario, eval_fugas)
registrar_horas(camila.id_usuario, curso_fugas.id_curso, 22)
resumen.append(("Camila Torres", "Diagnóstico de Fugas...", "GRADUADA: vio todo, aprobó la evaluación, sin taller pendiente"))

# Escenario 2: GRADUADO CON TALLER (ve todo, aprueba evaluación, taller APROBADO)
matricular_si_falta(julian.id_usuario, curso_refrios.id_curso)
ver_contenidos(julian.id_usuario, cont_refrios, len(cont_refrios))
presentar_evaluacion_bien(julian.id_usuario, eval_refrios)
entregar_taller(julian.id_usuario, taller_refrios, aprobar=True, comentario="Buen registro, etiqueta clara y completa.")
registrar_horas(julian.id_usuario, curso_refrios.id_curso, 10)
resumen.append(("Julián Restrepo", "Refrios", "GRADUADO: vio todo, aprobó evaluación y taller APROBADO -> curso COMPLETADO"))

# Escenario 3: REPROBÓ LA EVALUACIÓN (agotó los 2 intentos permitidos)
matricular_si_falta(valentina.id_usuario, curso_motobombas.id_curso)
ver_contenidos(valentina.id_usuario, cont_motobombas, len(cont_motobombas))
presentar_evaluacion_mal(valentina.id_usuario, eval_motobombas)
presentar_evaluacion_mal(valentina.id_usuario, eval_motobombas)
registrar_horas(valentina.id_usuario, curso_motobombas.id_curso, 6)
resumen.append(("Valentina Ríos", "MotoBombas", "REPROBÓ: vio todo el contenido pero agotó los 2 intentos de evaluación sin aprobar"))

# Escenario 4: TALLER RECHAZADO (aprueba evaluación, pero el taller es rechazado)
matricular_si_falta(santiago.id_usuario, curso_vacio.id_curso)
cont_vacio_lista = contenidos.listar_por_curso(curso_vacio.id_curso)
ver_contenidos(santiago.id_usuario, cont_vacio_lista, len(cont_vacio_lista))
entregar_taller(santiago.id_usuario, taller_vacio, aprobar=False, comentario="La foto no muestra con claridad el valor del manómetro. Repetir la prueba.")
registrar_horas(santiago.id_usuario, curso_vacio.id_curso, 4)
resumen.append(("Santiago Morales", "Aprender a generar vacío...", "NO APROBÓ: entregó el taller pero el instructor lo rechazó -> curso EN PROGRESO"))

# Escenario 5: AVANZANDO BIEN (progreso parcial, matrícula reciente, sin riesgo)
matricular_si_falta(mariana.id_usuario, curso_fugas.id_curso)
ver_contenidos(mariana.id_usuario, cont_fugas_lista, 2)
registrar_horas(mariana.id_usuario, curso_fugas.id_curso, 8)
resumen.append(("Mariana Gómez", "Diagnóstico de Fugas...", "AVANZANDO BIEN: 2 de 3 contenidos vistos, matrícula reciente, horas por debajo de lo estimado (semáforo amarillo esperado)"))

# Escenario 6: EN RIESGO (matriculada hace 40 días, casi sin avance)
cont_carga_lista = contenidos.listar_por_curso(curso_carga.id_curso)
matricular_si_falta(esteban.id_usuario, curso_carga.id_curso)
backdatear_matricula(esteban.id_usuario, curso_carga.id_curso, 40)
# 0 contenidos vistos a propósito: con 1 de 3 (33%) quedaba apenas por ENCIMA del umbral de
# riesgo (30%), lo que no activaba la regla de negocio. Con 0% sí queda genuinamente en riesgo.
resumen.append(("Esteban Cárdenas", "Carga y Recuperación...", "EN RIESGO: matriculado hace 40 días, 0% de avance (semáforo rojo esperado)"))

# Escenario 7: SIN NINGUNA ACTIVIDAD (matrícula reciente, 0%)
matricular_si_falta(laura.id_usuario, curso_electricidad.id_curso)
resumen.append(("Laura Jiménez", "Electricidad Automotriz...", "SIN ACTIVIDAD: matriculada, 0% de avance, 0 horas (no inició, matrícula reciente)"))

# Escenario 8: SIN ACTIVIDAD + matriculado hace mucho (en riesgo también por inactividad total)
matricular_si_falta(andres.id_usuario, curso_mantenimiento.id_curso)
backdatear_matricula(andres.id_usuario, curso_mantenimiento.id_curso, 25)
resumen.append(("Andrés Felipe Soto", "Mantenimiento Preventivo...", "SIN ACTIVIDAD y matriculado hace 25 días: 0% de avance (semáforo rojo esperado)"))

# Escenario 9: TALLER ENTREGADO, PENDIENTE DE CALIFICAR (usa la matrícula existente de Gabriela)
matricular_si_falta(gabriela.id_usuario, curso_vacio.id_curso)
ver_contenidos(gabriela.id_usuario, cont_vacio_lista, len(cont_vacio_lista))
entregar_taller(gabriela.id_usuario, taller_vacio, aprobar=None)
resumen.append(("Gabriela", "Aprender a generar vacío...", "TALLER PENDIENTE: entregó el taller, todavía sin calificar por el instructor"))

log("")
log("== Resumen de escenarios aplicados ==")
for nombre, curso, descripcion in resumen:
    log(f"  - {nombre} / {curso}: {descripcion}")

log("")
log("Listo. Revisa Reportes en la aplicación (sesión de Daniel Alejandro / Fernando Quintero) para ver el semáforo y los aprendices críticos.")
