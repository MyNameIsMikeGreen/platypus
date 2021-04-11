# Generated by Django 2.2.13 on 2020-06-14 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('ingredients', models.CharField(max_length=512)),
                ('method', models.CharField(max_length=8192)),
            ],
        ),
    ]
