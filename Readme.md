# Portal de Información Institucional — Biblioteca

Sistema web completo para la gestión de una biblioteca institucional, desarrollado con Django. Incluye catálogo de libros, préstamos, repositorio de tesis, cuerpo docente, recursos digitales y un sistema de roles con aprobación por el bibliotecario.

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
- Un **repositorio de tesis** consultable con soporte para archivos PDF y contador de visualizaciones
- Un **directorio del cuerpo docente** con biografías y categorías
- Una sección de **recursos y novedades** (tutoriales, manuales, videos)
- Un sistema de **solicitudes de préstamo** donde los usuarios piden libros y el bibliotecario aprueba o rechaza
- Un sistema de **solicitudes de rol** donde el usuario elige su rol al registrarse y el bibliotecario lo aprueba
- Un **panel de control** para el bibliotecario con gráficas, estadísticas y tesis más consultadas
- Un **historial de actividad** personal para cada usuario con timeline de préstamos, solicitudes y renovaciones
- **Alertas visuales en el home** cuando el usuario tiene préstamos vencidos o próximos a vencer

---

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Backend | Django 6.x (Python) |
| Base de datos | SQLite (desarrollo) |
| Frontend | HTML, CSS personalizado, JavaScript |
| Gráficas | Chart.js 4.4 |
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
- Protección contra eliminación si el libro tiene préstamos registrados — muestra mensaje claro en lugar de error del sistema
- Historial de préstamos por libro visible para el bibliotecario

### 2. Préstamos
- Registro de préstamos asociando ejemplar, usuario y fecha límite
- Estados automáticos: **Activo**, **Vencido**, **Devuelto**
- El sistema detecta préstamos vencidos automáticamente al cargar la lista
- Registro de devoluciones con liberación automática del ejemplar
- Filtros por estado (activos / vencidos / devueltos)
- Vista diferenciada: el bibliotecario ve todos los préstamos; el estudiante/profesor solo los suyos
- Límite configurable de préstamos activos simultáneos por usuario (por defecto: 3)

### 3. Notificaciones por correo
- **Recordatorio**: se envía cuando faltan 2 días o menos para el vencimiento
- **Aviso de vencimiento**: se envía cuando el préstamo ya está vencido
- **Confirmación de aprobación**: se envía al usuario cuando su solicitud es aprobada
- **Notificación de rechazo**: se envía al usuario cuando su solicitud es rechazada
- **Confirmación de renovación**: se envía al usuario cuando su renovación es aprobada
- **Rechazo de renovación**: se envía al usuario cuando su renovación es rechazada
- Historial completo de todas las notificaciones enviadas con estado (exitoso/fallido)
- El bibliotecario puede enviar notificaciones manualmente desde el panel o la lista de préstamos
- Procesamiento masivo automático mediante el comando `enviar_notificaciones`

### 4. Solicitudes de préstamo
- Los estudiantes y profesores pueden solicitar libros disponibles directamente desde el catálogo
- El bibliotecario recibe la solicitud en su panel con el contador de pendientes
- Flujo de aprobación: el bibliotecario asigna el ejemplar y la fecha de devolución
- Flujo de rechazo: el bibliotecario escribe un motivo que llega al usuario por correo
- Los usuarios pueden ver el historial de todas sus solicitudes

### 5. Renovaciones de préstamo
- El usuario solicita extensión de plazo indicando los días deseados (entre 1 y 30)
- El bibliotecario aprueba con una nueva fecha o rechaza con un motivo
- El usuario recibe correo de confirmación o rechazo automáticamente
- No se puede renovar un préstamo que ya tiene una renovación pendiente

### 6. Repositorio de Tesis
- Registro de tesis con autor, tutor, año, tipo (licenciatura/maestría/doctorado) y área temática
- Campo **Registrado por** que guarda qué usuario subió la tesis
- Soporte para subir y visualizar archivos PDF directamente en el navegador
- Búsqueda por título, autor y área
- Filtrado por tipo de tesis
- Control de disponibilidad (el bibliotecario puede marcar una tesis como no disponible)
- **Contador de visualizaciones**: cada vez que alguien abre el detalle de una tesis se incrementa el contador
- Profesores y bibliotecarios pueden registrar y editar tesis; solo el bibliotecario puede eliminarlas

