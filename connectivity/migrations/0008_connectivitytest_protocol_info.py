# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-16 15:25
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connectivity', '0007_auto_20180116_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectivitytest',
            name='protocol_info',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
            preserve_default=False,
        ),
    ]
