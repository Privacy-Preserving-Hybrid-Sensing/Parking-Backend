# Generated by Django 3.0.2 on 2020-01-30 06:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sparkee_common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingAvailabilityLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.DateTimeField(default=django.utils.timezone.now)),
                ('participant_uuid', models.CharField(max_length=100)),
                ('longitude', models.FloatField()),
                ('lattitude', models.FloatField()),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='ParticipantMovementLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.DateTimeField(default=django.utils.timezone.now)),
                ('participant_uuid', models.CharField(max_length=100)),
                ('longitude', models.FloatField()),
                ('lattitude', models.FloatField()),
            ],
        ),
        migrations.DeleteModel(
            name='Log',
        ),
        migrations.RenameField(
            model_name='parkingslot',
            old_name='log_type',
            new_name='participant_uuid',
        ),
        migrations.RenameField(
            model_name='parkingslot',
            old_name='ts',
            new_name='ts_register',
        ),
        migrations.RemoveField(
            model_name='parkingslot',
            name='msg',
        ),
        migrations.RemoveField(
            model_name='parkingslot',
            name='routing_key_uuid',
        ),
        migrations.RemoveField(
            model_name='parkingslot',
            name='status',
        ),
        migrations.RemoveField(
            model_name='parkingslot',
            name='value',
        ),
        migrations.AddField(
            model_name='parkingslot',
            name='confidence_available',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='parkingslot',
            name='confidence_unavailable',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='parkingslot',
            name='ts_update',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
