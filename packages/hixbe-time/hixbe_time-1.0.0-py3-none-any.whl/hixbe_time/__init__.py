"""Hixbe Time - High-precision NTP time synchronization package"""

from .core import (
    NTPClient,
    NTPClientConfig,
    NTPQueryResult,
    NTPParser,
    RawNTPTimestamp,
    ParsedNTPTimestamp,
    NTPPacketHeader,
    NTPTimestamps,
    ParsedNTPPacket,
)

__version__ = '1.0.0'
__author__ = 'Hixbe'
__license__ = 'MIT'

__all__ = [
    'NTPClient',
    'NTPClientConfig',
    'NTPQueryResult',
    'NTPParser',
    'RawNTPTimestamp',
    'ParsedNTPTimestamp',
    'NTPPacketHeader',
    'NTPTimestamps',
    'ParsedNTPPacket',
]
