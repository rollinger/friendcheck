# Generated by Django 2.0.10 on 2019-02-10 14:34

import django.contrib.postgres.fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0002_auto_20190210_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapoint',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='datapoint',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
        migrations.AlterField(
            model_name='friend',
            name='ranks',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='friend',
            name='social_signals',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='friend',
            name='timestamps',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.DateTimeField(), blank=True, null=True, size=None),
        ),
    ]
