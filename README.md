# Refrios Aprende

Plataforma de escritorio para la gestión de formación técnica de Refrios: cursos, contenidos,
evaluaciones, simulaciones de diagnóstico y seguimiento del avance de cada aprendiz.

Proyecto de grado — aplicación de escritorio en Python con arquitectura MVC y base de datos
SQLite local.

## Instalación rápida (sin programar)

No hace falta instalar Python ni ninguna dependencia. Todo el código fuente vive en la carpeta
[`RefriosAprende/`](RefriosAprende/).

1. Descarga el instalador más reciente desde la sección
   **[Releases](https://github.com/KIDanielC/RefriosAprende/releases/latest)** de este
   repositorio.
2. Ejecútalo. No pide permisos de administrador.
3. Abre "Refrios Aprende" desde el menú inicio o el acceso directo del escritorio.
4. En el primer arranque, como la base de datos todavía no tiene ningún administrador, se abre
   una ventana para crear la primera cuenta (nombre, usuario y contraseña a elección de quien
   instala). No hay ninguna cuenta ni contraseña de fábrica en el código.

El instalador no se versiona junto al código fuente (es un binario generado); si necesitas
recompilarlo tras algún cambio, sigue
[`RefriosAprende/documentation/EMPAQUETADO.md`](RefriosAprende/documentation/EMPAQUETADO.md).

## Roles y qué puede hacer cada uno

**Administrador**
- Gestión de usuarios (crear, editar, activar/desactivar, restablecer contraseña, roles).
- Gestión de cursos: categorías, prerrequisitos entre cursos, aprendizaje secuencial, estados
  Borrador / Activo / Inactivo.
- Una sola ventana ("Gestionar curso") para armar todo el contenido pedagógico de un curso,
  organizado según la metodología **aprender → practicar → simular → evaluar**: guía de
  aprendizaje, contenidos (texto, PDF, imagen), casos de simulación y evaluación final.
- Matrícula manual de aprendices, con validación de prerrequisitos.
- Ver notas e intentos de cada aprendiz por evaluación o caso de simulación.
- Reportes generales y configuración del sistema.

**Aprendiz**
- Ve sus cursos matriculados y avanza por cada uno en una sola pantalla ("Ver curso"): guía,
  contenido real y las acciones de practicar/presentar, sin cambiar de ventana.
- Practica casos de simulación y presenta la evaluación final (con límite de intentos).
- Sigue su progreso por curso y recibe un certificado al completarlo al 100%.

## Tecnologías

- **Python 3** + [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) para la interfaz.
- **SQLite** como base de datos (archivo local, sin servidor).
- **Matplotlib** para las gráficas del dashboard.
- **Pillow** para el manejo de imágenes.
- **pytest** para las pruebas automatizadas.
- **PyInstaller** + **Inno Setup** para el instalador de Windows.

## Ejecutar desde el código fuente (para desarrollo)

Requiere Python 3.12 o superior.

```
cd RefriosAprende
py -m venv .venv
.venv\Scripts\Activate.ps1    # o .venv\Scripts\activate.bat si usas cmd.exe
py -m pip install -r requirements-dev.txt
py main.py
```

La base de datos (`RefriosAprende/database/refrios.db`) se crea automáticamente al arrancar la
aplicación por primera vez. Como todavía no tiene ningún administrador, el primer arranque abre
la ventana para crear la primera cuenta (ver el paso 4 de la sección anterior).

## Pruebas automatizadas

```
cd RefriosAprende
py -m pytest -q
```

202 pruebas cubren usuarios, cursos y contenidos, evaluaciones, simulaciones, talleres,
certificados, respaldo/restauración, control de acceso por rol y un flujo de integración
completo de principio a fin.

## Estructura del proyecto

```
RefriosAprende/
├── main.py                 Punto de entrada de la aplicación
├── config/                 Configuración y paleta visual
├── model/                  Entidades y acceso a datos (DAO)
├── view/                   Pantallas e interfaz (CustomTkinter)
├── controller/             Lógica de negocio
├── database/               Esquema SQL y conexión (con migraciones incrementales)
├── utils/                  Utilidades (seguridad, texto enriquecido, semilla de datos)
├── tests/                  Suite de pruebas con pytest
├── packaging/              Configuración de PyInstaller e Inno Setup
└── documentation/          Documentación técnica (empaquetado, etc.)
```

La arquitectura sigue el patrón **MVC**: las vistas no contienen lógica de negocio, los
controladores no acceden directamente a la base de datos, y todo el acceso a datos pasa por los
DAO del modelo.

## Historial de desarrollo

El proyecto se construyó de forma incremental por sprints; el historial de commits refleja esa
progresión (arquitectura y usuarios → cursos y contenidos → evaluaciones y simulaciones →
pruebas, corrección de errores, rediseño visual y empaquetado). Cada commit del historial pasa
la suite de pruebas de forma independiente.
