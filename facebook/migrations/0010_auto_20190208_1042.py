# Generated by Django 2.0.10 on 2019-02-08 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0009_auto_20190205_1555'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friend',
            old_name='ranks',
            new_name='_ranks',
        ),
        migrations.AlterField(
            model_name='friend',
            name='last_rank',
            field=models.IntegerField(blank=True, null=True, verbose_name='Last FB Rank'),
        ),
    ]
