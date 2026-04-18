from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import PerfilUsuario


def get_rol(user):
    """Devuelve el rol del usuario o 'visitante' si no tiene perfil."""
    try:
        return user.perfil.rol
    except PerfilUsuario.DoesNotExist:
        return 'visitante'


def rol_requerido(*roles_permitidos):
    """
    Decorador que restringe el acceso a una vista según el rol del usuario.
    Uso: @rol_requerido('bibliotecario', 'profesor')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            rol = get_rol(request.user)
            if rol not in roles_permitidos:
                messages.error(
                    request,
                    f'No tienes permiso para acceder a esta sección. '
                    f'Se requiere uno de estos roles: {", ".join(roles_permitidos)}.'
                )
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def solo_bibliotecario(view_func):
    """Atajo: solo el bibliotecario puede acceder."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        rol = get_rol(request.user)
        if rol != 'bibliotecario' and not request.user.is_staff:
            messages.error(request, 'Esta sección es exclusiva del bibliotecario.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper