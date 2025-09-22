#!/usr/bin/env python3
"""
Test script for Google Maps integration in AIR-SAT mapping system
Demonstrates the new Google Maps functionality with simulated data
"""

import tkinter as tk
import customtkinter as ctk
import sys
import os
import time
import threading
import random
import math
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_manager import DataManager
from mapping.gps_map import GPSMapSystem

class TestGoogleMaps:
    """Test application for Google Maps integration"""
    
    def __init__(self):
        # Initialize CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("AIR-SAT Google Maps Test")
        self.root.geometry("1400x900")
        
        # Initialize data manager with test data
        self.data_manager = DataManager()
        self.setup_test_data()
        
        # Create UI
        self.setup_ui()
        
        # Start data simulation
        self.simulation_running = False
        self.start_simulation()
    
    def setup_test_data(self):
        """Setup initial test data"""
        # Simulate GPS position (Madrid, Spain)
        self.base_lat = 40.4168
        self.base_lon = -3.7038
        
        # Initialize sensor data with test values
        self.data_manager.sensor_data.update({
            'latitude': self.base_lat,
            'longitude': self.base_lon,
            'gps_altitude': 650.0,
            'speed': 0.0,
            'satellites': 8,
            'fix_quality': 2,
            'hdop': 1.2,
            'heading': 45.0,
            # Environmental data
            'pm2_5': 15.0,
            'pm10': 25.0,
            'co2_ppm_mhz19': 450,
            'co2_ppm_mq135': 440,
            'lpg_ppm': 0.1,
            'co_ppm': 2.5,
            'last_update': datetime.now().strftime('%H:%M:%S.%f')[:-3],
            'system_status': 'Simulación Activa'
        })
        
        # Add some initial track points
        for i in range(5):
            offset_lat = self.base_lat + (i * 0.0001)
            offset_lon = self.base_lon + (i * 0.0001)
            
            self.data_manager.track_points.append({
                'lat': offset_lat,
                'lon': offset_lon,
                'time': datetime.now(),
                'hdop': 1.0 + (i * 0.1)
            })
        
        # Add some waypoints
        self.data_manager.waypoints.extend([
            {
                'lat': self.base_lat + 0.001,
                'lon': self.base_lon + 0.001,
                'name': 'Test Point 1',
                'time': '12:00:00',
                'hdop': 1.1
            },
            {
                'lat': self.base_lat - 0.001,
                'lon': self.base_lon - 0.001,
                'name': 'Test Point 2',
                'time': '12:05:00',
                'hdop': 1.3
            }
        ])
        
        # Set map center
        self.data_manager.map_center = {
            "lat": self.base_lat,
            "lon": self.base_lon
        }
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🛰️ AIR-SAT Google Maps Integration Test",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Instructions
        instructions = ctk.CTkTextbox(main_frame, height=100)
        instructions.pack(fill="x", padx=10, pady=5)
        instructions.insert("0.0", 
            "INSTRUCCIONES PARA PRUEBA DE GOOGLE MAPS:\n\n"
            "1. Configure su Google Maps API Key usando el botón '🔑 API Key'\n"
            "2. Seleccione 'Google Maps' en el dropdown de Map Type\n"
            "3. Haga clic en '🌐 Open in Browser' para ver el mapa interactivo\n"
            "4. Use '📍 Center on GPS' para centrar en la posición simulada\n"
            "5. La simulación muestra datos de calidad del aire y partículas\n\n"
            "NOTA: Sin API Key, el mapa mostrará un error pero la interfaz funcionará."
        )
        instructions.configure(state="disabled")
        
        # Control panel
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Simulation controls
        ctk.CTkLabel(control_frame, text="Simulation Controls:", 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        
        self.sim_button = ctk.CTkButton(
            control_frame, text="⏸️ Pause Simulation", 
            command=self.toggle_simulation
        )
        self.sim_button.pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame, text="📍 Add Random Waypoint", 
            command=self.add_random_waypoint
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame, text="🗑️ Clear Track", 
            command=self.clear_track
        ).pack(side="left", padx=5)
        
        # Status
        self.status_label = ctk.CTkLabel(
            control_frame, text="Status: Simulation Running"
        )
        self.status_label.pack(side="right", padx=10)
        
        # GPS Map System
        map_frame = ctk.CTkFrame(main_frame)
        map_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.gps_map = GPSMapSystem(map_frame, self.data_manager)
    
    def start_simulation(self):
        """Start the data simulation"""
        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
    
    def simulation_loop(self):
        """Main simulation loop"""
        angle = 0
        
        while True:
            if self.simulation_running:
                # Simulate GPS movement in a circle
                radius = 0.001  # About 100 meters
                self.data_manager.sensor_data['latitude'] = self.base_lat + radius * math.cos(angle)
                self.data_manager.sensor_data['longitude'] = self.base_lon + radius * math.sin(angle)
                
                # Simulate heading
                self.data_manager.sensor_data['heading'] = (angle * 180 / math.pi) % 360
                
                # Simulate environmental data
                self.data_manager.sensor_data['pm2_5'] = 10 + 15 * (1 + math.sin(angle * 2))
                self.data_manager.sensor_data['pm10'] = 20 + 20 * (1 + math.cos(angle * 1.5))
                self.data_manager.sensor_data['co2_ppm_mhz19'] = int(400 + 200 * (1 + math.sin(angle * 0.5)))
                
                # Simulate HDOP variation
                self.data_manager.sensor_data['hdop'] = 1.0 + 0.5 * abs(math.sin(angle * 3))
                
                # Update timestamp
                self.data_manager.sensor_data['last_update'] = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                
                # Add track point occasionally
                if random.random() < 0.1:  # 10% chance
                    self.data_manager.add_track_point()
                
                # Update map if initialized
                if hasattr(self.gps_map, 'map_initialized') and self.gps_map.map_initialized:
                    self.gps_map.update_map_info()
                
                angle += 0.05  # Increment angle
                
            time.sleep(2)  # Update every 2 seconds
    
    def toggle_simulation(self):
        """Toggle simulation on/off"""
        self.simulation_running = not self.simulation_running
        
        if self.simulation_running:
            self.sim_button.configure(text="⏸️ Pause Simulation")
            self.status_label.configure(text="Status: Simulation Running")
        else:
            self.sim_button.configure(text="▶️ Resume Simulation")
            self.status_label.configure(text="Status: Simulation Paused")
    
    def add_random_waypoint(self):
        """Add a random waypoint near current position"""
        current_lat = self.data_manager.sensor_data['latitude']
        current_lon = self.data_manager.sensor_data['longitude']
        
        # Add random offset (up to 500 meters)
        offset_lat = current_lat + random.uniform(-0.005, 0.005)
        offset_lon = current_lon + random.uniform(-0.005, 0.005)
        
        waypoint_name = f"Random_{len(self.data_manager.waypoints)+1}"
        
        waypoint = {
            'lat': offset_lat,
            'lon': offset_lon,
            'name': waypoint_name,
            'time': datetime.now().strftime('%H:%M:%S'),
            'hdop': self.data_manager.sensor_data['hdop']
        }
        
        self.data_manager.waypoints.append(waypoint)
        
        # Update map
        if hasattr(self.gps_map, 'map_initialized') and self.gps_map.map_initialized:
            self.gps_map.update_map()
    
    def clear_track(self):
        """Clear the GPS track"""
        self.data_manager.clear_track()
        if hasattr(self.gps_map, 'map_initialized') and self.gps_map.map_initialized:
            self.gps_map.update_map()
    
    def run(self):
        """Run the test application"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting AIR-SAT Google Maps Test...")
    print("Make sure you have a Google Maps API key configured.")
    
    app = TestGoogleMaps()
    app.run()