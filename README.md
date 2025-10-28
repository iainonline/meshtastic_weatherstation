# Meshtastic Weather Station

Ultra-simple weather station for Raspberry Pi Zero 2 W. Sends temperature and humidity via Meshtastic CLI. **Minimal dependencies, maximum reliability.**

## Features

- 🌡️ DHT22 temperature and humidity sensor
- 📡 Uses Meshtastic CLI (simple subprocess calls)
- ⚡ **Fast install** - No heavy dependencies
- 🤖 Headless operation
- 🛡️ **Reliable** - Simple Python code, easy to debug
- 📊 Sends in Fahrenheit

## Why This Approach?

Uses `meshtastic` CLI command via subprocess instead of the Python library. Same functionality, way simpler:
- ✅ No protobuf, pypubsub, packaging complexity
- ✅ Installs in under 1 minute on Pi Zero 2 W  
- ✅ Easy to troubleshoot
- ✅ Minimal dependencies = fewer breaking points

## Requirements

- Raspberry Pi Zero 2 W (or any Linux system)
- Python 3.7+
- USB-connected Meshtastic node
- DHT22 temperature/humidity sensor (optional)

## Installation

### 1. Clone Repository

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

```bash
# System library for DHT22
sudo apt install libgpiod2 -y

# Install Meshtastic CLI (without heavy dependencies)
pip install --no-deps meshtastic

# Install minimal requirements
pip install -r requirements.txt
```

**Total install time: ~1 minute on Pi Zero 2 W**

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

### Run

```bash
source venv/bin/activate
python3 weather_station.py
```

**Output:**
```
[10:30:15] Sending: Temp: 72.5°F | Hum: 45.2%
✓ Sent
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

### "Meshtastic CLI not found" Error

The script uses the `meshtastic` CLI command. Install it:

```bash
pip install --no-deps meshtastic
pip install pyserial
```

Verify it works:
```bash
meshtastic --info
```

## Dependencies

**Minimal and reliable:**
- `meshtastic` CLI (installed with `--no-deps` flag)
- `pyserial` - Serial communication for Meshtastic CLI
- `adafruit-circuitpython-dht` - DHT22 sensor (optional)
- `adafruit-blinka` - GPIO support (optional)

**No heavy dependencies:** No protobuf, no pypubsub, no packaging, no dbus-fast!

**Install time on Pi Zero 2 W:** ~1 minute

## Project Structure

```
meshtastic_weatherstation/
├── weather_station.py      # Main app (~150 lines, simple & clean)
├── config.json             # Configuration
├── requirements.txt        # DHT22 dependencies only
└── README.md              # This file
```

## How It Works

1. Reads temperature/humidity from DHT22 sensor
2. Formats message: `"Temp: 72.5°F | Hum: 45.2%"`
3. Calls `meshtastic --sendtext "message"` via subprocess
4. Repeats every 60 seconds

Simple, reliable, easy to understand!

## Contributing

Feel free to submit issues or pull requests for improvements!

## License

MIT License - Feel free to modify and use as needed.
