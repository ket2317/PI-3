<div align="center">

<!-- CAPTURA 1: Logotipo del proyecto-->
<img src="https://github.com/user-attachments/assets/9a090400-5839-48d1-855e-e7d277ed2312" alt="Logotipo del Sistema de Gestión de Pequeños Negocios" width="140">

# Sistema de Gestión de Pequeños Negocios

**Punto de venta e inventario multi-sede para la administración y el control operativo de pequeños negocios**

Proyecto Integrador · Tercer Semestre · Ingeniería de Software · Universidad de Colima

<br>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
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

Su principal característica es el enfoque **multi-sede**: un mismo negocio puede administrar varias sucursales, cada una con su propio inventario y registro de ventas, mientras la dirección conserva una visión centralizada de toda la operación.

El sistema maneja distintos niveles de acceso —**Administrador**, **Gerente** y **Cajero**— de modo que cada usuario trabaja únicamente con la información y las acciones que corresponden a sus responsabilidades dentro de la organización.

<!-- CAPTURA 2: Vista general del sistema -->
<div align="center">
  <img src="https://github.com/user-attachments/assets/c1fa7f97-10c2-4d96-88d0-37a096cc0b56" alt="Panel principal de Vendora" width="85%">
  <p><em>Panel principal con indicadores de ventas e inventario</em></p>
</div>


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
- Administrar el catálogo de productos de manera centralizada.
- Gestionar sucursales, usuarios y roles con control de acceso.
- Garantizar la calidad del software mediante pruebas automatizadas.
- Desplegar la aplicación en la nube para que sea accesible desde cualquier lugar.

---

## Funcionalidades Principales

| Módulo | Descripción |
|:--|:--|
| **Autenticación** | Inicio de sesión seguro con manejo de sesiones y redirección según el rol del usuario. |
| **Punto de Venta** | Registro de ventas, selección de productos, cálculo de totales y emisión del comprobante de la operación. |
| **Inventario** | Consulta y control de existencias por sucursal; actualización automática tras cada venta. |
| **Productos** | Alta, consulta, edición y baja de productos del catálogo. |
| **Sucursales** | Administración de las sedes del negocio y su información. |
| **Usuarios y Roles** | Creación de cuentas, asignación de roles y de sucursal a cada usuario. |
| **Reportes** | Consulta de ventas e indicadores para apoyar la toma de decisiones. |


---

## Roles y Permisos

El sistema implementa un **control de acceso basado en roles (RBAC)**. Cada usuario tiene un único rol que determina lo que puede ver y hacer.

| Acción | Administrador | Gerente | Cajero |
|:--|:--:|:--:|:--:|
| Registrar ventas | ✓ | ✓ | ✓ |
| Consultar inventario | ✓ | ✓ | ✓ |
| Modificar inventario | ✓ | ✓ | — |
| Gestionar productos | ✓ | ✓ | — |
| Consultar reportes | ✓ | ✓ | — |
| Gestionar usuarios | ✓ | — | — |
| Gestionar sucursales | ✓ | — | — |

- **Administrador:** control total del sistema y de todas las sucursales.
- **Gerente:** supervisa la operación de su sucursal, su inventario y sus reportes.
- **Cajero:** opera el punto de venta de su sucursal.

---

## Capturas de Pantalla

### Inicio de Sesión

<!-- CAPTURA 3: login-->
<div align="center">
  <img src="https://github.com/user-attachments/assets/17ad4a1e-2bec-4bd6-9248-5fd837fae6ad" alt="Pantalla de inicio de sesión de Vendora" width="85%">
  <p><em>Inicio de sesión</em></p>
</div>


### Panel del Administrador

<!-- CAPTURA 4: Pantalla principal que ve el Administrador al iniciar sesión-->
<div align="center">
  <img src="https://github.com/user-attachments/assets/f7a18926-e2f7-42f5-8342-77243216a7b5" alt="Panel del Administrador de Vendora" width="85%">
  <p><em>Panel principal del Administrador con indicadores de ventas e inventario</em></p>
</div>

### Punto de Venta

