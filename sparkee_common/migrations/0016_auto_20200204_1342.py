# Generated by Django 3.0.2 on 2020-02-04 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkee_common', '0015_auto_20200204_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participantcredit',
            name='credit_value',
            field=models.FloatField(default=0),
        ),
    ]
