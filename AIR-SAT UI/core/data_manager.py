# core/data_manager.py
"""
Gestión centralizada de todos los datos del sistema GPS + GY91
Mantiene la misma estructura de datos y funcionalidad
"""

import math
import time
from datetime import datetime
from collections import deque
from .config import DATA_CONFIG, GPS_PRECISION

class DataManager:
    """Gestiona todos los datos del sistema de manera centralizada y optimizada"""
    
    def __init__(self):
        # Variables de control
        self.data_count = 0
        self.last_ui_update = time.time()
        self.ui_update_interval = DATA_CONFIG['ui_update_interval']
        self.max_data_points = DATA_CONFIG['max_data_points']
        
        # Buffer de tiempo
        self.time_buffer = deque(maxlen=self.max_data_points)
        
        # Inicializar buffers
        self._init_data_buffers()
        self._init_sensor_data()
        
        # Variables del mapa GPS
        self.map_center = {"lat": 0.0, "lon": 0.0}
        self.track_points = deque(maxlen=DATA_CONFIG['max_track_points'])
        self.waypoints = []
        
    def _init_data_buffers(self):
        """Inicializa todos los buffers de datos con la estructura original y nuevos sensores"""
        # Buffers para GPS - MANTIENE ESTRUCTURA EXACTA ORIGINAL
        self.gps_data = {
            'latitude': deque(maxlen=self.max_data_points),
            'longitude': deque(maxlen=self.max_data_points),
            'altitude': deque(maxlen=self.max_data_points),
            'speed': deque(maxlen=self.max_data_points),
            'satellites': deque(maxlen=self.max_data_points),
            'hdop': deque(maxlen=self.max_data_points),
            'vdop': deque(maxlen=self.max_data_points),
            'course': deque(maxlen=self.max_data_points),
            'fix_quality': deque(maxlen=self.max_data_points)
        }
        
        # Buffers para BMP280 - MANTIENE ESTRUCTURA EXACTA ORIGINAL
        self.bmp280_data = {
            'temp': deque(maxlen=self.max_data_points),
            'pressure': deque(maxlen=self.max_data_points),
            'altitude': deque(maxlen=self.max_data_points)
        }
        
        # Buffers para MPU9250 - MANTIENE ESTRUCTURA EXACTA ORIGINAL
        self.mpu9250_data = {
            'temp': deque(maxlen=self.max_data_points),
            'accel_x': deque(maxlen=self.max_data_points),
            'accel_y': deque(maxlen=self.max_data_points),
            'accel_z': deque(maxlen=self.max_data_points),
            'total_accel': deque(maxlen=self.max_data_points),
            'gyro_x': deque(maxlen=self.max_data_points),
            'gyro_y': deque(maxlen=self.max_data_points),
            'gyro_z': deque(maxlen=self.max_data_points),
            'mag_x': deque(maxlen=self.max_data_points),
            'mag_y': deque(maxlen=self.max_data_points),
            'mag_z': deque(maxlen=self.max_data_points),
            'roll': deque(maxlen=self.max_data_points),
            'pitch': deque(maxlen=self.max_data_points),
            'yaw': deque(maxlen=self.max_data_points),
            'heading': deque(maxlen=self.max_data_points)
        }
        
        # Nuevos buffers para SPS30 (Sensor de Partículas)
        self.sps30_data = {
            'pm1_0': deque(maxlen=self.max_data_points),
            'pm2_5': deque(maxlen=self.max_data_points),
            'pm4_0': deque(maxlen=self.max_data_points),
            'pm10': deque(maxlen=self.max_data_points),
            'nc0_5': deque(maxlen=self.max_data_points),
            'nc1_0': deque(maxlen=self.max_data_points),
            'nc2_5': deque(maxlen=self.max_data_points),
            'nc4_0': deque(maxlen=self.max_data_points),
            'nc10': deque(maxlen=self.max_data_points),
            'typical_size': deque(maxlen=self.max_data_points)
        }
        
        # Nuevos buffers para MQ135 (Calidad del Aire)
        self.mq135_data = {
            'lpg': deque(maxlen=self.max_data_points),
            'co': deque(maxlen=self.max_data_points),
            'smoke': deque(maxlen=self.max_data_points),
            'nh4': deque(maxlen=self.max_data_points),
            'co2': deque(maxlen=self.max_data_points),
            'alcohol': deque(maxlen=self.max_data_points),
            'ro': deque(maxlen=self.max_data_points)
        }
        
        # Nuevos buffers para MH-Z19 (CO₂)
        self.mhz19_data = {
            'co2_ppm': deque(maxlen=self.max_data_points),
            'temp': deque(maxlen=self.max_data_points),
            'range': deque(maxlen=self.max_data_points)
        }
        
        # Buffer para información de comunicación LoRa
        self.lora_data = {
            'rssi': deque(maxlen=self.max_data_points),
            'snr': deque(maxlen=self.max_data_points),
            'packet_count': deque(maxlen=self.max_data_points)
        }
    
    def _init_sensor_data(self):
        """Inicializa datos de sensores en tiempo real - ESTRUCTURA EXACTA ORIGINAL"""
        self.sensor_data = {
            # GPS - MANTIENE TODOS LOS CAMPOS ORIGINALES
            'latitude': 0.0, 'longitude': 0.0, 'gps_altitude': 0.0, 'speed': 0.0,
            'satellites': 0, 'fix_quality': 0, 'lat_dir': '', 'lon_dir': '',
            'hdop': 0.0, 'vdop': 0.0, 'utc_time': '',
            # BMP280 - MANTIENE TODOS LOS CAMPOS ORIGINALES
            'bmp_temp': 0.0, 'pressure': 0.0, 'bmp_altitude': 0.0,
            # MPU9250 - MANTIENE TODOS LOS CAMPOS ORIGINALES
            'mpu_temp': 0.0,
            'accel_x': 0.0, 'accel_y': 0.0, 'accel_z': 0.0,
            'gyro_x': 0.0, 'gyro_y': 0.0, 'gyro_z': 0.0,
            'mag_x': 0.0, 'mag_y': 0.0, 'mag_z': 0.0,
            'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0, 'heading': 0.0,
            # Calculados - MANTIENE TODOS LOS CAMPOS ORIGINALES
            'total_accel': 0.0, 'total_gyro': 0.0, 'total_mag': 0.0,
            'altitude_diff': 0.0,  # Diferencia GPS vs BMP280
            'last_update': 'No hay datos', 'system_status': 'Desconectado', 'data_quality': 'N/A'
        }
    
    def parse_gps_gy91_data(self, data_str):
        """
        Parsea datos del sistema GPS + GY91
        MANTIENE LA LÓGICA EXACTA DEL CÓDIGO ORIGINAL
        """
        try:
            parts = data_str.split(',')
            
            if len(parts) >= 28:  # 11 GPS + 17 GY91
                current_time = datetime.now()
                
                data = self.sensor_data
                
                # Datos GPS (campos 0-10) - EXACTAMENTE IGUAL AL ORIGINAL
                data['latitude'] = float(parts[0])
                data['longitude'] = float(parts[1])
                data['gps_altitude'] = float(parts[2])
                data['speed'] = float(parts[3])
                data['satellites'] = int(parts[4])
                data['fix_quality'] = int(parts[5])
                data['lat_dir'] = parts[6].strip()
                data['lon_dir'] = parts[7].strip()
                data['hdop'] = float(parts[8])
                data['vdop'] = float(parts[9])
                data['utc_time'] = parts[10].strip()
                
                # Datos GY91 - BMP280 (campos 11-13) - EXACTAMENTE IGUAL AL ORIGINAL
                data['bmp_temp'] = float(parts[11])
                data['pressure'] = float(parts[12])
                data['bmp_altitude'] = float(parts[13])
                
                # Datos GY91 - MPU9250 (campos 14-27) - EXACTAMENTE IGUAL AL ORIGINAL
                data['mpu_temp'] = float(parts[14])
                data['accel_x'] = float(parts[15])
                data['accel_y'] = float(parts[16])
                data['accel_z'] = float(parts[17])
                data['gyro_x'] = float(parts[18])
                data['gyro_y'] = float(parts[19])
                data['gyro_z'] = float(parts[20])
                data['mag_x'] = float(parts[21])
                data['mag_y'] = float(parts[22])
                data['mag_z'] = float(parts[23])
                data['roll'] = float(parts[24])
                data['pitch'] = float(parts[25])
                data['yaw'] = float(parts[26])
                data['heading'] = float(parts[27])
                
                # Calcular magnitudes totales - EXACTAMENTE IGUAL AL ORIGINAL
                data['total_accel'] = math.sqrt(data['accel_x']**2 + data['accel_y']**2 + data['accel_z']**2)
                data['total_gyro'] = math.sqrt(data['gyro_x']**2 + data['gyro_y']**2 + data['gyro_z']**2)
                data['total_mag'] = math.sqrt(data['mag_x']**2 + data['mag_y']**2 + data['mag_z']**2)
                
                # Calcular diferencia de altitudes - EXACTAMENTE IGUAL AL ORIGINAL
                data['altitude_diff'] = data['gps_altitude'] - data['bmp_altitude']
                
                # Actualizar timestamp - EXACTAMENTE IGUAL AL ORIGINAL
                data['last_update'] = current_time.strftime('%H:%M:%S.%f')[:-3]
                
                # Incrementar contador
                self.data_count += 1
                
                return True
                
        except (ValueError, IndexError):
            return False
        
        return False
    
    def add_to_plot_buffers(self, current_time):
        """
        Agrega datos a los buffers de plotting
        MISMA LÓGICA QUE EL CÓDIGO ORIGINAL
        """
        self.time_buffer.append(current_time)
        
        data = self.sensor_data
        
        # GPS - EXACTAMENTE IGUAL AL ORIGINAL
        self.gps_data['latitude'].append(data['latitude'])
        self.gps_data['longitude'].append(data['longitude'])
        self.gps_data['altitude'].append(data['gps_altitude'])
        self.gps_data['speed'].append(data['speed'])
        self.gps_data['satellites'].append(data['satellites'])
        self.gps_data['hdop'].append(data['hdop'])
        self.gps_data['vdop'].append(data['vdop'])
        
        # BMP280 - EXACTAMENTE IGUAL AL ORIGINAL
        self.bmp280_data['temp'].append(data['bmp_temp'])
        self.bmp280_data['pressure'].append(data['pressure'])
        self.bmp280_data['altitude'].append(data['bmp_altitude'])
        
        # MPU9250 - EXACTAMENTE IGUAL AL ORIGINAL
        self.mpu9250_data['temp'].append(data['mpu_temp'])
        self.mpu9250_data['accel_x'].append(data['accel_x'])
        self.mpu9250_data['accel_y'].append(data['accel_y'])
        self.mpu9250_data['accel_z'].append(data['accel_z'])
        self.mpu9250_data['gyro_x'].append(data['gyro_x'])
        self.mpu9250_data['gyro_y'].append(data['gyro_y'])
        self.mpu9250_data['gyro_z'].append(data['gyro_z'])
        self.mpu9250_data['mag_x'].append(data['mag_x'])
        self.mpu9250_data['mag_y'].append(data['mag_y'])
        self.mpu9250_data['mag_z'].append(data['mag_z'])
        self.mpu9250_data['roll'].append(data['roll'])
        self.mpu9250_data['pitch'].append(data['pitch'])
        self.mpu9250_data['yaw'].append(data['yaw'])
        self.mpu9250_data['heading'].append(data['heading'])
    
    def add_track_point(self):
        """
        Añade punto al track GPS
        MISMA LÓGICA QUE EL CÓDIGO ORIGINAL
        """
        if self.sensor_data['latitude'] != 0.0 and self.sensor_data['longitude'] != 0.0:
            new_point = {
                'lat': self.sensor_data['latitude'],
                'lon': self.sensor_data['longitude'],
                'time': datetime.now(),
                'hdop': self.sensor_data['hdop']
            }
            self.track_points.append(new_point)
            return True
        return False
    
    def add_waypoint(self, name=None):
        """
        Añade waypoint en la posición actual
        MISMA LÓGICA QUE EL CÓDIGO ORIGINAL
        """
        if self.sensor_data['latitude'] != 0.0 and self.sensor_data['longitude'] != 0.0:
            if not name:
                name = f"WP{len(self.waypoints)+1}"
                
            waypoint = {
                'lat': self.sensor_data['latitude'],
                'lon': self.sensor_data['longitude'],
                'name': name,
                'time': datetime.now().strftime('%H:%M:%S'),
                'hdop': self.sensor_data['hdop']
            }
            self.waypoints.append(waypoint)
            return waypoint
        return None
    
    def update_buffer_size(self, new_size):
        """
        Actualiza el tamaño del buffer de datos
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        try:
            new_max = int(new_size)
            self.max_data_points = new_max
            
            # Recrear buffers con nuevo tamaño - EXACTAMENTE IGUAL AL ORIGINAL
            self.time_buffer = deque(list(self.time_buffer)[-new_max:], maxlen=new_max)
            
            for key in self.gps_data:
                self.gps_data[key] = deque(list(self.gps_data[key])[-new_max:], maxlen=new_max)
            for key in self.bmp280_data:
                self.bmp280_data[key] = deque(list(self.bmp280_data[key])[-new_max:], maxlen=new_max)
            for key in self.mpu9250_data:
                self.mpu9250_data[key] = deque(list(self.mpu9250_data[key])[-new_max:], maxlen=new_max)
                
            return True
        except ValueError:
            return False
    
    def clear_plot_data(self):
        """
        Limpia todos los datos de las gráficas
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        self.time_buffer.clear()
        for key in self.gps_data:
            self.gps_data[key].clear()
        for key in self.bmp280_data:
            self.bmp280_data[key].clear()
        for key in self.mpu9250_data:
            self.mpu9250_data[key].clear()
    
    def clear_track(self):
        """Limpia el track del mapa"""
        self.track_points.clear()
        self.waypoints.clear()
    
    def should_update_ui(self):
        """
        Verifica si debe actualizar la UI basado en throttling
        MANTIENE LA LÓGICA EXACTA DEL ORIGINAL
        """
        current_time = time.time()
        if current_time - self.last_ui_update >= self.ui_update_interval:
            self.last_ui_update = current_time
            return True
        return False
    
    def get_data_quality(self):
        """
        Calcula la calidad de datos basada en GPS y sensores
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        sat_count = self.sensor_data['satellites']
        fix_quality = self.sensor_data['fix_quality']
        total_accel = self.sensor_data['total_accel']
        
        if sat_count >= GPS_PRECISION['excellent_satellites'] and fix_quality >= 2 and GPS_PRECISION['accel_tolerance'][0] < total_accel < GPS_PRECISION['accel_tolerance'][1]:
            return "ALTA", "#00aa00"
        elif sat_count >= GPS_PRECISION['good_satellites'] and fix_quality >= 1:
            return "MEDIA", "#ffaa00"
        else:
            return "BAJA", "#ff4444"
    
    def get_cardinal_direction(self, heading):
        """
        Convierte grados a dirección cardinal
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = int((heading + 11.25) / 22.5) % 16
        return directions[index]
    
    def lat_lon_to_meters(self, lat1, lon1, lat2, lon2):
        """
        Convierte diferencia lat/lon a metros usando fórmula haversine simplificada
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        # Para distancias cortas (< 1km) podemos usar aproximación lineal
        R = 6371000  # Radio de la Tierra en metros
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        # Aproximación para distancias cortas
        lat_avg = math.radians((lat1 + lat2) / 2)
        
        dx = R * dlon * math.cos(lat_avg)
        dy = R * dlat
        
        return dx, dy
    
    def calculate_track_statistics(self):
        """
        Calcula estadísticas del track GPS
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        if len(self.track_points) <= 1:
            return {"distance": 0.0, "dispersion": 0.0, "points": len(self.track_points)}
        
        # Calcular distancia total - EXACTAMENTE IGUAL AL ORIGINAL
        total_distance = 0.0
        for i in range(1, len(self.track_points)):
            prev_point = self.track_points[i-1]
            curr_point = self.track_points[i]
            
            dx, dy = self.lat_lon_to_meters(
                prev_point['lat'], prev_point['lon'],
                curr_point['lat'], curr_point['lon']
            )
            distance = math.sqrt(dx*dx + dy*dy)
            total_distance += distance
        
        # Calcular dispersión (desviación estándar de posiciones) - EXACTAMENTE IGUAL AL ORIGINAL
        dispersion = 0.0
        if len(self.track_points) > 2:
            # Calcular centro geométrico
            center_lat = sum(p['lat'] for p in self.track_points) / len(self.track_points)
            center_lon = sum(p['lon'] for p in self.track_points) / len(self.track_points)
            
            # Calcular dispersión RMS
            rms_error = 0.0
            for point in self.track_points:
                dx, dy = self.lat_lon_to_meters(center_lat, center_lon, point['lat'], point['lon'])
                rms_error += dx*dx + dy*dy
                
            dispersion = math.sqrt(rms_error / len(self.track_points))
        
        return {
            "distance": total_distance,
            "dispersion": dispersion, 
            "points": len(self.track_points)
        }
    
    def get_current_position(self):
        """Retorna la posición GPS actual"""
        return {
            'lat': self.sensor_data['latitude'],
            'lon': self.sensor_data['longitude'],
            'valid': self.sensor_data['latitude'] != 0.0 and self.sensor_data['longitude'] != 0.0
        }