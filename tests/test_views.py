from datetime import date

import pytest
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


def test_search_can_be_scoped_to_one_category(client, recipe_factory):
    matching = recipe_factory(title="Shared Curry", category="DINNER")
    recipe_factory(title="Shared Curry", category="LUNCH")
    recipe_factory(title="Different Dish", category="DINNER")

    response = client.get(
        reverse("recipes:index"),
        {"q": "shared", "category": "DINNER"},
    )

    assert response.status_code == 302
    assert response.url == matching.get_absolute_url()

    invalid = client.get(reverse("recipes:index"), {"category": "UNKNOWN"})
    assert invalid.status_code == 400
    assert "Select a valid choice" in invalid.content.decode()


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
        {"category": "DINNER", "recipe_count": 10},
    )

    assert response.status_code == 200
    assert set(response.context["recipes"]) == {first, second}
    assert response.context["is_tag"] is False
    assert "Meal plan" in response.content.decode()


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
        {"category": "DINNER", "recipe_count": 0},
    )

    assert response.status_code == 400
    assert "Ensure this value is greater than or equal to 1" in response.content.decode()

    unknown_category = client.get(
        reverse("recipes:search-results"),
        {"category": "UNKNOWN", "recipe_count": 1},
    )
    assert unknown_category.status_code == 400
    assert "Select a valid choice" in unknown_category.content.decode()


def test_planner_lists_each_available_category_once(client, recipe_factory):
    recipe_factory(category="DINNER")
    recipe_factory(category="DINNER")
    recipe_factory(category="SNACKS")

    response = client.get(reverse("recipes:planner"))

    assert response.context["form"].fields["category"].choices == [
        ("DINNER", "Dinner"),
        ("SNACKS", "Snacks"),
    ]


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
