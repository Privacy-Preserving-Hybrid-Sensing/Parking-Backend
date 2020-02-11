# Generated by Django 3.0.2 on 2020-02-04 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkee_common', '0011_parkingslot_zone'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('center_longitude', models.FloatField()),
                ('center_lattitude', models.FloatField()),
            ],
        ),
        migrations.RemoveField(
            model_name='parkingslot',
            name='zone',
        ),
    ]