# biblioteca/views/tesis.py

import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.db.models import Q

from biblioteca.decoradores import solo_bibliotecario, rol_requerido
from biblioteca.models import Tesis
from biblioteca.forms import TesisForm
from .general import paginar


@login_required
def tesis_list(request):
    tesis = Tesis.objects.all()

    q = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    area = request.GET.get('area', '')

    if q:
        tesis = tesis.filter(
            Q(titulo__icontains=q) |
            Q(autor__icontains=q) |
            Q(area__icontains=q)
        )
    if tipo:
        tesis = tesis.filter(tipo=tipo)
    if area:
        tesis = tesis.filter(area__icontains=area)

    areas = Tesis.objects.values_list('area', flat=True).distinct().order_by('area')

    return render(request, 'biblioteca/tesis_list.html', {
        'tesis': paginar(tesis, request, 9),
        'total': tesis.count(),
        'q': q,
        'tipo': tipo,
        'area': area,
        'areas': areas,
        'tipo_choices': Tesis.TIPO_CHOICES,
    })


@login_required
def tesis_detail(request, pk):
    tesis = get_object_or_404(Tesis, pk=pk)
    Tesis.objects.filter(pk=pk).update(vistas=tesis.vistas + 1)
    tesis.vistas += 1
    return render(request, 'biblioteca/tesis_detail.html', {'tesis': tesis})


@rol_requerido('bibliotecario', 'profesor')
def tesis_crear(request):
    form = TesisForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        tesis = form.save(commit=False)
        tesis.creado_por = request.user
        tesis.save()
        messages.success(request, f'Tesis "{tesis.titulo}" registrada correctamente.')
        return redirect('biblioteca:tesis_detail', pk=tesis.pk)
    return render(request, 'biblioteca/tesis_form.html', {
        'form': form,
        'titulo': 'Registrar tesis',
        'accion': 'Guardar tesis',
    })


@rol_requerido('bibliotecario', 'profesor')
def tesis_editar(request, pk):
    tesis = get_object_or_404(Tesis, pk=pk)
    form = TesisForm(request.POST or None, request.FILES or None, instance=tesis)
    if form.is_valid():
        form.save()
        messages.success(request, 'Tesis actualizada correctamente.')
        return redirect('biblioteca:tesis_detail', pk=tesis.pk)
    return render(request, 'biblioteca/tesis_form.html', {
        'form': form,
        'tesis': tesis,
        'titulo': 'Editar tesis',
        'accion': 'Guardar cambios',
    })


@solo_bibliotecario
def tesis_eliminar(request, pk):
    tesis = get_object_or_404(Tesis, pk=pk)
    if request.method == 'POST':
        titulo = tesis.titulo
        tesis.archivo_pdf.delete(save=False)
        tesis.delete()
        messages.success(request, f'Tesis "{titulo}" eliminada.')
        return redirect('biblioteca:tesis_list')

    return render(request, 'biblioteca/tesis_confirmar_eliminar.html', {'tesis': tesis})


@login_required
def tesis_ver_pdf(request, pk):
    """Abre el PDF en el navegador directamente."""
    tesis = get_object_or_404(Tesis, pk=pk)
    if not tesis.archivo_pdf:
        raise Http404('Esta tesis no tiene archivo PDF.')
    if not tesis.disponible and not request.user.is_staff:
        messages.error(request, 'Esta tesis no está disponible para consulta.')
        return redirect('biblioteca:tesis_list')
    return FileResponse(tesis.archivo_pdf.open('rb'), content_type='application/pdf')