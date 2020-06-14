from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Recipe


def index(request):
    recipe_list = Recipe.objects.order_by('title')
    context = {
        'recipe_list': recipe_list,
    }
    return render(request, 'recipes/index.html', context)


def detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ingredients_list = recipe.ingredients.split('\\n')
    method_list = recipe.method.split('\\n')
    context = {
        'recipe': recipe,
        'ingredients_list': ingredients_list,
        'method_list': method_list,
    }
    return render(request, 'recipes/detail.html', context)
