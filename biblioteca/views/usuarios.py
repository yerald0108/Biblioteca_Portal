# biblioteca/views/usuarios.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from biblioteca.decoradores import solo_bibliotecario, get_rol
from biblioteca.models import PerfilUsuario, Prestamo
from biblioteca.forms import PerfilForm, GestionUsuarioForm


@login_required
def mi_perfil(request):
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)
    form = PerfilForm(
        request.POST or None,
        request.FILES or None,
        instance=perfil,
        usuario=request.user
    )
    if form.is_valid():
        request.user.first_name = form.cleaned_data['first_name']
        request.user.last_name = form.cleaned_data['last_name']
        request.user.email = form.cleaned_data['email']
        request.user.save()
        form.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('biblioteca:mi_perfil')

    mis_prestamos = Prestamo.objects.filter(
        usuario=request.user
    ).select_related('ejemplar__libro').order_by('-fecha_prestamo')[:5]

    return render(request, 'biblioteca/mi_perfil.html', {
        'form': form,
        'perfil': perfil,
        'mis_prestamos': mis_prestamos,
    })


@solo_bibliotecario
def usuario_list(request):
    usuarios = User.objects.select_related('perfil').order_by('-date_joined')
    return render(request, 'biblioteca/usuario_list.html', {'usuarios': usuarios})


@solo_bibliotecario
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)
    form = GestionUsuarioForm(request.POST or None, instance=perfil)
    if form.is_valid():
        form.save()
        messages.success(request, f'Usuario "{usuario.username}" actualizado.')
        return redirect('biblioteca:usuario_list')

    return render(request, 'biblioteca/usuario_editar.html', {
        'form': form,
        'usuario': usuario,
        'perfil': perfil,
    })


@solo_bibliotecario
def solicitudes_rol_list(request):
    pendientes = PerfilUsuario.objects.filter(
        rol_solicitado__isnull=False,
        rol_aprobado=False
    ).select_related('usuario').order_by('usuario__date_joined')

    aprobados = PerfilUsuario.objects.filter(
        rol_aprobado=True,
        rol_solicitado__isnull=False
    ).select_related('usuario').order_by('-usuario__date_joined')[:10]

    return render(request, 'biblioteca/solicitudes_rol.html', {
        'pendientes': pendientes,
        'aprobados': aprobados,
    })


@solo_bibliotecario
def aprobar_rol(request, pk):
    perfil = get_object_or_404(PerfilUsuario, pk=pk)
    if request.method == 'POST':
        rol_nuevo = request.POST.get('rol', perfil.rol_solicitado)
        perfil.rol = rol_nuevo
        perfil.rol_aprobado = True
        perfil.save()
        messages.success(
            request,
            f'Rol "{perfil.get_rol_display()}" aprobado para '
            f'{perfil.usuario.get_full_name() or perfil.usuario.username}.'
        )
    return redirect('biblioteca:solicitudes_rol')


@solo_bibliotecario
def rechazar_rol(request, pk):
    perfil = get_object_or_404(PerfilUsuario, pk=pk)
    if request.method == 'POST':
        perfil.rol_solicitado = None
        perfil.motivo_solicitud = ''
        perfil.rol_aprobado = False
        perfil.rol = 'visitante'
        perfil.save()
        messages.success(
            request,
            f'Solicitud rechazada. '
            f'{perfil.usuario.get_full_name() or perfil.usuario.username} '
            f'queda como visitante.'
        )
    return redirect('biblioteca:solicitudes_rol')