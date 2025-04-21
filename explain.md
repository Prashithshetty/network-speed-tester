# Network Speed Tester - Technical Documentation

## Table of Contents
1. [Program Architecture](#program-architecture)
2. [Network Protocols](#network-protocols)
3. [Speed Testing Methodology](#speed-testing-methodology)
4. [Data Flow](#data-flow)
5. [Error Handling](#error-handling)
6. [Performance Optimization](#performance-optimization)
7. [Testing and Debugging](#testing-and-debugging)

## Program Architecture

### Module Structure
The program follows a modular architecture with clear separation of concerns:

1. **main.py**
   - Entry point of the application
   - Handles command-line argument parsing
   - Initializes the appropriate components
   - Manages the overall flow of the program

2. **network_tester.py**
   - Core class that orchestrates the speed testing
   - Abstracts protocol-specific details
   - Manages test execution and result collection
   - Provides a unified interface for both TCP and UDP tests

3. **tcp_handler.py**
   - Implements TCP-specific networking logic
   - Handles reliable data transfer
   - Manages connection-oriented communication
   - Implements TCP speed measurement algorithms

4. **udp_handler.py**
   - Implements UDP-specific networking logic
   - Handles packet-based communication
   - Tracks packet loss and latency
   - Implements jitter calculation

5. **config.py**
   - Centralizes configuration settings
   - Defines default values
   - Makes the program easily configurable

6. **utils.py**
   - Contains utility functions
   - Handles data formatting
   - Provides helper methods

### Class Hierarchy
```
NetworkSpeedTester
├── TCPHandler
│   ├── start_server()
│   ├── run_client_test()
│   └── _handle_client()
└── UDPHandler
    ├── start_server()
    ├── run_client_test()
    └── _calculate_statistics()
```

## Network Protocols

### TCP Implementation
The TCP implementation focuses on reliable, ordered data transfer:

1. **Connection Handling**
   ```python
   server_socket.listen(1)
   client_socket, address = server_socket.accept()
   ```
   - Creates a listening socket
   - Accepts incoming connections
   - Maintains connection state

2. **Data Transfer**
   ```python
   while remaining > 0:
       chunk_size = min(remaining, self.buffer_size)
       client_socket.sendall(test_data[:chunk_size])
       remaining -= chunk_size
   ```
   - Uses buffered sending
   - Ensures complete data transfer
   - Handles large datasets efficiently

3. **Speed Calculation**
   ```python
   speed_mbps = (bytes_sent * 8) / (1024 * 1024 * duration)
   ```
   - Measures actual data throughput
   - Accounts for transfer time
   - Converts to Mbps

### UDP Implementation
The UDP implementation focuses on real-time performance metrics:

1. **Packet Management**
   ```python
   packet = f"SEQ:{i}:{now}"
   client_socket.sendto(packet.encode('utf-8'), (self.host, self.port))
   ```
   - Implements sequence numbers
   - Tracks packet timing
   - Handles packet loss

2. **Statistics Collection**
   ```python
   packet_loss = (1 - packets_received / packets_sent) * 100
   jitter = statistics.stdev(rtts) * 1000  # ms
   ```
   - Calculates packet loss
   - Measures round-trip time
   - Computes jitter

## Speed Testing Methodology

### Test Types

1. **Download Test**
   - Server sends predefined amount of data
   - Client measures received data rate
   - Calculates effective download speed

2. **Upload Test**
   - Client sends predefined amount of data
   - Server measures received data rate
   - Calculates effective upload speed

### Measurement Process

1. **Data Generation**
   ```python
   def _generate_test_data(self, size: int) -> bytes:
       return bytes(random.getrandbits(8) for _ in range(size))
   ```
   - Creates random test data
   - Ensures consistent testing
   - Prevents compression effects

2. **Timing**
   ```python
   start_time = time.time()
   # ... perform test ...
   end_time = time.time()
   duration = end_time - start_time
   ```
   - Precise timing measurements
   - Accounts for total transfer time
   - Handles various test durations

## Data Flow

### Server Mode

1. **Initialization**
   ```python
   server_socket = socket.socket(...)
   server_socket.bind((host, port))
   ```
   - Creates socket
   - Binds to port
   - Prepares for connections

2. **Client Handling**
   ```python
   while True:
       handle_client(client_socket)
   ```
   - Accepts connections
   - Processes requests
   - Manages multiple tests

### Client Mode

1. **Test Request**
   ```python
   client_socket.connect((host, port))
   client_socket.sendall(test_type.encode('utf-8'))
   ```
   - Initiates connection
   - Specifies test type
   - Prepares for data transfer

2. **Result Processing**
   ```python
   speed, duration, bytes_transferred = run_test()
   print_results(speed, duration, bytes_transferred)
   ```
   - Collects metrics
   - Formats results
   - Displays statistics

## Error Handling

### Network Errors
```python
try:
    # network operations
except socket.timeout:
    handle_timeout()
except socket.error as e:
    handle_socket_error(e)
```
- Handles connection timeouts
- Manages network failures
- Provides error feedback

### Data Validation
```python
if not data:
    handle_incomplete_data()
if data.startswith(b'STATS:'):
    process_statistics(data)
```
- Validates received data
- Handles protocol violations
- Ensures data integrity

## Performance Optimization

### Buffer Management
```python
buffer_size = 8192  # 8KB default
chunk_size = min(remaining, buffer_size)
```
- Optimizes memory usage
- Balances throughput
- Prevents overflow

### Protocol-Specific Tuning

1. **TCP Optimization**
   - Uses appropriate buffer sizes
   - Manages connection state
   - Handles continuous data streams

2. **UDP Optimization**
   - Limits packet sizes
   - Implements packet tracking
   - Balances reliability and speed

### Resource Management
```python
try:
    # use resources
finally:
    socket.close()
```
- Proper cleanup
- Resource release
- Memory management

## Testing and Debugging

### Running Tests

1. **Local Testing**
   ```bash
   # Terminal 1 - Start TCP server
   python main.py -s -P tcp -v

   # Terminal 2 - Run TCP client test
   python main.py -c -H localhost -P tcp --both -v
   ```
   - Tests basic functionality
   - Verifies both protocols
   - Checks error handling

2. **Network Testing**
   ```bash
   # Server machine
   python main.py -s -P tcp -H 0.0.0.0

   # Client machine
   python main.py -c -H <server_ip> -P tcp --both
   ```
   - Tests real network conditions
   - Verifies cross-machine communication
   - Measures actual network performance

### Debugging Tips

1. **Verbose Mode**
   ```bash
   python main.py -s -P tcp -v
   ```
   - Enables detailed logging
   - Shows connection events
   - Displays transfer progress

2. **Common Issues**
   - Port already in use: Check for running instances
   - Connection refused: Verify server is running
   - Timeout: Check network connectivity
   - Low speed: Verify buffer sizes and system resources

3. **Performance Analysis**
   - Monitor system resources
   - Check network utilization
   - Analyze timing patterns
   - Review error logs

### Troubleshooting Guide

1. **Connection Issues**
   - Verify server is running
   - Check firewall settings
   - Confirm port availability
   - Test network connectivity

2. **Performance Issues**
   - Adjust buffer sizes
   - Monitor system resources
   - Check network congestion
   - Verify test parameters

3. **Protocol-Specific Issues**
   - TCP: Connection handling, data ordering
   - UDP: Packet loss, jitter calculation
   - Both: Timeout settings, resource usage
