# OpScaleSrv

A Python HTTP service that reads data from serial ports and provides it via REST API with ABAP integration support.
by Altay Kirecci
opriori (c)(p) 2025-09
https://www.opriori.com
https://github/altaykirecci/opscalesrv
**Since it is in beta stage, the source codes have not been made public yet.**

## Features

- **Serial Port Reading**: Read data from Arduino, sensors, and other serial devices
- **HTTP API**: RESTful API with JSON responses
- **Host-based Access Control**: Configurable IP and port restrictions
- **Comprehensive Logging**: Detailed request logging
- **ABAP Integration**: Ready-to-use ABAP client code
- **Test Mode**: Mock data for development and testing
- **CORS Support**: Cross-origin resource sharing enabled

## Installation

### Method 1: Direct Installation

```bash
pip install opscalesrv
opscalesrv --init
```

### Method 2: Virtual Environment Installation (Recommended)

#### How to Open Terminal

**Windows:**

- **Command Prompt**: Press `Win + R`, type `cmd`, press Enter
- **PowerShell**: Press `Win + X`, select "Windows PowerShell" or "Terminal"
- **Alternative**: Press `Win + R`, type `powershell`, press Enter

**macOS:**

- **Terminal**: Press `Cmd + Space`, type "Terminal", press Enter
- **Alternative**: Go to Applications → Utilities → Terminal
- **Spotlight**: Press `Cmd + Space`, type "Terminal"

**Linux:**

- **Ubuntu/Debian**: Press `Ctrl + Alt + T`
- **CentOS/RHEL**: Press `Ctrl + Alt + T`
- **Alternative**: Press `Alt + F2`, type `gnome-terminal` or `konsole`
- **Menu**: Applications → System Tools → Terminal

#### Installation Steps

**Windows:**

Open Command Prompt or PowerShell and run the following commands:

```cmd
mkdir opscalesrv
cd opscalesrv
python -m venv venv
venv\Scripts\activate
pip install opscalesrv
opscalesrv --init
opscalesrv
```

#### macOS

Open Terminal and run the following commands:

```bash
mkdir opscalesrv
cd opscalesrv
python3 -m venv venv
source venv/bin/activate
pip install opscalesrv
opscalesrv --init
opscalesrv
```

#### Linux

Open Terminal and run the following commands:

```bash
mkdir opscalesrv
cd opscalesrv
python3 -m venv venv
source venv/bin/activate
pip install opscalesrv
opscalesrv --init
opscalesrv
```

### Virtual Environment Benefits

- ✅ **Isolated Environment**: No conflicts with system packages
- ✅ **No Root Access**: No need for sudo/administrator privileges
- ✅ **Easy Cleanup**: Simply delete the folder to remove everything
- ✅ **Version Control**: Use specific package versions without affecting system

### Running OpScaleSrv After Installation

Once you have installed OpScaleSrv using the virtual environment method, you can run it anytime by following these steps:

#### Windows

```cmd
cd opscalesrv
venv\Scripts\activate
opscalesrv
```

**With arguments:**

```cmd
cd opscalesrv
venv\Scripts\activate
opscalesrv --host 0.0.0.0 --port 8080 --log --test
```

#### macOS

```bash
cd opscalesrv
source venv/bin/activate
opscalesrv
```

**With arguments:**

```bash
cd opscalesrv
source venv/bin/activate
opscalesrv --host 0.0.0.0 --port 8080 --log --test
```

#### Linux

```bash
cd opscalesrv
source venv/bin/activate
opscalesrv
```

**With arguments:**

```bash
cd opscalesrv
source venv/bin/activate
opscalesrv --host 0.0.0.0 --port 8080 --log --test
```

### Important Notes

- **Always activate the virtual environment** before running OpScaleSrv
- **Navigate to the opscalesrv directory** first
- **Use the correct activation command** for your operating system
- **Deactivate when done**: Type `deactivate` to exit the virtual environment

