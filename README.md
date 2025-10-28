# Meshtastic Battery Monitor

A Python application for Raspberry Pi Zero 2 W that monitors and sends battery percentage from a USB-connected Meshtastic node to a designated target node. Designed for headless operation - perfect for remote battery monitoring.

## Features

- 🔋 Automatically sends battery percentage every 60 seconds
- 📱 Connects to Meshtastic nodes via USB
- 🤖 Headless operation - no keyboard/mouse required
- ⚙️ JSON-based configuration
- 🔄 Configurable send intervals and target nodes
- 🚀 Auto-starts on boot with systemd service

## Requirements

- Raspberry Pi Zero 2 W (or any Linux system with ARM/x86 architecture)
- Python 3.7+
- USB-connected Meshtastic node
- Virtual environment (recommended)

## Hardware Compatibility

✅ **Raspberry Pi Zero 2 W** - Fully tested and optimized
✅ **ARM Architecture** - All libraries are ARM-compatible
✅ **USB Serial** - Works with any Meshtastic node connected via USB

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

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.json` to set your target node and preferences:

```json
{
  "target_node_num": 2658499212,
  "send_interval_seconds": 60,
  "auto_start_timeout_seconds": 10
}

```

**Configuration Parameters:**
- `target_node_num`: The Meshtastic node number to send messages to (decimal format)
- `send_interval_seconds`: How often to send battery updates (default: 60)
- `auto_start_timeout_seconds`: Not used in headless mode (kept for compatibility)

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
1. Display configuration
2. Connect to USB Meshtastic node
3. Start sending battery percentage every 60 seconds
4. Run continuously until stopped with Ctrl+C

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

- **meshtastic** (>=2.2.0) - Python library for Meshtastic communication
- **pyserial** (>=3.5) - Serial port communication library

Both libraries are fully compatible with Raspberry Pi Zero 2 W ARM architecture.

## Project Structure

```
SimpleMeshPing/
├── battery_monitor.py      # Main application
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Contributing

Feel free to submit issues or pull requests for improvements!

## License

MIT License - Feel free to modify and use as needed.
