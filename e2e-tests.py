import unittest
import requests
import socket
import json
import threading
import time
import subprocess
import os
from typing import Dict, Any, List

# API base URL - modify this to match your actual API endpoint
BASE_URL = "http://127.0.0.1:5050/"

# Simulator ports (matching the ones in the simulator)
SIMULATOR_PORTS = {
    'traffic': 5001,
    'parking': 5002,
    'air_quality': 5003,
    'lighting': 5004,
    'waste': 5005,
    'transit': 5006
}

SIMULATOR_HOST = '127.0.0.1'

# Endpoints for the different services
ENDPOINTS = {
    'traffic': f"{BASE_URL}/traffic",
    'parking': f"{BASE_URL}/parking",
    'air_quality': f"{BASE_URL}/air-quality",
    'lighting': f"{BASE_URL}/lighting",
    'waste': f"{BASE_URL}/waste",
    'transit': f"{BASE_URL}/transit"
}


class SimulatorClient:
    """Client that connects to the simulator and receives data"""

    def __init__(self, service_name: str, port: int):
        self.service_name = service_name
        self.port = port
        self.socket = None
        self.running = False
        self.data_received = []
        self.thread = None

    def start(self):
        """Connect to the simulator and start receiving data"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SIMULATOR_HOST, self.port))
        self.running = True
        self.thread = threading.Thread(target=self._receive_data)
        self.thread.daemon = True
        self.thread.start()

    def _receive_data(self):
        """Continuously receive data from the simulator"""
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        json_data = json.loads(line)
                        self.data_received.append(json_data)
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON: {line}")
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    def stop(self):
        """Stop receiving data and close the connection"""
        self.running = False
        if self.socket:
            self.socket.close()

    def get_data(self, count: int = 1, timeout: int = 10) -> List[Dict[str, Any]]:
        """Get a specific number of data points or wait until timeout"""
        start_time = time.time()
        while len(self.data_received) < count and time.time() - start_time < timeout:
            time.sleep(0.1)

        result = self.data_received[:count]
        self.data_received = self.data_received[count:]
        return result


class SmartCityAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Allow the simulator time to initialize
        time.sleep(3)

        # Initialize clients for each service
        cls.clients = {}
        for service, port in SIMULATOR_PORTS.items():
            client = SimulatorClient(service, port)
            try:
                client.start()
                cls.clients[service] = client
            except Exception as e:
                print(f"Failed to connect to {service} simulator: {e}")

    @classmethod
    def tearDownClass(cls):
        """Stop all clients and the simulator after tests"""
        for client in cls.clients.values():
            client.stop()

    def test_traffic_data_ingestion(self):
        """Test ingesting traffic data"""
        # Get data from the simulator
        traffic_data = self.clients['traffic'].get_data(count=3, timeout=15)
        self.assertTrue(len(traffic_data) > 0, "Failed to receive traffic data from simulator")

        # Test posting each traffic data record to the API
        for data in traffic_data:
            response = requests.post(ENDPOINTS['traffic'], json=data)
            self.assertEqual(response.status_code, 201, f"Failed to post traffic data: {response.text}")

        # Test retrieving the data back
        response = requests.get(ENDPOINTS['traffic'])
        self.assertEqual(response.status_code, 200)
        retrieved_data = response.json()

        # Check that at least one of our posted items exists in the response
        found = False
        for original in traffic_data:
            sensor_id = original['sensor_id']
            matching_items = [item for item in retrieved_data if item['sensor_id'] == sensor_id]
            if matching_items:
                found = True
                break

        self.assertTrue(found, "Could not find posted traffic data in GET response")

    def test_parking_data_ingestion(self):
        """Test ingesting parking data"""
        parking_data = self.clients['parking'].get_data(count=3, timeout=15)
        self.assertTrue(len(parking_data) > 0, "Failed to receive parking data from simulator")

        for data in parking_data:
            print(data)
            response = requests.post(ENDPOINTS['parking'], json=data)
            self.assertEqual(response.status_code, 201, f"Failed to post parking data: {response.text}")

        response = requests.get(ENDPOINTS['parking'])
        self.assertEqual(response.status_code, 200)
        retrieved_data = response.json()

        found = False
        for original in parking_data:
            lot_id = original['lot_id']
            matching_items = [item for item in retrieved_data if item['lot_id'] == lot_id]
            if matching_items:
                found = True
                break

        self.assertTrue(found, "Could not find posted parking data in GET response")

    def test_air_quality_data_ingestion(self):
        """Test ingesting air quality data"""
        air_quality_data = self.clients['air_quality'].get_data(count=3, timeout=15)
        self.assertTrue(len(air_quality_data) > 0, "Failed to receive air quality data from simulator")

        for data in air_quality_data:
            response = requests.post(ENDPOINTS['air_quality'], json=data)
            self.assertEqual(response.status_code, 201, f"Failed to post air quality data: {response.text}")

        response = requests.get(ENDPOINTS['air_quality'])
        self.assertEqual(response.status_code, 200)
        retrieved_data = response.json()

        found = False
        for original in air_quality_data:
            sensor_id = original['sensor_id']
            matching_items = [item for item in retrieved_data if item['sensor_id'] == sensor_id]
            if matching_items:
                found = True
                break

        self.assertTrue(found, "Could not find posted air quality data in GET response")

    def test_lighting_data_ingestion(self):
        """Test ingesting lighting data"""
        lighting_data = self.clients['lighting'].get_data(count=3, timeout=15)
        self.assertTrue(len(lighting_data) > 0, "Failed to receive lighting data from simulator")

        for data in lighting_data:
            response = requests.post(ENDPOINTS['lighting'], json=data)
            self.assertEqual(response.status_code, 201, f"Failed to post lighting data: {response.text}")

        response = requests.get(ENDPOINTS['lighting'])
        self.assertEqual(response.status_code, 200)
        retrieved_data = response.json()

        found = False
        for original in lighting_data:
            light_id = original['light_id']
            matching_items = [item for item in retrieved_data if item['light_id'] == light_id]
            if matching_items:
                found = True
                break

        self.assertTrue(found, "Could not find posted lighting data in GET response")

    def test_waste_data_ingestion(self):
        """Test ingesting waste management data"""
        waste_data = self.clients['waste'].get_data(count=3, timeout=15)
        self.assertTrue(len(waste_data) > 0, "Failed to receive waste data from simulator")

        for data in waste_data:
            response = requests.post(ENDPOINTS['waste'], json=data)
            self.assertEqual(response.status_code, 201, f"Failed to post waste data: {response.text}")

        response = requests.get(ENDPOINTS['waste'])
        self.assertEqual(response.status_code, 200)
        retrieved_data = response.json()

        found = False
        for original in waste_data:
            container_id = original['container_id']
            matching_items = [item for item in retrieved_data if item['container_id'] == container_id]
            if matching_items:
                found = True
                break

        self.assertTrue(found, "Could not find posted waste data in GET response")

    def test_transit_data_ingestion(self):
        """Test ingesting transit data"""
        transit_data = self.clients['transit'].get_data(count=3, timeout=15)
        self.assertTrue(len(transit_data) > 0, "Failed to receive transit data from simulator")

        for data in transit_data:
            response = requests.post(ENDPOINTS['transit'], json=data)
            self.assertEqual(response.status_code, 201, f"Failed to post transit data: {response.text}")

        response = requests.get(ENDPOINTS['transit'])
        self.assertEqual(response.status_code, 200)
        retrieved_data = response.json()

        found = False
        for original in transit_data:
            vehicle_id = original['vehicle_id']
            matching_items = [item for item in retrieved_data if item['vehicle_id'] == vehicle_id]
            if matching_items:
                found = True
                break

        self.assertTrue(found, "Could not find posted transit data in GET response")

    def test_data_validation(self):
        """Test API validation by sending invalid data"""
        # Test with missing required field
        invalid_traffic_data = {
            "sensor_id": "TRAFFIC-123456",
            "timestamp": "2023-04-09T10:15:30.123456",
            "location": {
                "latitude": 41.32,
                "longitude": 19.82
            },
            # Missing vehicle_count
            "average_speed": 45.5,
            "congestion_level": 2
        }

        response = requests.post(ENDPOINTS['traffic'], json=invalid_traffic_data)
        self.assertEqual(response.status_code, 400, "API should reject data with missing required fields")

        # Test with invalid data type
        invalid_air_data = {
            "sensor_id": "AIR-123456",
            "timestamp": "2023-04-09T10:15:30.123456",
            "location": {
                "latitude": 41.32,
                "longitude": 19.82
            },
            "aqi": "not a number",  # Should be an integer
            "temperature": 22.5,
            "humidity": 65.0
        }

        response = requests.post(ENDPOINTS['air_quality'], json=invalid_air_data)
        self.assertEqual(response.status_code, 400, "API should reject data with invalid data types")
