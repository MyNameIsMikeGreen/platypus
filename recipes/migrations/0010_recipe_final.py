# Generated by Django 3.1.7 on 2021-04-19 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20210122_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='final',
            field=models.BooleanField(default=True),
        ),
    ]
