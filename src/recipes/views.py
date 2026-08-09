import random

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_safe

from .catalog import CATALOG, RecipeData
from .forms import PlannerForm, RecipeSearchForm


@require_safe
def index(request: HttpRequest) -> HttpResponse:
    search_form = RecipeSearchForm(request.GET)
    form_is_valid = search_form.is_valid()
    search_term = search_form.cleaned_data["q"] if form_is_valid else ""
    search_category = search_form.cleaned_data["category"] if form_is_valid else ""
    recipes = CATALOG
    if search_category:
        recipes = tuple(recipe for recipe in recipes if recipe.category == search_category)
    if search_term:
        recipes = tuple(
            recipe for recipe in recipes if search_term.casefold() in recipe.title.casefold()
        )
        if len(recipes) == 1:
            return redirect(recipes[0])

    grouped: dict[str, list[RecipeData]] = {}
    for recipe in recipes:
        grouped.setdefault(recipe.category, []).append(recipe)
    categories = sorted(grouped.items(), key=lambda item: item[0].casefold())
    return render(
        request,
        "recipes/index.html",
        {
            "active_section": "recipes",
            "all_recipes": CATALOG,
            "categories": categories,
            "search_form": search_form,
            "search_term": search_term,
        },
        status=200 if form_is_valid else 400,
    )


@require_safe
def detail(
    request: HttpRequest,
    recipe_id: int,
    slug: str,
) -> HttpResponse:
    recipe = next(
        (recipe for recipe in CATALOG if recipe.id == recipe_id and recipe.slug == slug),
        None,
    )
    if recipe is None:
        raise Http404
    return render(
        request,
        "recipes/detail.html",
        {
            "recipe": recipe,
            "sorted_tags": sorted(recipe.tags, key=str.casefold),
            "active_section": "recipes",
        },
    )


@require_safe
def planner(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "recipes/planner.html",
        {"active_section": "planner", "form": PlannerForm()},
    )


@require_safe
def search_results(request: HttpRequest) -> HttpResponse:
    form = PlannerForm(request.GET)
    tag = request.GET.get("tag", "").strip()
    if tag:
        recipes = [recipe for recipe in CATALOG if tag in recipe.tags]
        return render(
            request,
            "recipes/search_results.html",
            {
                "active_section": "recipes",
                "is_tag": True,
                "recipes": recipes,
                "search_term": tag,
            },
        )

    if not form.is_valid():
        return render(
            request,
            "recipes/planner.html",
            {"active_section": "planner", "form": form},
            status=400,
        )

    category = form.cleaned_data["category"]
    recipe_count = form.cleaned_data["recipe_count"]
    candidates = [recipe for recipe in CATALOG if recipe.category == category]
    recipes = random.sample(candidates, min(recipe_count, len(candidates)))
    return render(
        request,
        "recipes/search_results.html",
        {
            "active_section": "planner",
            "is_tag": False,
            "recipes": recipes,
            "search_term": category,
        },
    )


@require_safe
def about(request: HttpRequest) -> HttpResponse:
    return render(request, "recipes/about.html", {"active_section": "about"})


def not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    _ = exception
    return render(request, "404.html", status=404)
