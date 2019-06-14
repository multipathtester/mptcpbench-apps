# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-16 12:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quicinfos', '0002_auto_20180316_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='quicpathinfo',
            name='ack_send_delay',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='quicpathinfo',
            name='rto_timeout',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='quicpathinfo',
            name='smoothed_rtt',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
    ]
