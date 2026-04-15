from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Categoria(models.Model):
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering            = ['nombre']

    def __str__(self):
        return self.nombre

class Libro(models.Model):
    titulo    = models.CharField(max_length=300)
    autor     = models.CharField(max_length=200)
    editorial = models.CharField(max_length=200, blank=True)
    anio      = models.PositiveIntegerField(verbose_name='Año', null=True, blank=True)
    isbn      = models.CharField(max_length=20, blank=True, unique=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='libros')
    descripcion  = models.TextField(blank=True)
    portada      = models.ImageField(upload_to='portadas/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Libro'
        verbose_name_plural = 'Libros'
        ordering            = ['titulo']

    def __str__(self):
        return f'{self.titulo} — {self.autor}'

    def ejemplares_disponibles(self):
        return self.ejemplares.filter(estado='disponible').count()

    def total_ejemplares(self):
        return self.ejemplares.count()

class Ejemplar(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('prestado',   'Prestado'),
        ('reservado',  'Reservado'),
        ('deteriorado','Deteriorado'),
    ]

    libro    = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='ejemplares')
    codigo   = models.CharField(max_length=50, unique=True, verbose_name='Código')
    estado   = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    ubicacion = models.CharField(max_length=100, blank=True,
                                  verbose_name='Ubicación en estantería')
    notas    = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Ejemplar'
        verbose_name_plural = 'Ejemplares'

    def __str__(self):
        return f'{self.codigo} — {self.libro.titulo}'

class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('activo',     'Activo'),
        ('devuelto',   'Devuelto'),
        ('vencido',    'Vencido'),
    ]

    ejemplar      = models.ForeignKey(Ejemplar, on_delete=models.PROTECT,
                                       related_name='prestamos')
    usuario       = models.ForeignKey(User, on_delete=models.PROTECT,
                                       related_name='prestamos')
    fecha_prestamo  = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateField(verbose_name='Fecha límite de devolución')
    fecha_devuelto  = models.DateTimeField(null=True, blank=True)
    estado          = models.CharField(max_length=20, choices=ESTADO_CHOICES,
                                        default='activo')
    notas           = models.TextField(blank=True)
    registrado_por  = models.ForeignKey(User, on_delete=models.SET_NULL,
                                         null=True, related_name='prestamos_registrados')

    class Meta:
        verbose_name        = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering            = ['-fecha_prestamo']

    def __str__(self):
        return f'{self.ejemplar.codigo} → {self.usuario.get_full_name() or self.usuario.username}'

    def esta_vencido(self):
        if self.estado == 'devuelto':
            return False
        return timezone.now().date() > self.fecha_devolucion

    def dias_restantes(self):
        delta = self.fecha_devolucion - timezone.now().date()
        return delta.days

    def save(self, *args, **kwargs):
        if self.esta_vencido() and self.estado == 'activo':
            self.estado = 'vencido'
        super().save(*args, **kwargs)

class NotificacionCorreo(models.Model):
    prestamo   = models.ForeignKey(Prestamo, on_delete=models.CASCADE,
                                    related_name='notificaciones')
    tipo       = models.CharField(max_length=50)   # 'vencimiento', 'recordatorio'
    enviado_en = models.DateTimeField(auto_now_add=True)
    exitoso    = models.BooleanField(default=False)
    mensaje    = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Notificación de correo'
        verbose_name_plural = 'Notificaciones de correo'
        
class Tesis(models.Model):
    TIPO_CHOICES = [
        ('licenciatura', 'Licenciatura'),
        ('maestria',     'Maestría'),
        ('doctorado',    'Doctorado'),
    ]

    titulo      = models.CharField(max_length=400)
    autor       = models.CharField(max_length=200)
    tutor       = models.CharField(max_length=200, blank=True)
    anio        = models.PositiveIntegerField(verbose_name='Año')
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES,
                                    default='licenciatura')
    area        = models.CharField(max_length=200, verbose_name='Área temática')
    resumen     = models.TextField(blank=True)
    archivo_pdf = models.FileField(upload_to='tesis/', null=True, blank=True,
                                    verbose_name='Archivo PDF')
    disponible  = models.BooleanField(default=True,
                                       verbose_name='Disponible para consulta')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Tesis'
        verbose_name_plural = 'Tesis'
        ordering            = ['-anio', 'titulo']

    def __str__(self):
        return f'{self.titulo} ({self.anio})'
    
class Profesor(models.Model):
    CATEGORIA_CHOICES = [
        ('titular',    'Titular'),
        ('auxiliar',   'Auxiliar'),
        ('asistente',  'Asistente'),
        ('instructor', 'Instructor'),
    ]

    AMBITO_CHOICES = [
        ('nacional',       'Nacional'),
        ('internacional',  'Internacional'),
    ]

    nombre        = models.CharField(max_length=200)
    apellidos     = models.CharField(max_length=200)
    categoria     = models.CharField(max_length=20, choices=CATEGORIA_CHOICES,
                                      default='titular')
    ambito        = models.CharField(max_length=20, choices=AMBITO_CHOICES,
                                      default='nacional')
    pais          = models.CharField(max_length=100, blank=True,
                                      verbose_name='País (si es internacional)')
    especialidad  = models.CharField(max_length=200)
    biografia     = models.TextField(blank=True, verbose_name='Biografía')
    email         = models.EmailField(blank=True)
    foto          = models.ImageField(upload_to='profesores/', null=True, blank=True)
    activo        = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Profesor'
        verbose_name_plural = 'Profesores'
        ordering            = ['apellidos', 'nombre']

    def __str__(self):
        return f'{self.apellidos}, {self.nombre}'

    def nombre_completo(self):
        return f'{self.nombre} {self.apellidos}'

    def iniciales(self):
        partes = self.nombre.split() + self.apellidos.split()
        return ''.join(p[0] for p in partes[:2]).upper()
    
class Recurso(models.Model):
    TIPO_CHOICES = [
        ('novedad',   'Novedad literaria'),
        ('tutorial',  'Tutorial'),
        ('manual',    'Manual'),
        ('video',     'Video'),
    ]

    titulo      = models.CharField(max_length=300)
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True)
    archivo     = models.FileField(upload_to='recursos/', null=True, blank=True,
                                    verbose_name='Archivo (PDF, DOC...)')
    url_video   = models.URLField(blank=True, verbose_name='URL del video (YouTube, etc.)')
    imagen      = models.ImageField(upload_to='recursos/imagenes/', null=True, blank=True)
    publicado   = models.BooleanField(default=True)
    destacado   = models.BooleanField(default=False,
                                       verbose_name='Destacar en inicio')
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    autor       = models.ForeignKey(User, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='recursos',
                                     verbose_name='Publicado por')

    class Meta:
        verbose_name        = 'Recurso'
        verbose_name_plural = 'Recursos'
        ordering            = ['-fecha_publicacion']

    def __str__(self):
        return f'[{self.get_tipo_display()}] {self.titulo}'

    def tiene_archivo(self):
        return bool(self.archivo)

    def tiene_video(self):
        return bool(self.url_video)

    def embed_url(self):
        """Convierte URL de YouTube a formato embed."""
        url = self.url_video
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('watch?v=')[-1].split('&')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        return url