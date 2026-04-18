from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from .models import NotificacionCorreo


def _enviar_correo(asunto, cuerpo_texto, cuerpo_html, destinatario):
    """Función base que envía un correo con versión texto y HTML."""
    try:
        msg = EmailMultiAlternatives(
            subject=asunto,
            body=cuerpo_texto,
            to=[destinatario],
        )
        msg.attach_alternative(cuerpo_html, 'text/html')
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        return str(e)


def _html_base(contenido, titulo):
    """Plantilla HTML base para todos los correos."""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{titulo}</title>
    </head>
    <body style="margin:0; padding:0; background:#F1EFE8;
                 font-family:'Source Sans 3', Arial, sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#F1EFE8; padding:2rem 0;">
        <tr>
          <td align="center">
            <table width="600" cellpadding="0" cellspacing="0"
                   style="max-width:600px; width:100%;">

              <!-- HEADER -->
              <tr>
                <td style="background:#042C53; border-radius:12px 12px 0 0;
                           padding:1.5rem 2rem; text-align:center;">
                  <div style="display:inline-block; width:48px; height:48px;
                              background:#378ADD; border-radius:8px;
                              line-height:48px; text-align:center;
                              font-size:24px; font-weight:700; color:#E6F1FB;
                              margin-bottom:0.75rem;">B</div>
                  <div style="font-size:18px; font-weight:600;
                              color:#E6F1FB; margin-top:8px;">
                    Portal de Información Institucional
                  </div>
                  <div style="font-size:12px; color:#85B7EB; margin-top:4px;">
                    Biblioteca · Repositorio · Cuerpo Docente
                  </div>
                </td>
              </tr>

              <!-- CONTENIDO -->
              <tr>
                <td style="background:#ffffff; padding:2rem;">
                  {contenido}
                </td>
              </tr>

              <!-- FOOTER -->
              <tr>
                <td style="background:#F1EFE8; border-radius:0 0 12px 12px;
                           padding:1rem 2rem; text-align:center;
                           border-top:1px solid #D3D1C7;">
                  <p style="font-size:12px; color:#888780; margin:0;">
                    Este correo fue generado automáticamente por el
                    Portal de Información Institucional.
                    Por favor no respondas a este mensaje.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


def enviar_notificacion_vencimiento(prestamo):
    """Envía correo al usuario cuando su préstamo está vencido."""
    usuario = prestamo.usuario
    if not usuario.email:
        NotificacionCorreo.objects.create(
            prestamo=prestamo, tipo='vencimiento', exitoso=False,
            mensaje='El usuario no tiene correo registrado.'
        )
        return False

    dias_retraso = prestamo.dias_retraso()
    nombre       = usuario.get_full_name() or usuario.username
    libro        = prestamo.ejemplar.libro.titulo
    autor        = prestamo.ejemplar.libro.autor
    codigo       = prestamo.ejemplar.codigo
    fecha_limite = prestamo.fecha_devolucion.strftime('%d/%m/%Y')

    asunto = f'[Biblioteca] Préstamo vencido: {libro}'

    cuerpo_texto = f"""
Estimado/a {nombre},

Le informamos que su préstamo ha vencido:

  Libro:           {libro}
  Autor:           {autor}
  Código ejemplar: {codigo}
  Fecha límite:    {fecha_limite}
  Días de retraso: {dias_retraso}

Por favor, devuelva el ejemplar a la biblioteca a la brevedad posible.

Portal de Información Institucional
    """

    contenido_html = f"""
      <div style="margin-bottom:1.5rem;">
        <div style="background:#FCEBEB; border-left:4px solid #E24B4A;
                    border-radius:6px; padding:1rem 1.25rem; margin-bottom:1.5rem;">
          <div style="font-size:16px; font-weight:600; color:#A32D2D;
                      margin-bottom:4px;">
            Préstamo vencido
          </div>
          <div style="font-size:13px; color:#791F1F;">
            Han pasado <strong>{dias_retraso} día{'s' if dias_retraso != 1 else ''}</strong>
            desde la fecha límite de devolución.
          </div>
        </div>

        <p style="font-size:15px; color:#2C2C2A; margin-bottom:1.5rem;">
          Estimado/a <strong>{nombre}</strong>,
          le informamos que el siguiente préstamo ha superado su fecha límite:
        </p>

        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#F1EFE8; border-radius:8px;
                      padding:1rem; margin-bottom:1.5rem;">
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;
                       width:40%;">Libro</td>
            <td style="padding:6px 0; font-size:13px; font-weight:600;
                       color:#2C2C2A;">{libro}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">Autor</td>
            <td style="padding:6px 0; font-size:13px; color:#2C2C2A;">{autor}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">
              Código ejemplar
            </td>
            <td style="padding:6px 0; font-size:13px; color:#2C2C2A;">{codigo}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">
              Fecha límite
            </td>
            <td style="padding:6px 0; font-size:13px; font-weight:600;
                       color:#E24B4A;">{fecha_limite}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">
              Días de retraso
            </td>
            <td style="padding:6px 0; font-size:13px; font-weight:600;
                       color:#E24B4A;">{dias_retraso} día{'s' if dias_retraso != 1 else ''}</td>
          </tr>
        </table>

        <p style="font-size:14px; color:#2C2C2A; margin-bottom:1.5rem;">
          Por favor, devuelva el ejemplar a la biblioteca a la brevedad posible
          para evitar sanciones adicionales.
        </p>

        <div style="background:#E6F1FB; border-radius:6px;
                    padding:0.875rem 1rem; font-size:13px; color:#185FA5;">
          Si ya realizó la devolución, ignore este mensaje.
          Si tiene alguna consulta, comuníquese directamente con la biblioteca.
        </div>
      </div>
    """

    resultado = _enviar_correo(
        asunto, cuerpo_texto,
        _html_base(contenido_html, asunto),
        usuario.email
    )

    exitoso = resultado is True
    NotificacionCorreo.objects.create(
        prestamo=prestamo,
        tipo='vencimiento',
        exitoso=exitoso,
        mensaje=f'Enviado a {usuario.email}' if exitoso else str(resultado)
    )
    return exitoso


