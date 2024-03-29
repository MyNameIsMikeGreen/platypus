from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

UNCATEGORISED = "UNCATEGORISED"


class Recipe(models.Model):
    title = models.CharField(max_length=128)
    ingredients = ArrayField(models.CharField(max_length=128))
    method = ArrayField(models.CharField(max_length=1024))
    category = models.CharField(
        max_length=32,
        default=UNCATEGORISED,
    )
    published_date = models.DateField(auto_now=True)
    final = models.BooleanField(default=True)
    tags = ArrayField(models.CharField(max_length=128), blank=True, default=list)
    image_urls = ArrayField(models.URLField(max_length=256), blank=True, default=list)

    def get_absolute_url(self):
        return reverse('recipes:detail', args=[str(self.id)]) + f"{slugify(self.title)}/"
