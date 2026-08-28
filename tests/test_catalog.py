import json

import pytest
from django.conf import settings

from recipes.catalog import CatalogError, load_catalog

VALID_RECIPE = {
    "id": 1,
    "title": "Recipe",
    "ingredients": ["Ingredient"],
    "instructions": ["Step"],
    "category": "Category",
    "published_on": "2025-01-01",
    "last_updated_on": "2025-01-01",
    "is_final": True,
    "tags": [],
    "image_urls": [],
}


def test_checked_in_catalog_is_valid():
    catalog = load_catalog(settings.RECIPE_CATALOG_PATH)

    assert catalog
    assert len({recipe.id for recipe in catalog}) == len(catalog)
    assert len({recipe.slug for recipe in catalog}) == len(catalog)


@pytest.mark.parametrize(
    ("document", "message"),
    [
        ({"schema_version": 2, "recipes": []}, "schema_version"),
        ({"schema_version": 1, "recipes": "invalid"}, "non-empty list"),
        ({"schema_version": 1, "recipes": []}, "non-empty list"),
        ({"schema_version": 1, "recipes": ["invalid"]}, "must be an object"),
        ({"schema_version": 1, "recipes": [{**VALID_RECIPE, "extra": True}]}, "exactly"),
        (
                {
                    "schema_version": 1,
                    "recipes": [
                        {
                            "id": 1,
                            "title": "Recipe",
                            "ingredients": [],
                            "instructions": ["Step"],
                            "category": "Category",
                            "published_on": "2025-01-01",
                            "last_updated_on": "2025-01-01",
                            "is_final": True,
                            "tags": [],
                            "image_urls": [],
                        }
                    ],
                },
                "ingredients",
        ),
    ],
)
def test_invalid_catalog_is_rejected(tmp_path, document, message):
    path = tmp_path / "recipes.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(CatalogError, match=message):
        load_catalog(path)


def test_duplicate_ids_are_rejected(tmp_path):
    path = tmp_path / "recipes.json"
    path.write_text(
        json.dumps({"schema_version": 1, "recipes": [VALID_RECIPE, VALID_RECIPE]}),
        encoding="utf-8",
    )

    with pytest.raises(CatalogError, match="IDs must be unique"):
        load_catalog(path)


def test_missing_and_malformed_catalogs_are_rejected(tmp_path):
    missing = tmp_path / "missing.json"
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{invalid", encoding="utf-8")

    with pytest.raises(CatalogError, match="not found"):
        load_catalog(missing)
    with pytest.raises(CatalogError, match="not valid JSON"):
        load_catalog(malformed)


def test_duplicate_slugs_and_unapproved_image_hosts_are_rejected(tmp_path):
    recipe = {**VALID_RECIPE, "title": "Duplicate Title"}
    path = tmp_path / "recipes.json"
    _document = {"schema_version": 1, "recipes": [recipe, {**recipe, "id": 2}]}
    path.write_text(json.dumps(_document), encoding="utf-8")

    with pytest.raises(CatalogError, match="title slugs must be unique"):
        load_catalog(path)

    recipe["image_urls"] = ["https://example.com/image.jpg"]
    path.write_text(
        json.dumps({"schema_version": 1, "recipes": [recipe]}),
        encoding="utf-8",
    )
    with pytest.raises(CatalogError, match=r"res\.cloudinary\.com"):
        load_catalog(path)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"id": True}, "positive integer"),
        ({"title": ""}, "non-empty string"),
        ({"title": "x" * 161}, "at most 160"),
        ({"title": "!!!"}, "URL-safe slug"),
        ({"published_on": "20250101"}, "YYYY-MM-DD"),
        ({"published_on": "2025-99-99"}, "valid date"),
        ({"last_updated_on": "20250101"}, "YYYY-MM-DD"),
        ({"last_updated_on": "2025-99-99"}, "valid date"),
        ({"last_updated_on": "2024-12-31"}, "must not be before published_on"),
        ({"is_final": "yes"}, "true or false"),
        ({"image_urls": "invalid"}, "must be a list"),
        ({"image_urls": [""]}, "non-empty string"),
        ({"category": "x" * 41}, "at most 40"),
        ({"tags": [1]}, "non-empty string"),
    ],
)
def test_invalid_recipe_fields_are_rejected(tmp_path, changes, message):
    path = tmp_path / "recipes.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "recipes": [{**VALID_RECIPE, **changes}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CatalogError, match=message):
        load_catalog(path)


def test_duplicate_json_fields_and_unknown_catalog_fields_are_rejected(tmp_path):
    path = tmp_path / "recipes.json"
    path.write_text(
        '{"schema_version": 1, "schema_version": 1, "recipes": []}',
        encoding="utf-8",
    )
    with pytest.raises(CatalogError, match="Duplicate JSON field"):
        load_catalog(path)

    path.write_text(
        json.dumps({"schema_version": 1, "recipes": [VALID_RECIPE], "extra": True}),
        encoding="utf-8",
    )
    with pytest.raises(CatalogError, match="only schema_version and recipes"):
        load_catalog(path)
