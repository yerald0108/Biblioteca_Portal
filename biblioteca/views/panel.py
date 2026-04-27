# biblioteca/views/panel.py

import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.models import User

from biblioteca.decoradores import solo_bibliotecario
from biblioteca.models import (
    Libro, Ejemplar, Tesis, Profesor, Recurso, Prestamo,
    PerfilUsuario, SolicitudPrestamo, RenovacionPrestamo,
    NotificacionCorreo,
)


@login_required
@solo_bibliotecario
def panel_bibliotecario(request):
    """
    Panel de control del bibliotecario con estadísticas, gráficos y alertas.
    La actualización masiva de préstamos vencidos debe ejecutarse como
    tarea programada (cron/celery), no en cada carga de página.
    """
    hoy = timezone.now().date()

    stats = {
        'total_libros': Libro.objects.count(),
        'total_ejemplares': Ejemplar.objects.count(),
        'total_tesis': Tesis.objects.count(),
        'total_profesores': Profesor.objects.filter(activo=True).count(),
        'total_usuarios': User.objects.count(),
        'total_recursos': Recurso.objects.filter(publicado=True).count(),
    }

    solicitudes_pendientes = SolicitudPrestamo.objects.filter(estado='pendiente').count()
    renovaciones_pendientes = RenovacionPrestamo.objects.filter(estado='pendiente').count()
    roles_pendientes = PerfilUsuario.objects.filter(
        rol_solicitado__isnull=False, rol_aprobado=False
    ).count()
    tesis_populares = Tesis.objects.order_by('-vistas')[:5]

    prestamos_activos = Prestamo.objects.filter(estado='activo').count()
    prestamos_vencidos = Prestamo.objects.filter(estado='vencido').count()

    prestamos_por_vencer = Prestamo.objects.filter(
        estado='activo',
        fecha_devolucion__lte=hoy + timezone.timedelta(days=2),
        fecha_devolucion__gte=hoy,
    ).select_related('ejemplar__libro', 'usuario')

    prestamos_vencidos_lista = Prestamo.objects.filter(
        estado='vencido'
    ).select_related('ejemplar__libro', 'usuario')[:10]

    ultimos_libros = Libro.objects.order_by('-fecha_registro')[:5]

    ultimas_notificaciones = NotificacionCorreo.objects.select_related(
        'prestamo__usuario', 'prestamo__ejemplar__libro'
    ).order_by('-enviado_en')[:8]

    total_notificaciones = NotificacionCorreo.objects.count()
    notif_exitosas = NotificacionCorreo.objects.filter(exitoso=True).count()
    notif_fallidas = NotificacionCorreo.objects.filter(exitoso=False).count()

    # Datos para gráficas
    labels_meses = []
    valores_meses = []
    nombres_meses = [
        'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
    ]
    for i in range(5, -1, -1):
        fecha = hoy - timezone.timedelta(days=30 * i)
        count = Prestamo.objects.filter(
            fecha_prestamo__year=fecha.year,
            fecha_prestamo__month=fecha.month,
        ).count()
        labels_meses.append(nombres_meses[fecha.month - 1])
        valores_meses.append(count)

    datos_prestamos_json = json.dumps({
        'labels': labels_meses,
        'valores': valores_meses,
    })

    cats = (
        Libro.objects.values('categoria__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    datos_categorias_json = json.dumps({
        'labels': [c['categoria__nombre'] or 'Sin categoría' for c in cats],
        'valores': [c['total'] for c in cats],
    })

    estados = {'disponible': 0, 'prestado': 0, 'reservado': 0, 'deteriorado': 0}
    for ej in Ejemplar.objects.values('estado').annotate(total=Count('id')):
        if ej['estado'] in estados:
            estados[ej['estado']] = ej['total']
    datos_inventario_json = json.dumps(list(estados.values()))

    usuarios = User.objects.select_related('perfil').order_by('-date_joined')

    return render(request, 'biblioteca/panel_bibliotecario.html', {
        'stats': stats,
        'prestamos_activos': prestamos_activos,
        'prestamos_vencidos': prestamos_vencidos,
        'prestamos_por_vencer': prestamos_por_vencer,
        'prestamos_vencidos_lista': prestamos_vencidos_lista,
        'ultimos_libros': ultimos_libros,
        'usuarios': usuarios,
        'datos_prestamos_json': datos_prestamos_json,
        'datos_categorias_json': datos_categorias_json,
        'datos_inventario_json': datos_inventario_json,
        'solicitudes_pendientes': solicitudes_pendientes,
        'renovaciones_pendientes': renovaciones_pendientes,
        'roles_pendientes': roles_pendientes,
        'tesis_populares': tesis_populares,
        'ultimas_notificaciones': ultimas_notificaciones,
        'total_notificaciones': total_notificaciones,
        'notif_exitosas': notif_exitosas,
        'notif_fallidas': notif_fallidas,
    })