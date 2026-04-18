from .decoradores import get_rol


def rol_usuario(request):
    """Inyecta el rol del usuario en todos los templates."""
    if request.user.is_authenticated:
        rol = get_rol(request.user)
        return {
            'rol_usuario':        rol,
            'es_bibliotecario':   rol == 'bibliotecario' or request.user.is_staff,
            'es_estudiante':      rol == 'estudiante',
            'es_profesor':        rol == 'profesor',
            'es_visitante':       rol == 'visitante',
        }
    return {
        'rol_usuario':      'anonimo',
        'es_bibliotecario': False,
        'es_estudiante':    False,
        'es_profesor':      False,
        'es_visitante':     True,
    }