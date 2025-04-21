# Network Speed Tester

[![GitHub Repository](https://img.shields.io/badge/GitHub-network--speed--tester-blue?style=flat&logo=github)](https://github.com/Prashithshetty/network-speed-tester)

A versatile Python-based network speed testing tool that supports both TCP and UDP protocols for measuring network performance metrics including download speed, upload speed, packet loss, RTT (Round Trip Time), and jitter.

## Features

- **Dual Protocol Support**: TCP and UDP testing capabilities
- **Flexible Operation Modes**: Run as either server or client
- **Comprehensive Testing**: Measure both download and upload speeds
- **Detailed Statistics**: 
  - Transfer speeds in Mbps
  - Data transfer amounts
  - Test duration
  - UDP-specific metrics (packet loss, RTT, jitter)
- **Configurable Parameters**: Customize buffer size, data size, timeout, and more
- **Modular Architecture**: Well-organized code structure for better maintainability

## Project Structure

The project is organized into several modules:

- `main.py` - Entry point and command-line interface
- `network_tester.py` - Main NetworkSpeedTester class
- `tcp_handler.py` - TCP protocol implementation
- `udp_handler.py` - UDP protocol implementation
- `config.py` - Default settings and configurations
- `utils.py` - Utility functions

This modular structure makes the code more maintainable and easier to extend.

## Requirements

- Python 3.x
- Standard Python libraries (no external dependencies)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Prashithshetty/network-speed-tester.git
   cd network-speed-tester
   ```
2. Ensure you have Python 3.x installed
3. No additional package installation required

## Usage

### Basic Command Structure

```bash
python main.py [-h] (-s | -c) [-H HOST] [-p PORT] [-b BUFFER]
               [-d DATA_SIZE] [-t TIMEOUT] [-P {tcp,udp}] [-v]
               [--download] [--upload] [--both]
```

### Running as Server

```bash
# Start TCP server
python main.py -s -P tcp

# Start UDP server
python main.py -s -P udp
```

### Running as Client

```bash
# Test both download and upload using TCP
python main.py -c -H <server_ip> -P tcp --both

# Test only download using UDP
python main.py -c -H <server_ip> -P udp --download

# Test only upload with custom parameters
python main.py -c -H <server_ip> -b 16384 -d 20971520 --upload
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-s, --server` | Run in server mode | - |
| `-c, --client` | Run in client mode | - |
| `-H, --host` | Host address | 127.0.0.1 |
| `-p, --port` | Port number | 5000 |
| `-b, --buffer` | Buffer size in bytes | 8192 |
| `-d, --data-size` | Data size in bytes | 10MB |
| `-t, --timeout` | Timeout in seconds | 10 |
| `-P, --protocol` | Protocol (tcp/udp) | tcp |
| `-v, --verbose` | Verbose output | False |
| `--download` | Test download speed | - |
| `--upload` | Test upload speed | - |
| `--both` | Test both speeds | - |

## Example Output

### TCP Test
```
Connecting to 127.0.0.1:5000 using TCP...

Testing download speed...
Download speed: 1973.94 Mbps
Data received: 10.00 MB
Duration: 0.04 seconds

Testing upload speed...
Upload speed: 38.79 Mbps
Data sent: 10.00 MB
Duration: 2.06 seconds
```

### UDP Test
```
Connecting to 127.0.0.1:5000 using UDP...

Testing download speed...
Download speed: 33.27 Mbps
Data received: 1000.00 KB
Duration: 0.23 seconds
Packet loss: 0.00%
Average RTT: 117.30 ms
Jitter: 66.24 ms

Testing upload speed...
Upload speed: 34.39 Mbps
Data sent: 1000.00 KB
Duration: 0.23 seconds
Packet loss: 0.00%
Average RTT: 114.34 ms
Jitter: 64.23 ms
```

## Performance Considerations

- **Buffer Size**: Larger buffer sizes may improve performance but consume more memory
- **Data Size**: 
  - TCP: Uses 10MB of test data for accurate throughput measurement
  - UDP: Uses 1MB (1000 packets) to balance speed and reliability
- **Protocol Choice**:
  - TCP: Reliable, ordered delivery with built-in congestion control
  - UDP: Faster but unreliable, better for real-time applications and latency testing

## Limitations

- Single-threaded operation
- No encryption for data transfer
- Basic error handling
- UDP packet size limited to 1024 bytes

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.
