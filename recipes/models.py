from django.db import models

UNCATEGORISED = "UNCATEGORISED"
MAINS = "MAINS"
DESSERTS = "DESSERTS"
SNACKS = "SNACKS"
CATEGORIES = [
    (UNCATEGORISED, 'Uncategorised'),
    (MAINS, 'Mains'),
    (DESSERTS, 'Desserts'),
    (SNACKS, 'Snacks'),
]


class Recipe(models.Model):
    title = models.CharField(max_length=128)
    ingredients = models.CharField(max_length=512)
    method = models.CharField(max_length=8192)
    category = models.CharField(
        max_length=32,
        choices=CATEGORIES,
        default=UNCATEGORISED,
    )


class RecipeImage(models.Model):
    url = models.URLField(max_length=256, null=True)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    relative_order = models.IntegerField()
