from django import template
from apps.core.utils import format_money as util_format_money

register = template.Library()

@register.filter
def format_money(value):
    """
    Template filter to format money using the core utility.
    """
    return util_format_money(value)
