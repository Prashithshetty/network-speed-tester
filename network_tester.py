import threading
from typing import Tuple, Dict, Optional

from tcp_handler import TCPHandler
from udp_handler import UDPHandler

class NetworkSpeedTester:
    def __init__(self, host: str, port: int, buffer_size: int, data_size: int,
                 timeout: int, protocol: str = 'tcp', verbose: bool = False):
        """
        Initialize Network Speed Tester.
        
        Args:
            host (str): Host address
            port (int): Port number
            buffer_size (int): Size of buffer for data transfer
            data_size (int): Total size of data to transfer
            timeout (int): Socket timeout in seconds
            protocol (str): Protocol to use ('tcp' or 'udp')
            verbose (bool): Enable verbose output
        """
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.data_size = data_size
        self.timeout = timeout
        self.protocol = protocol.lower()
        self.verbose = verbose
        self.stop_event = threading.Event()

        # Initialize the appropriate handler based on protocol
        if self.protocol == 'tcp':
            self.handler = TCPHandler(
                host=host,
                port=port,
                buffer_size=buffer_size,
                data_size=data_size,
                timeout=timeout,
                verbose=verbose
            )
        else:
            self.handler = UDPHandler(
                host=host,
                port=port,
                buffer_size=buffer_size,
                data_size=data_size,
                timeout=timeout,
                verbose=verbose
            )

    def start_server(self) -> None:
        """Start the speed test server."""
        try:
            self.handler.start_server()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            self.stop_event.set()

    def run_client_test(self, test_type: str) -> Tuple[float, float, int, Optional[Dict]]:
        """
        Run a client speed test.
        
        Args:
            test_type (str): Type of test ('upload' or 'download')
            
        Returns:
            Tuple containing:
            - float: Speed in Mbps
            - float: Duration in seconds
            - int: Bytes transferred
            - Optional[Dict]: Additional statistics for UDP tests
        """
        if self.protocol == 'tcp':
            speed, duration, bytes_transferred = self.handler.run_client_test(test_type)
            return speed, duration, bytes_transferred, None
        else:
            return self.handler.run_client_test(test_type)
