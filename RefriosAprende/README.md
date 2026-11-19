# Refrios Aprende

Versión 1.0.1

Aplicación de escritorio (Windows) para la formación técnica en refrigeración automotriz:
cursos, contenidos, evaluaciones, simulaciones de diagnóstico, talleres prácticos y
seguimiento del avance de cada aprendiz por parte del instructor.

## Preparación

Requiere Python 3.12 o superior.

```
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

`requirements-dev.txt` incluye `requirements.txt` (las dependencias de la aplicación)
más `pytest` y `pyinstaller`, necesarios para correr las pruebas y compilar el instalador.

## Ejecución

```
py main.py
```

En el primer arranque, si la base de datos todavía no tiene ningún administrador, la
aplicación abre una ventana para crear la primera cuenta (nombre, usuario y contraseña a
elección de quien instala). No hay ninguna cuenta ni contraseña de fábrica en el código.

## Pruebas

```
py -m pytest -q
```

Con cobertura:

```
py -m pytest tests --cov=model --cov=controller --cov=utils --cov=config --cov=database --cov-report=term
```

## Empaquetado (instalador de Windows)

Ver [`documentation/EMPAQUETADO.md`](documentation/EMPAQUETADO.md) para el procedimiento
completo (generar la semilla, compilar con PyInstaller, compilar el instalador con Inno
Setup y verificar que el paquete resultante no trae datos de ejemplo).

Este repositorio **no** trae ninguna base de datos de demostración: la que se empaqueta
(`packaging/semilla/refrios.db`) solo tiene el esquema y los roles fijos del sistema
(Administrador, Aprendiz), sin usuarios, cursos ni resultados.
