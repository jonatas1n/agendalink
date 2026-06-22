from django import template

from core.currency import format_currency

register = template.Library()


@register.filter(name="currency")
def currency_filter(value):
    return format_currency(value, symbol=True)


@register.filter(name="currency_number")
def currency_number_filter(value):
    return format_currency(value, symbol=False)
