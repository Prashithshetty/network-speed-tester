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
