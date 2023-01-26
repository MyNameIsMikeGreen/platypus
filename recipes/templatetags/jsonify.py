import json

from django import template

register = template.Library()


@register.filter
def jsonify(object):
    return json.dumps(object)