import pytest
from datetime import date
from django.urls import reverse


def test_index_groups_recipes_and_searches_by_title(client, recipe_factory):
    matching = recipe_factory(title="Matching Recipe", category="DINNER")
    recipe_factory(title="Different Dish", category="SNACKS")

    response = client.get(reverse("recipes:index"))
    assert response.status_code == 200
    assert response.context["categories"][0][0] == "DINNER"
    assert response.context["active_section"] == "recipes"
    content = response.content.decode()
    assert 'aria-current="page">Recipes' in content
    assert content.count("data-category-toggle checked") == 2
    assert 'data-category="DINNER"' in content
    assert 'data-category="SNACKS"' in content
    assert "category-filter.js" in content
    assert content.count("data-url=") == 2
    assert "search-autocomplete.js" in content

    response = client.get(reverse("recipes:index"), {"q": "matching"})
    assert response.status_code == 302
    assert response.url == matching.get_absolute_url()


def test_empty_search_result_is_helpful(client, recipe_factory):
    recipe_factory()

    response = client.get(reverse("recipes:index"), {"q": "absent"})

    assert response.status_code == 200
    assert "No matching recipes" in response.content.decode()


def test_search_is_trimmed_case_insensitive_and_keeps_multiple_results(client, recipe_factory):
    first = recipe_factory(title="Green Curry", category="DINNER")
    second = recipe_factory(title="Green Soup", category="LUNCH")
    recipe_factory(title="Red Curry", category="DINNER")

    response = client.get(reverse("recipes:index"), {"q": "  gReEn  "})

    assert response.status_code == 200
    assert response.context["search_term"] == "gReEn"
    visible_titles = [
        recipe.title for _, recipes in response.context["categories"] for recipe in recipes
    ]
    assert visible_titles == [first.title, second.title]
    assert {recipe.title for recipe in response.context["all_recipes"]} == {
        "Green Curry",
        "Green Soup",
        "Red Curry",
    }


def test_index_exposes_time_data_attributes_and_slider_controls(client, recipe_factory):
    recipe_factory(
        title="Quick Snack",
        category="SNACKS",
        total_time_minutes=15,
        active_time_minutes=10,
    )

    response = client.get(reverse("recipes:index"))

    assert response.status_code == 200
    content = response.content.decode()
    assert 'data-recipe-item' in content
    assert 'data-total-minutes="15"' in content
    assert 'data-active-minutes="10"' in content
    assert 'data-time-controls' in content
    assert 'data-total-time-slider' in content
    assert 'data-active-time-slider' in content
    assert 'data-time-empty' in content
    assert "time-badge" not in content
    assert 'data-filter-drawer' in content
    assert "<details" in content
    assert '<details class="filter-drawer" data-filter-drawer open' not in content


def test_index_exposes_status_filter_controls_linking_to_dedicated_pages(client, recipe_factory):
    recipe_factory(title="Draft Dish", is_final=False)

    response = client.get(reverse("recipes:index"))

    assert response.status_code == 200
    content = response.content.decode()
    assert 'data-status-controls' in content
    assert '<legend>Show draft &amp; favourite recipes</legend>' in content
    assert 'data-status-toggle="draft" checked' in content
    assert 'data-status-toggle="favourite" checked' in content
    assert 'href="/search-results/?status=draft"' in content
    assert 'href="/search-results/?status=favourite"' in content
    assert 'aria-label="View all draft recipes"' in content
    assert 'aria-label="View all favourite recipes"' in content


