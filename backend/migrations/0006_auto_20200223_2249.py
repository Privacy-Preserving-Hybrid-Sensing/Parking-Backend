# Generated by Django 3.0.3 on 2020-02-23 22:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_auto_20200223_2105'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participantcredit',
            old_name='credit_value',
            new_name='incentive',
        ),
        migrations.RenameField(
            model_name='subscription',
            old_name='credit_charged',
            new_name='charged',
        ),
    ]
