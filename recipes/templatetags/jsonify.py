import json

from django import template

register = template.Library()


def jsonify(object):
    return json.dumps(object)


register.filter('jsonify', jsonify)
