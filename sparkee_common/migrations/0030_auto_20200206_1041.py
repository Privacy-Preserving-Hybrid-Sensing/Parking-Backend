# Generated by Django 3.0.2 on 2020-02-06 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkee_common', '0029_auto_20200205_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participantcredit',
            name='credit_value',
            field=models.FloatField(default=0),
        ),
    ]
