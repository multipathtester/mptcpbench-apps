# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-09 16:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simplehttpget', '0010_simplehttpgettest_quic_test_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simplehttpgetresult',
            name='error_msg',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
    ]
