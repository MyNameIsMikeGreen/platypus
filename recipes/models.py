from typing import Any

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_mysql.models.fields.lists import ListCharField

COMMA_ENCODING = "##COMMA_LITERAL"
UNCATEGORISED = "UNCATEGORISED"


class PlatypusList(ListCharField):

    # For MySQL list compatibility, encode commas before persisting. Decode them when rendering.
    def get_prep_value(self, value: Any) -> Any:
        value = [v.replace(",", COMMA_ENCODING) for v in value]
        return super().get_prep_value(value)


class Recipe(models.Model):
    title = models.CharField(max_length=128)
    ingredients = PlatypusList(base_field=models.CharField(max_length=128), max_length=128)
    method = PlatypusList(base_field=models.CharField(max_length=1024), max_length=1024)
    category = models.CharField(max_length=32, default=UNCATEGORISED)
    published_date = models.DateField(auto_now=True)
    final = models.BooleanField(default=True)
    tags = PlatypusList(base_field=models.CharField(max_length=128), blank=True, default=list, max_length=128)
    image_urls = PlatypusList(base_field=models.URLField(max_length=256), blank=True, default=list, max_length=256)

    def get_absolute_url(self):
        return reverse('recipes:detail', args=[str(self.id)]) + f"{slugify(self.title)}/"
