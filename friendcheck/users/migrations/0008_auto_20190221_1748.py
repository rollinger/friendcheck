# Generated by Django 2.0.10 on 2019-02-21 17:48

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20190221_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='timeline_of_datapoints',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.DateTimeField(), blank=True, null=True, size=None),
        ),
    ]