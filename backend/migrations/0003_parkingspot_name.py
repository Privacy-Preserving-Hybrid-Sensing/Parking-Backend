# Generated by Django 3.0.3 on 2020-02-19 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_auto_20200219_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingspot',
            name='name',
            field=models.CharField(db_index=True, default='', max_length=100),
        ),
    ]