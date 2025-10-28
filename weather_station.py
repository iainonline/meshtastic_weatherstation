#!/usr/bin/env python3
"""
Meshtastic Weather Station
Sends temperature and humidity via Meshtastic using AT commands over serial.
No meshtastic Python library required - uses direct serial communication.
"""

import json
import time
import sys
import serial
import serial.tools.list_ports
from datetime import datetime

# Try to import DHT22 libraries, gracefully disable if not available
try:
    import adafruit_dht
    import board
    DHT22_AVAILABLE = True
except ImportError:
    DHT22_AVAILABLE = False
    print("Warning: DHT22 libraries not available. Temperature/humidity disabled.")


class MeshtasticWeatherStation:
    def __init__(self, config_file='config.json'):
        """Initialize the weather station with configuration."""
        self.config = self.load_config(config_file)
        self.target_node_id = self.config.get('target_node_id', '!ffffffff')  # Broadcast by default
        self.send_interval = self.config.get('send_interval_seconds', 60)
        self.dht22_pin = self.config.get('dht22_gpio_pin', 4)
        self.dht22_enabled = self.config.get('dht22_enabled', True) and DHT22_AVAILABLE
        self.serial_port = None
        self.running = False
        self.dht_device = None
        
        # Initialize DHT22 sensor if enabled
        if self.dht22_enabled:
            try:
                pin = getattr(board, f'D{self.dht22_pin}')
                self.dht_device = adafruit_dht.DHT22(pin, use_pulseio=False)
                print(f"✓ DHT22 sensor initialized on GPIO{self.dht22_pin}")
            except Exception as e:
                print(f"⚠ Warning: Could not initialize DHT22 sensor: {e}")
                self.dht22_enabled = False

    def load_config(self, config_file):
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file '{config_file}' not found. Using defaults.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in config file '{config_file}'. Using defaults.")
            return {}

    def find_meshtastic_port(self):
        """Find the Meshtastic device serial port."""
        ports = serial.tools.list_ports.comports()
        
        # Look for common Meshtastic device patterns
        for port in ports:
            port_str = str(port).lower()
            # Check for common USB-serial chips used in Meshtastic devices
            if any(pattern in port_str for pattern in ['cp210', 'ch340', 'usb serial', 'ttyusb', 'ttyacm']):
                return port.device
        
        # If no pattern match, return first available port
        if ports:
            return ports[0].device
        
        return None

    def connect_to_node(self):
        """Connect to USB-connected Meshtastic node."""
        try:
            port = self.find_meshtastic_port()
            if not port:
                print("✗ No serial devices found")
                return False
            
            print(f"Connecting to Meshtastic node on {port}...")
            self.serial_port = serial.Serial(port, 115200, timeout=1)
            time.sleep(2)  # Give device time to initialize
            
            print(f"✓ Connected to {port}")
            return True
        except Exception as e:
            print(f"✗ Error connecting to node: {e}")
            return False

    def send_text_message(self, message):
        """Send text message via Meshtastic using AT commands."""
        if not self.serial_port:
            print("✗ Not connected to device")
            return False
        
        try:
            # Use AT command to send message
            # Format: AT+SENDTEXT=<destination>,<message>
            cmd = f"AT+SENDTEXT={self.target_node_id},{message}\r\n"
            self.serial_port.write(cmd.encode('utf-8'))
            time.sleep(0.5)
            
            # Read response
            response = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
            
            return True
        except Exception as e:
            print(f"✗ Error sending message: {e}")
            return False

    def get_temperature_humidity(self):
        """Get temperature and humidity from DHT22 sensor."""
        if not self.dht22_enabled or not self.dht_device:
            return None, None
        
        try:
            temperature_c = self.dht_device.temperature
            humidity = self.dht_device.humidity
            return temperature_c, humidity
        except RuntimeError:
            # DHT sensors can be flaky, this is normal
            return None, None
        except Exception as e:
            print(f"Error reading DHT22: {e}")
            return None, None

    def send_weather_update(self):
        """Send weather update message."""
        temperature, humidity = self.get_temperature_humidity()
        
        # Build message
        message_parts = []
        
        if temperature is not None and humidity is not None:
            temperature_f = temperature * 9/5 + 32
            message_parts.append(f"Temp: {temperature_f:.1f}°F")
            message_parts.append(f"Hum: {humidity:.1f}%")
        else:
            if self.dht22_enabled:
                message_parts.append("Sensor: N/A")
            else:
                message_parts.append("Weather Station Online")
        
        message = " | ".join(message_parts)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending: {message}")
        
        if self.send_text_message(message):
            print("✓ Message sent")
        else:
            print("✗ Failed to send message")

    def monitor_loop(self):
        """Main monitoring loop."""
        print(f"\n{'='*50}")
        print(f"Weather Station Monitoring Started")
        print(f"Sending every {self.send_interval} seconds")
        print(f"Target: {self.target_node_id}")
        if self.dht22_enabled:
            print(f"DHT22 Sensor: GPIO{self.dht22_pin}")
        print(f"{'='*50}\n")
        print("Press Ctrl+C to stop\n")
        
        while self.running:
            self.send_weather_update()
            
            # Wait for interval
            time.sleep(self.send_interval)

    def start_monitoring(self):
        """Start the weather monitoring process."""
        if not self.connect_to_node():
            return False
        
        self.running = True
        
        try:
            self.monitor_loop()
        except KeyboardInterrupt:
            print("\n\nStopping monitoring...")
        finally:
            self.stop_monitoring()
        
        return True

    def stop_monitoring(self):
        """Stop the monitoring process."""
        self.running = False
        
        # Cleanup DHT sensor
        if self.dht_device:
            try:
                self.dht_device.exit()
            except:
                pass
        
        if self.serial_port:
            try:
                self.serial_port.close()
                print("✓ Disconnected from device")
            except:
                pass
            self.serial_port = None


def main():
    """Main entry point for the application."""
    print("\n" + "="*50)
    print("  Meshtastic Weather Station")
    print("="*50)
    
    station = MeshtasticWeatherStation()
    
    # Display configuration
    print(f"Target Node: {station.target_node_id}")
    print(f"Send Interval: {station.send_interval} seconds")
    if station.dht22_enabled:
        print(f"DHT22 Sensor: GPIO{station.dht22_pin}")
    print("="*50)
    print("\nStarting monitoring (Press Ctrl+C to stop)...\n")
    
    # Auto-start monitoring
    station.start_monitoring()


if __name__ == "__main__":
    main()
