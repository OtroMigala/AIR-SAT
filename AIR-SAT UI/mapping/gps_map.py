# mapping/gps_map.py
"""
Sistema principal de mapas GPS para el sistema GPS + GY91
Coordina todos los módulos de mapeo y mantiene la funcionalidad exacta del original
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import MAP_CONFIG, FILE_FORMATS, EXPORT_CONFIG
from .image_handler import ImageHandler
from .map_renderer import MapRenderer

class GPSMapSystem:
    """
    Sistema completo de mapas GPS
    MANTIENE LA FUNCIONALIDAD EXACTA DEL CÓDIGO ORIGINAL
    """
    
    def __init__(self, parent_frame, data_manager):
        self.parent = parent_frame
        self.data_manager = data_manager
        
        # Inicializar módulos
        self.image_handler = ImageHandler(data_manager)
        self.map_renderer = None  # Se inicializa después del canvas
        
        # Variables de control del mapa - EXACTAMENTE IGUAL AL ORIGINAL
        self.zoom_level = 1.0
        self.meters_per_pixel = 1.0
        self.auto_center = True
        self.map_initialized = False
        
        # Variables para eventos de mouse - EXACTAMENTE IGUAL AL ORIGINAL
        self.map_last_x = 0
        self.map_last_y = 0
        
        # UI Elements (para acceso desde otros métodos)
        self.ui_elements = {}
        
        # Configurar la interfaz
        self.setup_map_interface()
        
    def setup_map_interface(self):
        """
        Configura la interfaz completa del mapa GPS
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        # Panel de control del mapa
        self.setup_map_controls()
        
        # Frame de información
        self.setup_info_frame()
        
        # Canvas del mapa
        self.setup_map_canvas()
        
        # Inicializar renderer después de crear canvas
        self.map_renderer = MapRenderer(self.map_canvas, self.data_manager, self.image_handler)
        
        # Configurar zoom inicial
        self.set_zoom_scale(MAP_CONFIG['default_zoom_scale'])
        self.map_renderer.draw_initial_map()
        
        self.map_initialized = True
    
    def setup_map_controls(self):
        """Configura controles del mapa - EXACTAMENTE IGUAL AL ORIGINAL"""
        map_control_frame = ctk.CTkFrame(self.parent)
        map_control_frame.pack(fill="x", padx=5, pady=5)
        
        # Título
        ctk.CTkLabel(map_control_frame, text="🎯 MAPA GPS DE PRECISIÓN - BÚSQUEDA DE SATÉLITE",
                   font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
        
        # Controles de zoom precisión
        zoom_frame = ctk.CTkFrame(map_control_frame)
        zoom_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(zoom_frame, text="Zoom:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkButton(zoom_frame, text="🔍+", width=40, command=self.zoom_in).pack(side="left", padx=2)
        ctk.CTkButton(zoom_frame, text="🔍-", width=40, command=self.zoom_out).pack(side="left", padx=2)
        
        # Zoom presets para búsqueda - EXACTAMENTE IGUAL AL ORIGINAL
        preset_frame = ctk.CTkFrame(map_control_frame)
        preset_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(preset_frame, text="Escala:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        for scale in MAP_CONFIG['zoom_presets']:
            ctk.CTkButton(preset_frame, text=f"{scale}m", width=50, 
                         command=lambda s=scale: self.set_zoom_scale(s)).pack(side="left", padx=1)
        
        # Controles de vista - EXACTAMENTE IGUAL AL ORIGINAL
        view_frame = ctk.CTkFrame(map_control_frame)
        view_frame.pack(side="left", padx=10)
        
        self.auto_center_var = ctk.BooleanVar(value=True)
        self.auto_center_check = ctk.CTkCheckBox(view_frame, text="Auto-centrar", 
                                               variable=self.auto_center_var,
                                               command=self.toggle_auto_center)
        self.auto_center_check.pack(side="left", padx=5)
        
        ctk.CTkButton(view_frame, text="📍 Centrar", width=80, command=self.center_map).pack(side="left", padx=2)
        ctk.CTkButton(view_frame, text="🗑️ Limpiar", width=80, command=self.clear_track).pack(side="left", padx=2)
        
        # Opciones de visualización - MEJORADO CON IMAGEN
        self.setup_display_options(map_control_frame)
    
    def setup_display_options(self, parent):
        """Configura opciones de visualización - MEJORADO CON IMAGEN"""
        display_frame = ctk.CTkFrame(parent)
        display_frame.pack(side="right", padx=10)
        
        # Imagen de fondo
        image_frame = ctk.CTkFrame(display_frame)
        image_frame.pack(side="left", padx=5)
        
        ctk.CTkButton(image_frame, text="📷 Cargar Mapa", width=100, 
                     command=self.load_background_image).pack(side="top", padx=2, pady=1)
        ctk.CTkButton(image_frame, text="🔧 Calibrar", width=100, 
                     command=self.calibrate_image).pack(side="top", padx=2, pady=1)
        
        opacity_frame = ctk.CTkFrame(image_frame)
        opacity_frame.pack(side="top", padx=2, pady=1)
        ctk.CTkLabel(opacity_frame, text="Opacidad:", font=ctk.CTkFont(size=9)).pack(side="left")
        self.opacity_slider = ctk.CTkSlider(opacity_frame, from_=0.1, to=1.0, number_of_steps=9, 
                                          command=self.update_opacity, width=80)
        self.opacity_slider.set(MAP_CONFIG['default_opacity'])
        self.opacity_slider.pack(side="left", padx=2)
        
        # Controles de capas
        layers_frame = ctk.CTkFrame(display_frame)
        layers_frame.pack(side="left", padx=5)
        
        self.background_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(layers_frame, text="Mapa fondo", 
                       variable=self.background_var).pack(side="top", padx=2, pady=1)
        
        self.precision_circle_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(layers_frame, text="Círculo precisión", 
                       variable=self.precision_circle_var).pack(side="top", padx=2, pady=1)
        
        self.grid_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(layers_frame, text="Grilla", 
                       variable=self.grid_var).pack(side="top", padx=2, pady=1)
        
        # Waypoints y exportación
        control_frame2 = ctk.CTkFrame(display_frame)
        control_frame2.pack(side="left", padx=5)
        
        ctk.CTkButton(control_frame2, text="📌 Waypoint", width=90, 
                     command=self.add_waypoint).pack(side="top", padx=2, pady=1)
        ctk.CTkButton(control_frame2, text="💾 Guardar Track", width=90, 
                     command=self.save_track).pack(side="top", padx=2, pady=1)
    
    def setup_info_frame(self):
        """Configura frame de información - EXACTAMENTE IGUAL AL ORIGINAL"""
        info_frame = ctk.CTkFrame(self.parent)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        # Información de precisión
        precision_info_frame = ctk.CTkFrame(info_frame)
        precision_info_frame.pack(side="left", fill="x", expand=True, padx=2)
        
        ctk.CTkLabel(precision_info_frame, text="📊 INFORMACIÓN DE PRECISIÓN",
                   font=ctk.CTkFont(size=12, weight="bold")).pack()
        
        precision_data_frame = ctk.CTkFrame(precision_info_frame)
        precision_data_frame.pack(fill="x", padx=5, pady=5)
        
        # Coordenadas actuales - EXACTAMENTE IGUAL AL ORIGINAL
        coords_frame = ctk.CTkFrame(precision_data_frame)
        coords_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(coords_frame, text="📍 Posición:", width=100).pack(side="left", padx=5)
        self.ui_elements['map_coords_label'] = ctk.CTkLabel(coords_frame, text="0.000000°, 0.000000°",
                                           font=ctk.CTkFont(size=11, weight="bold"))
        self.ui_elements['map_coords_label'].pack(side="left", padx=5)
        
        # Precisión HDOP - EXACTAMENTE IGUAL AL ORIGINAL
        hdop_frame = ctk.CTkFrame(precision_data_frame)
        hdop_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(hdop_frame, text="🎯 HDOP:", width=100).pack(side="left", padx=5)
        self.ui_elements['map_hdop_label'] = ctk.CTkLabel(hdop_frame, text="0.0 (Error: 0.0m)",
                                         font=ctk.CTkFont(size=11, weight="bold"))
        self.ui_elements['map_hdop_label'].pack(side="left", padx=5)
        
        # Escala actual - EXACTAMENTE IGUAL AL ORIGINAL
        scale_frame = ctk.CTkFrame(precision_data_frame)
        scale_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(scale_frame, text="📏 Escala:", width=100).pack(side="left", padx=5)
        self.ui_elements['map_scale_label'] = ctk.CTkLabel(scale_frame, text="1.0 m/píxel",
                                          font=ctk.CTkFont(size=11, weight="bold"))
        self.ui_elements['map_scale_label'].pack(side="left", padx=5)
        
        # Estadísticas del track - EXACTAMENTE IGUAL AL ORIGINAL
        self.setup_track_stats(info_frame)
    
    def setup_track_stats(self, parent):
        """Configura estadísticas del track - EXACTAMENTE IGUAL AL ORIGINAL"""
        track_info_frame = ctk.CTkFrame(parent)
        track_info_frame.pack(side="right", fill="y", padx=2)
        
        ctk.CTkLabel(track_info_frame, text="📈 ESTADÍSTICAS TRACK",
                   font=ctk.CTkFont(size=12, weight="bold")).pack()
        
        track_data_frame = ctk.CTkFrame(track_info_frame)
        track_data_frame.pack(fill="x", padx=5, pady=5)
        
        # Puntos en track
        points_frame = ctk.CTkFrame(track_data_frame)
        points_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(points_frame, text="Puntos:", width=80).pack(side="left", padx=5)
        self.ui_elements['track_points_label'] = ctk.CTkLabel(points_frame, text="0")
        self.ui_elements['track_points_label'].pack(side="left", padx=5)
        
        # Distancia total
        distance_frame = ctk.CTkFrame(track_data_frame)
        distance_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(distance_frame, text="Distancia:", width=80).pack(side="left", padx=5)
        self.ui_elements['track_distance_label'] = ctk.CTkLabel(distance_frame, text="0.0 m")
        self.ui_elements['track_distance_label'].pack(side="left", padx=5)
        
        # Área de dispersión
        area_frame = ctk.CTkFrame(track_data_frame)
        area_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(area_frame, text="Dispersión:", width=80).pack(side="left", padx=5)
        self.ui_elements['dispersion_label'] = ctk.CTkLabel(area_frame, text="0.0 m")
        self.ui_elements['dispersion_label'].pack(side="left", padx=5)
    
    def setup_map_canvas(self):
        """Configura canvas del mapa - MEJORADO PARA LLENAR ESPACIO"""
        canvas_frame = ctk.CTkFrame(self.parent)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas con scrollbars - Asegurar tamaño mínimo
        self.map_canvas = tk.Canvas(canvas_frame, bg=MAP_CONFIG['colors']["background"], 
                                   highlightthickness=0, width=800, height=600)
        
        # Scrollbars
        v_scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=self.map_canvas.yview)
        h_scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="horizontal", command=self.map_canvas.xview)
        
        self.map_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.map_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind para actualizar tamaño cuando cambia el frame
        canvas_frame.bind("<Configure>", self._on_canvas_frame_resize)
        
        # Eventos del mouse para el mapa - EXACTAMENTE IGUAL AL ORIGINAL
        self.map_canvas.bind("<Button-1>", self.on_map_click)
        self.map_canvas.bind("<B1-Motion>", self.on_map_drag)
        self.map_canvas.bind("<MouseWheel>", self.on_map_wheel)
        self.map_canvas.bind("<Button-3>", self.on_map_right_click)
    
    def _on_canvas_frame_resize(self, event):
        """Maneja el redimensionamiento del frame del canvas"""
        if event.widget == self.map_canvas.master:
            # Actualizar scroll region para permitir scrolling
            self.map_canvas.configure(scrollregion=self.map_canvas.bbox("all"))
            
            # Opcional: Actualizar el mapa cuando cambia el tamaño
            if self.map_initialized:
                self.parent.after_idle(self.update_map)
    
    # === MÉTODOS DE CONTROL DEL MAPA ===
    
    def set_zoom_scale(self, meters_scale):
        """
        Establece el zoom basado en metros por ventana
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        canvas_width = self.map_canvas.winfo_width() or 800
        canvas_height = self.map_canvas.winfo_height() or 600
        min_dimension = min(canvas_width, canvas_height)
        
        # Calcular metros por píxel para que la escala total sea meters_scale
        self.meters_per_pixel = meters_scale / min_dimension * 2
        self.zoom_level = 1.0 / self.meters_per_pixel
        
        if self.map_initialized:
            self.update_map()
    
    def zoom_in(self):
        """Acerca el zoom del mapa - EXACTAMENTE IGUAL AL ORIGINAL"""
        self.zoom_level *= 1.5
        self.meters_per_pixel /= 1.5
        self.update_map()
    
    def zoom_out(self):
        """Aleja el zoom del mapa - EXACTAMENTE IGUAL AL ORIGINAL"""
        self.zoom_level /= 1.5
        self.meters_per_pixel *= 1.5
        self.update_map()
    
    def toggle_auto_center(self):
        """Toggle auto-centrar mapa - EXACTAMENTE IGUAL AL ORIGINAL"""
        self.auto_center = self.auto_center_var.get()
    
    def center_map(self):
        """Centra el mapa en la posición actual - EXACTAMENTE IGUAL AL ORIGINAL"""
        position = self.data_manager.get_current_position()
        if position['valid']:
            self.data_manager.map_center["lat"] = position['lat']
            self.data_manager.map_center["lon"] = position['lon']
            self.update_map()
    
    def clear_track(self):
        """Limpia el track del mapa - EXACTAMENTE IGUAL AL ORIGINAL"""
        self.data_manager.clear_track()
        self.update_map()
    
    def add_waypoint(self):
        """Añade un waypoint en la posición actual - MEJORADO"""
        position = self.data_manager.get_current_position()
        if position['valid']:
            waypoint_name = simpledialog.askstring(
                "Nuevo Waypoint",
                f"Nombre para el waypoint en:\n"
                f"Lat: {position['lat']:.6f}°\n"
                f"Lon: {position['lon']:.6f}°",
                initialvalue=f"WP{len(self.data_manager.waypoints)+1}"
            )
            
            if waypoint_name:
                waypoint = self.data_manager.add_waypoint(waypoint_name)
                if waypoint:
                    self.update_map()
                    messagebox.showinfo(
                        "Waypoint Añadido",
                        f"Waypoint '{waypoint_name}' añadido exitosamente\n"
                        f"Posición: {waypoint['lat']:.6f}°, {waypoint['lon']:.6f}°\n"
                        f"Precisión: ±{self.data_manager.sensor_data['hdop'] * 3:.1f}m"
                    )
        else:
            messagebox.showwarning("Sin GPS", "No hay datos GPS válidos para crear waypoint")
    
    # === MÉTODOS DE IMAGEN ===
    
    def load_background_image(self):
        """Carga imagen de fondo"""
        if self.image_handler.load_background_image(self.parent):
            self.update_map()
    
    def calibrate_image(self):
        """Calibra imagen de fondo"""
        if self.image_handler.calibrate_image(self.parent):
            self.update_map()
    
    def update_opacity(self, value):
        """Actualiza opacidad de imagen"""
        self.image_handler.update_opacity(value)
        if self.map_initialized:
            self.update_map()
    
    # === MÉTODOS DE EXPORTACIÓN ===
    
    def save_track(self):
        """Guarda el track GPS en archivo - MANTIENE FUNCIONALIDAD ORIGINAL"""
        if not self.data_manager.track_points:
            messagebox.showwarning("Sin Datos", "No hay puntos de track para guardar")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Guardar track GPS",
            defaultextension=".gpx",
            filetypes=FILE_FORMATS['export_types']
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self._save_track_csv(file_path)
                elif file_path.endswith('.gpx'):
                    self._save_track_gpx(file_path)
                elif file_path.endswith('.kml'):
                    self._save_track_kml(file_path)
                else:
                    self._save_track_txt(file_path)
                    
                messagebox.showinfo("Guardado", f"Track guardado en:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
    
    def _save_track_csv(self, file_path):
        """Guarda track en formato CSV - EXACTAMENTE IGUAL AL ORIGINAL"""
        with open(file_path, 'w') as f:
            f.write("Timestamp,Latitude,Longitude,HDOP,Time\n")
            for point in self.data_manager.track_points:
                timestamp = point['time'].strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp},{point['lat']:.8f},{point['lon']:.8f},{point['hdop']:.2f},{point['time'].strftime('%H:%M:%S')}\n")
    
    def _save_track_gpx(self, file_path):
        """Guarda track en formato GPX - EXACTAMENTE IGUAL AL ORIGINAL"""
        with open(file_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(f'<gpx version="1.1" creator="{EXPORT_CONFIG["gpx_creator"]}">\n')
            f.write('  <trk>\n')
            f.write(f'    <name>{EXPORT_CONFIG["track_name"]}</name>\n')
            f.write('    <trkseg>\n')
            
            for point in self.data_manager.track_points:
                timestamp = point['time'].strftime(EXPORT_CONFIG['time_format'])
                f.write(f'      <trkpt lat="{point["lat"]:.{EXPORT_CONFIG["coordinate_precision"]}f}" lon="{point["lon"]:.{EXPORT_CONFIG["coordinate_precision"]}f}">\n')
                f.write(f'        <time>{timestamp}</time>\n')
                f.write(f'        <hdop>{point["hdop"]:.2f}</hdop>\n')
                f.write('      </trkpt>\n')
                
            f.write('    </trkseg>\n')
            f.write('  </trk>\n')
            f.write('</gpx>\n')
    
    def _save_track_kml(self, file_path):
        """Guarda track en formato KML - EXACTAMENTE IGUAL AL ORIGINAL"""
        with open(file_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
            f.write('  <Document>\n')
            f.write(f'    <name>{EXPORT_CONFIG["track_name"]}</name>\n')
            f.write('    <Placemark>\n')
            f.write('      <name>Track GPS</name>\n')
            f.write('      <LineString>\n')
            f.write('        <coordinates>\n')
            
            for point in self.data_manager.track_points:
                f.write(f'          {point["lon"]:.{EXPORT_CONFIG["coordinate_precision"]}f},{point["lat"]:.{EXPORT_CONFIG["coordinate_precision"]}f},0\n')
                
            f.write('        </coordinates>\n')
            f.write('      </LineString>\n')
            f.write('    </Placemark>\n')
            f.write('  </Document>\n')
            f.write('</kml>\n')
    
    def _save_track_txt(self, file_path):
        """Guarda track en formato texto simple - EXACTAMENTE IGUAL AL ORIGINAL"""
        from datetime import datetime
        with open(file_path, 'w') as f:
            f.write("TRACK GPS - Sistema de Navegación Satélite\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de puntos: {len(self.data_manager.track_points)}\n\n")
            
            for i, point in enumerate(self.data_manager.track_points, 1):
                f.write(f"Punto {i:3d}: {point['lat']:.{EXPORT_CONFIG['coordinate_precision']}f}°, {point['lon']:.{EXPORT_CONFIG['coordinate_precision']}f}° ")
                f.write(f"(HDOP: {point['hdop']:.2f}) - {point['time'].strftime('%H:%M:%S')}\n")
    
    # === EVENTOS DE MOUSE ===
    
    def on_map_click(self, event):
        """Maneja el click en el mapa - EXACTAMENTE IGUAL AL ORIGINAL"""
        self.map_last_x = event.x
        self.map_last_y = event.y
    
    def on_map_drag(self, event):
        """Maneja el arrastre del mapa - EXACTAMENTE IGUAL AL ORIGINAL"""
        dx = event.x - self.map_last_x
        dy = event.y - self.map_last_y
        
        # Convertir píxeles a metros
        dx_meters = dx * self.meters_per_pixel
        dy_meters = -dy * self.meters_per_pixel  # Y negativo
        
        # Convertir metros a cambio en lat/lon
        R = 6371000  # Radio de la Tierra
        dlat = dy_meters / R * 180 / math.pi
        dlon = dx_meters / (R * math.cos(math.radians(self.data_manager.map_center["lat"]))) * 180 / math.pi
        
        self.data_manager.map_center["lat"] -= dlat
        self.data_manager.map_center["lon"] -= dlon
        
        self.map_last_x = event.x
        self.map_last_y = event.y
        
        # Desactivar auto-centrar temporalmente
        self.auto_center = False
        self.auto_center_var.set(False)
        
        self.update_map()
    
    def on_map_wheel(self, event):
        """Maneja el zoom con la rueda del mouse - EXACTAMENTE IGUAL AL ORIGINAL"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_map_right_click(self, event):
        """Maneja el click derecho en el mapa - EXACTAMENTE IGUAL AL ORIGINAL"""
        # Crear menú contextual
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="📍 Centrar aquí", command=self.center_map)
        context_menu.add_command(label="📌 Añadir waypoint", command=self.add_waypoint)
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Limpiar track", command=self.clear_track)
        context_menu.add_command(label="🔄 Reset zoom", command=lambda: self.set_zoom_scale(20))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    # === ACTUALIZACIÓN Y LIMPIEZA ===
    
    def update_map(self):
        """
        Actualiza el mapa completo
        COORDINADOR PRINCIPAL - MANTIENE AUTO-CENTRADO
        """
        if not self.map_initialized:
            return
            
        # Auto-centrar si está habilitado
        position = self.data_manager.get_current_position()
        if self.auto_center and position['valid']:
            self.data_manager.map_center["lat"] = position['lat']
            self.data_manager.map_center["lon"] = position['lon']
        
        # Actualizar parámetros del renderer
        self.map_renderer.update_map_params(
            self.data_manager.map_center, 
            self.zoom_level, 
            self.meters_per_pixel
        )
        
        # Renderizar mapa
        self.map_renderer.update_map(
            show_grid=self.grid_var.get(),
            show_precision_circle=self.precision_circle_var.get(),
            show_background=self.background_var.get()
        )
        
        # Actualizar información
        self.update_map_info()
    
    def update_map_info(self):
        """
        Actualiza la información del mapa
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        # Coordenadas
        self.ui_elements['map_coords_label'].configure(
            text=f"{self.data_manager.sensor_data['latitude']:.6f}°, {self.data_manager.sensor_data['longitude']:.6f}°"
        )
        
        # HDOP y error estimado
        if self.data_manager.sensor_data['hdop'] > 0:
            error_estimate = self.data_manager.sensor_data['hdop'] * 3.0
            hdop_color = "#00aa00" if self.data_manager.sensor_data['hdop'] < 2.0 else "#ffaa00" if self.data_manager.sensor_data['hdop'] < 5.0 else "#ff4444"
            self.ui_elements['map_hdop_label'].configure(
                text=f"{self.data_manager.sensor_data['hdop']:.1f} (Error: ±{error_estimate:.1f}m)",
                text_color=hdop_color
            )
        else:
            self.ui_elements['map_hdop_label'].configure(text="Sin datos HDOP")
            
        # Escala actual
        self.ui_elements['map_scale_label'].configure(text=f"{self.meters_per_pixel:.3f} m/píxel")
        
        # Estadísticas del track
        stats = self.data_manager.calculate_track_statistics()
        self.ui_elements['track_points_label'].configure(text=str(stats['points']))
        self.ui_elements['track_distance_label'].configure(text=f"{stats['distance']:.1f} m")
        self.ui_elements['dispersion_label'].configure(text=f"{stats['dispersion']:.1f} m")
    
    def cleanup(self):
        """Limpieza al cerrar la aplicación"""
        if self.map_renderer:
            self.map_renderer.cleanup()
        
        # Limpiar referencias
        self.image_handler = None
        self.map_renderer = None