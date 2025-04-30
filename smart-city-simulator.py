import json
import socket
import threading
import time
import random
import datetime
from typing import Dict, Any, Tuple

# Configuration
HOST = '127.0.0.1'  # localhost
PORTS = {
    'traffic': 5001,
    'parking': 5002,
    'air_quality': 5003,
    'lighting': 5004,
    'waste': 5005,
    'transit': 5006
}

# Simulation constants
NUM_TRAFFIC_SENSORS = 10
NUM_PARKING_LOTS = 8
NUM_AIR_QUALITY_SENSORS = 6
NUM_STREET_LIGHTS = 15
NUM_WASTE_CONTAINERS = 12
NUM_TRANSIT_VEHICLES = 8

# City area boundaries (latitude and longitude ranges)
LAT_MIN, LAT_MAX = 41.3000, 41.3500  # Example: Tirana area
LON_MIN, LON_MAX = 19.7500, 19.8500


# Helper functions
def generate_id() -> str:
    """Generate a simple UUID-like ID"""
    return f"{random.randint(100000, 999999)}"


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.datetime.now().isoformat()


def random_location() -> Tuple[float, float]:
    """Generate random coordinates within city boundaries"""
    lat = random.uniform(LAT_MIN, LAT_MAX)
    lon = random.uniform(LON_MIN, LON_MAX)
    return lat, lon


# Data generators for each service
class TrafficDataGenerator:
    def __init__(self):
        self.sensors = []
        for _ in range(NUM_TRAFFIC_SENSORS):
            lat, lon = random_location()
            self.sensors.append({
                "sensor_id": f"TRAFFIC-{generate_id()}",
                "location": {
                    "latitude": lat,
                    "longitude": lon
                }
            })
    
    def generate_data(self) -> Dict[str, Any]:
        sensor = random.choice(self.sensors)
        
        # Time-based traffic patterns (rush hours)
        hour = datetime.datetime.now().hour
        rush_hour_factor = 1.0
        if 7 <= hour <= 9 or 16 <= hour <= 18:  # Morning/evening rush
            rush_hour_factor = 2.5
        elif 10 <= hour <= 15:  # Mid-day
            rush_hour_factor = 1.5
        elif 22 <= hour or hour <= 5:  # Night
            rush_hour_factor = 0.3
            
        base_vehicle_count = int(random.normalvariate(50, 15) * rush_hour_factor)
        vehicle_count = max(0, base_vehicle_count)
        
        # Speed is inversely related to vehicle count
        speed_factor = max(0.2, min(1.0, 1.5 - (vehicle_count / 200)))
        speed = random.normalvariate(50, 8) * speed_factor
        
        # Congestion level based on vehicle count and speed
        if vehicle_count > 80 and speed < 20:
            congestion = 5  # Gridlock
        elif vehicle_count > 60 and speed < 30:
            congestion = 4  # Heavy congestion
        elif vehicle_count > 40 and speed < 40:
            congestion = 3  # Moderate congestion
        elif vehicle_count > 20:
            congestion = 2  # Light congestion
        elif vehicle_count > 10:
            congestion = 1  # Free flowing
        else:
            congestion = 0  # Empty
            
        return {
            "sensor_id": sensor["sensor_id"],
            "timestamp": get_timestamp(),
            "location": sensor["location"],
            "vehicle_count": vehicle_count,
            "average_speed": round(speed, 1),
            "congestion_level": congestion
        }


class ParkingDataGenerator:
    def __init__(self):
        self.parking_lots = []
        
        for i in range(NUM_PARKING_LOTS):
            lot_id = f"PARKING-{generate_id()}"
            lat, lon = random_location()
            capacity = random.randint(20, 200)
            
            self.parking_lots.append({
                "lot_id": lot_id,
                "location": {
                    "latitude": lat,
                    "longitude": lon
                },
                "total_spaces": capacity
            })
    
    def generate_data(self) -> Dict[str, Any]:
        # Select random lot
        lot = random.choice(self.parking_lots)
        lot_id = lot["lot_id"]
        total_spaces = lot["total_spaces"]
        
        # Time-based parking patterns
        hour = datetime.datetime.now().hour
        if 8 <= hour <= 18:  # Business hours
            base_occupancy = 0.7
        elif 19 <= hour <= 22:  # Evening
            base_occupancy = 0.5
        else:  # Night
            base_occupancy = 0.2
        
        # Calculate lot occupancy with some randomness
        occupancy_rate = base_occupancy * random.uniform(0.8, 1.2)
        occupancy_rate = min(1.0, max(0.0, occupancy_rate))  # Keep between 0 and 1
        occupied_spaces = int(total_spaces * occupancy_rate)
        available_spaces = total_spaces - occupied_spaces
        
        return {
            "lot_id": lot_id,
            "timestamp": get_timestamp(),
            "location": lot["location"],
            "available_spaces": available_spaces,
            "total_spaces": total_spaces,
            "occupancy_rate": round(occupancy_rate, 2)
        }


