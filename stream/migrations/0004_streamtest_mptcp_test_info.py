# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-16 09:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mptcpinfos', '0001_initial'),
        ('stream', '0003_streamtest_multipath_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamtest',
            name='mptcp_test_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mptcpinfos.MPTCPTestInfo'),
        ),
    ]
