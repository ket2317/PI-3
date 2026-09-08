# Sistema de Gestión de Pequeños Negocios

Proyecto Integrador de Tercer Semestre enfocado en el desarrollo de un sistema de punto de venta e inventario multi-sede para la administración y control operativo de pequeños negocios.

---

## Descripción del Proyecto

El sistema permitirá gestionar ventas, inventario, productos, sucursales, usuarios y roles dentro de un pequeño negocio. La aplicación manejará distintos niveles de acceso como Administrador, Gerente y Cajero, permitiendo organizar la información de acuerdo con las responsabilidades de cada usuario.

---

## Integrantes

- Olivera Kevin Orlando
- Navarro Suárez Keyla Cecilia
- Radillo Domínguez Estefanía
- Rodríguez Hernández Xanic Osmelí
- Ruiz Ríos Jonas Eloy

---

## Objetivo General

Desarrollar una solución integral para la gestión de pequeños negocios que permita controlar las ventas, el inventario, los productos, las sucursales y los usuarios, facilitando el flujo de información entre los diferentes niveles de la organización.

---

## Tecnologías Utilizadas

- **Backend:** Python, FastAPI
- **Base de Datos:** PostgreSQL
- **ORM:** SQLAlchemy
- **Frontend:** HTML, CSS y JavaScript
- **Testing:** Pytest y HTTPX
- **Control de versiones:** Git y GitHub
- **Despliegue:** Render

---

## Licencia

Este proyecto utiliza la licencia **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Consultar el archivo `LICENSE` para más información.

---

## Despliegue en Render

El repositorio incluye `render.yaml` para crear el servicio FastAPI y PostgreSQL mediante un Blueprint.

1. En Render, seleccionar **New > Blueprint** y conectar este repositorio.
2. Confirmar que la rama sea `main`.
3. Proporcionar valores secretos para `ADMIN_EMAIL` y `ADMIN_PASSWORD` cuando Render los solicite.
4. Crear los recursos y esperar a que finalice el primer despliegue.

El comando de inicio aplica las migraciones de Alembic, crea de forma idempotente el primer administrador y arranca Uvicorn. `DATABASE_URL` se obtiene de Render PostgreSQL y `SESSION_SECRET` se genera automáticamente; ninguna credencial real debe guardarse en Git.

Cuando termine el despliegue, comprobar:

- `/health` responde `{"status":"ok"}`.
- `/login` carga el formulario.
- El administrador puede iniciar sesión con las variables configuradas.
