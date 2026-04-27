from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from biblioteca.models import Libro, Prestamo, Tesis, Profesor, Recurso
from biblioteca.forms import RegistroUsuarioForm
from django.contrib import messages
from django.utils import timezone
from biblioteca.decoradores import get_rol


@login_required
def home(request):
    
    hoy = timezone.now().date()
    rol = get_rol(request.user)

    # Alertas personalizadas por rol
    alertas = []

    if rol in ('estudiante', 'profesor'):
        # Préstamos vencidos
        vencidos = Prestamo.objects.filter(
            usuario=request.user,
            estado='vencido'
        ).select_related('ejemplar__libro')

        for p in vencidos:
            alertas.append({
                'tipo':    'error',
                'mensaje': f'Tu préstamo de "{p.ejemplar.libro.titulo}" está vencido '
                           f'hace {p.dias_retraso()} día{"s" if p.dias_retraso() != 1 else ""}. '
                           f'Por favor devuélvelo a la biblioteca.',
                'url':     'biblioteca:prestamo_list',
                'cta':     'Ver mis préstamos',
            })

        # Próximos a vencer (2 días o menos)
        por_vencer = Prestamo.objects.filter(
            usuario=request.user,
            estado='activo',
            fecha_devolucion__lte=hoy + timezone.timedelta(days=2),
            fecha_devolucion__gte=hoy,
        ).select_related('ejemplar__libro')

        for p in por_vencer:
            dias = p.dias_restantes()
            alertas.append({
                'tipo':    'warning',
                'mensaje': f'Tu préstamo de "{p.ejemplar.libro.titulo}" vence '
                           f'{"hoy" if dias == 0 else f"en {dias} día{'s' if dias != 1 else ''}"}. '
                           f'Devuélvelo o solicita una renovación.',
                'url':     'biblioteca:prestamo_list',
                'cta':     'Ver mis préstamos',
            })

        # Solicitud de rol pendiente
        if hasattr(request.user, 'perfil'):
            perfil = request.user.perfil
            if perfil.tiene_solicitud_pendiente():
                alertas.append({
                    'tipo':    'info',
                    'mensaje': f'Tu solicitud de rol "{perfil.get_rol_solicitado_display()}" '
                               f'está pendiente de aprobación por el bibliotecario.',
                    'url':     None,
                    'cta':     None,
                })

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

        # Guardar solicitud de rol en el perfil
        perfil = usuario.perfil
        perfil.rol_solicitado   = form.cleaned_data['rol_solicitado']
        perfil.motivo_solicitud = form.cleaned_data.get('motivo_solicitud', '')
        perfil.save()

        login(request, usuario)

        rol_display = dict(form.ROL_OPCIONES).get(
            form.cleaned_data['rol_solicitado'], 'Desconocido'
        )
        messages.success(
            request,
            f'Bienvenido/a {usuario.get_full_name() or usuario.username}. '
            f'Tu solicitud de rol "{rol_display}" está pendiente de aprobación. '
            f'Mientras tanto puedes navegar el portal como visitante.'
        )
        return redirect('home')

    return render(request, 'registration/registro.html', {'form': form})