## Quick Start

### 1. Basic Usage

```bash
# Copy ABAP files to current directory
opscalesrv --abap

# Initialize/creating configuration file
opscalesrv --init
# Start the server (default: localhost:7373)
opscalesrv

# Start with custom host and port
opscalesrv --host 0.0.0.0 --port 8080

# Run in test mode (returns mock data)
opscalesrv --test

# Start with logging enabled
opscalesrv --log

# Start with all options
opscalesrv --host 0.0.0.0 --port 8080 --log --test
```

### 2. Configuration

#### Method 1: Using --init parameter (Recommended)

```bash
# Create configuration file in current directory
opscalesrv --init

# This will create opscalesrv.json with default settings
# You can then edit it to customize your configuration
```

#### Method 2: Manual creation

Create a `opscalesrv.json` configuration file:

```json
{
  "allowed_hosts": [
    {
      "ip": "127.0.0.1",
      "ports": [7373, 8080],
      "description": "Localhost access"
    },
    {
      "ip": "192.168.1.100",
      "ports": [7373],
      "description": "Local network access"
    }
  ],
  "serial": {
    "port": "/dev/ttyUSB0",
    "baudrate": 9600,
    "timeout": 1,
    "description": "Arduino connection"
  },
  "settings": {
    "log_file": "requests.log",
    "deny_unknown_hosts": true,
    "log_all_requests": true
  }
}
```

### 3. API Usage

#### GET Request

```bash
curl http://localhost:7373/
```

#### POST Request (Not Supported)

POST requests are not supported. Only GET requests are allowed.

```bash
curl -X POST http://localhost:7373/
# Returns: 405 Method Not Allowed
```

#### Response Format

OpScaleSrv 4 farklı response body türü oluşturur:

##### 1. **Test Mode Response** (Test Verisi)

```json
{
  "message": {
    "value": "0",
    "msg": "hello world",
    "mode": "test",
    "result": "OK"
  },
  "timestamp": "2025-01-26T10:30:45.123456",
  "method": "GET",
  "path": "/?test=1",
  "client_ip": "127.0.0.1",
  "client_port": 54321
}
```

**Açıklama**: Test mode aktifken (`--test` parametresi veya `?test=1` URL parametresi) döner. Gerçek serial port kullanılmaz, sabit test verisi döndürülür.

##### 2. **Success Response** (Başarılı Serial Okuma)

```json
{
  "message": {
    "value": "25.5",
    "msg": "Temperature reading successful",
    "mode": "read",
    "result": "OK"
  },
  "timestamp": "2025-01-26T10:30:45.123456",
  "method": "GET",
  "path": "/",
  "client_ip": "127.0.0.1",
  "client_port": 54321
}
```

**Açıklama**: Serial porttan başarıyla veri okunduğunda döner. `value` alanı serial porttan okunan gerçek değeri içerir.

##### 3. **Error Response** (Serial Port Hatası)

```json
{
  "message": {
    "value": "-1",
    "msg": "could not open port '/dev/ttyUSB0': FileNotFoundError(2, 'Sistem belirtilen yolu bulamıyor.', None, 3)",
    "mode": "read",
    "result": "FAIL"
  },
  "timestamp": "2025-01-26T10:30:45.123456",
  "method": "GET",
  "path": "/",
  "client_ip": "127.0.0.1",
  "client_port": 54321
}
```

**Açıklama**: Serial port okuma hatası durumunda döner. `result: "FAIL"` ve `value: "-1"` ile hata durumu belirtilir. `msg` alanı detaylı hata açıklamasını içerir.

##### 4. **Method Not Allowed Response** (POST Hatası)

```json
{
  "error": "Method Not Allowed",
  "message": "Only GET method is supported",
  "allowed_methods": ["GET"],
  "timestamp": "2025-01-26T10:30:45.123456"
}
```

**Açıklama**: POST request gönderildiğinde döner. Sadece GET method'u desteklenir.

