from django import template

register = template.Library()

@register.filter
def format_money(value):
    try:
        value = float(value)
        return "{:,.0f}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value
