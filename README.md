<div align="center">

<img src="https://github.com/user-attachments/assets/9a090400-5839-48d1-855e-e7d277ed2312" alt="Logotipo del Sistema de Gestión de Pequeños Negocios" width="140">

# Sistema de Gestión de Pequeños Negocios

**Punto de venta e inventario multi-sede para la administración y el control operativo de pequeños negocios**

Proyecto Integrador · Tercer Semestre · Ingeniería de Software · Universidad de Colima

<br>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)
![License](https://img.shields.io/badge/Licencia-AGPL--3.0-blue?style=for-the-badge)

<br>

[Descripción](#descripción-del-proyecto) ·
[Funcionalidades](#funcionalidades-principales) ·
[Arquitectura](#arquitectura-del-sistema) ·
[Instalación](#instalación-local) ·
[Despliegue](#despliegue-en-render) ·
[Equipo](#equipo-de-desarrollo)

</div>

---

## Tabla de Contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Problemática](#problemática)
3. [Objetivos](#objetivos)
4. [Funcionalidades Principales](#funcionalidades-principales)
5. [Roles y Permisos](#roles-y-permisos)
6. [Capturas de Pantalla](#capturas-de-pantalla)
7. [Arquitectura del Sistema](#arquitectura-del-sistema)
8. [Modelo de Datos](#modelo-de-datos)
9. [Tecnologías Utilizadas](#tecnologías-utilizadas)
10. [Estructura del Proyecto](#estructura-del-proyecto)
11. [Instalación Local](#instalación-local)
12. [Variables de Entorno](#variables-de-entorno)
13. [Pruebas](#pruebas)
14. [Despliegue en Render](#despliegue-en-render)
15. [Seguridad](#seguridad)
16. [Flujo de Trabajo con Git](#flujo-de-trabajo-con-git)
17. [Equipo de Desarrollo](#equipo-de-desarrollo)
18. [Licencia](#licencia)

---

## Descripción del Proyecto

El **Sistema de Gestión de Pequeños Negocios** es una aplicación web que integra en una sola plataforma las operaciones esenciales de un comercio: **ventas, inventario, productos, sucursales, usuarios y roles**.

Su principal característica es el enfoque **multi-sede**: un mismo negocio puede administrar varias sucursales, cada una con su propio catálogo de productos, inventario y registro de ventas, mientras la dirección conserva una visión centralizada de toda la operación.

El sistema maneja distintos niveles de acceso —**Administrador**, **Gerente** y **Cajero**— de modo que cada usuario trabaja únicamente con la información y las acciones que corresponden a sus responsabilidades dentro de la organización.

<div align="center">
  <img src="https://github.com/user-attachments/assets/c1fa7f97-10c2-4d96-88d0-37a096cc0b56" alt="Panel principal del sistema" width="85%">
  <p><em>Panel principal con indicadores de ventas e inventario</em></p>
</div>

---

## Problemática

Muchos pequeños negocios todavía controlan sus ventas e inventario con libretas, hojas de cálculo aisladas o sistemas que no se comunican entre sucursales. Esto genera:

- Diferencias entre el inventario registrado y el inventario físico.
- Dificultad para saber qué se vende, cuándo y en qué sucursal.
- Falta de control sobre quién realiza cada operación.
- Información dispersa que retrasa la toma de decisiones.

Este proyecto propone una solución accesible, centralizada y organizada por roles para atender esas necesidades.

---

## Objetivos

### Objetivo General

Desarrollar una solución integral para la gestión de pequeños negocios que permita controlar las ventas, el inventario, los productos, las sucursales y los usuarios, facilitando el flujo de información entre los diferentes niveles de la organización.

### Objetivos Específicos

- Registrar ventas de forma ágil desde un punto de venta sencillo para el cajero.
- Mantener el inventario actualizado por sucursal, reflejando cada venta y movimiento.
- Administrar el catálogo de productos de cada sucursal.
- Gestionar sucursales, usuarios y roles con control de acceso.
- Garantizar la calidad del software mediante pruebas automatizadas.
- Desplegar la aplicación en la nube para que sea accesible desde cualquier lugar.

---

## Funcionalidades Principales

| Módulo | Descripción |
|:--|:--|
| **Autenticación** | Inicio de sesión con nombre de usuario, sesiones firmadas, redirección según el rol y recuperación de contraseña por correo electrónico. |
| **Punto de Venta** | Registro de ventas, búsqueda de productos, cálculo de IVA y totales, selección del método de pago y emisión del comprobante. |
| **Inventario** | Consulta y control de existencias por sucursal, entradas de mercancía, alertas de bajo inventario y actualización automática tras cada venta. |
| **Productos y Categorías** | Alta, consulta, edición y baja de productos por sucursal, organizados por categorías. |
| **Sucursales** | Administración de las sedes del negocio y su información. |
| **Usuarios y Roles** | Creación de cuentas, asignación de roles y de sucursal a cada usuario. |
| **Reportes** | Ventas por periodo, estadísticas, productos más vendidos y exportación de reportes en PDF. |
| **Aviso de Privacidad** | Registro de la aceptación del aviso de privacidad por parte de cada usuario. |
| **Interfaz** | Tema claro y oscuro, e interfaz disponible en español e inglés. |

---

## Roles y Permisos

El sistema implementa un **control de acceso basado en roles (RBAC)**. Cada usuario tiene un único rol que determina lo que puede ver y hacer.

| Acción | Administrador | Gerente | Cajero |
|:--|:--:|:--:|:--:|
| Registrar ventas | ✓ | ✓ | ✓ |
| Consultar inventario | ✓ | ✓ | ✓ |
| Modificar inventario | ✓ | ✓ | — |
| Gestionar productos | ✓ | ✓ | — |
| Gestionar categorías | ✓ | — | — |
| Consultar reportes | ✓ | ✓ | — |
| Gestionar usuarios | ✓ | Cajeros de su sucursal | — |
| Gestionar sucursales | ✓ | — | — |

- **Administrador:** control total del sistema y de todas las sucursales.
- **Gerente:** supervisa la operación de su sucursal, su inventario, sus cajeros y sus reportes.
- **Cajero:** opera el punto de venta de su sucursal.

---

## Capturas de Pantalla

### Inicio de Sesión

<div align="center">
  <img src="https://github.com/user-attachments/assets/17ad4a1e-2bec-4bd6-9248-5fd837fae6ad" alt="Pantalla de inicio de sesión" width="85%">
  <p><em>Inicio de sesión</em></p>
</div>

### Panel del Administrador

<div align="center">
  <img src="https://github.com/user-attachments/assets/f7a18926-e2f7-42f5-8342-77243216a7b5" alt="Panel del Administrador" width="85%">
  <p><em>Panel principal del Administrador con indicadores de ventas e inventario</em></p>
</div>

### Punto de Venta

<div align="center">
  <img src="https://github.com/user-attachments/assets/09d24d98-6c0d-4bed-b4f4-db11e2f76af7" alt="Punto de venta" width="85%">
  <p><em>Punto de venta con ticket actual, cálculo de IVA y método de pago</em></p>
</div>

### Inventario y Productos

<div align="center">
  <img src="https://github.com/user-attachments/assets/2444c761-40f5-41c4-b162-8be17872ed55" alt="Inventario" width="85%">
  <p><em>Inventario por sucursal con alertas de bajo inventario</em></p>
</div>

<div align="center">
  <img src="https://github.com/user-attachments/assets/435b6d13-a9f0-48f2-8fa4-985dbedf63aa" alt="Productos" width="85%">
  <p><em>Gestión del catálogo de productos por sucursal</em></p>
</div>

### Sucursales y Usuarios

<div align="center">
  <img src="https://github.com/user-attachments/assets/3c3e6a3e-91f8-4a07-95d0-8f40b165b10c" alt="Sucursales" width="85%">
  <p><em>Gestión de sucursales</em></p>
</div>

<div align="center">
  <img src="https://github.com/user-attachments/assets/3a924e89-d750-45bf-bc28-8a5fbf19a15b" alt="Usuarios" width="85%">
  <p><em>Usuarios y roles</em></p>
</div>

### Reportes

<div align="center">
  <img src="https://github.com/user-attachments/assets/ff410f11-e15b-4cb0-acd3-1f95f940747b" alt="Reportes" width="85%">
  <p><em>Reportes de ventas e indicadores</em></p>
</div>

---

## Arquitectura del Sistema

La aplicación sigue una **arquitectura cliente-servidor en capas**. El frontend consume la API REST construida con FastAPI, que aplica las reglas de negocio y se comunica con PostgreSQL a través de SQLAlchemy.

```mermaid
flowchart LR
    U["Usuario<br/>(Administrador · Gerente · Cajero)"] --> F["Frontend<br/>HTML · CSS · JavaScript"]
    F -- "Peticiones HTTP" --> A["API REST<br/>FastAPI"]
    A --> S["Autenticación<br/>y control de roles"]
    A --> L["Lógica de negocio"]
    L --> O["ORM<br/>SQLAlchemy"]
    O --> D[("PostgreSQL")]
    M["Migraciones<br/>Alembic"] --> D
```

### Flujo de una Venta

```mermaid
sequenceDiagram
    actor C as Cajero
    participant F as Frontend
    participant A as API FastAPI
    participant D as PostgreSQL

    C->>F: Agrega productos a la venta
    F->>A: Envía la venta
    A->>A: Valida sesión, rol y sucursal
    A->>D: Verifica existencias
    D-->>A: Stock disponible
    A->>D: Registra la venta y descuenta inventario
    D-->>A: Confirmación
    A-->>F: Venta registrada
    F-->>C: Muestra comprobante
```

---

## Modelo de Datos

Vista conceptual de las entidades principales del sistema:

```mermaid
erDiagram
    SUCURSAL ||--o{ USUARIO : "tiene asignados"
    ROL ||--o{ USUARIO : "define permisos de"
    SUCURSAL ||--o{ PRODUCTO : "ofrece"
    CATEGORIA ||--o{ PRODUCTO : "clasifica"
    SUCURSAL ||--o{ INVENTARIO : "mantiene"
    PRODUCTO ||--o{ INVENTARIO : "se almacena en"
    SUCURSAL ||--o{ ENTRADA : "recibe"
    ENTRADA ||--|{ DETALLE_ENTRADA : "contiene"
    PRODUCTO ||--o{ DETALLE_ENTRADA : "aparece en"
    SUCURSAL ||--o{ VENTA : "registra"
    USUARIO ||--o{ VENTA : "realiza"
    METODO_PAGO ||--o{ VENTA : "se usa en"
    VENTA ||--|{ DETALLE_VENTA : "contiene"
    PRODUCTO ||--o{ DETALLE_VENTA : "aparece en"
```

El diccionario de datos completo se encuentra en [`Diccionario_de_Datos_PiNet.docx`](Diccionario_de_Datos_PiNet.docx).

---

## Tecnologías Utilizadas

| Capa | Tecnología | Uso en el proyecto |
|:--|:--|:--|
| **Backend** | Python, FastAPI | API REST, lógica de negocio y autenticación |
| **Base de Datos** | PostgreSQL | Almacenamiento persistente de la información |
| **ORM** | SQLAlchemy | Mapeo objeto-relacional y consultas |
| **Migraciones** | Alembic | Control de versiones del esquema de la base de datos |
| **Servidor** | Uvicorn | Servidor ASGI para ejecutar la aplicación |
| **Frontend** | HTML (Jinja2), CSS y JavaScript | Interfaz de usuario |
| **Seguridad** | bcrypt, itsdangerous | Cifrado de contraseñas y firma de sesiones |
| **Correo** | FastAPI-Mail | Envío de correos de recuperación de contraseña |
| **Reportes** | ReportLab | Generación de reportes en PDF |
| **Testing** | Pytest y HTTPX | Pruebas automatizadas de la API |
| **Control de versiones** | Git y GitHub | Trabajo colaborativo y respaldo del código |
| **Despliegue** | Render | Hospedaje de la aplicación y de PostgreSQL en la nube |

---

## Estructura del Proyecto

```text
.
├── app/                    # Código fuente de la aplicación (FastAPI)
│   ├── main.py             # Punto de entrada de la aplicación
│   ├── database.py         # Conexión a PostgreSQL y sesiones de SQLAlchemy
│   ├── dependencies/       # Autenticación y control de acceso por rol
│   ├── models/             # Modelos de SQLAlchemy
│   ├── schemas/            # Esquemas de validación (Pydantic)
│   ├── routers/            # Rutas y endpoints de la API
│   ├── services/           # Lógica de negocio, correo y reportes PDF
│   ├── utils/              # Funciones auxiliares
│   ├── templates/          # Vistas HTML (Jinja2)
│   └── static/             # CSS, JavaScript e imágenes
├── migrations/             # Migraciones de la base de datos (Alembic)
├── scripts/
│   └── seed_admin.py       # Creación del primer administrador
├── tests/                  # Pruebas con Pytest y HTTPX
├── .env.example            # Plantilla de variables de entorno
├── alembic.ini             # Configuración de Alembic
├── render.yaml             # Blueprint de despliegue en Render
├── requirements.txt        # Dependencias de Python
├── LICENSE                 # Licencia AGPL-3.0
└── README.md
```

---

## Instalación Local

### Requisitos Previos

- [Python 3.10 o superior](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/) instalado y en ejecución
- [Git](https://git-scm.com/downloads)

### Pasos

**1. Clonar el repositorio**

```bash
git clone https://github.com/ket2317/PI-3.git
cd PI-3
```

**2. Crear y activar un entorno virtual**

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (CMD)
.venv\Scripts\activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**4. Crear la base de datos**

```bash
createdb -U postgres pi_net
```

O desde `psql`:

```sql
CREATE DATABASE pi_net;
```

**5. Configurar las variables de entorno**

Copiar el archivo de ejemplo y editarlo con los datos locales (ver [Variables de Entorno](#variables-de-entorno)):

```bash
# Linux / macOS
cp .env.example .env

# Windows
copy .env.example .env
```

Como mínimo, ajustar `DATABASE_URL` con el usuario y la contraseña de PostgreSQL, y definir `SESSION_SECRET` y `ADMIN_PASSWORD`.

**6. Aplicar las migraciones**

```bash
alembic upgrade head
```

Esto crea las tablas, los roles (Administrador, Gerente y Cajero) y los métodos de pago iniciales.

**7. Crear el primer administrador**

```bash
python -m scripts.seed_admin
```

El script toma los datos `ADMIN_*` del archivo `.env` y puede ejecutarse varias veces sin duplicar la cuenta.

**8. Iniciar el servidor**

```bash
uvicorn app.main:app --reload
```

| Recurso | URL |
|:--|:--|
| Aplicación | `http://localhost:8000` (redirige a `/login`) |
| Documentación de la API (Swagger) | `http://localhost:8000/docs` |
| Estado del servicio | `http://localhost:8000/health` |

Para iniciar sesión se utiliza el **nombre de usuario** definido en `ADMIN_USERNAME` (por defecto `admin`) y la contraseña definida en `ADMIN_PASSWORD`.

---

## Variables de Entorno

| Variable | Descripción | Ejemplo |
|:--|:--|:--|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL | `postgresql+psycopg2://usuario:contraseña@localhost:5432/pi_net` |
| `SESSION_SECRET` | Clave secreta para firmar las sesiones | Cadena aleatoria larga |
| `ADMIN_NAME` | Nombre del primer administrador | `Administrador General` |
| `ADMIN_USERNAME` | Usuario con el que inicia sesión el administrador | `admin` |
| `ADMIN_EMAIL` | Correo del primer administrador | `admin@ejemplo.com` |
| `ADMIN_PASSWORD` | Contraseña del primer administrador | Contraseña segura |
| `RENDER` | `true` en producción (cookies solo por HTTPS); `false` en local | `false` |
| `MAIL_USERNAME` | Cuenta de Gmail para enviar los correos de recuperación de contraseña | `tu-correo@gmail.com` |
| `MAIL_PASSWORD` | [Contraseña de aplicación](https://support.google.com/accounts/answer/185833) de Gmail | — |
| `MAIL_FROM` | Remitente de los correos | `tu-correo@gmail.com` |

> Las variables `MAIL_*` solo son necesarias para la recuperación de contraseña; el resto del sistema funciona sin ellas.

> **Importante:** el archivo `.env` nunca debe subirse al repositorio; ya está incluido en `.gitignore`.

---

## Pruebas

El proyecto cuenta con pruebas automatizadas escritas con **Pytest** y el `TestClient` de FastAPI (basado en **HTTPX**), que validan la autenticación, los permisos por rol y el comportamiento de los endpoints de la API.

Las pruebas se ejecutan contra la base de datos configurada en `DATABASE_URL`, que debe contener los usuarios de prueba utilizados en [`tests/test_permissions.py`](tests/test_permissions.py).

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con detalle de cada prueba
pytest -v
```

---

## Despliegue en Render

El repositorio incluye [`render.yaml`](render.yaml) para crear el servicio web y la base de datos PostgreSQL mediante un **Blueprint**.

1. En Render, seleccionar **New > Blueprint** y conectar este repositorio.
2. Confirmar que la rama sea `main`.
3. Proporcionar los valores secretos que Render solicite: `ADMIN_EMAIL`, `ADMIN_PASSWORD` y, si se usará la recuperación de contraseña, `MAIL_USERNAME`, `MAIL_PASSWORD` y `MAIL_FROM`.
4. Crear los recursos y esperar a que finalice el primer despliegue.

El comando de inicio realiza tres acciones:

1. Aplica las migraciones de Alembic.
2. Crea de forma idempotente el primer administrador.
3. Arranca el servidor Uvicorn.

`DATABASE_URL` se obtiene de Render PostgreSQL y `SESSION_SECRET` se genera automáticamente; **ninguna credencial real debe guardarse en Git**.

### Verificación del Despliegue

Al terminar el despliegue, comprobar que:

- [ ] `/health` responde `{"status":"ok"}`.
- [ ] `/login` carga el formulario de inicio de sesión.
- [ ] El administrador puede iniciar sesión correctamente.

---

## Seguridad

- Contraseñas almacenadas con hash bcrypt, nunca en texto plano.
- Sesiones firmadas con una clave secreta generada automáticamente.
- Cookies de sesión restringidas a HTTPS en producción.
- Control de acceso por rol y por sucursal en cada ruta protegida del backend.
- Recuperación de contraseña mediante enlaces con token de un solo uso.
- Credenciales y secretos gestionados mediante variables de entorno.
- Creación idempotente del administrador inicial para evitar cuentas duplicadas.

---

## Flujo de Trabajo con Git

El equipo trabaja de forma colaborativa en GitHub siguiendo estas prácticas:

- La rama `main` contiene la versión estable que se despliega en Render.
- Cada funcionalidad se desarrolla en una rama independiente.
- Los cambios se integran mediante *pull requests* revisados por el equipo.
- Los mensajes de *commit* describen de forma clara el cambio realizado.

---

## Equipo de Desarrollo

| Integrante | Área |
|:--|:--|
| **Olivera Kevin Orlando** | Frontend |
| **Navarro Suárez Keyla Cecilia** | Base de datos |
| **Radillo Domínguez Estefanía** | Frontend |
| **Rodríguez Hernández Xanic Osmelí** | Backend |
| **Ruiz Ríos Jonas Eloy** | Backend |

---

## Licencia

Este proyecto se distribuye bajo la licencia **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Consultar el archivo [`LICENSE`](LICENSE) para más información.

---

<div align="center">

**Universidad de Colima** · Ingeniería de Software · Proyecto Integrador de Tercer Semestre

</div>