def enviar_recordatorio(prestamo):
    """Envía recordatorio cuando faltan 2 días o menos para el vencimiento."""
    usuario = prestamo.usuario
    if not usuario.email:
        NotificacionCorreo.objects.create(
            prestamo=prestamo, tipo='recordatorio', exitoso=False,
            mensaje='El usuario no tiene correo registrado.'
        )
        return False

    dias      = prestamo.dias_restantes()
    nombre    = usuario.get_full_name() or usuario.username
    libro     = prestamo.ejemplar.libro.titulo
    autor     = prestamo.ejemplar.libro.autor
    fecha_dev = prestamo.fecha_devolucion.strftime('%d/%m/%Y')

    asunto = f'[Biblioteca] Recordatorio: devolución en {dias} día{"s" if dias != 1 else ""}'

    cuerpo_texto = f"""
Estimado/a {nombre},

Le recordamos que su préstamo vence pronto:

  Libro:          {libro}
  Autor:          {autor}
  Fecha límite:   {fecha_dev}
  Días restantes: {dias}

Por favor, devuelva el ejemplar a tiempo.

Portal de Información Institucional
    """

    color_alerta = '#EF9F27' if dias > 1 else '#E24B4A'
    fondo_alerta = '#FAEEDA' if dias > 1 else '#FCEBEB'

    contenido_html = f"""
      <div style="margin-bottom:1.5rem;">
        <div style="background:{fondo_alerta}; border-left:4px solid {color_alerta};
                    border-radius:6px; padding:1rem 1.25rem; margin-bottom:1.5rem;">
          <div style="font-size:16px; font-weight:600; color:{color_alerta};
                      margin-bottom:4px;">
            Recordatorio de devolución
          </div>
          <div style="font-size:13px; color:{color_alerta};">
            Tu préstamo vence en
            <strong>{dias} día{'s' if dias != 1 else ''}</strong>.
          </div>
        </div>

        <p style="font-size:15px; color:#2C2C2A; margin-bottom:1.5rem;">
          Estimado/a <strong>{nombre}</strong>,
          te recordamos que tienes un préstamo próximo a vencer:
        </p>

        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#F1EFE8; border-radius:8px;
                      padding:1rem; margin-bottom:1.5rem;">
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A; width:40%;">
              Libro
            </td>
            <td style="padding:6px 0; font-size:13px; font-weight:600;
                       color:#2C2C2A;">{libro}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">Autor</td>
            <td style="padding:6px 0; font-size:13px; color:#2C2C2A;">{autor}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">
              Fecha límite
            </td>
            <td style="padding:6px 0; font-size:13px; font-weight:600;
                       color:{color_alerta};">{fecha_dev}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">
              Días restantes
            </td>
            <td style="padding:6px 0; font-size:13px; font-weight:600;
                       color:{color_alerta};">
              {dias} día{'s' if dias != 1 else ''}
            </td>
          </tr>
        </table>

        <p style="font-size:14px; color:#2C2C2A; margin-bottom:1.5rem;">
          Por favor devuelve el libro antes de la fecha límite para
          evitar que el préstamo quede vencido.
        </p>

        <div style="background:#E6F1FB; border-radius:6px;
                    padding:0.875rem 1rem; font-size:13px; color:#185FA5;">
          Si ya realizaste la devolución, ignora este mensaje.
        </div>
      </div>
    """

    resultado = _enviar_correo(
        asunto, cuerpo_texto,
        _html_base(contenido_html, asunto),
        usuario.email
    )

    exitoso = resultado is True
    NotificacionCorreo.objects.create(
        prestamo=prestamo,
        tipo='recordatorio',
        exitoso=exitoso,
        mensaje=f'Enviado a {usuario.email}' if exitoso else str(resultado)
    )
    return exitoso


