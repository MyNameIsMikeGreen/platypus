from django import forms

from .catalog import CATALOG


def _category_choices() -> list[tuple[str, str]]:
    categories = sorted({recipe.category for recipe in CATALOG})
    return [(category, category.title()) for category in categories]


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
                "role": "combobox",
            }
        ),
    )
    category = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={"data-search-category": True, "id": "recipe-search-category"}),
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [("", "All categories"), *_category_choices()]


class PlannerForm(forms.Form):
    recipe_count = forms.IntegerField(
        label="Number of recipes",
        min_value=1,
        max_value=50,
        initial=7,
    )
    category = forms.ChoiceField(label="Category")

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = _category_choices()
