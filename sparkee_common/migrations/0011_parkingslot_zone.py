# Generated by Django 3.0.2 on 2020-02-04 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkee_common', '0010_auto_20200204_0119'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingslot',
            name='zone',
            field=models.CharField(db_index=True, default='', max_length=100),
        ),
    ]
