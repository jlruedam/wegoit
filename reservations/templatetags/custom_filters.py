from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplica value * arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''