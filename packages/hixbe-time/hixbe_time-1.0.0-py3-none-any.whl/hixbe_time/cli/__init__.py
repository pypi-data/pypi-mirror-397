#!/usr/bin/env python3
"""
Hixbe Time CLI - Command-line interface for NTP time synchronization
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Optional

from ..core.client import NTPClient, NTPClientConfig, NTPQueryResult


class HixbeTimeCLI:
    """CLI application for Hixbe Time"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog='hixbe-time',
            description='High-precision NTP time synchronization',
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        
        parser.add_argument(
            '-s', '--server',
            default='time.hixbe.com',
            help='NTP server to query (default: time.hixbe.com)',
        )
        
        parser.add_argument(
            '-j', '--json',
            action='store_true',
            help='Output in JSON format',
        )
        
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Verbose output with packet details',
        )
        
        parser.add_argument(
            '-o', '--offset',
            action='store_true',
            help='Show only time offset in milliseconds',
        )
        
        parser.add_argument(
            '-c', '--continuous',
            action='store_true',
            help='Continuous synchronization mode',
        )
        
        parser.add_argument(
            '-i', '--interval',
            type=int,
            default=5000,
            help='Interval for continuous mode in milliseconds (default: 5000)',
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s 1.0.0',
        )
        
        return parser
    
    def run(self, args: Optional[list] = None) -> None:
        """Run the CLI application"""
        parsed_args = self.parser.parse_args(args)
        
        if parsed_args.continuous:
            self._continuous_mode(parsed_args)
        else:
            self._single_query(parsed_args)
    
    def _single_query(self, args: argparse.Namespace) -> None:
        """Execute a single NTP query"""
        try:
            config = NTPClientConfig(host=args.server)
            client = NTPClient(config)
            result = client.query_sync()
            
            if args.json:
                self._output_json(result)
            elif args.offset:
                self._output_offset(result)
            elif args.verbose:
                self._output_verbose(result)
            else:
                self._output_default(result)
        
        except Exception as error:
            self._handle_error(error)
    
    def _continuous_mode(self, args: argparse.Namespace) -> None:
        """Continuous synchronization mode"""
        interval_seconds = args.interval / 1000
        count = 0
        
        print(f'⏱️  Starting continuous sync (will fallback to time.google.com if needed)')
        print(f'📊 Interval: {args.interval}ms ({interval_seconds:.1f}s)')
        print('Press Ctrl+C to stop\n')
        
        try:
            while True:
                count += 1
                try:
                    config = NTPClientConfig(host=args.server)
                    client = NTPClient(config)
                    result = client.query_sync()
                    
                    server_time = result.parsed.timestamps.transmit.date
                    local_time = result.client_receive_time
                    offset_ms = (server_time - local_time).total_seconds() * 1000
                    
                    status = '✅'
                    offset_str = f'{offset_ms:+.0f}ms'
                    
                    print(
                        f'[{count}] {status} {server_time.isoformat()} | '
                        f'Offset: {offset_str}'
                    )
                
                except Exception as error:
                    print(f'[{count}] ❌ Error: {error}')
                
                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            print('\n\n✋ Stopped by user')
            sys.exit(0)
    
    def _output_default(self, result: NTPQueryResult) -> None:
        """Default output format"""
        parsed = result.parsed
        server_time = parsed.timestamps.transmit.date
        local_time = result.client_receive_time
        offset_seconds = (server_time - local_time).total_seconds()
        
        print('=' * 70)
        print('🕐 HIXBE TIME SYNC')
        print('=' * 70)
        print()
        print(f'Server:        {result.server_address} ({result.used_server})')
        print(f'UTC Time:      {server_time.isoformat()}')
        print(f'Local Time:    {parsed.timestamps.transmit.local}')
        print(f'Offset:        {offset_seconds:+.3f} seconds')
        print(f'Precision:     ±{parsed.header.precision} (2^x sec)')
        print(f'Stratum:       {parsed.header.stratum}')
        print('=' * 70)
    
    def _output_json(self, result: NTPQueryResult) -> None:
        """JSON output format"""
        parsed = result.parsed
        server_time = parsed.timestamps.transmit.date
        local_time = result.client_receive_time
        offset_ms = (server_time - local_time).total_seconds() * 1000
        
        output = {
            'timestamp': int(server_time.timestamp() * 1000),
            'iso': server_time.isoformat(),
            'server': {
                'address': result.server_address,
                'stratum': parsed.header.stratum,
                'referenceId': parsed.header.reference_id,
            },
            'offset': int(offset_ms),
            'precision': parsed.header.precision,
            'version': parsed.header.version_number,
        }
        
        print(json.dumps(output, indent=2))
    
    def _output_offset(self, result: NTPQueryResult) -> None:
        """Output only the offset"""
        server_time = result.parsed.timestamps.transmit.date
        local_time = result.client_receive_time
        offset_ms = (server_time - local_time).total_seconds() * 1000
        print(f'{offset_ms:+.0f}')
    
    def _output_verbose(self, result: NTPQueryResult) -> None:
        """Verbose output with packet details"""
        parsed = result.parsed
        
        print('=' * 71)
        print('🕐 HIXBE TIME - DETAILED REPORT')
        print('=' * 71)
        print()
        print('📡 TIMESTAMPS:')
        print(f'  Reference: {parsed.timestamps.reference.iso}')
        print(f'  Transmit:  {parsed.timestamps.transmit.iso}')
        print(f'  Receive:   {parsed.timestamps.receive.iso}')
        print()
        
        # Raw transmit timestamp (bytes 40-47)
        raw = parsed.timestamps.transmit.raw
        print('💾 RAW TRANSMIT TIMESTAMP (Bytes 40-47):')
        print(f'  Hex: {raw.seconds:08X}{raw.fraction:08X}')
        print(f'  Seconds (NTP): {raw.seconds} → Unix: {parsed.timestamps.transmit.unix.seconds}')
        print(f'  Fraction: 0x{raw.fraction:08X} = {parsed.timestamps.transmit.unix.milliseconds:.3f}ms')
        print()
        
        print('📋 PACKET HEADER:')
        print(f'  Leap Indicator: {parsed.header.leap_indicator}')
        print(f'  Version:        {parsed.header.version_number}')
        print(f'  Mode:           {parsed.header.mode}')
        print(f'  Stratum:        {parsed.header.stratum}')
        print(f'  Poll Interval:  2^{parsed.header.poll_interval}')
        print(f'  Precision:      2^{parsed.header.precision}')
        print(f'  Root Delay:     {parsed.header.root_delay / 1000000:.3f} ms')
        print(f'  Root Dispersion: {parsed.header.root_dispersion / 1000000:.3f} ms')
        print(f'  Reference ID:   {parsed.header.reference_id}')
        print()
        
        print('📦 RAW PACKET (HEX):')
        hex_dump = result.hex_dump
        for i in range(0, len(hex_dump), 32):
            print(f'  {hex_dump[i:i+32]}')
        print('=' * 71)
    
    @staticmethod
    def _handle_error(error: Exception) -> None:
        """Handle and display errors"""
        print(f'❌ Error: {error}', file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point"""
    cli = HixbeTimeCLI()
    cli.run()


if __name__ == '__main__':
    main()