def test_index_marks_draft_and_favourite_recipes_with_badges_and_data_attributes(
    client, recipe_factory
):
    favourite = recipe_factory(title="Amber Favourite Dish", is_final=True, is_favourite=True)
    draft = recipe_factory(title="Brown Draft Dish", is_final=False, is_favourite=False)
    plain = recipe_factory(title="Cyan Plain Dish", is_final=True, is_favourite=False)

    response = client.get(reverse("recipes:index"))
    content = response.content.decode()

    assert response.status_code == 200
    assert content.count('data-is-draft="true"') == 1
    assert content.count('data-is-favourite="true"') == 1
    assert content.count('class="draft"') == 1
    assert content.count('class="favourite"') == 1

    def item_html(recipe):
        anchor = content.index(f'href="{recipe.get_absolute_url()}"')
        start = content.rindex("<li", 0, anchor)
        end = content.index("</li>", anchor)
        return content[start:end]

    assert 'class="favourite"' in item_html(favourite)
    assert 'class="draft"' not in item_html(favourite)
    assert 'class="draft"' in item_html(draft)
    assert 'class="favourite"' not in item_html(draft)
    assert 'class="draft"' not in item_html(plain)
    assert 'class="favourite"' not in item_html(plain)


def test_index_exposes_tag_filter_controls_linking_to_dedicated_pages(client, recipe_factory):
    recipe_factory(title="Curry", category="MAINS", tags=["Spicy", "Vegetarian"])
    recipe_factory(title="Toast", category="SNACKS", tags=["Vegetarian"])
    recipe_factory(title="Plain Bread", category="SNACKS", tags=[])

    response = client.get(reverse("recipes:index"))

    assert response.status_code == 200
    assert response.context["all_tags"] == ["Spicy", "Vegetarian"]
    content = response.content.decode()
    assert 'data-tag-controls' in content
    # Every tag must be enabled by default.
    assert content.count("data-tag-toggle checked") == 2
    assert 'data-tag-status' in content
    assert 'data-tags="Spicy,Vegetarian"' in content
    assert 'data-tags="Vegetarian"' in content
    assert 'data-tags=""' in content
    # Each tag is also an enumerated link to its dedicated single-tag page.
    assert response.context["all_tags"], "expected at least one tag"
    for tag in response.context["all_tags"]:
        assert f'href="/search-results/?tag={tag}"' in content
        assert f'aria-label="View all {tag} recipes"' in content
    assert '<button type="button" class="tag-clear-button" data-tag-clear>Clear all</button>' in content


def test_index_omits_tag_filters_when_no_recipes_have_tags(client, recipe_factory):
    recipe_factory(tags=[])

    response = client.get(reverse("recipes:index"))

    assert response.status_code == 200
    assert response.context["all_tags"] == []
    assert 'data-tag-controls' not in response.content.decode()


