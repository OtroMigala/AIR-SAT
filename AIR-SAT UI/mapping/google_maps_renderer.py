# mapping/google_maps_renderer.py
"""
Google Maps renderer for AIR-SAT mapping system
Replaces the tkinter Canvas with real Google Maps integration
"""

import os
import json
import tempfile
import webbrowser
import threading
import time
import http.server
import socketserver
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import MAP_CONFIG, GPS_PRECISION
from .google_maps_config import google_maps_config

class GoogleMapsRenderer:
    """
    Google Maps renderer that integrates with the existing AIR-SAT data flow
    Maintains the same interface as the original MapRenderer
    """
    
    def __init__(self, parent_frame, data_manager, image_handler=None):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        self.image_handler = image_handler
        
        # Map state variables (same as original)
        self.map_center = {"lat": 0.0, "lon": 0.0}
        self.zoom_level = 15  # Google Maps zoom level (1-20)
        self.meters_per_pixel = 1.0
        self.map_colors = MAP_CONFIG['colors']
        
        # Display state
        self.show_grid = True
        self.show_precision_circle = True
        self.show_background = True
        
        # Web server for map
        self.map_server = None
        self.map_port = 8765
        self.map_file_path = None
        
        # Zone data for environmental mapping
        self.air_quality_zones = []
        self.particle_zones = []
        self.track_data = []
        
        # Setup the web-based map interface
        self.setup_map_interface()
        
    def setup_map_interface(self):
        """Setup the Google Maps interface within the tkinter frame"""
        # Create a frame for the map controls and webview
        self.map_frame = ttk.Frame(self.parent_frame)
        self.map_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Control panel
        control_frame = ttk.Frame(self.map_frame)
        control_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(control_frame, text="Google Maps - AIR-SAT Environmental Mapping", 
                 font=('Arial', 12, 'bold')).pack(side="left")
        
        # Map controls
        ttk.Button(control_frame, text="Refresh Map", 
                  command=self.update_map).pack(side="right", padx=2)
        ttk.Button(control_frame, text="Center on GPS", 
                  command=self.center_on_current_position).pack(side="right", padx=2)
        ttk.Button(control_frame, text="Open in Browser", 
                  command=self.open_in_browser).pack(side="right", padx=2)
        ttk.Button(control_frame, text="API Key", 
                  command=self.configure_api_key).pack(side="right", padx=2)
        
        # Info panel
        info_frame = ttk.Frame(self.map_frame)
        info_frame.pack(fill="x", pady=(0, 5))
        
        self.status_label = ttk.Label(info_frame, text="Initializing Google Maps...")
        self.status_label.pack(side="left")
        
        self.coords_label = ttk.Label(info_frame, text="GPS: No data")
        self.coords_label.pack(side="right")
        
        # Web view area (placeholder for now)
        self.web_frame = ttk.Frame(self.map_frame, relief="sunken", borderwidth=2)
        self.web_frame.pack(fill="both", expand=True)
        
        # Check if API key is configured
        api_status = "[OK] API Key Configured" if google_maps_config.is_configured() else "[REQUIRED] API Key Required"
        
        # Instructions label
        self.instructions_label = ttk.Label(
            self.web_frame, 
            text=f"Google Maps Integration\n\nStatus: {api_status}\n\nClick 'Open in Browser' to view the interactive map\nThe map will update automatically with GPS data and environmental zones\n\nUse 'API Key' button if you need to configure a different key",
            justify="center",
            font=('Arial', 10)
        )
        self.instructions_label.pack(expand=True)
        
        # Generate initial map
        self.generate_map_html()
        self.start_map_server()
        
    def generate_map_html(self):
        """Generate the HTML file with Google Maps integration"""
        # Get current position or use default
        current_lat = self.data_manager.sensor_data.get('latitude', 40.7128)
        current_lon = self.data_manager.sensor_data.get('longitude', -74.0060)
        
        if current_lat == 0.0 and current_lon == 0.0:
            current_lat, current_lon = 40.7128, -74.0060  # Default to NYC
        
        self.map_center = {"lat": current_lat, "lon": current_lon}
        
        # Prepare track data
        track_points = []
        for point in self.data_manager.track_points:
            track_points.append({
                'lat': point['lat'],
                'lng': point['lon'],
                'time': point['time'].isoformat() if hasattr(point['time'], 'isoformat') else str(point['time']),
                'hdop': point.get('hdop', 0)
            })
        
        # Prepare waypoints
        waypoints = []
        for wp in self.data_manager.waypoints:
            waypoints.append({
                'lat': wp['lat'],
                'lng': wp['lon'],
                'name': wp['name'],
                'time': wp.get('time', '')
            })
        
        # Prepare environmental zones based on sensor data
        try:
            air_quality_zones = self.generate_air_quality_zones()
        except Exception as e:
            print(f"Error generating air quality zones: {e}")
            air_quality_zones = []
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AIR-SAT Environmental Mapping</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        #map {{
            height: 100vh;
            width: 100%;
        }}
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
        }}
        .info-window {{
            max-width: 300px;
            font-size: 14px;
        }}
        .legend {{
            background: white;
            border-radius: 3px;
            bottom: 30px;
            box-shadow: 0 1px 2px rgba(60,64,67,.3);
            margin: 10px;
            padding: 12px;
            position: absolute;
            right: 10px;
            z-index: 1;
        }}
        .legend h3 {{
            margin-top: 0;
            color: #333;
        }}
        .legend-item {{
            margin: 5px 0;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 15px;
            margin-right: 8px;
            border: 1px solid #ccc;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="legend">
        <h3>🛰️ AIR-SAT Legend</h3>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #ff4444;"></span>
            Current Position
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #00ff00;"></span>
            GPS Track
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #00aaff;"></span>
            Waypoints
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #ffaa00;"></span>
            High Pollution
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #00aa00;"></span>
            Good Air Quality
        </div>
    </div>

    <script>
        let map;
        let trackPath;
        let currentMarker;
        let precisionCircle;
        let markers = [];
        let zones = [];

        // Data from Python
        const trackPoints = {json.dumps(track_points)};
        const waypoints = {json.dumps(waypoints)};
        const currentPosition = {{ lat: {current_lat}, lng: {current_lon} }};
        const airQualityZones = {json.dumps(air_quality_zones)};
        
        function initMap() {{
            // Initialize map
            map = new google.maps.Map(document.getElementById("map"), {{
                zoom: {self.zoom_level},
                center: currentPosition,
                mapTypeId: google.maps.MapTypeId.HYBRID
            }});

            // Draw track if available
            if (trackPoints.length > 0) {{
                drawTrack();
            }}

            // Draw waypoints
            drawWaypoints();

            // Draw current position
            drawCurrentPosition();

            // Draw environmental zones
            drawEnvironmentalZones();

            // Add event listeners
            map.addListener("center_changed", () => {{
                // Update center when map is moved
                const center = map.getCenter();
                console.log("Map center:", center.lat(), center.lng());
            }});
        }}

        function drawTrack() {{
            if (trackPath) {{
                trackPath.setMap(null);
            }}

            trackPath = new google.maps.Polyline({{
                path: trackPoints,
                geodesic: true,
                strokeColor: "#00ff00",
                strokeOpacity: 1.0,
                strokeWeight: 3,
            }});

            trackPath.setMap(map);

            // Add markers for track points
            trackPoints.forEach((point, index) => {{
                if (index % 5 === 0) {{ // Show every 5th point to avoid clutter
                    const marker = new google.maps.Marker({{
                        position: point,
                        map: map,
                        icon: {{
                            path: google.maps.SymbolPath.CIRCLE,
                            scale: 4,
                            fillColor: "#00ff00",
                            fillOpacity: 0.8,
                            strokeWeight: 1,
                            strokeColor: "#ffffff"
                        }},
                        title: `Track Point ${{index + 1}}\\nTime: ${{point.time}}\\nHDOP: ${{point.hdop}}`
                    }});
                    
                    markers.push(marker);
                }}
            }});
        }}

        function drawWaypoints() {{
            waypoints.forEach((waypoint, index) => {{
                const marker = new google.maps.Marker({{
                    position: waypoint,
                    map: map,
                    icon: {{
                        path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                        scale: 8,
                        fillColor: "#00aaff",
                        fillOpacity: 1.0,
                        strokeWeight: 2,
                        strokeColor: "#ffffff"
                    }},
                    title: waypoint.name
                }});

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div class="info-window">
                            <h3>📌 ${{waypoint.name}}</h3>
                            <p><strong>Coordinates:</strong><br>
                            ${{waypoint.lat.toFixed(6)}}°, ${{waypoint.lng.toFixed(6)}}°</p>
                            <p><strong>Time:</strong> ${{waypoint.time}}</p>
                        </div>
                    `
                }});

                marker.addListener("click", () => {{
                    infoWindow.open(map, marker);
                }});

                markers.push(marker);
            }});
        }}

        function drawCurrentPosition() {{
            if (currentMarker) {{
                currentMarker.setMap(null);
            }}
            if (precisionCircle) {{
                precisionCircle.setMap(null);
            }}

            // Current position marker
            currentMarker = new google.maps.Marker({{
                position: currentPosition,
                map: map,
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 12,
                    fillColor: "#ff4444",
                    fillOpacity: 1.0,
                    strokeWeight: 3,
                    strokeColor: "#ffffff"
                }},
                title: "Current GPS Position"
            }});

            // Precision circle based on HDOP
            const hdop = {self.data_manager.sensor_data.get('hdop', 0)};
            if (hdop > 0) {{
                const radiusMeters = hdop * {GPS_PRECISION['base_error_meters']};
                
                precisionCircle = new google.maps.Circle({{
                    strokeColor: "#ffaa00",
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: "#ffaa00",
                    fillOpacity: 0.2,
                    map: map,
                    center: currentPosition,
                    radius: radiusMeters
                }});
            }}

            // Info window for current position
            const infoWindow = new google.maps.InfoWindow({{
                content: `
                    <div class="info-window">
                        <h3>🛰️ Current Position</h3>
                        <p><strong>Coordinates:</strong><br>
                        ${{currentPosition.lat.toFixed(6)}}°, ${{currentPosition.lng.toFixed(6)}}°</p>
                        <p><strong>HDOP:</strong> ${{hdop.toFixed(2)}} (±${{(hdop * {GPS_PRECISION['base_error_meters']}).toFixed(1)}}m)</p>
                        <p><strong>Satellites:</strong> {self.data_manager.sensor_data.get('satellites', 0)}</p>
                    </div>
                `
            }});

            currentMarker.addListener("click", () => {{
                infoWindow.open(map, currentMarker);
            }});
        }}

        function drawEnvironmentalZones() {{
            // Clear existing zones
            zones.forEach(zone => zone.setMap(null));
            zones = [];

            airQualityZones.forEach(zone => {{
                const circle = new google.maps.Circle({{
                    strokeColor: zone.color,
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: zone.color,
                    fillOpacity: 0.3,
                    map: map,
                    center: {{ lat: zone.lat, lng: zone.lng }},
                    radius: zone.radius
                }});

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div class="info-window">
                            <h3>🌍 Environmental Zone</h3>
                            <p><strong>Air Quality:</strong> ${{zone.quality}}</p>
                            <p><strong>PM2.5:</strong> ${{zone.pm25}} µg/m³</p>
                            <p><strong>CO₂:</strong> ${{zone.co2}} ppm</p>
                            <p><strong>Time:</strong> ${{zone.time}}</p>
                        </div>
                    `
                }});

                circle.addListener("click", () => {{
                    infoWindow.setPosition(circle.getCenter());
                    infoWindow.open(map);
                }});

                zones.push(circle);
            }});
        }}

        function updateMapData(newData) {{
            // Function to update map with new data from Python
            console.log("Updating map with new data:", newData);
            
            // Update current position
            if (newData.currentPosition) {{
                currentPosition.lat = newData.currentPosition.lat;
                currentPosition.lng = newData.currentPosition.lng;
                drawCurrentPosition();
            }}

            // Update track
            if (newData.trackPoints) {{
                trackPoints.length = 0;
                trackPoints.push(...newData.trackPoints);
                drawTrack();
            }}

            // Update environmental zones
            if (newData.airQualityZones) {{
                airQualityZones.length = 0;
                airQualityZones.push(...newData.airQualityZones);
                drawEnvironmentalZones();
            }}
        }}

        // Auto-refresh every 5 seconds
        setInterval(() => {{
            fetch('/api/data')
                .then(response => response.json())
                .then(data => updateMapData(data))
                .catch(error => console.log('Update not available:', error));
        }}, 5000);
    </script>

    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key={google_maps_config.get_api_key()}&callback=initMap">
    </script>
