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
python network_speed_tester.py [-h] (-s | -c) [-H HOST] [-p PORT] [-b BUFFER]
                              [-d DATA_SIZE] [-t TIMEOUT] [-P {tcp,udp}] [-v]
                              [--download] [--upload] [--both]
```

### Running as Server

```bash
# Start TCP server
python network_speed_tester.py -s -P tcp

# Start UDP server
python network_speed_tester.py -s -P udp
```

### Running as Client

```bash
# Test both download and upload using TCP
python network_speed_tester.py -c -H <server_ip> -P tcp --both

# Test only download using UDP
python network_speed_tester.py -c -H <server_ip> -P udp --download

# Test only upload with custom parameters
python network_speed_tester.py -c -H <server_ip> -b 16384 -d 20971520 --upload
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
Connecting to 192.168.1.100:5000 using TCP...

Testing download speed...
Download speed: 94.52 Mbps
Data received: 10.00 MB
Duration: 0.85 seconds

Testing upload speed...
Upload speed: 89.76 Mbps
Data sent: 10.00 MB
Duration: 0.89 seconds
```

### UDP Test
```
Connecting to 192.168.1.100:5000 using UDP...

Testing download speed...
Download speed: 85.24 Mbps
Data received: 10.00 MB
Duration: 0.94 seconds
Packet loss: 0.15%
Average RTT: 2.45 ms
Jitter: 0.32 ms
```

## Performance Considerations

- **Buffer Size**: Larger buffer sizes may improve performance but consume more memory
- **Data Size**: Larger data sizes provide more accurate results but take longer to complete
- **Protocol Choice**:
  - TCP: Reliable, ordered delivery with built-in congestion control
  - UDP: Faster but unreliable, better for real-time applications

## Limitations

- Single-threaded operation
- No encryption for data transfer
- Basic error handling
- UDP packet size limited to 1024 bytes

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.
