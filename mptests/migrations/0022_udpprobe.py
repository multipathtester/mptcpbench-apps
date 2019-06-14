# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-16 11:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mptests', '0021_mobilebenchmark_wifi_multiple_ssid'),
    ]

    operations = [
        migrations.CreateModel(
            name='UDPProbe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('delay', models.DurationField()),
                ('is_wifi', models.BooleanField()),
                ('mobile_benchmark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptests.MobileBenchmark')),
            ],
        ),
    ]
