from recipes.models import COMMA_ENCODING
from django import template

register = template.Library()


@register.filter
def decode_commas(object):
    return object.replace(COMMA_ENCODING, ",")