def enviar_confirmacion_prestamo(prestamo):
    """
    Envía correo al usuario cuando su solicitud de préstamo es aprobada.
    """
    usuario = prestamo.usuario
    if not usuario.email:
        return False

    nombre    = usuario.get_full_name() or usuario.username
    libro     = prestamo.ejemplar.libro.titulo
    autor     = prestamo.ejemplar.libro.autor
    codigo    = prestamo.ejemplar.codigo
    fecha_dev = prestamo.fecha_devolucion.strftime('%d/%m/%Y')

    asunto = f'[Biblioteca] Préstamo aprobado: {libro}'

    cuerpo_texto = f"""
Estimado/a {nombre},

Tu solicitud de préstamo ha sido aprobada:

  Libro:        {libro}
  Autor:        {autor}
  Código:       {codigo}
  Devolver antes del: {fecha_dev}

Puedes retirar el libro en la biblioteca.

Portal de Información Institucional
    """

    contenido_html = f"""
      <div style="margin-bottom:1.5rem;">
        <div style="background:#E1F5EE; border-left:4px solid #1D9E75;
                    border-radius:6px; padding:1rem 1.25rem; margin-bottom:1.5rem;">
          <div style="font-size:16px; font-weight:600; color:#0F6E56;
                      margin-bottom:4px;">
            ¡Solicitud aprobada!
          </div>
          <div style="font-size:13px; color:#085041;">
            Tu préstamo ha sido registrado correctamente.
          </div>
        </div>

        <p style="font-size:15px; color:#2C2C2A; margin-bottom:1.5rem;">
          Estimado/a <strong>{nombre}</strong>,
          tu solicitud de préstamo ha sido aprobada por el bibliotecario:
        </p>

        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#F1EFE8; border-radius:8px;
                      padding:1rem; margin-bottom:1.5rem;">
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A; width:40%;">
              Libro
            </td>
            <td style="padding:6px 0; font-size:13px; font-weight:600;
                       color:#2C2C2A;">{libro}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">Autor</td>
            <td style="padding:6px 0; font-size:13px; color:#2C2C2A;">{autor}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">
              Código ejemplar
            </td>
            <td style="padding:6px 0; font-size:13px; color:#2C2C2A;">{codigo}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">
              Fecha límite de devolución
            </td>
            <td style="padding:6px 0; font-size:13px; font-weight:600;
                       color:#1D9E75;">{fecha_dev}</td>
          </tr>
        </table>

        <div style="background:#E6F1FB; border-radius:6px;
                    padding:0.875rem 1rem; font-size:13px; color:#185FA5;">
          Puedes retirar el libro directamente en la biblioteca.
          Recuerda devolverlo antes de la fecha límite.
        </div>
      </div>
    """

    resultado = _enviar_correo(
        asunto, cuerpo_texto,
        _html_base(contenido_html, asunto),
        usuario.email
    )
    return resultado is True


