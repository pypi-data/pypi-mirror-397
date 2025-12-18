# hixbe-time Examples

Comprehensive examples demonstrating various use cases for the hixbe-time package.

## Table of Contents

- [Basic Usage](#basic-usage)
- [CLI Examples](#cli-examples)
- [Advanced Usage](#advanced-usage)
- [Real-World Applications](#real-world-applications)

## Basic Usage

### Simple Time Query

```python
from hixbe_time import NTPClient

client = NTPClient()
server_time = client.get_time()
print(f"Current server time: {server_time}")
```

### Get Time with Offset

```python
from hixbe_time import NTPClient

client = NTPClient()
offset = client.get_offset()
server_time = client.get_time()

print(f"Server time: {server_time}")
print(f"Offset: {offset:+.2f}ms")
print(f"Status: {'System is slow' if offset > 0 else 'System is fast'}")
```

### Complete Query Result

```python
from hixbe_time import NTPClient

client = NTPClient()
result = client.query_sync()

print(f"Server: {result.server_address} ({result.used_server})")
print(f"Stratum: {result.parsed.header.stratum}")
print(f"Version: {result.parsed.header.version_number}")
print(f"Transmit time: {result.parsed.timestamps.transmit.iso}")
print(f"Receive time: {result.parsed.timestamps.receive.iso}")
```

## CLI Examples

### Basic Commands

```bash
# Get current time
hixbe-time

# Get time in JSON format
hixbe-time --json

# Show only offset
hixbe-time --offset

# Verbose output with packet details
hixbe-time --verbose
```

### Using Different Servers

```bash
# Query Google's NTP server
hixbe-time --server time.google.com

# Query pool.ntp.org
hixbe-time --server pool.ntp.org --json
```

### Continuous Monitoring

```bash
# Monitor every 5 seconds (default)
hixbe-time --continuous

# Monitor every 2 seconds
hixbe-time --continuous --interval 2000

# Monitor specific server every 10 seconds
hixbe-time --server time.google.com --continuous --interval 10000
```

### Scripting with CLI

```bash
# Get offset and use in a script
OFFSET=$(hixbe-time --offset)
if [ $OFFSET -gt 1000 ]; then
    echo "WARNING: Clock is off by ${OFFSET}ms"
fi

# Parse JSON output with jq
hixbe-time --json | jq '.server.stratum'
```

## Advanced Usage

### Custom Configuration

```python
from hixbe_time import NTPClient, NTPClientConfig

# Custom configuration
config = NTPClientConfig(
    host='time.google.com',
    port=123,
    timeout=3.0,
    fallback_servers=['time.cloudflare.com', 'pool.ntp.org']
)

client = NTPClient(config)
result = client.query_sync()
print(f"Time from {result.used_server}: {result.parsed.timestamps.transmit.iso}")
```

### Analyze NTP Packet

```python
from hixbe_time import NTPClient

client = NTPClient()
result = client.query_sync()

# Header information
header = result.parsed.header
print("=== NTP Packet Header ===")
print(f"Leap Indicator: {header.leap_indicator}")
print(f"Version: {header.version_number}")
print(f"Mode: {header.mode}")
print(f"Stratum: {header.stratum}")
print(f"Poll Interval: 2^{header.poll_interval} seconds")
print(f"Precision: 2^{header.precision} seconds")
print(f"Reference ID: {header.reference_id}")

# Timestamps
timestamps = result.parsed.timestamps
print("\n=== Timestamps ===")
print(f"Reference: {timestamps.reference.iso}")
print(f"Originate: {timestamps.originate.iso}")
print(f"Receive: {timestamps.receive.iso}")
print(f"Transmit: {timestamps.transmit.iso}")

# Raw data
print(f"\n=== Raw Transmit Timestamp ===")
print(f"Seconds: {timestamps.transmit.raw.seconds}")
print(f"Fraction: 0x{timestamps.transmit.raw.fraction:08X}")
print(f"Unix timestamp: {timestamps.transmit.timestamp}")
```

### Query Multiple Servers

```python
from hixbe_time import NTPClient, NTPClientConfig

servers = [
    'time.hixbe.com',
    'time.google.com',
    'time.cloudflare.com',
    'pool.ntp.org',
]

results = []

for server in servers:
    config = NTPClientConfig(host=server, timeout=3.0)
    client = NTPClient(config)
    
    try:
        result = client.query_sync()
        results.append({
            'server': server,
            'time': result.parsed.timestamps.transmit.iso,
            'stratum': result.parsed.header.stratum,
            'offset': (result.parsed.timestamps.transmit.date - 
                      result.client_receive_time).total_seconds() * 1000
        })
        print(f"✅ {server}: {result.parsed.timestamps.transmit.iso}")
    except Exception as e:
        print(f"❌ {server}: {e}")

# Find server with lowest stratum
if results:
    best_server = min(results, key=lambda x: x['stratum'])
    print(f"\nBest server: {best_server['server']} (stratum {best_server['stratum']})")
```

### Calculate Round-Trip Delay

```python
from hixbe_time import NTPClient

client = NTPClient()
result = client.query_sync()

# Round-trip delay calculation
t0 = result.client_originate_time  # Client send time
t1 = result.parsed.timestamps.receive.date  # Server receive time
t2 = result.parsed.timestamps.transmit.date  # Server transmit time
t3 = result.client_receive_time  # Client receive time

delay = ((t3 - t0) - (t2 - t1)).total_seconds()
offset = ((t1 - t0) + (t2 - t3)).total_seconds() / 2

print(f"Round-trip delay: {delay * 1000:.3f}ms")
print(f"Clock offset: {offset * 1000:.3f}ms")
```

## Real-World Applications

### 1. Time Synchronization Monitor

```python
import time
import logging
from datetime import datetime
from hixbe_time import NTPClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TimeSyncMonitor:
    def __init__(self, threshold_ms=1000, check_interval=300):
        self.client = NTPClient()
        self.threshold_ms = threshold_ms
        self.check_interval = check_interval
    
    def check_sync(self):
        """Check if system time is synchronized"""
        try:
            offset = self.client.get_offset()
            
            if abs(offset) > self.threshold_ms:
                logger.warning(f"Clock drift detected: {offset:+.0f}ms")
                return False
            else:
                logger.info(f"Clock synchronized: {offset:+.0f}ms")
                return True
        except Exception as e:
            logger.error(f"NTP query failed: {e}")
            return None
    
    def run(self):
        """Run continuous monitoring"""
        logger.info("Starting time synchronization monitor")
        
        try:
            while True:
                self.check_sync()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")

# Run the monitor
if __name__ == '__main__':
    monitor = TimeSyncMonitor(threshold_ms=500, check_interval=60)
    monitor.run()
```

### 2. Distributed System Time Logger

```python
from datetime import datetime
from hixbe_time import NTPClient

class TimeLogger:
    def __init__(self):
        self.client = NTPClient()
    
    def log(self, event, data=None):
        """Log event with both local and server time"""
        local_time = datetime.now()
        try:
            server_time = self.client.get_time()
            offset = self.client.get_offset()
            
            log_entry = {
                'event': event,
                'local_time': local_time.isoformat(),
                'server_time': server_time.isoformat(),
                'offset_ms': round(offset, 2),
                'data': data
            }
            
            print(f"[{local_time}] [Server: {server_time}] "
                  f"[Offset: {offset:+.0f}ms] {event}")
            
            return log_entry
        except Exception as e:
            print(f"[{local_time}] Warning: Could not sync with NTP server: {e}")
            return {
                'event': event,
                'local_time': local_time.isoformat(),
                'server_time': None,
                'offset_ms': None,
                'data': data
            }

# Usage
logger = TimeLogger()
logger.log("Application started")
logger.log("User login", {"user_id": 123})
logger.log("Database query", {"query_time_ms": 45})
```

### 3. Network Latency Tester

```python
from hixbe_time import NTPClient, NTPClientConfig

class NetworkLatencyTester:
    def __init__(self):
        self.servers = [
            'time.hixbe.com',
            'time.google.com',
            'time.cloudflare.com',
            'pool.ntp.org',
        ]
    
    def test_latency(self, server, samples=5):
        """Test network latency to NTP server"""
        config = NTPClientConfig(host=server, timeout=5.0)
        client = NTPClient(config)
        
        latencies = []
        
        for i in range(samples):
            try:
                result = client.query_sync()
                
                t0 = result.client_originate_time
                t3 = result.client_receive_time
                
                # Calculate round-trip time
                rtt = (t3 - t0).total_seconds() * 1000
                latencies.append(rtt)
            except Exception as e:
                print(f"  Sample {i+1}: Failed - {e}")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            return {
                'server': server,
                'samples': len(latencies),
                'avg_ms': avg_latency,
                'min_ms': min_latency,
                'max_ms': max_latency
            }
        return None
    
    def run_tests(self):
        """Test all servers"""
        print("Testing network latency to NTP servers...\n")
        
        results = []
        for server in self.servers:
            print(f"Testing {server}...")
            result = self.test_latency(server)
            if result:
                results.append(result)
                print(f"  Average: {result['avg_ms']:.2f}ms")
                print(f"  Min: {result['min_ms']:.2f}ms")
                print(f"  Max: {result['max_ms']:.2f}ms\n")
        
        # Find fastest server
        if results:
            fastest = min(results, key=lambda x: x['avg_ms'])
            print(f"Fastest server: {fastest['server']} ({fastest['avg_ms']:.2f}ms)")

# Run latency tests
if __name__ == '__main__':
    tester = NetworkLatencyTester()
    tester.run_tests()
```

### 4. Time Service with Caching

```python
from datetime import datetime, timedelta
from hixbe_time import NTPClient

class CachedTimeService:
    def __init__(self, cache_duration_seconds=60):
        self.client = NTPClient()
        self.cache_duration = timedelta(seconds=cache_duration_seconds)
        self.cached_offset = None
        self.last_update = None
    
    def get_offset(self, force_refresh=False):
        """Get time offset with caching"""
        now = datetime.now()
        
        if (force_refresh or 
            self.cached_offset is None or 
            self.last_update is None or 
            now - self.last_update > self.cache_duration):
            
            try:
                self.cached_offset = self.client.get_offset()
                self.last_update = now
                print(f"Updated offset from NTP server: {self.cached_offset:+.0f}ms")
            except Exception as e:
                print(f"Failed to update offset: {e}")
                if self.cached_offset is None:
                    raise
        
        return self.cached_offset
    
    def get_corrected_time(self):
        """Get current time corrected with NTP offset"""
        offset_ms = self.get_offset()
        local_time = datetime.now()
        corrected_time = local_time + timedelta(milliseconds=offset_ms)
        return corrected_time

# Usage
service = CachedTimeService(cache_duration_seconds=30)

for i in range(10):
    corrected_time = service.get_corrected_time()
    print(f"Corrected time: {corrected_time.isoformat()}")
    import time
    time.sleep(5)
```

## Error Handling Examples

### Graceful Degradation

```python
from hixbe_time import NTPClient, NTPClientConfig
from datetime import datetime

def get_reliable_time():
    """Get time with fallback to local time"""
    try:
        client = NTPClient()
        return client.get_time(), True  # NTP time, synchronized
    except Exception as e:
        print(f"Warning: Using local time (NTP failed: {e})")
        return datetime.now(), False  # Local time, not synchronized

time, is_synced = get_reliable_time()
print(f"Time: {time} (Synchronized: {is_synced})")
```

### Retry Logic

```python
import time
from hixbe_time import NTPClient

def query_with_retry(max_attempts=3, delay=2):
    """Query NTP with retry logic"""
    client = NTPClient()
    
    for attempt in range(max_attempts):
        try:
            result = client.query_sync()
            print(f"Success on attempt {attempt + 1}")
            return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
    
    raise Exception(f"All {max_attempts} attempts failed")

try:
    result = query_with_retry()
    print(f"Time: {result.parsed.timestamps.transmit.iso}")
except Exception as e:
    print(f"Could not get NTP time: {e}")
```

## Performance Testing

```python
import time
from hixbe_time import NTPClient

def benchmark_queries(count=10):
    """Benchmark NTP query performance"""
    client = NTPClient()
    times = []
    
    print(f"Running {count} queries...")
    
    for i in range(count):
        start = time.time()
        try:
            result = client.query_sync()
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  Query {i+1}: {elapsed*1000:.2f}ms")
        except Exception as e:
            print(f"  Query {i+1}: Failed - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\nResults:")
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  Min: {min_time*1000:.2f}ms")
        print(f"  Max: {max_time*1000:.2f}ms")
        print(f"  Success rate: {len(times)}/{count}")

if __name__ == '__main__':
    benchmark_queries(10)
```
