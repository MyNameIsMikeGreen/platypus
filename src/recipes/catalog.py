import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

CATALOG_FIELDS = {"schema_version", "recipes"}
MAX_CATEGORY_LENGTH = 40
MAX_ID = 2_147_483_647
MAX_TITLE_LENGTH = 160
MAX_TIME_MINUTES = 10_080  # One week; a generous upper bound for a home recipe.
RECIPE_FIELDS = {
    "id",
    "title",
    "ingredients",
    "instructions",
    "category",
    "total_time_minutes",
    "active_time_minutes",
    "published_on",
    "last_updated_on",
    "is_final",
    "tags",
    "image_urls",
}


class CatalogError(ValueError):
    """Raised when the checked-in recipe catalog is invalid."""


@dataclass(frozen=True, slots=True)
class RecipeData:
    id: int
    slug: str
    title: str
    ingredients: tuple[str, ...]
    instructions: tuple[str, ...]
    category: str
    total_time_minutes: int
    active_time_minutes: int
    published_on: date
    last_updated_on: date
    is_final: bool
    tags: tuple[str, ...]
    image_urls: tuple[str, ...]

    def get_absolute_url(self) -> str:
        return reverse("recipes:detail", kwargs={"recipe_id": self.id, "slug": self.slug})

    @property
    def total_time_display(self) -> str:
        return _format_minutes(self.total_time_minutes)

    @property
    def active_time_display(self) -> str:
        return _format_minutes(self.active_time_minutes)


def _format_minutes(total_minutes: int) -> str:
    days, remainder = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hr{'s' if hours != 1 else ''}")
    if minutes or not parts:
        parts.append(f"{minutes} min")
    return " ".join(parts)


def _string(value: object, field: str, recipe_id: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"Recipe {recipe_id}: {field} must be a non-empty string.")
    return value


def _positive_int(value: object, field: str, recipe_id: object, *, max_value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= max_value:
        raise CatalogError(
            f"Recipe {recipe_id}: {field} must be a positive integer of at most {max_value}."
        )
    return value


def _string_list(
    value: object, field: str, recipe_id: object, *, allow_empty: bool
) -> tuple[str, ...]:
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise CatalogError(f"Recipe {recipe_id}: {field} must be {qualifier}.")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise CatalogError(f"Recipe {recipe_id}: every {field} entry must be a non-empty string.")
    return tuple(value)


def _date(value: object, field: str, recipe_id: object) -> date:
    text = _string(value, field, recipe_id)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise CatalogError(f"Recipe {recipe_id}: {field} must use YYYY-MM-DD.")
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise CatalogError(f"Recipe {recipe_id}: {field} must be a valid date.") from error


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise CatalogError(f"Duplicate JSON field: {key}.")
        result[key] = value
    return result


def _parse_recipe(raw: object) -> RecipeData:
    if not isinstance(raw, dict):
        raise CatalogError("Each recipe must be an object.")
    if set(raw) != RECIPE_FIELDS:
        raise CatalogError(
            f"Each recipe must contain exactly these fields: {', '.join(sorted(RECIPE_FIELDS))}."
        )
    recipe_id = raw.get("id")
    if (
        not isinstance(recipe_id, int)
        or isinstance(recipe_id, bool)
        or not 1 <= recipe_id <= MAX_ID
    ):
        raise CatalogError(f"Recipe {recipe_id}: id must be a positive integer.")

    title = _string(raw.get("title"), "title", recipe_id)
    if len(title) > MAX_TITLE_LENGTH:
        raise CatalogError(f"Recipe {recipe_id}: title must be at most 160 characters.")
    generated_slug = slugify(title)
    if not generated_slug or len(generated_slug) > MAX_TITLE_LENGTH:
        raise CatalogError(f"Recipe {recipe_id}: title must produce a URL-safe slug.")

    published_on = _date(raw.get("published_on"), "published_on", recipe_id)
    last_updated_on = _date(raw.get("last_updated_on"), "last_updated_on", recipe_id)
    if last_updated_on < published_on:
        raise CatalogError(f"Recipe {recipe_id}: last_updated_on must not be before published_on.")

    is_final = raw.get("is_final")
    if not isinstance(is_final, bool):
        raise CatalogError(f"Recipe {recipe_id}: is_final must be true or false.")

    image_urls = _string_list(raw.get("image_urls"), "image_urls", recipe_id, allow_empty=True)
    for image_url in image_urls:
        parsed = urlparse(image_url)
        if parsed.scheme != "https" or parsed.netloc != "res.cloudinary.com":
            raise CatalogError(
                f"Recipe {recipe_id}: image URLs must use HTTPS on res.cloudinary.com."
            )

    category = _string(raw.get("category"), "category", recipe_id)
    if len(category) > MAX_CATEGORY_LENGTH:
        raise CatalogError(f"Recipe {recipe_id}: category must be at most 40 characters.")

    total_time_minutes = _positive_int(
        raw.get("total_time_minutes"), "total_time_minutes", recipe_id, max_value=MAX_TIME_MINUTES
    )
    active_time_minutes = _positive_int(
        raw.get("active_time_minutes"),
        "active_time_minutes",
        recipe_id,
        max_value=MAX_TIME_MINUTES,
    )
    if active_time_minutes > total_time_minutes:
        raise CatalogError(
            f"Recipe {recipe_id}: active_time_minutes must not be more than total_time_minutes."
        )

    return RecipeData(
        id=recipe_id,
        slug=generated_slug,
        title=title,
        ingredients=_string_list(
            raw.get("ingredients"), "ingredients", recipe_id, allow_empty=False
        ),
        instructions=_string_list(
            raw.get("instructions"), "instructions", recipe_id, allow_empty=False
        ),
        category=category,
        total_time_minutes=total_time_minutes,
        active_time_minutes=active_time_minutes,
        published_on=published_on,
        last_updated_on=last_updated_on,
        is_final=is_final,
        tags=_string_list(raw.get("tags"), "tags", recipe_id, allow_empty=True),
        image_urls=image_urls,
    )


def load_catalog(path: Path) -> tuple[RecipeData, ...]:
    try:
        document = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
    except FileNotFoundError as error:
        raise CatalogError(f"Recipe catalog not found: {path}") from error
    except json.JSONDecodeError as error:
        raise CatalogError(f"Recipe catalog is not valid JSON: {error}") from error

    if not isinstance(document, dict) or set(document) != CATALOG_FIELDS:
        raise CatalogError("Recipe catalog must contain only schema_version and recipes.")
    if document.get("schema_version") != 1:
        raise CatalogError("Recipe catalog schema_version must be 1.")
    raw_recipes = document.get("recipes")
    if not isinstance(raw_recipes, list) or not raw_recipes:
        raise CatalogError("Recipe catalog recipes must be a non-empty list.")

    recipes = tuple(_parse_recipe(raw) for raw in raw_recipes)
    ids = [recipe.id for recipe in recipes]
    slugs = [recipe.slug for recipe in recipes]
    if len(ids) != len(set(ids)):
        raise CatalogError("Recipe IDs must be unique.")
    if len(slugs) != len(set(slugs)):
        raise CatalogError("Recipe title slugs must be unique.")
    return tuple(sorted(recipes, key=lambda recipe: recipe.title.casefold()))


CATALOG = load_catalog(settings.RECIPE_CATALOG_PATH)
