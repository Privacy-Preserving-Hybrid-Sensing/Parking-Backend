# Generated by Django 3.0.3 on 2020-02-23 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_auto_20200223_2249'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participation',
            old_name='processed',
            new_name='incentive_processed',
        ),
        migrations.RemoveField(
            model_name='participation',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='participation',
            name='longitude',
        ),
        migrations.AddField(
            model_name='participation',
            name='incentive_value',
            field=models.IntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='ParticipantCredit',
        ),
    ]
