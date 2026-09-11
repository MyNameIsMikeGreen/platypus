"""Aggregation of ingredients across multiple recipes into one shared shopping list.

Used by the meal-planner results page so a user can copy a single combined shopping list for
every recipe shown, instead of visiting each recipe individually. Ingredients are matched using
their quantity-free export name (see :mod:`recipes.ingredients`) so the same ingredient appearing
in several recipes - regardless of quantity or casing - collapses into a single row.
"""

from typing import Iterable, NamedTuple

from .catalog import RecipeData
from .ingredients import export_name


class SharedIngredient(NamedTuple):
    """A deduplicated ingredient row for the shared shopping list, and which recipes use it."""

    export_name: str
    recipe_titles: tuple[str, ...]


def build_shared_shopping_list(recipes: Iterable[RecipeData]) -> tuple[SharedIngredient, ...]:
    """Combine every ingredient across `recipes` into one alphabetised, deduplicated list.

    Ingredients are grouped by their case-folded export name (quantity-free), keeping the
    casing of the first recipe that used it, and recording every recipe title that includes
    them (so the UI can hint how many recipes need a given ingredient).
    """
    recipe_titles_by_key: dict[str, list[str]] = {}
    display_name_by_key: dict[str, str] = {}
    for recipe in recipes:
        for ingredient in recipe.ingredients:
            name = export_name(ingredient)
            key = name.casefold()
            titles = recipe_titles_by_key.setdefault(key, [])
            if recipe.title not in titles:
                titles.append(recipe.title)
            display_name_by_key.setdefault(key, name)

    return tuple(
        SharedIngredient(export_name=display_name_by_key[key], recipe_titles=tuple(titles))
        for key, titles in sorted(
            recipe_titles_by_key.items(),
            key=lambda item: display_name_by_key[item[0]].casefold(),
        )
    )
