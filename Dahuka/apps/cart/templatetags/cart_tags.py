from django import template
from apps.core.utils import format_money as util_format_money

register = template.Library()

@register.filter
def format_money(value):
    return util_format_money(value)
