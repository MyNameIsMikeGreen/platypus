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


def test_index_exposes_tag_filter_controls_all_enabled_by_default(client, recipe_factory):
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


def test_detail_renders_ingredient_export_checkboxes_checked_by_default(client, recipe_factory):
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
        {"count_dinner": 10},
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
        {"count_mains": 2, "count_light_dishes": 5},
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


def test_tag_selection_returns_matching_recipes(client, recipe_factory):
    tagged = recipe_factory(tags=["Vegetarian"])
    recipe_factory(tags=["Other"])

    response = client.get(reverse("recipes:search-results"), {"tag": "Vegetarian"})

    assert response.status_code == 200
    assert response.context["recipes"] == [tagged]
    assert response.context["is_tag"] is True
    assert "All recipes" in response.content.decode()


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

    too_many = client.get(
        reverse("recipes:search-results"),
        {"count_dinner": 51},
    )
    assert too_many.status_code == 400
    assert "Ensure this value is less than or equal to 50" in too_many.content.decode()


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


def test_planner_and_about_pages(client, recipe_factory):
    recipe_factory()

    planner = client.get(reverse("recipes:planner"))
    about = client.get(reverse("recipes:about"))

    assert planner.status_code == 200
    assert about.status_code == 200
    assert planner.context["active_section"] == "planner"
    assert about.context["active_section"] == "about"
    content = about.content.decode()
    assert "terrible chimaera" in content
    assert "https://MikeGreen.net/" in content


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
        "recipes:about",
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