def test_index_does_not_render_time_filter_form_fields(client, recipe_factory):
    recipe_factory()

    response = client.get(reverse("recipes:index"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "max_total_time" not in content
    assert "max_active_time" not in content


def test_detail_renders_recipe_information_safely(client, recipe_factory):
    recipe = recipe_factory(
        title='Safe </script><script>alert("x")</script>',
        slug="safe-recipe",
        ingredients=["One", "Two"],
        instructions=["First", "Second"],
        tags=["Zebra", "Alpha"],
        image_urls=["https://example.com/image.jpg"],
        is_final=False,
    )

    response = client.get(recipe.get_absolute_url())
    content = response.content.decode()

    assert response.status_code == 200
    assert "This recipe is still under development." in content
    assert content.index("Alpha") < content.index("Zebra")
    assert "&lt;/script&gt;&lt;script&gt;" in content
    assert 'loading="lazy"' in content
    assert 'referrerpolicy="no-referrer"' in content


def test_detail_shows_favourite_indicator_when_recipe_is_favourite(client, recipe_factory):
    recipe = recipe_factory(is_favourite=True)

    response = client.get(recipe.get_absolute_url())
    content = response.content.decode()

    assert response.status_code == 200
    assert 'class="favourite favourite-detail"' in content
    assert 'aria-label="Favourite recipe"' in content


def test_detail_hides_favourite_indicator_when_recipe_is_not_favourite(client, recipe_factory):
    recipe = recipe_factory(is_favourite=False)

    response = client.get(recipe.get_absolute_url())
    content = response.content.decode()

    assert response.status_code == 200
    assert 'class="favourite favourite-detail"' not in content


def test_detail_renders_ingredient_checklist_with_export_names(client, recipe_factory):
    recipe = recipe_factory(ingredients=["600ml Double Cream", "6 Eggs", "Salt and Pepper (To Taste)"])

    response = client.get(recipe.get_absolute_url())
    content = response.content.decode()

    assert response.status_code == 200
    # Every ingredient is selected by default and paired with its quantity-free name.
    assert content.count("data-ingredient-toggle") == 3
    assert content.count('data-ingredient-toggle data-ingredient-name="') == 3
    assert 'data-ingredient-name="Double Cream" checked' in content
    assert 'data-ingredient-name="Eggs" checked' in content
    assert 'data-ingredient-name="Salt and Pepper (To Taste)" checked' in content
    assert "600ml Double Cream" in content
    assert "data-ingredient-clear" in content
    assert "data-ingredient-copy" in content
    assert "data-ingredient-status" in content
    assert "ingredient-export.js" in content


def test_detail_renders_method_steps_as_an_unchecked_checklist(client, recipe_factory):
    recipe = recipe_factory(instructions=["Preheat the oven.", "Mix the batter.", "Bake for 20 minutes."])

    response = client.get(recipe.get_absolute_url())
    content = response.content.decode()

    assert response.status_code == 200
    # Every step renders as a checkbox that starts unchecked, ready to be crossed off.
    assert content.count("data-method-step-toggle") == 3
    assert content.count("data-method-step-toggle checked") == 0
    assert "Preheat the oven." in content
    assert "Mix the batter." in content
    assert "Bake for 20 minutes." in content
    assert "data-method-status" in content
    assert 'data-method-reset hidden' in content
    assert "method-progress.js" in content


def test_detail_renders_photo_lightbox_when_recipe_has_images(client, recipe_factory):
    recipe = recipe_factory(
        image_urls=[
            "https://example.com/one.jpg",
            "https://example.com/two.jpg",
        ],
    )

    response = client.get(recipe.get_absolute_url())
    content = response.content.decode()

    assert response.status_code == 200
    assert content.count("data-gallery-trigger") == 2
    assert 'data-gallery-index="0"' in content
    assert 'data-gallery-index="1"' in content
    assert 'data-lightbox' in content
    assert 'data-lightbox-prev' in content
    assert 'data-lightbox-next' in content
    assert 'data-lightbox-close' in content
    assert 'role="dialog" aria-modal="true"' in content
    assert "gallery-lightbox.js" in content
    # Photos should no longer link directly out to the raw image URL.
    assert '<a href="https://example.com/one.jpg"' not in content


def test_detail_omits_gallery_and_script_when_recipe_has_no_images(client, recipe_factory):
    recipe = recipe_factory(image_urls=[])

    response = client.get(recipe.get_absolute_url())
    content = response.content.decode()

    assert response.status_code == 200
    assert "data-gallery" not in content
    assert "gallery-lightbox.js" not in content


def test_detail_hides_last_updated_when_same_as_published(client, recipe_factory):
    recipe = recipe_factory(
        published_on=date(2025, 1, 1),
        last_updated_on=date(2025, 1, 1),
    )

    response = client.get(recipe.get_absolute_url())
    content = response.content.decode()

    assert "Published 1 Jan 2025" in content
    assert "Updated" not in content


def test_detail_shows_last_updated_when_different_from_published(client, recipe_factory):
    recipe = recipe_factory(
        published_on=date(2025, 1, 1),
        last_updated_on=date(2025, 3, 15),
    )

    response = client.get(recipe.get_absolute_url())
    content = response.content.decode()

    assert "Published 1 Jan 2025" in content
    assert "Updated 15 Mar 2025" in content
    assert content.index("Published 1 Jan 2025") < content.index("Updated 15 Mar 2025")


def test_detail_returns_not_found_for_unknown_recipe_or_wrong_slug(client, recipe_factory):
    recipe = recipe_factory()

    assert client.get("/999/unknown/").status_code == 404
    assert client.get(f"/{recipe.id}/wrong-slug/").status_code == 404


def test_planner_returns_unique_recipes_from_selected_category(client, recipe_factory):
    first = recipe_factory(category="DINNER")
    second = recipe_factory(category="DINNER")
    recipe_factory(category="SNACK")

    response = client.get(
        reverse("recipes:search-results"),
        {"count_dinner": 2},
    )

    assert response.status_code == 200
    assert response.context["groups"][0][0] == "DINNER"
    assert set(response.context["groups"][0][1]) == {first, second}
    assert response.context["recipe_count_total"] == 2
    assert response.context["is_tag"] is False
    assert "Meal plan" in response.content.decode()


def test_planner_can_combine_multiple_category_counts(client, recipe_factory):
    main1 = recipe_factory(category="MAINS")
    main2 = recipe_factory(category="MAINS")
    main3 = recipe_factory(category="MAINS")
    light1 = recipe_factory(category="LIGHT DISHES")

    response = client.get(
        reverse("recipes:search-results"),
        {"count_mains": 2, "count_light_dishes": 1},
    )

    assert response.status_code == 200
    groups = dict(response.context["groups"])
    assert len(groups["MAINS"]) == 2
    assert set(groups["MAINS"]) <= {main1, main2, main3}
    assert groups["LIGHT DISHES"] == [light1]
    assert response.context["recipe_count_total"] == 3
    content = response.content.decode()
    assert "Mains" in content
    assert "Light Dishes" in content


def test_planner_results_show_deduplicated_shared_shopping_list(client, recipe_factory):
    recipe_factory(title="Omelette", category="MAINS", ingredients=["6 Eggs", "1 Onion"])
    recipe_factory(title="Pancakes", category="MAINS", ingredients=["3 Eggs", "240g Caster Sugar"])

    response = client.get(reverse("recipes:search-results"), {"count_mains": 2})

    assert response.status_code == 200
    shared = response.context["shared_ingredients"]
    names = [item.export_name for item in shared]
    assert names == ["Caster Sugar", "Eggs", "Onion"]
    eggs = next(item for item in shared if item.export_name == "Eggs")
    assert set(eggs.recipe_titles) == {"Omelette", "Pancakes"}

    content = response.content.decode()
    assert "Shared shopping list" in content
    assert content.count('data-ingredient-name="Eggs"') == 1
    assert "Copy shopping list" in content
    assert "ingredient-export.js" in content


def test_planner_results_link_back_to_the_planner_with_the_requested_counts(
    client, recipe_factory
):
    recipe_factory(category="MAINS")
    recipe_factory(category="MAINS")
    recipe_factory(category="LIGHT DISHES")
    recipe_factory(category="SNACKS")

    response = client.get(
        reverse("recipes:search-results"),
        {"count_mains": 2, "count_light_dishes": 1, "count_snacks": 0},
    )

    assert response.status_code == 200
    planner_url = f"{reverse('recipes:planner')}?count_light_dishes=1&count_mains=2"
    assert response.context["planner_url"] == planner_url
    assert f'href="{planner_url.replace("&", "&amp;")}"' in response.content.decode()


def test_planner_is_prefilled_with_valid_counts_and_ignores_invalid_ones(client, recipe_factory):
    for _ in range(3):
        recipe_factory(category="DINNER")
    recipe_factory(category="LUNCH")
    recipe_factory(category="SNACKS")

    response = client.get(
        reverse("recipes:planner"),
        {"count_dinner": 2, "count_lunch": 5, "count_snacks": "lots"},
    )

    assert response.status_code == 200
    form = response.context["form"]
    assert not form.is_bound
    assert form.initial == {"count_dinner": 2}
    content = response.content.decode()
    assert 'name="count_dinner" value="2"' in content
    assert 'name="count_lunch" value="0"' in content
    assert 'name="count_snacks" value="0"' in content
    assert "errorlist" not in content

    all_zero = client.get(reverse("recipes:planner"), {"count_dinner": 0})
    assert all_zero.context["form"].initial == {}
    assert "errorlist" not in all_zero.content.decode()


def test_planner_results_disable_swaps_for_categories_without_alternatives(
    client, recipe_factory
):
    mains = [recipe_factory(category="MAINS") for _ in range(3)]
    light = recipe_factory(category="LIGHT DISHES")

    response = client.get(
        reverse("recipes:search-results"), {"count_mains": 2, "count_light_dishes": 1}
    )

    assert response.status_code == 200
    assert response.context["swappable_categories"] == {"MAINS"}
    content = response.content.decode()
    assert f'data-plan-swap-url="{reverse("recipes:plan-swap")}"' in content
    assert 'data-plan-group="MAINS"' in content
    assert content.count("data-plan-slot") == 3
    assert content.count("data-plan-swap ") == 3
    planned_mains = dict(response.context["groups"])["MAINS"]
    for recipe in planned_mains:
        assert (
            f'aria-label="Swap {recipe.title} for another recipe" title="Swap for another recipe"'
            in content
        )
    assert set(planned_mains) < set(mains)
    # Every Light Dishes recipe is already planned, so its button is shown but disabled, with a
    # tooltip explaining why.
    assert content.count('aria-disabled="true"') == 1
    assert (
        f'aria-label="Swap {light.title} for another recipe" aria-disabled="true" '
        'title="No other Light Dishes recipes available"'
    ) in content
    assert "plan-swap.js" in content


def test_planner_results_disable_every_swap_and_omit_script_when_nothing_can_be_swapped(
    client, recipe_factory
):
    recipe_factory(category="MAINS")
    recipe_factory(category="MAINS")

    response = client.get(reverse("recipes:search-results"), {"count_mains": 2})

    assert response.status_code == 200
    assert response.context["swappable_categories"] == set()
    content = response.content.decode()
    assert content.count("data-plan-swap ") == 2
    assert content.count('aria-disabled="true"') == 2
    assert content.count('title="No other Mains recipes available"') == 2
    assert "plan-swap.js" not in content


def test_plan_swap_replaces_recipe_with_an_unplanned_one_from_the_same_category(
    client, recipe_factory
):
    outgoing = recipe_factory(title="Omelette", category="MAINS", ingredients=["6 Eggs"])
    kept = recipe_factory(title="Pancakes", category="MAINS", ingredients=["3 Eggs", "1 Lemon"])
    incoming = recipe_factory(title="Risotto", category="MAINS", ingredients=["300g Rice"])
    light = recipe_factory(title="Salad", category="LIGHT DISHES", ingredients=["1 Lettuce"])
    recipe_factory(title="Soup", category="LIGHT DISHES", ingredients=["1 Leek"])

    response = client.get(
        reverse("recipes:plan-swap"),
        {"plan": [outgoing.id, kept.id, light.id], "swap": outgoing.id},
    )

    assert response.status_code == 200
    assert response.context["recipe"] == incoming
    assert response.context["swappable_categories"] == {"MAINS"}
    shared = response.context["shared_ingredients"]
    assert [item.export_name for item in shared] == ["Eggs", "Lemon", "Lettuce", "Rice"]
    eggs = next(item for item in shared if item.export_name == "Eggs")
    assert eggs.recipe_titles == ("Pancakes",)

    content = response.content.decode()
    assert f'data-recipe-id="{incoming.id}"' in content
    assert f'href="{incoming.get_absolute_url()}"' in content
    assert f'aria-label="Swap {incoming.title} for another recipe"' in content
    assert "Shared shopping list" in content
    assert 'data-ingredient-name="Rice"' in content
    assert "<html" not in content


def test_plan_swap_offers_rejected_recipes_again_only_once_every_alternative_is_rejected(
    client, recipe_factory, monkeypatch
):
    current = recipe_factory(category="MAINS")
    rejected = [recipe_factory(category="MAINS") for _ in range(2)]
    unseen = recipe_factory(category="MAINS")
    offered_candidates = []

    def choose_first(candidates):
        offered_candidates.append(list(candidates))
        return candidates[0]

    monkeypatch.setattr("recipes.views.random.choice", choose_first)

    response = client.get(
        reverse("recipes:plan-swap"),
        {"plan": [current.id], "swap": current.id, "rejected": [r.id for r in rejected]},
    )
    assert response.status_code == 200
    assert response.context["recipe"] == unseen

    response = client.get(
        reverse("recipes:plan-swap"),
        {
            "plan": [current.id],
            "swap": current.id,
            "rejected": [recipe.id for recipe in [*rejected, unseen]],
        },
    )
    assert response.status_code == 200
    assert offered_candidates == [[unseen], [*rejected, unseen]]


def test_plan_swap_is_a_conflict_when_every_recipe_in_the_category_is_planned(
    client, recipe_factory
):
    first = recipe_factory(category="MAINS")
    second = recipe_factory(category="MAINS")
    recipe_factory(category="LIGHT DISHES")

    response = client.get(
        reverse("recipes:plan-swap"), {"plan": [first.id, second.id], "swap": first.id}
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "query",
    [
        {},
        {"swap": 1},
        {"plan": [1, 2]},
        {"plan": [1, 2], "swap": 3},
        {"plan": [1, 1], "swap": 1},
        {"plan": [1, 999], "swap": 1},
        {"plan": ["one"], "swap": "one"},
        {"plan": [1], "swap": 1, "rejected": [999]},
    ],
)
def test_plan_swap_rejects_invalid_requests(client, recipe_factory, query):
    for _ in range(3):
        recipe_factory(category="MAINS")

    response = client.get(reverse("recipes:plan-swap"), query)

    assert response.status_code == 400


def test_tag_selection_returns_matching_recipes(client, recipe_factory):
    tagged = recipe_factory(tags=["Vegetarian"])
    recipe_factory(tags=["Other"])

    response = client.get(reverse("recipes:search-results"), {"tag": "Vegetarian"})

    assert response.status_code == 200
    assert response.context["recipes"] == [tagged]
    assert response.context["is_tag"] is True
    assert "All recipes" in response.content.decode()


def test_tag_selection_shows_shared_shopping_list_for_matching_recipes(client, recipe_factory):
    recipe_factory(title="Curry", tags=["Vegetarian"], ingredients=["2 Cloves Garlic"])
    recipe_factory(title="Stir Fry", tags=["Vegetarian"], ingredients=["3 Garlic Cloves"])
    recipe_factory(title="Steak", tags=["Other"], ingredients=["1 Steak"])

    response = client.get(reverse("recipes:search-results"), {"tag": "Vegetarian"})

    assert response.status_code == 200
    names = {item.export_name for item in response.context["shared_ingredients"]}
    assert names == {"Garlic", "Garlic Cloves"}
    content = response.content.decode()
    assert "Shared shopping list" in content
    assert "Steak" not in content.split("Shared shopping list")[1].split("</details>")[0]


def test_search_results_with_no_matching_recipes_hides_shared_shopping_list(
    client, recipe_factory
):
    recipe_factory(tags=["Other"])

    response = client.get(reverse("recipes:search-results"), {"tag": "Nonexistent"})

    assert response.status_code == 200
    assert response.context["shared_ingredients"] == ()
    content = response.content.decode()
    assert "Shared shopping list" not in content
    assert "ingredient-export.js" not in content


def test_status_draft_filter_returns_only_draft_recipes(client, recipe_factory):
    draft = recipe_factory(title="Draft Recipe", is_final=False)
    recipe_factory(title="Finished Recipe", is_final=True)

    response = client.get(reverse("recipes:search-results"), {"status": "draft"})

    assert response.status_code == 200
    assert response.context["recipes"] == [draft]
    assert response.context["is_tag"] is True
    content = response.content.decode()
    assert "<p class=\"eyebrow\">Status</p>" in content
    assert "<h1>Draft</h1>" in content


def test_status_favourite_filter_returns_only_favourite_recipes(client, recipe_factory):
    favourite = recipe_factory(title="Favourite Recipe", is_favourite=True)
    recipe_factory(title="Plain Recipe", is_favourite=False)

    response = client.get(reverse("recipes:search-results"), {"status": "favourite"})

    assert response.status_code == 200
    assert response.context["recipes"] == [favourite]
    assert response.context["is_tag"] is True
    content = response.content.decode()
    assert "<h1>Favourite</h1>" in content


def test_status_filter_is_case_insensitive_and_ignores_unknown_values(client, recipe_factory):
    draft = recipe_factory(title="Draft Recipe", is_final=False)

    response = client.get(reverse("recipes:search-results"), {"status": "DRAFT"})
    assert response.context["recipes"] == [draft]

    unknown_response = client.get(
        reverse("recipes:search-results"), {"count_mains": 1, "status": "unknown"}
    )
    assert unknown_response.status_code in (200, 400)
    assert unknown_response.context.get("is_tag") is not True


def test_invalid_planner_input_returns_bad_request(client, recipe_factory):
    recipe_factory(category="DINNER")

    response = client.get(
        reverse("recipes:search-results"),
        {"count_dinner": 0},
    )

    assert response.status_code == 400
    assert "Choose at least one recipe" in response.content.decode()

    negative_count = client.get(
        reverse("recipes:search-results"),
        {"count_dinner": -1},
    )
    assert negative_count.status_code == 400
    assert "Ensure this value is greater than or equal to 0" in negative_count.content.decode()

    more_than_available = client.get(
        reverse("recipes:search-results"),
        {"count_dinner": 2},
    )
    assert more_than_available.status_code == 400
    assert (
        "Ensure this value is less than or equal to 1" in more_than_available.content.decode()
    )


def test_planner_caps_each_category_count_at_its_number_of_recipes(client, recipe_factory):
    for _ in range(3):
        recipe_factory(category="DINNER")
    for _ in range(60):
        recipe_factory(category="MAINS")

    response = client.get(reverse("recipes:planner"))

    form = response.context["form"]
    assert 'max="3"' in str(form["count_dinner"])
    assert 'max="60"' in str(form["count_mains"])
    content = response.content.decode()
    assert str(form["count_dinner"]) in content
    assert str(form["count_mains"]) in content

    assert client.get(reverse("recipes:search-results"), {"count_dinner": 3}).status_code == 200
    assert client.get(reverse("recipes:search-results"), {"count_dinner": 4}).status_code == 400
    every_main = client.get(reverse("recipes:search-results"), {"count_mains": 60})
    assert every_main.status_code == 200
    assert every_main.context["recipe_count_total"] == 60


def test_planner_lists_each_available_category_once(client, recipe_factory):
    recipe_factory(category="DINNER")
    recipe_factory(category="DINNER")
    recipe_factory(category="SNACKS")

    response = client.get(reverse("recipes:planner"))

    assert sorted(response.context["form"].category_fields.values()) == ["DINNER", "SNACKS"]
    content = response.content.decode()
    assert content.count('data-quantity-input') == 2
    assert "Dinner" in content
    assert "Snacks" in content


def test_planner_page(client, recipe_factory):
    recipe_factory()

    planner = client.get(reverse("recipes:planner"))

    assert planner.status_code == 200
    assert planner.context["active_section"] == "planner"


def test_footer_contains_linked_author_and_current_copyright(client):
    content = client.get(reverse("recipes:index")).content.decode()

    assert '<footer class="site-footer">' in content
    assert f"&copy; 2020&ndash;{date.today().year}" in content
    assert '<a href="https://MikeGreen.net/">Mike Green</a>' in content


def test_custom_404_and_security_headers(client):
    response = client.get("/not-a-page/")

    assert response.status_code == 404
    assert "Page not found" in response.content.decode()
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]


def test_unapproved_host_is_rejected(client):
    response = client.get("/", headers={"host": "unapproved.invalid"})

    assert response.status_code == 400


@pytest.mark.parametrize(
    "route_name",
    [
        "recipes:index",
        "recipes:planner",
        "recipes:search-results",
        "recipes:plan-swap",
    ],
)
def test_read_only_pages_reject_post(client, route_name):
    assert client.post(reverse(route_name)).status_code == 405


def test_recipe_detail_rejects_post(client, recipe_factory):
    recipe = recipe_factory()

    assert client.post(recipe.get_absolute_url()).status_code == 405


def test_head_requests_and_security_headers_are_supported(client):
    response = client.head(reverse("recipes:index"))

    assert response.status_code == 200
    assert response.content == b""
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
