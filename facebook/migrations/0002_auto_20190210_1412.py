# Generated by Django 2.0.10 on 2019-02-10 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datapoint',
            name='fbid_data',
            field=models.TextField(blank=True, help_text='Expects comma-seperated list of facebook ids', null=True, verbose_name='FB ID List'),
        ),
    ]