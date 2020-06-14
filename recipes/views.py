from django.http import HttpResponse

from .models import Recipe


def index(request):
    recipe_list = Recipe.objects.order_by('title')
    output = '<br />'.join([recipe.title for recipe in recipe_list])
    return HttpResponse(output)


def detail(request, recipe_id):
    recipe = Recipe.objects.get(pk=recipe_id)
    return HttpResponse("<b>Title</b>: %s<br />"
                        "<b>Ingredients</b>: %s<br />"
                        "<b>Method</b>: %s<br />"
                        % (recipe.title, recipe.ingredients, recipe.method, ))
