# Generated by Django 3.2 on 2021-10-20 19:43

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_recipe_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), size=None),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='method',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1024), size=None),
        ),
    ]