class AirQualityDataGenerator:
    def __init__(self):
        self.sensors = []
        for _ in range(NUM_AIR_QUALITY_SENSORS):
            lat, lon = random_location()
            self.sensors.append({
                "sensor_id": f"AIR-{generate_id()}",
                "location": {
                    "latitude": lat,
                    "longitude": lon
                }
            })
    
    def generate_data(self) -> Dict[str, Any]:
        sensor = random.choice(self.sensors)
        
        # Base air quality (affected by time of day)
        hour = datetime.datetime.now().hour
        traffic_factor = 1.0
        
        if 7 <= hour <= 9 or 16 <= hour <= 18:  # Rush hours
            traffic_factor = 1.5
        elif 22 <= hour or hour <= 5:  # Night
            traffic_factor = 0.6
        
        # AQI calculation (simplified)
        base_aqi = random.normalvariate(50, 15)
        aqi = int(base_aqi * traffic_factor)
        aqi = max(0, min(300, aqi))  # Keep AQI in reasonable range
        
        # Weather conditions
        season = (datetime.datetime.now().month % 12) // 3  # 0=winter, 1=spring, 2=summer, 3=fall
        base_temp = [5, 15, 25, 15][season]  # Base temp by season
        hour_factor = min(hour, 24-hour) / 6  # Peak at noon
        temperature = base_temp + hour_factor * 8 + random.normalvariate(0, 2)
        
        humidity = random.normalvariate([70, 65, 60, 70][season], 10)
        humidity = max(0, min(100, humidity))  # Keep between 0-100%
        
        return {
            "sensor_id": sensor["sensor_id"],
            "timestamp": get_timestamp(),
            "location": sensor["location"],
            "aqi": aqi,
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1)
        }


class LightingDataGenerator:
    def __init__(self):
        self.lights = []
        for i in range(NUM_STREET_LIGHTS):
            lat, lon = random_location()
            self.lights.append({
                "light_id": f"LIGHT-{generate_id()}",
                "location": {
                    "latitude": lat,
                    "longitude": lon
                }
            })
    
    def generate_data(self) -> Dict[str, Any]:
        light = random.choice(self.lights)
        
        # Light status based on time of day
        hour = datetime.datetime.now().hour
        is_night = hour <= 6 or hour >= 18
        
        if is_night:
            status_options = ["on", "dimmed", "malfunction"]
            weights = [0.85, 0.1, 0.05]  # 85% on, 10% dimmed, 5% malfunction
        else:
            status_options = ["off", "malfunction"]
            weights = [0.95, 0.05]  # 95% off, 5% malfunction
            
        status = random.choices(status_options, weights=weights, k=1)[0]
        
        # Brightness based on status
        if status == "on":
            brightness = random.randint(90, 100)
        elif status == "dimmed":
            brightness = random.randint(30, 70)
        else:
            brightness = random.randint(0, 20)
            
        # Power consumption based on brightness
        power_base = 40  # Base wattage
        power = power_base * (brightness / 100) if status != "off" else 0
        
        return {
            "light_id": light["light_id"],
            "timestamp": get_timestamp(),
            "location": light["location"],
            "status": status,
            "brightness_level": brightness,
            "power_consumption": round(power + random.uniform(-2, 2), 1)
        }


class WasteDataGenerator:
    def __init__(self):
        self.containers = []
        waste_types = ["general", "recycling", "compost", "paper", "glass"]
        
        for _ in range(NUM_WASTE_CONTAINERS):
            lat, lon = random_location()
            waste_type = random.choice(waste_types)
            
            self.containers.append({
                "container_id": f"WASTE-{generate_id()}",
                "location": {
                    "latitude": lat,
                    "longitude": lon
                },
                "waste_type": waste_type
            })
    
    def generate_data(self) -> Dict[str, Any]:
        container = random.choice(self.containers)
        
        # Fill level simulation
        base_fill = random.uniform(0.1, 0.9)
        
        # Collection priority based on fill level
        if base_fill > 0.9:
            priority = 5  # Urgent
        elif base_fill > 0.7:
            priority = 4  # High
        elif base_fill > 0.5:
            priority = 3  # Medium
        elif base_fill > 0.3:
            priority = 2  # Low
        else:
            priority = 1  # Very low
            
        return {
            "container_id": container["container_id"],
            "timestamp": get_timestamp(),
            "location": container["location"],
            "waste_type": container["waste_type"],
            "fill_level": round(base_fill, 2),
            "collection_priority": priority
        }


