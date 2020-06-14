from django.db import models


class Recipe(models.Model):
    title = models.CharField(max_length=128)
    ingredients = models.CharField(max_length=512)
    method = models.CharField(max_length=8192)
