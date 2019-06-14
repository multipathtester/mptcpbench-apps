# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-17 09:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('msg', '0004_msgtest_rcv_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='msgconfig',
            name='test',
        ),
        migrations.AddField(
            model_name='msgtest',
            name='config',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='msg.MsgConfig'),
            preserve_default=False,
        ),
    ]
