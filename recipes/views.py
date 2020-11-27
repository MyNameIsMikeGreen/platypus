import random

from django.shortcuts import render, get_object_or_404

from .models import Recipe, RecipeImage

BULLET_POINT_DELIMITER = ';'


def fixtures_are_loaded(categorised_recipe_lists: list):
    for categorised_recipe_list in categorised_recipe_lists:
        if categorised_recipe_list["recipes"]:
            return True
    return False


def index(request):
    recipe_list = Recipe.objects.order_by('title')
    categories = set([recipe.category for recipe in recipe_list])
    categorised_recipe_lists = []
    for category in categories:
        categorised_recipe_lists.append({
            "category": category,
            "recipes": [recipe for recipe in recipe_list if recipe.category == category]
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


def planner(request):
    recipe_count = int(request.GET.get('recipe_count', '0'))
    if not recipe_count:
        return render(request, 'recipes/planner_input.html')
    category = request.GET.get('category', 'MAINS')
    recipes_in_category = Recipe.objects.filter(category=category)
    if recipe_count > len(recipes_in_category):
        recipe_count = len(recipes_in_category)
    recipe_set = set()
    while len(recipe_set) < recipe_count:
        recipe_set.add(random.choice(recipes_in_category))
    context = {
        'recipe_list': recipe_set
    }
    return render(request, 'recipes/planner_results.html', context)


def about(request):
    return render(request, 'recipes/about.html')