def enviar_rechazo_solicitud(solicitud):
    """
    Envía correo al usuario cuando su solicitud es rechazada.
    """
    usuario = solicitud.usuario
    if not usuario.email:
        return False

    nombre    = usuario.get_full_name() or usuario.username
    libro     = solicitud.libro.titulo
    motivo    = solicitud.respuesta or 'No se especificó un motivo.'

    asunto = f'[Biblioteca] Solicitud no aprobada: {libro}'

    cuerpo_texto = f"""
Estimado/a {nombre},

Tu solicitud de préstamo no pudo ser aprobada:

  Libro:  {libro}
  Motivo: {motivo}

Puedes contactar a la biblioteca para más información.

Portal de Información Institucional
    """

    contenido_html = f"""
      <div style="margin-bottom:1.5rem;">
        <div style="background:#FCEBEB; border-left:4px solid #E24B4A;
                    border-radius:6px; padding:1rem 1.25rem; margin-bottom:1.5rem;">
          <div style="font-size:16px; font-weight:600; color:#A32D2D;
                      margin-bottom:4px;">
            Solicitud no aprobada
          </div>
          <div style="font-size:13px; color:#791F1F;">
            Tu solicitud de préstamo no pudo ser procesada en este momento.
          </div>
        </div>

        <p style="font-size:15px; color:#2C2C2A; margin-bottom:1rem;">
          Estimado/a <strong>{nombre}</strong>,
          lamentamos informarte que tu solicitud para el siguiente libro
          no pudo ser aprobada:
        </p>

        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#F1EFE8; border-radius:8px;
                      padding:1rem; margin-bottom:1.5rem;">
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A; width:30%;">
              Libro
            </td>
            <td style="padding:6px 0; font-size:13px; font-weight:600;
                       color:#2C2C2A;">{libro}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;
                       vertical-align:top;">
              Motivo
            </td>
            <td style="padding:6px 0; font-size:13px; color:#2C2C2A;">{motivo}</td>
          </tr>
        </table>

        <div style="background:#E6F1FB; border-radius:6px;
                    padding:0.875rem 1rem; font-size:13px; color:#185FA5;">
          Puedes visitar la biblioteca para consultar otras opciones disponibles
          o realizar una nueva solicitud más adelante.
        </div>
      </div>
    """

    resultado = _enviar_correo(
        asunto, cuerpo_texto,
        _html_base(contenido_html, asunto),
        usuario.email
    )
    return resultado is True


def procesar_notificaciones_pendientes():
    """
    Revisa todos los préstamos y envía notificaciones según corresponda.
    """
    from .models import Prestamo
    hoy      = timezone.now().date()
    enviados = 0

    # Préstamos vencidos sin notificación enviada hoy
    vencidos = Prestamo.objects.filter(estado='vencido').exclude(
        notificaciones__tipo='vencimiento',
        notificaciones__enviado_en__date=hoy
    ).select_related('usuario', 'ejemplar__libro')

    for p in vencidos:
        if enviar_notificacion_vencimiento(p):
            enviados += 1

    # Préstamos que vencen en 1 o 2 días
    por_vencer = Prestamo.objects.filter(
        estado='activo',
        fecha_devolucion__gt=hoy,
        fecha_devolucion__lte=hoy + timezone.timedelta(days=2),
    ).exclude(
        notificaciones__tipo='recordatorio',
        notificaciones__enviado_en__date=hoy
    ).select_related('usuario', 'ejemplar__libro')

    for p in por_vencer:
        if enviar_recordatorio(p):
            enviados += 1

    return enviados
  
