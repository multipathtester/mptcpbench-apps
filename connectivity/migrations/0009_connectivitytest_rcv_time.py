# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-17 08:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('connectivity', '0008_connectivitytest_protocol_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectivitytest',
            name='rcv_time',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