<!-- CAPTURA 5: Pantalla del cajero con una venta en proceso (varios productos agregados y el total visible). -->
<div align="center">
  <img src="https://github.com/user-attachments/assets/09d24d98-6c0d-4bed-b4f4-db11e2f76af7" alt="Punto de venta de Vendora" width="85%">
  <p><em>Punto de venta con ticket actual, cálculo de IVA y método de pago</em></p>
</div>

### Inventario y Productos

<!-- CAPTURA 6 y 7: Tabla de inventario de una sucursal y catálogo/formulario de productos. -->
<div align="center">
  <img src="https://github.com/user-attachments/assets/2444c761-40f5-41c4-b162-8be17872ed55" alt="Inventario de Vendora" width="85%">
  <p><em>Inventario por sucursal con alertas de bajo inventario</em></p>
</div>

<div align="center">
  <img src="https://github.com/user-attachments/assets/435b6d13-a9f0-48f2-8fa4-985dbedf63aa" alt="Productos de Vendora" width="85%">
  <p><em>Gestión del catálogo de productos por sucursal</em></p>
</div>




### Sucursales y Usuarios

<!-- CAPTURA 8 y 9: Listado de sucursales y gestión de usuarios con sus roles. -->
<div align="center">
  <img src="https://github.com/user-attachments/assets/3c3e6a3e-91f8-4a07-95d0-8f40b165b10c" alt="Sucursales de Vendora" width="85%">
  <p><em>Gestión de sucursales</em></p>
</div>

<div align="center">
  <img src="https://github.com/user-attachments/assets/3a924e89-d750-45bf-bc28-8a5fbf19a15b" alt="Usuarios de Vendora" width="85%">
  <p><em>Usuarios y roles</em></p>
</div>



### Reportes

<!-- CAPTURA 10: Pantalla de reportes o resumen de ventas. -->
<div align="center">
  <img src="https://github.com/user-attachments/assets/ff410f11-e15b-4cb0-acd3-1f95f940747b" alt="Reportes de Vendora" width="85%">
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

<!-- CAPTURA OPCIONAL: Si el equipo tiene un diagrama de arquitectura propio, guardarlo como docs/capturas/arquitectura.png y colocarlo aquí. -->

---

## Modelo de Datos

Vista conceptual de las entidades principales del sistema:

```mermaid
erDiagram
    SUCURSAL ||--o{ USUARIO : "tiene asignados"
    ROL ||--o{ USUARIO : "define permisos de"
    SUCURSAL ||--o{ INVENTARIO : "mantiene"
    PRODUCTO ||--o{ INVENTARIO : "se almacena en"
    SUCURSAL ||--o{ VENTA : "registra"
    USUARIO ||--o{ VENTA : "realiza"
    VENTA ||--|{ DETALLE_VENTA : "contiene"
    PRODUCTO ||--o{ DETALLE_VENTA : "aparece en"
```

<!-- CAPTURA 11 (opcional): Diagrama entidad-relación completo de la base de datos -->

---

## Tecnologías Utilizadas

| Capa | Tecnología | Uso en el proyecto |
|:--|:--|:--|
| **Backend** | Python, FastAPI | API REST, lógica de negocio y autenticación |
| **Base de Datos** | PostgreSQL | Almacenamiento persistente de la información |
| **ORM** | SQLAlchemy | Mapeo objeto-relacional y consultas |
| **Migraciones** | Alembic | Control de versiones del esquema de la base de datos |
| **Servidor** | Uvicorn | Servidor ASGI para ejecutar la aplicación |
| **Frontend** | HTML, CSS y JavaScript | Interfaz de usuario |
| **Testing** | Pytest y HTTPX | Pruebas automatizadas de la API |
| **Control de versiones** | Git y GitHub | Trabajo colaborativo y respaldo del código |
| **Despliegue** | Render | Hospedaje de la aplicación y de PostgreSQL en la nube |

---

## Estructura del Proyecto

