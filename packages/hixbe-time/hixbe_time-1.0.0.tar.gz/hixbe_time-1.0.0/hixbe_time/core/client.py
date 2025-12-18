"""
NTP Client - Sends NTP requests and retrieves responses
"""

import socket
import struct
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, List
from .parser import NTPParser, ParsedNTPPacket


@dataclass
class NTPClientConfig:
    """Configuration for NTP client"""
    host: str = 'time.hixbe.com'
    port: int = 123
    timeout: float = 5.0
    fallback_servers: Optional[List[str]] = None


@dataclass
class NTPQueryResult:
    """Result from NTP query"""
    buffer: bytes
    hex_dump: str
    parsed: ParsedNTPPacket
    server_address: str
    client_receive_time: datetime
    client_originate_time: datetime
    used_server: Optional[str] = None


class NTPClient:
    """NTP Client for querying time servers"""
    
    def __init__(self, config: Optional[NTPClientConfig] = None):
        """Initialize NTP client with configuration"""
        if config is None:
            config = NTPClientConfig()
        
        self.host = config.host
        self.port = config.port
        self.timeout = config.timeout
        self.fallback_servers = config.fallback_servers or ['time.google.com', 'pool.ntp.org']
    
    async def query(self) -> NTPQueryResult:
        """Send NTP request and receive response with automatic fallback"""
        servers = [self.host] + self.fallback_servers
        last_error: Optional[Exception] = None
        
        for server in servers:
            try:
                return await self._query_server(server)
            except Exception as error:
                last_error = error
                # Continue to next server
        
        # All servers failed
        raise Exception(
            f"NTP query failed for all servers ({', '.join(servers)}): {last_error}"
        )
    
    def query_sync(self) -> NTPQueryResult:
        """Synchronous version of query"""
        servers = [self.host] + self.fallback_servers
        last_error: Optional[Exception] = None
        
        for server in servers:
            try:
                return self._query_server_sync(server)
            except Exception as error:
                last_error = error
                # Continue to next server
        
        # All servers failed
        raise Exception(
            f"NTP query failed for all servers ({', '.join(servers)}): {last_error}"
        )
    
    async def _query_server(self, host: str) -> NTPQueryResult:
        """Query a specific NTP server (async wrapper)"""
        # For async, we'll use the sync version wrapped
        # In a real implementation, you might want to use asyncio.get_event_loop().run_in_executor
        return self._query_server_sync(host)
    
    def _query_server_sync(self, host: str) -> NTPQueryResult:
        """Query a specific NTP server (synchronous)"""
        client_originate_time = datetime.now(timezone.utc)
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        
        try:
            # Create NTP request packet
            ntp_packet = self._create_request_packet()
            
            # Send request
            sock.sendto(ntp_packet, (host, self.port))
            
            # Receive response
            buffer, server_info = sock.recvfrom(1024)
            client_receive_time = datetime.now(timezone.utc)
            
            # Parse response
            parsed = NTPParser.parse_packet(buffer)
            
            return NTPQueryResult(
                buffer=buffer,
                hex_dump=self._hex_dump(buffer),
                parsed=parsed,
                server_address=server_info[0],
                client_receive_time=client_receive_time,
                client_originate_time=client_originate_time,
                used_server=host,
            )
        
        except socket.timeout:
            raise Exception(f'NTP request timeout after {self.timeout}s to {host}')
        
        finally:
            sock.close()
    
    def _create_request_packet(self) -> bytes:
        """
        Create NTP request packet (48 bytes)
        
        NTP packet format:
        - Byte 0: LI (2 bits), VN (3 bits), Mode (3 bits)
        - Bytes 1-47: Other fields (zeros for client request)
        """
        # LI = 0, VN = 3 (NTP v3), Mode = 3 (client)
        packet = bytearray(48)
        packet[0] = 0b00011011  # LI=0, VN=3, Mode=3
        
        return bytes(packet)
    
    @staticmethod
    def _hex_dump(buffer: bytes) -> str:
        """Create hex dump of buffer"""
        return buffer.hex().upper()
    
    def get_time(self) -> datetime:
        """Get current time from NTP server"""
        result = self.query_sync()
        return result.parsed.timestamps.transmit.date
    
    def get_offset(self) -> float:
        """Get offset between local and server time in milliseconds"""
        result = self.query_sync()
        server_time = result.parsed.timestamps.transmit.date
        local_time = result.client_receive_time
        offset_seconds = (server_time - local_time).total_seconds()
        return offset_seconds * 1000  # Convert to milliseconds
    
    def get_time_sync(self) -> datetime:
        """Alias for get_time (synchronous)"""
        return self.get_time()
    
    def get_offset_sync(self) -> float:
        """Alias for get_offset (synchronous)"""
        return self.get_offset()
