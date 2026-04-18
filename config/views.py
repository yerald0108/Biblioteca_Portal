from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from biblioteca.models import Libro, Prestamo, Tesis, Profesor
from biblioteca.forms import RegistroUsuarioForm
from django.contrib import messages


@login_required
def home(request):
    from biblioteca.models import Libro, Prestamo, Tesis, Profesor, Recurso

    context = {
        'total_libros':     Libro.objects.count(),
        'total_prestamos':  Prestamo.objects.filter(estado='activo').count(),
        'total_tesis':      Tesis.objects.filter(disponible=True).count(),
        'total_profesores': Profesor.objects.filter(activo=True).count(),

        # Recursos destacados (máximo 3)
        'recursos_destacados': Recurso.objects.filter(
            publicado=True, destacado=True
        ).order_by('-fecha_publicacion')[:3],

        # Últimas novedades literarias
        'ultimas_novedades': Recurso.objects.filter(
            publicado=True, tipo='novedad'
        ).order_by('-fecha_publicacion')[:3],

        # Últimos libros registrados
        'ultimos_libros': Libro.objects.select_related(
            'categoria'
        ).order_by('-fecha_registro')[:4],

        # Últimas tesis
        'ultimas_tesis': Tesis.objects.filter(
            disponible=True
        ).order_by('-fecha_registro')[:3],
    }
    return render(request, 'home.html', context)


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegistroUsuarioForm(request.POST or None)
    if form.is_valid():
        usuario = form.save()

        # Guardar el rol solicitado en el perfil
        perfil = usuario.perfil
        perfil.rol_solicitado   = form.cleaned_data['rol_solicitado']
        perfil.motivo_solicitud = form.cleaned_data.get('motivo_solicitud', '')
        perfil.save()

        login(request, usuario)
        messages.success(
            request,
            f'Bienvenido/a {usuario.get_full_name() or usuario.username}. '
            f'Tu solicitud de rol "{perfil.get_rol_solicitado_display()}" '
            f'está pendiente de aprobación por el bibliotecario. '
            f'Mientras tanto puedes navegar el portal como visitante.'
        )
        return redirect('home')

    return render(request, 'registration/registro.html', {'form': form})