# Generated by Django 3.0.2 on 2020-02-03 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkee_common', '0008_parkingslot_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingavailabilitysubscription',
            name='subscriber_type',
            field=models.CharField(db_index=True, default='web', max_length=100),
        ),
    ]