</body>
</html>
"""
        
        # Save to temporary file
        if not self.map_file_path:
            temp_dir = tempfile.gettempdir()
            self.map_file_path = os.path.join(temp_dir, "airsat_map.html")
        
        with open(self.map_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return self.map_file_path
    
    def generate_air_quality_zones(self):
        """Generate environmental zones based on sensor data"""
        zones = []
        
        # Create zones from recent track points with environmental data
        for i, point in enumerate(list(self.data_manager.track_points)[-10:]):  # Last 10 points
            # Get corresponding sensor data (simplified - in real implementation would need time correlation)
            pm25 = self.data_manager.sensor_data.get('pm2_5', 0)
            co2 = max(
                self.data_manager.sensor_data.get('co2_ppm_mhz19', 0),
                self.data_manager.sensor_data.get('co2_ppm_mq135', 0)
            )
            
            # Determine zone color based on air quality
            if pm25 <= 12 and co2 <= 1000:
                color = "#00aa00"  # Good
                quality = "Good"
            elif pm25 <= 35 and co2 <= 2000:
                color = "#ffff00"  # Moderate
                quality = "Moderate"
            elif pm25 <= 55 and co2 <= 5000:
                color = "#ff8800"  # Unhealthy
                quality = "Unhealthy"
            else:
                color = "#ff0000"  # Hazardous
                quality = "Hazardous"
            
            zones.append({
                'lat': point['lat'],
                'lng': point['lon'],
                'radius': 50,  # 50 meter radius
                'color': color,
                'quality': quality,
                'pm25': pm25,
                'co2': co2,
                'time': point['time'].strftime('%H:%M:%S') if hasattr(point['time'], 'strftime') else str(point['time'])
            })
        
        return zones
    
    def start_map_server(self):
        """Start a simple HTTP server to serve the map"""
        try:
            class MapHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=tempfile.gettempdir(), **kwargs)
                
                def log_message(self, format, *args):
                    # Suppress HTTP server logs
                    pass
                
                def do_GET(self):
                    try:
                        if self.path == '/api/data':
                            # Serve updated data as JSON
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            
                            # Get current data safely
                            try:
                                current_lat = self.server.data_manager.sensor_data.get('latitude', 0)
                                current_lon = self.server.data_manager.sensor_data.get('longitude', 0)
                                
                                data = {
                                    'currentPosition': {'lat': current_lat, 'lng': current_lon} if current_lat != 0 else None,
                                    'trackPoints': [{'lat': p['lat'], 'lng': p['lon']} for p in self.server.data_manager.track_points],
                                    'airQualityZones': self.server.renderer.generate_air_quality_zones()
                                }
                                
                                self.wfile.write(json.dumps(data).encode())
                            except Exception as e:
                                print(f"Error serving API data: {e}")
                                self.wfile.write(json.dumps({'error': 'Data not available'}).encode())
                        else:
                            super().do_GET()
                    except Exception as e:
                        print(f"HTTP request error: {e}")
            
            # Find available port
            self.map_server = None
            for port in range(8765, 8775):
                try:
                    self.map_server = socketserver.TCPServer(("localhost", port), MapHandler)
                    self.map_server.data_manager = self.data_manager
                    self.map_server.renderer = self
                    self.map_port = port
                    break
                except OSError as e:
                    print(f"Port {port} unavailable: {e}")
                    continue
            
            if self.map_server:
                # Start server in background thread
                server_thread = threading.Thread(target=self.map_server.serve_forever, daemon=True)
                server_thread.start()
                
                self.status_label.config(text=f"Map server running on port {self.map_port}")
                print(f"Google Maps server started on port {self.map_port}")
            else:
                self.status_label.config(text="Could not start map server - all ports busy")
                print("Could not start map server - all ports in range 8765-8774 are busy")
                
        except Exception as e:
            error_msg = f"Server error: {str(e)}"
            self.status_label.config(text=error_msg)
            print(error_msg)
    
    def configure_api_key(self):
        """Configure Google Maps API key"""
        google_maps_config.prompt_for_api_key()
        self.update_map()  # Regenerate map with new API key
    
    def open_in_browser(self):
        """Open the map in the default web browser"""
        try:
            if self.map_file_path and os.path.exists(self.map_file_path):
                map_url = f"http://localhost:{self.map_port}/airsat_map.html"
                print(f"Opening map in browser: {map_url}")
                webbrowser.open(map_url)
                self.status_label.config(text="Map opened in browser")
            else:
                self.update_map()  # Regenerate map file
                if self.map_file_path and os.path.exists(self.map_file_path):
                    map_url = f"http://localhost:{self.map_port}/airsat_map.html"
                    webbrowser.open(map_url)
                    self.status_label.config(text="Map opened in browser")
                else:
                    messagebox.showerror("Error", "Could not generate map file. Check console for errors.")
        except Exception as e:
            error_msg = f"Error opening browser: {str(e)}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)
    
    def center_on_current_position(self):
        """Center map on current GPS position"""
        lat = self.data_manager.sensor_data.get('latitude', 0)
        lon = self.data_manager.sensor_data.get('longitude', 0)
        
        if lat != 0 and lon != 0:
            self.map_center = {"lat": lat, "lon": lon}
            self.update_map()
            self.coords_label.config(text=f"GPS: {lat:.6f}°, {lon:.6f}°")
        else:
            messagebox.showwarning("No GPS", "No valid GPS coordinates available")
    
    def update_map(self):
        """Update the map with current data"""
        try:
            self.generate_map_html()
            
            # Update status
            lat = self.data_manager.sensor_data.get('latitude', 0)
            lon = self.data_manager.sensor_data.get('longitude', 0)
            
            if lat != 0 and lon != 0:
                self.coords_label.config(text=f"GPS: {lat:.6f}°, {lon:.6f}°")
                self.status_label.config(text="Map updated with current data")
            else:
                self.coords_label.config(text="GPS: No data")
                self.status_label.config(text="Map updated (no GPS data)")
                
        except Exception as e:
            self.status_label.config(text=f"Update error: {str(e)}")
    
    # Methods to maintain compatibility with original MapRenderer interface
    def draw_initial_map(self):
        """Initialize the map (compatibility method)"""
        self.update_map()
    
    def update_map_params(self, map_center, zoom_level, meters_per_pixel):
        """Update map parameters (compatibility method)"""
        self.map_center = map_center.copy()
        self.zoom_level = max(1, min(20, int(15 - (zoom_level - 1) * 2)))  # Convert to Google Maps zoom
        self.meters_per_pixel = meters_per_pixel
    
    def geo_to_canvas(self, lat, lon):
        """Convert geo coordinates to canvas coordinates (compatibility method)"""
        # Return dummy values for compatibility
        return 400, 300
    
    def canvas_to_geo(self, canvas_x, canvas_y):
        """Convert canvas coordinates to geo coordinates (compatibility method)"""
        # Return current center for compatibility
        return self.map_center["lat"], self.map_center["lon"]
    
    def get_visible_bounds(self):
        """Get visible map bounds (compatibility method)"""
        # Return approximate bounds based on center and zoom
        lat_offset = 0.01 * (20 - self.zoom_level)
        lon_offset = 0.01 * (20 - self.zoom_level)
        
        return {
            'north': self.map_center["lat"] + lat_offset,
            'south': self.map_center["lat"] - lat_offset,
            'east': self.map_center["lon"] + lon_offset,
            'west': self.map_center["lon"] - lon_offset
        }
    
    def clear_map(self):
        """Clear map elements (compatibility method)"""
        self.update_map()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.map_server:
            self.map_server.shutdown()
            self.map_server = None
        
        if self.map_file_path and os.path.exists(self.map_file_path):
            try:
                os.remove(self.map_file_path)
            except:
                pass