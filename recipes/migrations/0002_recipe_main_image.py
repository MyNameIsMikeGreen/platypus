# Generated by Django 2.2.13 on 2020-06-14 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='main_image',
            field=models.URLField(max_length=256, null=True),
        ),
    ]
