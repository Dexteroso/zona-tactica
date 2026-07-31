from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def antiguedad(value):
    if value is None:
        return ""

    ahora = timezone.now()
    if timezone.is_naive(value) and timezone.is_aware(ahora):
        value = timezone.make_aware(value, timezone.get_current_timezone())

    segundos = max((ahora - value).total_seconds(), 0)
    minutos = int(segundos // 60)

    if minutos >= 24 * 60:
        cantidad = minutos // (24 * 60)
        unidad = "día" if cantidad == 1 else "días"
    elif minutos >= 60:
        cantidad = minutos // 60
        unidad = "hora" if cantidad == 1 else "horas"
    else:
        cantidad = minutos
        unidad = "minuto" if cantidad == 1 else "minutos"

    return f"hace {cantidad} {unidad}"
