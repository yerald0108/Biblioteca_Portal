# biblioteca/views/solicitudes.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

from biblioteca.decoradores import solo_bibliotecario, rol_requerido
from biblioteca.models import Libro, Prestamo, SolicitudPrestamo
from biblioteca.forms import (
    SolicitudPrestamoForm,
    AprobarSolicitudForm,
    RechazarSolicitudForm,
)
from biblioteca.correo import (
    enviar_confirmacion_prestamo,
    enviar_rechazo_solicitud,
)
from .general import paginar


@rol_requerido('estudiante', 'profesor', 'bibliotecario')
def solicitud_crear(request, libro_pk):
    libro = get_object_or_404(Libro, pk=libro_pk)

    if not libro.ejemplares_disponibles():
        messages.error(request, 'Este libro no tiene ejemplares disponibles.')
        return redirect('biblioteca:libro_detail', pk=libro_pk)

    limite = getattr(settings, 'LIMITE_PRESTAMOS_ACTIVOS', 3)
    prestamos_activos = Prestamo.objects.filter(
        usuario=request.user,
        estado__in=['activo', 'vencido']
    ).count()
    if prestamos_activos >= limite:
        messages.error(
            request,
            f'Has alcanzado el límite de {limite} préstamos activos simultáneos. '
            f'Debes devolver un libro antes de solicitar otro.'
        )
        return redirect('biblioteca:libro_detail', pk=libro_pk)

    solicitud_existente = SolicitudPrestamo.objects.filter(
        usuario=request.user,
        libro=libro,
        estado='pendiente'
    ).exists()
    if solicitud_existente:
        messages.warning(request, 'Ya tienes una solicitud pendiente para este libro.')
        return redirect('biblioteca:libro_detail', pk=libro_pk)

    form = SolicitudPrestamoForm(request.POST or None)
    if form.is_valid():
        solicitud = form.save(commit=False)
        solicitud.libro = libro
        solicitud.usuario = request.user
        solicitud.save()
        messages.success(
            request,
            'Solicitud enviada correctamente. El bibliotecario la revisará pronto.'
        )
        return redirect('biblioteca:mis_solicitudes')

    return render(request, 'biblioteca/solicitud_form.html', {
        'form': form,
        'libro': libro,
    })


@login_required
def mis_solicitudes(request):
    solicitudes = SolicitudPrestamo.objects.filter(
        usuario=request.user
    ).select_related('libro', 'prestamo').order_by('-fecha_solicitud')

    return render(request, 'biblioteca/mis_solicitudes.html', {
        'solicitudes': paginar(solicitudes, request, 10),
    })


@solo_bibliotecario
def solicitud_list(request):
    estado_filtro = request.GET.get('estado', 'pendiente')
    solicitudes = SolicitudPrestamo.objects.select_related(
        'libro', 'usuario'
    ).all()

    if estado_filtro:
        solicitudes = solicitudes.filter(estado=estado_filtro)

    return render(request, 'biblioteca/solicitud_list.html', {
        'solicitudes': paginar(solicitudes, request, 15),
        'estado_filtro': estado_filtro,
        'total_pendientes': SolicitudPrestamo.objects.filter(estado='pendiente').count(),
    })


@solo_bibliotecario
def solicitud_aprobar(request, pk):
    solicitud = get_object_or_404(SolicitudPrestamo, pk=pk, estado='pendiente')
    form = AprobarSolicitudForm(request.POST or None, libro=solicitud.libro)

    if form.is_valid():
        ejemplar = form.cleaned_data['ejemplar']
        fecha_devolucion = form.cleaned_data['fecha_devolucion']
        respuesta = form.cleaned_data.get('respuesta', '')

        prestamo = Prestamo.objects.create(
            ejemplar=ejemplar,
            usuario=solicitud.usuario,
            fecha_devolucion=fecha_devolucion,
            estado='activo',
            registrado_por=request.user,
            notas=f'Aprobado desde solicitud #{solicitud.pk}',
        )

        ejemplar.estado = 'prestado'
        ejemplar.save()

        solicitud.estado = 'aprobada'
        solicitud.prestamo = prestamo
        solicitud.respuesta = respuesta
        solicitud.atendida_por = request.user
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()

        enviar_confirmacion_prestamo(prestamo)

        messages.success(
            request,
            f'Solicitud aprobada. Préstamo creado para '
            f'{solicitud.usuario.get_full_name() or solicitud.usuario.username}.'
        )
        return redirect('biblioteca:solicitud_list')

    return render(request, 'biblioteca/solicitud_aprobar.html', {
        'form': form,
        'solicitud': solicitud,
    })


@solo_bibliotecario
def solicitud_rechazar(request, pk):
    solicitud = get_object_or_404(SolicitudPrestamo, pk=pk, estado='pendiente')
    form = RechazarSolicitudForm(request.POST or None)

    if form.is_valid():
        solicitud.estado = 'rechazada'
        solicitud.respuesta = form.cleaned_data['respuesta']
        solicitud.atendida_por = request.user
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()

        enviar_rechazo_solicitud(solicitud)

        messages.success(request, 'Solicitud rechazada.')
        return redirect('biblioteca:solicitud_list')

    return render(request, 'biblioteca/solicitud_rechazar.html', {
        'form': form,
        'solicitud': solicitud,
    })