# biblioteca/views/recursos.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.db.models import Q

from biblioteca.decoradores import solo_bibliotecario
from biblioteca.models import Recurso
from biblioteca.forms import RecursoForm


@login_required
def recurso_list(request):
    recursos = Recurso.objects.filter(publicado=True)

    q = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')

    if q:
        recursos = recursos.filter(
            Q(titulo__icontains=q) |
            Q(descripcion__icontains=q)
        )
    if tipo:
        recursos = recursos.filter(tipo=tipo)

    novedades = recursos.filter(tipo='novedad')
    tutoriales = recursos.filter(tipo='tutorial')
    manuales = recursos.filter(tipo='manual')
    videos = recursos.filter(tipo='video')

    return render(request, 'biblioteca/recurso_list.html', {
        'recursos': recursos,
        'novedades': novedades,
        'tutoriales': tutoriales,
        'manuales': manuales,
        'videos': videos,
        'total': recursos.count(),
        'q': q,
        'tipo': tipo,
        'tipo_choices': Recurso.TIPO_CHOICES,
    })


@login_required
def recurso_detail(request, pk):
    recurso = get_object_or_404(Recurso, pk=pk, publicado=True)
    return render(request, 'biblioteca/recurso_detail.html', {'recurso': recurso})


@solo_bibliotecario
def recurso_crear(request):
    form = RecursoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        recurso = form.save(commit=False)
        recurso.autor = request.user
        recurso.save()
        messages.success(request, f'Recurso "{recurso.titulo}" publicado correctamente.')
        return redirect('biblioteca:recurso_detail', pk=recurso.pk)

    return render(request, 'biblioteca/recurso_form.html', {
        'form': form,
        'titulo': 'Publicar recurso',
        'accion': 'Publicar',
    })


@solo_bibliotecario
def recurso_editar(request, pk):
    recurso = get_object_or_404(Recurso, pk=pk)
    form = RecursoForm(request.POST or None, request.FILES or None, instance=recurso)
    if form.is_valid():
        form.save()
        messages.success(request, 'Recurso actualizado correctamente.')
        return redirect('biblioteca:recurso_detail', pk=recurso.pk)

    return render(request, 'biblioteca/recurso_form.html', {
        'form': form,
        'recurso': recurso,
        'titulo': 'Editar recurso',
        'accion': 'Guardar cambios',
    })


@solo_bibliotecario
def recurso_eliminar(request, pk):
    recurso = get_object_or_404(Recurso, pk=pk)
    if request.method == 'POST':
        titulo = recurso.titulo
        recurso.archivo.delete(save=False)
        recurso.imagen.delete(save=False)
        recurso.delete()
        messages.success(request, f'Recurso "{titulo}" eliminado.')
        return redirect('biblioteca:recurso_list')

    return render(request, 'biblioteca/recurso_confirmar_eliminar.html', {'recurso': recurso})


@login_required
def recurso_descargar(request, pk):
    recurso = get_object_or_404(Recurso, pk=pk, publicado=True)
    if not recurso.archivo:
        raise Http404('Este recurso no tiene archivo descargable.')
    return FileResponse(
        recurso.archivo.open('rb'),
        as_attachment=True,
        filename=recurso.archivo.name.split('/')[-1]
    )