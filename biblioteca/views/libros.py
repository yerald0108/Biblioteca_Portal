# biblioteca/views/libros.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from config import settings
from biblioteca.decoradores import solo_bibliotecario
from biblioteca.models import Libro, Prestamo
from biblioteca.forms import LibroForm, EjemplarForm, BusquedaForm
from .general import paginar


@login_required
def libro_list(request):
    form = BusquedaForm(request.GET)
    libros = Libro.objects.select_related('categoria').prefetch_related('ejemplares')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        categoria = form.cleaned_data.get('categoria')
        estado = form.cleaned_data.get('estado')

        if q:
            libros = libros.filter(
                Q(titulo__icontains=q) |
                Q(autor__icontains=q) |
                Q(isbn__icontains=q)
            )
        if categoria:
            libros = libros.filter(categoria=categoria)
        if estado:
            libros = libros.filter(ejemplares__estado=estado).distinct()

    libros_page = paginar(libros, request, 10)
    return render(request, 'biblioteca/libro_list.html', {
        'libros': libros_page,
        'form': form,
        'total': libros.count(),
    })


@login_required
def libro_detail(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    ejemplares = libro.ejemplares.all()

    limite = getattr(settings, 'LIMITE_PRESTAMOS_ACTIVOS', 3)
    prestamos_usuario_count = None
    if request.user.is_authenticated:
        prestamos_usuario_count = Prestamo.objects.filter(
            usuario=request.user,
            estado__in=['activo', 'vencido']
        ).count()

    historial = None
    if request.user.is_staff or (
        hasattr(request.user, 'perfil') and
        request.user.perfil.rol == 'bibliotecario'
    ):
        historial = Prestamo.objects.filter(
            ejemplar__libro=libro
        ).select_related(
            'usuario', 'ejemplar', 'registrado_por'
        ).order_by('-fecha_prestamo')[:20]

    return render(request, 'biblioteca/libro_detail.html', {
        'libro': libro,
        'ejemplares': ejemplares,
        'prestamos_usuario_count': prestamos_usuario_count,
        'limite_prestamos': limite,
        'historial': historial,
    })


@solo_bibliotecario
def libro_crear(request):
    form = LibroForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        libro = form.save()
        messages.success(request, f'Libro "{libro.titulo}" registrado correctamente.')
        return redirect('biblioteca:libro_detail', pk=libro.pk)

    return render(request, 'biblioteca/libro_form.html', {
        'form': form,
        'titulo': 'Registrar nuevo libro',
        'accion': 'Guardar libro',
    })


@solo_bibliotecario
def libro_editar(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    form = LibroForm(request.POST or None, request.FILES or None, instance=libro)
    if form.is_valid():
        form.save()
        messages.success(request, f'Libro "{libro.titulo}" actualizado.')
        return redirect('biblioteca:libro_detail', pk=libro.pk)

    return render(request, 'biblioteca/libro_form.html', {
        'form': form,
        'libro': libro,
        'titulo': 'Editar libro',
        'accion': 'Guardar cambios',
    })


@solo_bibliotecario
def libro_eliminar(request, pk):
    libro = get_object_or_404(Libro, pk=pk)

    tiene_prestamos = Prestamo.objects.filter(
        ejemplar__libro=libro
    ).exists()

    if request.method == 'POST':
        if tiene_prestamos:
            messages.error(
                request,
                f'No se puede eliminar "{libro.titulo}" porque tiene préstamos '
                f'registrados en el historial. Primero devuelve todos los '
                f'ejemplares prestados.'
            )
            return redirect('biblioteca:libro_detail', pk=libro.pk)

        titulo = libro.titulo
        libro.delete()
        messages.success(request, f'Libro "{titulo}" eliminado.')
        return redirect('biblioteca:libro_list')

    return render(request, 'biblioteca/libro_confirmar_eliminar.html', {
        'libro': libro,
        'tiene_prestamos': tiene_prestamos,
    })


@solo_bibliotecario
def ejemplar_agregar(request, libro_pk):
    libro = get_object_or_404(Libro, pk=libro_pk)
    form = EjemplarForm(request.POST or None)
    if form.is_valid():
        ejemplar = form.save(commit=False)
        ejemplar.libro = libro
        ejemplar.save()
        messages.success(request, f'Ejemplar "{ejemplar.codigo}" agregado.')
        return redirect('biblioteca:libro_detail', pk=libro_pk)

    return render(request, 'biblioteca/ejemplar_form.html', {
        'form': form,
        'libro': libro,
    })