### 7. Cuerpo Docente
- Directorio de profesores con foto, biografía, especialidad y categoría docente
- Categorías: Titular, Auxiliar, Asistente, Instructor
- Ámbito: Nacional o Internacional (con país)
- Búsqueda por nombre, apellidos y especialidad
- Filtrado por categoría y ámbito

### 8. Recursos y Novedades
- Publicación de contenidos de cuatro tipos: **Novedades literarias**, **Tutoriales**, **Manuales**, **Videos**
- Soporte para archivos adjuntos descargables (PDF, DOC, etc.)
- Soporte para videos de YouTube con embed automático
- Opción de imagen de portada para cada recurso
- Marcado de recursos como destacados (aparecen en la página de inicio)
- Solo el bibliotecario puede crear, editar y eliminar recursos

### 9. Gestión de Usuarios y Roles
- Registro propio de nuevos usuarios con selección de rol solicitado (Estudiante o Profesor)
- El usuario queda como **Visitante** hasta que el bibliotecario aprueba su solicitud de rol
- El bibliotecario puede cambiar el rol aprobado desde la sección **Solicitudes de rol**
- Perfiles de usuario con foto, carnet/matrícula y teléfono
- Carnet digital imprimible con préstamos activos

### 10. Historial de actividad personal
- Timeline unificado con todos los eventos del usuario: préstamos, devoluciones, solicitudes y renovaciones
- Estadísticas rápidas: préstamos activos, vencidos, devueltos, solicitudes y renovaciones pendientes
- Accesible desde "Mi perfil" → "Ver mi actividad"

### 11. Alertas visuales en el home
- Si el usuario tiene préstamos **vencidos**, aparece un banner rojo con el nombre del libro y los días de retraso
- Si el usuario tiene préstamos **próximos a vencer** (2 días o menos), aparece un banner amarillo
- Si la solicitud de rol del usuario está **pendiente de aprobación**, aparece un banner informativo azul
- Las alertas son descartables con un botón de cierre

### 12. Panel del Bibliotecario
- Estadísticas generales del sistema (libros, ejemplares, tesis, usuarios, recursos)
- Contadores de solicitudes de préstamo, renovaciones y roles pendientes con acceso directo
- Gráfica de barras: préstamos registrados por mes (últimos 6 meses)
- Gráfica de dona: libros por categoría
- Gráfica de dona: estado del inventario (disponible/prestado/reservado/deteriorado)
- Listado de préstamos por vencer en los próximos 2 días con botón de notificación directa
- Listado de préstamos vencidos con días de retraso
- **Tesis más consultadas**: tabla con el top 5 de tesis por número de visualizaciones
- Historial de las últimas 8 notificaciones enviadas
- Resumen de notificaciones (total, exitosas, fallidas)
- Acciones rápidas: registrar libro, registrar préstamo, gestionar usuarios, ver correos, categorías, solicitudes de rol

### 13. Gestión de Categorías
- CRUD completo de categorías de libros desde el frontend (sin ir al admin de Django)
- Solo el bibliotecario puede crear, editar y eliminar categorías
- No se puede eliminar una categoría que tenga libros asociados

### 14. Búsqueda Global
- Busca simultáneamente en libros, tesis, profesores y recursos desde una sola barra
- Resultados agrupados por tipo con acceso directo a cada elemento

---

## Roles de usuario

| Rol | Qué puede hacer |
|---|---|
| **Visitante** | Ver catálogo, tesis, profesores y recursos. No puede solicitar préstamos. |
| **Estudiante** | Todo lo anterior + solicitar préstamos + ver sus solicitudes, préstamos y actividad |
| **Profesor** | Todo lo anterior + registrar y editar tesis |
| **Bibliotecario** | Acceso completo: gestión de libros, préstamos, usuarios, recursos, panel, notificaciones, categorías y roles |

> Al registrarse, el usuario elige si es Estudiante o Profesor y queda como **Visitante** hasta que el bibliotecario apruebe su solicitud desde el panel.

---

## Flujo de registro y aprobación de rol

1. El usuario va a `/registro/` y completa el formulario eligiendo su rol (Estudiante o Profesor)
2. Puede escribir información adicional como su número de matrícula o departamento
3. El sistema crea la cuenta con rol **Visitante** y guarda la solicitud de rol
4. El usuario puede navegar el portal pero no puede solicitar préstamos
5. El bibliotecario recibe la solicitud en el panel → **Solicitudes de rol**
6. El bibliotecario puede aprobar el rol solicitado, cambiarlo a otro, o rechazarlo
7. Una vez aprobado, el usuario tiene acceso completo a las funciones de su rol

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

