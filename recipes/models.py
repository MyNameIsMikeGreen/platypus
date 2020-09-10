from django.db import models

UNCATEGORISED = "UNCATEGORISED"


class Recipe(models.Model):
    title = models.CharField(max_length=128)
    ingredients = models.CharField(max_length=512)
    method = models.CharField(max_length=8192)
    category = models.CharField(
        max_length=32,
        default=UNCATEGORISED,
    )


class RecipeImage(models.Model):
    url = models.URLField(max_length=256, null=True)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    relative_order = models.IntegerField()
