# Generated by Django 3.0.2 on 2020-02-04 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkee_common', '0019_auto_20200204_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataparticipationparkingavailability',
            name='availability_value',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='dataparticipationparkingavailability',
            name='lattitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='dataparticipationparkingavailability',
            name='longitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='interimparkingavailability',
            name='lattitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='interimparkingavailability',
            name='longitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='interimparkingavailability',
            name='total_available',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='interimparkingavailability',
            name='total_unavailable',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='parkingavailabilitylog',
            name='availability_value',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='parkingavailabilitylog',
            name='lattitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='parkingavailabilitylog',
            name='longitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='parkingavailabilitysubscription',
            name='lattitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='parkingavailabilitysubscription',
            name='longitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='parkingslot',
            name='lattitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='parkingslot',
            name='longitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='parkingslot',
            name='total_available',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='parkingslot',
            name='total_unavailable',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='parkingzone',
            name='center_lattitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='parkingzone',
            name='center_longitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='participantcredit',
            name='credit_value',
            field=models.FloatField(default=100),
        ),
        migrations.AlterField(
            model_name='participantmovementlog',
            name='lattitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='participantmovementlog',
            name='longitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
    ]