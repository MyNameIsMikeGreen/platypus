from django.db import migrations
from django.db.models import SlugField, CharField
from autoslug import AutoSlugField

from recipes.models import Recipe


def migrate_data_forward(apps, schema_editor):
    for instance in Recipe.objects.all():
        instance.slug = instance.title.replace(" ", "-")
        instance.save()


def migrate_data_backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='Recipe',
            name='slug',
            field=CharField(max_length=256, null=True),
            preserve_default=False,
        ),
        migrations.RunPython(
            migrate_data_forward,
            migrate_data_backward,
        ),
    ]