-- ============================================================
-- Refrios Aprende - Esquema de Base de Datos (SQLite)
-- Normalizado a 3FN
-- ============================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------
-- ROLES
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id_rol      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_rol  TEXT NOT NULL UNIQUE CHECK (nombre_rol IN ('ADMINISTRADOR', 'APRENDIZ'))
);

-- ---------------------------------------------------------
-- USUARIOS
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    documento       TEXT NOT NULL UNIQUE,
    correo          TEXT NOT NULL UNIQUE,
    usuario         TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    id_rol          INTEGER NOT NULL,
    activo          INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    fecha_creacion  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (id_rol) REFERENCES roles (id_rol)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------------------------------------------------------
-- CURSOS
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS cursos (
    id_curso        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_curso    TEXT NOT NULL,
    descripcion     TEXT,
    id_instructor   INTEGER NOT NULL,
    estado          TEXT NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO')),
    fecha_creacion  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (id_instructor) REFERENCES usuarios (id_usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------------------------------------------------------
-- GUIAS DE APRENDIZAJE (una por curso: objetivos, competencias, actividades)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS guias_aprendizaje (
    id_guia                 INTEGER PRIMARY KEY AUTOINCREMENT,
    id_curso                INTEGER NOT NULL UNIQUE,
    objetivo_general        TEXT,
    objetivos_especificos   TEXT,
    competencias            TEXT,
    actividades              TEXT,
    criterios_evaluacion    TEXT,
    duracion_horas          INTEGER,
    fecha_actualizacion     TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (id_curso) REFERENCES cursos (id_curso)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- CONTENIDOS (unidades de un curso)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS contenidos (
    id_contenido    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_curso        INTEGER NOT NULL,
    titulo          TEXT NOT NULL,
    tipo_contenido  TEXT NOT NULL CHECK (tipo_contenido IN ('TEXTO', 'IMAGEN', 'PDF', 'VIDEO_LOCAL')),
    ruta_archivo    TEXT,
    contenido_texto TEXT,
    orden           INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_curso) REFERENCES cursos (id_curso)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- EVALUACIONES
-- ---------------------------------------------------------
-- id_contenido NULL  -> evaluacion final del curso completo (Sprint 3)
-- id_contenido NO NULL -> cuestionario corto de validacion de un contenido puntual (Sprint 2)
CREATE TABLE IF NOT EXISTS evaluaciones (
    id_evaluacion       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_curso            INTEGER NOT NULL,
    id_contenido        INTEGER,
    titulo              TEXT NOT NULL,
    tipo_evaluacion     TEXT NOT NULL DEFAULT 'CUESTIONARIO' CHECK (tipo_evaluacion IN ('CUESTIONARIO', 'SIMULACION')),
    nota_minima_aprobar REAL NOT NULL DEFAULT 3.0,
    intentos_permitidos INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_curso) REFERENCES cursos (id_curso)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (id_contenido) REFERENCES contenidos (id_contenido)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- PREGUNTAS
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS preguntas (
    id_pregunta     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_evaluacion   INTEGER NOT NULL,
    enunciado       TEXT NOT NULL,
    caso_clinico    TEXT,
    orden           INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones (id_evaluacion)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- OPCIONES
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS opciones (
    id_opcion       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pregunta     INTEGER NOT NULL,
    texto_opcion    TEXT NOT NULL,
    es_correcta     INTEGER NOT NULL DEFAULT 0 CHECK (es_correcta IN (0, 1)),
    FOREIGN KEY (id_pregunta) REFERENCES preguntas (id_pregunta)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- RESULTADOS (intentos de evaluación de un usuario)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS resultados (
    id_resultado    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario      INTEGER NOT NULL,
    id_evaluacion   INTEGER NOT NULL,
    nota_obtenida   REAL NOT NULL,
    aprobado        INTEGER NOT NULL CHECK (aprobado IN (0, 1)),
    fecha_intento   TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones (id_evaluacion)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- PROGRESO (avance de un usuario en un curso)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS progreso (
    id_progreso         INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario          INTEGER NOT NULL,
    id_curso             INTEGER NOT NULL,
    porcentaje_avance   REAL NOT NULL DEFAULT 0 CHECK (porcentaje_avance BETWEEN 0 AND 100),
    estado              TEXT NOT NULL DEFAULT 'NO_INICIADO' CHECK (estado IN ('NO_INICIADO', 'EN_PROGRESO', 'COMPLETADO')),
    fecha_actualizacion TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (id_usuario, id_curso),
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (id_curso) REFERENCES cursos (id_curso)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- SIMULACIONES (casos de diagnóstico ligados a una pregunta/evaluación tipo SIMULACION)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS simulaciones (
    id_simulacion       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_evaluacion       INTEGER NOT NULL,
    titulo_caso         TEXT NOT NULL,
    descripcion_escenario TEXT NOT NULL,
    diagnostico_correcto  TEXT NOT NULL,
    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones (id_evaluacion)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- CONTENIDOS_VISTOS (seguimiento de lectura, base del calculo de progreso)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS contenidos_vistos (
    id_usuario      INTEGER NOT NULL,
    id_contenido    INTEGER NOT NULL,
    fecha_visto     TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (id_usuario, id_contenido),
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (id_contenido) REFERENCES contenidos (id_contenido)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- Índices de apoyo
-- ---------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios (id_rol);
CREATE INDEX IF NOT EXISTS idx_contenidos_curso ON contenidos (id_curso);
CREATE INDEX IF NOT EXISTS idx_preguntas_evaluacion ON preguntas (id_evaluacion);
CREATE INDEX IF NOT EXISTS idx_opciones_pregunta ON opciones (id_pregunta);
CREATE INDEX IF NOT EXISTS idx_resultados_usuario ON resultados (id_usuario);
CREATE INDEX IF NOT EXISTS idx_progreso_usuario ON progreso (id_usuario);
CREATE INDEX IF NOT EXISTS idx_contenidos_vistos_contenido ON contenidos_vistos (id_contenido);

-- Una sola evaluacion final (CUESTIONARIO) por curso; las SIMULACION no tienen este limite.
CREATE UNIQUE INDEX IF NOT EXISTS idx_evaluaciones_final_unica_por_curso
    ON evaluaciones (id_curso)
    WHERE id_contenido IS NULL AND tipo_evaluacion = 'CUESTIONARIO';

-- ---------------------------------------------------------
-- Datos semilla: roles fijos del sistema
-- ---------------------------------------------------------
INSERT OR IGNORE INTO roles (nombre_rol) VALUES ('ADMINISTRADOR');
INSERT OR IGNORE INTO roles (nombre_rol) VALUES ('APRENDIZ');
