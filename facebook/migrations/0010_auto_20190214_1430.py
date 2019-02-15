# Generated by Django 2.0.10 on 2019-02-14 14:30

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0009_auto_20190214_1419'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friend',
            old_name='total_volatility',
            new_name='total_movement',
        ),
        migrations.AddField(
            model_name='friend',
            name='movement',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
    ]