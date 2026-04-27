# biblioteca/views/notificaciones.py

from django.shortcuts import render, redirect
from django.contrib import messages

from biblioteca.decoradores import solo_bibliotecario
from biblioteca.models import Prestamo, NotificacionCorreo
from biblioteca.correo import procesar_notificaciones_pendientes
from .general import paginar


@solo_bibliotecario
def notificaciones_list(request):
    """Listado de notificaciones y envío masivo manual."""
    if request.method == 'POST' and request.POST.get('accion') == 'enviar_masivo':
        enviados = procesar_notificaciones_pendientes()
        messages.success(
            request,
            f'{enviados} notificación(es) enviada(s) correctamente.'
        )
        return redirect('biblioteca:notificaciones')

    notificaciones = NotificacionCorreo.objects.select_related(
        'prestamo__usuario',
        'prestamo__ejemplar__libro'
    ).order_by('-enviado_en')

    tipo_filtro = request.GET.get('tipo', '')
    exito_filtro = request.GET.get('exitoso', '')

    if tipo_filtro:
        notificaciones = notificaciones.filter(tipo=tipo_filtro)
    if exito_filtro:
        notificaciones = notificaciones.filter(exitoso=(exito_filtro == '1'))

    return render(request, 'biblioteca/notificaciones_list.html', {
        'notificaciones': paginar(notificaciones, request, 20),
        'tipo_filtro': tipo_filtro,
        'exito_filtro': exito_filtro,
        'total': NotificacionCorreo.objects.count(),
        'total_exitosas': NotificacionCorreo.objects.filter(exitoso=True).count(),
        'total_fallidas': NotificacionCorreo.objects.filter(exitoso=False).count(),
        'total_pendientes_envio': Prestamo.objects.filter(estado='vencido').count(),
    })