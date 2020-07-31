from django.shortcuts import render, get_object_or_404, get_list_or_404

from .models import Recipe, RecipeImage, CATEGORIES

BULLET_POINT_DELIMITER = ';'


def fixtures_are_loaded(categorised_recipe_lists: list):
    for categorised_recipe_list in categorised_recipe_lists:
        if categorised_recipe_list["recipes"]:
            return True
    return False


def index(request):
    recipe_list = Recipe.objects.order_by('title')
    categorised_recipe_lists = []
    for category in CATEGORIES:
        categorised_recipe_lists.append({
            "category": category[1],
            "recipes": [recipe for recipe in recipe_list if recipe.category == category[0]]
        })

    fixtures_loaded = fixtures_are_loaded(categorised_recipe_lists)

    context = {
        'categorised_recipe_lists': categorised_recipe_lists,
        'fixtures_loaded': fixtures_loaded
    }
    return render(request, 'recipes/index.html', context)


def detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ingredients_list = recipe.ingredients.split(BULLET_POINT_DELIMITER)
    method_list = recipe.method.split(BULLET_POINT_DELIMITER)
    image_list = RecipeImage.objects.filter(recipe_id=recipe_id).order_by('relative_order')
    context = {
        'recipe': recipe,
        'ingredients_list': ingredients_list,
        'method_list': method_list,
        'image_list': image_list
    }
    return render(request, 'recipes/detail.html', context)


def about(request):
    return render(request, 'recipes/about.html', None)
