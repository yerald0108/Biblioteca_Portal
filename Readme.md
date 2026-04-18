# Portal de Información Institucional — Biblioteca

Sistema web completo para la gestión de una biblioteca institucional, desarrollado con Django. Incluye catálogo de libros, préstamos, repositorio de tesis, cuerpo docente y recursos digitales.

---

## Tabla de contenidos

- [¿Qué hace este proyecto?](#qué-hace-este-proyecto)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Módulos del sistema](#módulos-del-sistema)
- [Roles de usuario](#roles-de-usuario)
- [Requisitos previos](#requisitos-previos)
- [Instalación paso a paso](#instalación-paso-a-paso)
- [Configuración del entorno](#configuración-del-entorno)
- [Poblar la base de datos con datos de prueba](#poblar-la-base-de-datos-con-datos-de-prueba)
- [Usuarios de prueba](#usuarios-de-prueba)
- [Comandos útiles](#comandos-útiles)
- [Estructura del proyecto](#estructura-del-proyecto)

---

## ¿Qué hace este proyecto?

Este portal resuelve el problema del control manual de préstamos y la falta de visibilidad digital del inventario físico de una biblioteca institucional. Centraliza en un solo lugar:

- El **catálogo digital** de todos los libros físicos con sus ejemplares
- El **control de préstamos** con seguimiento de estados y fechas de vencimiento
- Las **notificaciones automáticas por correo** cuando un préstamo vence o está próximo a vencer
- Un **repositorio de tesis** consultable con soporte para archivos PDF
- Un **directorio del cuerpo docente** con biografías y categorías
- Una sección de **recursos y novedades** (tutoriales, manuales, videos)
- Un sistema de **solicitudes de préstamo** donde los usuarios piden libros y el bibliotecario aprueba o rechaza
- Un **panel de control** para el bibliotecario con gráficas y estadísticas en tiempo real

---

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Backend | Django 6.x (Python) |
| Base de datos | SQLite (desarrollo) |
| Frontend | HTML, CSS personalizado, JavaScript |
| Gráficas | Chart.js |
| Correo electrónico | SMTP (Gmail u otro proveedor) |
| Tipografía | Google Fonts (Playfair Display + Source Sans 3) |

---

## Módulos del sistema

### 1. Gestión de Libros
- Catálogo completo con título, autor, editorial, año, ISBN y categoría
- Portada opcional por libro
- Ejemplares físicos por libro (cada uno con código, estado y ubicación en estantería)
- Búsqueda y filtrado por texto, categoría y estado de disponibilidad
- Paginación de resultados
- Alta, edición y baja de libros y ejemplares (solo bibliotecario)

### 2. Préstamos
- Registro de préstamos asociando ejemplar, usuario y fecha límite
- Estados automáticos: **Activo**, **Vencido**, **Devuelto**
- El sistema detecta préstamos vencidos automáticamente al cargar la lista
- Registro de devoluciones con liberación automática del ejemplar
- Filtros por estado (activos / vencidos / devueltos)
- Vista diferenciada: el bibliotecario ve todos los préstamos; el estudiante/profesor solo los suyos

### 3. Notificaciones por correo
- **Recordatorio**: se envía cuando faltan 2 días o menos para el vencimiento
- **Aviso de vencimiento**: se envía cuando el préstamo ya está vencido
- **Confirmación de aprobación**: se envía al usuario cuando su solicitud es aprobada
- **Notificación de rechazo**: se envía al usuario cuando su solicitud es rechazada
- Historial completo de todas las notificaciones enviadas con estado (exitoso/fallido)
- El bibliotecario puede enviar notificaciones manualmente desde el panel o la lista de préstamos
- Procesamiento masivo automático mediante el comando `enviar_notificaciones`

### 4. Solicitudes de préstamo
- Los estudiantes y profesores pueden solicitar libros disponibles directamente desde el catálogo
- El bibliotecario recibe la solicitud en su panel con el contador de pendientes
- Flujo de aprobación: el bibliotecario asigna el ejemplar y la fecha de devolución
- Flujo de rechazo: el bibliotecario escribe un motivo que llega al usuario por correo
- Los usuarios pueden ver el historial de todas sus solicitudes

### 5. Repositorio de Tesis
- Registro de tesis con autor, tutor, año, tipo (licenciatura/maestría/doctorado) y área temática
- Soporte para subir y visualizar archivos PDF directamente en el navegador
- Búsqueda por título, autor y área
- Filtrado por tipo de tesis
- Control de disponibilidad (el bibliotecario puede marcar una tesis como no disponible)
- Profesores y bibliotecarios pueden registrar nuevas tesis

### 6. Cuerpo Docente
- Directorio de profesores con foto, biografía, especialidad y categoría docente
- Categorías: Titular, Auxiliar, Asistente, Instructor
- Ámbito: Nacional o Internacional (con país)
- Búsqueda por nombre, apellidos y especialidad
- Filtrado por categoría y ámbito

### 7. Recursos y Novedades
- Publicación de contenidos de cuatro tipos: **Novedades literarias**, **Tutoriales**, **Manuales**, **Videos**
- Soporte para archivos adjuntos descargables (PDF, DOC, etc.)
- Soporte para videos de YouTube con embed automático
- Opción de imagen de portada para cada recurso
- Marcado de recursos como destacados (aparecen en la página de inicio)
- Solo el bibliotecario puede crear, editar y eliminar recursos

### 8. Gestión de Usuarios
- Registro propio de nuevos usuarios
- Perfiles de usuario con foto, carnet/matrícula y teléfono
- El bibliotecario puede cambiar el rol de cualquier usuario desde el panel
- Cada usuario puede editar sus propios datos desde "Mi perfil"

### 9. Panel del Bibliotecario
- Estadísticas generales del sistema (libros, ejemplares, tesis, usuarios, recursos)
- Contador de solicitudes pendientes con acceso rápido
- Gráfica de barras: préstamos registrados por mes (últimos 6 meses)
- Gráfica de dona: libros por categoría
- Gráfica de dona: estado del inventario (disponible/prestado/reservado/deteriorado)
- Listado de préstamos por vencer en los próximos 2 días con botón de notificación directa
- Listado de préstamos vencidos con días de retraso
- Historial de las últimas 8 notificaciones enviadas
- Resumen de notificaciones (total, exitosas, fallidas)
- Acciones rápidas: registrar libro, registrar préstamo, gestionar usuarios, ver correos

---

## Roles de usuario

| Rol | Qué puede hacer |
|---|---|
| **Visitante** | Ver catálogo, tesis, profesores y recursos. No puede solicitar préstamos. |
| **Estudiante** | Todo lo anterior + solicitar préstamos + ver sus solicitudes y préstamos |
| **Profesor** | Todo lo anterior + registrar y editar tesis |
| **Bibliotecario** | Acceso completo: gestión de libros, préstamos, usuarios, recursos, panel, notificaciones |

> Los usuarios nuevos que se registran solos reciben el rol **Visitante** por defecto. El bibliotecario debe cambiarles el rol manualmente desde la gestión de usuarios.

---

## Requisitos previos

Antes de instalar, asegúrate de tener instalado en tu PC:

- **Python 3.10 o superior** — [python.org/downloads](https://www.python.org/downloads/)
- **pip** (viene incluido con Python)
- **Git** — [git-scm.com](https://git-scm.com/) (opcional, para clonar el repositorio)

Para verificar que los tienes instalados, abre una terminal y ejecuta:

```bash
python --version
pip --version
```

---

## Instalación paso a paso

### Paso 1 — Obtener el código

**Opción A: Clonar con Git**
```bash
git clone https://github.com/tu-usuario/biblioteca-portal.git
cd biblioteca-portal
```

**Opción B: Descargar el ZIP**

Descarga el archivo ZIP del proyecto, descomprímelo y entra a la carpeta desde la terminal.

---

### Paso 2 — Crear el entorno virtual

Un entorno virtual aísla las dependencias del proyecto para que no interfieran con otros proyectos Python en tu PC.

**En Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```

**En macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

Sabrás que el entorno está activo porque verás `(venv)` al inicio de tu línea de comandos.

---

### Paso 3 — Instalar las dependencias

Con el entorno virtual activo, instala todas las librerías necesarias:

```bash
pip install django
pip install pillow
pip install python-dotenv
```

O si el proyecto tiene un archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### Paso 4 — Crear el archivo de configuración `.env`

En la raíz del proyecto (al mismo nivel que `manage.py`), crea un archivo llamado `.env` con el siguiente contenido:

```env
# Correo saliente (necesario para las notificaciones)
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
```

> **Importante sobre la contraseña de Gmail:** Gmail no acepta tu contraseña normal. Debes generar una "Contraseña de aplicación":
> 1. Ve a tu cuenta de Google → Seguridad
> 2. Activa la verificación en dos pasos
> 3. Busca "Contraseñas de aplicación" y genera una para "Correo"
> 4. Usa esa contraseña de 16 caracteres en el `.env`

Si no quieres configurar el correo ahora y solo quieres probar el sistema, edita `config/settings.py` y cambia temporalmente:

```python
# Cambia esta línea:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Por esta (imprime los correos en la terminal en vez de enviarlos):
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

### Paso 5 — Crear la base de datos

Este comando crea todas las tablas necesarias en la base de datos SQLite:

```bash
python manage.py migrate
```

Verás una lista de migraciones aplicadas. Al terminar, se crea automáticamente el archivo `db.sqlite3` en la raíz del proyecto.

---

### Paso 6 — Crear el superusuario (administrador)

```bash
python manage.py createsuperuser
```

El sistema te pedirá:
- **Username:** el nombre de usuario que usarás para entrar (por ejemplo: `admin`)
- **Email:** tu correo electrónico
- **Password:** tu contraseña (no se muestra al escribir, es normal)

Este usuario tendrá acceso completo al sistema y al panel de Django en `/admin/`.

---

### Paso 7 — Crear la carpeta de medios

Django necesita una carpeta donde guardar las imágenes y archivos subidos:

```bash
# En Windows:
mkdir media

# En macOS/Linux:
mkdir media
```

---

### Paso 8 — Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

Verás algo así en la terminal:

```
Django version 6.x, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Abre tu navegador y ve a **http://127.0.0.1:8000**

---

## Poblar la base de datos con datos de prueba

El proyecto incluye un comando que crea automáticamente libros, usuarios, préstamos, tesis, profesores y recursos de ejemplo para que puedas explorar el sistema sin tener que cargar datos manualmente:

```bash
python manage.py poblar_datos
```

Este comando crea:
- 8 categorías de libros
- 12 libros con entre 2 y 4 ejemplares cada uno
- 6 usuarios con diferentes roles
- 6 préstamos (algunos activos, algunos vencidos)
- 6 tesis en el repositorio
- 6 profesores en el directorio docente
- 6 recursos publicados (novedades, tutoriales, manuales, videos)

> Si ejecutas el comando varias veces, no duplica los datos (usa `get_or_create` internamente).

---

## Usuarios de prueba

Después de ejecutar `poblar_datos`, puedes iniciar sesión con cualquiera de estos usuarios. La contraseña de todos es **`prueba1234`**:

| Usuario | Rol | Descripción |
|---|---|---|
| `bibliotecario1` | Bibliotecario | Acceso completo al sistema y al panel |
| `estudiante1` | Estudiante | Puede solicitar préstamos y ver sus solicitudes |
| `estudiante2` | Estudiante | Tiene préstamos vencidos asignados |
| `estudiante3` | Estudiante | Tiene un préstamo activo |
| `profesor1` | Profesor | Puede registrar tesis y solicitar préstamos |
| `visitante1` | Visitante | Solo puede navegar el catálogo |

El superusuario que creaste en el Paso 6 también puede entrar con sus credenciales.

---

## Comandos útiles

### Enviar notificaciones de correo manualmente

Este comando revisa todos los préstamos y envía correos a los usuarios que tienen préstamos vencidos o que vencen en los próximos 2 días, siempre que no hayan recibido ya una notificación hoy:

```bash
python manage.py enviar_notificaciones
```

Para automatizarlo en producción, puedes configurar un cron job (Linux) o una tarea programada (Windows) que lo ejecute una vez al día.

**Ejemplo de cron job (Linux/Mac) — ejecutar todos los días a las 8 AM:**
```bash
0 8 * * * /ruta/al/proyecto/venv/bin/python /ruta/al/proyecto/manage.py enviar_notificaciones
```

### Acceder al panel de administración de Django

El panel nativo de Django está disponible en:

```
http://127.0.0.1:8000/admin/
```

Entra con el superusuario que creaste. Desde aquí puedes gestionar directamente todos los modelos de la base de datos.

### Crear un nuevo superusuario adicional

```bash
python manage.py createsuperuser
```

### Ver todas las URLs disponibles del proyecto

```bash
python manage.py show_urls
```

### Restablecer la base de datos desde cero

Si quieres empezar de cero, elimina el archivo `db.sqlite3` y vuelve a ejecutar los pasos 5 y 6:

```bash
# En Windows:
del db.sqlite3

# En macOS/Linux:
rm db.sqlite3

python manage.py migrate
python manage.py createsuperuser
python manage.py poblar_datos
```

---

## Estructura del proyecto

```
biblioteca-portal/
│
├── config/                     # Configuración principal del proyecto Django
│   ├── settings.py             # Configuración: base de datos, correo, apps, etc.
│   ├── urls.py                 # URLs raíz del proyecto
│   └── views.py                # Vistas globales (home, registro)
│
├── biblioteca/                 # Aplicación principal
│   ├── models.py               # Modelos de datos (Libro, Ejemplar, Préstamo, etc.)
│   ├── views.py                # Lógica de todas las vistas
│   ├── urls.py                 # URLs de la aplicación biblioteca
│   ├── forms.py                # Formularios Django
│   ├── admin.py                # Configuración del panel de administración
│   ├── signals.py              # Señales (creación automática de perfil al registrarse)
│   ├── decoradores.py          # Decoradores de control de acceso por rol
│   ├── correo.py               # Lógica de envío de correos HTML
│   ├── context_processors.py   # Inyecta variables de rol en todos los templates
│   ├── management/
│   │   └── commands/
│   │       ├── enviar_notificaciones.py   # Comando para envío masivo de correos
│   │       └── poblar_datos.py            # Comando para datos de prueba
│   └── templatetags/
│       └── biblioteca_extras.py           # Filtros y tags personalizados
│
├── templates/                  # Plantillas HTML
│   ├── base.html               # Plantilla base (navbar, footer, mensajes)
│   ├── home.html               # Página de inicio
│   ├── biblioteca/             # Templates de cada módulo
│   │   ├── libro_list.html
│   │   ├── libro_detail.html
│   │   ├── prestamo_list.html
│   │   ├── panel_bibliotecario.html
│   │   └── ...
│   ├── includes/               # Fragmentos reutilizables
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   └── paginacion.html
│   └── registration/           # Login, registro, logout
│
├── static/
│   ├── css/main.css            # Sistema de diseño completo con variables CSS
│   └── js/main.js              # JavaScript básico (cierre automático de alertas)
│
├── media/                      # Archivos subidos por los usuarios (no incluido en git)
├── .env                        # Variables de entorno sensibles (no incluido en git)
├── .gitignore
└── manage.py                   # Punto de entrada de Django
```

---

## Flujo típico de uso del sistema

### Como estudiante o profesor:
1. Registrarse en `/registro/` o iniciar sesión
2. El bibliotecario cambia el rol desde el panel de usuarios
3. Buscar un libro en el catálogo (`/biblioteca/libros/`)
4. Hacer clic en "Solicitar préstamo" en la página del libro
5. El bibliotecario aprueba la solicitud y el usuario recibe un correo de confirmación
6. El usuario ve sus préstamos activos en `/biblioteca/prestamos/` o en "Mi perfil"
7. Recibe un correo de recordatorio 2 días antes del vencimiento

### Como bibliotecario:
1. Iniciar sesión con una cuenta staff
2. Acceder al panel en `/biblioteca/panel/`
3. Gestionar libros, ejemplares, tesis, profesores y recursos
4. Revisar y gestionar solicitudes de préstamo en `/biblioteca/solicitudes/`
5. Registrar devoluciones desde la lista de préstamos
6. Enviar notificaciones masivas desde `/biblioteca/notificaciones/`

---

## Solución de problemas frecuentes

**Error: `ModuleNotFoundError: No module named 'dotenv'`**
```bash
pip install python-dotenv
```

**Error: `ModuleNotFoundError: No module named 'PIL'`**
```bash
pip install pillow
```

**Los correos no se envían**

Verifica en `config/settings.py` que `EMAIL_BACKEND` esté configurado como SMTP y que las credenciales en `.env` sean correctas. Para depurar, cámbialo temporalmente a `console.EmailBackend` — los correos aparecerán en la terminal.

**El servidor arranca pero las imágenes no se ven**

Asegúrate de que la carpeta `media/` exista en la raíz del proyecto y de que `config/urls.py` incluya:
```python
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
(Ya está incluido en el proyecto por defecto.)

**Error al hacer migrate: tabla ya existe**

Elimina el archivo `db.sqlite3` y vuelve a ejecutar `python manage.py migrate`.