```text
.
├── app/                    # Código fuente del backend (FastAPI)
│   ├── main.py             # Punto de entrada de la aplicación
│   ├── models/             # Modelos de SQLAlchemy
│   ├── schemas/            # Esquemas de validación
│   ├── routers/            # Rutas y endpoints de la API
│   ├── services/           # Lógica de negocio
│   └── static/             # Frontend: HTML, CSS y JavaScript
├── alembic/                # Migraciones de la base de datos
├── tests/                  # Pruebas con Pytest y HTTPX
├── docs/
│   └── capturas/           # Imágenes utilizadas en este README
├── render.yaml             # Blueprint de despliegue en Render
├── requirements.txt        # Dependencias de Python
├── LICENSE                 # Licencia AGPL-3.0
└── README.md
```
---

## Instalación Local

### Requisitos Previos

- Python 3.10 o superior
- PostgreSQL en ejecución
- Git

### Pasos

**1. Clonar el repositorio**

```bash
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>
```

**2. Crear y activar un entorno virtual**

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**4. Configurar las variables de entorno**

Crear un archivo `.env` en la raíz del proyecto (ver la sección [Variables de Entorno](#variables-de-entorno)).

**5. Aplicar las migraciones**

```bash
alembic upgrade head
```

**6. Iniciar el servidor**

```bash
uvicorn app.main:app --reload
```

La aplicación quedará disponible en `http://localhost:8000`, y la documentación interactiva de la API en `http://localhost:8000/docs`.

<!-- CAPTURA 12 (opcional): Documentación automática de la API en /docs (Swagger UI). Guardar como docs/capturas/swagger.png -->
<div align="center">
  <img src="docs/capturas/swagger.png" alt="Documentación interactiva de la API" width="85%">
  <p><em>Documentación interactiva generada por FastAPI</em></p>
</div>

---

## Variables de Entorno

| Variable | Descripción | Ejemplo |
|:--|:--|:--|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL | `postgresql://usuario:contraseña@localhost:5432/negocio` |
| `SESSION_SECRET` | Clave secreta para firmar las sesiones | Cadena aleatoria larga |
| `ADMIN_EMAIL` | Correo del primer administrador | `admin@ejemplo.com` |
| `ADMIN_PASSWORD` | Contraseña del primer administrador | Contraseña segura |

> **Importante:** el archivo `.env` nunca debe subirse al repositorio. Verificar que esté incluido en `.gitignore`.

---

## Pruebas

El proyecto cuenta con pruebas automatizadas escritas con **Pytest** y **HTTPX**, que validan el comportamiento de los endpoints de la API.

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con detalle de cada prueba
pytest -v
```

<!-- CAPTURA 13 (opcional): Terminal mostrando las pruebas aprobadas. Guardar como docs/capturas/pruebas.png -->
<div align="center">
  <img src="docs/capturas/pruebas.png" alt="Resultado de las pruebas automatizadas" width="75%">
</div>

---

## Despliegue en Render

El repositorio incluye `render.yaml` para crear el servicio FastAPI y la base de datos PostgreSQL mediante un **Blueprint**.

1. En Render, seleccionar **New > Blueprint** y conectar este repositorio.
2. Confirmar que la rama sea `main`.
3. Proporcionar valores secretos para `ADMIN_EMAIL` y `ADMIN_PASSWORD` cuando Render los solicite.
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

<!-- CAPTURA 14 (opcional): Panel de Render con el servicio en estado "Live". Guardar como docs/capturas/render.png -->
<div align="center">
  <img src="docs/capturas/render.png" alt="Servicio desplegado en Render" width="85%">
</div>

**Aplicación en producción:** `https://<nombre-del-servicio>.onrender.com`
<!-- Reemplazar con la URL real del servicio en Render. -->

---

## Seguridad

- Contraseñas almacenadas de forma cifrada, nunca en texto plano.
- Sesiones firmadas con una clave secreta generada automáticamente.
- Control de acceso por rol en cada ruta protegida del backend.
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

<!-- CAPTURA 15 (opcional): Fotografía del equipo. Guardar como docs/capturas/equipo.jpg -->

---

## Licencia

Este proyecto se distribuye bajo la licencia **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Consultar el archivo [`LICENSE`](LICENSE) para más información.

---

<div align="center">

**Universidad de Colima** · Ingeniería de Software · Proyecto Integrador de Tercer Semestre

</div>
