# biblioteca/views/categorias.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count

from biblioteca.decoradores import solo_bibliotecario
from biblioteca.models import Categoria
from biblioteca.forms import CategoriaForm


@solo_bibliotecario
def categoria_list(request):
    categorias = Categoria.objects.annotate(
        total_libros=Count('libros')
    ).order_by('nombre')
    return render(request, 'biblioteca/categoria_list.html', {
        'categorias': categorias,
    })


@solo_bibliotecario
def categoria_crear(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        categoria = form.save()
        messages.success(request, f'Categoría "{categoria.nombre}" creada.')
        return redirect('biblioteca:categoria_list')
    return render(request, 'biblioteca/categoria_form.html', {
        'form': form,
        'titulo': 'Nueva categoría',
        'accion': 'Crear categoría',
    })


@solo_bibliotecario
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if form.is_valid():
        form.save()
        messages.success(request, f'Categoría "{categoria.nombre}" actualizada.')
        return redirect('biblioteca:categoria_list')
    return render(request, 'biblioteca/categoria_form.html', {
        'form': form,
        'categoria': categoria,
        'titulo': 'Editar categoría',
        'accion': 'Guardar cambios',
    })


@solo_bibliotecario
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        if categoria.libros.count() > 0:
            messages.error(
                request,
                f'No se puede eliminar "{categoria.nombre}" porque tiene '
                f'{categoria.libros.count()} libro(s) asociado(s).'
            )
            return redirect('biblioteca:categoria_list')
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada.')
        return redirect('biblioteca:categoria_list')
    return render(request, 'biblioteca/categoria_confirmar_eliminar.html', {
        'categoria': categoria,
    })