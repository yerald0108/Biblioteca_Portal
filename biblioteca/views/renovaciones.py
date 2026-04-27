# biblioteca/views/renovaciones.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from biblioteca.decoradores import solo_bibliotecario, rol_requerido
from biblioteca.models import Prestamo, RenovacionPrestamo
from biblioteca.forms import (
    RenovacionForm,
    AprobarRenovacionForm,
    RechazarRenovacionForm,
)
from biblioteca.correo import (
    enviar_confirmacion_renovacion,
    enviar_rechazo_renovacion,
)
from .general import paginar


@rol_requerido('estudiante', 'profesor', 'bibliotecario')
def renovacion_crear(request, prestamo_pk):
    prestamo = get_object_or_404(Prestamo, pk=prestamo_pk, usuario=request.user)

    if prestamo.estado == 'devuelto':
        messages.error(request, 'Este préstamo ya fue devuelto.')
        return redirect('biblioteca:prestamo_list')

    renovacion_pendiente = RenovacionPrestamo.objects.filter(
        prestamo=prestamo, estado='pendiente'
    ).exists()
    if renovacion_pendiente:
        messages.warning(
            request,
            'Ya tienes una solicitud de renovación pendiente para este préstamo.'
        )
        return redirect('biblioteca:prestamo_list')

    form = RenovacionForm(request.POST or None)
    if form.is_valid():
        renovacion = form.save(commit=False)
        renovacion.prestamo = prestamo
        renovacion.usuario = request.user
        renovacion.save()
        messages.success(
            request,
            'Solicitud de renovación enviada. El bibliotecario la revisará pronto.'
        )
        return redirect('biblioteca:mis_renovaciones')

    return render(request, 'biblioteca/renovacion_form.html', {
        'form': form,
        'prestamo': prestamo,
    })


@login_required
def mis_renovaciones(request):
    renovaciones = RenovacionPrestamo.objects.filter(
        usuario=request.user
    ).select_related('prestamo__ejemplar__libro').order_by('-fecha_solicitud')

    return render(request, 'biblioteca/mis_renovaciones.html', {
        'renovaciones': paginar(renovaciones, request, 10),
    })


@solo_bibliotecario
def renovacion_list(request):
    estado_filtro = request.GET.get('estado', 'pendiente')
    renovaciones = RenovacionPrestamo.objects.select_related(
        'prestamo__ejemplar__libro', 'usuario'
    ).all()

    if estado_filtro:
        renovaciones = renovaciones.filter(estado=estado_filtro)

    return render(request, 'biblioteca/renovacion_list.html', {
        'renovaciones': paginar(renovaciones, request, 15),
        'estado_filtro': estado_filtro,
        'total_pendientes': RenovacionPrestamo.objects.filter(estado='pendiente').count(),
    })


@solo_bibliotecario
def renovacion_aprobar(request, pk):
    renovacion = get_object_or_404(RenovacionPrestamo, pk=pk, estado='pendiente')
    form = AprobarRenovacionForm(request.POST or None, prestamo=renovacion.prestamo)

    if form.is_valid():
        nueva_fecha = form.cleaned_data['nueva_fecha']
        respuesta = form.cleaned_data.get('respuesta', '')

        renovacion.prestamo.fecha_devolucion = nueva_fecha
        if renovacion.prestamo.estado == 'vencido':
            renovacion.prestamo.estado = 'activo'
        renovacion.prestamo.save()

        renovacion.estado = 'aprobada'
        renovacion.nueva_fecha = nueva_fecha
        renovacion.respuesta = respuesta
        renovacion.atendida_por = request.user
        renovacion.fecha_respuesta = timezone.now()
        renovacion.save()

        enviar_confirmacion_renovacion(renovacion)

        messages.success(
            request,
            f'Renovación aprobada. Nueva fecha: {nueva_fecha.strftime("%d/%m/%Y")}.'
        )
        return redirect('biblioteca:renovacion_list')

    return render(request, 'biblioteca/renovacion_aprobar.html', {
        'form': form,
        'renovacion': renovacion,
    })


@solo_bibliotecario
def renovacion_rechazar(request, pk):
    renovacion = get_object_or_404(RenovacionPrestamo, pk=pk, estado='pendiente')
    form = RechazarRenovacionForm(request.POST or None)

    if form.is_valid():
        renovacion.estado = 'rechazada'
        renovacion.respuesta = form.cleaned_data['respuesta']
        renovacion.atendida_por = request.user
        renovacion.fecha_respuesta = timezone.now()
        renovacion.save()

        enviar_rechazo_renovacion(renovacion)

        messages.success(request, 'Renovación rechazada.')
        return redirect('biblioteca:renovacion_list')

    return render(request, 'biblioteca/renovacion_rechazar.html', {
        'form': form,
        'renovacion': renovacion,
    })