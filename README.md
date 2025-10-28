# Meshtastic Weather Station

A Python application for Raspberry Pi Zero 2 W that sends temperature and humidity data via Meshtastic. **No meshtastic Python library required** - uses direct serial communication for maximum simplicity and speed.

## Features

- 🌡️ Reads temperature and humidity from DHT22 sensor
- � Sends data via Meshtastic using AT commands over serial
- 🚀 **Ultra-fast install** - NO meshtastic library dependencies!
- 🤖 Headless operation - no keyboard/mouse required
- ⚙️ JSON-based configuration
- 🔄 Configurable send intervals
- 📊 Sends data in Fahrenheit

## Why No Meshtastic Library?

The official `meshtastic` Python library has heavy dependencies (protobuf, dbus-fast, etc.) that take 30+ minutes to compile on Pi Zero 2 W. This version uses **direct serial AT commands** instead - same functionality, **installs in seconds**!

## Requirements

- Raspberry Pi Zero 2 W (or any Linux system)
- Python 3.7+
- USB-connected Meshtastic node
- DHT22 temperature/humidity sensor (optional)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/iainonline/meshtastic_weatherstation.git
cd meshtastic_weatherstation
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

**SUPER SIMPLE - Just 2 packages!**

```bash
# Install system library for DHT22
sudo apt install libgpiod2 -y

# Install Python dependencies (under 30 seconds!)
pip install -r requirements.txt
```

That's it! No meshtastic library, no protobuf, no dbus-fast compilation!

## Hardware Setup

### DHT22 Sensor Wiring (Default: GPIO4)
- **VCC (Pin 1)** → 3.3V (Pi Pin 1)
- **Data (Pin 2)** → GPIO4 (Pi Pin 7) - Configurable in config.json
- **GND (Pin 4)** → GND (Pi Pin 6)
- **10kΩ pull-up resistor** between VCC and Data (recommended)

## Configuration

Edit `config.json`:

```json
{
  "target_node_id": "!ffffffff",
  "send_interval_seconds": 60,
  "dht22_enabled": true,
  "dht22_gpio_pin": 4
}
```

**Parameters:**
- `target_node_id`: Meshtastic node ID (use `!ffffffff` for broadcast, or specific node like `!a1b2c3d4`)
- `send_interval_seconds`: How often to send updates (default: 60)
- `dht22_enabled`: Enable/disable DHT22 sensor
- `dht22_gpio_pin`: GPIO pin for DHT22 data line (default: 4)

## Usage

### Manual Run

```bash
source venv/bin/activate
python3 weather_station.py
```

The script will:
1. Initialize DHT22 sensor (if enabled)
2. Find and connect to Meshtastic device via USB
3. Send weather data every 60 seconds
4. Run continuously until stopped with Ctrl+C

**Example output:**
```
Temp: 72.5°F | Hum: 45.2%
```

### Running on Boot (Headless Setup)

For headless Raspberry Pi operation, set up a systemd service:

#### 1. Create the service file:

```bash
sudo nano /etc/systemd/system/mesh-battery.service
```

#### 2. Add this content:

```ini
[Unit]
Description=Meshtastic Weather Station
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/meshtastic_weatherstation
ExecStart=/home/pi/meshtastic_weatherstation/venv/bin/python3 /home/pi/meshtastic_weatherstation/weather_station.py
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

### "ModuleNotFoundError" Errors
If you get import errors, verify you followed the exact installation order:
```bash
# Must install meshtastic FIRST with --no-deps
pip install --no-deps meshtastic==2.3.12
# THEN install requirements
pip install -r requirements.txt
```

## Dependencies

**Minimal - Just 2 packages!**
- **pyserial** (>=3.5) - USB serial communication
- **adafruit-circuitpython-dht** - DHT22 sensor (optional)
- **adafruit-blinka** - GPIO support for CircuitPython

**NO meshtastic library required!** Uses direct AT command communication over serial.

**Total install time on Pi Zero 2 W:** ~30 seconds (vs 30+ minutes with meshtastic library)

## Project Structure

```
meshtastic_weatherstation/
├── weather_station.py      # Main application (NO meshtastic library!)
├── config.json             # Configuration file
├── requirements.txt        # Minimal dependencies (just pyserial + DHT22)
└── README.md              # This file
```

## Contributing

Feel free to submit issues or pull requests for improvements!

## License

MIT License - Feel free to modify and use as needed.
