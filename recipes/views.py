import random

from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify

from .models import Recipe, RecipeImage

BULLET_POINT_DELIMITER = ';'


def fixtures_are_loaded(categorised_recipe_lists: list):
    for categorised_recipe_list in categorised_recipe_lists:
        if categorised_recipe_list["recipes"]:
            return True
    return False


def index(request):
    search_term = request.GET.get('search_term')
    if not search_term:
        recipe_list = Recipe.objects.order_by('title')
        return render_recipe_category_lists(recipe_list, request)
    else:
        recipes_matching_search_term = Recipe.objects.filter(title__icontains=search_term)
        if len(recipes_matching_search_term) == 1:
            return redirect('recipes:detail', recipes_matching_search_term[0].pk, permanent=True)
        return render_recipe_category_lists(recipes_matching_search_term, request)


def render_recipe_category_lists(recipe_list, request):
    categories = set([recipe.category for recipe in recipe_list])
    categorised_recipe_lists = []
    for category in categories:
        categorised_recipe_lists.append({
            "category": category,
            "recipes": [recipe for recipe in recipe_list if recipe.category == category]
        })
    categorised_recipe_lists.sort(key=lambda x: len(x["recipes"]), reverse=True)
    fixtures_loaded = fixtures_are_loaded(categorised_recipe_lists)
    context = {
        'categorised_recipe_lists': categorised_recipe_lists,
        'fixtures_loaded': fixtures_loaded,
        'all_recipe_titles': [recipe.title for recipe in Recipe.objects.all()]
    }
    return render(request, 'recipes/index.html', context)


def detail(request, recipe_id, slug=None):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    expected_slug = slugify(recipe.title)
    if slug != expected_slug:
        return redirect(f"/{str(recipe_id)}/{expected_slug}/", permanent=True)
    ingredients_list = recipe.ingredients.split(BULLET_POINT_DELIMITER)
    method_list = recipe.method.split(BULLET_POINT_DELIMITER)
    image_url_list = [image.url for image in RecipeImage.objects.filter(recipe_id=recipe_id).order_by('relative_order')]
    recipe.tags = sorted(recipe.tags, key=str.casefold)
    context = {
        'recipe': recipe,
        'ingredients_list': ingredients_list,
        'method_list': method_list,
        'image_url_list': image_url_list
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
