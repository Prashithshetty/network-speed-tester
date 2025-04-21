import argparse
import sys

from config import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_BUFFER_SIZE,
    DEFAULT_DATA_SIZE,
    DEFAULT_TIMEOUT
)
from network_tester import NetworkSpeedTester
from utils import format_size

def main():
    """Main entry point for the network speed tester."""
    parser = argparse.ArgumentParser(description='Network Speed Tester')
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('-s', '--server', action='store_true', help='Run in server mode')
    mode_group.add_argument('-c', '--client', action='store_true', help='Run in client mode')
    
    # Network settings
    parser.add_argument('-H', '--host', default=DEFAULT_HOST, help=f'Host address (default: {DEFAULT_HOST})')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help=f'Port number (default: {DEFAULT_PORT})')
    parser.add_argument('-b', '--buffer', type=int, default=DEFAULT_BUFFER_SIZE, help=f'Buffer size in bytes (default: {DEFAULT_BUFFER_SIZE})')
    parser.add_argument('-d', '--data-size', type=int, default=DEFAULT_DATA_SIZE, help=f'Data size in bytes (default: {format_size(DEFAULT_DATA_SIZE)})')
    parser.add_argument('-t', '--timeout', type=int, default=DEFAULT_TIMEOUT, help=f'Timeout in seconds (default: {DEFAULT_TIMEOUT})')
    parser.add_argument('-P', '--protocol', choices=['tcp', 'udp'], default='tcp', help='Protocol to use (default: tcp)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Client options
    client_group = parser.add_argument_group('Client options')
    client_group.add_argument('--download', action='store_true', help='Test download speed')
    client_group.add_argument('--upload', action='store_true', help='Test upload speed')
    client_group.add_argument('--both', action='store_true', help='Test both download and upload speeds')
    
    args = parser.parse_args()
    
    # Initialize the speed tester
    tester = NetworkSpeedTester(
        host=args.host,
        port=args.port,
        buffer_size=args.buffer,
        data_size=args.data_size,
        timeout=args.timeout,
        protocol=args.protocol,
        verbose=args.verbose
    )
    
    try:
        if args.server:
            # Start server mode
            tester.start_server()
        elif args.client:
            # If no specific test type is selected, test both
            if not (args.download or args.upload or args.both):
                args.both = True
            
            print(f"Connecting to {args.host}:{args.port} using {args.protocol.upper()}...")
            
            # Run download test
            if args.download or args.both:
                print(f"\nTesting download speed...")
                speed, duration, bytes_received, stats = tester.run_client_test('download')
                print(f"Download speed: {speed:.2f} Mbps")
                print(f"Data received: {format_size(bytes_received)}")
                print(f"Duration: {duration:.2f} seconds")
                
                # Print UDP-specific statistics if available
                if stats:
                    print(f"Packet loss: {stats['packet_loss']:.2f}%")
                    print(f"Average RTT: {stats['avg_rtt']:.2f} ms")
                    print(f"Jitter: {stats['jitter']:.2f} ms")
            
            # Run upload test
            if args.upload or args.both:
                print(f"\nTesting upload speed...")
                speed, duration, bytes_sent, stats = tester.run_client_test('upload')
                print(f"Upload speed: {speed:.2f} Mbps")
                print(f"Data sent: {format_size(bytes_sent)}")
                print(f"Duration: {duration:.2f} seconds")
                
                # Print UDP-specific statistics if available
                if stats:
                    print(f"Packet loss: {stats['packet_loss']:.2f}%")
                    print(f"Average RTT: {stats['avg_rtt']:.2f} ms")
                    print(f"Jitter: {stats['jitter']:.2f} ms")
                
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
