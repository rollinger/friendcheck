# Generated by Django 2.0.10 on 2019-02-22 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0011_auto_20190221_0832'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='comparison',
            field=models.BooleanField(default=False, verbose_name='Add to comparison Chart'),
        ),
    ]