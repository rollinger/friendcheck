# Generated by Django 2.0.10 on 2019-02-21 17:03

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20190221_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='timeline_of_datapoints',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.DateTimeField(), default=[], size=None),
        ),
    ]
