#!/usr/bin/env python3
"""
Meshtastic Weather Station
Sends battery percentage, temperature, and humidity via Meshtastic serial interface.
Uses direct serial communication - no meshtastic library required.
"""

import json
import time
import sys
import serial
import serial.tools.list_ports
from datetime import datetime
import adafruit_dht
import board


class MeshBatteryMonitor:
    def __init__(self, config_file='config.json'):
        """Initialize the battery monitor with configuration."""
        self.config = self.load_config(config_file)
        self.target_node_num = self.config.get('target_node_num', 2658499212)
        self.send_interval = self.config.get('send_interval_seconds', 60)
        self.auto_start_timeout = self.config.get('auto_start_timeout_seconds', 10)
        self.dht22_pin = self.config.get('dht22_gpio_pin', 4)  # Default GPIO4
        self.dht22_enabled = self.config.get('dht22_enabled', True)
        self.interface = None
        self.running = False
        self.stop_event = Event()
        self.dht_device = None
        
        # Initialize DHT22 sensor if enabled
        if self.dht22_enabled:
            try:
                # Map GPIO pin number to board pin
                pin = getattr(board, f'D{self.dht22_pin}')
                self.dht_device = adafruit_dht.DHT22(pin, use_pulseio=False)
                print(f"✓ DHT22 sensor initialized on GPIO{self.dht22_pin}")
            except Exception as e:
                print(f"⚠ Warning: Could not initialize DHT22 sensor: {e}")
                print(f"  Temperature/humidity readings will be disabled")
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

    def connect_to_node(self):
        """Connect to USB-connected Meshtastic node."""
        try:
            print("Connecting to Meshtastic node via USB...")
            self.interface = meshtastic.serial_interface.SerialInterface()
            print(f"✓ Connected to node: {self.interface.myInfo.my_node_num}")
            return True
        except Exception as e:
            print(f"✗ Error connecting to node: {e}")
            return False

    def get_battery_percentage(self):
        """Get battery percentage from the connected node."""
        try:
            if self.interface and self.interface.nodesByNum:
                my_node_num = self.interface.myInfo.my_node_num
                if my_node_num in self.interface.nodesByNum:
                    node_info = self.interface.nodesByNum[my_node_num]
                    if 'deviceMetrics' in node_info and 'batteryLevel' in node_info['deviceMetrics']:
                        return node_info['deviceMetrics']['batteryLevel']
                    elif 'position' in node_info and 'batteryLevel' in node_info['position']:
                        return node_info['position']['batteryLevel']
            return None
        except Exception as e:
            print(f"Error getting battery level: {e}")
            return None

    def get_temperature_humidity(self):
        """Get temperature and humidity from DHT22 sensor."""
        if not self.dht22_enabled or not self.dht_device:
            return None, None
        
        try:
            temperature_c = self.dht_device.temperature
            humidity = self.dht_device.humidity
            return temperature_c, humidity
        except RuntimeError as e:
            # DHT sensors can be flaky, this is normal
            return None, None
        except Exception as e:
            print(f"Error reading DHT22: {e}")
            return None, None

    def send_battery_message(self):
        """Send battery percentage, temperature, and humidity to target node."""
        battery_level = self.get_battery_percentage()
        temperature, humidity = self.get_temperature_humidity()
        
        # Build message
        message_parts = []
        
        if battery_level is not None:
            message_parts.append(f"Bat: {battery_level}%")
        else:
            message_parts.append("Bat: N/A")
        
        if temperature is not None and humidity is not None:
            # Convert to Fahrenheit
            temperature_f = temperature * 9/5 + 32
            message_parts.append(f"Temp: {temperature_f:.1f}°F")
            message_parts.append(f"Hum: {humidity:.1f}%")
        else:
            if self.dht22_enabled:
                message_parts.append("Temp/Hum: N/A")
        
        message = " | ".join(message_parts)
        
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending to node {self.target_node_num}: {message}")
            self.interface.sendText(message, destinationId=self.target_node_num)
            print("✓ Message sent successfully")
        except Exception as e:
            print(f"✗ Error sending message: {e}")

    def monitor_loop(self):
        """Main monitoring loop that sends messages at intervals."""
        print(f"\n{'='*50}")
        print(f"Weather Station Monitoring Started")
        print(f"Sending every {self.send_interval} seconds")
        print(f"Target Node: {self.target_node_num}")
        if self.dht22_enabled:
            print(f"DHT22 Sensor: GPIO{self.dht22_pin}")
        print(f"{'='*50}\n")
        print("Press Ctrl+C to stop\n")
        
        while not self.stop_event.is_set():
            self.send_battery_message()
            
            # Wait for the interval or until stopped
            for _ in range(self.send_interval):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

    def start_monitoring(self):
        """Start the battery monitoring process."""
        if not self.connect_to_node():
            return False
        
        self.running = True
        self.stop_event.clear()
        
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
        self.stop_event.set()
        
        # Cleanup DHT sensor
        if self.dht_device:
            try:
                self.dht_device.exit()
            except:
                pass
        
        if self.interface:
            try:
                self.interface.close()
                print("✓ Disconnected from node")
            except:
                pass
            self.interface = None

    def test_connection(self):
        """Test connection to USB node and display info."""
        if self.connect_to_node():
            try:
                print(f"\nNode Information:")
                print(f"  My Node Number: {self.interface.myInfo.my_node_num}")
                battery = self.get_battery_percentage()
                if battery is not None:
                    print(f"  Battery Level: {battery}%")
                else:
                    print(f"  Battery Level: Not available")
                
                # Test DHT22
                if self.dht22_enabled:
                    temp, hum = self.get_temperature_humidity()
                    if temp is not None and hum is not None:
                        temp_f = temp * 9/5 + 32
                        print(f"  Temperature: {temp:.1f}°C ({temp_f:.1f}°F)")
                        print(f"  Humidity: {hum:.1f}%")
                    else:
                        print(f"  Temperature/Humidity: Not available (sensor warming up)")
                
                print(f"  Target Node Number: {self.target_node_num}")
            finally:
                self.interface.close()
            return True
        return False


def main():
    """Main entry point for the application."""
    print("\n" + "="*50)
    print("  Meshtastic Weather Station")
    print("="*50)
    
    monitor = MeshBatteryMonitor()
    
    # Display configuration
    print(f"Target Node Number: {monitor.target_node_num}")
    print(f"Send Interval: {monitor.send_interval} seconds")
    if monitor.dht22_enabled:
        print(f"DHT22 Sensor: GPIO{monitor.dht22_pin}")
    print("="*50)
    print("\nStarting monitoring (Press Ctrl+C to stop)...\n")
    
    # Auto-start monitoring
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
