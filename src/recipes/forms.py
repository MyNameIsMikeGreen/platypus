from collections import Counter
from urllib.parse import urlencode

from django import forms
from django.utils.text import slugify

from .catalog import CATALOG


def _category_recipe_counts() -> dict[str, int]:
    """How many recipes each category has, in category order."""
    return dict(sorted(Counter(recipe.category for recipe in CATALOG).items()))


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
    every other count is left at zero. Each count is capped at the number of recipes the
    category has, since a plan never repeats a recipe.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.category_fields: dict[str, str] = {}
        for category, recipe_count in _category_recipe_counts().items():
            field_name = category_count_field_name(category)
            self.category_fields[field_name] = category
            self.fields[field_name] = forms.IntegerField(
                label=category.title(),
                required=False,
                min_value=0,
                max_value=recipe_count,
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

    @classmethod
    def prefilled(cls, data: object) -> "PlannerForm":
        """An unbound form pre-filled with any valid counts in `data`, such as a previous plan's.

        Unlike binding `data` directly, this never reports errors, so re-opening the planner
        to tweak a previous request shows its counts without complaining about anything invalid.
        """
        previous = cls(data)
        previous.is_valid()
        return cls(
            initial={
                field: previous.cleaned_data[field]
                for field in previous.category_fields
                if previous.cleaned_data.get(field)
            }
        )

    def category_counts(self) -> list[tuple[str, int]]:
        """Categories with a positive requested count, in category order."""
        return [
            (category, self.cleaned_data[field])
            for field, category in self.category_fields.items()
            if self.cleaned_data.get(field)
        ]

    def counts_query(self) -> str:
        """The positive requested counts as a query string, for re-opening the planner with."""
        return urlencode(
            {
                field: self.cleaned_data[field]
                for field in self.category_fields
                if self.cleaned_data.get(field)
            }
        )


class PlanSwapForm(forms.Form):
    """A request to swap one recipe in an existing meal plan for another.

    `plan` is every recipe currently shown in the meal plan, in page order, so the replacement
    can be kept unique across the whole plan and the shared shopping list rebuilt for it.
    `rejected` lists recipes already swapped out, so repeated swaps work through every
    alternative before offering one of them again.
    """

    plan = forms.TypedMultipleChoiceField(coerce=int)
    swap = forms.TypedChoiceField(coerce=int)
    rejected = forms.TypedMultipleChoiceField(coerce=int, required=False)

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        recipe_choices = [(recipe.id, recipe.title) for recipe in CATALOG]
        for field in self.fields.values():
            field.choices = recipe_choices

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        plan = cleaned_data.get("plan")
        swap = cleaned_data.get("swap")
        if plan is not None and len(set(plan)) != len(plan):
            raise forms.ValidationError("A meal plan cannot contain the same recipe twice.")
        if plan is not None and swap is not None and swap not in plan:
            raise forms.ValidationError("Only a recipe in the meal plan can be swapped.")
        return cleaned_data