```bash
pip install -r requirements.txt
```

Si no tienes `requirements.txt`, instala las dependencias manualmente:

```bash
pip install django pillow python-dotenv
```

---

### Paso 4 — Crear el archivo de configuración `.env`

En la raíz del proyecto (al mismo nivel que `manage.py`), crea un archivo llamado `.env`:

```env
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
```

> **Contraseña de aplicación de Gmail:** Gmail no acepta tu contraseña normal. Para generarla:
> 1. Ve a tu cuenta de Google → Seguridad → activa la verificación en dos pasos
> 2. Abre `myaccount.google.com/apppasswords`
> 3. Pon un nombre como "Portal Biblioteca" y haz clic en **Crear**
> 4. Copia la contraseña de 16 caracteres (ejemplo: `khrd agbj ygft wzvp`) y pégala en `.env`

Si no quieres configurar el correo ahora, edita `config/settings.py` y cambia temporalmente:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Los correos aparecerán en la terminal en lugar de enviarse.

---

### Paso 5 — Crear la base de datos

```bash
python manage.py migrate
```

---

### Paso 6 — Crear el superusuario

```bash
python manage.py createsuperuser
```

Este usuario tendrá acceso completo al sistema y al panel de Django en `/admin/`.

---

### Paso 7 — Crear la carpeta de medios

```bash
# En Windows:
mkdir media

# En macOS/Linux:
mkdir media
```

---

### Paso 8 — Iniciar el servidor

```bash
python manage.py runserver
```

Abre tu navegador en **http://127.0.0.1:8000**

---

## Poblar la base de datos con datos de prueba

```bash
python manage.py poblar_datos
```

Este comando crea:
- 8 categorías de libros
- 12 libros con entre 2 y 4 ejemplares cada uno
- 6 usuarios con diferentes roles (todos con `rol_aprobado = True`)
- 6 préstamos (algunos activos, algunos vencidos)
- 6 tesis en el repositorio
- 6 profesores en el directorio docente
- 6 recursos publicados (novedades, tutoriales, manuales, videos)

> Si ejecutas el comando varias veces no duplica los datos, usa `get_or_create` internamente.

---

## Usuarios de prueba

Después de ejecutar `poblar_datos`, todos los usuarios tienen la contraseña **`prueba1234`**:

| Usuario | Contraseña | Rol | Descripción |
|---|---|---|---|
| `bibliotecario1` | prueba1234 | Bibliotecario | Acceso completo al sistema y al panel |
| `estudiante1` | prueba1234 | Estudiante | Tiene préstamos vencidos asignados |
| `estudiante2` | prueba1234 | Estudiante | Tiene préstamos vencidos asignados |
| `estudiante3` | prueba1234 | Estudiante | Tiene un préstamo activo |
| `profesor1` | prueba1234 | Profesor | Puede registrar tesis y solicitar préstamos |
| `visitante1` | prueba1234 | Visitante | Solo puede navegar el catálogo |

---

## Comandos útiles

### Enviar notificaciones de correo

Revisa todos los préstamos y envía correos a usuarios con préstamos vencidos o próximos a vencer (solo si no han recibido notificación hoy):

```bash
python manage.py enviar_notificaciones
```

Para automatizarlo, configura un cron job (Linux/Mac):

```bash
0 8 * * * /ruta/al/proyecto/venv/bin/python /ruta/al/proyecto/manage.py enviar_notificaciones
```

### Panel de administración de Django

```
http://127.0.0.1:8000/admin/
```

### Restablecer la base de datos desde cero

