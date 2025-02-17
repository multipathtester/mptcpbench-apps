# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-16 14:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mptests', '0003_clientip'),
        ('connectivity', '0002_auto_20180116_1504'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectivityConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port', models.PositiveIntegerField()),
                ('url', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConnectivityResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('success', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConnectivityTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('start_time', models.DateTimeField()),
                ('wait_time', models.DurationField()),
                ('duration', models.DurationField()),
                ('name', models.CharField(max_length=20)),
                ('config', models.CharField(max_length=20)),
                ('benchmark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptests.Benchmark')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='connectivityresult',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='connectivity.ConnectivityTest'),
        ),
        migrations.AddField(
            model_name='connectivityconfig',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='connectivity.ConnectivityTest'),
        ),
    ]
