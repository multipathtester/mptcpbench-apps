from datetime import timedelta, datetime
import json
import pytz

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import Client, TestCase

from .models import Benchmark, MobileBenchmark, Location, UDPProbe
from mptcpbench.netconnectivities.models import NetConnectivity


def create_benchmark(start_time=datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc)):
    return Benchmark.objects.create(
        duration=timedelta(seconds=42.421521),
        start_time=start_time,
        tz="Europe/Brussels",
        ping_med=24.0,
        ping_std=8.9,
        wifi_bytes_received=45,
        wifi_bytes_sent=78,
        cell_bytes_received=33,
        cell_bytes_sent=25,
        multipath_service="aggregate",
        server_name="FR",
        platform="iOS",
        platform_version_name="11.2.5",
        platform_version_code="Version 11.2.5 (Build 15D5057a)",
        device_uuid="11fe6a48-03a8-4c68-bf56-e3a86d45feac",
        device_model="iPhone SE",
        device_model_code="iPhone8,4",
        software_name="QUICTester",
        software_version="1.0",
    )


def get_mptcp_info():
    return [{'0': {'flags': 0,
                   'rxbytes': 141273,
                   'subflowcount': 2,
                   'subflows': {'0': {'dst_ip': '5.196.169.235',
                                      'interfaceindex': 9,
                                      'isexpensive': 0,
                                      'rxbytes': 141273,
                                      'src_ip': '192.168.10.107',
                                      'switches': 0,
                                      'tcp_last_outif': 9,
                                      'tcpi_cell_rxbytes': 0,
                                      'tcpi_cell_rxpackets': 0,
                                      'tcpi_cell_txbytes': 0,
                                      'tcpi_cell_txpackets': 0,
                                      'tcpi_flags': 0,
                                      'tcpi_if_cell': 0,
                                      'tcpi_if_wifi': 1,
                                      'tcpi_if_wifi_awdl': 0,
                                      'tcpi_if_wifi_infra': 1,
                                      'tcpi_if_wired': 1,
                                      'tcpi_options': 7,
                                      'tcpi_rcv_mss': 1408,
                                      'tcpi_rcv_nxt': 659003116,
                                      'tcpi_rcv_space': 131072,
                                      'tcpi_rcv_wscale': 6,
                                      'tcpi_rto': 0,
                                      'tcpi_rttbest': 5,
                                      'tcpi_rttcur': 5,
                                      'tcpi_rttvar': 0,
                                      'tcpi_rxbytes': 141273,
                                      'tcpi_rxduplicatebytes': 1264,
                                      'tcpi_rxoutoforderbytes': 0,
                                      'tcpi_rxpackets': 143,
                                      'tcpi_snd_bw': 0,
                                      'tcpi_snd_cwnd': 4866,
                                      'tcpi_snd_mss': 1408,
                                      'tcpi_snd_nxt': 3457751994,
                                      'tcpi_snd_sbbytes': 0,
                                      'tcpi_snd_ssthresh': 1073725440,
                                      'tcpi_snd_wnd': 57216,
                                      'tcpi_snd_wscale': 7,
                                      'tcpi_srtt': 5,
                                      'tcpi_state': 4,
                                      'tcpi_synrexmits': 0,
                                      'tcpi_txbytes': 685,
                                      'tcpi_txpackets': 73,
                                      'tcpi_txretransmitbytes': 18,
                                      'tcpi_txretransmitpackets': 2,
                                      'tcpi_txunacked': 0,
                                      'tcpi_wifi_rxbytes': 141273,
                                      'tcpi_wifi_rxpackets': 143,
                                      'tcpi_wifi_txbytes': 685,
                                      'tcpi_wifi_txpackets': 73,
                                      'tcpi_wired_rxbytes': 0,
                                      'tcpi_wired_rxpackets': 0,
                                      'tcpi_wired_txbytes': 0,
                                      'tcpi_wired_txpackets': 0,
                                      'txbytes': 685},
                                '1': {'dst_ip': '5.196.169.235',
                                      'interfaceindex': 3,
                                      'isexpensive': 1,
                                      'rxbytes': 0,
                                      'src_ip': '10.218.251.61',
                                      'switches': 0,
                                      'tcp_last_outif': 3,
                                      'tcpi_cell_rxbytes': 0,
                                      'tcpi_cell_rxpackets': 0,
                                      'tcpi_cell_txbytes': 0,
                                      'tcpi_cell_txpackets': 0,
                                      'tcpi_flags': 0,
                                      'tcpi_if_cell': 1,
                                      'tcpi_if_wifi': 0,
                                      'tcpi_if_wifi_awdl': 0,
                                      'tcpi_if_wifi_infra': 0,
                                      'tcpi_if_wired': 0,
                                      'tcpi_options': 7,
                                      'tcpi_rcv_mss': 1368,
                                      'tcpi_rcv_nxt': 3041214175,
                                      'tcpi_rcv_space': 131328,
                                      'tcpi_rcv_wscale': 6,
                                      'tcpi_rto': 0,
                                      'tcpi_rttbest': 0,
                                      'tcpi_rttcur': 192,
                                      'tcpi_rttvar': 96,
                                      'tcpi_rxbytes': 0,
                                      'tcpi_rxduplicatebytes': 0,
                                      'tcpi_rxoutoforderbytes': 0,
                                      'tcpi_rxpackets': 0,
                                      'tcpi_snd_bw': 0,
                                      'tcpi_snd_cwnd': 4380,
                                      'tcpi_snd_mss': 1368,
                                      'tcpi_snd_nxt': 2192104759,
                                      'tcpi_snd_sbbytes': 0,
                                      'tcpi_snd_ssthresh': 1073725440,
                                      'tcpi_snd_wnd': 57216,
                                      'tcpi_snd_wscale': 7,
                                      'tcpi_srtt': 192,
                                      'tcpi_state': 4,
                                      'tcpi_synrexmits': 0,
                                      'tcpi_txbytes': 0,
                                      'tcpi_txpackets': 0,
                                      'tcpi_txretransmitbytes': 0,
                                      'tcpi_txretransmitpackets': 0,
                                      'tcpi_txunacked': 0,
                                      'tcpi_wifi_rxbytes': 0,
                                      'tcpi_wifi_rxpackets': 0,
                                      'tcpi_wifi_txbytes': 0,
                                      'tcpi_wifi_txpackets': 0,
                                      'tcpi_wired_rxbytes': 0,
                                      'tcpi_wired_rxpackets': 0,
                                      'tcpi_wired_txbytes': 0,
                                      'tcpi_wired_txpackets': 0,
                                      'txbytes': 0}},
                   'switchcount': 0,
                   'time': 1521118012.5468512,
                   'txbytes': 685},
             '1': {'flags': 0,
                   'rxbytes': 612,
                   'subflowcount': 2,
                   'subflows': {'0': {'dst_ip': '5.196.169.235',
                                      'interfaceindex': 9,
                                      'isexpensive': 0,
                                      'rxbytes': 612,
                                      'src_ip': '192.168.10.107',
                                      'switches': 0,
                                      'tcp_last_outif': 9,
                                      'tcpi_cell_rxbytes': 0,
                                      'tcpi_cell_rxpackets': 0,
                                      'tcpi_cell_txbytes': 0,
                                      'tcpi_cell_txpackets': 0,
                                      'tcpi_flags': 0,
                                      'tcpi_if_cell': 0,
                                      'tcpi_if_wifi': 1,
                                      'tcpi_if_wifi_awdl': 0,
                                      'tcpi_if_wifi_infra': 1,
                                      'tcpi_if_wired': 1,
                                      'tcpi_options': 7,
                                      'tcpi_rcv_mss': 1408,
                                      'tcpi_rcv_nxt': 967035970,
                                      'tcpi_rcv_space': 131072,
                                      'tcpi_rcv_wscale': 6,
                                      'tcpi_rto': 0,
                                      'tcpi_rttbest': 6,
                                      'tcpi_rttcur': 6,
                                      'tcpi_rttvar': 0,
                                      'tcpi_rxbytes': 612,
                                      'tcpi_rxduplicatebytes': 0,
                                      'tcpi_rxoutoforderbytes': 0,
                                      'tcpi_rxpackets': 68,
                                      'tcpi_snd_bw': 0,
                                      'tcpi_snd_cwnd': 110380,
                                      'tcpi_snd_mss': 1408,
                                      'tcpi_snd_nxt': 3174757351,
                                      'tcpi_snd_sbbytes': 0,
                                      'tcpi_snd_ssthresh': 1073725440,
                                      'tcpi_snd_wnd': 262144,
                                      'tcpi_snd_wscale': 7,
                                      'tcpi_srtt': 6,
                                      'tcpi_state': 4,
                                      'tcpi_synrexmits': 0,
                                      'tcpi_txbytes': 138829,
                                      'tcpi_txpackets': 139,
                                      'tcpi_txretransmitbytes': 2816,
                                      'tcpi_txretransmitpackets': 2,
                                      'tcpi_txunacked': 0,
                                      'tcpi_wifi_rxbytes': 612,
                                      'tcpi_wifi_rxpackets': 68,
                                      'tcpi_wifi_txbytes': 138829,
                                      'tcpi_wifi_txpackets': 139,
                                      'tcpi_wired_rxbytes': 0,
                                      'tcpi_wired_rxpackets': 0,
                                      'tcpi_wired_txbytes': 0,
                                      'tcpi_wired_txpackets': 0,
                                      'txbytes': 138829},
                                '1': {'dst_ip': '5.196.169.235',
                                      'interfaceindex': 3,
                                      'isexpensive': 1,
                                      'rxbytes': 0,
                                      'src_ip': '10.218.251.61',
                                      'switches': 0,
                                      'tcp_last_outif': 3,
                                      'tcpi_cell_rxbytes': 0,
                                      'tcpi_cell_rxpackets': 0,
                                      'tcpi_cell_txbytes': 0,
                                      'tcpi_cell_txpackets': 0,
                                      'tcpi_flags': 0,
                                      'tcpi_if_cell': 1,
                                      'tcpi_if_wifi': 0,
                                      'tcpi_if_wifi_awdl': 0,
                                      'tcpi_if_wifi_infra': 0,
                                      'tcpi_if_wired': 0,
                                      'tcpi_options': 7,
                                      'tcpi_rcv_mss': 1368,
                                      'tcpi_rcv_nxt': 922029148,
                                      'tcpi_rcv_space': 131328,
                                      'tcpi_rcv_wscale': 6,
                                      'tcpi_rto': 0,
                                      'tcpi_rttbest': 0,
                                      'tcpi_rttcur': 177,
                                      'tcpi_rttvar': 88,
                                      'tcpi_rxbytes': 0,
                                      'tcpi_rxduplicatebytes': 0,
                                      'tcpi_rxoutoforderbytes': 0,
                                      'tcpi_rxpackets': 0,
                                      'tcpi_snd_bw': 0,
                                      'tcpi_snd_cwnd': 4380,
                                      'tcpi_snd_mss': 1368,
                                      'tcpi_snd_nxt': 2024177415,
                                      'tcpi_snd_sbbytes': 0,
                                      'tcpi_snd_ssthresh': 1073725440,
                                      'tcpi_snd_wnd': 65408,
                                      'tcpi_snd_wscale': 7,
                                      'tcpi_srtt': 177,
                                      'tcpi_state': 4,
                                      'tcpi_synrexmits': 0,
                                      'tcpi_txbytes': 0,
                                      'tcpi_txpackets': 0,
                                      'tcpi_txretransmitbytes': 0,
                                      'tcpi_txretransmitpackets': 0,
                                      'tcpi_txunacked': 0,
                                      'tcpi_wifi_rxbytes': 0,
                                      'tcpi_wifi_rxpackets': 0,
                                      'tcpi_wifi_txbytes': 0,
                                      'tcpi_wifi_txpackets': 0,
                                      'tcpi_wired_rxbytes': 0,
                                      'tcpi_wired_rxpackets': 0,
                                      'tcpi_wired_txbytes': 0,
                                      'tcpi_wired_txpackets': 0,
                                      'txbytes': 0}},
                   'switchcount': 0,
                   'time': 1521118012.547406,
                   'txbytes': 138829},
             'time': 1521118012.546711}]


