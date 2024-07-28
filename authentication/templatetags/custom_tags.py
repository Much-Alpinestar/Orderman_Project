from django import template

register = template.Library()

@register.filter(name='boolean_to_yes_no')
def boolean_to_yes_no(value):
    if value is True:
        return 'Ja'
    elif value is False:
        return 'Nein'
    return value
