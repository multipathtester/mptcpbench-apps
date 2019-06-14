# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-30 23:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('collect', '0001_initial'),
        ('benches', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectivityBench',
            fields=[
                ('bench_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='benches.Bench')),
                ('port', models.PositiveIntegerField()),
                ('url', models.CharField(max_length=200)),
            ],
            bases=('benches.bench',),
        ),
        migrations.CreateModel(
            name='ConnectivityResult',
            fields=[
                ('result_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collect.Result')),
                ('success', models.BooleanField()),
            ],
            bases=('collect.result',),
        ),
    ]
