# Generated by Django 3.0.3 on 2020-02-28 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0022_parkingspothistory_notify_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='participation',
            name='previous_value',
            field=models.FloatField(default=0),
        ),
    ]