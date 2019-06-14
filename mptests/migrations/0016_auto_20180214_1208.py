# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-14 11:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mptests', '0015_mobilebenchmark'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='benchmark',
            name='mobile',
        ),
        migrations.AlterField(
            model_name='mobilebenchmark',
            name='benchmark',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mobile_benchmark', to='mptests.Benchmark'),
        ),
    ]
