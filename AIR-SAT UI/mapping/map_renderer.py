# mapping/map_renderer.py
"""
Renderizado del mapa GPS con optimización de rendimiento - VERSIÓN CORREGIDA
Corrige el problema de renderizado de imágenes de fondo
"""

import tkinter as tk
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import MAP_CONFIG, GRID_CONFIG, GPS_PRECISION

class MapRenderer:
    """
    Renderiza todos los elementos del mapa GPS
    VERSIÓN CORREGIDA - Arregla problemas de imagen de fondo
    """
    
    def __init__(self, canvas, data_manager, image_handler):
        self.canvas = canvas
        self.data_manager = data_manager
        self.image_handler = image_handler
        
        # Variables del mapa
        self.map_center = {"lat": 0.0, "lon": 0.0}
        self.zoom_level = 1.0
        self.meters_per_pixel = 1.0
        self.map_colors = MAP_CONFIG['colors']
        
        # Estado de visualización
        self.show_grid = True
        self.show_precision_circle = True
        self.show_background = True
        
    def draw_initial_map(self):
        """Dibuja el mapa inicial"""
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Texto de instrucciones
        self.canvas.create_text(
            canvas_width/2, canvas_height/2,
            text="🛰️ MAPA GPS DE PRECISIÓN\n\nConecte el GPS para comenzar el tracking\n\nClick derecho: Menú\nRueda: Zoom\nArrastrar: Mover mapa",
            fill=self.map_colors["text"],
            font=("Arial", 12),
            justify="center",
            tags="instructions"
        )
    
    def update_map(self, show_grid=True, show_precision_circle=True, show_background=True):
        """
        Actualiza el mapa con los datos actuales
        VERSIÓN CORREGIDA - Mejor manejo de imagen de fondo
        """
        self.show_grid = show_grid
        self.show_precision_circle = show_precision_circle
        self.show_background = show_background
        
        print(f"Actualizando mapa - Centro: {self.map_center}, Zoom: {self.meters_per_pixel:.3f} m/px")  # DEBUG
        
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        print(f"Canvas size: {canvas_width}x{canvas_height}")  # DEBUG
        
        # Dibujar imagen de fondo si está disponible y habilitada
        if self.show_background and self.image_handler.background_image:
            print("Intentando dibujar imagen de fondo...")  # DEBUG
            self.draw_background_image(canvas_width, canvas_height)
        else:
            print(f"No dibujando imagen: show_background={self.show_background}, imagen_disponible={self.image_handler.background_image is not None}")  # DEBUG
            
        # Dibujar grilla si está habilitada
        if self.show_grid:
            self.draw_grid(canvas_width, canvas_height)
            
        # Dibujar track si hay puntos
        if len(self.data_manager.track_points) > 1:
            self.draw_track()
            
        # Dibujar waypoints
        self.draw_waypoints()
        
        # Dibujar posición actual
        if self.data_manager.sensor_data['latitude'] != 0.0 and self.data_manager.sensor_data['longitude'] != 0.0:
            self.draw_current_position()
            
        # Dibujar círculo de precisión
        if self.show_precision_circle and self.data_manager.sensor_data['hdop'] > 0:
            self.draw_precision_circle()
    
    def draw_background_image(self, canvas_width, canvas_height):
        """
        Dibuja la imagen de fondo calibrada
        VERSIÓN CORREGIDA - Mejor manejo de errores y debug
        """
        try:
            print("Solicitando imagen al image_handler...")  # DEBUG
            
            image_info = self.image_handler.get_background_photo_for_canvas(
                canvas_width, canvas_height, self.map_center, self.meters_per_pixel
            )
            
            if image_info and image_info.get('photo'):
                print(f"Imagen recibida, dibujando en ({image_info['x']}, {image_info['y']})")  # DEBUG
                
                # Verificar que las coordenadas estén en rango razonable
                if (-5000 <= image_info['x'] <= canvas_width + 5000 and 
                    -5000 <= image_info['y'] <= canvas_height + 5000):
                    
                    # Dibujar la imagen en el canvas
                    image_id = self.canvas.create_image(
                        image_info['x'], image_info['y'],
                        anchor="nw",
                        image=image_info['photo'],
                        tags="background_image"
                    )
                    
                    print(f"Imagen dibujada con ID: {image_id}")  # DEBUG
                    
                    # Mover la imagen al fondo (debajo de otros elementos)
                    self.canvas.tag_lower("background_image")
                    
                else:
                    print(f"Imagen fuera de rango: ({image_info['x']}, {image_info['y']})")  # DEBUG
            else:
                print("No se recibió imagen válida del image_handler")  # DEBUG
                
        except Exception as e:
            print(f"Error dibujando imagen de fondo: {e}")
            import traceback
            traceback.print_exc()  # DEBUG completo
    
    def draw_grid(self, width, height):
        """Dibuja una grilla de referencia"""
        # Calcular espaciado de grilla basado en escala
        grid_spacing_meters = self._get_grid_spacing()
        grid_spacing_pixels = grid_spacing_meters / self.meters_per_pixel
        
        # Líneas verticales
        start_x = (width / 2) % grid_spacing_pixels
        x = start_x
        while x < width:
            self.canvas.create_line(x, 0, x, height, 
                                  fill=self.map_colors["grid"], width=1, tags="grid")
            x += grid_spacing_pixels
            
        # Líneas horizontales
        start_y = (height / 2) % grid_spacing_pixels
        y = start_y
        while y < height:
            self.canvas.create_line(0, y, width, y, 
                                  fill=self.map_colors["grid"], width=1, tags="grid")
            y += grid_spacing_pixels
            
        # Etiquetas de escala
        self.canvas.create_text(
            20, 20,
            text=f"Grilla: {grid_spacing_meters}m\nEscala: {self.meters_per_pixel:.3f} m/px",
            fill=self.map_colors["text"],
            font=("Arial", 9),
            anchor="nw",
            tags="grid_info"
        )
    
    def _get_grid_spacing(self):
        """Calcula el espaciado de grilla basado en escala"""
        for threshold, spacing in GRID_CONFIG['spacing_rules']:
            if self.meters_per_pixel < threshold:
                return spacing
        return 100.0  # Fallback
    
    def draw_track(self):
        """Dibuja el track GPS"""
        if len(self.data_manager.track_points) < 2:
            return
            
        # Convertir puntos del track a coordenadas de canvas
        canvas_points = []
        for point in self.data_manager.track_points:
            x, y = self.geo_to_canvas(point['lat'], point['lon'])
            canvas_points.extend([x, y])
            
        # Dibujar línea del track
        if len(canvas_points) >= 4:
            self.canvas.create_line(
                canvas_points,
                fill=self.map_colors["track"],
                width=2,
                tags="track",
                smooth=True
            )
            
        # Dibujar puntos individuales del track
        for i, point in enumerate(self.data_manager.track_points):
            x, y = self.geo_to_canvas(point['lat'], point['lon'])
            
            canvas_width = self.canvas.winfo_width() or 800
            canvas_height = self.canvas.winfo_height() or 600
            
            if 0 <= x <= canvas_width and 0 <= y <= canvas_height:
                size = max(2, int(3 / self.meters_per_pixel))
                size = min(size, 8)  # Límite máximo
                
                self.canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill=self.map_colors["track"],
                    outline=self.map_colors["track"],
                    tags="track_point"
                )
    
    def draw_waypoints(self):
        """Dibuja los waypoints"""
        for waypoint in self.data_manager.waypoints:
            x, y = self.geo_to_canvas(waypoint['lat'], waypoint['lon'])
            
            size = max(8, int(12 / self.meters_per_pixel))
            size = min(size, 20)
            
            # Círculo del waypoint
            self.canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill=self.map_colors["waypoint"],
                outline="white",
                width=2,
                tags="waypoint"
            )
            
            # Etiqueta del waypoint
            self.canvas.create_text(
                x, y - size - 15,
                text=waypoint['name'],
                fill=self.map_colors["waypoint"],
                font=("Arial", 8, "bold"),
                tags="waypoint_label"
            )
    
    def draw_current_position(self):
        """Dibuja la posición actual del GPS"""
        x, y = self.geo_to_canvas(
            self.data_manager.sensor_data['latitude'], 
            self.data_manager.sensor_data['longitude']
        )
        
        size = max(10, int(15 / self.meters_per_pixel))
        size = min(size, 25)
        
        # Círculo principal (posición actual)
        self.canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill=self.map_colors["current"],
            outline="white",
            width=3,
            tags="current_position"
        )
        
        # Punto central
        small_size = max(3, size // 3)
        self.canvas.create_oval(
            x - small_size, y - small_size, x + small_size, y + small_size,
            fill="white",
            outline="white",
            tags="current_center"
        )
        
        # Flecha de dirección basada en heading
        if self.data_manager.sensor_data['heading'] > 0:
            heading_rad = math.radians(self.data_manager.sensor_data['heading'] - 90)  # Ajustar para que 0° sea norte
            arrow_length = size * 2
            
            end_x = x + arrow_length * math.cos(heading_rad)
            end_y = y + arrow_length * math.sin(heading_rad)
            
            self.canvas.create_line(
                x, y, end_x, end_y,
                fill="yellow",
                width=3,
                arrow=tk.LAST,
                arrowshape=(10, 12, 4),
                tags="heading_arrow"
            )
    
    def draw_precision_circle(self):
        """Dibuja el círculo de precisión basado en HDOP"""
        if self.data_manager.sensor_data['hdop'] <= 0:
            return
            
        # Calcular radio de error en metros (HDOP * factor base)
        base_error = GPS_PRECISION['base_error_meters']  # Error base en metros para HDOP = 1
        error_radius_meters = self.data_manager.sensor_data['hdop'] * base_error
        
        # Convertir a píxeles
        error_radius_pixels = error_radius_meters / self.meters_per_pixel
        
        x, y = self.geo_to_canvas(
            self.data_manager.sensor_data['latitude'], 
            self.data_manager.sensor_data['longitude']
        )
        
        # Dibujar círculo de precisión
        self.canvas.create_oval(
            x - error_radius_pixels, y - error_radius_pixels,
            x + error_radius_pixels, y + error_radius_pixels,
            outline=self.map_colors["precision_circle"],
            width=2,
            tags="precision_circle"
        )
        
        # Etiqueta del radio
        self.canvas.create_text(
            x + error_radius_pixels + 10, y,
            text=f"±{error_radius_meters:.1f}m",
            fill=self.map_colors["precision_circle"],
            font=("Arial", 9),
            tags="precision_label"
        )
    
    def geo_to_canvas(self, lat, lon):
        """Convierte coordenadas geográficas a píxeles del canvas"""
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Calcular offset en metros desde el centro del mapa
        dx_meters, dy_meters = self.data_manager.lat_lon_to_meters(
            self.map_center["lat"], self.map_center["lon"], lat, lon
        )
        
        # Convertir a píxeles
        dx_pixels = dx_meters / self.meters_per_pixel
        dy_pixels = -dy_meters / self.meters_per_pixel  # Y negativo porque canvas Y crece hacia abajo
        
        # Posición en canvas
        x = canvas_width / 2 + dx_pixels
        y = canvas_height / 2 + dy_pixels
        
        return x, y
    
    def canvas_to_geo(self, canvas_x, canvas_y):
        """Convierte píxeles del canvas a coordenadas geográficas"""
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Calcular offset en píxeles desde el centro
        dx_pixels = canvas_x - canvas_width / 2
        dy_pixels = canvas_y - canvas_height / 2
        
        # Convertir a metros
        dx_meters = dx_pixels * self.meters_per_pixel
        dy_meters = -dy_pixels * self.meters_per_pixel  # Y negativo
        
        # Convertir metros a lat/lon
        R = 6371000  # Radio de la Tierra
        dlat = dy_meters / R * 180 / math.pi
        dlon = dx_meters / (R * math.cos(math.radians(self.map_center["lat"]))) * 180 / math.pi
        
        lat = self.map_center["lat"] + dlat
        lon = self.map_center["lon"] + dlon
        
        return lat, lon
    
    def update_map_params(self, map_center, zoom_level, meters_per_pixel):
        """Actualiza parámetros del mapa"""
        self.map_center = map_center.copy()
        self.zoom_level = zoom_level
        self.meters_per_pixel = meters_per_pixel
        
        # Limpiar cache de imagen cuando cambian parámetros
        if hasattr(self.image_handler, '_cached_photo'):
            self.image_handler._cached_photo = None
    
    def get_visible_bounds(self):
        """Retorna los límites geográficos visibles en el canvas"""
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Esquinas del canvas
        top_left_lat, top_left_lon = self.canvas_to_geo(0, 0)
        bottom_right_lat, bottom_right_lon = self.canvas_to_geo(canvas_width, canvas_height)
        
        return {
            'north': max(top_left_lat, bottom_right_lat),
            'south': min(top_left_lat, bottom_right_lat),
            'east': max(top_left_lon, bottom_right_lon),
            'west': min(top_left_lon, bottom_right_lon)
        }
    
    def clear_map(self):
        """Limpia todos los elementos del mapa"""
        self.canvas.delete("all")
    
    def cleanup(self):
        """Limpieza al cerrar"""
        self.clear_map()