def enviar_confirmacion_renovacion(renovacion):
    """Correo al usuario cuando su renovación es aprobada."""
    usuario = renovacion.usuario
    if not usuario.email:
        return False

    nombre     = usuario.get_full_name() or usuario.username
    libro      = renovacion.prestamo.ejemplar.libro.titulo
    nueva_fecha = renovacion.nueva_fecha.strftime('%d/%m/%Y')

    asunto = f'[Biblioteca] Renovación aprobada: {libro}'

    cuerpo_texto = f"""
Estimado/a {nombre},

Tu solicitud de renovación ha sido aprobada.

  Libro:              {libro}
  Nueva fecha límite: {nueva_fecha}

Portal de Información Institucional
    """

    contenido_html = f"""
      <div>
        <div style="background:#E1F5EE; border-left:4px solid #1D9E75;
                    border-radius:6px; padding:1rem 1.25rem; margin-bottom:1.5rem;">
          <div style="font-size:16px; font-weight:600; color:#0F6E56; margin-bottom:4px;">
            ¡Renovación aprobada!
          </div>
          <div style="font-size:13px; color:#085041;">
            Tu préstamo ha sido extendido correctamente.
          </div>
        </div>
        <p style="font-size:15px; color:#2C2C2A; margin-bottom:1.5rem;">
          Estimado/a <strong>{nombre}</strong>,
          tu solicitud de renovación ha sido aprobada:
        </p>
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#F1EFE8; border-radius:8px; padding:1rem; margin-bottom:1.5rem;">
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A; width:40%;">Libro</td>
            <td style="padding:6px 0; font-size:13px; font-weight:600; color:#2C2C2A;">{libro}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">Nueva fecha límite</td>
            <td style="padding:6px 0; font-size:13px; font-weight:600; color:#1D9E75;">{nueva_fecha}</td>
          </tr>
        </table>
        <div style="background:#E6F1FB; border-radius:6px; padding:0.875rem 1rem;
                    font-size:13px; color:#185FA5;">
          Recuerda devolver el libro antes de la nueva fecha límite.
        </div>
      </div>
    """

    resultado = _enviar_correo(
        asunto, cuerpo_texto,
        _html_base(contenido_html, asunto),
        usuario.email
    )
    return resultado is True


def enviar_rechazo_renovacion(renovacion):
    """Correo al usuario cuando su renovación es rechazada."""
    usuario = renovacion.usuario
    if not usuario.email:
        return False

    nombre  = usuario.get_full_name() or usuario.username
    libro   = renovacion.prestamo.ejemplar.libro.titulo
    motivo  = renovacion.respuesta or 'No se especificó un motivo.'
    fecha   = renovacion.prestamo.fecha_devolucion.strftime('%d/%m/%Y')

    asunto = f'[Biblioteca] Renovación no aprobada: {libro}'

    cuerpo_texto = f"""
Estimado/a {nombre},

Tu solicitud de renovación no pudo ser aprobada.

  Libro:          {libro}
  Fecha límite:   {fecha}
  Motivo:         {motivo}

Por favor devuelve el libro antes de la fecha límite.

Portal de Información Institucional
    """

    contenido_html = f"""
      <div>
        <div style="background:#FCEBEB; border-left:4px solid #E24B4A;
                    border-radius:6px; padding:1rem 1.25rem; margin-bottom:1.5rem;">
          <div style="font-size:16px; font-weight:600; color:#A32D2D; margin-bottom:4px;">
            Renovación no aprobada
          </div>
          <div style="font-size:13px; color:#791F1F;">
            Tu solicitud de renovación no pudo ser procesada.
          </div>
        </div>
        <p style="font-size:15px; color:#2C2C2A; margin-bottom:1rem;">
          Estimado/a <strong>{nombre}</strong>,
          lamentamos informarte que tu solicitud de renovación no fue aprobada:
        </p>
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#F1EFE8; border-radius:8px; padding:1rem; margin-bottom:1.5rem;">
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A; width:30%;">Libro</td>
            <td style="padding:6px 0; font-size:13px; font-weight:600; color:#2C2C2A;">{libro}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A;">Fecha límite</td>
            <td style="padding:6px 0; font-size:13px; font-weight:600; color:#E24B4A;">{fecha}</td>
          </tr>
          <tr>
            <td style="padding:6px 0; font-size:13px; color:#5F5E5A; vertical-align:top;">Motivo</td>
            <td style="padding:6px 0; font-size:13px; color:#2C2C2A;">{motivo}</td>
          </tr>
        </table>
        <div style="background:#E6F1FB; border-radius:6px; padding:0.875rem 1rem;
                    font-size:13px; color:#185FA5;">
          Por favor devuelve el libro antes de la fecha límite para evitar sanciones.
          Si tienes alguna consulta, comunícate con la biblioteca directamente.
        </div>
      </div>
    """

    resultado = _enviar_correo(
        asunto, cuerpo_texto,
        _html_base(contenido_html, asunto),
        usuario.email
    )
    return resultado is True