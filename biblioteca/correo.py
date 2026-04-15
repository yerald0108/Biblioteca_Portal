from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import NotificacionCorreo

def enviar_notificacion_vencimiento(prestamo):
    """Envía correo al usuario cuando su préstamo está vencido."""
    usuario = prestamo.usuario
    if not usuario.email:
        return False

    asunto = f'[Biblioteca] Préstamo vencido: {prestamo.ejemplar.libro.titulo}'
    cuerpo = f"""
Estimado/a {usuario.get_full_name() or usuario.username},

Le informamos que su préstamo ha vencido:

  Libro:           {prestamo.ejemplar.libro.titulo}
  Autor:           {prestamo.ejemplar.libro.autor}
  Código ejemplar: {prestamo.ejemplar.codigo}
  Fecha límite:    {prestamo.fecha_devolucion.strftime('%d/%m/%Y')}
  Días de retraso: {abs(prestamo.dias_restantes())}

Por favor, devuelva el ejemplar a la biblioteca a la brevedad posible.

Portal de Información Institucional
    """

    try:
        send_mail(asunto, cuerpo, None, [usuario.email], fail_silently=False)
        NotificacionCorreo.objects.create(
            prestamo=prestamo, tipo='vencimiento', exitoso=True,
            mensaje=f'Correo enviado a {usuario.email}'
        )
        return True
    except Exception as e:
        NotificacionCorreo.objects.create(
            prestamo=prestamo, tipo='vencimiento', exitoso=False,
            mensaje=str(e)
        )
        return False

def enviar_recordatorio(prestamo):
    """Envía recordatorio cuando faltan 2 días o menos para el vencimiento."""
    usuario = prestamo.usuario
    if not usuario.email:
        return False

    dias = prestamo.dias_restantes()
    asunto = f'[Biblioteca] Recordatorio: devolución en {dias} día(s)'
    cuerpo = f"""
Estimado/a {usuario.get_full_name() or usuario.username},

Le recordamos que su préstamo vence pronto:

  Libro:        {prestamo.ejemplar.libro.titulo}
  Autor:        {prestamo.ejemplar.libro.autor}
  Fecha límite: {prestamo.fecha_devolucion.strftime('%d/%m/%Y')}
  Días restantes: {dias}

Por favor, devuelva el ejemplar a tiempo o comuníquese con la biblioteca.

Portal de Información Institucional
    """

    try:
        send_mail(asunto, cuerpo, None, [usuario.email], fail_silently=False)
        NotificacionCorreo.objects.create(
            prestamo=prestamo, tipo='recordatorio', exitoso=True,
            mensaje=f'Recordatorio enviado a {usuario.email}'
        )
        return True
    except Exception as e:
        NotificacionCorreo.objects.create(
            prestamo=prestamo, tipo='recordatorio', exitoso=False,
            mensaje=str(e)
        )
        return False

def procesar_notificaciones_pendientes():
    """
    Revisa todos los préstamos activos y envía notificaciones según corresponda.
    Se llama desde el comando de gestión o manualmente desde el admin.
    """
    from .models import Prestamo
    from django.utils import timezone

    hoy      = timezone.now().date()
    enviados = 0

    # Préstamos vencidos sin notificación enviada hoy
    vencidos = Prestamo.objects.filter(
        estado='vencido'
    ).exclude(
        notificaciones__tipo='vencimiento',
        notificaciones__enviado_en__date=hoy
    )
    for p in vencidos:
        if enviar_notificacion_vencimiento(p):
            enviados += 1

    # Préstamos que vencen en 1 o 2 días
    limite_min = hoy
    limite_max = hoy + timezone.timedelta(days=2)
    por_vencer = Prestamo.objects.filter(
        estado='activo',
        fecha_devolucion__gt=limite_min,
        fecha_devolucion__lte=limite_max,
    ).exclude(
        notificaciones__tipo='recordatorio',
        notificaciones__enviado_en__date=hoy
    )
    for p in por_vencer:
        if enviar_recordatorio(p):
            enviados += 1

    return enviados