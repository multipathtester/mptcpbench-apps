# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-17 16:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mptests', '0006_benchmark_rcv_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Localisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField(verbose_name='Latitude')),
                ('lon', models.FloatField(verbose_name='Longitude')),
                ('timestamp', models.DateTimeField()),
                ('acc', models.FloatField(verbose_name='Accuracy')),
                ('alt', models.FloatField(verbose_name='Altitude')),
                ('speed', models.FloatField()),
            ],
        ),
        migrations.RemoveField(
            model_name='benchmark',
            name='acc',
        ),
        migrations.RemoveField(
            model_name='benchmark',
            name='alt',
        ),
        migrations.RemoveField(
            model_name='benchmark',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='benchmark',
            name='lon',
        ),
        migrations.AddField(
            model_name='localisation',
            name='benchmark',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptests.Benchmark'),
        ),
    ]
