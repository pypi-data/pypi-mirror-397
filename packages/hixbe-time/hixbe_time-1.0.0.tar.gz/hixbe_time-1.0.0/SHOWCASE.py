"""Showcase examples for hixbe-time package"""

from hixbe_time import NTPClient, NTPClientConfig
import time
import json

def example_basic():
    """Example 1: Basic time query"""
    print("=" * 70)
    print("Example 1: Basic Time Query")
    print("=" * 70)
    
    client = NTPClient()
    server_time = client.get_time()
    print(f"Server time: {server_time}")
    print(f"ISO format: {server_time.isoformat()}")
    print()


def example_offset():
    """Example 2: Check time offset"""
    print("=" * 70)
    print("Example 2: Time Offset Check")
    print("=" * 70)
    
    client = NTPClient()
    offset = client.get_offset()
    
    status = "slow" if offset > 0 else "fast"
    print(f"System clock is {status} by {abs(offset):.2f}ms")
    
    if abs(offset) > 1000:
        print("⚠️  WARNING: Clock drift is significant!")
    else:
        print("✅ Clock is well synchronized")
    print()


def example_detailed():
    """Example 3: Detailed query result"""
    print("=" * 70)
    print("Example 3: Detailed Query Result")
    print("=" * 70)
    
    client = NTPClient()
    result = client.query_sync()
    
    print(f"Server: {result.server_address} ({result.used_server})")
    print(f"Stratum: {result.parsed.header.stratum}")
    print(f"Version: {result.parsed.header.version_number}")
    print(f"Precision: 2^{result.parsed.header.precision} seconds")
    print(f"Reference ID: {result.parsed.header.reference_id}")
    print()
    print("Timestamps:")
    print(f"  Reference: {result.parsed.timestamps.reference.iso}")
    print(f"  Originate: {result.parsed.timestamps.originate.iso}")
    print(f"  Receive:   {result.parsed.timestamps.receive.iso}")
    print(f"  Transmit:  {result.parsed.timestamps.transmit.iso}")
    print()


def example_custom_server():
    """Example 4: Query custom server"""
    print("=" * 70)
    print("Example 4: Query Custom Server")
    print("=" * 70)
    
    servers = ['time.hixbe.com', 'time.google.com', 'pool.ntp.org']
    
    for server in servers:
        try:
            config = NTPClientConfig(host=server, timeout=3.0)
            client = NTPClient(config)
            result = client.query_sync()
            
            print(f"✅ {server}:")
            print(f"   Time: {result.parsed.timestamps.transmit.iso}")
            print(f"   Stratum: {result.parsed.header.stratum}")
        except Exception as e:
            print(f"❌ {server}: {e}")
    print()


def example_continuous():
    """Example 5: Continuous monitoring (5 iterations)"""
    print("=" * 70)
    print("Example 5: Continuous Monitoring")
    print("=" * 70)
    
    client = NTPClient()
    
    for i in range(5):
        try:
            result = client.query_sync()
            offset = client.get_offset()
            server_time = result.parsed.timestamps.transmit.date
            
            print(f"[{i+1}] {server_time.isoformat()} | Offset: {offset:+.0f}ms")
        except Exception as e:
            print(f"[{i+1}] Error: {e}")
        
        if i < 4:  # Don't sleep on last iteration
            time.sleep(2)
    print()


def example_json_output():
    """Example 6: JSON output"""
    print("=" * 70)
    print("Example 6: JSON Output")
    print("=" * 70)
    
    client = NTPClient()
    result = client.query_sync()
    
    server_time = result.parsed.timestamps.transmit.date
    offset = client.get_offset()
    
    output = {
        'timestamp': int(server_time.timestamp() * 1000),
        'iso': server_time.isoformat(),
        'server': {
            'address': result.server_address,
            'hostname': result.used_server,
            'stratum': result.parsed.header.stratum,
            'referenceId': result.parsed.header.reference_id,
        },
        'offset': round(offset, 2),
        'precision': result.parsed.header.precision,
        'version': result.parsed.header.version_number,
    }
    
    print(json.dumps(output, indent=2))
    print()


def example_error_handling():
    """Example 7: Error handling with fallback"""
    print("=" * 70)
    print("Example 7: Error Handling with Fallback")
    print("=" * 70)
    
    # Try with invalid server first, will fallback automatically
    config = NTPClientConfig(
        host='invalid.server.example',
        fallback_servers=['time.hixbe.com', 'time.google.com']
    )
    client = NTPClient(config)
    
    try:
        result = client.query_sync()
        print(f"✅ Successfully connected to: {result.used_server}")
        print(f"   Time: {result.parsed.timestamps.transmit.iso}")
    except Exception as e:
        print(f"❌ All servers failed: {e}")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "HIXBE TIME SHOWCASE" + " " * 29 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    examples = [
        example_basic,
        example_offset,
        example_detailed,
        example_custom_server,
        example_continuous,
        example_json_output,
        example_error_handling,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Example failed: {e}\n")
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == '__main__':
    main()