#### Response Alanları

| Alan             | Tip     | Açıklama                                                |
| ---------------- | ------- | ------------------------------------------------------- |
| `message.value`  | string  | Serial porttan okunan değer (başarılı) veya "-1" (hata) |
| `message.msg`    | string  | Durum mesajı veya hata açıklaması                       |
| `message.mode`   | string  | "test" (test mode) veya "read" (serial mode)            |
| `message.result` | string  | "OK" (başarılı) veya "FAIL" (hata)                      |
| `timestamp`      | string  | ISO formatında zaman damgası                            |
| `method`         | string  | HTTP metodu ("GET")                                     |
| `path`           | string  | İstek yolu                                              |
| `client_ip`      | string  | İstemci IP adresi                                       |
| `client_port`    | integer | İstemci port numarası                                   |

## ABAP Integration

The package includes ready-to-use ABAP client code in the `abap/` directory.

### ABAP Client Features

- HTTP client integration
- JSON parsing with `/ui2/cl_json`
- Network connectivity testing
- Multiple connection options
- Detailed error handling
- Debug mode with system information
- Response headers analysis
- Object-oriented class-based approach
- Reusable methods for different scenarios

### Available ABAP Files

1. **`serial_service_test.abap`** - Standalone report program
2. **`serial_service_class.abap`** - Reusable class with methods
3. **`serial_class_test.abap`** - Test program using the class methods

### Using ABAP Client

#### Method 1: Using --abap parameter (Recommended)

```bash
# Copy ABAP files to current directory
opscalesrv --abap

# This will copy all ABAP files to your current directory:
# - serial_service_test.abap (standalone report)
# - serial_service_class.abap (reusable class)
# - serial_class_test.abap (test program using the class)
# You can then copy them to your SAP system
```

#### Method 2: Manual extraction

1. Copy the ABAP code from `opscalesrv/abap/` directory
2. Create new ABAP programs/classes in SAP system
3. Paste the code and configure parameters
4. Run the program to test connectivity

### ABAP Program Parameters

- **Host**: Server hostname (default: localhost)
- **Port**: Server port (default: 7373)
- **Test Options**: Multiple connection testing
- **Debug Mode**: System information and network diagnostics

### ABAP Class Usage Examples

#### Using the Reusable Class

```abap
DATA: ls_result TYPE ZAKIR_SERIAL_SERVICE_CLASS=>ty_serial_result,
      lv_value  TYPE string.

" Method 1: Get full result with all details
TRY.
    ls_result = ZAKIR_SERIAL_SERVICE_CLASS=>call_serial_service(
      iv_host = '192.168.1.100'
      iv_port = '7373'
      iv_timeout = 10
    ).
    IF ls_result-success = abap_true.
      WRITE: / 'Value:', ls_result-value,
               / 'Message:', ls_result-message,
               / 'Mode:', ls_result-mode,
               / 'Result:', ls_result-result,
               / 'Timestamp:', ls_result-timestamp.
    ELSE.
      WRITE: / 'Error:', ls_result-error_text.
    ENDIF.
  CATCH ZAKIR_SERIAL_SERVICE_CLASS=>connection_error.
    WRITE: / 'Connection error occurred'.
  CATCH ZAKIR_SERIAL_SERVICE_CLASS=>timeout_error.
    WRITE: / 'Timeout error occurred'.
  CATCH ZAKIR_SERIAL_SERVICE_CLASS=>parse_error.
    WRITE: / 'Parse error occurred'.
ENDTRY.

" Method 2: Get only the serial value
TRY.
    lv_value = ZAKIR_SERIAL_SERVICE_CLASS=>get_serial_value(
      iv_host = '192.168.1.100'
      iv_port = '7373'
    ).
    WRITE: / 'Serial Value:', lv_value.
  CATCH ZAKIR_SERIAL_SERVICE_CLASS=>connection_error.
    WRITE: / 'Connection error occurred'.
  CATCH ZAKIR_SERIAL_SERVICE_CLASS=>timeout_error.
    WRITE: / 'Timeout error occurred'.
  CATCH ZAKIR_SERIAL_SERVICE_CLASS=>parse_error.
    WRITE: / 'Parse error occurred'.
ENDTRY.

" Method 3: Test connection before calling
TRY.
    IF ZAKIR_SERIAL_SERVICE_CLASS=>test_connection(
      iv_host = '192.168.1.100'
      iv_port = '7373'
    ) = abap_true.
      WRITE: / 'Connection successful - proceeding with data call'.
      " Now call the actual service
      lv_value = ZAKIR_SERIAL_SERVICE_CLASS=>get_serial_value(
        iv_host = '192.168.1.100'
        iv_port = '7373'
      ).
    ELSE.
      WRITE: / 'Connection failed - check server status'.
    ENDIF.
  CATCH ZAKIR_SERIAL_SERVICE_CLASS=>connection_error.
    WRITE: / 'Connection error occurred'.
  CATCH ZAKIR_SERIAL_SERVICE_CLASS=>timeout_error.
    WRITE: / 'Timeout error occurred'.
ENDTRY.
```

