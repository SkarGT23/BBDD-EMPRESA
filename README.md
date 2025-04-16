# Proyecto Flask de Base de Datos

Este proyecto es una aplicación web desarrollada con Flask para la gestión de proveedores y promociones.

## Características
- Gestión de proveedores: agregar, editar, eliminar y listar proveedores.
- Gestión de promociones: agregar, editar, eliminar y listar promociones.
- Interfaz web sencilla usando Jinja2 y Bootstrap (si está presente).
- Base de datos gestionada con SQLAlchemy y migraciones.

## Requisitos
Instala las dependencias con:
```bash
pip install -r requirements.txt
```

## Estructura del proyecto
- `app.py` o archivo principal: punto de entrada de la aplicación.
- `templates/`: archivos HTML de la interfaz.
- `migrations/`: archivos de migración de la base de datos.
- `requirements.txt`: dependencias del proyecto.

## Ejecución
1. Activa tu entorno virtual (opcional pero recomendado).
2. Ejecuta la aplicación:
   ```bash
   flask run
   ```
3. Accede a `http://localhost:5000` en tu navegador.

## Migraciones de Base de Datos
Para aplicar migraciones:
```bash
flask db upgrade
```

## Autor
- [SkarGT23]

## Licencia
Este proyecto está bajo la licencia MIT.
