# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-16 09:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mptcpinfos', '0002_mptcpconnectioninfo_flags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_rcv_nxt',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_rcv_space',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_rto',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_rttbest',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_rttcur',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_rttvar',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_snd_cwnd',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_snd_mss',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_snd_nxt',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_snd_sbbytes',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_snd_ssthresh',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_snd_wnd',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='mptcpsubflowinfo',
            name='tcpi_srtt',
            field=models.BigIntegerField(),
        ),
    ]
