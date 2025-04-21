import argparse
import socket
import time
import threading
import random
import sys
import statistics

# Default settings
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5000
DEFAULT_BUFFER_SIZE = 8192  # 8KB buffer
DEFAULT_DATA_SIZE = 10 * 1024 * 1024  # 10MB default test size
DEFAULT_TIMEOUT = 10  # seconds
DEFAULT_UDP_PACKETS = 1000

class NetworkSpeedTester:
    
    
    def __init__(self, host: str, port: int, buffer_size: int, data_size: int,
                 timeout: int, protocol: str = 'tcp', verbose: bool = False):
       
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.data_size = data_size
        self.timeout = timeout
        self.protocol = protocol.lower()
        self.verbose = verbose
        self.stop_event = threading.Event()
    
    def _generate_test_data(self, size: int) -> bytes:
        return bytes(random.getrandbits(8) for _ in range(size))
    
    def start_server(self) -> None:
       
        if self.protocol == 'tcp':
            self._start_tcp_server()
        else:
            self._start_udp_server()

    def _start_tcp_server(self) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        server_socket.settimeout(self.timeout)
        
        print(f"TCP Server started on {self.host}:{self.port}")
        
        try:
            while not self.stop_event.is_set():
                try:
                    client_socket, address = server_socket.accept()
                    print(f"Connection from {address}")
                    
                    client_socket.settimeout(self.timeout)
                    
                    self._handle_tcp_client(client_socket)
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            server_socket.close()
    
    def _handle_tcp_client(self, client_socket: socket.socket) -> None:
        try:
            test_type = client_socket.recv(16).decode('utf-8').strip()
            
            if test_type == 'upload':
                if self.verbose:
                    print("Starting upload test (receiving data)...")
                
                total_received = 0
                start_time = time.time()
                
                while True:
                    data = client_socket.recv(self.buffer_size)
                    if not data:
                        break
                    total_received += len(data)
                
                end_time = time.time()
                duration = end_time - start_time
                
                if self.verbose:
                    print(f"Received {total_received} bytes in {duration:.2f} seconds")
                
                response = f"STATS:{total_received}:{duration}"
                client_socket.sendall(response.encode('utf-8'))
                
            elif test_type == 'download':
                if self.verbose:
                    print("Starting download test (sending data)...")
                
                test_data = self._generate_test_data(self.buffer_size)
                remaining = self.data_size
                
                start_time = time.time()
                
                while remaining > 0 and not self.stop_event.is_set():
                    chunk_size = min(remaining, self.buffer_size)
                    client_socket.sendall(test_data[:chunk_size])
                    remaining -= chunk_size
                
                end_time = time.time()
                duration = end_time - start_time
                
                if self.verbose:
                    print(f"Sent {self.data_size} bytes in {duration:.2f} seconds")
                
                response = f"STATS:{self.data_size}:{duration}"
                client_socket.sendall(response.encode('utf-8'))
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()



    def _start_udp_server(self) -> None:
        """Start UDP server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.host, self.port))
        server_socket.settimeout(1.0)  
        
        print(f"UDP Server started on {self.host}:{self.port}")
        
        packet_times = {}
        
        try:
            while not self.stop_event.is_set():
                try:
                    data, addr = server_socket.recvfrom(self.buffer_size)
                    
                    if data.startswith(b'START:'):
                        
                        test_type = data.decode('utf-8').split(':')[1]
                        if self.verbose:
                            print(f"Starting UDP {test_type} test with {addr}")
                        
                        
                        packet_times = {}
                        
                       
                        server_socket.sendto(b'READY', addr)
                        
                    elif data.startswith(b'SEQ:'):
                       
                        parts = data.decode('utf-8').split(':')
                        seq_num = int(parts[1])
                        client_time = float(parts[2])
                        
                        
                        packet_times[seq_num] = {
                            'client_time': client_time,
                            'server_time': time.time()
                        }
                        
                        
                        response = f"ACK:{seq_num}:{time.time()}"
                        server_socket.sendto(response.encode('utf-8'), addr)
                        
                    elif data.startswith(b'END'):
                        
                        if self.verbose:
                            print(f"UDP test complete, received {len(packet_times)} packets")
                        
                        
                        results = f"RESULTS:{len(packet_times)}"
                        server_socket.sendto(results.encode('utf-8'), addr)
                    
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("UDP server stopping...")
        finally:
            server_socket.close()

    def run_client_test(self, test_type: str) -> Tuple[float, float, int]:
        
        if self.protocol == 'tcp':
            return self._run_tcp_client_test(test_type)
        else:
            return self._run_udp_client_test(test_type)
        
    def _run_tcp_client_test(self, test_type: str) -> Tuple[float, float, int]:
        """Run a TCP client speed test"""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(self.timeout)
        
        try:
            client_socket.connect((self.host, self.port))
            
           
            client_socket.sendall(test_type.encode('utf-8'))
            
            if test_type == 'upload':
               
                if self.verbose:
                    print(f"Starting upload test to {self.host}:{self.port}...")
                
                
                test_data = self._generate_test_data(self.buffer_size)
                remaining = self.data_size
                
                start_time = time.time()
                
                while remaining > 0:
                    chunk_size = min(remaining, self.buffer_size)
                    client_socket.sendall(test_data[:chunk_size])
                    remaining -= chunk_size
                
                
                response = client_socket.recv(1024).decode('utf-8')
                if response.startswith('STATS:'):
                    _, bytes_sent, duration = response.split(':')
                    bytes_sent = int(bytes_sent)
                    duration = float(duration)
                else:
                 
                    end_time = time.time()
                    duration = end_time - start_time
                    bytes_sent = self.data_size
                
            elif test_type == 'download':
                
                if self.verbose:
                    print(f"Starting download test from {self.host}:{self.port}...")
                
                total_received = 0
                start_time = time.time()
                
                while True:
                    data = client_socket.recv(self.buffer_size)
                    if not data or data.startswith(b'STATS:'):
                        break
                    total_received += len(data)
                
                
                if data and data.startswith(b'STATS:'):
                    try:
                        _, bytes_received, server_duration = data.decode('utf-8').split(':')
                        bytes_received = int(bytes_received)
                        server_duration = float(server_duration)
                        
                        total_received = bytes_received
                        duration = server_duration
                    except:
                       
                        end_time = time.time()
                        duration = end_time - start_time
                else:
                    
                    end_time = time.time()
                    duration = end_time - start_time
                
                bytes_sent = total_received
            
            
            speed_mbps = (bytes_sent * 8) / (1024 * 1024 * duration)
            
            return speed_mbps, duration, bytes_sent
            
        except Exception as e:
            print(f"Error during {test_type} test: {e}")
            return 0.0, 0.0, 0
        finally:
            client_socket.close()

    def _run_udp_client_test(self, test_type: str) -> Tuple[float, float, int, dict]:
       
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(self.timeout)
        
        try:
            
            start_msg = f"START:{test_type}"
            client_socket.sendto(start_msg.encode('utf-8'), (self.host, self.port))
            
            
            try:
                data, _ = client_socket.recvfrom(1024)
                if data != b'READY':
                    print("Did not receive ready signal from server")
                    return 0.0, 0.0, 0, {}
            except socket.timeout:
                print("Timed out waiting for server ready signal")
                return 0.0, 0.0, 0, {}
            
            if self.verbose:
                print(f"Starting UDP {test_type} test with {self.host}:{self.port}")
            
            
            packet_size = 1024  
            num_packets = min(DEFAULT_UDP_PACKETS, self.data_size // packet_size)
            sent_times = {}
            received_times = {}
            
            start_time = time.time()
            
            for i in range(num_packets):
                
                now = time.time()
                packet = f"SEQ:{i}:{now}"
                client_socket.sendto(packet.encode('utf-8'), (self.host, self.port))
                sent_times[i] = now
                
                
                if i % 50 == 0 and i > 0:
                    time.sleep(0.01)
            
        
            client_socket.settimeout(0.5)  
            
            for _ in range(num_packets):
                try:
                    data, _ = client_socket.recvfrom(1024)
                    if data.startswith(b'ACK:'):
                        parts = data.decode('utf-8').split(':')
                        seq_num = int(parts[1])
                        server_time = float(parts[2])
                        receive_time = time.time()
                        
                        received_times[seq_num] = {
                            'server_time': server_time,
                            'receive_time': receive_time
                        }
                except socket.timeout:
                    continue
            
            end_time = time.time()
            duration = end_time - start_time
            
            
            client_socket.sendto(b'END', (self.host, self.port))
            
            
            packets_sent = num_packets
            packets_received = len(received_times)
            bytes_sent = packets_sent * packet_size
            bytes_received = packets_received * packet_size
            
           
            packet_loss = (1 - packets_received / packets_sent) * 100 if packets_sent > 0 else 0
            
           
            rtts = []
            for seq_num in received_times:
                if seq_num in sent_times:
                    rtt = received_times[seq_num]['receive_time'] - sent_times[seq_num]
                    rtts.append(rtt)
            
            
            jitter = statistics.stdev(rtts) * 1000 if len(rtts) > 1 else 0  # in ms
            
            
            speed_mbps = (bytes_sent * 8) / (1024 * 1024 * duration) if duration > 0 else 0
            
            stats = {
                'packet_loss': packet_loss,
                'min_rtt': min(rtts) * 1000 if rtts else 0,  # ms
                'max_rtt': max(rtts) * 1000 if rtts else 0,  # ms
                'avg_rtt': statistics.mean(rtts) * 1000 if rtts else 0,  # ms
                'jitter': jitter,  # ms
                'packets_sent': packets_sent,
                'packets_received': packets_received
            }
            
            return speed_mbps, duration, bytes_sent, stats
            
        except Exception as e:
            print(f"Error during UDP {test_type} test: {e}")
            return 0.0, 0.0, 0, {}
        finally:
            client_socket.close()

def format_size(size_bytes: int) -> str:
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"
    
def main():
    
    parser = argparse.ArgumentParser(description='Network Speed Tester')
    
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('-s', '--server', action='store_true', help='Run in server mode')
    mode_group.add_argument('-c', '--client', action='store_true', help='Run in client mode')
    
  
    parser.add_argument('-H', '--host', default=DEFAULT_HOST, help=f'Host address (default: {DEFAULT_HOST})')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help=f'Port number (default: {DEFAULT_PORT})')
    parser.add_argument('-b', '--buffer', type=int, default=DEFAULT_BUFFER_SIZE, help=f'Buffer size in bytes (default: {DEFAULT_BUFFER_SIZE})')
    parser.add_argument('-d', '--data-size', type=int, default=DEFAULT_DATA_SIZE, help=f'Data size in bytes (default: {format_size(DEFAULT_DATA_SIZE)})')
    parser.add_argument('-t', '--timeout', type=int, default=DEFAULT_TIMEOUT, help=f'Timeout in seconds (default: {DEFAULT_TIMEOUT})')
    parser.add_argument('-P', '--protocol', choices=['tcp', 'udp'], default='tcp', help='Protocol to use (default: tcp)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
   
    client_group = parser.add_argument_group('Client options')
    client_group.add_argument('--download', action='store_true', help='Test download speed')
    client_group.add_argument('--upload', action='store_true', help='Test upload speed')
    client_group.add_argument('--both', action='store_true', help='Test both download and upload speeds')
    
    args = parser.parse_args()
    
    
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
            
            tester.start_server()
        elif args.client:
            
            if not (args.download or args.upload or args.both):
               
                args.both = True
            
            print(f"Connecting to {args.host}:{args.port} using {args.protocol.upper()}...")
            
            if args.download or args.both:
                print(f"\nTesting download speed...")
                if args.protocol == 'tcp':
                    speed, duration, bytes_received = tester.run_client_test('download')
                    print(f"Download speed: {speed:.2f} Mbps")
                    print(f"Data received: {format_size(bytes_received)}")
                    print(f"Duration: {duration:.2f} seconds")
                else:
                    speed, duration, bytes_received, stats = tester.run_client_test('download')
                    print(f"Download speed: {speed:.2f} Mbps")
                    print(f"Data received: {format_size(bytes_received)}")
                    print(f"Duration: {duration:.2f} seconds")
                    print(f"Packet loss: {stats['packet_loss']:.2f}%")
                    print(f"Average RTT: {stats['avg_rtt']:.2f} ms")
                    print(f"Jitter: {stats['jitter']:.2f} ms")
            
            if args.upload or args.both:
                print(f"\nTesting upload speed...")
                if args.protocol == 'tcp':
                    speed, duration, bytes_sent = tester.run_client_test('upload')
                    print(f"Upload speed: {speed:.2f} Mbps")
                    print(f"Data sent: {format_size(bytes_sent)}")
                    print(f"Duration: {duration:.2f} seconds")
                else:
                    speed, duration, bytes_sent, stats = tester.run_client_test('upload')
                    print(f"Upload speed: {speed:.2f} Mbps")
                    print(f"Data sent: {format_size(bytes_sent)}")
                    print(f"Duration: {duration:.2f} seconds")
                    print(f"Packet loss: {stats['packet_loss']:.2f}%")
                    print(f"Average RTT: {stats['avg_rtt']:.2f} ms")
                    print(f"Jitter: {stats['jitter']:.2f} ms")
                
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()