```bash
# Windows:
del db.sqlite3

# macOS/Linux:
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
├── config/
│   ├── settings.py             # Configuración general, correo, límites
│   ├── urls.py                 # URLs raíz
│   └── views.py                # Home y registro (con alertas personalizadas por rol)
│
├── biblioteca/
│   ├── models.py               # Todos los modelos del sistema
│   ├── views.py                # Lógica de todas las vistas
│   ├── urls.py                 # URLs de la aplicación
│   ├── forms.py                # Formularios Django
│   ├── admin.py                # Configuración del panel admin
│   ├── signals.py              # Creación automática de perfil al registrarse
│   ├── decoradores.py          # Control de acceso por rol
│   ├── correo.py               # Envío de correos HTML
│   ├── context_processors.py   # Variables de rol en todos los templates
│   ├── management/
│   │   └── commands/
│   │       ├── enviar_notificaciones.py
│   │       └── poblar_datos.py
│   └── templatetags/
│       └── biblioteca_extras.py
│
├── templates/
│   ├── base.html
│   ├── home.html               # Con alertas visuales por rol
│   ├── biblioteca/
│   │   ├── libro_list.html
│   │   ├── libro_detail.html
│   │   ├── libro_confirmar_eliminar.html  # Con protección contra ProtectedError
│   │   ├── prestamo_list.html
│   │   ├── panel_bibliotecario.html       # Con tesis más consultadas
│   │   ├── mi_actividad.html              # Timeline personal del usuario
│   │   ├── solicitudes_rol.html           # Aprobación de roles por el bibliotecario
│   │   └── ...
│   ├── includes/
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   └── paginacion.html
│   └── registration/
│       ├── login.html
│       ├── registro.html       # Con selector visual de rol
│       └── logged_out.html
│
├── static/
│   ├── css/main.css            # Sistema de diseño con variables CSS
│   └── js/main.js              # Menú de usuario, alertas y validación de formularios
│
├── media/
├── .env
├── .gitignore
└── manage.py
```

---

## Flujo típico de uso del sistema

### Como estudiante o profesor:
1. Registrarse en `/registro/` eligiendo el rol deseado y enviando la solicitud
2. Navegar el portal como visitante mientras se espera aprobación
3. Una vez aprobado el rol, buscar un libro en `/biblioteca/libros/`
4. Solicitar el préstamo — el bibliotecario lo aprueba y llega un correo de confirmación
5. Ver los préstamos activos en `/biblioteca/prestamos/` o en "Mi actividad"
6. Si un préstamo está próximo a vencer, aparece una alerta en el home
7. Solicitar una renovación si se necesita más tiempo

### Como bibliotecario:
1. Iniciar sesión y acceder al panel en `/biblioteca/panel/`
2. Revisar las solicitudes de rol pendientes en **Solicitudes de rol**
3. Gestionar libros, ejemplares, tesis, profesores, categorías y recursos
4. Aprobar o rechazar solicitudes de préstamo en `/biblioteca/solicitudes/`
5. Registrar devoluciones desde la lista de préstamos
6. Enviar notificaciones masivas desde `/biblioteca/notificaciones/`
7. Consultar las tesis más visitadas en el panel de control

---

## Configuración avanzada

### Límite de préstamos activos por usuario

En `config/settings.py`:

```python
LIMITE_PRESTAMOS_ACTIVOS = 3  # Cambia este valor según las políticas de la biblioteca
```

### Correo en modo desarrollo (sin SMTP)

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Los correos se imprimirán en la terminal en lugar de enviarse realmente.

### Correo en producción (Gmail SMTP)

```python
EMAIL_BACKEND    = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST       = 'smtp.gmail.com'
EMAIL_PORT       = 587
EMAIL_USE_TLS    = True
EMAIL_HOST_USER  = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
```

---

## Solución de problemas frecuentes

**`ModuleNotFoundError: No module named 'dotenv'`**
```bash
pip install python-dotenv
```

**`ModuleNotFoundError: No module named 'PIL'`**
```bash
pip install pillow
```

**Los correos no se envían**

Verifica que `EMAIL_BACKEND` esté configurado como SMTP y que las credenciales en `.env` sean correctas. Para depurar usa `console.EmailBackend`.

**Las imágenes no se ven**

Verifica que la carpeta `media/` exista y que `config/urls.py` incluya:
```python
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Error `ProtectedError` al eliminar un libro**

El libro tiene préstamos registrados. Primero registra la devolución de todos los ejemplares prestados desde la lista de préstamos, luego podrás eliminarlo.

**Error al hacer migrate: tabla ya existe**

Elimina `db.sqlite3` y ejecuta `python manage.py migrate` de nuevo.

**Un usuario recién registrado no puede solicitar préstamos**

Su solicitud de rol está pendiente de aprobación. El bibliotecario debe ir a **Solicitudes de rol** en el panel y aprobarla.