#### Class Methods Available

| Method                | Description                        | Parameters                     | Returns                   |
| --------------------- | ---------------------------------- | ------------------------------ | ------------------------- |
| `call_serial_service` | Get full response with all details | host, port, timeout, test_mode | Complete result structure |
| `get_serial_value`    | Get only the serial value          | host, port, timeout            | String value              |
| `test_connection`     | Test if server is reachable        | host, port, timeout            | Boolean success           |

#### Exception Handling

- `connection_error`: Network or HTTP errors
- `timeout_error`: Request timeout
- `parse_error`: JSON parsing errors

### Test Program: `serial_class_test.abap`

This program demonstrates how to use the `SERIAL_SERVICE_METHOD` class with a user-friendly interface.

#### Features:

- **Selection Screen**: Easy parameter configuration
- **Multiple Test Options**: Test connection, get full result, or get only value
- **Error Handling**: Comprehensive exception handling with user-friendly messages
- **Visual Feedback**: Clear success/error indicators with emojis

#### Selection Screen Parameters:

- **Host**: Server hostname (default: localhost)
- **Port**: Server port (default: 7373)
- **Timeout**: Request timeout in seconds (default: 10)
- **Test Options**: Checkboxes to select which methods to test

#### Usage:

1. Run the program in SAP
2. Configure host, port, and timeout parameters
3. Select which methods to test (connection, full result, value only)
4. Execute to see the results

This program is perfect for:

- Testing the class functionality
- Demonstrating proper usage
- Debugging connection issues
- Learning how to implement the class in your own programs

## Configuration Options

### Serial Configuration

```json
{
  "serial": {
    "port": "/dev/ttyUSB0",     // Serial port path (REQUIRED)
    "baudrate": 9600,           // Communication speed (REQUIRED)
    "bytesize": 8,              // Data bits: 5, 6, 7, 8 (REQUIRED)
    "parity": "N",              // Parity: N, E, O, M, S (optional)
    "stopbits": 1,              // Stop bits: 1, 1.5, 2 (optional)
    "timeout": 1,               // Read timeout in seconds (optional)
    "xonxoff": false,           // Software flow control (optional)
    "rtscts": false,            // Hardware flow control RTS/CTS (optional)
    "dsrdtr": false,            // Hardware flow control DSR/DTR (optional)
    "write_timeout": null,      // Write timeout in seconds (optional)
    "inter_byte_timeout": null, // Inter-character timeout (optional)
    "exclusive": null,          // Exclusive access mode (optional)
    "description": "Arduino"    // Optional description
  }
}
```

**Required Parameters:**

