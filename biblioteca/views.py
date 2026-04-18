from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import FileResponse, Http404
import os

from config import settings

from .correo import (
    enviar_notificacion_vencimiento,
    enviar_recordatorio,
    enviar_confirmacion_prestamo,
    enviar_rechazo_solicitud,
    procesar_notificaciones_pendientes,
)
from .decoradores import solo_bibliotecario, rol_requerido, get_rol
from biblioteca.forms import RegistroUsuarioForm
from .models import Libro, Ejemplar, Categoria, Prestamo, Tesis, Profesor, Recurso, PerfilUsuario, Recurso, SolicitudPrestamo, RenovacionPrestamo
from .forms import LibroForm, EjemplarForm, BusquedaForm, PrestamoForm, TesisForm, ProfesorForm, RecursoForm, PerfilForm, GestionUsuarioForm, SolicitudPrestamoForm, AprobarSolicitudForm, RechazarSolicitudForm, AprobarRenovacionForm, RechazarRenovacionForm, RenovacionForm, CategoriaForm
from .correo import enviar_notificacion_vencimiento, procesar_notificaciones_pendientes, NotificacionCorreo, enviar_confirmacion_renovacion, enviar_rechazo_renovacion

from django.core.paginator import Paginator


def paginar(queryset, request, por_pagina=10):
    paginator = Paginator(queryset, por_pagina)
    pagina    = request.GET.get('pagina', 1)
    return paginator.get_page(pagina)

@login_required
def libro_list(request):
    form    = BusquedaForm(request.GET)
    libros  = Libro.objects.select_related('categoria').prefetch_related('ejemplares')

    if form.is_valid():
        q         = form.cleaned_data.get('q')
        categoria = form.cleaned_data.get('categoria')
        estado    = form.cleaned_data.get('estado')

        if q:
            libros = libros.filter(
                Q(titulo__icontains=q) |
                Q(autor__icontains=q)  |
                Q(isbn__icontains=q)
            )
        if categoria:
            libros = libros.filter(categoria=categoria)
        if estado:
            libros = libros.filter(ejemplares__estado=estado).distinct()

    libros_page = paginar(libros, request, 10)
    return render(request, 'biblioteca/libro_list.html', {
        'libros': libros_page,
        'form':   form,
        'total':  libros.count(),
    })

@login_required
def libro_detail(request, pk):
    from django.conf import settings
    libro      = get_object_or_404(Libro, pk=pk)
    ejemplares = libro.ejemplares.all()

    limite = getattr(settings, 'LIMITE_PRESTAMOS_ACTIVOS', 3)
    prestamos_usuario_count = None
    if request.user.is_authenticated:
        prestamos_usuario_count = Prestamo.objects.filter(
            usuario=request.user,
            estado__in=['activo', 'vencido']
        ).count()

    # Historial de préstamos del libro (solo para bibliotecario)
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
        'libro':                   libro,
        'ejemplares':              ejemplares,
        'prestamos_usuario_count': prestamos_usuario_count,
        'limite_prestamos':        limite,
        'historial':               historial,
    })

