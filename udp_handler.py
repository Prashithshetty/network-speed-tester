import socket
import time
import random
import statistics
from typing import Tuple, Dict

from config import DEFAULT_UDP_PACKETS

class UDPHandler:
    def __init__(self, host: str, port: int, buffer_size: int, data_size: int,
                 timeout: int, verbose: bool = False):
        """
        Initialize UDP Handler.
        
        Args:
            host (str): Host address
            port (int): Port number
            buffer_size (int): Size of buffer for data transfer
            data_size (int): Total size of data to transfer
            timeout (int): Socket timeout in seconds
            verbose (bool): Enable verbose output
        """
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.data_size = data_size
        self.timeout = timeout
        self.verbose = verbose

    def start_server(self) -> None:
        """Start UDP server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.host, self.port))
        server_socket.settimeout(1.0)
        
        print(f"UDP Server started on {self.host}:{self.port}")
        
        packet_times = {}
        
        try:
            while True:
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
                    break
        finally:
            server_socket.close()

    def run_client_test(self, test_type: str) -> Tuple[float, float, int, Dict]:
        """
        Run UDP client speed test.
        
        Args:
            test_type (str): Type of test ('upload' or 'download')
            
        Returns:
            Tuple[float, float, int, Dict]: Speed in Mbps, duration, bytes sent, statistics
        """
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
