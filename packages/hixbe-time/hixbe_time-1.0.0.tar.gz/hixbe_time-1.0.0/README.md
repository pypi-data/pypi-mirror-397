# hixbe-time

**High-precision NTP time synchronization package with powerful CLI tools**

A professional-grade Python package for querying NTP servers and synchronizing system time with network time servers. Built with Hixbe's primary server `time.hixbe.com` for ultra-reliable time synchronization.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Rich Feature Set**
- 🚀 High-performance NTP client
- 📊 Raw packet inspection & analysis
- ⏱️ Precise timestamp conversion (NTP to Unix)
- 🔄 Continuous sync mode with configurable intervals
- 📡 Multiple server support (Hixbe, pool.ntp.org, etc.)
- 📋 Detailed verbose reporting
- 🎨 Beautiful CLI with multiple output formats
- 🔐 Type-safe implementation with dataclasses
- ⚡ Zero external dependencies (uses Python standard library)

## Installation

```bash
pip install hixbe-time
```

### Development Installation

```bash
git clone https://github.com/hixbehq/python-time.git
cd python-time
pip install -e .
```

## Quick Start

### CLI Usage

```bash
# Get current time from Hixbe server
hixbe-time

# Verbose mode with raw packet details
hixbe-time --verbose

# Output as JSON
hixbe-time --json

# Get time offset (useful for scripts)
hixbe-time --offset

# Continuous synchronization (every 5 seconds)
hixbe-time --continuous

# Custom interval (every 2 seconds)
hixbe-time --continuous --interval 2000

# Query different server
hixbe-time --server pool.ntp.org --verbose

# Show only the offset
hixbe-time --offset
```

### Programmatic Usage

```python
from hixbe_time import NTPClient

# Basic usage
client = NTPClient()
result = client.query_sync()
print(result.parsed.timestamps.transmit.date)

# Get current time
time = client.get_time()
print(time)  # datetime object

# Get offset between local and server time
offset_ms = client.get_offset()
print(f'System is {"slow" if offset_ms > 0 else "fast"} by {abs(offset_ms):.0f}ms')

# Custom server
from hixbe_time import NTPClientConfig

config = NTPClientConfig(
    host='time.google.com',
    timeout=3.0
)
custom_client = NTPClient(config)
time = custom_client.get_time()
```

## API Reference

### `NTPClient`

Main class for NTP queries.

```python
class NTPClient:
    def __init__(self, config: Optional[NTPClientConfig] = None):
        """
        Initialize NTP client
        
        Args:
            config: Client configuration (optional)
        """
    
    def query_sync(self) -> NTPQueryResult:
        """
        Query NTP server synchronously
        
        Returns:
            NTPQueryResult with complete packet data
        """
    
    def get_time(self) -> datetime:
        """
        Get current time from NTP server
        
        Returns:
            datetime object with server time
        """
    
    def get_offset(self) -> float:
        """
        Get offset between local and server time
        
        Returns:
            Offset in milliseconds (positive = local is slow)
        """
```

### `NTPClientConfig`

Configuration options for NTP client.

```python
@dataclass
class NTPClientConfig:
    host: str = 'time.hixbe.com'      # NTP server hostname
    port: int = 123                    # NTP port (default: 123)
    timeout: float = 5.0               # Timeout in seconds
    fallback_servers: Optional[List[str]] = None  # Fallback servers
```

### `NTPQueryResult`

Result from NTP query containing all response data.

```python
@dataclass
class NTPQueryResult:
    buffer: bytes                      # Raw response buffer
    hex_dump: str                      # Hexadecimal dump
    parsed: ParsedNTPPacket            # Parsed packet data
    server_address: str                # Server IP address
    client_receive_time: datetime      # Client receive timestamp
    client_originate_time: datetime    # Client send timestamp
    used_server: Optional[str]         # Server hostname used
```

## CLI Options

```
usage: hixbe-time [-h] [-s SERVER] [-j] [-v] [-o] [-c] [-i INTERVAL] [--version]

High-precision NTP time synchronization

options:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        NTP server to query (default: time.hixbe.com)
  -j, --json            Output in JSON format
  -v, --verbose         Verbose output with packet details
  -o, --offset          Show only time offset in milliseconds
  -c, --continuous      Continuous synchronization mode
  -i INTERVAL, --interval INTERVAL
                        Interval for continuous mode in milliseconds (default: 5000)
  --version             show program's version number and exit
```

## Examples

### Get Server Time

```python
from hixbe_time import NTPClient

client = NTPClient()
server_time = client.get_time()
print(f"Server time: {server_time}")
```

### Check Time Synchronization

```python
from hixbe_time import NTPClient

client = NTPClient()
offset = client.get_offset()

if abs(offset) > 1000:
    print(f"⚠️  WARNING: System clock is off by {offset:.0f}ms")
else:
    print(f"✅ System clock is synchronized (offset: {offset:.0f}ms)")
```

### Query Multiple Servers

```python
from hixbe_time import NTPClient, NTPClientConfig

servers = ['time.hixbe.com', 'time.google.com', 'pool.ntp.org']

for server in servers:
    config = NTPClientConfig(host=server)
    client = NTPClient(config)
    try:
        result = client.query_sync()
        print(f"{server}: {result.parsed.timestamps.transmit.iso}")
    except Exception as e:
        print(f"{server}: Error - {e}")
```

### Continuous Monitoring

```python
import time
from hixbe_time import NTPClient

client = NTPClient()

while True:
    try:
        result = client.query_sync()
        server_time = result.parsed.timestamps.transmit.date
        offset = client.get_offset()
        print(f"{server_time.isoformat()} | Offset: {offset:+.0f}ms")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(5)  # Wait 5 seconds
```

## Output Formats

### Default Format

```
======================================================================
🕐 HIXBE TIME SYNC
======================================================================

Server:        154.26.137.94 (time.hixbe.com)
UTC Time:      2025-12-16T04:27:07.341Z
Local Time:    2025-12-16 04:27:07.341000+00:00
Offset:        +0.480 seconds
Precision:     ±231 (2^x sec)
Stratum:       2
======================================================================
```

### JSON Format

```json
{
  "timestamp": 1765859251781,
  "iso": "2025-12-16T04:27:31.781Z",
  "server": {
    "address": "154.26.137.94",
    "stratum": 2,
    "referenceId": "0xD8EF230C"
  },
  "offset": 524,
  "precision": 231,
  "version": 4
}
```

### Verbose Format

Shows detailed packet analysis including:
- All timestamps (reference, originate, receive, transmit)
- Raw NTP timestamp data in hexadecimal
- Complete packet header information
- Full hex dump of the response packet

## Requirements

- Python 3.8 or higher
- No external dependencies (uses standard library only)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Hixbe - https://hixbe.com

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **Homepage**: https://github.com/hixbehq/python-time
- **PyPI**: https://pypi.org/project/hixbe-time/
- **Issues**: https://github.com/hixbehq/python-time/issues