| Parameter  | Type    | Description                            | Example Values                                                            |
| ---------- | ------- | -------------------------------------- | ------------------------------------------------------------------------- |
| `port`     | string  | Serial port path/device name           | `/dev/ttyUSB0`, `/dev/ttyACM0`, `COM1`, `COM3`, `/dev/cu.usbserial-*`     |
| `baudrate` | integer | Communication speed in bits per second | `9600`, `19200`, `38400`, `57600`, `115200`, `230400`, `460800`, `921600` |
| `bytesize` | integer | Number of data bits per character      | `5`, `6`, `7`, `8`                                                        |

**Optional Parameters:**

| Parameter            | Type    | Description                        | Possible Values                                                      | Default |
| -------------------- | ------- | ---------------------------------- | -------------------------------------------------------------------- | ------- |
| `parity`             | string  | Parity checking method             | `"N"` (None), `"E"` (Even), `"O"` (Odd), `"M"` (Mark), `"S"` (Space) | `"N"`   |
| `stopbits`           | float   | Number of stop bits                | `1`, `1.5`, `2`                                                      | `1`     |
| `timeout`            | float   | Read timeout in seconds            | `0.1`, `1.0`, `5.0`, `null` (blocking)                               | `null`  |
| `xonxoff`            | boolean | Software flow control (XON/XOFF)   | `true`, `false`                                                      | `false` |
| `rtscts`             | boolean | Hardware flow control (RTS/CTS)    | `true`, `false`                                                      | `false` |
| `dsrdtr`             | boolean | Hardware flow control (DSR/DTR)    | `true`, `false`                                                      | `false` |
| `write_timeout`      | float   | Write timeout in seconds           | `0.1`, `1.0`, `5.0`, `null` (blocking)                               | `null`  |
| `inter_byte_timeout` | float   | Inter-character timeout in seconds | `0.1`, `0.5`, `1.0`, `null` (disabled)                               | `null`  |
| `exclusive`          | boolean | Exclusive access mode              | `true`, `false`                                                      | `false` |

**Parameter Details:**

- **`port`**: The serial port device path. Common examples:
  
  - Linux: `/dev/ttyUSB0`, `/dev/ttyACM0`, `/dev/ttyS0`
  - Windows: `COM1`, `COM3`, `COM10`
  - macOS: `/dev/cu.usbserial-*`, `/dev/cu.usbmodem-*`

- **`baudrate`**: Standard baud rates include:
  
  - Low speed: `300`, `600`, `1200`, `2400`, `4800`, `9600`
  - Medium speed: `19200`, `38400`, `57600`, `115200`
  - High speed: `230400`, `460800`, `921600`, `1000000`

- **`bytesize`**: Data bits per character:
  
  - `5`: 5 data bits (rarely used)
  - `6`: 6 data bits (rarely used)
  - `7`: 7 data bits (common for ASCII)
  - `8`: 8 data bits (most common)

- **`parity`**: Error detection method:
  
  - `"N"`: No parity (most common)
  - `"E"`: Even parity
  - `"O"`: Odd parity
  - `"M"`: Mark parity (always 1)
  - `"S"`: Space parity (always 0)

- **`stopbits`**: Stop bits after data:
  
  - `1`: One stop bit (most common)
  - `1.5`: One and a half stop bits
  - `2`: Two stop bits

- **`timeout`**: Read operation timeout:
  
  - `null`: Blocking mode (wait indefinitely)
  - `0`: Non-blocking mode (return immediately)
  - `>0`: Timeout in seconds

- **Flow Control Options**:
  
  - `xonxoff`: Software flow control using XON/XOFF characters
  - `rtscts`: Hardware flow control using RTS/CTS signals
  - `dsrdtr`: Hardware flow control using DSR/DTR signals

- **`write_timeout`**: Write operation timeout (same format as `timeout`)

- **`inter_byte_timeout`**: Maximum time between characters in a read operation

- **`exclusive`**: Prevents other processes from accessing the same port

### Host Access Control

