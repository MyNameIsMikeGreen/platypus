from django import forms
from django.utils.text import slugify

from .catalog import CATALOG

MAX_CATEGORY_RECIPE_COUNT = 50


def _categories() -> list[str]:
    return sorted({recipe.category for recipe in CATALOG})


def category_count_field_name(category: str) -> str:
    """The PlannerForm field name used for a category's quantity input."""
    return f"count_{slugify(category).replace('-', '_')}"


class RecipeSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        max_length=160,
        strip=True,
        widget=forms.SearchInput(
            attrs={
                "aria-autocomplete": "list",
                "aria-controls": "recipe-suggestions",
                "aria-expanded": "false",
                "autocomplete": "off",
                "id": "recipe-search",
                "list": "recipe-search-data",
                "placeholder": "Search by title",
                "role": "combobox",
            }
        ),
    )


class PlannerForm(forms.Form):
    """A planner request built from one quantity field per recipe category.

    Rendering the form (`for field in form`) yields one bound field per category, each a
    "how many" count. This lets a single request plan a mix such as 3 mains and 2 light
    dishes, while keeping the classic single-category plan a simple special case where
    every other count is left at zero.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.category_fields: dict[str, str] = {}
        for category in _categories():
            field_name = category_count_field_name(category)
            self.category_fields[field_name] = category
            self.fields[field_name] = forms.IntegerField(
                label=category.title(),
                required=False,
                min_value=0,
                max_value=MAX_CATEGORY_RECIPE_COUNT,
                initial=0,
                widget=forms.NumberInput(
                    attrs={
                        "inputmode": "numeric",
                        "data-quantity-input": "",
                        "aria-label": f"Number of {category.title()} recipes",
                    }
                ),
            )

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        if not any(cleaned_data.get(field) for field in self.category_fields):
            raise forms.ValidationError(
                "Choose at least one recipe by increasing a category count above."
            )
        return cleaned_data

    def category_counts(self) -> list[tuple[str, int]]:
        """Categories with a positive requested count, in category order."""
        return [
            (category, self.cleaned_data[field])
            for field, category in self.category_fields.items()
            if self.cleaned_data.get(field)
        ]
