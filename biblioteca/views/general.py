# biblioteca/views/general.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

from biblioteca.models import (
    Libro, Tesis, Profesor, Recurso, PerfilUsuario, Prestamo,
    SolicitudPrestamo, RenovacionPrestamo
)
from biblioteca.forms import BusquedaForm


def paginar(queryset, request, por_pagina=10):
    """Helper de paginación reutilizable."""
    paginator = Paginator(queryset, por_pagina)
    pagina = request.GET.get('pagina', 1)
    return paginator.get_page(pagina)


@login_required
def busqueda_global(request):
    q = request.GET.get('q', '').strip()

    libros = []
    tesis = []
    profesores = []
    recursos = []

    if q:
        libros = Libro.objects.filter(
            Q(titulo__icontains=q) |
            Q(autor__icontains=q) |
            Q(isbn__icontains=q)
        ).select_related('categoria')[:8]

        tesis = Tesis.objects.filter(
            Q(titulo__icontains=q) |
            Q(autor__icontains=q) |
            Q(area__icontains=q) |
            Q(resumen__icontains=q)
        )[:6]

        profesores = Profesor.objects.filter(
            Q(nombre__icontains=q) |
            Q(apellidos__icontains=q) |
            Q(especialidad__icontains=q),
            activo=True
        )[:6]

        recursos = Recurso.objects.filter(
            Q(titulo__icontains=q) |
            Q(descripcion__icontains=q),
            publicado=True
        )[:6]

    total = len(libros) + len(tesis) + len(profesores) + len(recursos)

    return render(request, 'biblioteca/busqueda_global.html', {
        'q': q,
        'libros': libros,
        'tesis': tesis,
        'profesores': profesores,
        'recursos': recursos,
        'total': total,
    })


@login_required
def carnet_biblioteca(request):
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)
    prestamos_activos = Prestamo.objects.filter(
        usuario=request.user,
        estado__in=['activo', 'vencido']
    ).select_related('ejemplar__libro').order_by('fecha_devolucion')

    return render(request, 'biblioteca/carnet.html', {
        'perfil': perfil,
        'prestamos_activos': prestamos_activos,
    })


@login_required
def mi_actividad(request):
    # Recopilar todos los eventos del usuario
    prestamos = Prestamo.objects.filter(
        usuario=request.user
    ).select_related('ejemplar__libro').order_by('-fecha_prestamo')

    solicitudes = SolicitudPrestamo.objects.filter(
        usuario=request.user
    ).select_related('libro').order_by('-fecha_solicitud')

    renovaciones = RenovacionPrestamo.objects.filter(
        usuario=request.user
    ).select_related('prestamo__ejemplar__libro').order_by('-fecha_solicitud')

    # Construir timeline unificado
    eventos = []

    for p in prestamos:
        eventos.append({
            'tipo': 'prestamo',
            'fecha': p.fecha_prestamo,
            'titulo': p.ejemplar.libro.titulo,
            'subtipo': p.estado,
            'objeto': p,
            'icono': '📚',
            'color': 'azul',
        })
        if p.estado == 'devuelto' and p.fecha_devuelto:
            eventos.append({
                'tipo': 'devolucion',
                'fecha': p.fecha_devuelto,
                'titulo': p.ejemplar.libro.titulo,
                'subtipo': 'devuelto',
                'objeto': p,
                'icono': '✅',
                'color': 'verde',
            })

    for s in solicitudes:
        color = 'ambar' if s.estado == 'pendiente' else 'verde' if s.estado == 'aprobada' else 'rojo'
        eventos.append({
            'tipo': 'solicitud',
            'fecha': s.fecha_solicitud,
            'titulo': s.libro.titulo,
            'subtipo': s.estado,
            'objeto': s,
            'icono': '📋',
            'color': color,
        })

    for r in renovaciones:
        color = 'ambar' if r.estado == 'pendiente' else 'verde' if r.estado == 'aprobada' else 'rojo'
        eventos.append({
            'tipo': 'renovacion',
            'fecha': r.fecha_solicitud,
            'titulo': r.prestamo.ejemplar.libro.titulo,
            'subtipo': r.estado,
            'objeto': r,
            'icono': '🔄',
            'color': color,
        })

    eventos.sort(key=lambda e: e['fecha'], reverse=True)

    stats = {
        'prestamos_activos': prestamos.filter(estado='activo').count(),
        'prestamos_vencidos': prestamos.filter(estado='vencido').count(),
        'prestamos_devueltos': prestamos.filter(estado='devuelto').count(),
        'solicitudes_pendientes': solicitudes.filter(estado='pendiente').count(),
        'solicitudes_aprobadas': solicitudes.filter(estado='aprobada').count(),
        'renovaciones_pendientes': renovaciones.filter(estado='pendiente').count(),
    }

    return render(request, 'biblioteca/mi_actividad.html', {
        'eventos': eventos,
        'stats': stats,
    })