#!/usr/bin/env python3
"""
Meshtastic Weather Station - Simple & Reliable
Sends temperature and humidity via Meshtastic CLI.
Ultra-minimal dependencies - just Python standard library + DHT22.
"""

import json
import time
import subprocess
from datetime import datetime

# Try to import DHT22, gracefully disable if not available
DHT22_AVAILABLE = False
try:
    import adafruit_dht
    import board
    DHT22_AVAILABLE = True
except ImportError:
    pass


class WeatherStation:
    """Simple weather station using Meshtastic CLI."""
    
    def __init__(self, config_file='config.json'):
        """Initialize with configuration."""
        self.config = self.load_config(config_file)
        self.target = self.config.get('target_node_id', '!ffffffff')
        self.interval = self.config.get('send_interval_seconds', 60)
        self.dht22_enabled = self.config.get('dht22_enabled', True) and DHT22_AVAILABLE
        self.gpio_pin = self.config.get('dht22_gpio_pin', 4)
        self.sensor = None
        
        # Initialize DHT22
        if self.dht22_enabled:
            try:
                pin = getattr(board, f'D{self.gpio_pin}')
                self.sensor = adafruit_dht.DHT22(pin, use_pulseio=False)
                print(f"✓ DHT22 initialized on GPIO{self.gpio_pin}")
            except Exception as e:
                print(f"⚠ DHT22 init failed: {e}")
                self.dht22_enabled = False

    def load_config(self, config_file):
        """Load JSON configuration."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠ Config error: {e}, using defaults")
            return {}

    def read_sensor(self):
        """Read temperature and humidity from DHT22."""
        if not self.dht22_enabled or not self.sensor:
            return None, None
        
        try:
            temp_c = self.sensor.temperature
            humidity = self.sensor.humidity
            if temp_c is not None and humidity is not None:
                return temp_c, humidity
        except RuntimeError:
            pass  # DHT22 read errors are normal
        except Exception as e:
            print(f"⚠ Sensor error: {e}")
        
        return None, None

    def send_message(self, message):
        """Send message via Meshtastic CLI."""
        try:
            # Use meshtastic --sendtext command
            cmd = ['meshtastic', '--sendtext', message]
            
            if self.target != '!ffffffff':
                cmd.extend(['--dest', self.target])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return True
            else:
                print(f"⚠ Send failed: {result.stderr.strip()}")
                return False
                
        except FileNotFoundError:
            print("✗ Meshtastic CLI not found. Install with: pip install meshtastic")
            return False
        except subprocess.TimeoutExpired:
            print("⚠ Send timeout")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def build_message(self):
        """Build weather message."""
        temp_c, humidity = self.read_sensor()
        
        if temp_c is not None and humidity is not None:
            temp_f = temp_c * 9/5 + 32
            return f"Temp: {temp_f:.1f}°F | Hum: {humidity:.1f}%"
        elif self.dht22_enabled:
            return "Weather: Sensor N/A"
        else:
            return "Weather Station Online"

    def run(self):
        """Main monitoring loop."""
        print("\n" + "="*50)
        print("  Meshtastic Weather Station")
        print("="*50)
        print(f"Target: {self.target}")
        print(f"Interval: {self.interval}s")
        if self.dht22_enabled:
            print(f"DHT22: GPIO{self.gpio_pin}")
        print("="*50)
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                message = self.build_message()
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                print(f"[{timestamp}] Sending: {message}")
                
                if self.send_message(message):
                    print("✓ Sent")
                else:
                    print("✗ Failed")
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n✓ Stopped")
        finally:
            if self.sensor:
                try:
                    self.sensor.exit()
                except:
                    pass


def main():
    """Entry point."""
    station = WeatherStation()
    station.run()


if __name__ == "__main__":
    main()
