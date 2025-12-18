"""
NTP Timestamp Parser
Handles conversion between NTP timestamps and Python datetime objects
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RawNTPTimestamp:
    """Raw NTP timestamp (seconds and fraction)"""
    seconds: int
    fraction: int


@dataclass
class UnixTime:
    """Unix timestamp representation"""
    seconds: int
    milliseconds: float


@dataclass
class ParsedNTPTimestamp:
    """Fully parsed NTP timestamp with multiple representations"""
    raw: RawNTPTimestamp
    unix: UnixTime
    date: datetime
    iso: str
    local: str
    timestamp: float


@dataclass
class NTPPacketHeader:
    """NTP packet header information"""
    leap_indicator: int
    version_number: int
    mode: int
    stratum: int
    poll_interval: int
    precision: int
    root_delay: int
    root_dispersion: int
    reference_id: str


@dataclass
class NTPTimestamps:
    """All timestamps from NTP packet"""
    reference: ParsedNTPTimestamp
    originate: ParsedNTPTimestamp
    receive: ParsedNTPTimestamp
    transmit: ParsedNTPTimestamp


@dataclass
class ParsedNTPPacket:
    """Complete parsed NTP packet"""
    header: NTPPacketHeader
    timestamps: NTPTimestamps
    round_trip_delay: Optional[float]
    clock_offset: Optional[float]


class NTPParser:
    """Parser for NTP packets"""
    
    # NTP epoch starts on January 1, 1900
    # Unix epoch starts on January 1, 1970
    # The difference is 2,208,988,800 seconds
    NTP_EPOCH_OFFSET = 2208988800
    
    @classmethod
    def parse_packet(cls, buffer: bytes) -> ParsedNTPPacket:
        """
        Parse raw NTP response buffer (48 bytes)
        
        Packet structure:
        - Bytes 0-3: LI, VN, Mode, Stratum, Poll, Precision
        - Bytes 4-7: Root Delay
        - Bytes 8-11: Root Dispersion
        - Bytes 12-15: Reference ID
        - Bytes 16-23: Reference Timestamp
        - Bytes 24-31: Originate Timestamp
        - Bytes 32-39: Receive Timestamp
        - Bytes 40-47: Transmit Timestamp
        """
        if len(buffer) < 48:
            raise ValueError('Invalid NTP packet: minimum 48 bytes required')
        
        # Parse header
        first_byte = buffer[0]
        leap_indicator = (first_byte >> 6) & 0b11
        version_number = (first_byte >> 3) & 0b111
        mode = first_byte & 0b111
        stratum = buffer[1]
        poll_interval = buffer[2]
        precision = buffer[3]
        
        # Parse timestamps
        reference_timestamp = cls._parse_ntp_timestamp(buffer, 16)
        originate_timestamp = cls._parse_ntp_timestamp(buffer, 24)
        receive_timestamp = cls._parse_ntp_timestamp(buffer, 32)
        transmit_timestamp = cls._parse_ntp_timestamp(buffer, 40)
        
        # Parse root delay and dispersion
        root_delay = int.from_bytes(buffer[4:8], byteorder='big')
        root_dispersion = int.from_bytes(buffer[8:12], byteorder='big')
        reference_id = int.from_bytes(buffer[12:16], byteorder='big')
        
        return ParsedNTPPacket(
            header=NTPPacketHeader(
                leap_indicator=leap_indicator,
                version_number=version_number,
                mode=mode,
                stratum=stratum,
                poll_interval=poll_interval,
                precision=precision,
                root_delay=root_delay,
                root_dispersion=root_dispersion,
                reference_id=cls._format_reference_id(reference_id, stratum),
            ),
            timestamps=NTPTimestamps(
                reference=reference_timestamp,
                originate=originate_timestamp,
                receive=receive_timestamp,
                transmit=transmit_timestamp,
            ),
            round_trip_delay=None,
            clock_offset=None,
        )
    
    @classmethod
    def _parse_ntp_timestamp(cls, buffer: bytes, offset: int) -> ParsedNTPTimestamp:
        """Parse 8-byte NTP timestamp (64-bit fixed-point: 32-bit seconds, 32-bit fraction)"""
        seconds = int.from_bytes(buffer[offset:offset + 4], byteorder='big')
        fraction = int.from_bytes(buffer[offset + 4:offset + 8], byteorder='big')
        
        # Convert fraction to milliseconds (32-bit fraction / 2^32 * 1000)
        milliseconds = (fraction / 0x100000000) * 1000
        
        # Convert NTP timestamp to Unix timestamp
        unix_seconds = seconds - cls.NTP_EPOCH_OFFSET
        timestamp = unix_seconds + (milliseconds / 1000)
        date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        return ParsedNTPTimestamp(
            raw=RawNTPTimestamp(seconds=seconds, fraction=fraction),
            unix=UnixTime(seconds=unix_seconds, milliseconds=milliseconds),
            date=date,
            iso=date.isoformat(),
            local=str(date.astimezone()),
            timestamp=timestamp,
        )
    
    @staticmethod
    def _format_reference_id(ref_id: int, stratum: int) -> str:
        """Format reference ID based on stratum"""
        if stratum == 0:
            return 'KISS'
        if stratum == 1:
            # ASCII string for stratum 1
            try:
                return ref_id.to_bytes(4, byteorder='big').decode('ascii').rstrip('\x00')
            except:
                return f'0x{ref_id:08X}'
        else:
            # IPv4 address or identifier
            return f'0x{ref_id:08X}'
