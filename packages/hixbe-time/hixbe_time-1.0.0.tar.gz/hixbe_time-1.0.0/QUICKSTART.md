# hixbe-time - Quick Start Guide

## Installation

### Using pip
```bash
pip install hixbe-time
```

### From source
```bash
git clone https://github.com/hixbehq/python-time.git
cd python-time
pip install -e .
```

## CLI Usage

### Get Current Time
```bash
$ hixbe-time
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

### JSON Format (for scripts)
```bash
$ hixbe-time --json
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

### Detailed Analysis
```bash
$ hixbe-time --verbose
=======================================================================
🕐 HIXBE TIME - DETAILED REPORT
=======================================================================

📡 TIMESTAMPS:
  Reference: 2025-12-16T04:27:15.229Z
  Transmit:  2025-12-16T04:27:22.765Z
  Receive:   2025-12-16T04:27:22.764Z

💾 RAW TRANSMIT TIMESTAMP (Bytes 40-47):
  Hex: ECEB5E2AC3DA6422
  Seconds (NTP): 3974848042 → Unix: 1765859242
  Fraction: 0xC3DA6422 = 765.051ms

📋 PACKET HEADER:
  Leap Indicator: 0
  Version:        4
  Mode:           4
  Stratum:        2
  Poll Interval:  2^1
  Precision:      2^231
  Root Delay:     0.002 ms
  Root Dispersion: 0.012 ms
  Reference ID:   0xD8EF230C
```

### Offset Only (useful for scripting)
```bash
$ hixbe-time --offset
+486
```

### Continuous Monitoring
```bash
$ hixbe-time --continuous --interval 2000
⏱️  Starting continuous sync (will fallback to time.google.com if needed)
📊 Interval: 2000ms (2.0s)
Press Ctrl+C to stop

[1] ✅ 2025-12-16T04:27:09.201Z | Offset: +468ms
[2] ✅ 2025-12-16T04:27:11.205Z | Offset: +456ms
[3] ✅ 2025-12-16T04:27:13.210Z | Offset: +442ms
```

## Code Usage

### Python

#### Basic Time Query
```python
from hixbe_time import NTPClient

# Create client and get time
client = NTPClient()
server_time = client.get_time()
print(f"Server time: {server_time}")
```

#### Get Full Query Result
```python
from hixbe_time import NTPClient

client = NTPClient()
result = client.query_sync()

# Access parsed data
transmit_time = result.parsed.timestamps.transmit.date
print(f"Transmit time: {transmit_time.isoformat()}")
print(f"Server: {result.server_address}")
print(f"Stratum: {result.parsed.header.stratum}")
```

#### Check Time Offset
```python
from hixbe_time import NTPClient

client = NTPClient()
offset_ms = client.get_offset()

if offset_ms > 0:
    print(f"System is slow by {offset_ms:.0f}ms")
else:
    print(f"System is fast by {abs(offset_ms):.0f}ms")
```

#### Custom Server
```python
from hixbe_time import NTPClient, NTPClientConfig

# Use Google's NTP server
config = NTPClientConfig(host='time.google.com', timeout=3.0)
client = NTPClient(config)
time = client.get_time()
print(f"Google time: {time}")
```

#### Multiple Servers with Fallback
```python
from hixbe_time import NTPClient, NTPClientConfig

# Will automatically try fallback servers if primary fails
config = NTPClientConfig(
    host='time.hixbe.com',
    fallback_servers=['time.google.com', 'pool.ntp.org']
)
client = NTPClient(config)
result = client.query_sync()
print(f"Used server: {result.used_server}")
```

#### Error Handling
```python
from hixbe_time import NTPClient, NTPClientConfig

config = NTPClientConfig(host='invalid.server.com', timeout=2.0)
client = NTPClient(config)

try:
    result = client.query_sync()
    print(f"Success: {result.parsed.timestamps.transmit.iso}")
except Exception as e:
    print(f"Failed to get time: {e}")
```

#### Continuous Monitoring
```python
import time
from hixbe_time import NTPClient

client = NTPClient()

try:
    while True:
        result = client.query_sync()
        offset = client.get_offset()
        print(f"{result.parsed.timestamps.transmit.iso} | Offset: {offset:+.0f}ms")
        time.sleep(5)
except KeyboardInterrupt:
    print("Stopped")
```

## Common Use Cases

### 1. Time Synchronization Check
```python
from hixbe_time import NTPClient

def check_time_sync(threshold_ms=1000):
    client = NTPClient()
    offset = client.get_offset()
    
    if abs(offset) > threshold_ms:
        return False, f"Clock off by {offset:.0f}ms"
    return True, f"Clock synchronized (offset: {offset:.0f}ms)"

synced, message = check_time_sync()
print(message)
```

### 2. Log Timestamps with Server Time
```python
from hixbe_time import NTPClient
from datetime import datetime

client = NTPClient()

def log_with_server_time(message):
    server_time = client.get_time()
    local_time = datetime.now()
    print(f"[Local: {local_time}] [Server: {server_time}] {message}")

log_with_server_time("Application started")
```

### 3. Automated Time Monitoring Script
```python
import time
import logging
from hixbe_time import NTPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = NTPClient()

while True:
    try:
        offset = client.get_offset()
        if abs(offset) > 1000:
            logger.warning(f"Clock drift detected: {offset:.0f}ms")
        else:
            logger.info(f"Clock synchronized: {offset:+.0f}ms")
    except Exception as e:
        logger.error(f"NTP query failed: {e}")
    
    time.sleep(300)  # Check every 5 minutes
```

## Next Steps

- Read the full [README.md](README.md) for detailed API documentation
- Check out [EXAMPLES.md](EXAMPLES.md) for more examples
- Browse the source code to understand the implementation
