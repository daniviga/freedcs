# Generated by Django 3.0.6 on 2020-06-03 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telemetry', '0005_telemetry_clock'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='telemetry',
            options={'ordering': ['-time', 'device'], 'verbose_name_plural': 'Telemetry'},
        ),
    ]
