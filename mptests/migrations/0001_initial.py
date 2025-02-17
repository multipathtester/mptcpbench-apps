# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-16 10:29
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Benchmark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('run_time', models.DurationField()),
                ('start_time', models.DateTimeField()),
                ('ping_mean', models.DurationField()),
                ('ping_var', models.DurationField()),
                ('lat', models.FloatField(blank=True, null=True, verbose_name='Latitude')),
                ('lon', models.FloatField(blank=True, null=True, verbose_name='Longitude')),
                ('acc', models.FloatField(blank=True, null=True, verbose_name='Accuracy')),
                ('alt', models.FloatField(blank=True, null=True, verbose_name='Altitude')),
                ('server_name', models.CharField(max_length=20)),
                ('platform', models.CharField(max_length=20)),
                ('platform_version_name', models.CharField(max_length=30)),
                ('platform_version_code', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=50)),
                ('model_code', models.CharField(max_length=20)),
                ('software_name', models.CharField(max_length=20)),
                ('software_version', models.CharField(max_length=40)),
                ('quic_version', models.CharField(max_length=40)),
            ],
        ),
    ]
