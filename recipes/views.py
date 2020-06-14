from django.http import HttpResponse
from django.template import loader

from .models import Recipe


def index(request):
    recipe_list = Recipe.objects.order_by('title')
    template = loader.get_template('recipes/index.html')
    context = {
        'recipe_list': recipe_list,
    }
    return HttpResponse(template.render(context, request))


def detail(request, recipe_id):
    recipe = Recipe.objects.get(pk=recipe_id)
    return HttpResponse("<b>Title</b>: %s<br />"
                        "<b>Ingredients</b>: %s<br />"
                        "<b>Method</b>: %s<br />"
                        % (recipe.title, recipe.ingredients, recipe.method, ))
