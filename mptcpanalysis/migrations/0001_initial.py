# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-30 23:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import mptcpbench.mptcpanalysis.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('collect', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MPTCPConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conn_id', models.PositiveIntegerField()),
                ('duration', models.DurationField()),
                ('start_time', models.DurationField()),
                ('max_idle_time', models.DurationField(default=datetime.timedelta(0))),
                ('max_idle_time_payload', models.DurationField(default=datetime.timedelta(0))),
                ('socks_daddr', models.GenericIPAddressField(blank=True, null=True)),
                ('socks_port', models.PositiveIntegerField(blank=True, null=True, validators=[mptcpbench.mptcpanalysis.models.validate_port_number])),
                ('trace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.Trace')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPConnectionAddAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_from_client', models.BooleanField()),
                ('advertised_addr', models.GenericIPAddressField()),
                ('sent_time', models.DateTimeField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPConnectionFlow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('bytes_mptcptrace', models.BigIntegerField()),
                ('reinj_bytes', models.BigIntegerField()),
                ('reinj_pc', models.FloatField(validators=[mptcpbench.mptcpanalysis.models.validate_positive_float])),
                ('time_last_ack_tcp', models.DurationField()),
                ('time_last_payload_tcp', models.DurationField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPConnectionFlowBurst',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('subflow_id', models.PositiveIntegerField()),
                ('bytes', models.BigIntegerField()),
                ('packets', models.BigIntegerField()),
                ('duration', models.DurationField()),
                ('start_time', models.DateTimeField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPConnectionFlowRetransDSS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('delta', models.DurationField()),
                ('subflow_id', models.PositiveIntegerField()),
                ('dss', models.BigIntegerField()),
                ('delta_from_first_sending', models.DurationField()),
                ('delta_from_last_retrans', models.DurationField()),
                ('delta_from_last_remote_packet', models.DurationField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPConnectionFlowRTT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('rtt_25p', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_75p', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_90p', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_95p', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_97p', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_98p', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_99p', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_avg', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_max', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_median', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_min', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_samples', models.PositiveIntegerField()),
                ('rtt_stdev', models.DecimalField(decimal_places=3, max_digits=10)),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPConnectionRemoveAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_from_client', models.BooleanField()),
                ('kernel_subflow_id', models.PositiveIntegerField()),
                ('sent_time', models.DateTimeField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPSubflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subflow_id', models.PositiveIntegerField()),
                ('daddr', models.GenericIPAddressField()),
                ('dport', models.PositiveIntegerField(validators=[mptcpbench.mptcpanalysis.models.validate_port_number])),
                ('interface', models.CharField(max_length=16)),
                ('saddr', models.GenericIPAddressField()),
                ('sport', models.PositiveIntegerField(validators=[mptcpbench.mptcpanalysis.models.validate_port_number])),
                ('type', models.CharField(max_length=4)),
                ('wscaledst', models.PositiveSmallIntegerField()),
                ('wscalesrc', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPSubflowFlow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('bytes', models.BigIntegerField()),
                ('bytes_data', models.BigIntegerField()),
                ('bytes_retrans', models.BigIntegerField()),
                ('bytes_tcpip_hdr', models.BigIntegerField()),
                ('nb_ack', models.BigIntegerField()),
                ('nb_fin', models.PositiveIntegerField()),
                ('nb_rst', models.PositiveIntegerField()),
                ('nb_syn', models.PositiveIntegerField()),
                ('packets', models.BigIntegerField()),
                ('packets_outoforder', models.BigIntegerField()),
                ('packets_retrans', models.BigIntegerField()),
                ('reinjected_orig_bytes', models.BigIntegerField()),
                ('reinjected_orig_packets', models.BigIntegerField()),
                ('time_fin_ack_tcp', models.DurationField()),
                ('time_first_ack', models.FloatField()),
                ('time_first_payload', models.FloatField()),
                ('time_last_ack_tcp', models.DurationField()),
                ('time_last_payload', models.FloatField()),
                ('time_last_payload_tcp', models.DurationField()),
                ('time_last_payload_with_retrans_tcp', models.DurationField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPSubflowFlowComplete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('maximum_in_flight_size', models.BigIntegerField()),
                ('minimum_in_flight_size', models.BigIntegerField()),
                ('nb_flow_control', models.BigIntegerField()),
                ('nb_network_duplicate', models.BigIntegerField()),
                ('nb_reordering', models.BigIntegerField()),
                ('nb_rtx_fr', models.BigIntegerField()),
                ('nb_rtx_rto', models.BigIntegerField()),
                ('nb_unknown', models.BigIntegerField()),
                ('nb_unnecessary_rtx_fr', models.BigIntegerField()),
                ('nb_unnecessary_rtx_rto', models.BigIntegerField()),
                ('rtt_avg', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_max', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_min', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rtt_samples', models.BigIntegerField()),
                ('rtt_stdev', models.DecimalField(decimal_places=3, max_digits=10)),
                ('segment_size_max', models.PositiveIntegerField()),
                ('segment_size_min', models.PositiveIntegerField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPSubflowFlowIsReinjection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('sent_time', models.DurationField()),
                ('bytes', models.PositiveIntegerField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPSubflowFlowReinjectedOrig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('end_seq', models.BigIntegerField()),
                ('begin_seq', models.BigIntegerField()),
                ('times_reinjected', models.PositiveIntegerField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPSubflowFlowReinjectedOrigTimestamp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('sent_time', models.DurationField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPSubflowFlowTimestampRetrans',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_client_to_server', models.BooleanField()),
                ('delta', models.DurationField()),
                ('time_from_first_sending', models.DurationField()),
                ('time_from_last_retrans', models.DurationField()),
                ('time_from_last_remote_packet', models.DurationField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPSubflowMatch',
            fields=[
                ('subflow', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='mptcpanalysis.MPTCPSubflow')),
                ('tcp_conn_id', models.BigIntegerField()),
                ('backup', models.BooleanField()),
                ('duration', models.DurationField()),
                ('start_time', models.DurationField()),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MPTCPSubflowSOCKSInfo',
            fields=[
                ('subflow', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='mptcpanalysis.MPTCPSubflow')),
                ('socks_daddr', models.GenericIPAddressField()),
                ('socks_port', models.PositiveIntegerField(validators=[mptcpbench.mptcpanalysis.models.validate_port_number])),
                ('conn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection')),
            ],
        ),
        migrations.AddField(
            model_name='mptcpsubflowflowtimestampretrans',
            name='subflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPSubflow'),
        ),
        migrations.AddField(
            model_name='mptcpsubflowflowreinjectedorigtimestamp',
            name='subflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPSubflow'),
        ),
        migrations.AddField(
            model_name='mptcpsubflowflowreinjectedorig',
            name='subflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPSubflow'),
        ),
        migrations.AddField(
            model_name='mptcpsubflowflowisreinjection',
            name='subflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPSubflow'),
        ),
        migrations.AddField(
            model_name='mptcpsubflowflowcomplete',
            name='subflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPSubflow'),
        ),
        migrations.AddField(
            model_name='mptcpsubflowflow',
            name='subflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPSubflow'),
        ),
        migrations.AddField(
            model_name='mptcpsubflow',
            name='conn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mptcpanalysis.MPTCPConnection'),
        ),
        migrations.AlterUniqueTogether(
            name='mptcpsubflowflowcomplete',
            unique_together=set([('subflow', 'is_client_to_server')]),
        ),
        migrations.AlterUniqueTogether(
            name='mptcpsubflowflow',
            unique_together=set([('subflow', 'is_client_to_server')]),
        ),
        migrations.AlterUniqueTogether(
            name='mptcpsubflow',
            unique_together=set([('conn', 'subflow_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='mptcpconnectionflowrtt',
            unique_together=set([('conn', 'is_client_to_server')]),
        ),
        migrations.AlterUniqueTogether(
            name='mptcpconnectionflow',
            unique_together=set([('conn', 'is_client_to_server')]),
        ),
        migrations.AlterUniqueTogether(
            name='mptcpconnection',
            unique_together=set([('conn_id', 'trace')]),
        ),
    ]
