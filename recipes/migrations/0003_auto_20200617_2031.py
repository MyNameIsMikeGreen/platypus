# Generated by Django 2.2.13 on 2020-06-17 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_recipe_main_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='main_image',
        ),
        migrations.CreateModel(
            name='RecipeImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=256, null=True)),
                ('relative_order', models.IntegerField()),
                ('recipe_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe')),
            ],
        ),
    ]