class TransitDataGenerator:
    def __init__(self):
        self.vehicles = []
        vehicle_types = ["bus", "tram", "subway", "ferry"]
        
        # Create vehicles
        for i in range(NUM_TRANSIT_VEHICLES):
            vehicle_type = random.choice(vehicle_types)
            route_id = f"ROUTE-{random.randint(1,10):02d}"
            
            self.vehicles.append({
                "vehicle_id": f"{vehicle_type.upper()}-{generate_id()}",
                "route_id": route_id,
                "vehicle_type": vehicle_type,
                "capacity": {
                    "bus": random.randint(40, 80),
                    "tram": random.randint(60, 120),
                    "subway": random.randint(150, 300),
                    "ferry": random.randint(100, 500)
                }[vehicle_type]
            })
    
    def generate_data(self) -> Dict[str, Any]:
        vehicle = random.choice(self.vehicles)
        capacity = vehicle["capacity"]
        
        # Generate a random location
        lat, lon = random_location()
        
        # Time-based occupancy patterns
        hour = datetime.datetime.now().hour
        if 7 <= hour <= 9 or 16 <= hour <= 18:  # Rush hours
            base_occupancy = random.uniform(0.7, 1.0)
        elif 10 <= hour <= 15:  # Mid-day
            base_occupancy = random.uniform(0.3, 0.7)
        elif 19 <= hour <= 22:  # Evening
            base_occupancy = random.uniform(0.2, 0.5)
        else:  # Night
            base_occupancy = random.uniform(0.05, 0.3)
            
        passenger_count = int(capacity * base_occupancy * random.uniform(0.8, 1.2))
        passenger_count = min(capacity, max(0, passenger_count))  # Keep within capacity
        
        return {
            "vehicle_id": vehicle["vehicle_id"],
            "timestamp": get_timestamp(),
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "route_id": vehicle["route_id"],
            "vehicle_type": vehicle["vehicle_type"],
            "passenger_count": passenger_count
        }


class ServiceSimulator:
    def __init__(self, service_name, port, generator):
        self.service_name = service_name
        self.port = port
        self.generator = generator
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, port))
        self.server_socket.listen(5)
        self.clients = []
        self.running = True
        
    def handle_client(self, client_socket, client_address):
        print(f"[{self.service_name}] New connection from {client_address}")
        try:
            while self.running:
                data = self.generator.generate_data()
                message = json.dumps(data) + "\n"
                client_socket.sendall(message.encode('utf-8'))
                time.sleep(random.uniform(1, 5))  # Random interval between 1-5 seconds
        except (BrokenPipeError, ConnectionResetError):
            print(f"[{self.service_name}] Client {client_address} disconnected")
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
    
    def start(self):
        print(f"[{self.service_name}] Server started on port {self.port}")
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
    
    def accept_connections(self):
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append(client_socket)
                client_thread = threading.Thread(target=self.handle_client, 
                                              args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"[{self.service_name}] Error accepting connection: {e}")
    
    def stop(self):
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.server_socket.close()
        print(f"[{self.service_name}] Server stopped")


def main():
    print("Starting Smart City Data Simulator")
    print(f"Serving on {HOST}")
    
    # Initialize data generators
    traffic_gen = TrafficDataGenerator()
    parking_gen = ParkingDataGenerator()
    air_quality_gen = AirQualityDataGenerator()
    lighting_gen = LightingDataGenerator()
    waste_gen = WasteDataGenerator()
    transit_gen = TransitDataGenerator()
    
    # Create simulators
    simulators = [
        ServiceSimulator("Traffic", PORTS['traffic'], traffic_gen),
        ServiceSimulator("Parking", PORTS['parking'], parking_gen),
        ServiceSimulator("Air Quality", PORTS['air_quality'], air_quality_gen),
        ServiceSimulator("Lighting", PORTS['lighting'], lighting_gen),
        ServiceSimulator("Waste", PORTS['waste'], waste_gen),
        ServiceSimulator("Transit", PORTS['transit'], transit_gen)
    ]
    
    # Start all simulators
    for simulator in simulators:
        simulator.start()
    
    try:
        print("\nSimulators running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down simulators...")
        for simulator in simulators:
            simulator.stop()
        print("All simulators stopped.")


if __name__ == "__main__":
    main()
