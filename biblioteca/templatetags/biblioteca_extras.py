from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_pagina(context, numero):
    """
    Devuelve la URL actual conservando todos los parámetros GET
    excepto 'pagina', que se reemplaza por el número indicado.
    """
    request = context['request']
    params  = request.GET.copy()
    params['pagina'] = numero
    return f'?{params.urlencode()}'

@register.filter
def abs_valor(value):
    """Devuelve el valor absoluto de un número."""
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return 0


@register.filter
def pluralize_es(value, arg=''):
    """
    Pluraliza en español.
    Uso: {{ valor|pluralize_es:"día,días" }}
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return ''
    bits = arg.split(',')
    if len(bits) == 2:
        singular, plural = bits
        return singular if value == 1 else plural
    return ''