# biblioteca/views/prestamos.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from biblioteca.decoradores import solo_bibliotecario, get_rol
from biblioteca.models import Prestamo
from biblioteca.forms import PrestamoForm
from biblioteca.correo import enviar_notificacion_vencimiento
from .general import paginar


@login_required
def prestamo_list(request):
    rol = get_rol(request.user)

    if rol == 'bibliotecario' or request.user.is_staff:
        prestamos = Prestamo.objects.select_related(
            'ejemplar__libro', 'usuario'
        ).all()
    elif rol in ('estudiante', 'profesor'):
        prestamos = Prestamo.objects.select_related(
            'ejemplar__libro', 'usuario'
        ).filter(usuario=request.user)
    else:
        messages.info(request, 'Los visitantes no tienen préstamos registrados.')
        return redirect('home')

    # La actualización masiva de estados vencidos se delega a una tarea periódica.
    # Aquí solo filtramos si es necesario.
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        prestamos = prestamos.filter(estado=estado_filtro)

    return render(request, 'biblioteca/prestamo_list.html', {
        'prestamos': paginar(prestamos, request, 15),
        'estado_filtro': estado_filtro,
        'total_activos': Prestamo.objects.filter(estado='activo').count(),
        'total_vencidos': Prestamo.objects.filter(estado='vencido').count(),
        'es_bibliotecario': rol == 'bibliotecario' or request.user.is_staff,
    })


@solo_bibliotecario
def prestamo_crear(request):
    form = PrestamoForm(request.POST or None)
    if form.is_valid():
        prestamo = form.save(commit=False)
        prestamo.registrado_por = request.user
        prestamo.save()
        prestamo.ejemplar.estado = 'prestado'
        prestamo.ejemplar.save()
        messages.success(request, 'Préstamo registrado correctamente.')
        return redirect('biblioteca:prestamo_list')

    return render(request, 'biblioteca/prestamo_form.html', {'form': form})


@solo_bibliotecario
def prestamo_devolver(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if request.method == 'POST':
        prestamo.estado = 'devuelto'
        prestamo.fecha_devuelto = timezone.now()
        prestamo.save()
        prestamo.ejemplar.estado = 'disponible'
        prestamo.ejemplar.save()
        messages.success(request, 'Devolución registrada correctamente.')
        return redirect('biblioteca:prestamo_list')

    return render(request, 'biblioteca/prestamo_devolver.html', {'prestamo': prestamo})


@solo_bibliotecario
def prestamo_notificar(request, pk):
    """El bibliotecario puede enviar manualmente el correo de vencimiento."""
    prestamo = get_object_or_404(Prestamo, pk=pk)
    enviado = enviar_notificacion_vencimiento(prestamo)
    if enviado:
        messages.success(request, 'Notificación enviada correctamente.')
    else:
        messages.warning(request, 'No se pudo enviar. Verifica que el usuario tenga email.')
    return redirect('biblioteca:prestamo_list')