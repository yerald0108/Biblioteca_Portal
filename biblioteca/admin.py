from django.contrib import admin
from .models import Categoria, Libro, Ejemplar, Prestamo, Profesor, NotificacionCorreo, Tesis, Recurso, PerfilUsuario, SolicitudPrestamo, RenovacionPrestamo

class EjemplarInline(admin.TabularInline):
    model  = Ejemplar
    extra  = 1
    fields = ['codigo', 'estado', 'ubicacion']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display  = ['titulo', 'autor', 'categoria', 'anio', 'fecha_registro']
    list_filter   = ['categoria']
    search_fields = ['titulo', 'autor', 'isbn']
    inlines       = [EjemplarInline]

@admin.register(Ejemplar)
class EjemplarAdmin(admin.ModelAdmin):
    list_display  = ['codigo', 'libro', 'estado', 'ubicacion']
    list_filter   = ['estado']
    search_fields = ['codigo', 'libro__titulo']

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display  = ['ejemplar', 'usuario', 'fecha_devolucion', 'estado']
    list_filter   = ['estado']
    search_fields = ['ejemplar__codigo', 'usuario__username']

@admin.register(NotificacionCorreo)
class NotificacionCorreoAdmin(admin.ModelAdmin):
    list_display = ['prestamo', 'tipo', 'enviado_en', 'exitoso']
    
@admin.register(Tesis)
class TesisAdmin(admin.ModelAdmin):
    list_display  = ['titulo', 'autor', 'tipo', 'anio', 'area', 'disponible']
    list_filter   = ['tipo', 'disponible', 'anio']
    search_fields = ['titulo', 'autor', 'area']
    list_editable = ['disponible']

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display  = ['apellidos', 'nombre', 'categoria', 'ambito', 'especialidad', 'activo']
    list_filter   = ['categoria', 'ambito', 'activo']
    search_fields = ['nombre', 'apellidos', 'especialidad']
    list_editable = ['activo']

@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display  = ['titulo', 'tipo', 'publicado', 'destacado', 'fecha_publicacion']
    list_filter   = ['tipo', 'publicado', 'destacado']
    search_fields = ['titulo', 'descripcion']
    list_editable = ['publicado', 'destacado']
    
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display  = ['usuario', 'rol', 'carnet', 'telefono']
    list_filter   = ['rol']
    search_fields = ['usuario__username', 'usuario__first_name', 'carnet']
    list_editable = ['rol']
    
@admin.register(SolicitudPrestamo)
class SolicitudPrestamoAdmin(admin.ModelAdmin):
    list_display  = ['usuario', 'libro', 'estado', 'fecha_solicitud']
    list_filter   = ['estado']
    search_fields = ['usuario__username', 'libro__titulo']
    
@admin.register(RenovacionPrestamo)
class RenovacionPrestamoAdmin(admin.ModelAdmin):
    list_display  = ['prestamo', 'usuario', 'dias_solicitados', 'estado', 'fecha_solicitud']
    list_filter   = ['estado']
    search_fields = ['usuario__username', 'prestamo__ejemplar__libro__titulo']