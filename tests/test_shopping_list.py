from datetime import date

import pytest

from recipes.catalog import RecipeData
from recipes.shopping_list import SharedIngredient, build_shared_shopping_list


def _recipe(recipe_id, title, ingredients):
    return RecipeData(
        id=recipe_id,
        slug=f"recipe-{recipe_id}",
        title=title,
        ingredients=tuple(ingredients),
        instructions=("Do the thing.",),
        category="MAINS",
        total_time_minutes=30,
        active_time_minutes=15,
        published_on=date(2025, 1, 1),
        last_updated_on=date(2025, 1, 1),
        is_final=True,
        is_favourite=False,
        tags=(),
        image_urls=(),
    )


def test_no_recipes_returns_empty_list():
    assert build_shared_shopping_list([]) == ()


def test_single_recipe_lists_each_ingredient_once_with_its_own_title():
    recipe = _recipe(1, "Soup", ["600ml Double Cream", "6 Eggs"])

    result = build_shared_shopping_list([recipe])

    assert result == (
        SharedIngredient(export_name="Double Cream", recipe_titles=("Soup",)),
        SharedIngredient(export_name="Eggs", recipe_titles=("Soup",)),
    )


def test_same_ingredient_across_recipes_is_deduplicated_and_lists_both_titles():
    first = _recipe(1, "Omelette", ["6 Eggs", "Salt and Pepper (To Taste)"])
    second = _recipe(2, "Pancakes", ["3 Eggs", "240g Caster Sugar"])

    result = build_shared_shopping_list([first, second])

    by_name = {item.export_name: item for item in result}
    assert by_name["Eggs"].recipe_titles == ("Omelette", "Pancakes")
    assert by_name["Salt and Pepper (To Taste)"].recipe_titles == ("Omelette",)
    assert by_name["Caster Sugar"].recipe_titles == ("Pancakes",)


def test_matching_is_case_insensitive_and_keeps_first_seen_casing():
    first = _recipe(1, "First", ["6 eggs"])
    second = _recipe(2, "Second", ["3 EGGS"])

    result = build_shared_shopping_list([first, second])

    assert result == (SharedIngredient(export_name="eggs", recipe_titles=("First", "Second")),)


def test_a_recipe_listing_the_same_ingredient_twice_only_lists_its_title_once():
    recipe = _recipe(1, "Stew", ["1 Onion", "1/2 Onion"])

    result = build_shared_shopping_list([recipe])

    assert result == (SharedIngredient(export_name="Onion", recipe_titles=("Stew",)),)


def test_results_are_sorted_alphabetically_by_export_name():
    recipe = _recipe(1, "Mix", ["6 Eggs", "1 Onion", "240g Caster Sugar"])

    result = build_shared_shopping_list([recipe])

    assert [item.export_name for item in result] == ["Caster Sugar", "Eggs", "Onion"]


@pytest.mark.parametrize("recipes", [[], iter([])])
def test_accepts_any_iterable_of_recipes(recipes):
    assert build_shared_shopping_list(recipes) == ()
