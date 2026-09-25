import random

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_safe

from .catalog import CATALOG, RecipeData
from .forms import PlannerForm, RecipeSearchForm
from .shopping_list import build_shared_shopping_list


@require_safe
def index(request: HttpRequest) -> HttpResponse:
    search_form = RecipeSearchForm(request.GET)
    form_is_valid = search_form.is_valid()
    search_term = search_form.cleaned_data["q"] if form_is_valid else ""
    recipes = CATALOG
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
    all_tags = sorted({tag for recipe in CATALOG for tag in recipe.tags}, key=str.casefold)
    return render(
        request,
        "recipes/index.html",
        {
            "active_section": "recipes",
            "all_recipes": CATALOG,
            "all_tags": all_tags,
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


def _can_refresh(category: str, shown_ids: set[int]) -> bool:
    """Whether some other CATALOG recipe in `category` isn't already in `shown_ids`.

    Used both to decide whether a planner result's refresh link starts enabled, and to check
    that a refresh request still has somewhere to swap to.
    """
    same_category = [recipe for recipe in CATALOG if recipe.category == category]
    shown_in_category = sum(1 for recipe in same_category if recipe.id in shown_ids)
    return len(same_category) > shown_in_category


def _parse_recipe_ids(raw: str) -> list[int]:
    """Parse a comma-separated list of recipe IDs, in order, dropping duplicates and anything
    unrecognised. Order is preserved so a refresh only changes the one recipe it swaps, rather
    than reshuffling the position of every other recipe already in the plan.
    """
    return list(dict.fromkeys(int(token) for token in raw.split(",") if token.strip().isdigit()))


def _group_plan(recipes: list[RecipeData]) -> list[tuple[str, list[RecipeData], bool]]:
    """Group `recipes` by category (alphabetically), alongside whether each category has another
    CATALOG recipe left to refresh into. Shared by the initial planner search and by
    `refresh_recipe`, so a plan looks and behaves identically how ever it was assembled.
    """
    grouped: dict[str, list[RecipeData]] = {}
    for recipe in recipes:
        grouped.setdefault(recipe.category, []).append(recipe)
    return [
        (category, category_recipes, _can_refresh(category, {r.id for r in category_recipes}))
        for category, category_recipes in sorted(
            grouped.items(), key=lambda item: item[0].casefold()
        )
    ]


def _render_plan_results(request: HttpRequest, plan_recipes: list[RecipeData]) -> HttpResponse:
    """Render the meal-plan results page for exactly `plan_recipes`."""
    return render(
        request,
        "recipes/search_results.html",
        {
            "active_section": "planner",
            "is_tag": False,
            "groups": _group_plan(plan_recipes),
            "recipe_count_total": len(plan_recipes),
            "shared_ingredients": build_shared_shopping_list(plan_recipes),
            "plan_ids": ",".join(str(recipe.id) for recipe in plan_recipes),
        },
    )


STATUS_FILTERS = {
    "draft": ("Draft", lambda recipe: not recipe.is_final),
    "favourite": ("Favourite", lambda recipe: recipe.is_favourite),
}


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
                "eyebrow": "Tag",
                "recipes": recipes,
                "search_term": tag,
                "shared_ingredients": build_shared_shopping_list(recipes),
            },
        )

    status = request.GET.get("status", "").strip().casefold()
    if status in STATUS_FILTERS:
        label, matches_status = STATUS_FILTERS[status]
        recipes = [recipe for recipe in CATALOG if matches_status(recipe)]
        return render(
            request,
            "recipes/search_results.html",
            {
                "active_section": "recipes",
                "is_tag": True,
                "eyebrow": "Status",
                "recipes": recipes,
                "search_term": label,
                "shared_ingredients": build_shared_shopping_list(recipes),
            },
        )

    if not form.is_valid():
        return render(
            request,
            "recipes/planner.html",
            {"active_section": "planner", "form": form},
            status=400,
        )

    all_planned_recipes: list[RecipeData] = []
    for category, count in form.category_counts():
        candidates = [recipe for recipe in CATALOG if recipe.category == category]
        recipes = random.sample(candidates, min(count, len(candidates)))
        all_planned_recipes.extend(recipes)

    return _render_plan_results(request, all_planned_recipes)


@require_safe
def refresh_recipe(request: HttpRequest) -> HttpResponse:
    """Swap one planner result for a different recipe from the same category.

    Backs the refresh ("re-roll") link shown on each meal-plan result: `recipe_id` is the result
    being replaced and `plan` is every recipe ID currently shown anywhere in the plan (so the
    replacement can't duplicate another result already on the page). The replacement is drawn
    from exactly the same pool the original planner search used - every CATALOG recipe in that
    category - so it's exactly as if that recipe had been picked the first time round, and the
    rest of the plan (and its shared shopping list) is simply re-rendered around it. If nothing
    is left to swap to, the plan is re-rendered unchanged.
    """
    raw_recipe_id = request.GET.get("recipe_id", "")
    if not raw_recipe_id.isdigit():
        return HttpResponseBadRequest("recipe_id must be a positive integer.")
    recipe_id = int(raw_recipe_id)

    catalog_by_id = {recipe.id: recipe for recipe in CATALOG}
    recipe = catalog_by_id.get(recipe_id)
    if recipe is None:
        raise Http404

    plan_ids = _parse_recipe_ids(request.GET.get("plan", ""))
    if recipe_id not in plan_ids:
        return HttpResponseBadRequest("recipe_id must be one of the recipes in plan.")

    plan_recipes = [catalog_by_id[pid] for pid in plan_ids if pid in catalog_by_id]
    candidates = [
        candidate
        for candidate in CATALOG
        if candidate.category == recipe.category and candidate.id not in plan_ids
    ]
    if candidates:
        replacement = random.choice(candidates)
        index = next(i for i, r in enumerate(plan_recipes) if r.id == recipe_id)
        plan_recipes[index] = replacement

    return _render_plan_results(request, plan_recipes)


def not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    _ = exception
    return render(request, "404.html", status=404)
