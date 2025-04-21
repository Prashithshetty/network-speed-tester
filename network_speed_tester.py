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

    