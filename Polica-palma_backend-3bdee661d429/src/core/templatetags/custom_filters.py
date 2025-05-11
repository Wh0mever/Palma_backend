from django import template

register = template.Library()


@register.filter(name='to_str')
def to_str(val):
    try:
        return str(val)
    except:
        return val


@register.filter(name='decimal_dot')
def decimal_dot(val):
    try:
        return str(val).replace(',', '.')
    except:
        return val
