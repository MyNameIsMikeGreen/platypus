from django.shortcuts import render
from django.http import HttpResponse

from .models import Recipe


def index(request):
    recipe_list = Recipe.objects.order_by('title')
    output = '<br />'.join([recipe.title for recipe in recipe_list])
    return HttpResponse(output)


def detail(request, recipe_id):
    return HttpResponse("You're looking at recipe %s." % recipe_id)
