# Generated by Django 3.0.3 on 2020-02-24 13:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_auto_20200224_1339'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parkingspotchanges',
            old_name='status',
            new_name='parking_status',
        ),
        migrations.RenameField(
            model_name='parkingspotchanges',
            old_name='ts_change',
            new_name='ts_register',
        ),
        migrations.AddField(
            model_name='parkingspotchanges',
            name='name',
            field=models.CharField(db_index=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='parkingspotchanges',
            name='registrar_uuid',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='parkingspotchanges',
            name='ts_update',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='parkingspotchanges',
            name='zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.ParkingZone'),
        ),
        migrations.AlterField(
            model_name='parkingspotchanges',
            name='confidence_level',
            field=models.FloatField(default=1.0),
        ),
        migrations.AlterField(
            model_name='parkingspotchanges',
            name='latitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='parkingspotchanges',
            name='longitude',
            field=models.CharField(default='0.0', max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='parkingspotchanges',
            unique_together={('longitude', 'latitude', 'ts_update')},
        ),
        migrations.RemoveField(
            model_name='parkingspotchanges',
            name='parking_spot',
        ),
    ]
