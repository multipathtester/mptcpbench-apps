# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-23 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iperf', '0003_auto_20180117_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='iperfresult',
            name='error_msg',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
