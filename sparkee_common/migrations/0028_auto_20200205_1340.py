# Generated by Django 3.0.2 on 2020-02-05 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkee_common', '0027_auto_20200205_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataparticipationparkingavailability',
            name='latitude',
            field=models.CharField(db_index=True, default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='dataparticipationparkingavailability',
            name='longitude',
            field=models.CharField(db_index=True, default='0.0', max_length=100),
        ),
    ]