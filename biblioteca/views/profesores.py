# biblioteca/views/profesores.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from biblioteca.decoradores import solo_bibliotecario
from biblioteca.models import Profesor
from biblioteca.forms import ProfesorForm


@login_required
def profesor_list(request):
    profesores = Profesor.objects.filter(activo=True)

    q = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    ambito = request.GET.get('ambito', '')

    if q:
        profesores = profesores.filter(
            Q(nombre__icontains=q) |
            Q(apellidos__icontains=q) |
            Q(especialidad__icontains=q)
        )
    if categoria:
        profesores = profesores.filter(categoria=categoria)
    if ambito:
        profesores = profesores.filter(ambito=ambito)

    return render(request, 'biblioteca/profesor_list.html', {
        'profesores': profesores,
        'total': profesores.count(),
        'q': q,
        'categoria': categoria,
        'ambito': ambito,
        'categoria_choices': Profesor.CATEGORIA_CHOICES,
        'ambito_choices': Profesor.AMBITO_CHOICES,
    })


@login_required
def profesor_detail(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    return render(request, 'biblioteca/profesor_detail.html', {'profesor': profesor})


@solo_bibliotecario
def profesor_crear(request):
    form = ProfesorForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        profesor = form.save()
        messages.success(request, f'Profesor "{profesor.nombre_completo()}" registrado.')
        return redirect('biblioteca:profesor_detail', pk=profesor.pk)

    return render(request, 'biblioteca/profesor_form.html', {
        'form': form,
        'titulo': 'Registrar profesor',
        'accion': 'Guardar profesor',
    })


@solo_bibliotecario
def profesor_editar(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    form = ProfesorForm(request.POST or None, request.FILES or None, instance=profesor)
    if form.is_valid():
        form.save()
        messages.success(request, 'Profesor actualizado correctamente.')
        return redirect('biblioteca:profesor_detail', pk=profesor.pk)

    return render(request, 'biblioteca/profesor_form.html', {
        'form': form,
        'profesor': profesor,
        'titulo': 'Editar profesor',
        'accion': 'Guardar cambios',
    })


@solo_bibliotecario
def profesor_eliminar(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    if request.method == 'POST':
        nombre = profesor.nombre_completo()
        profesor.foto.delete(save=False)
        profesor.delete()
        messages.success(request, f'Profesor "{nombre}" eliminado.')
        return redirect('biblioteca:profesor_list')

    return render(request, 'biblioteca/profesor_confirmar_eliminar.html', {'profesor': profesor})