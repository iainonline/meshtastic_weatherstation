# Meshtastic Weather Station

A Python application for Raspberry Pi Zero 2 W that monitors and sends battery percentage, temperature, and humidity from a USB-connected Meshtastic node to a designated target node. Includes DHT22 temperature/humidity sensor support. Designed for headless operation - perfect for remote weather monitoring.

## Features

- 🔋 Automatically sends battery percentage every 60 seconds
- 🌡️ Reads temperature and humidity from DHT22 sensor
- 📱 Connects to Meshtastic nodes via USB
- 🤖 Headless operation - no keyboard/mouse required
- ⚙️ JSON-based configuration
- 🔄 Configurable send intervals and target nodes
- 🚀 Auto-starts on boot with systemd service
- 📊 Sends data in both Celsius and Fahrenheit

## Requirements

- Raspberry Pi Zero 2 W (or any Linux system with ARM/x86 architecture)
- Python 3.7+
- USB-connected Meshtastic node
- DHT22 temperature/humidity sensor (optional)
- Virtual environment (recommended)

## Hardware Setup

### Meshtastic Node
✅ **Raspberry Pi Zero 2 W** - Fully tested and optimized
✅ **ARM Architecture** - All libraries are ARM-compatible
✅ **USB Serial** - Works with any Meshtastic node connected via USB

### DHT22 Sensor Wiring (Default: GPIO4)
- **VCC (Pin 1)** → 3.3V (Pi Pin 1)
- **Data (Pin 2)** → GPIO4 (Pi Pin 7) - Configurable in config.json
- **GND (Pin 4)** → GND (Pi Pin 6)
- **Note:** A 10kΩ pull-up resistor between VCC and Data is recommended (some modules have this built-in)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/SimpleMeshPing.git
cd SimpleMeshPing
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 4. Install Dependencies

**IMPORTANT for Raspberry Pi Zero 2 W (USB-only setup):**

```bash
# Install system library for DHT22 sensor
sudo apt install libgpiod2 -y

# Install meshtastic without dependencies (skips slow dbus-fast compilation)
pip install --no-deps meshtastic==2.3.12

# Install only USB-required dependencies (fast!)
pip install -r requirements.txt
```

**Note:** This installation method skips Bluetooth dependencies (dbus-fast, bleak) which can take 30+ minutes to compile on Pi Zero 2 W. Since this project uses USB connection only, these are not needed.

## Configuration

Edit `config.json` to set your target node and preferences:

```json
{
  "target_node_num": 2658499212,
  "send_interval_seconds": 60,
  "auto_start_timeout_seconds": 10,
  "dht22_enabled": true,
  "dht22_gpio_pin": 4
}
```

**Configuration Parameters:**
- `target_node_num`: The Meshtastic node number to send messages to (decimal format)
- `send_interval_seconds`: How often to send weather updates (default: 60)
- `auto_start_timeout_seconds`: Not used in headless mode (kept for compatibility)
- `dht22_enabled`: Enable/disable DHT22 sensor (true/false)
- `dht22_gpio_pin`: GPIO pin number for DHT22 data line (default: 4 = Physical Pin 7)

**Finding Your Target Node Number:**
You can find node numbers using the Meshtastic app or by checking your node's web interface.

## Usage

### Manual Run

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python3 battery_monitor.py
```

The script will:
1. Initialize DHT22 sensor (if enabled)
2. Display configuration
3. Connect to USB Meshtastic node
4. Start sending battery, temperature, and humidity data every 60 seconds
5. Run continuously until stopped with Ctrl+C

**Example output message:**
```
Bat: 95% | Temp: 22.5°C (72.5°F) | Hum: 45.2%
```

### Running on Boot (Headless Setup)

For headless Raspberry Pi operation, set up a systemd service:

#### 1. Create the service file:

```bash
sudo nano /etc/systemd/system/mesh-battery.service
```

#### 2. Add this content (update paths as needed):

```ini
[Unit]
Description=Meshtastic Battery Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/iain/SimpleMeshPing
ExecStart=/home/iain/SimpleMeshPing/venv/bin/python3 /home/iain/SimpleMeshPing/battery_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mesh-battery.service
sudo systemctl start mesh-battery.service
```

#### 4. Check service status:

```bash
sudo systemctl status mesh-battery.service
```

#### 5. View logs:

```bash
sudo journalctl -u mesh-battery.service -f
```

## Troubleshooting

### USB Permission Issues
If you get permission errors accessing the USB device:
```bash
sudo usermod -a -G dialout $USER
```
Then log out and log back in (or reboot).

### DHT22 Sensor Issues

**"RuntimeError: A full buffer was not returned"**
- DHT22 sensors can be temperamental and may fail occasionally
- The script will retry on next interval
- Ensure proper wiring and 10kΩ pull-up resistor

**GPIO Permission Issues**
```bash
sudo usermod -a -G gpio $USER
```
Then reboot.

**Sensor reads "N/A"**
- Check wiring (VCC to 3.3V, GND to GND, Data to GPIO4)
- Verify `dht22_enabled: true` in config.json
- Check correct GPIO pin number in config.json
- DHT22 needs a few seconds to warm up on first read

### No Node Found
- Ensure your Meshtastic device is connected via USB
- Check with `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`
- Verify the device is powered on

### Battery Info Not Available
Some nodes may not report battery status immediately. The app will send "Battery: N/A" until data is available.

### Service Won't Start
- Check logs: `sudo journalctl -u mesh-battery.service -n 50`
- Verify Python path in service file matches your installation
- Ensure virtual environment has all dependencies installed

## Dependencies

- **meshtastic** (2.3.12) - Python library for Meshtastic communication
- **pyserial** (>=3.5) - Serial port communication library
- **adafruit-circuitpython-dht** - DHT22 temperature/humidity sensor library
- **RPi.GPIO** - Raspberry Pi GPIO control

All libraries are fully compatible with Raspberry Pi Zero 2 W ARM architecture.

## Project Structure

```
SimpleMeshPing/
├── battery_monitor.py      # Main weather station application
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Contributing

Feel free to submit issues or pull requests for improvements!

## License

MIT License - Feel free to modify and use as needed.
