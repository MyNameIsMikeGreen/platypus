# Generated by Django 2.2.13 on 2020-06-17 20:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20200617_2031'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipeimage',
            old_name='recipe_id',
            new_name='recipe',
        ),
    ]
