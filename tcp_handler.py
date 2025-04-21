import socket
import time
import random
from typing import Tuple

class TCPHandler:
    def __init__(self, host: str, port: int, buffer_size: int, data_size: int,
                 timeout: int, verbose: bool = False):
        """
        Initialize TCP Handler.
        
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

    def _generate_test_data(self, size: int) -> bytes:
        """Generate random test data."""
        return bytes(random.getrandbits(8) for _ in range(size))

    def start_server(self) -> None:
        """Start TCP server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        server_socket.settimeout(self.timeout)
        
        print(f"TCP Server started on {self.host}:{self.port}")
        
        try:
            while True:
                try:
                    client_socket, address = server_socket.accept()
                    print(f"Connection from {address}")
                    
                    client_socket.settimeout(self.timeout)
                    self._handle_client(client_socket)
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    break
        finally:
            server_socket.close()

    def _handle_client(self, client_socket: socket.socket) -> None:
        """Handle TCP client connection."""
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
                
                while remaining > 0:
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

    def run_client_test(self, test_type: str) -> Tuple[float, float, int]:
        """
        Run TCP client speed test.
        
        Args:
            test_type (str): Type of test ('upload' or 'download')
            
        Returns:
            Tuple[float, float, int]: Speed in Mbps, duration in seconds, bytes transferred
        """
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
                
                # Set a shorter timeout for receiving the response
                client_socket.settimeout(2)
                try:
                    response = client_socket.recv(1024).decode('utf-8')
                    if response.startswith('STATS:'):
                        _, bytes_sent, duration = response.split(':')
                        bytes_sent = int(bytes_sent)
                        duration = float(duration)
                    else:
                        end_time = time.time()
                        duration = end_time - start_time
                        bytes_sent = self.data_size
                except socket.timeout:
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
