# Generated by Django 2.0.10 on 2019-02-11 14:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0006_auto_20190211_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datapoint',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datapoints', to=settings.AUTH_USER_MODEL),
        ),
    ]