```json
{
  "allowed_hosts": [
    {
      "ip": "127.0.0.1",        // Client IP address
      "ports": [7373, 8080],    // Allowed ports
      "description": "Local"    // Optional description
    }
  ]
}
```

### Settings

```json
{
  "settings": {
    "log_file": "requests.log",     // Log file path
    "deny_unknown_hosts": true,     // Block unauthorized hosts
    "log_all_requests": true,       // Log all requests
    "encode": "utf-8"               // Character encoding for serial data
  }
}
```

**Settings Parameters:**

| Parameter            | Type    | Description                        | Example Values                                    | Default          |
| -------------------- | ------- | ---------------------------------- | ------------------------------------------------- | ---------------- |
| `log_file`           | string  | Path to log file                   | `"requests.log"`, `"/var/log/opscalesrv.log"`      | `"requests.log"` |
| `deny_unknown_hosts` | boolean | Block unauthorized hosts           | `true`, `false`                                   | `true`           |
| `log_all_requests`   | boolean | Log all HTTP requests              | `true`, `false`                                   | `true`           |
| `encode`             | string  | Character encoding for serial data | `"utf-8"`, `"iso-8859-9"`, `"ascii"`, `"latin-1"` | `"utf-8"`        |

**Encoding Options:**

- `"utf-8"`: Unicode UTF-8 encoding (default, most common)
- `"iso-8859-9"`: Turkish character support
- `"ascii"`: Basic ASCII characters only
- `"latin-1"`: ISO-8859-1 encoding
- `"cp1252"`: Windows-1252 encoding
- `"utf-16"`: Unicode UTF-16 encoding

**Note:** If the specified encoding fails to decode the data, the system will automatically fall back to UTF-8, and if that also fails, it will use Latin-1 as a last resort.

## Command Line Options

```bash
opscalesrv [OPTIONS]

Options:
  --host HOST     Host to bind to (default: localhost)
  --port PORT     Port to listen on (default: 7373)
  --test          Run in test mode (returns mock data)
  --abap          Copy ABAP files to current directory and exit
  --init          Initialize opscalesrv.json configuration file and exit
  --log           Enable logging to requests.log file
  --help          Show help message
```

## Use Cases

### IoT Data Collection

- Read sensor data from Arduino/Raspberry Pi
- Provide real-time data via HTTP API
- Integrate with monitoring systems

### Industrial Automation

- Connect to PLCs and industrial devices
- Provide data to SCADA systems
- Enable remote monitoring

### SAP Integration

- Bridge between serial devices and SAP systems
- Real-time data integration
- Automated data collection

## Development

### Project Structure

```
opscalesrv/
|-- __init__.py          # Main server code
|-- abap/                # ABAP client code
|   |-- serial_service_test.abap
|   |-- serial_service_class.abap
|   |-- serial_class_test.abap
|-- opscalesrv.json       # Configuration template
|-- requirements.txt     # Dependencies
```

### Dependencies

- `pyserial>=3.5` - Serial port communication
- `requests>=2.25.0` - HTTP client (for testing)

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   
   ```bash
   # Use different port
   opscalesrv --port 8080
   ```

2. **Serial Port Access Denied**
   
   ```bash
   # Add user to dialout group (Linux)
   sudo usermod -a -G dialout $USER
   ```

3. **ABAP Connection Failed**
   
   - Check if Python service is running
   - Verify network connectivity
   - Check firewall settings
   - Use debug mode in ABAP program

### Log Analysis

Check the log file for detailed request information:

```bash
tail -f requests.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Email: altay.kirecci@gmail.com
- https://www.opriori.com
- Issues: [GitHub Issues](https://github.com/altaykirecci/opscalesrv/issues)
- Documentation: [GitHub Wiki](https://github.com/altaykirecci/opscalesrv/wiki)

## Changelog

### v1.0.0

- Initial release
- Serial port reading functionality
- HTTP API with JSON responses
- Host-based access control
- ABAP integration support
- Comprehensive logging
- Test mode support