@solo_bibliotecario
def libro_crear(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para registrar libros.')
        return redirect('biblioteca:libro_list')

    form = LibroForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        libro = form.save()
        messages.success(request, f'Libro "{libro.titulo}" registrado correctamente.')
        return redirect('biblioteca:libro_detail', pk=libro.pk)

    return render(request, 'biblioteca/libro_form.html', {
        'form':   form,
        'titulo': 'Registrar nuevo libro',
        'accion': 'Guardar libro',
    })

@solo_bibliotecario
def libro_editar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para editar libros.')
        return redirect('biblioteca:libro_list')

    libro = get_object_or_404(Libro, pk=pk)
    form  = LibroForm(request.POST or None, request.FILES or None, instance=libro)
    if form.is_valid():
        form.save()
        messages.success(request, f'Libro "{libro.titulo}" actualizado.')
        return redirect('biblioteca:libro_detail', pk=libro.pk)

    return render(request, 'biblioteca/libro_form.html', {
        'form':   form,
        'libro':  libro,
        'titulo': 'Editar libro',
        'accion': 'Guardar cambios',
    })

@solo_bibliotecario
def libro_eliminar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para eliminar libros.')
        return redirect('biblioteca:libro_list')

    libro = get_object_or_404(Libro, pk=pk)
    if request.method == 'POST':
        titulo = libro.titulo
        libro.delete()
        messages.success(request, f'Libro "{titulo}" eliminado.')
        return redirect('biblioteca:libro_list')

    return render(request, 'biblioteca/libro_confirmar_eliminar.html', {'libro': libro})

@solo_bibliotecario
def ejemplar_agregar(request, libro_pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para agregar ejemplares.')
        return redirect('biblioteca:libro_detail', pk=libro_pk)

    libro = get_object_or_404(Libro, pk=libro_pk)
    form  = EjemplarForm(request.POST or None)
    if form.is_valid():
        ejemplar       = form.save(commit=False)
        ejemplar.libro = libro
        ejemplar.save()
        messages.success(request, f'Ejemplar "{ejemplar.codigo}" agregado.')
        return redirect('biblioteca:libro_detail', pk=libro_pk)

    return render(request, 'biblioteca/ejemplar_form.html', {
        'form':  form,
        'libro': libro,
    })
    
@login_required
def prestamo_list(request):
    rol = get_rol(request.user)

    if rol == 'bibliotecario' or request.user.is_staff:
        prestamos = Prestamo.objects.select_related(
            'ejemplar__libro', 'usuario'
        ).all()
    elif rol in ('estudiante', 'profesor'):
        prestamos = Prestamo.objects.select_related(
            'ejemplar__libro', 'usuario'
        ).filter(usuario=request.user)
    else:
        # visitante no tiene préstamos
        messages.info(request, 'Los visitantes no tienen préstamos registrados.')
        return redirect('home')

    # Actualizar estados vencidos
    for p in prestamos:
        if p.esta_vencido() and p.estado == 'activo':
            p.estado = 'vencido'
            p.save()

    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        prestamos = prestamos.filter(estado=estado_filtro)

    return render(request, 'biblioteca/prestamo_list.html', {
        'prestamos':      paginar(prestamos, request, 15),
        'estado_filtro':  estado_filtro,
        'total_activos':  Prestamo.objects.filter(estado='activo').count(),
        'total_vencidos': Prestamo.objects.filter(estado='vencido').count(),
        'es_bibliotecario': rol == 'bibliotecario' or request.user.is_staff,
    })

@solo_bibliotecario
def prestamo_crear(request):
    if not request.user.is_staff:
        messages.error(request, 'Solo el bibliotecario puede registrar préstamos.')
        return redirect('biblioteca:prestamo_list')

    form = PrestamoForm(request.POST or None)
    if form.is_valid():
        prestamo = form.save(commit=False)
        prestamo.registrado_por = request.user
        prestamo.save()
        # Marcar el ejemplar como prestado
        prestamo.ejemplar.estado = 'prestado'
        prestamo.ejemplar.save()
        messages.success(request, f'Préstamo registrado correctamente.')
        return redirect('biblioteca:prestamo_list')

    return render(request, 'biblioteca/prestamo_form.html', {'form': form})

@solo_bibliotecario
def prestamo_devolver(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Solo el bibliotecario puede registrar devoluciones.')
        return redirect('biblioteca:prestamo_list')

    prestamo = get_object_or_404(Prestamo, pk=pk)
    if request.method == 'POST':
        prestamo.estado         = 'devuelto'
        prestamo.fecha_devuelto = timezone.now()
        prestamo.save()
        # Liberar el ejemplar
        prestamo.ejemplar.estado = 'disponible'
        prestamo.ejemplar.save()
        messages.success(request, f'Devolución registrada correctamente.')
        return redirect('biblioteca:prestamo_list')

    return render(request, 'biblioteca/prestamo_devolver.html', {'prestamo': prestamo})

@solo_bibliotecario
def prestamo_notificar(request, pk):
    """El bibliotecario puede enviar manualmente el correo de vencimiento."""
    if not request.user.is_staff:
        return redirect('biblioteca:prestamo_list')

    prestamo = get_object_or_404(Prestamo, pk=pk)
    enviado  = enviar_notificacion_vencimiento(prestamo)
    if enviado:
        messages.success(request, 'Notificación enviada correctamente.')
    else:
        messages.warning(request, 'No se pudo enviar. Verifica que el usuario tenga email.')
    return redirect('biblioteca:prestamo_list')

@login_required
def tesis_list(request):
    tesis = Tesis.objects.all()

    q    = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    area = request.GET.get('area', '')

    if q:
        tesis = tesis.filter(
            Q(titulo__icontains=q) |
            Q(autor__icontains=q)  |
            Q(area__icontains=q)
        )
    if tipo:
        tesis = tesis.filter(tipo=tipo)
    if area:
        tesis = tesis.filter(area__icontains=area)

    areas = Tesis.objects.values_list('area', flat=True).distinct().order_by('area')

    return render(request, 'biblioteca/tesis_list.html', {
        'tesis':        paginar(tesis, request, 9),
        'total':        tesis.count(),
        'q':            q,
        'tipo':         tipo,
        'area':         area,
        'areas':        areas,
        'tipo_choices': Tesis.TIPO_CHOICES,
    })

@login_required
def tesis_detail(request, pk):
    tesis = get_object_or_404(Tesis, pk=pk)
    return render(request, 'biblioteca/tesis_detail.html', {'tesis': tesis})

@rol_requerido('bibliotecario', 'profesor')
def tesis_crear(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para registrar tesis.')
        return redirect('biblioteca:tesis_list')

    form = TesisForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        tesis = form.save()
        messages.success(request, f'Tesis "{tesis.titulo}" registrada correctamente.')
        return redirect('biblioteca:tesis_detail', pk=tesis.pk)

    return render(request, 'biblioteca/tesis_form.html', {
        'form':   form,
        'titulo': 'Registrar tesis',
        'accion': 'Guardar tesis',
    })

@rol_requerido('bibliotecario', 'profesor')
def tesis_editar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para editar tesis.')
        return redirect('biblioteca:tesis_list')

    tesis = get_object_or_404(Tesis, pk=pk)
    form  = TesisForm(request.POST or None, request.FILES or None, instance=tesis)
    if form.is_valid():
        form.save()
        messages.success(request, f'Tesis actualizada correctamente.')
        return redirect('biblioteca:tesis_detail', pk=tesis.pk)

    return render(request, 'biblioteca/tesis_form.html', {
        'form':   form,
        'tesis':  tesis,
        'titulo': 'Editar tesis',
        'accion': 'Guardar cambios',
    })

@solo_bibliotecario
def tesis_eliminar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para eliminar tesis.')
        return redirect('biblioteca:tesis_list')

    tesis = get_object_or_404(Tesis, pk=pk)
    if request.method == 'POST':
        titulo = tesis.titulo
        if tesis.archivo_pdf:
            if os.path.isfile(tesis.archivo_pdf.path):
                os.remove(tesis.archivo_pdf.path)
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

@login_required
def profesor_list(request):
    profesores = Profesor.objects.filter(activo=True)

    q         = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    ambito    = request.GET.get('ambito', '')

    if q:
        profesores = profesores.filter(
            Q(nombre__icontains=q)       |
            Q(apellidos__icontains=q)    |
            Q(especialidad__icontains=q)
        )
    if categoria:
        profesores = profesores.filter(categoria=categoria)
    if ambito:
        profesores = profesores.filter(ambito=ambito)

    return render(request, 'biblioteca/profesor_list.html', {
        'profesores':        profesores,
        'total':             profesores.count(),
        'q':                 q,
        'categoria':         categoria,
        'ambito':            ambito,
        'categoria_choices': Profesor.CATEGORIA_CHOICES,
        'ambito_choices':    Profesor.AMBITO_CHOICES,
    })

@login_required
def profesor_detail(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    return render(request, 'biblioteca/profesor_detail.html', {'profesor': profesor})

@solo_bibliotecario
def profesor_crear(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para registrar profesores.')
        return redirect('biblioteca:profesor_list')

    form = ProfesorForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        profesor = form.save()
        messages.success(request, f'Profesor "{profesor.nombre_completo()}" registrado.')
        return redirect('biblioteca:profesor_detail', pk=profesor.pk)

    return render(request, 'biblioteca/profesor_form.html', {
        'form':   form,
        'titulo': 'Registrar profesor',
        'accion': 'Guardar profesor',
    })

@solo_bibliotecario
def profesor_editar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para editar profesores.')
        return redirect('biblioteca:profesor_list')

    profesor = get_object_or_404(Profesor, pk=pk)
    form     = ProfesorForm(request.POST or None, request.FILES or None, instance=profesor)
    if form.is_valid():
        form.save()
        messages.success(request, 'Profesor actualizado correctamente.')
        return redirect('biblioteca:profesor_detail', pk=profesor.pk)

    return render(request, 'biblioteca/profesor_form.html', {
        'form':     form,
        'profesor': profesor,
        'titulo':   'Editar profesor',
        'accion':   'Guardar cambios',
    })

@solo_bibliotecario
def profesor_eliminar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para eliminar profesores.')
        return redirect('biblioteca:profesor_list')

    profesor = get_object_or_404(Profesor, pk=pk)
    if request.method == 'POST':
        nombre = profesor.nombre_completo()
        if profesor.foto:
            if os.path.isfile(profesor.foto.path):
                os.remove(profesor.foto.path)
        profesor.delete()
        messages.success(request, f'Profesor "{nombre}" eliminado.')
        return redirect('biblioteca:profesor_list')

    return render(request, 'biblioteca/profesor_confirmar_eliminar.html', {'profesor': profesor})

@login_required
def recurso_list(request):
    recursos = Recurso.objects.filter(publicado=True)

    q    = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')

    if q:
        recursos = recursos.filter(
            Q(titulo__icontains=q) |
            Q(descripcion__icontains=q)
        )
    if tipo:
        recursos = recursos.filter(tipo=tipo)

    # Separar por tipo para la vista
    novedades  = recursos.filter(tipo='novedad')
    tutoriales = recursos.filter(tipo='tutorial')
    manuales   = recursos.filter(tipo='manual')
    videos     = recursos.filter(tipo='video')

    return render(request, 'biblioteca/recurso_list.html', {
        'recursos':      recursos,
        'novedades':     novedades,
        'tutoriales':    tutoriales,
        'manuales':      manuales,
        'videos':        videos,
        'total':         recursos.count(),
        'q':             q,
        'tipo':          tipo,
        'tipo_choices':  Recurso.TIPO_CHOICES,
    })


@login_required
def recurso_detail(request, pk):
    recurso = get_object_or_404(Recurso, pk=pk, publicado=True)
    return render(request, 'biblioteca/recurso_detail.html', {'recurso': recurso})


@solo_bibliotecario
def recurso_crear(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para publicar recursos.')
        return redirect('biblioteca:recurso_list')

    form = RecursoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        recurso        = form.save(commit=False)
        recurso.autor  = request.user
        recurso.save()
        messages.success(request, f'Recurso "{recurso.titulo}" publicado correctamente.')
        return redirect('biblioteca:recurso_detail', pk=recurso.pk)

    return render(request, 'biblioteca/recurso_form.html', {
        'form':   form,
        'titulo': 'Publicar recurso',
        'accion': 'Publicar',
    })


@solo_bibliotecario
def recurso_editar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para editar recursos.')
        return redirect('biblioteca:recurso_list')

    recurso = get_object_or_404(Recurso, pk=pk)
    form    = RecursoForm(request.POST or None, request.FILES or None, instance=recurso)
    if form.is_valid():
        form.save()
        messages.success(request, 'Recurso actualizado correctamente.')
        return redirect('biblioteca:recurso_detail', pk=recurso.pk)

    return render(request, 'biblioteca/recurso_form.html', {
        'form':    form,
        'recurso': recurso,
        'titulo':  'Editar recurso',
        'accion':  'Guardar cambios',
    })


@solo_bibliotecario
def recurso_eliminar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para eliminar recursos.')
        return redirect('biblioteca:recurso_list')

    recurso = get_object_or_404(Recurso, pk=pk)
    if request.method == 'POST':
        titulo = recurso.titulo
        if recurso.archivo and os.path.isfile(recurso.archivo.path):
            os.remove(recurso.archivo.path)
        if recurso.imagen and os.path.isfile(recurso.imagen.path):
            os.remove(recurso.imagen.path)
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
    
# ── PANEL BIBLIOTECARIO ──────────────────────────────────────

@solo_bibliotecario
def panel_bibliotecario(request):
    if not request.user.is_staff:
        messages.error(request, 'Acceso restringido al bibliotecario.')
        return redirect('home')
    
    # Actualizar estados vencidos cada vez que se carga el panel
    Prestamo.actualizar_vencidos()

    import json
    from django.db.models import Count
    from django.utils import timezone

    hoy = timezone.now().date()

    stats = {
        'total_libros':     Libro.objects.count(),
        'total_ejemplares': Ejemplar.objects.count(),
        'total_tesis':      Tesis.objects.count(),
        'total_profesores': Profesor.objects.filter(activo=True).count(),
        'total_usuarios':   User.objects.count(),
        'total_recursos':   Recurso.objects.filter(publicado=True).count(),
    }
    
    solicitudes_pendientes = SolicitudPrestamo.objects.filter(estado='pendiente').count()
    renovaciones_pendientes = RenovacionPrestamo.objects.filter(estado='pendiente').count()

    prestamos_activos  = Prestamo.objects.filter(estado='activo').count()
    prestamos_vencidos = Prestamo.objects.filter(estado='vencido').count()

    prestamos_por_vencer = Prestamo.objects.filter(
        estado='activo',
        fecha_devolucion__lte=hoy + timezone.timedelta(days=2),
        fecha_devolucion__gte=hoy,
    ).select_related('ejemplar__libro', 'usuario')

    prestamos_vencidos_lista = Prestamo.objects.filter(
        estado='vencido'
    ).select_related('ejemplar__libro', 'usuario')[:10]

    ultimos_libros = Libro.objects.order_by('-fecha_registro')[:5]
    
    # Últimas notificaciones enviadas
    ultimas_notificaciones = NotificacionCorreo.objects.select_related(
        'prestamo__usuario',
        'prestamo__ejemplar__libro'
    ).order_by('-enviado_en')[:8]

    # Resumen de notificaciones
    total_notificaciones  = NotificacionCorreo.objects.count()
    notif_exitosas        = NotificacionCorreo.objects.filter(exitoso=True).count()
    notif_fallidas        = NotificacionCorreo.objects.filter(exitoso=False).count()

    # ── Datos para gráficas ──────────────────────────────────

    # 1. Préstamos por mes (últimos 6 meses)
    labels_meses = []
    valores_meses = []
    nombres_meses = ['Ene','Feb','Mar','Abr','May','Jun',
                     'Jul','Ago','Sep','Oct','Nov','Dic']
    for i in range(5, -1, -1):
        fecha = hoy - timezone.timedelta(days=30 * i)
        count = Prestamo.objects.filter(
            fecha_prestamo__year=fecha.year,
            fecha_prestamo__month=fecha.month,
        ).count()
        labels_meses.append(nombres_meses[fecha.month - 1])
        valores_meses.append(count)

    datos_prestamos_json = json.dumps({
        'labels':  labels_meses,
        'valores': valores_meses,
    })

    # 2. Libros por categoría
    cats = Libro.objects.values(
        'categoria__nombre'
    ).annotate(total=Count('id')).order_by('-total')
    datos_categorias_json = json.dumps({
        'labels':  [c['categoria__nombre'] or 'Sin categoría' for c in cats],
        'valores': [c['total'] for c in cats],
    })

    # 3. Estado del inventario
    estados = {'disponible': 0, 'prestado': 0, 'reservado': 0, 'deteriorado': 0}
    for ej in Ejemplar.objects.values('estado').annotate(total=Count('id')):
        if ej['estado'] in estados:
            estados[ej['estado']] = ej['total']
    datos_inventario_json = json.dumps(list(estados.values()))

    usuarios = User.objects.select_related('perfil').order_by('-date_joined')

    return render(request, 'biblioteca/panel_bibliotecario.html', {
        'stats':                    stats,
        'prestamos_activos':        prestamos_activos,
        'prestamos_vencidos':       prestamos_vencidos,
        'prestamos_por_vencer':     prestamos_por_vencer,
        'prestamos_vencidos_lista': prestamos_vencidos_lista,
        'ultimos_libros':           ultimos_libros,
        'usuarios':                 usuarios,
        'datos_prestamos_json':     datos_prestamos_json,
        'datos_categorias_json':    datos_categorias_json,
        'datos_inventario_json':    datos_inventario_json,
        'solicitudes_pendientes':   solicitudes_pendientes,
        'renovaciones_pendientes': renovaciones_pendientes,
        
        'ultimas_notificaciones': ultimas_notificaciones,
        'total_notificaciones':   total_notificaciones,
        'notif_exitosas':         notif_exitosas,
        'notif_fallidas':         notif_fallidas,
    })


# ── PERFIL PROPIO ────────────────────────────────────────────

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
        # Guardar datos del User
        request.user.first_name = form.cleaned_data['first_name']
        request.user.last_name  = form.cleaned_data['last_name']
        request.user.email      = form.cleaned_data['email']
        request.user.save()
        form.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('biblioteca:mi_perfil')

    mis_prestamos = Prestamo.objects.filter(
        usuario=request.user
    ).select_related('ejemplar__libro').order_by('-fecha_prestamo')[:5]

    return render(request, 'biblioteca/mi_perfil.html', {
        'form':          form,
        'perfil':        perfil,
        'mis_prestamos': mis_prestamos,
    })


# ── GESTIÓN DE USUARIOS (solo bibliotecario) ─────────────────

@solo_bibliotecario
def usuario_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Acceso restringido.')
        return redirect('home')

    usuarios = User.objects.select_related('perfil').order_by('-date_joined')
    return render(request, 'biblioteca/usuario_list.html', {'usuarios': usuarios})


@solo_bibliotecario
def usuario_editar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Acceso restringido.')
        return redirect('home')

    usuario = get_object_or_404(User, pk=pk)
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)
    form = GestionUsuarioForm(request.POST or None, instance=perfil)
    if form.is_valid():
        form.save()
        messages.success(request, f'Usuario "{usuario.username}" actualizado.')
        return redirect('biblioteca:usuario_list')

    return render(request, 'biblioteca/usuario_editar.html', {
        'form':    form,
        'usuario': usuario,
        'perfil':  perfil,
    })
    
@login_required
def home(request):
    context = {
        'total_libros':     Libro.objects.count(),
        'total_prestamos':  Prestamo.objects.filter(estado='activo').count(),
        'total_tesis':      Tesis.objects.filter(disponible=True).count(),
        'total_profesores': Profesor.objects.filter(activo=True).count(),
    }
    return render(request, 'home.html', context)


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegistroUsuarioForm(request.POST or None)
    if form.is_valid():
        usuario = form.save()
        login(request, usuario)
        return redirect('home')
    return render(request, 'registration/registro.html', {'form': form})

@solo_bibliotecario
def notificaciones_list(request):
    # Envío masivo desde el botón del panel
    if request.method == 'POST' and request.POST.get('accion') == 'enviar_masivo':
        from .correo import procesar_notificaciones_pendientes
        enviados = procesar_notificaciones_pendientes()
        messages.success(
            request,
            f'{enviados} notificación(es) enviada(s) correctamente.'
        )
        return redirect('biblioteca:notificaciones')

    notificaciones = NotificacionCorreo.objects.select_related(
        'prestamo__usuario',
        'prestamo__ejemplar__libro'
    ).order_by('-enviado_en')

    tipo_filtro  = request.GET.get('tipo', '')
    exito_filtro = request.GET.get('exitoso', '')

    if tipo_filtro:
        notificaciones = notificaciones.filter(tipo=tipo_filtro)
    if exito_filtro:
        notificaciones = notificaciones.filter(exitoso=(exito_filtro == '1'))

    return render(request, 'biblioteca/notificaciones_list.html', {
        'notificaciones':      paginar(notificaciones, request, 20),
        'tipo_filtro':         tipo_filtro,
        'exito_filtro':        exito_filtro,
        'total':               NotificacionCorreo.objects.count(),
        'total_exitosas':      NotificacionCorreo.objects.filter(exitoso=True).count(),
        'total_fallidas':      NotificacionCorreo.objects.filter(exitoso=False).count(),
        'total_pendientes_envio': Prestamo.objects.filter(estado='vencido').count(),
    })
    
@rol_requerido('estudiante', 'profesor', 'bibliotecario')
def solicitud_crear(request, libro_pk):
    libro = get_object_or_404(Libro, pk=libro_pk)

    # Verificar que el libro tenga ejemplares disponibles
    if not libro.ejemplares_disponibles():
        messages.error(request, 'Este libro no tiene ejemplares disponibles.')
        return redirect('biblioteca:libro_detail', pk=libro_pk)
    
    @rol_requerido('estudiante', 'profesor', 'bibliotecario')
    def solicitud_crear(request, libro_pk):
        libro = get_object_or_404(Libro, pk=libro_pk)

        if not libro.ejemplares_disponibles():
            messages.error(request, 'Este libro no tiene ejemplares disponibles.')
            return redirect('biblioteca:libro_detail', pk=libro_pk)

        # ── NUEVO: verificar límite de préstamos activos ──────────
        from django.conf import settings
        limite = getattr(settings, 'LIMITE_PRESTAMOS_ACTIVOS', 3)
        prestamos_activos = Prestamo.objects.filter(
            usuario=request.user,
            estado__in=['activo', 'vencido']
        ).count()
        if prestamos_activos >= limite:
            messages.error(
                request,
                f'Has alcanzado el límite de {limite} préstamos activos simultáneos. '
                f'Debes devolver un libro antes de solicitar otro.'
            )
            return redirect('biblioteca:libro_detail', pk=libro_pk)
        # ─────────────────────────────────────────────────────────

        solicitud_existente = SolicitudPrestamo.objects.filter(
            usuario=request.user,
            libro=libro,
            estado='pendiente'
        ).exists()
        if solicitud_existente:
            messages.warning(request, 'Ya tienes una solicitud pendiente para este libro.')
            return redirect('biblioteca:libro_detail', pk=libro_pk)

        form = SolicitudPrestamoForm(request.POST or None)
        if form.is_valid():
            solicitud          = form.save(commit=False)
            solicitud.libro    = libro
            solicitud.usuario  = request.user
            solicitud.save()
            messages.success(
                request,
                'Solicitud enviada correctamente. El bibliotecario la revisará pronto.'
            )
            return redirect('biblioteca:mis_solicitudes')

        return render(request, 'biblioteca/solicitud_form.html', {
            'form':  form,
            'libro': libro,
        })

    # Verificar que no tenga una solicitud pendiente para este libro
    solicitud_existente = SolicitudPrestamo.objects.filter(
        usuario=request.user,
        libro=libro,
        estado='pendiente'
    ).exists()
    if solicitud_existente:
        messages.warning(request, 'Ya tienes una solicitud pendiente para este libro.')
        return redirect('biblioteca:libro_detail', pk=libro_pk)

    form = SolicitudPrestamoForm(request.POST or None)
    if form.is_valid():
        solicitud          = form.save(commit=False)
        solicitud.libro    = libro
        solicitud.usuario  = request.user
        solicitud.save()
        messages.success(
            request,
            f'Solicitud enviada correctamente. '
            f'El bibliotecario la revisará pronto.'
        )
        return redirect('biblioteca:mis_solicitudes')

    return render(request, 'biblioteca/solicitud_form.html', {
        'form':  form,
        'libro': libro,
    })


@login_required
def mis_solicitudes(request):
    solicitudes = SolicitudPrestamo.objects.filter(
        usuario=request.user
    ).select_related('libro', 'prestamo').order_by('-fecha_solicitud')

    return render(request, 'biblioteca/mis_solicitudes.html', {
        'solicitudes': paginar(solicitudes, request, 10),
    })


@solo_bibliotecario
def solicitud_list(request):
    estado_filtro = request.GET.get('estado', 'pendiente')
    solicitudes   = SolicitudPrestamo.objects.select_related(
        'libro', 'usuario'
    ).all()

    if estado_filtro:
        solicitudes = solicitudes.filter(estado=estado_filtro)

    return render(request, 'biblioteca/solicitud_list.html', {
        'solicitudes':    paginar(solicitudes, request, 15),
        'estado_filtro':  estado_filtro,
        'total_pendientes': SolicitudPrestamo.objects.filter(estado='pendiente').count(),
    })


@solo_bibliotecario
def solicitud_aprobar(request, pk):
    solicitud = get_object_or_404(SolicitudPrestamo, pk=pk, estado='pendiente')
    form      = AprobarSolicitudForm(
        request.POST or None,
        libro=solicitud.libro
    )

    if form.is_valid():
        ejemplar         = form.cleaned_data['ejemplar']
        fecha_devolucion = form.cleaned_data['fecha_devolucion']
        respuesta        = form.cleaned_data.get('respuesta', '')

        # Crear el préstamo
        prestamo = Prestamo.objects.create(
            ejemplar         = ejemplar,
            usuario          = solicitud.usuario,
            fecha_devolucion = fecha_devolucion,
            estado           = 'activo',
            registrado_por   = request.user,
            notas            = f'Aprobado desde solicitud #{solicitud.pk}',
        )

        # Marcar el ejemplar como prestado
        ejemplar.estado = 'prestado'
        ejemplar.save()

        # Actualizar la solicitud
        solicitud.estado          = 'aprobada'
        solicitud.prestamo        = prestamo
        solicitud.respuesta       = respuesta
        solicitud.atendida_por    = request.user
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()
        
        # Enviar correo de confirmación al usuario
        enviar_confirmacion_prestamo(prestamo)

        messages.success(
            request,
            f'Solicitud aprobada. Préstamo creado para '
            f'{solicitud.usuario.get_full_name() or solicitud.usuario.username}.'
        )
        return redirect('biblioteca:solicitud_list')

    return render(request, 'biblioteca/solicitud_aprobar.html', {
        'form':      form,
        'solicitud': solicitud,
    })


@solo_bibliotecario
def solicitud_rechazar(request, pk):
    solicitud = get_object_or_404(SolicitudPrestamo, pk=pk, estado='pendiente')
    form      = RechazarSolicitudForm(request.POST or None)

    if form.is_valid():
        solicitud.estado          = 'rechazada'
        solicitud.respuesta       = form.cleaned_data['respuesta']
        solicitud.atendida_por    = request.user
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()
        
        # Enviar correo de rechazo al usuario
        enviar_rechazo_solicitud(solicitud)    
        
        messages.success(request, 'Solicitud rechazada.')
        return redirect('biblioteca:solicitud_list')

    return render(request, 'biblioteca/solicitud_rechazar.html', {
        'form':      form,
        'solicitud': solicitud,
    })
    
@rol_requerido('estudiante', 'profesor', 'bibliotecario')
def renovacion_crear(request, prestamo_pk):
    prestamo = get_object_or_404(Prestamo, pk=prestamo_pk, usuario=request.user)

    # Solo se puede renovar si está activo o vencido
    if prestamo.estado == 'devuelto':
        messages.error(request, 'Este préstamo ya fue devuelto.')
        return redirect('biblioteca:prestamo_list')

    # Verificar que no tenga una renovación pendiente
    renovacion_pendiente = RenovacionPrestamo.objects.filter(
        prestamo=prestamo,
        estado='pendiente'
    ).exists()
    if renovacion_pendiente:
        messages.warning(request, 'Ya tienes una solicitud de renovación pendiente para este préstamo.')
        return redirect('biblioteca:prestamo_list')

    form = RenovacionForm(request.POST or None)
    if form.is_valid():
        renovacion          = form.save(commit=False)
        renovacion.prestamo = prestamo
        renovacion.usuario  = request.user
        renovacion.save()
        messages.success(
            request,
            'Solicitud de renovación enviada. El bibliotecario la revisará pronto.'
        )
        return redirect('biblioteca:mis_renovaciones')

    return render(request, 'biblioteca/renovacion_form.html', {
        'form':     form,
        'prestamo': prestamo,
    })


@login_required
def mis_renovaciones(request):
    renovaciones = RenovacionPrestamo.objects.filter(
        usuario=request.user
    ).select_related(
        'prestamo__ejemplar__libro'
    ).order_by('-fecha_solicitud')

    return render(request, 'biblioteca/mis_renovaciones.html', {
        'renovaciones': paginar(renovaciones, request, 10),
    })


@solo_bibliotecario
def renovacion_list(request):
    estado_filtro = request.GET.get('estado', 'pendiente')
    renovaciones  = RenovacionPrestamo.objects.select_related(
        'prestamo__ejemplar__libro', 'usuario'
    ).all()

    if estado_filtro:
        renovaciones = renovaciones.filter(estado=estado_filtro)

    return render(request, 'biblioteca/renovacion_list.html', {
        'renovaciones':     paginar(renovaciones, request, 15),
        'estado_filtro':    estado_filtro,
        'total_pendientes': RenovacionPrestamo.objects.filter(estado='pendiente').count(),
    })


@solo_bibliotecario
def renovacion_aprobar(request, pk):
    renovacion = get_object_or_404(RenovacionPrestamo, pk=pk, estado='pendiente')
    form       = AprobarRenovacionForm(
        request.POST or None,
        prestamo=renovacion.prestamo
    )

    if form.is_valid():
        nueva_fecha = form.cleaned_data['nueva_fecha']
        respuesta   = form.cleaned_data.get('respuesta', '')

        # Actualizar la fecha del préstamo
        renovacion.prestamo.fecha_devolucion = nueva_fecha
        if renovacion.prestamo.estado == 'vencido':
            renovacion.prestamo.estado = 'activo'
        renovacion.prestamo.save()

        # Actualizar la renovación
        renovacion.estado          = 'aprobada'
        renovacion.nueva_fecha     = nueva_fecha
        renovacion.respuesta       = respuesta
        renovacion.atendida_por    = request.user
        renovacion.fecha_respuesta = timezone.now()
        renovacion.save()

        # Enviar correo
        enviar_confirmacion_renovacion(renovacion)

        messages.success(
            request,
            f'Renovación aprobada. Nueva fecha: {nueva_fecha.strftime("%d/%m/%Y")}.'
        )
        return redirect('biblioteca:renovacion_list')

    return render(request, 'biblioteca/renovacion_aprobar.html', {
        'form':       form,
        'renovacion': renovacion,
    })


@solo_bibliotecario
def renovacion_rechazar(request, pk):
    renovacion = get_object_or_404(RenovacionPrestamo, pk=pk, estado='pendiente')
    form       = RechazarRenovacionForm(request.POST or None)

    if form.is_valid():
        renovacion.estado          = 'rechazada'
        renovacion.respuesta       = form.cleaned_data['respuesta']
        renovacion.atendida_por    = request.user
        renovacion.fecha_respuesta = timezone.now()
        renovacion.save()

        # Enviar correo
        enviar_rechazo_renovacion(renovacion)

        messages.success(request, 'Renovación rechazada.')
        return redirect('biblioteca:renovacion_list')

    return render(request, 'biblioteca/renovacion_rechazar.html', {
        'form':       form,
        'renovacion': renovacion,
    })
    
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
        'form':   form,
        'titulo': 'Nueva categoría',
        'accion': 'Crear categoría',
    })


@solo_bibliotecario
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form      = CategoriaForm(request.POST or None, instance=categoria)
    if form.is_valid():
        form.save()
        messages.success(request, f'Categoría "{categoria.nombre}" actualizada.')
        return redirect('biblioteca:categoria_list')
    return render(request, 'biblioteca/categoria_form.html', {
        'form':      form,
        'categoria': categoria,
        'titulo':    'Editar categoría',
        'accion':    'Guardar cambios',
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
    
@login_required
def carnet_biblioteca(request):
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)
    prestamos_activos = Prestamo.objects.filter(
        usuario=request.user,
        estado__in=['activo', 'vencido']
    ).select_related('ejemplar__libro').order_by('fecha_devolucion')

    return render(request, 'biblioteca/carnet.html', {
        'perfil':           perfil,
        'prestamos_activos': prestamos_activos,
    })
    
@login_required
def busqueda_global(request):
    q = request.GET.get('q', '').strip()

    libros     = []
    tesis      = []
    profesores = []
    recursos   = []

    if q:
        libros = Libro.objects.filter(
            Q(titulo__icontains=q) |
            Q(autor__icontains=q)  |
            Q(isbn__icontains=q)
        ).select_related('categoria')[:8]

        tesis = Tesis.objects.filter(
            Q(titulo__icontains=q)  |
            Q(autor__icontains=q)   |
            Q(area__icontains=q)    |
            Q(resumen__icontains=q)
        )[:6]

        profesores = Profesor.objects.filter(
            Q(nombre__icontains=q)       |
            Q(apellidos__icontains=q)    |
            Q(especialidad__icontains=q)
        ).filter(activo=True)[:6]

        recursos = Recurso.objects.filter(
            Q(titulo__icontains=q)       |
            Q(descripcion__icontains=q)
        ).filter(publicado=True)[:6]

    total = len(libros) + len(tesis) + len(profesores) + len(recursos)

    return render(request, 'biblioteca/busqueda_global.html', {
        'q':          q,
        'libros':     libros,
        'tesis':      tesis,
        'profesores': profesores,
        'recursos':   recursos,
        'total':      total,
    })