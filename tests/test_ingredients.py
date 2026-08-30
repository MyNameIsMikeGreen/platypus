import pytest

from recipes.ingredients import export_name


@pytest.mark.parametrize(
    ("ingredient", "expected"),
    [
        ("600ml Double Cream", "Double Cream"),
        ("6 Eggs", "Eggs"),
        ("240g Caster Sugar", "Caster Sugar"),
        ("1 Egg (Optional)", "Egg (Optional)"),
        ("1/2 Onion", "Onion"),
        ("1/4 Teaspoon Salt", "Salt"),
        ("1.5 Tablespoons Ras-El-Hanout", "Ras-El-Hanout"),
        ("~150ml Milk", "Milk"),
        ("~5 Celery Sticks", "Celery Sticks"),
        ("2-3 Slices Thick Bread", "Thick Bread"),
        ("150g-200g King Prawns", "King Prawns"),
        ("500g 10-15% Fat Minced Beef", "10-15% Fat Minced Beef"),
        ("1 Can (~250g) Chickpeas", "Chickpeas"),
        ("1 Tin (400g) Chopped Tomatoes", "Chopped Tomatoes"),
        ("425g (1 Tin) Pumpkin", "Pumpkin"),
        ("1 Head of Broccoli", "Broccoli"),
        ("8 Rashers of Bacon", "Bacon"),
        ("6-8 Rashers Bacon", "Bacon"),
        ("2 Cloves Garlic", "Garlic"),
        ("2 Garlic Cloves", "Garlic Cloves"),
        ("1 Ball Mozzarella", "Mozzarella"),
        ("Half Teaspoon Baking Powder", "Baking Powder"),
        ("Half Teaspoon Bicarbonate of Soda", "Bicarbonate of Soda"),
        ("Pinch of Salt", "Salt"),
        ("Pinch Salt Flakes", "Salt Flakes"),
        ("Handful of Fresh Basil", "Fresh Basil"),
        ("Handful Fresh Basil (Optional)", "Fresh Basil (Optional)"),
        # No recognised leading quantity: returned unchanged.
        ("Salt and Pepper (To Taste)", "Salt and Pepper (To Taste)"),
        ("Fresh Rosemary", "Fresh Rosemary"),
        ("Olive Oil", "Olive Oil"),
        ("Toppings of Choice", "Toppings of Choice"),
        (
            "Meat Filling of Choice (e.g. Pulled Pork/Chicken, Spiced Mince Beef)",
            "Meat Filling of Choice (e.g. Pulled Pork/Chicken, Spiced Mince Beef)",
        ),
        # Whitespace is trimmed even when nothing else changes.
        ("  Fresh Rosemary  ", "Fresh Rosemary"),
        (" 2 Tablespoons Flour", "Flour"),
    ],
)
def test_export_name_strips_recognised_quantities(ingredient, expected):
    assert export_name(ingredient) == expected


def test_export_name_never_returns_empty_string():
    # A pathological "quantity-only" ingredient should fall back to the original text
    # rather than exporting nothing.
    assert export_name("2 Tablespoons") == "2 Tablespoons"
