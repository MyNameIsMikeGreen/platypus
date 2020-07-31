# Generated by Django 2.2.13 on 2020-07-31 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20200617_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='category',
            field=models.CharField(choices=[('UNCATEGORISED', 'Uncategorised'), ('MAIN', 'Main'), ('DESSERT', 'Dessert'), ('SNACK', 'Snack')], default='UNCATEGORISED', max_length=32),
        ),
    ]