def get_quic_info():
    return [{'Connections': {'bd2fb5850e0f011e': {'ConnFlowControl': {'BytesRead': 136594,
                                                                      'BytesSent': 132641,
                                                                      'HighestReceivedByte': 136594,
                                                                      'LastWindowUpdateTime': '2018-03-15T12:46:01.718808Z',
                                                                      'MaxReceiveWindowIncrement': 25165824,
                                                                      'ReceiveWindow': 175701,
                                                                      'ReceiveWindowIncrement': 49152,
                                                                      'RetransmittedBytes': 22500,
                                                                      'SendingWindow': 43125},
                                                  'MaxPathID': 255,
                                                  'NumActivePaths': 3,
                                                  'NumIncomingStreams': 2,
                                                  'NumOutgoingStreams': 0,
                                                  'OpenStreams': [1, 3],
                                                  'Paths': {'0': {'AckSendDelay': 25000000,
                                                                  'BytesInFlight': 0,
                                                                  'CongestionWindow': 46720,
                                                                  'InterfaceName': '',
                                                                  'LargestAckedPacket': 6,
                                                                  'LargestObservedPacketNumber': 6,
                                                                  'LargestObservedReceiveTime': '2018-03-15T12:45:55.4751Z',
                                                                  'LargestReceivedPacketWithAck': 6,
                                                                  'LastActivityTime': '2018-03-15T12:45:55.475069Z',
                                                                  'LastLostTime': '0001-01-01T00:00:00Z',
                                                                  'LastReceivedPacketNumber': 6,
                                                                  'LastSentTime': '2018-03-15T12:45:55.451145Z',
                                                                  'LeastUnackedPacketNumber': 7,
                                                                  'LocalAddr': {'IP': '::', 'Port': 55560, 'Zone': ''},
                                                                  'Losses': 0,
                                                                  'LowerLimitPacketNumber': 5,
                                                                  'PacketsReceivedSinceLastAck': 1,
                                                                  'RTOCount': 0,
                                                                  'RTOTimeout': 257522000,
                                                                  'ReceivedPackets': 6,
                                                                  'RemoteAddr': {'IP': '5.196.169.235', 'Port': 8080, 'Zone': ''},
                                                                  'Retransmissions': 0,
                                                                  'RetransmittablePacketsReceivedSinceLastAck': 0,
                                                                  'SentPackets': 6,
                                                                  'SmoothedRTT': 201690000,
                                                                  'TLPCount': 0},
                                                            '1': {'AckSendDelay': 25000000,
                                                                  'BytesInFlight': 0,
                                                                  'CongestionWindow': 46720,
                                                                  'InterfaceName': 'pdp_ip0',
                                                                  'LargestAckedPacket': 8,
                                                                  'LargestObservedPacketNumber': 8,
                                                                  'LargestObservedReceiveTime': '2018-03-15T12:46:01.691851Z',
                                                                  'LargestReceivedPacketWithAck': 8,
                                                                  'LastActivityTime': '2018-03-15T12:46:01.691721Z',
                                                                  'LastLostTime': '0001-01-01T00:00:00Z',
                                                                  'LastReceivedPacketNumber': 8,
                                                                  'LastSentTime': '2018-03-15T12:46:01.691982Z',
                                                                  'LeastUnackedPacketNumber': 9,
                                                                  'LocalAddr': {'IP': '10.218.251.61', 'Port': 49302, 'Zone': ''},
                                                                  'Losses': 0,
                                                                  'LowerLimitPacketNumber': 6,
                                                                  'PacketsReceivedSinceLastAck': 0,
                                                                  'RTOCount': 0,
                                                                  'RTOTimeout': 598151000,
                                                                  'ReceivedPackets': 8,
                                                                  'RemoteAddr': {'IP': '5.196.169.235', 'Port': 8080, 'Zone': ''},
                                                                  'Retransmissions': 0,
                                                                  'RetransmittablePacketsReceivedSinceLastAck': 0,
                                                                  'SentPackets': 9,
                                                                  'SmoothedRTT': 156831000,
                                                                  'TLPCount': 0},
                                                            '2': {'AckSendDelay': 25000000,
                                                                  'BytesInFlight': 2058,
                                                                  'CongestionWindow': 46720,
                                                                  'InterfaceName': 'en0',
                                                                  'LargestAckedPacket': 451,
                                                                  'LargestObservedPacketNumber': 453,
                                                                  'LargestObservedReceiveTime': '2018-03-15T12:46:02.239701Z',
                                                                  'LargestReceivedPacketWithAck': 452,
                                                                  'LastActivityTime': '2018-03-15T12:46:02.239476Z',
                                                                  'LastLostTime': '0001-01-01T00:00:00Z',
                                                                  'LastReceivedPacketNumber': 453,
                                                                  'LastSentTime': '2018-03-15T12:46:02.280572Z',
                                                                  'LeastUnackedPacketNumber': 453,
                                                                  'LocalAddr': {'IP': '192.168.10.107', 'Port': 60104, 'Zone': ''},
                                                                  'Losses': 0,
                                                                  'LowerLimitPacketNumber': 451,
                                                                  'PacketsReceivedSinceLastAck': 0,
                                                                  'RTOCount': 0,
                                                                  'RTOTimeout': 200000000,
                                                                  'ReceivedPackets': 453,
                                                                  'RemoteAddr': {'IP': '5.196.169.235', 'Port': 8080, 'Zone': ''},
                                                                  'Retransmissions': 42,
                                                                  'RetransmittablePacketsReceivedSinceLastAck': 0,
                                                                  'SentPackets': 454,
                                                                  'SmoothedRTT': 8382000,
                                                                  'TLPCount': 0}},
                                                  'Streams': {'1': {'BytesRead': 136009,
                                                                    'BytesSent': 641,
                                                                    'HighestReceivedByte': 136009,
                                                                    'LastWindowUpdateTime': '2018-03-15T12:46:01.615161Z',
                                                                    'MaxReceiveWindowIncrement': 16777216,
                                                                    'ReceiveWindow': 155948,
                                                                    'ReceiveWindowIncrement': 32768,
                                                                    'RetransmittedBytes': 135,
                                                                    'SendingWindow': 32127},
                                                              '3': {'BytesRead': 585,
                                                                    'BytesSent': 132000,
                                                                    'HighestReceivedByte': 585,
                                                                    'LastWindowUpdateTime': '2018-03-15T12:45:55.488006Z',
                                                                    'MaxReceiveWindowIncrement': 16777216,
                                                                    'ReceiveWindow': 32768,
                                                                    'ReceiveWindowIncrement': 32768,
                                                                    'RetransmittedBytes': 22365,
                                                                    'SendingWindow': 19939}}}},
             'Time': '2018-03-15T12:46:02.281185Z'},
            {'Connections': {'bd2fb5850e0f011e': {'ConnFlowControl': {'BytesRead': 138603,
                                                                      'BytesSent': 134650,
                                                                      'HighestReceivedByte': 138603,
                                                                      'LastWindowUpdateTime': '2018-03-15T12:46:01.718808Z',
                                                                      'MaxReceiveWindowIncrement': 25165824,
                                                                      'ReceiveWindow': 175701,
                                                                      'ReceiveWindowIncrement': 49152,
                                                                      'RetransmittedBytes': 22500,
                                                                      'SendingWindow': 41116},
                                                  'MaxPathID': 255,
                                                  'NumActivePaths': 3,
                                                  'NumIncomingStreams': 2,
                                                  'NumOutgoingStreams': 0,
                                                  'OpenStreams': [1, 3],
                                                  'Paths': {'0': {'AckSendDelay': 25000000,
                                                                  'BytesInFlight': 0,
                                                                  'CongestionWindow': 46720,
                                                                  'InterfaceName': '',
                                                                  'LargestAckedPacket': 6,
                                                                  'LargestObservedPacketNumber': 6,
                                                                  'LargestObservedReceiveTime': '2018-03-15T12:45:55.4751Z',
                                                                  'LargestReceivedPacketWithAck': 6,
                                                                  'LastActivityTime': '2018-03-15T12:45:55.475069Z',
                                                                  'LastLostTime': '0001-01-01T00:00:00Z',
                                                                  'LastReceivedPacketNumber': 6,
                                                                  'LastSentTime': '2018-03-15T12:45:55.451145Z',
                                                                  'LeastUnackedPacketNumber': 7,
                                                                  'LocalAddr': {'IP': '::', 'Port': 55560, 'Zone': ''},
                                                                  'Losses': 0,
                                                                  'LowerLimitPacketNumber': 5,
                                                                  'PacketsReceivedSinceLastAck': 1,
                                                                  'RTOCount': 0,
                                                                  'RTOTimeout': 257522000,
                                                                  'ReceivedPackets': 6,
                                                                  'RemoteAddr': {'IP': '5.196.169.235', 'Port': 8080, 'Zone': ''},
                                                                  'Retransmissions': 0,
                                                                  'RetransmittablePacketsReceivedSinceLastAck': 0,
                                                                  'SentPackets': 6,
                                                                  'SmoothedRTT': 201690000,
                                                                  'TLPCount': 0},
                                                            '1': {'AckSendDelay': 25000000,
                                                                  'BytesInFlight': 0,
                                                                  'CongestionWindow': 46720,
                                                                  'InterfaceName': 'pdp_ip0',
                                                                  'LargestAckedPacket': 8,
                                                                  'LargestObservedPacketNumber': 8,
                                                                  'LargestObservedReceiveTime': '2018-03-15T12:46:01.691851Z',
                                                                  'LargestReceivedPacketWithAck': 8,
                                                                  'LastActivityTime': '2018-03-15T12:46:01.691721Z',
                                                                  'LastLostTime': '0001-01-01T00:00:00Z',
                                                                  'LastReceivedPacketNumber': 8,
                                                                  'LastSentTime': '2018-03-15T12:46:01.691982Z',
                                                                  'LeastUnackedPacketNumber': 9,
                                                                  'LocalAddr': {'IP': '10.218.251.61', 'Port': 49302, 'Zone': ''},
                                                                  'Losses': 0,
                                                                  'LowerLimitPacketNumber': 6,
                                                                  'PacketsReceivedSinceLastAck': 0,
                                                                  'RTOCount': 0,
                                                                  'RTOTimeout': 598151000,
                                                                  'ReceivedPackets': 8,
                                                                  'RemoteAddr': {'IP': '5.196.169.235', 'Port': 8080, 'Zone': ''},
                                                                  'Retransmissions': 0,
                                                                  'RetransmittablePacketsReceivedSinceLastAck': 0,
                                                                  'SentPackets': 9,
                                                                  'SmoothedRTT': 156831000,
                                                                  'TLPCount': 0},
                                                            '2': {'AckSendDelay': 25000000,
                                                                  'BytesInFlight': 2058,
                                                                  'CongestionWindow': 46720,
                                                                  'InterfaceName': 'en0',
                                                                  'LargestAckedPacket': 457,
                                                                  'LargestObservedPacketNumber': 460,
                                                                  'LargestObservedReceiveTime': '2018-03-15T12:46:02.342697Z',
                                                                  'LargestReceivedPacketWithAck': 459,
                                                                  'LastActivityTime': '2018-03-15T12:46:02.342465Z',
                                                                  'LastLostTime': '0001-01-01T00:00:00Z',
                                                                  'LastReceivedPacketNumber': 460,
                                                                  'LastSentTime': '2018-03-15T12:46:02.3846Z',
                                                                  'LeastUnackedPacketNumber': 459,
                                                                  'LocalAddr': {'IP': '192.168.10.107', 'Port': 60104, 'Zone': ''},
                                                                  'Losses': 0,
                                                                  'LowerLimitPacketNumber': 458,
                                                                  'PacketsReceivedSinceLastAck': 0,
                                                                  'RTOCount': 0,
                                                                  'RTOTimeout': 200000000,
                                                                  'ReceivedPackets': 460,
                                                                  'RemoteAddr': {'IP': '5.196.169.235', 'Port': 8080, 'Zone': ''},
                                                                  'Retransmissions': 42,
                                                                  'RetransmittablePacketsReceivedSinceLastAck': 0,
                                                                  'SentPackets': 460,
                                                                  'SmoothedRTT': 8295000,
                                                                  'TLPCount': 0}},
                                                  'Streams': {'1': {'BytesRead': 138009,
                                                                    'BytesSent': 650,
                                                                    'HighestReceivedByte': 138009,
                                                                    'LastWindowUpdateTime': '2018-03-15T12:46:01.615161Z',
                                                                    'MaxReceiveWindowIncrement': 16777216,
                                                                    'ReceiveWindow': 155948,
                                                                    'ReceiveWindowIncrement': 32768,
                                                                    'RetransmittedBytes': 135,
                                                                    'SendingWindow': 32118},
                                                              '3': {'BytesRead': 594,
                                                                    'BytesSent': 134000,
                                                                    'HighestReceivedByte': 594,
                                                                    'LastWindowUpdateTime': '2018-03-15T12:45:55.488006Z',
                                                                    'MaxReceiveWindowIncrement': 16777216,
                                                                    'ReceiveWindow': 32768,
                                                                    'ReceiveWindowIncrement': 32768,
                                                                    'RetransmittedBytes': 22365,
                                                                    'SendingWindow': 17939}}}},
             'Time': '2018-03-15T12:46:02.385329Z'}]


class PostBenchmarkTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_benchmark_with_lon_lat(self):
        json_dict = {
            'locations': [
                {
                    'lat': "50.40121",
                    'lon': "4.37287",
                    'timestamp': "2018-01-16T11:41:40.744000+0100",
                    'acc': "5.0",
                    'alt': "152.0",
                    'speed': "0",
                },
                {
                    'lat': "50.40152",
                    'lon': "4.37299",
                    'timestamp': "2018-01-16T11:41:41.744000+0100",
                    'acc': "10.0",
                    'alt': "151.0",
                    'speed': "1.2",
                },
            ],
            'duration': "42.421521",
            'start_time': "2018-01-16T11:41:40.744000+0100",
            'tz': "Europe/Brussels",
            'ping_med': "24.0",
            'ping_std': "8.9",
            'wifi_bytes_received': 45,
            'wifi_bytes_sent': 78,
            'cell_bytes_received': 33,
            'cell_bytes_sent': 25,
            'multipath_service': 'aggregate',
            'server_name': "FR",
            'platform': "iOS",
            'platform_version_name': "11.2.5",
            'platform_version_code': "Version 11.2.5 (Build 15D5057a)",
            'device_uuid': "11FE6A48-03A8-4C68-BF56-E3A86D45FEAC",
            'device_model': "iPhone SE",
            'device_model_code': "iPhone8,4",
            'software_name': "QUICTester",
            'software_version': "1.0",
        }
        json_to_send = json.dumps(json_dict)
        send_time = timezone.now()
        response = self.client.post(reverse(
            "mptests:create_benchmark"), json_to_send, content_type="application/json")
        json_response = json.loads(response.content.decode("UTF-8"))
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check benchmark was created
        benchmark = Benchmark.objects.get(uuid=json_response['uuid'])
        self.assertEqual(benchmark.duration, timedelta(seconds=42.421521))
        self.assertEqual(benchmark.start_time, datetime(
            2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(benchmark.tz, "Europe/Brussels")
        self.assertEqual(benchmark.ping_med, 24.0)
        self.assertEqual(benchmark.ping_std, 8.9)
        self.assertEqual(benchmark.wifi_bytes_received, 45)
        self.assertEqual(benchmark.wifi_bytes_sent, 78)
        self.assertEqual(benchmark.cell_bytes_received, 33)
        self.assertEqual(benchmark.cell_bytes_sent, 25)
        self.assertEqual(benchmark.location_set.count(), 2)
        loc0 = benchmark.location_set.filter(benchmark=benchmark, lat=50.40121)
        self.assertEqual(len(loc0), 1)
        loc0 = loc0[0]
        self.assertEqual(loc0.lon, 4.37287)
        self.assertEqual(loc0.acc, 5.0)
        self.assertEqual(loc0.alt, 152.0)
        self.assertEqual(loc0.speed, 0)
        self.assertEqual(loc0.timestamp, datetime(
            2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        loc1 = benchmark.location_set.filter(benchmark=benchmark, lat=50.40152)
        self.assertEqual(len(loc1), 1)
        loc1 = loc1[0]
        self.assertEqual(loc1.lat, 50.40152)
        self.assertEqual(loc1.lon, 4.37299)
        self.assertEqual(loc1.acc, 10.0)
        self.assertEqual(loc1.alt, 151.0)
        self.assertEqual(loc1.speed, 1.2)
        self.assertEqual(loc1.timestamp, datetime(
            2018, 1, 16, 10, 41, 41, 744000, tzinfo=pytz.utc))
        self.assertEqual(benchmark.multipath_service, 'aggregate')
        self.assertEqual(benchmark.server_name, "FR")
        self.assertEqual(benchmark.platform, "iOS")
        self.assertEqual(benchmark.platform_version_name, "11.2.5")
        self.assertEqual(benchmark.platform_version_code,
                         "Version 11.2.5 (Build 15D5057a)")
        self.assertEqual(str(benchmark.device_uuid),
                         "11fe6a48-03a8-4c68-bf56-e3a86d45feac")
        self.assertEqual(benchmark.device_model, "iPhone SE")
        self.assertEqual(benchmark.device_model_code, "iPhone8,4")
        self.assertEqual(benchmark.software_name, "QUICTester")
        self.assertEqual(benchmark.software_version, "1.0")
        self.assertFalse(benchmark.user_interrupted)
        self.assertTrue(timedelta(seconds=0) <=
                        benchmark.rcv_time - send_time <= timedelta(seconds=1))

    def test_post_benchmark_without_locations(self):
        json_dict = {
            'locations': [],
            'duration': "42.421521",
            'start_time': "2018-01-16T11:41:40.744000+0100",
            'tz': "Europe/Brussels",
            'ping_med': "24.0",
            'ping_std': "8.9",
            'wifi_bytes_received': 45,
            'wifi_bytes_sent': 78,
            'cell_bytes_received': 33,
            'cell_bytes_sent': 25,
            'multipath_service': 'aggregate',
            'server_name': "FR",
            'platform': "iOS",
            'platform_version_name': "11.2.5",
            'platform_version_code': "Version 11.2.5 (Build 15D5057a)",
            'device_uuid': "11FE6A48-03A8-4C68-BF56-E3A86D45FEAC",
            'device_model': "iPhone SE",
            'device_model_code': "iPhone8,4",
            'software_name': "QUICTester",
            'software_version': "1.0",
        }
        json_to_send = json.dumps(json_dict)
        send_time = timezone.now()
        response = self.client.post(reverse(
            "mptests:create_benchmark"), json_to_send, content_type="application/json")
        json_response = json.loads(response.content.decode("UTF-8"))
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check benchmark was created
        benchmark = Benchmark.objects.get(uuid=json_response['uuid'])
        self.assertEqual(benchmark.duration, timedelta(seconds=42.421521))
        self.assertEqual(benchmark.start_time, datetime(
            2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(benchmark.tz, "Europe/Brussels")
        self.assertEqual(benchmark.ping_med, 24.0)
        self.assertEqual(benchmark.ping_std, 8.9)
        self.assertEqual(benchmark.wifi_bytes_received, 45)
        self.assertEqual(benchmark.wifi_bytes_sent, 78)
        self.assertEqual(benchmark.cell_bytes_received, 33)
        self.assertEqual(benchmark.cell_bytes_sent, 25)
        self.assertEqual(benchmark.location_set.count(), 0)
        self.assertEqual(benchmark.multipath_service, 'aggregate')
        self.assertEqual(benchmark.server_name, "FR")
        self.assertEqual(benchmark.platform, "iOS")
        self.assertEqual(benchmark.platform_version_name, "11.2.5")
        self.assertEqual(benchmark.platform_version_code,
                         "Version 11.2.5 (Build 15D5057a)")
        self.assertEqual(str(benchmark.device_uuid),
                         "11fe6a48-03a8-4c68-bf56-e3a86d45feac")
        self.assertEqual(benchmark.device_model, "iPhone SE")
        self.assertEqual(benchmark.device_model_code, "iPhone8,4")
        self.assertEqual(benchmark.software_name, "QUICTester")
        self.assertEqual(benchmark.software_version, "1.0")
        self.assertTrue(timedelta(seconds=0) <=
                        benchmark.rcv_time - send_time <= timedelta(seconds=1))

    def test_post_benchmark_with_mobile(self):
        json_dict = {
            'locations': [
                {
                    'lat': "50.40121",
                    'lon': "4.37287",
                    'timestamp': "2018-01-16T11:41:40.744000+0100",
                    'acc': "5.0",
                    'alt': "152.0",
                    'speed': "0",
                },
                {
                    'lat': "50.40152",
                    'lon': "4.37299",
                    'timestamp': "2018-01-16T11:41:41.744000+0100",
                    'acc': "10.0",
                    'alt': "151.0",
                    'speed': "1.2",
                },
            ],
            'mobile': {
                'wifi_bytes_distance': 37.5,
                'wifi_bytes_lost_time': "2018-01-16T11:41:40.744000+0100",
                'wifi_system_distance': 50.0,
                'wifi_system_lost_time': "2018-01-16T11:41:41.744000+0100",
            },
            'duration': "42.421521",
            'start_time': "2018-01-16T11:41:40.744000+0100",
            'tz': "Europe/Brussels",
            'ping_med': "24.0",
            'ping_std': "8.9",
            'wifi_bytes_received': 45,
            'wifi_bytes_sent': 78,
            'cell_bytes_received': 33,
            'cell_bytes_sent': 25,
            'multipath_service': 'aggregate',
            'server_name': "FR",
            'platform': "iOS",
            'platform_version_name': "11.2.5",
            'platform_version_code': "Version 11.2.5 (Build 15D5057a)",
            'device_uuid': "11FE6A48-03A8-4C68-BF56-E3A86D45FEAC",
            'device_model': "iPhone SE",
            'device_model_code': "iPhone8,4",
            'software_name': "QUICTester",
            'software_version': "1.0",
        }
        json_to_send = json.dumps(json_dict)
        send_time = timezone.now()
        response = self.client.post(reverse(
            "mptests:create_benchmark"), json_to_send, content_type="application/json")
        json_response = json.loads(response.content.decode("UTF-8"))
        # Check that the response is 201 CREATED
        self.assertEqual(response.status_code, 201)
        # Check benchmark was created
        benchmark = Benchmark.objects.get(uuid=json_response['uuid'])
        self.assertEqual(benchmark.duration, timedelta(seconds=42.421521))
        self.assertEqual(benchmark.start_time, datetime(
            2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(benchmark.tz, "Europe/Brussels")
        self.assertEqual(benchmark.mobile.wifi_bytes_distance, 37.5)
        self.assertEqual(benchmark.mobile.wifi_bytes_lost_time, datetime(
            2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        self.assertEqual(benchmark.mobile.wifi_system_distance, 50.0)
        self.assertEqual(benchmark.mobile.wifi_system_lost_time, datetime(
            2018, 1, 16, 10, 41, 41, 744000, tzinfo=pytz.utc))
        self.assertEqual(benchmark.ping_med, 24.0)
        self.assertEqual(benchmark.ping_std, 8.9)
        self.assertEqual(benchmark.wifi_bytes_received, 45)
        self.assertEqual(benchmark.wifi_bytes_sent, 78)
        self.assertEqual(benchmark.cell_bytes_received, 33)
        self.assertEqual(benchmark.cell_bytes_sent, 25)
        self.assertEqual(benchmark.location_set.count(), 2)
        loc0 = benchmark.location_set.filter(benchmark=benchmark, lat=50.40121)
        self.assertEqual(len(loc0), 1)
        loc0 = loc0[0]
        self.assertEqual(loc0.lon, 4.37287)
        self.assertEqual(loc0.acc, 5.0)
        self.assertEqual(loc0.alt, 152.0)
        self.assertEqual(loc0.speed, 0)
        self.assertEqual(loc0.timestamp, datetime(
            2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc))
        loc1 = benchmark.location_set.filter(benchmark=benchmark, lat=50.40152)
        self.assertEqual(len(loc1), 1)
        loc1 = loc1[0]
        self.assertEqual(loc1.lat, 50.40152)
        self.assertEqual(loc1.lon, 4.37299)
        self.assertEqual(loc1.acc, 10.0)
        self.assertEqual(loc1.alt, 151.0)
        self.assertEqual(loc1.speed, 1.2)
        self.assertEqual(loc1.timestamp, datetime(
            2018, 1, 16, 10, 41, 41, 744000, tzinfo=pytz.utc))
        self.assertEqual(benchmark.multipath_service, 'aggregate')
        self.assertEqual(benchmark.server_name, "FR")
        self.assertEqual(benchmark.platform, "iOS")
        self.assertEqual(benchmark.platform_version_name, "11.2.5")
        self.assertEqual(benchmark.platform_version_code,
                         "Version 11.2.5 (Build 15D5057a)")
        self.assertEqual(str(benchmark.device_uuid),
                         "11fe6a48-03a8-4c68-bf56-e3a86d45feac")
        self.assertEqual(benchmark.device_model, "iPhone SE")
        self.assertEqual(benchmark.device_model_code, "iPhone8,4")
        self.assertEqual(benchmark.software_name, "QUICTester")
        self.assertEqual(benchmark.software_version, "1.0")
        self.assertTrue(timedelta(seconds=0) <=
                        benchmark.rcv_time - send_time <= timedelta(seconds=1))


class ListBenchmark(TestCase):
    def setUp(self):
        self.client = Client()
        self.b1 = Benchmark.objects.create(
            duration=timedelta(seconds=42.421521),
            start_time=datetime(2018, 1, 16, 10, 41, 40,
                                744000, tzinfo=pytz.utc),
            tz="Europe/Brussels",
            ping_med=24.0,
            ping_std=8.9,
            wifi_bytes_received=45,
            wifi_bytes_sent=78,
            cell_bytes_received=33,
            cell_bytes_sent=25,
            multipath_service="aggregate",
            server_name="FR",
            platform="iOS",
            platform_version_name="11.2.5",
            platform_version_code="Version 11.2.5 (Build 15D5057a)",
            device_uuid="11fe6a48-03a8-4c68-bf56-e3a86d45feac",
            device_model="iPhone SE",
            device_model_code="iPhone8,4",
            software_name="QUICTester",
            software_version="1.0",
        )
        Location.objects.create(
            benchmark=self.b1,
            lat=4.1234,
            lon=50.1234,
            timestamp=datetime(2018, 1, 16, 10, 41, 40,
                               744000, tzinfo=pytz.utc),
            acc=10.0,
            alt=15.0,
            speed=1.234,
        )
        Location.objects.create(
            benchmark=self.b1,
            lat=4.5678,
            lon=50.5678,
            timestamp=datetime(2018, 1, 16, 10, 41, 47,
                               744000, tzinfo=pytz.utc),
            acc=5.0,
            alt=17.0,
            speed=1.5678,
        )
        NetConnectivity.objects.create(
            benchmark=self.b1,
            network_type="wifi",
            timestamp=datetime(2018, 1, 16, 10, 41, 40,
                               744000, tzinfo=pytz.utc),
            wifi_network_name="WiFi Name",
            wifi_bssid="12:34:56:78:90:ab",
        )
        NetConnectivity.objects.create(
            benchmark=self.b1,
            network_type="wifi",
            timestamp=datetime(2018, 1, 16, 10, 41, 47,
                               744000, tzinfo=pytz.utc),
            wifi_network_name="WiFi Namer",
            wifi_bssid="12:34:56:78:90:ac",
        )
        self.b2 = Benchmark.objects.create(
            duration=timedelta(seconds=42.421521),
            start_time=datetime(2018, 1, 16, 10, 41, 41,
                                744000, tzinfo=pytz.utc),
            tz="Europe/Brussels",
            ping_med=24.0,
            ping_std=8.9,
            wifi_bytes_received=45,
            wifi_bytes_sent=78,
            cell_bytes_received=33,
            cell_bytes_sent=25,
            multipath_service="aggregate",
            server_name="FR",
            platform="iOS",
            platform_version_name="11.2.5",
            platform_version_code="Version 11.2.5 (Build 15D5057a)",
            device_uuid="11fe6a48-03a8-4c68-bf56-e3a86d45feac",
            device_model="iPhone SE",
            device_model_code="iPhone8,4",
            software_name="QUICTester",
            software_version="1.0",
            user_interrupted=True,
        )
        self.b3 = Benchmark.objects.create(
            duration=timedelta(seconds=42.421521),
            start_time=datetime(2018, 1, 16, 10, 41, 42,
                                744000, tzinfo=pytz.utc),
            tz="Europe/Brussels",
            ping_med=24.0,
            ping_std=8.9,
            wifi_bytes_received=45,
            wifi_bytes_sent=78,
            cell_bytes_received=33,
            cell_bytes_sent=25,
            multipath_service="aggregate",
            server_name="FR",
            platform="iOS",
            platform_version_name="11.2.5",
            platform_version_code="Version 11.2.5 (Build 15D5057a)",
            device_uuid="11fe6a48-03a8-4c68-bf56-e3a86d45feac",
            device_model="iPhone SE",
            device_model_code="iPhone8,4",
            software_name="QUICTester",
            software_version="1.0",
        )
        Location.objects.create(
            benchmark=self.b3,
            lat=4.1234,
            lon=50.1234,
            timestamp=datetime(2018, 1, 16, 10, 41, 40,
                               744000, tzinfo=pytz.utc),
            acc=10.0,
            alt=15.0,
            speed=1.234,
        )
        NetConnectivity.objects.create(
            benchmark=self.b3,
            network_type="wificell",
            timestamp=datetime(2018, 1, 16, 10, 41, 40,
                               744000, tzinfo=pytz.utc),
            wifi_network_name="WiFi Name",
            wifi_bssid="12:34:56:78:90:ab",
            cell_network_name="Operator",
            cell_code="LTE (4G)",
            cell_code_description="LTE (4G)",
            cell_iso_country_code="BE",
            cell_operator_code="123-45",
        )
        NetConnectivity.objects.create(
            benchmark=self.b3,
            network_type="cellwifi",
            timestamp=datetime(2018, 1, 16, 10, 41, 47,
                               744000, tzinfo=pytz.utc),
            wifi_network_name="WiFi Namer",
            wifi_bssid="12:34:56:78:90:ac",
            cell_network_name="Operator",
            cell_code="LTE (4G)",
            cell_code_description="LTE (4G)",
            cell_iso_country_code="BE",
            cell_operator_code="123-45",
        )
        mb = MobileBenchmark.objects.create(
            benchmark=self.b3,
            wifi_bytes_distance=12.4,
            wifi_bytes_lost_time=datetime(
                2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc),
            wifi_system_distance=30.0,
            wifi_system_lost_time=datetime(
                2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc),
        )
        UDPProbe.objects.create(
            mobile_benchmark=mb,
            is_wifi=True,
            time=datetime(2018, 1, 16, 10, 41, 40, 744000, tzinfo=pytz.utc),
            delay="0.0248",
        )

    def test_get_benchmark(self):
        response = self.client.get(reverse("mptests:list_benchmark", kwargs={
                                   'device_uuid': "11fe6a48-03a8-4c68-bf56-e3a86d45feac"}))
        json_response = json.loads(response.content.decode("UTF-8"))
        self.assertEqual(len(json_response), 3)
        json1 = {
            'tz': 'Europe/Brussels',
            'location': {
                'timestamp': '2018-01-16T11:41:40.744000+01:00',
                'lat': 4.1234,
                'acc': 10.0,
                'alt': 15.0,
                'lon': 50.1234,
                'speed': 1.234,
            },
            'netconnectivity': {
                'wifi_bssid': '12:34:56:78:90:ab',
                'network_type': 'wifi',
                'wifi_network_name': 'WiFi Name',
                'timestamp': '2018-01-16T10:41:40.744000Z',
            },
            'wifi_bytes_sent': 78,
            'software_name': 'QUICTester',
            'software_version': '1.0',
            'ping_std': 8.9,
            'cell_bytes_sent': 25,
            'start_time': '2018-01-16T10:41:40.744000Z',
            'ping_med': 24.0,
            'server_name': 'FR',
            'platform_version_code': 'Version 11.2.5 (Build 15D5057a)',
            'platform_version_name': '11.2.5',
            'platform': 'iOS',
            'duration': '42.421521',
            'device_model': 'iPhone SE',
            'multipath_service': 'aggregate',
            'device_model_code': 'iPhone8,4',
            'cell_bytes_received': 33,
            'user_interrupted': False,
            'uuid': str(self.b1.uuid),
            'wifi_bytes_received': 45
        }
        json2 = {
            'tz': 'Europe/Brussels',
            'wifi_bytes_sent': 78,
            'software_name': 'QUICTester',
            'software_version': '1.0',
            'ping_std': 8.9,
            'cell_bytes_sent': 25,
            'start_time': '2018-01-16T10:41:41.744000Z',
            'ping_med': 24.0,
            'server_name': 'FR',
            'platform_version_code': 'Version 11.2.5 (Build 15D5057a)',
            'platform_version_name': '11.2.5',
            'platform': 'iOS',
            'duration': '42.421521',
            'device_model': 'iPhone SE',
            'multipath_service': 'aggregate',
            'device_model_code': 'iPhone8,4',
            'cell_bytes_received': 33,
            'user_interrupted': True,
            'uuid': str(self.b2.uuid),
            'wifi_bytes_received': 45
        }
        json3 = {
            'tz': 'Europe/Brussels',
            'location': {
                'timestamp': '2018-01-16T11:41:40.744000+01:00',
                'lat': 4.1234,
                'acc': 10.0,
                'alt': 15.0,
                'lon': 50.1234,
                'speed': 1.234,
            },
            'mobile': {
                'wifi_bytes_lost_time': '2018-01-16T11:41:40.744000+01:00',
                'wifi_system_lost_time': '2018-01-16T11:41:40.744000+01:00',
                'wifi_system_distance': 30.0,
                'wifi_bytes_distance': 12.4,
                'wifi_bssid_switches': 0,
                'wifi_multiple_ssid': False,
            },
            'netconnectivity': {
                'wifi_bssid': '12:34:56:78:90:ab',
                'cell_code': 'LTE (4G)',
                'cell_iso_country_code': 'BE',
                'network_type': 'wificell',
                'wifi_network_name': 'WiFi Name',
                'cell_network_name': 'Operator',
                'timestamp': '2018-01-16T10:41:40.744000Z',
                'cell_code_description': 'LTE (4G)',
                'cell_operator_code': '123-45',
            },
            'wifi_bytes_sent': 78,
            'software_name': 'QUICTester',
            'software_version': '1.0',
            'ping_std': 8.9,
            'cell_bytes_sent': 25,
            'start_time': '2018-01-16T10:41:42.744000Z',
            'ping_med': 24.0,
            'server_name': 'FR',
            'platform_version_code': 'Version 11.2.5 (Build 15D5057a)',
            'platform_version_name': '11.2.5',
            'platform': 'iOS',
            'duration': '42.421521',
            'device_model': 'iPhone SE',
            'multipath_service': 'aggregate',
            'device_model_code': 'iPhone8,4',
            'cell_bytes_received': 33,
            'user_interrupted': False,
            'uuid': str(self.b3.uuid),
            'wifi_bytes_received': 45
        }
        self.assertTrue(json1 in json_response)
        self.assertTrue(json2 in json_response)
        self.assertTrue(json3 in json_response)


class GetMaxWifiBytesDistance(TestCase):
    def setUp(self):
        b1 = create_benchmark()
        b2 = create_benchmark(start_time=datetime(
            2018, 1, 16, 10, 41, 41, 744000, tzinfo=pytz.utc))
        b3 = create_benchmark(start_time=datetime(
            2018, 1, 16, 10, 41, 42, 744000, tzinfo=pytz.utc))
        MobileBenchmark.objects.create(
            benchmark=b1,
            wifi_bytes_distance=25.0,
            wifi_bytes_lost_time=timezone.now(),
            wifi_system_distance=30.0,
            wifi_system_lost_time=timezone.now(),
        )
        MobileBenchmark.objects.create(
            benchmark=b2,
            wifi_bytes_distance=29.8,
            wifi_bytes_lost_time=timezone.now(),
            wifi_system_distance=30.0,
            wifi_system_lost_time=timezone.now(),
        )
        MobileBenchmark.objects.create(
            benchmark=b3,
            wifi_bytes_distance=12.4,
            wifi_bytes_lost_time=timezone.now(),
            wifi_system_distance=30.0,
            wifi_system_lost_time=timezone.now(),
        )

    def test_get_max_wifi_distance(self):
        response = self.client.get(reverse("mptests:max_wifi_distance"))
        json_response = json.loads(response.content.decode("UTF-8"))
        self.assertTrue('wifi_bytes_distance' in json_response)
        self.assertEqual(json_response['wifi_bytes_distance'], 29.8)
        self.assertTrue('wifi_bssid_switches' in json_response)
        self.assertEqual(json_response['wifi_bssid_switches'], 0)
