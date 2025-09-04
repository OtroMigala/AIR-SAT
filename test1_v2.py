import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
from datetime import datetime, timedelta
import time
import math
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk

class GPSGy91Monitor:
    def __init__(self):
        # Configuración de la ventana principal
        self.root = ctk.CTk()
        self.root.title("Sistema GPS + GY91 - Monitor de Navegación | GPS + BMP280 + MPU9250")
        self.root.geometry("1600x1000")
        
        # Variables de control
        self.is_running = False
        self.serial_port = None
        self.data_count = 0
        self.plotting_enabled = True
        
        # Buffer de datos para rendimiento óptimo
        self.max_data_points = 500
        self.time_buffer = deque(maxlen=self.max_data_points)
        
        # Variables para control de actualización de UI
        self.update_counter = 0
        self.last_ui_update = time.time()
        self.ui_update_interval = 0.1  # Actualizar UI cada 100ms máximo
        
        # Buffers para GPS
        self.gps_data = {
            'latitude': deque(maxlen=self.max_data_points),
            'longitude': deque(maxlen=self.max_data_points),
            'altitude': deque(maxlen=self.max_data_points),
            'speed': deque(maxlen=self.max_data_points),
            'satellites': deque(maxlen=self.max_data_points),
            'hdop': deque(maxlen=self.max_data_points),
            'vdop': deque(maxlen=self.max_data_points)
        }
        
        # Buffers para BMP280
        self.bmp280_data = {
            'temp': deque(maxlen=self.max_data_points),
            'pressure': deque(maxlen=self.max_data_points),
            'altitude': deque(maxlen=self.max_data_points)
        }
        
        # Buffers para MPU9250
        self.mpu9250_data = {
            'temp': deque(maxlen=self.max_data_points),
            'accel_x': deque(maxlen=self.max_data_points),
            'accel_y': deque(maxlen=self.max_data_points),
            'accel_z': deque(maxlen=self.max_data_points),
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
        
        # Variables para datos en tiempo real
        self.sensor_data = {
            # GPS
            'latitude': 0.0, 'longitude': 0.0, 'gps_altitude': 0.0, 'speed': 0.0,
            'satellites': 0, 'fix_quality': 0, 'lat_dir': '', 'lon_dir': '',
            'hdop': 0.0, 'vdop': 0.0, 'utc_time': '',
            # BMP280
            'bmp_temp': 0.0, 'pressure': 0.0, 'bmp_altitude': 0.0,
            # MPU9250
            'mpu_temp': 0.0,
            'accel_x': 0.0, 'accel_y': 0.0, 'accel_z': 0.0,
            'gyro_x': 0.0, 'gyro_y': 0.0, 'gyro_z': 0.0,
            'mag_x': 0.0, 'mag_y': 0.0, 'mag_z': 0.0,
            'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0, 'heading': 0.0,
            # Calculados
            'total_accel': 0.0, 'total_gyro': 0.0, 'total_mag': 0.0,
            'altitude_diff': 0.0,  # Diferencia GPS vs BMP280
            'last_update': 'No hay datos', 'system_status': 'Desconectado', 'data_quality': 'N/A'
        }
        
        # Variables del mapa GPS
        self.map_center = {"lat": 0.0, "lon": 0.0}
        self.zoom_level = 1.0
        self.meters_per_pixel = 1.0  # Metros por píxel en el zoom actual
        self.track_points = deque(maxlen=1000)
        self.map_colors = {
            "background": "#1a1a1a",
            "grid": "#333333",
            "track": "#00ff00",
            "current": "#ff4444",
            "precision_circle": "#ffaa00",
            "waypoint": "#00aaff",
            "text": "#ffffff"
        }
        self.show_precision_circle = True
        self.show_grid = True
        self.auto_center = True
        self.waypoints = []
        self.map_initialized = False
        
        # Variables para imagen de fondo
        self.background_image = None
        self.background_photo = None
        self.image_calibrated = False
        self.image_bounds = {  # Coordenadas GPS de las esquinas de la imagen
            "top_left": {"lat": 0.0, "lon": 0.0},
            "bottom_right": {"lat": 0.0, "lon": 0.0}
        }
        self.image_opacity = 0.8
        self.show_background = True
        
        # Configurar matplotlib
        plt.style.use('fast')
        plt.rcParams.update({
            'font.size': 8,
            'figure.facecolor': '#212121',
            'axes.facecolor': '#2b2b2b',
            'text.color': 'white',
            'axes.labelcolor': 'white',
            'xtick.color': 'white',
            'ytick.color': 'white'
        })
        
        # Variables para optimización de gráficas
        self.plot_update_counter = 0
        self.plot_update_interval = 10
        self.current_tab = "📊 Monitor Tiempo Real"
        
        # Crear la interfaz
        self.setup_gui()
        
    def setup_gui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header con información del sistema
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        title_label = ctk.CTkLabel(header_frame, 
                                 text="🛰️ SISTEMA GPS + GY91 - NAVEGACIÓN AVANZADA",
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=5)
        
        subtitle_label = ctk.CTkLabel(header_frame,
                                    text="GPS (Posicionamiento Global) + BMP280 (Barómetro) + MPU9250 (IMU 9-DOF)",
                                    font=ctk.CTkFont(size=12))
        subtitle_label.pack(pady=2)
        
        # Frame de conexión
        conn_frame = ctk.CTkFrame(main_frame)
        conn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(conn_frame, text="↻", width=30,
                    command=self.update_ports).pack(side="left", padx=5)
        
        self.port_var = ctk.StringVar()
        self.port_select = ctk.CTkOptionMenu(conn_frame, 
                                        variable=self.port_var,
                                        values=self.get_ports())
        self.port_select.pack(side="left", padx=5)
        
        self.baud_var = ctk.StringVar(value="115200")
        baud_select = ctk.CTkOptionMenu(conn_frame,
                                    variable=self.baud_var,
                                    values=["9600", "115200"])
        baud_select.pack(side="left", padx=5)
        
        self.connect_btn = ctk.CTkButton(conn_frame, text="Conectar",
                                    command=self.toggle_connection)
        self.connect_btn.pack(side="left", padx=5)
        
        # Status y contadores
        self.status_label = ctk.CTkLabel(conn_frame, text="🔴 Desconectado", 
                                       font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.pack(side="left", padx=20)
        
        self.data_count_label = ctk.CTkLabel(conn_frame, text="Muestras: 0", 
                                           font=ctk.CTkFont(size=12))
        self.data_count_label.pack(side="left", padx=10)
        
        # Control de gráficas
        self.plot_toggle = ctk.CTkButton(conn_frame, text="⏸️ Pausar Gráficas",
                                       command=self.toggle_plotting)
        self.plot_toggle.pack(side="left", padx=10)
        
        # Sistema de pestañas
        self.tabview = ctk.CTkTabview(main_frame, command=self.tab_changed)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Pestaña 1: Monitor en tiempo real
        self.tabview.add("📊 Monitor Tiempo Real")
        self.setup_realtime_tab()
        
        # Pestaña 2: Gráficas
        self.tabview.add("📈 Gráficas Tiempo Real")
        self.plots_initialized = False
        
        # Pestaña 3: Mapa GPS de Precisión
        self.tabview.add("🗺️ Mapa GPS")
        self.setup_map_tab()
    def get_ports(self):
        """Obtiene lista de puertos seriales (método temprano para inicialización segura)."""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            return ports if ports else ["No hay puertos"]
        except Exception:
            return ["No hay puertos"]
        
    def update_ports(self):
        """Actualiza la lista de puertos disponibles (seguro si port_select aún no existe)."""
        try:
            ports = self.get_ports()
            # If port_select widget exists, update its values; otherwise do nothing now.
            if hasattr(self, 'port_select') and getattr(self, 'port_select') is not None:
                self.port_select.configure(values=ports)
        except Exception:
            # Silenciar cualquier error para no romper la inicialización de la GUI
            pass
    def setup_map_tab(self):
        """Configura la pestaña del mapa GPS de precisión"""
        map_frame = self.tabview.tab("🗺️ Mapa GPS")
        
        # Panel de control del mapa
        map_control_frame = ctk.CTkFrame(map_frame)
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
        
        # Zoom presets para búsqueda
        preset_frame = ctk.CTkFrame(map_control_frame)
        preset_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(preset_frame, text="Escala:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkButton(preset_frame, text="100m", width=50, command=lambda: self.set_zoom_scale(100)).pack(side="left", padx=1)
        ctk.CTkButton(preset_frame, text="50m", width=50, command=lambda: self.set_zoom_scale(50)).pack(side="left", padx=1)
        ctk.CTkButton(preset_frame, text="20m", width=50, command=lambda: self.set_zoom_scale(20)).pack(side="left", padx=1)
        ctk.CTkButton(preset_frame, text="10m", width=50, command=lambda: self.set_zoom_scale(10)).pack(side="left", padx=1)
        ctk.CTkButton(preset_frame, text="5m", width=50, command=lambda: self.set_zoom_scale(5)).pack(side="left", padx=1)
        ctk.CTkButton(preset_frame, text="2m", width=50, command=lambda: self.set_zoom_scale(2)).pack(side="left", padx=1)
        
        # Controles de vista
        view_frame = ctk.CTkFrame(map_control_frame)
        view_frame.pack(side="left", padx=10)
        
        self.auto_center_var = ctk.BooleanVar(value=True)
        self.auto_center_check = ctk.CTkCheckBox(view_frame, text="Auto-centrar", 
                                               variable=self.auto_center_var,
                                               command=self.toggle_auto_center)
        self.auto_center_check.pack(side="left", padx=5)
        
        ctk.CTkButton(view_frame, text="📍 Centrar", width=80, command=self.center_map).pack(side="left", padx=2)
        ctk.CTkButton(view_frame, text="🗑️ Limpiar", width=80, command=self.clear_track).pack(side="left", padx=2)
        
        # Opciones de visualización
        display_frame = ctk.CTkFrame(map_control_frame)
        display_frame.pack(side="right", padx=10)
        
        # Imagen de fondo
        image_frame = ctk.CTkFrame(display_frame)
        image_frame.pack(side="left", padx=5)
        
        ctk.CTkButton(image_frame, text="📷 Cargar Mapa", width=100, command=self.load_background_image).pack(side="top", padx=2, pady=1)
        ctk.CTkButton(image_frame, text="🔧 Calibrar", width=100, command=self.calibrate_image).pack(side="top", padx=2, pady=1)
        
        opacity_frame = ctk.CTkFrame(image_frame)
        opacity_frame.pack(side="top", padx=2, pady=1)
        ctk.CTkLabel(opacity_frame, text="Opacidad:", font=ctk.CTkFont(size=9)).pack(side="left")
        self.opacity_slider = ctk.CTkSlider(opacity_frame, from_=0.1, to=1.0, number_of_steps=9, 
                                          command=self.update_opacity, width=80)
        self.opacity_slider.set(0.8)
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
        
        # Waypoints y limpieza
        control_frame2 = ctk.CTkFrame(display_frame)
        control_frame2.pack(side="left", padx=5)
        
        ctk.CTkButton(control_frame2, text="📌 Waypoint", width=90, command=self.add_waypoint).pack(side="top", padx=2, pady=1)
        ctk.CTkButton(control_frame2, text="💾 Guardar Track", width=90, command=self.save_track).pack(side="top", padx=2, pady=1)
        
        # Info frame
        info_frame = ctk.CTkFrame(map_frame)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        # Información de precisión
        precision_info_frame = ctk.CTkFrame(info_frame)
        precision_info_frame.pack(side="left", fill="x", expand=True, padx=2)
        
        ctk.CTkLabel(precision_info_frame, text="📊 INFORMACIÓN DE PRECISIÓN",
                   font=ctk.CTkFont(size=12, weight="bold")).pack()
        
        precision_data_frame = ctk.CTkFrame(precision_info_frame)
        precision_data_frame.pack(fill="x", padx=5, pady=5)
        
        # Coordenadas actuales
        coords_frame = ctk.CTkFrame(precision_data_frame)
        coords_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(coords_frame, text="📍 Posición:", width=100).pack(side="left", padx=5)
        self.map_coords_label = ctk.CTkLabel(coords_frame, text="0.000000°, 0.000000°",
                                           font=ctk.CTkFont(size=11, weight="bold"))
        self.map_coords_label.pack(side="left", padx=5)
        
        # Precisión HDOP
        hdop_frame = ctk.CTkFrame(precision_data_frame)
        hdop_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(hdop_frame, text="🎯 HDOP:", width=100).pack(side="left", padx=5)
        self.map_hdop_label = ctk.CTkLabel(hdop_frame, text="0.0 (Error: 0.0m)",
                                         font=ctk.CTkFont(size=11, weight="bold"))
        self.map_hdop_label.pack(side="left", padx=5)
        
        # Escala actual
        scale_frame = ctk.CTkFrame(precision_data_frame)
        scale_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(scale_frame, text="📏 Escala:", width=100).pack(side="left", padx=5)
        self.map_scale_label = ctk.CTkLabel(scale_frame, text="1.0 m/píxel",
                                          font=ctk.CTkFont(size=11, weight="bold"))
        self.map_scale_label.pack(side="left", padx=5)
        
        # Estadísticas del track
        track_info_frame = ctk.CTkFrame(info_frame)
        track_info_frame.pack(side="right", fill="y", padx=2)
        
        ctk.CTkLabel(track_info_frame, text="📈 ESTADÍSTICAS TRACK",
                   font=ctk.CTkFont(size=12, weight="bold")).pack()
        
        track_data_frame = ctk.CTkFrame(track_info_frame)
        track_data_frame.pack(fill="x", padx=5, pady=5)
        
        # Puntos en track
        points_frame = ctk.CTkFrame(track_data_frame)
        points_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(points_frame, text="Puntos:", width=80).pack(side="left", padx=5)
        self.track_points_label = ctk.CTkLabel(points_frame, text="0")
        self.track_points_label.pack(side="left", padx=5)
        
        # Distancia total
        distance_frame = ctk.CTkFrame(track_data_frame)
        distance_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(distance_frame, text="Distancia:", width=80).pack(side="left", padx=5)
        self.track_distance_label = ctk.CTkLabel(distance_frame, text="0.0 m")
        self.track_distance_label.pack(side="left", padx=5)
        
        # Área de dispersión
        area_frame = ctk.CTkFrame(track_data_frame)
        area_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(area_frame, text="Dispersión:", width=80).pack(side="left", padx=5)
        self.dispersion_label = ctk.CTkLabel(area_frame, text="0.0 m")
        self.dispersion_label.pack(side="left", padx=5)
        
        # Canvas del mapa
        canvas_frame = ctk.CTkFrame(map_frame)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas con scrollbars
        self.map_canvas = tk.Canvas(canvas_frame, bg=self.map_colors["background"], highlightthickness=0)
        
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
        
        # Eventos del mouse para el mapa
        self.map_canvas.bind("<Button-1>", self.on_map_click)
        self.map_canvas.bind("<B1-Motion>", self.on_map_drag)
        self.map_canvas.bind("<MouseWheel>", self.on_map_wheel)
        self.map_canvas.bind("<Button-3>", self.on_map_right_click)
        
        # Variables para el drag
        self.map_last_x = 0
        self.map_last_y = 0
        
        # Configurar zoom inicial
        self.set_zoom_scale(20)  # Zoom inicial de 20 metros por defecto
        self.draw_initial_map()
        
        self.map_initialized = True
        
    def set_zoom_scale(self, meters_scale):
        """Establece el zoom basado en metros por ventana"""
        canvas_width = self.map_canvas.winfo_width() or 800
        canvas_height = self.map_canvas.winfo_height() or 600
        min_dimension = min(canvas_width, canvas_height)
        
        # Calcular metros por píxel para que la escala total sea meters_scale
        self.meters_per_pixel = meters_scale / min_dimension * 2
        self.zoom_level = 1.0 / self.meters_per_pixel
        
        if self.map_initialized:
            self.update_map()
            
    def zoom_in(self):
        """Acerca el zoom del mapa"""
        self.zoom_level *= 1.5
        self.meters_per_pixel /= 1.5
        self.update_map()
        
    def zoom_out(self):
        """Aleja el zoom del mapa"""
        self.zoom_level /= 1.5
        self.meters_per_pixel *= 1.5
        self.update_map()
        
    def toggle_auto_center(self):
        """Toggle auto-centrar mapa"""
        self.auto_center = self.auto_center_var.get()
        
    def center_map(self):
        """Centra el mapa en la posición actual"""
        if self.sensor_data['latitude'] != 0.0 and self.sensor_data['longitude'] != 0.0:
            self.map_center["lat"] = self.sensor_data['latitude']
            self.map_center["lon"] = self.sensor_data['longitude']
            self.update_map()
            
    def clear_track(self):
        """Limpia el track del mapa"""
        self.track_points.clear()
        self.waypoints.clear()
        self.update_map()
        
    def load_background_image(self):
        """Carga una imagen de fondo para el mapa"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen de mapa",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Todos", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.background_image = Image.open(file_path)
                self.image_calibrated = False
                
                # Mostrar información de la imagen
                width, height = self.background_image.size
                messagebox.showinfo(
                    "Imagen Cargada",
                    f"Imagen cargada exitosamente:\n"
                    f"Archivo: {file_path.split('/')[-1]}\n"
                    f"Dimensiones: {width} x {height} píxeles\n\n"
                    f"Ahora debe CALIBRAR la imagen con coordenadas GPS\n"
                    f"usando el botón 'Calibrar'"
                )
                
                # Auto-calibrar si hay posición GPS actual válida
                if self.sensor_data['latitude'] != 0.0 and self.sensor_data['longitude'] != 0.0:
                    self.auto_calibrate_image()
                else:
                    self.calibrate_image()
                    
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{str(e)}")
                
    def auto_calibrate_image(self):
        """Auto-calibra la imagen centrada en la posición GPS actual"""
        if not self.background_image:
            return
            
        # Usar la posición actual como centro de la imagen
        current_lat = self.sensor_data['latitude']
        current_lon = self.sensor_data['longitude']
        
        # Estimar el área que cubre la imagen (asumir ~500m de radio por defecto)
        estimated_radius_meters = 500.0
        
        # Convertir a grados aproximadamente
        lat_degree_meters = 111000  # Metros por grado de latitud
        lon_degree_meters = 111000 * math.cos(math.radians(current_lat))  # Ajustado por latitud
        
        lat_offset = estimated_radius_meters / lat_degree_meters
        lon_offset = estimated_radius_meters / lon_degree_meters
        
        # Establecer bounds de la imagen
        self.image_bounds = {
            "top_left": {
                "lat": current_lat + lat_offset,
                "lon": current_lon - lon_offset
            },
            "bottom_right": {
                "lat": current_lat - lat_offset,
                "lon": current_lon + lon_offset
            }
        }
        
        self.image_calibrated = True
        self.map_center["lat"] = current_lat
        self.map_center["lon"] = current_lon
        
        messagebox.showinfo(
            "Auto-Calibración",
            f"Imagen auto-calibrada centrada en:\n"
            f"Lat: {current_lat:.6f}°\n"
            f"Lon: {current_lon:.6f}°\n"
            f"Área estimada: ±{estimated_radius_meters}m\n\n"
            f"Use 'Calibrar' para ajustar manualmente si es necesario."
        )
        
        self.update_map()
        
    def calibrate_image(self):
        """Calibra la imagen con coordenadas GPS específicas"""
        if not self.background_image:
            messagebox.showwarning("Sin Imagen", "Primero debe cargar una imagen de fondo")
            return
            
        dialog = ImageCalibrationDialog(self.root, self.sensor_data)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.image_bounds = dialog.result
            self.image_calibrated = True
            
            # Centrar mapa en el centro de la imagen calibrada
            center_lat = (self.image_bounds["top_left"]["lat"] + self.image_bounds["bottom_right"]["lat"]) / 2
            center_lon = (self.image_bounds["top_left"]["lon"] + self.image_bounds["bottom_right"]["lon"]) / 2
            
            self.map_center["lat"] = center_lat
            self.map_center["lon"] = center_lon
            
            self.update_map()
            
    def update_opacity(self, value):
        """Actualiza la opacidad de la imagen de fondo"""
        self.image_opacity = float(value)
        if self.map_initialized and self.background_image and self.image_calibrated:
            self.update_map()
            
    def save_track(self):
        """Guarda el track GPS en archivo"""
        if not self.track_points:
            messagebox.showwarning("Sin Datos", "No hay puntos de track para guardar")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Guardar track GPS",
            defaultextension=".gpx",
            filetypes=[
                ("GPX", "*.gpx"),
                ("CSV", "*.csv"),
                ("KML", "*.kml"),
                ("Texto", "*.txt")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.save_track_csv(file_path)
                elif file_path.endswith('.gpx'):
                    self.save_track_gpx(file_path)
                elif file_path.endswith('.kml'):
                    self.save_track_kml(file_path)
                else:
                    self.save_track_txt(file_path)
                    
                messagebox.showinfo("Guardado", f"Track guardado en:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
                
    def save_track_csv(self, file_path):
        """Guarda track en formato CSV"""
        with open(file_path, 'w') as f:
            f.write("Timestamp,Latitude,Longitude,HDOP,Time\n")
            for point in self.track_points:
                timestamp = point['time'].strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp},{point['lat']:.8f},{point['lon']:.8f},{point['hdop']:.2f},{point['time'].strftime('%H:%M:%S')}\n")
                
    def save_track_gpx(self, file_path):
        """Guarda track en formato GPX"""
        with open(file_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<gpx version="1.1" creator="Sistema GPS + GY91">\n')
            f.write('  <trk>\n')
            f.write('    <name>Satélite Track</name>\n')
            f.write('    <trkseg>\n')
            
            for point in self.track_points:
                timestamp = point['time'].strftime('%Y-%m-%dT%H:%M:%SZ')
                f.write(f'      <trkpt lat="{point["lat"]:.8f}" lon="{point["lon"]:.8f}">\n')
                f.write(f'        <time>{timestamp}</time>\n')
                f.write(f'        <hdop>{point["hdop"]:.2f}</hdop>\n')
                f.write('      </trkpt>\n')
                
            f.write('    </trkseg>\n')
            f.write('  </trk>\n')
            f.write('</gpx>\n')
            
    def save_track_kml(self, file_path):
        """Guarda track en formato KML"""
        with open(file_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
            f.write('  <Document>\n')
            f.write('    <name>Satélite Track</name>\n')
            f.write('    <Placemark>\n')
            f.write('      <name>Track GPS</name>\n')
            f.write('      <LineString>\n')
            f.write('        <coordinates>\n')
            
            for point in self.track_points:
                f.write(f'          {point["lon"]:.8f},{point["lat"]:.8f},0\n')
                
            f.write('        </coordinates>\n')
            f.write('      </LineString>\n')
            f.write('    </Placemark>\n')
            f.write('  </Document>\n')
            f.write('</kml>\n')
            
    def save_track_txt(self, file_path):
        """Guarda track en formato texto simple"""
        with open(file_path, 'w') as f:
            f.write("TRACK GPS - Sistema de Navegación Satélite\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de puntos: {len(self.track_points)}\n\n")
            
            for i, point in enumerate(self.track_points, 1):
                f.write(f"Punto {i:3d}: {point['lat']:.8f}°, {point['lon']:.8f}° ")
                f.write(f"(HDOP: {point['hdop']:.2f}) - {point['time'].strftime('%H:%M:%S')}\n")

class ImageCalibrationDialog:
    """Diálogo para calibrar imagen con coordenadas GPS"""
    def __init__(self, parent, sensor_data):
        self.result = None
        self.sensor_data = sensor_data
        
        # Crear ventana de diálogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Calibrar Imagen con GPS")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  # Modal
        
        # Centrar ventana
        self.dialog.transient(parent)
        
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="📍 CALIBRACIÓN DE IMAGEN CON GPS", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Instrucciones
        instructions = tk.Text(main_frame, height=4, wrap=tk.WORD, 
                              font=("Arial", 9), bg="#f0f0f0")
        instructions.pack(fill="x", pady=(0, 15))
        instructions.insert("1.0", 
            "Para calibrar la imagen, debe especificar las coordenadas GPS que corresponden a:\n"
            "• Esquina SUPERIOR IZQUIERDA de la imagen\n"
            "• Esquina INFERIOR DERECHA de la imagen\n"
            "Esto permite mapear píxeles de imagen a coordenadas del mundo real.")
        instructions.config(state="disabled")
        
        # Frame para coordenadas
        coords_frame = tk.LabelFrame(main_frame, text="Coordenadas GPS de las esquinas", 
                                   font=("Arial", 10, "bold"))
        coords_frame.pack(fill="x", pady=(0, 15))
        
        # Esquina superior izquierda
        tk.Label(coords_frame, text="🔺 Esquina Superior Izquierda:", 
                font=("Arial", 9, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        tk.Label(coords_frame, text="Latitud:").grid(row=1, column=0, sticky="e", padx=5)
        self.top_left_lat = tk.Entry(coords_frame, width=15)
        self.top_left_lat.grid(row=1, column=1, padx=5)
        self.top_left_lat.insert(0, f"{self.sensor_data['latitude'] + 0.001:.6f}")
        
        tk.Label(coords_frame, text="Longitud:").grid(row=1, column=2, sticky="e", padx=5)
        self.top_left_lon = tk.Entry(coords_frame, width=15)
        self.top_left_lon.grid(row=1, column=3, padx=5)
        self.top_left_lon.insert(0, f"{self.sensor_data['longitude'] - 0.001:.6f}")
        
        # Esquina inferior derecha
        tk.Label(coords_frame, text="🔻 Esquina Inferior Derecha:", 
                font=("Arial", 9, "bold")).grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=(10,5))
        
        tk.Label(coords_frame, text="Latitud:").grid(row=3, column=0, sticky="e", padx=5)
        self.bottom_right_lat = tk.Entry(coords_frame, width=15)
        self.bottom_right_lat.grid(row=3, column=1, padx=5)
        self.bottom_right_lat.insert(0, f"{self.sensor_data['latitude'] - 0.001:.6f}")
        
        tk.Label(coords_frame, text="Longitud:").grid(row=3, column=2, sticky="e", padx=5)
        self.bottom_right_lon = tk.Entry(coords_frame, width=15)
        self.bottom_right_lon.grid(row=3, column=3, padx=5)
        self.bottom_right_lon.insert(0, f"{self.sensor_data['longitude'] + 0.001:.6f}")
        
        # Botón para usar posición actual
        current_pos_frame = tk.Frame(main_frame)
        current_pos_frame.pack(fill="x", pady=(0, 15))
        
        tk.Button(current_pos_frame, text="📍 Usar Posición Actual como Centro", 
                 command=self.use_current_position,
                 bg="#4CAF50", fg="white", font=("Arial", 9)).pack()
        
        if self.sensor_data['latitude'] != 0.0:
            current_info = tk.Label(current_pos_frame, 
                                  text=f"Posición GPS actual: {self.sensor_data['latitude']:.6f}°, {self.sensor_data['longitude']:.6f}°",
                                  font=("Arial", 8), fg="#666")
            current_info.pack(pady=2)
        
        # Botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        tk.Button(button_frame, text="✅ Calibrar", command=self.calibrate,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 10))
        tk.Button(button_frame, text="❌ Cancelar", command=self.cancel,
                 bg="#f44336", fg="white", font=("Arial", 10)).pack(side="left")
        
    def use_current_position(self):
        """Usa la posición GPS actual como centro y estima área"""
        if self.sensor_data['latitude'] == 0.0:
            tk.messagebox.showwarning("Sin GPS", "No hay datos GPS válidos")
            return
            
        # Área estimada de 200m radio
        lat_offset = 0.0018  # Aproximadamente 200m
        lon_offset = 0.0018 / math.cos(math.radians(self.sensor_data['latitude']))
        
        # Actualizar campos
        self.top_left_lat.delete(0, tk.END)
        self.top_left_lat.insert(0, f"{self.sensor_data['latitude'] + lat_offset:.6f}")
        
        self.top_left_lon.delete(0, tk.END) 
        self.top_left_lon.insert(0, f"{self.sensor_data['longitude'] - lon_offset:.6f}")
        
        self.bottom_right_lat.delete(0, tk.END)
        self.bottom_right_lat.insert(0, f"{self.sensor_data['latitude'] - lat_offset:.6f}")
        
        self.bottom_right_lon.delete(0, tk.END)
        self.bottom_right_lon.insert(0, f"{self.sensor_data['longitude'] + lon_offset:.6f}")
        
    def calibrate(self):
        """Aplica la calibración"""
        try:
            self.result = {
                "top_left": {
                    "lat": float(self.top_left_lat.get()),
                    "lon": float(self.top_left_lon.get())
                },
                "bottom_right": {
                    "lat": float(self.bottom_right_lat.get()),
                    "lon": float(self.bottom_right_lon.get())
                }
            }
            
            # Validar que las coordenadas sean válidas
            if (self.result["top_left"]["lat"] <= self.result["bottom_right"]["lat"] or
                self.result["top_left"]["lon"] >= self.result["bottom_right"]["lon"]):
                tk.messagebox.showerror("Error", 
                    "Coordenadas inválidas:\n"
                    "• La latitud superior debe ser mayor que la inferior\n"
                    "• La longitud izquierda debe ser menor que la derecha")
                return
                
            self.dialog.destroy()
            
        except ValueError:
            tk.messagebox.showerror("Error", "Por favor ingrese coordenadas numéricas válidas")
            
    def cancel(self):
        """Cancela la calibración"""
        self.dialog.destroy()

    def add_waypoint(self):
        """Añade un waypoint en la posición actual"""
        if self.sensor_data['latitude'] != 0.0 and self.sensor_data['longitude'] != 0.0:
            waypoint_name = simpledialog.askstring(
                "Nuevo Waypoint",
                f"Nombre para el waypoint en:\n"
                f"Lat: {self.sensor_data['latitude']:.6f}°\n"
                f"Lon: {self.sensor_data['longitude']:.6f}°",
                initialvalue=f"WP{len(self.waypoints)+1}"
            )
            
            if waypoint_name:
                waypoint = {
                    'lat': self.sensor_data['latitude'],
                    'lon': self.sensor_data['longitude'],
                    'name': waypoint_name,
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'hdop': self.sensor_data['hdop']
                }
                self.waypoints.append(waypoint)
                self.update_map()
                
                messagebox.showinfo(
                    "Waypoint Añadido",
                    f"Waypoint '{waypoint_name}' añadido exitosamente\n"
                    f"Posición: {waypoint['lat']:.6f}°, {waypoint['lon']:.6f}°\n"
                    f"Precisión: ±{self.sensor_data['hdop'] * 3:.1f}m"
                )
        else:
            messagebox.showwarning("Sin GPS", "No hay datos GPS válidos para crear waypoint")
        """Añade un waypoint en la posición actual"""
        if self.sensor_data['latitude'] != 0.0 and self.sensor_data['longitude'] != 0.0:
            waypoint = {
                'lat': self.sensor_data['latitude'],
                'lon': self.sensor_data['longitude'],
                'name': f"WP{len(self.waypoints)+1}",
                'time': datetime.now().strftime('%H:%M:%S')
            }
            self.waypoints.append(waypoint)
            self.update_map()
            
    def lat_lon_to_meters(self, lat1, lon1, lat2, lon2):
        """Convierte diferencia lat/lon a metros usando fórmula haversine simplificada"""
        # Para distancias cortas (< 1km) podemos usar aproximación lineal
        R = 6371000  # Radio de la Tierra en metros
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        # Aproximación para distancias cortas
        lat_avg = math.radians((lat1 + lat2) / 2)
        
        dx = R * dlon * math.cos(lat_avg)
        dy = R * dlat
        
        return dx, dy
        
    def meters_to_pixels(self, meters_x, meters_y):
        """Convierte metros a píxeles en el canvas"""
        pixels_x = meters_x / self.meters_per_pixel
        pixels_y = -meters_y / self.meters_per_pixel  # Y negativo porque canvas Y crece hacia abajo
        return pixels_x, pixels_y
        
    def geo_to_canvas(self, lat, lon):
        """Convierte coordenadas geográficas a píxeles del canvas"""
        canvas_width = self.map_canvas.winfo_width() or 800
        canvas_height = self.map_canvas.winfo_height() or 600
        
        # Calcular offset en metros desde el centro del mapa
        dx_meters, dy_meters = self.lat_lon_to_meters(
            self.map_center["lat"], self.map_center["lon"], lat, lon
        )
        
        # Convertir a píxeles
        dx_pixels, dy_pixels = self.meters_to_pixels(dx_meters, dy_meters)
        
        # Posición en canvas
        x = canvas_width / 2 + dx_pixels
        y = canvas_height / 2 + dy_pixels
        
        return x, y
        
    def draw_initial_map(self):
        """Dibuja el mapa inicial"""
        self.map_canvas.delete("all")
        
        canvas_width = self.map_canvas.winfo_width() or 800
        canvas_height = self.map_canvas.winfo_height() or 600
        
        # Texto de instrucciones
        self.map_canvas.create_text(
            canvas_width/2, canvas_height/2,
            text="🛰️ MAPA GPS DE PRECISIÓN\n\nConecte el GPS para comenzar el tracking\n\nClick derecho: Menú\nRueda: Zoom\nArrastrar: Mover mapa",
            fill=self.map_colors["text"],
            font=("Arial", 12),
            justify="center",
            tags="instructions"
        )
        
    def update_map(self):
        """Actualiza el mapa con los datos actuales"""
        if not self.map_initialized:
            return
            
        self.map_canvas.delete("all")
        
        canvas_width = self.map_canvas.winfo_width() or 800
        canvas_height = self.map_canvas.winfo_height() or 600
        
        # Dibujar imagen de fondo si está disponible y habilitada
        if (self.background_var.get() and self.background_image and 
            self.image_calibrated and self.show_background):
            self.draw_background_image(canvas_width, canvas_height)
            
        # Dibujar grilla si está habilitada
        if self.grid_var.get():
            self.draw_grid(canvas_width, canvas_height)
            
        # Dibujar track si hay puntos
        if len(self.track_points) > 1:
            self.draw_track()
            
        # Dibujar waypoints
        self.draw_waypoints()
        
        # Dibujar posición actual
        if self.sensor_data['latitude'] != 0.0 and self.sensor_data['longitude'] != 0.0:
            self.draw_current_position()
            
        # Dibujar círculo de precisión
        if self.precision_circle_var.get() and self.sensor_data['hdop'] > 0:
            self.draw_precision_circle()
            
        # Actualizar etiquetas de información
        self.update_map_info()
        
    def draw_background_image(self, canvas_width, canvas_height):
        """Dibuja la imagen de fondo calibrada"""
        try:
            # Calcular las coordenadas de pantalla para las esquinas de la imagen
            top_left_x, top_left_y = self.geo_to_canvas(
                self.image_bounds["top_left"]["lat"], 
                self.image_bounds["top_left"]["lon"]
            )
            bottom_right_x, bottom_right_y = self.geo_to_canvas(
                self.image_bounds["bottom_right"]["lat"], 
                self.image_bounds["bottom_right"]["lon"]
            )
            
            # Calcular el tamaño necesario de la imagen en píxeles
            image_width = abs(bottom_right_x - top_left_x)
            image_height = abs(bottom_right_y - top_left_y)
            
            if image_width > 0 and image_height > 0:
                # Redimensionar imagen para que encaje en el área calibrada
                resized_image = self.background_image.resize(
                    (int(image_width), int(image_height)), 
                    Image.Resampling.LANCZOS
                )
                
                # Aplicar opacidad
                if self.image_opacity < 1.0:
                    # Crear una imagen con canal alpha
                    if resized_image.mode != 'RGBA':
                        resized_image = resized_image.convert('RGBA')
                    
                    # Ajustar alpha
                    alpha = int(255 * self.image_opacity)
                    resized_image.putalpha(alpha)
                
                # Convertir a PhotoImage para tkinter
                self.background_photo = ImageTk.PhotoImage(resized_image)
                
                # Dibujar la imagen en el canvas
                self.map_canvas.create_image(
                    top_left_x, top_left_y,
                    anchor="nw",
                    image=self.background_photo,
                    tags="background_image"
                )
                
        except Exception as e:
            print(f"Error dibujando imagen de fondo: {e}")
        
    def draw_grid(self, width, height):
        """Dibuja una grilla de referencia"""
        # Calcular espaciado de grilla basado en escala
        if self.meters_per_pixel < 0.1:  # Zoom muy alto
            grid_spacing_meters = 1.0  # 1 metro
        elif self.meters_per_pixel < 0.5:
            grid_spacing_meters = 5.0  # 5 metros
        elif self.meters_per_pixel < 1.0:
            grid_spacing_meters = 10.0  # 10 metros
        elif self.meters_per_pixel < 5.0:
            grid_spacing_meters = 50.0  # 50 metros
        else:
            grid_spacing_meters = 100.0  # 100 metros
            
        grid_spacing_pixels = grid_spacing_meters / self.meters_per_pixel
        
        # Líneas verticales
        start_x = (width / 2) % grid_spacing_pixels
        x = start_x
        while x < width:
            self.map_canvas.create_line(x, 0, x, height, 
                                      fill=self.map_colors["grid"], width=1, tags="grid")
            x += grid_spacing_pixels
            
        # Líneas horizontales
        start_y = (height / 2) % grid_spacing_pixels
        y = start_y
        while y < height:
            self.map_canvas.create_line(0, y, width, y, 
                                      fill=self.map_colors["grid"], width=1, tags="grid")
            y += grid_spacing_pixels
            
        # Etiquetas de escala
        self.map_canvas.create_text(
            20, 20,
            text=f"Grilla: {grid_spacing_meters}m\nEscala: {self.meters_per_pixel:.3f} m/px",
            fill=self.map_colors["text"],
            font=("Arial", 9),
            anchor="nw",
            tags="grid_info"
        )
        
    def draw_track(self):
        """Dibuja el track GPS"""
        if len(self.track_points) < 2:
            return
            
        # Convertir puntos del track a coordenadas de canvas
        canvas_points = []
        for point in self.track_points:
            x, y = self.geo_to_canvas(point['lat'], point['lon'])
            canvas_points.extend([x, y])
            
        # Dibujar línea del track
        if len(canvas_points) >= 4:
            self.map_canvas.create_line(
                canvas_points,
                fill=self.map_colors["track"],
                width=2,
                tags="track",
                smooth=True
            )
            
        # Dibujar puntos individuales del track
        for i, point in enumerate(self.track_points):
            x, y = self.geo_to_canvas(point['lat'], point['lon'])
            
            if 0 <= x <= self.map_canvas.winfo_width() and 0 <= y <= self.map_canvas.winfo_height():
                size = max(2, int(3 / self.meters_per_pixel))
                size = min(size, 8)  # Límite máximo
                
                self.map_canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill=self.map_colors["track"],
                    outline=self.map_colors["track"],
                    tags="track_point"
                )
                
    def draw_waypoints(self):
        """Dibuja los waypoints"""
        for waypoint in self.waypoints:
            x, y = self.geo_to_canvas(waypoint['lat'], waypoint['lon'])
            
            size = max(8, int(12 / self.meters_per_pixel))
            size = min(size, 20)
            
            # Círculo del waypoint
            self.map_canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill=self.map_colors["waypoint"],
                outline="white",
                width=2,
                tags="waypoint"
            )
            
            # Etiqueta del waypoint
            self.map_canvas.create_text(
                x, y - size - 15,
                text=waypoint['name'],
                fill=self.map_colors["waypoint"],
                font=("Arial", 8, "bold"),
                tags="waypoint_label"
            )
            
    def draw_current_position(self):
        """Dibuja la posición actual del GPS"""
        x, y = self.geo_to_canvas(self.sensor_data['latitude'], self.sensor_data['longitude'])
        
        size = max(10, int(15 / self.meters_per_pixel))
        size = min(size, 25)
        
        # Círculo principal (posición actual)
        self.map_canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill=self.map_colors["current"],
            outline="white",
            width=3,
            tags="current_position"
        )
        
        # Punto central
        small_size = max(3, size // 3)
        self.map_canvas.create_oval(
            x - small_size, y - small_size, x + small_size, y + small_size,
            fill="white",
            outline="white",
            tags="current_center"
        )
        
        # Flecha de dirección basada en heading
        if self.sensor_data['heading'] > 0:
            heading_rad = math.radians(self.sensor_data['heading'] - 90)  # Ajustar para que 0° sea norte
            arrow_length = size * 2
            
            end_x = x + arrow_length * math.cos(heading_rad)
            end_y = y + arrow_length * math.sin(heading_rad)
            
            self.map_canvas.create_line(
                x, y, end_x, end_y,
                fill="yellow",
                width=3,
                arrow=tk.LAST,
                arrowshape=(10, 12, 4),
                tags="heading_arrow"
            )
            
    def draw_precision_circle(self):
        """Dibuja el círculo de precisión basado en HDOP"""
        if self.sensor_data['hdop'] <= 0:
            return
            
        # Calcular radio de error en metros (HDOP * factor base)
        base_error = 3.0  # Error base en metros para HDOP = 1
        error_radius_meters = self.sensor_data['hdop'] * base_error
        
        # Convertir a píxeles
        error_radius_pixels = error_radius_meters / self.meters_per_pixel
        
        x, y = self.geo_to_canvas(self.sensor_data['latitude'], self.sensor_data['longitude'])
        
        # Dibujar círculo de precisión
        self.map_canvas.create_oval(
            x - error_radius_pixels, y - error_radius_pixels,
            x + error_radius_pixels, y + error_radius_pixels,
            outline=self.map_colors["precision_circle"],
            width=2,
            tags="precision_circle"
        )
        
        # Etiqueta del radio
        self.map_canvas.create_text(
            x + error_radius_pixels + 10, y,
            text=f"±{error_radius_meters:.1f}m",
            fill=self.map_colors["precision_circle"],
            font=("Arial", 9),
            tags="precision_label"
        )
        
    def update_map_info(self):
        """Actualiza la información del mapa"""
        # Coordenadas
        self.map_coords_label.configure(
            text=f"{self.sensor_data['latitude']:.6f}°, {self.sensor_data['longitude']:.6f}°"
        )
        
        # HDOP y error estimado
        if self.sensor_data['hdop'] > 0:
            error_estimate = self.sensor_data['hdop'] * 3.0
            hdop_color = "#00aa00" if self.sensor_data['hdop'] < 2.0 else "#ffaa00" if self.sensor_data['hdop'] < 5.0 else "#ff4444"
            self.map_hdop_label.configure(
                text=f"{self.sensor_data['hdop']:.1f} (Error: ±{error_estimate:.1f}m)",
                text_color=hdop_color
            )
        else:
            self.map_hdop_label.configure(text="Sin datos HDOP")
            
        # Escala actual
        self.map_scale_label.configure(text=f"{self.meters_per_pixel:.3f} m/píxel")
        
        # Estadísticas del track
        self.track_points_label.configure(text=str(len(self.track_points)))
        
        if len(self.track_points) > 1:
            # Calcular distancia total
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
                
            self.track_distance_label.configure(text=f"{total_distance:.1f} m")
            
            # Calcular dispersión (desviación estándar de posiciones)
            if len(self.track_points) > 2:
                # Calcular centro geométrico
                center_lat = sum(p['lat'] for p in self.track_points) / len(self.track_points)
                center_lon = sum(p['lon'] for p in self.track_points) / len(self.track_points)
                
                # Calcular dispersión RMS
                rms_error = 0.0
                for point in self.track_points:
                    dx, dy = self.lat_lon_to_meters(center_lat, center_lon, point['lat'], point['lon'])
                    rms_error += dx*dx + dy*dy
                    
                rms_error = math.sqrt(rms_error / len(self.track_points))
                self.dispersion_label.configure(text=f"{rms_error:.1f} m")
            else:
                self.dispersion_label.configure(text="N/A")
        else:
            self.track_distance_label.configure(text="0.0 m")
            self.dispersion_label.configure(text="0.0 m")
            
    def on_map_click(self, event):
        """Maneja el click en el mapa"""
        self.map_last_x = event.x
        self.map_last_y = event.y
        
    def on_map_drag(self, event):
        """Maneja el arrastre del mapa"""
        dx = event.x - self.map_last_x
        dy = event.y - self.map_last_y
        
        # Convertir píxeles a metros
        dx_meters = dx * self.meters_per_pixel
        dy_meters = -dy * self.meters_per_pixel  # Y negativo
        
        # Convertir metros a cambio en lat/lon
        R = 6371000  # Radio de la Tierra
        dlat = dy_meters / R * 180 / math.pi
        dlon = dx_meters / (R * math.cos(math.radians(self.map_center["lat"]))) * 180 / math.pi
        
        self.map_center["lat"] -= dlat
        self.map_center["lon"] -= dlon
        
        self.map_last_x = event.x
        self.map_last_y = event.y
        
        # Desactivar auto-centrar temporalmente
        self.auto_center = False
        self.auto_center_var.set(False)
        
        self.update_map()
        
    def on_map_wheel(self, event):
        """Maneja el zoom con la rueda del mouse"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
            
    def on_map_right_click(self, event):
        """Maneja el click derecho en el mapa"""
        # Crear menú contextual
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="📍 Centrar aquí", command=self.center_map)
        context_menu.add_command(label="📌 Añadir waypoint", command=self.add_waypoint)
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Limpiar track", command=self.clear_track)
        context_menu.add_command(label="🔄 Reset zoom", command=lambda: self.set_zoom_scale(20))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def tab_changed(self):
        """Callback cuando cambia de pestaña"""
        self.current_tab = self.tabview.get()
        
        if self.current_tab == "📈 Gráficas Tiempo Real" and not self.plots_initialized:
            self.setup_plots_tab()
            self.plots_initialized = True
            
    def setup_realtime_tab(self):
        """Configura la pestaña de monitor en tiempo real"""
        realtime_frame = self.tabview.tab("📊 Monitor Tiempo Real")
        
        # Frame principal de datos con 3 columnas
        sensors_frame = ctk.CTkFrame(realtime_frame)
        sensors_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # === COLUMNA 1: GPS ===
        gps_frame = ctk.CTkFrame(sensors_frame)
        gps_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        gps_title = ctk.CTkLabel(gps_frame, 
                               text="🛰️ GPS - POSICIONAMIENTO GLOBAL",
                               font=ctk.CTkFont(size=16, weight="bold"),
                               text_color="#00aa00")
        gps_title.pack(pady=5)
        
        # Coordenadas
        coords_title = ctk.CTkLabel(gps_frame, text="📍 COORDENADAS",
                                  font=ctk.CTkFont(size=12, weight="bold"))
        coords_title.pack(pady=(5, 2))
        
        # Latitud
        lat_frame = ctk.CTkFrame(gps_frame)
        lat_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(lat_frame, text="Latitud:", width=80).pack(side="left", padx=5)
        self.lat_label = ctk.CTkLabel(lat_frame, text="0.000000°",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    text_color="#ff6600")
        self.lat_label.pack(side="right", padx=5)
        
        # Longitud
        lon_frame = ctk.CTkFrame(gps_frame)
        lon_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(lon_frame, text="Longitud:", width=80).pack(side="left", padx=5)
        self.lon_label = ctk.CTkLabel(lon_frame, text="0.000000°",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    text_color="#ff6600")
        self.lon_label.pack(side="right", padx=5)
        
        # Altitud GPS
        gps_alt_frame = ctk.CTkFrame(gps_frame)
        gps_alt_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(gps_alt_frame, text="🏔️ Alt GPS:", width=80).pack(side="left", padx=5)
        self.gps_alt_label = ctk.CTkLabel(gps_alt_frame, text="0.0 m",
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        text_color="#aa00ff")
        self.gps_alt_label.pack(side="right", padx=5)
        
        # Velocidad
        speed_frame = ctk.CTkFrame(gps_frame)
        speed_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(speed_frame, text="🚀 Velocidad:", width=80).pack(side="left", padx=5)
        self.speed_label = ctk.CTkLabel(speed_frame, text="0.0 km/h",
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      text_color="#0066ff")
        self.speed_label.pack(side="right", padx=5)
        
        # Estado GPS
        gps_status_title = ctk.CTkLabel(gps_frame, text="🔧 ESTADO GPS",
                                      font=ctk.CTkFont(size=12, weight="bold"))
        gps_status_title.pack(pady=(10, 2))
        
        # Satélites
        sat_frame = ctk.CTkFrame(gps_frame)
        sat_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(sat_frame, text="Satélites:", width=80).pack(side="left", padx=5)
        self.sat_label = ctk.CTkLabel(sat_frame, text="0",
                                    font=ctk.CTkFont(size=12, weight="bold"))
        self.sat_label.pack(side="right", padx=5)
        
        # Calidad Fix
        fix_frame = ctk.CTkFrame(gps_frame)
        fix_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(fix_frame, text="Fix:", width=80).pack(side="left", padx=5)
        self.fix_label = ctk.CTkLabel(fix_frame, text="0",
                                    font=ctk.CTkFont(size=12, weight="bold"))
        self.fix_label.pack(side="right", padx=5)
        
        # HDOP/VDOP
        dop_frame = ctk.CTkFrame(gps_frame)
        dop_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(dop_frame, text="HDOP/VDOP:", width=80).pack(side="left", padx=5)
        self.dop_label = ctk.CTkLabel(dop_frame, text="0.0 / 0.0",
                                    font=ctk.CTkFont(size=11, weight="bold"))
        self.dop_label.pack(side="right", padx=5)
        
        # Tiempo UTC
        utc_frame = ctk.CTkFrame(gps_frame)
        utc_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(utc_frame, text="UTC:", width=80).pack(side="left", padx=5)
        self.utc_label = ctk.CTkLabel(utc_frame, text="--:--:--",
                                    font=ctk.CTkFont(size=12, weight="bold"),
                                    text_color="#00dd00")
        self.utc_label.pack(side="right", padx=5)
        
        # Especificaciones GPS
        gps_specs_frame = ctk.CTkFrame(gps_frame)
        gps_specs_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(gps_specs_frame, text="📋 ESPECIFICACIONES",
                   font=ctk.CTkFont(size=12, weight="bold")).pack(pady=2)
        ctk.CTkLabel(gps_specs_frame, text="• Precisión: ±3m (CEP)",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
        ctk.CTkLabel(gps_specs_frame, text="• Actualización: 1Hz",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
        ctk.CTkLabel(gps_specs_frame, text="• Canales: 72",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
        
        # === COLUMNA 2: BMP280 ===
        bmp_frame = ctk.CTkFrame(sensors_frame)
        bmp_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        bmp_title = ctk.CTkLabel(bmp_frame, 
                               text="📊 BMP280 - SENSOR BAROMÉTRICO",
                               font=ctk.CTkFont(size=16, weight="bold"),
                               text_color="#ff8800")
        bmp_title.pack(pady=5)
        
        # Temperatura BMP280
        bmp_temp_frame = ctk.CTkFrame(bmp_frame)
        bmp_temp_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(bmp_temp_frame, text="🌡️ Temperatura:", width=100).pack(side="left", padx=5)
        self.bmp_temp_label = ctk.CTkLabel(bmp_temp_frame, text="0.00 °C",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         text_color="#ff6600")
        self.bmp_temp_label.pack(side="right", padx=5)
        
        # Presión BMP280
        bmp_pres_frame = ctk.CTkFrame(bmp_frame)
        bmp_pres_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(bmp_pres_frame, text="📏 Presión:", width=100).pack(side="left", padx=5)
        self.bmp_pres_label = ctk.CTkLabel(bmp_pres_frame, text="0.00 mbar",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         text_color="#0066ff")
        self.bmp_pres_label.pack(side="right", padx=5)
        
        # Altitud BMP280
        bmp_alt_frame = ctk.CTkFrame(bmp_frame)
        bmp_alt_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(bmp_alt_frame, text="🏔️ Alt Baro:", width=100).pack(side="left", padx=5)
        self.bmp_alt_label = ctk.CTkLabel(bmp_alt_frame, text="0.0 m",
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        text_color="#aa00ff")
        self.bmp_alt_label.pack(side="right", padx=5)
        
        # Diferencia de Altitudes
        alt_comp_title = ctk.CTkLabel(bmp_frame, text="📏 COMPARACIÓN ALTITUD",
                                    font=ctk.CTkFont(size=12, weight="bold"))
        alt_comp_title.pack(pady=(10, 2))
        
        diff_alt_frame = ctk.CTkFrame(bmp_frame)
        diff_alt_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(diff_alt_frame, text="ΔH (GPS-Baro):", width=100).pack(side="left", padx=5)
        self.diff_alt_label = ctk.CTkLabel(diff_alt_frame, text="0.0 m",
                                         font=ctk.CTkFont(size=14, weight="bold"))
        self.diff_alt_label.pack(side="right", padx=5)
        
        # Características BMP280
        bmp_specs_frame = ctk.CTkFrame(bmp_frame)
        bmp_specs_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(bmp_specs_frame, text="📋 ESPECIFICACIONES",
                   font=ctk.CTkFont(size=12, weight="bold")).pack(pady=2)
        ctk.CTkLabel(bmp_specs_frame, text="• Resolución: 0.18 Pa",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
        ctk.CTkLabel(bmp_specs_frame, text="• Precisión: ±1 hPa",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
        ctk.CTkLabel(bmp_specs_frame, text="• Rango: 300-1100 hPa",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
        ctk.CTkLabel(bmp_specs_frame, text="• Bus: I2C (0x76)",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
        
        # === COLUMNA 3: MPU9250 ===
        mpu_frame = ctk.CTkFrame(sensors_frame)
        mpu_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        mpu_title = ctk.CTkLabel(mpu_frame, 
                               text="🧭 MPU9250 - IMU 9-DOF",
                               font=ctk.CTkFont(size=16, weight="bold"),
                               text_color="#0088ff")
        mpu_title.pack(pady=5)
        
        # Temperatura MPU9250
        mpu_temp_frame = ctk.CTkFrame(mpu_frame)
        mpu_temp_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(mpu_temp_frame, text="🌡️ Temp IMU:", width=100).pack(side="left", padx=5)
        self.mpu_temp_label = ctk.CTkLabel(mpu_temp_frame, text="0.0 °C",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         text_color="#ff6600")
        self.mpu_temp_label.pack(side="right", padx=5)
        
        # Acelerómetro
        accel_title = ctk.CTkLabel(mpu_frame, text="🎯 ACELERÓMETRO",
                                 font=ctk.CTkFont(size=12, weight="bold"))
        accel_title.pack(pady=(5, 2))
        
        accel_xyz_frame = ctk.CTkFrame(mpu_frame)
        accel_xyz_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(accel_xyz_frame, text="X,Y,Z:", width=50).pack(side="left", padx=5)
        self.accel_label = ctk.CTkLabel(accel_xyz_frame, text="0.000, 0.000, 0.000 g",
                                      font=ctk.CTkFont(size=11, weight="bold"),
                                      text_color="#ff8800")
        self.accel_label.pack(side="right", padx=5)
        
        accel_total_frame = ctk.CTkFrame(mpu_frame)
        accel_total_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(accel_total_frame, text="|A|:", width=50).pack(side="left", padx=5)
        self.accel_total_label = ctk.CTkLabel(accel_total_frame, text="0.000 g",
                                            font=ctk.CTkFont(size=12, weight="bold"),
                                            text_color="#ff4400")
        self.accel_total_label.pack(side="right", padx=5)
        
        # Giroscopio
        gyro_title = ctk.CTkLabel(mpu_frame, text="🌀 GIROSCOPIO",
                                font=ctk.CTkFont(size=12, weight="bold"))
        gyro_title.pack(pady=(5, 2))
        
        gyro_xyz_frame = ctk.CTkFrame(mpu_frame)
        gyro_xyz_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(gyro_xyz_frame, text="X,Y,Z:", width=50).pack(side="left", padx=5)
        self.gyro_label = ctk.CTkLabel(gyro_xyz_frame, text="0.00, 0.00, 0.00 dps",
                                     font=ctk.CTkFont(size=11, weight="bold"),
                                     text_color="#0088ff")
        self.gyro_label.pack(side="right", padx=5)
        
        gyro_total_frame = ctk.CTkFrame(mpu_frame)
        gyro_total_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(gyro_total_frame, text="|G|:", width=50).pack(side="left", padx=5)
        self.gyro_total_label = ctk.CTkLabel(gyro_total_frame, text="0.00 dps",
                                           font=ctk.CTkFont(size=12, weight="bold"),
                                           text_color="#0066dd")
        self.gyro_total_label.pack(side="right", padx=5)
        
        # Magnetómetro
        mag_title = ctk.CTkLabel(mpu_frame, text="🧲 MAGNETÓMETRO",
                               font=ctk.CTkFont(size=12, weight="bold"))
        mag_title.pack(pady=(5, 2))
        
        mag_xyz_frame = ctk.CTkFrame(mpu_frame)
        mag_xyz_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(mag_xyz_frame, text="X,Y,Z:", width=50).pack(side="left", padx=5)
        self.mag_label = ctk.CTkLabel(mag_xyz_frame, text="0.0, 0.0, 0.0 µT",
                                    font=ctk.CTkFont(size=11, weight="bold"),
                                    text_color="#aa00ff")
        self.mag_label.pack(side="right", padx=5)
        
        # Orientación
        orient_title = ctk.CTkLabel(mpu_frame, text="📐 ORIENTACIÓN",
                                  font=ctk.CTkFont(size=12, weight="bold"))
        orient_title.pack(pady=(5, 2))
        
        # Roll, Pitch, Yaw
        rpy_frame = ctk.CTkFrame(mpu_frame)
        rpy_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(rpy_frame, text="R,P,Y:", width=50).pack(side="left", padx=5)
        self.rpy_label = ctk.CTkLabel(rpy_frame, text="0.0°, 0.0°, 0.0°",
                                    font=ctk.CTkFont(size=11, weight="bold"),
                                    text_color="#00aa44")
        self.rpy_label.pack(side="right", padx=5)
        
        # Heading
        heading_frame = ctk.CTkFrame(mpu_frame)
        heading_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(heading_frame, text="Rumbo:", width=50).pack(side="left", padx=5)
        self.heading_label = ctk.CTkLabel(heading_frame, text="0.0° (N)",
                                        font=ctk.CTkFont(size=12, weight="bold"),
                                        text_color="#00dd00")
        self.heading_label.pack(side="right", padx=5)
        
        # Frame inferior con monitor y estado
        bottom_frame = ctk.CTkFrame(realtime_frame)
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Monitor de datos
        monitor_frame = ctk.CTkFrame(bottom_frame)
        monitor_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        monitor_title = ctk.CTkLabel(monitor_frame, text="📄 Monitor de Datos",
                                   font=ctk.CTkFont(size=14, weight="bold"))
        monitor_title.pack(pady=5)
        
        self.data_display = ctk.CTkTextbox(monitor_frame, height=120)
        self.data_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Panel de estado
        status_frame = ctk.CTkFrame(bottom_frame)
        status_frame.pack(side="right", fill="y", padx=2, pady=5)
        
        status_title = ctk.CTkLabel(status_frame, text="⚡ ESTADO DEL SISTEMA",
                                  font=ctk.CTkFont(size=14, weight="bold"))
        status_title.pack(pady=5)
        
        # Última actualización
        update_frame = ctk.CTkFrame(status_frame)
        update_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(update_frame, text="🕒 Última actualización:",
                   font=ctk.CTkFont(size=10)).pack()
        self.last_update_label = ctk.CTkLabel(update_frame, text="No hay datos",
                                            font=ctk.CTkFont(size=10),
                                            text_color="#888888")
        self.last_update_label.pack()
        
        # Calidad de datos
        quality_frame = ctk.CTkFrame(status_frame)
        quality_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(quality_frame, text="📊 Calidad de datos:",
                   font=ctk.CTkFont(size=10)).pack()
        self.quality_label = ctk.CTkLabel(quality_frame, text="N/A",
                                        font=ctk.CTkFont(size=10, weight="bold"))
        self.quality_label.pack()
        
        # Botones de control
        ctk.CTkButton(status_frame, text="Limpiar Monitor",
                    command=self.clear_display).pack(pady=5)
        
    def setup_plots_tab(self):
        """Configura la pestaña de gráficas"""
        plots_frame = self.tabview.tab("📈 Gráficas Tiempo Real")
        
        # Control panel para gráficas
        control_frame = ctk.CTkFrame(plots_frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(control_frame, text="🎛️ CONTROLES DE GRÁFICAS",
                   font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
        
        # Buffer size control
        ctk.CTkLabel(control_frame, text="Buffer:", font=ctk.CTkFont(size=10)).pack(side="left", padx=5)
        self.buffer_var = ctk.StringVar(value="500")
        buffer_select = ctk.CTkOptionMenu(control_frame, variable=self.buffer_var,
                                        values=["250", "500", "1000"],
                                        command=self.update_buffer_size)
        buffer_select.pack(side="left", padx=5)
        
        ctk.CTkButton(control_frame, text="🗑️ Limpiar Datos",
                    command=self.clear_plot_data).pack(side="left", padx=10)
        
        # Crear figura con subplots
        self.fig, self.axes = plt.subplots(3, 3, figsize=(12, 8))
        self.fig.patch.set_facecolor('#212121')
        self.fig.suptitle('Sistema GPS + GY91 - Datos Tiempo Real', fontsize=12, color='white')
        
        # Configurar subplots
        plot_titles = [
            "GPS - Latitud/Longitud", "GPS - Altitud/Velocidad", "BMP280 - Temp/Presión",
            "Acelerómetro (g)", "Giroscopio (dps)", "Magnetómetro (µT)",
            "Orientación (°)", "Rumbo/Heading (°)", "Altitudes GPS vs BMP280"
        ]
        
        for i, (row, col) in enumerate([(r, c) for r in range(3) for c in range(3)]):
            ax = self.axes[row, col]
            ax.set_title(plot_titles[i], fontsize=9, color='white')
            ax.set_facecolor('#2b2b2b')
            ax.tick_params(colors='white', labelsize=7)
            ax.grid(True, alpha=0.2)
            
            for spine in ax.spines.values():
                spine.set_color('white')
        
        plt.tight_layout()
        
        # Integrar matplotlib con tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, plots_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurar animación
        self.animation = FuncAnimation(self.fig, self.update_plots, interval=2000, blit=False)
        
    def update_buffer_size(self, new_size):
        """Actualiza el tamaño del buffer de datos"""
        try:
            new_max = int(new_size)
            self.max_data_points = new_max
            
            # Recrear buffers con nuevo tamaño
            self.time_buffer = deque(list(self.time_buffer)[-new_max:], maxlen=new_max)
            
            for key in self.gps_data:
                self.gps_data[key] = deque(list(self.gps_data[key])[-new_max:], maxlen=new_max)
            for key in self.bmp280_data:
                self.bmp280_data[key] = deque(list(self.bmp280_data[key])[-new_max:], maxlen=new_max)
            for key in self.mpu9250_data:
                self.mpu9250_data[key] = deque(list(self.mpu9250_data[key])[-new_max:], maxlen=new_max)
                
        except ValueError:
            pass
            
    def clear_plot_data(self):
        """Limpia todos los datos de las gráficas"""
        self.time_buffer.clear()
        for key in self.gps_data:
            self.gps_data[key].clear()
        for key in self.bmp280_data:
            self.bmp280_data[key].clear()
        for key in self.mpu9250_data:
            self.mpu9250_data[key].clear()
    
    def toggle_plotting(self):
        """Toggle para pausar/reanudar gráficas"""
        self.plotting_enabled = not self.plotting_enabled
        if self.plotting_enabled:
            self.plot_toggle.configure(text="⏸️ Pausar Gráficas")
        else:
            self.plot_toggle.configure(text="▶️ Reanudar Gráficas")
    
    def update_plots(self, frame):
        """Actualiza gráficas"""
        if (self.current_tab != "📈 Gráficas Tiempo Real" or 
            not self.plotting_enabled or 
            len(self.time_buffer) < 5):
            return
        
        try:
            times = list(self.time_buffer)
            step = max(1, len(times) // 200)
            times_sampled = times[::step]
            
            # Limpiar plots
            for ax in self.axes.flat:
                ax.clear()
                ax.set_facecolor('#2b2b2b')
                ax.tick_params(colors='white', labelsize=7)
                ax.grid(True, alpha=0.2)
                for spine in ax.spines.values():
                    spine.set_color('white')
            
            # Plot datos GPS y sensores
            if len(self.gps_data['latitude']) > 0:
                # GPS Coordenadas
                self.axes[0, 0].plot(times_sampled, list(self.gps_data['latitude'])[::step], 'g-', label='Lat', linewidth=1)
                self.axes[0, 0].plot(times_sampled, list(self.gps_data['longitude'])[::step], 'r-', label='Lon', linewidth=1)
                self.axes[0, 0].set_title("GPS - Latitud/Longitud", fontsize=9, color='white')
                self.axes[0, 0].legend(fontsize=7)
                
                # GPS Altitud/Velocidad
                ax2 = self.axes[0, 1].twinx()
                self.axes[0, 1].plot(times_sampled, list(self.gps_data['altitude'])[::step], 'b-', label='Alt (m)', linewidth=1)
                ax2.plot(times_sampled, list(self.gps_data['speed'])[::step], 'orange', label='Vel (km/h)', linewidth=1)
                self.axes[0, 1].set_title("GPS - Altitud/Velocidad", fontsize=9, color='white')
                self.axes[0, 1].legend(loc='upper left', fontsize=7)
                ax2.legend(loc='upper right', fontsize=7)
                
                # BMP280
                ax3 = self.axes[0, 2].twinx()
                self.axes[0, 2].plot(times_sampled, list(self.bmp280_data['temp'])[::step], 'r-', label='Temp (°C)', linewidth=1)
                ax3.plot(times_sampled, list(self.bmp280_data['pressure'])[::step], 'b-', label='Pres (mbar)', linewidth=1)
                self.axes[0, 2].set_title("BMP280 - Temp/Presión", fontsize=9, color='white')
                self.axes[0, 2].legend(loc='upper left', fontsize=7)
                ax3.legend(loc='upper right', fontsize=7)
                
                # MPU9250 plots
                if len(self.mpu9250_data['accel_x']) > 0:
                    # Acelerómetro
                    self.axes[1, 0].plot(times_sampled, list(self.mpu9250_data['accel_x'])[::step], 'r-', linewidth=1, alpha=0.8)
                    self.axes[1, 0].plot(times_sampled, list(self.mpu9250_data['accel_y'])[::step], 'g-', linewidth=1, alpha=0.8)
                    self.axes[1, 0].plot(times_sampled, list(self.mpu9250_data['accel_z'])[::step], 'b-', linewidth=1, alpha=0.8)
                    self.axes[1, 0].set_title("Acelerómetro (g)", fontsize=9, color='white')
                    
                    # Giroscopio
                    self.axes[1, 1].plot(times_sampled, list(self.mpu9250_data['gyro_x'])[::step], 'r-', linewidth=1, alpha=0.8)
                    self.axes[1, 1].plot(times_sampled, list(self.mpu9250_data['gyro_y'])[::step], 'g-', linewidth=1, alpha=0.8)
                    self.axes[1, 1].plot(times_sampled, list(self.mpu9250_data['gyro_z'])[::step], 'b-', linewidth=1, alpha=0.8)
                    self.axes[1, 1].set_title("Giroscopio (dps)", fontsize=9, color='white')
                    
                    # Magnetómetro
                    self.axes[1, 2].plot(times_sampled, list(self.mpu9250_data['mag_x'])[::step], 'r-', linewidth=1, alpha=0.8)
                    self.axes[1, 2].plot(times_sampled, list(self.mpu9250_data['mag_y'])[::step], 'g-', linewidth=1, alpha=0.8)
                    self.axes[1, 2].plot(times_sampled, list(self.mpu9250_data['mag_z'])[::step], 'b-', linewidth=1, alpha=0.8)
                    self.axes[1, 2].set_title("Magnetómetro (µT)", fontsize=9, color='white')
                    
                    # Orientación
                    self.axes[2, 0].plot(times_sampled, list(self.mpu9250_data['roll'])[::step], 'r-', linewidth=1)
                    self.axes[2, 0].plot(times_sampled, list(self.mpu9250_data['pitch'])[::step], 'g-', linewidth=1)
                    self.axes[2, 0].plot(times_sampled, list(self.mpu9250_data['yaw'])[::step], 'b-', linewidth=1)
                    self.axes[2, 0].set_title("Orientación (°)", fontsize=9, color='white')
                    
                    # Rumbo
                    self.axes[2, 1].plot(times_sampled, list(self.mpu9250_data['heading'])[::step], 'lime', linewidth=1)
                    self.axes[2, 1].set_title("Rumbo Magnético (°)", fontsize=9, color='white')
                    self.axes[2, 1].set_ylim(0, 360)
                
                # Comparación altitudes
                self.axes[2, 2].plot(times_sampled, list(self.gps_data['altitude'])[::step], 'g-', label='GPS', linewidth=1)
                self.axes[2, 2].plot(times_sampled, list(self.bmp280_data['altitude'])[::step], 'orange', label='BMP280', linewidth=1)
                self.axes[2, 2].set_title("Altitudes GPS vs BMP280", fontsize=9, color='white')
                self.axes[2, 2].legend(fontsize=7)
            
            # Formateo de fecha
            for i, ax in enumerate([self.axes[2, 0], self.axes[2, 1], self.axes[2, 2]]):
                if len(times_sampled) > 1:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=6)
            
            plt.tight_layout()
            self.canvas.draw_idle()
            
        except Exception as e:
            pass
        
    def get_cardinal_direction(self, heading):
        """Convierte grados a dirección cardinal"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = int((heading + 11.25) / 22.5) % 16
        return directions[index]
        
    def update_all_displays(self):
        """Actualiza displays con throttling para mejor rendimiento"""
        current_time = time.time()
        
        if current_time - self.last_ui_update < self.ui_update_interval:
            return
            
        self.last_ui_update = current_time
        
        # GPS
        self.lat_label.configure(text=f"{self.sensor_data['latitude']:.6f}° {self.sensor_data['lat_dir']}")
        self.lon_label.configure(text=f"{self.sensor_data['longitude']:.6f}° {self.sensor_data['lon_dir']}")
        self.gps_alt_label.configure(text=f"{self.sensor_data['gps_altitude']:.1f} m")
        self.speed_label.configure(text=f"{self.sensor_data['speed']:.1f} km/h")
        
        # Estado GPS con colores
        sat_count = self.sensor_data['satellites']
        sat_color = "#00aa00" if sat_count >= 8 else "#ffaa00" if sat_count >= 4 else "#ff4444"
        self.sat_label.configure(text=str(sat_count), text_color=sat_color)
        
        fix_quality = self.sensor_data['fix_quality']
        fix_color = "#00aa00" if fix_quality >= 2 else "#ffaa00" if fix_quality == 1 else "#ff4444"
        fix_text = "3D Fix" if fix_quality >= 2 else "2D Fix" if fix_quality == 1 else "No Fix"
        self.fix_label.configure(text=fix_text, text_color=fix_color)
        
        self.dop_label.configure(text=f"{self.sensor_data['hdop']:.1f} / {self.sensor_data['vdop']:.1f}")
        self.utc_label.configure(text=self.sensor_data['utc_time'])
        
        # BMP280
        self.bmp_temp_label.configure(text=f"{self.sensor_data['bmp_temp']:.2f} °C")
        self.bmp_pres_label.configure(text=f"{self.sensor_data['pressure']:.2f} mbar")
        self.bmp_alt_label.configure(text=f"{self.sensor_data['bmp_altitude']:.1f} m")
        
        # Diferencia de altitudes
        alt_diff = abs(self.sensor_data['altitude_diff'])
        alt_color = "#00aa00" if alt_diff < 5.0 else "#ffaa00" if alt_diff < 15.0 else "#ff4444"
        self.diff_alt_label.configure(text=f"{self.sensor_data['altitude_diff']:.1f} m", text_color=alt_color)
        
        # MPU9250
        self.mpu_temp_label.configure(text=f"{self.sensor_data['mpu_temp']:.1f} °C")
        self.accel_label.configure(text=f"{self.sensor_data['accel_x']:.3f}, {self.sensor_data['accel_y']:.3f}, {self.sensor_data['accel_z']:.3f} g")
        self.accel_total_label.configure(text=f"{self.sensor_data['total_accel']:.3f} g")
        self.gyro_label.configure(text=f"{self.sensor_data['gyro_x']:.2f}, {self.sensor_data['gyro_y']:.2f}, {self.sensor_data['gyro_z']:.2f} dps")
        self.gyro_total_label.configure(text=f"{self.sensor_data['total_gyro']:.2f} dps")
        self.mag_label.configure(text=f"{self.sensor_data['mag_x']:.1f}, {self.sensor_data['mag_y']:.1f}, {self.sensor_data['mag_z']:.1f} µT")
        self.rpy_label.configure(text=f"{self.sensor_data['roll']:.1f}°, {self.sensor_data['pitch']:.1f}°, {self.sensor_data['yaw']:.1f}°")
        
        # Heading con dirección cardinal
        cardinal = self.get_cardinal_direction(self.sensor_data['heading'])
        self.heading_label.configure(text=f"{self.sensor_data['heading']:.1f}° ({cardinal})")
        
        # Estado del sistema
        self.last_update_label.configure(text=self.sensor_data['last_update'])
        
        # Calidad de datos basada en GPS y sensores
        if sat_count >= 8 and fix_quality >= 2 and 0.95 < self.sensor_data['total_accel'] < 1.05:
            quality_text, quality_color = "ALTA", "#00aa00"
        elif sat_count >= 4 and fix_quality >= 1:
            quality_text, quality_color = "MEDIA", "#ffaa00"
        else:
            quality_text, quality_color = "BAJA", "#ff4444"
        
        self.quality_label.configure(text=quality_text, text_color=quality_color)
        
        # Actualizar mapa si la pestaña está activa y tenemos datos GPS válidos
        if (self.current_tab == "🗺️ Mapa GPS" and 
            self.map_initialized and 
            self.sensor_data['latitude'] != 0.0 and 
            self.sensor_data['longitude'] != 0.0):
            
            # Añadir punto al track
            new_point = {
                'lat': self.sensor_data['latitude'],
                'lon': self.sensor_data['longitude'],
                'time': datetime.now(),
                'hdop': self.sensor_data['hdop']
            }
            self.track_points.append(new_point)
            
            # Auto-centrar si está habilitado
            if self.auto_center:
                self.map_center["lat"] = self.sensor_data['latitude']
                self.map_center["lon"] = self.sensor_data['longitude']
            
            # Actualizar mapa (throttling incluido)
            self.update_map()
        
    def parse_gps_gy91_data(self, data_str):
        """Parsea datos del sistema GPS + GY91"""
        try:
            parts = data_str.split(',')
            
            if len(parts) >= 28:  # 11 GPS + 17 GY91
                current_time = datetime.now()
                
                data = self.sensor_data
                
                # Datos GPS (campos 0-10)
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
                
                # Datos GY91 - BMP280 (campos 11-13)
                data['bmp_temp'] = float(parts[11])
                data['pressure'] = float(parts[12])
                data['bmp_altitude'] = float(parts[13])
                
                # Datos GY91 - MPU9250 (campos 14-27)
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
                
                # Calcular magnitudes totales
                data['total_accel'] = math.sqrt(data['accel_x']**2 + data['accel_y']**2 + data['accel_z']**2)
                data['total_gyro'] = math.sqrt(data['gyro_x']**2 + data['gyro_y']**2 + data['gyro_z']**2)
                data['total_mag'] = math.sqrt(data['mag_x']**2 + data['mag_y']**2 + data['mag_z']**2)
                
                # Calcular diferencia de altitudes
                data['altitude_diff'] = data['gps_altitude'] - data['bmp_altitude']
                
                # Actualizar timestamp
                data['last_update'] = current_time.strftime('%H:%M:%S.%f')[:-3]
                
                # Agregar a buffers solo si las gráficas están habilitadas y visibles
                if (self.plotting_enabled and 
                    self.current_tab == "📈 Gráficas Tiempo Real" and 
                    self.plots_initialized):
                    
                    self.time_buffer.append(current_time)
                    
                    # GPS
                    self.gps_data['latitude'].append(data['latitude'])
                    self.gps_data['longitude'].append(data['longitude'])
                    self.gps_data['altitude'].append(data['gps_altitude'])
                    self.gps_data['speed'].append(data['speed'])
                    self.gps_data['satellites'].append(data['satellites'])
                    self.gps_data['hdop'].append(data['hdop'])
                    self.gps_data['vdop'].append(data['vdop'])
                    
                    # BMP280
                    self.bmp280_data['temp'].append(data['bmp_temp'])
                    self.bmp280_data['pressure'].append(data['pressure'])
                    self.bmp280_data['altitude'].append(data['bmp_altitude'])
                    
                    # MPU9250
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
                
                # Incrementar contador
                self.data_count += 1
                
                return True
                
        except (ValueError, IndexError):
            return False
        
        return False
        
    def get_ports(self):
        """Obtiene lista de puertos seriales disponibles"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else ["No hay puertos"]
    
    def update_ports(self):
        """Actualiza la lista de puertos disponibles"""
        self.port_select.configure(values=self.get_ports())
        
    def toggle_connection(self):
        """Conectar/Desconectar puerto serial"""
        if not self.is_running:
            try:
                port = self.port_var.get()
                baud = int(self.baud_var.get())
                self.serial_port = serial.Serial(port, baud, timeout=0.1)
                self.is_running = True
                self.connect_btn.configure(text="Desconectar")
                self.status_label.configure(text=f"🟢 Conectado a {port}")
                
                # Iniciar thread de lectura
                self.read_thread = threading.Thread(target=self.read_serial)
                self.read_thread.daemon = True
                self.read_thread.start()
                
                # Mensaje de inicio
                timestamp = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
                self.data_display.insert("end", f"{timestamp}Sistema GPS + GY91 conectado a {port}\n")
                self.data_display.insert("end", f"{timestamp}Monitoreo en tiempo real activado\n")
                self.data_display.see("end")
                
            except serial.SerialException as e:
                self.data_display.insert("end", f"Error: {str(e)}\n")
                self.data_display.see("end")
        else:
            self.disconnect()
            
    def disconnect(self):
        """Desconectar puerto serial"""
        self.is_running = False
        if self.serial_port:
            self.serial_port.close()
        self.connect_btn.configure(text="Conectar")
        self.status_label.configure(text="🔴 Desconectado")
        
        timestamp = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
        self.data_display.insert("end", f"{timestamp}Sistema desconectado\n")
        self.data_display.see("end")
        
    def read_serial(self):
        """Lee datos del puerto serial"""
        while self.is_running:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.readline()
                    try:
                        decoded = data.decode().strip()
                        timestamp = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
                        
                        # Procesar líneas que comienzan con "DATA:"
                        if decoded.startswith("DATA:"):
                            csv_data = decoded[5:].strip()  # Remover "DATA:" del inicio
                            if self.parse_gps_gy91_data(csv_data):
                                # Actualizar displays con throttling
                                self.root.after_idle(self.update_all_displays)
                                
                                # Actualizar contador menos frecuentemente
                                if self.data_count % 10 == 0:
                                    self.root.after_idle(lambda: self.data_count_label.configure(text=f"Muestras: {self.data_count}"))
                                
                                # Log cada 100 muestras
                                if self.data_count % 100 == 0:
                                    self.data_display.insert("end", f"{timestamp}📊 Sistema actualizado - Muestra {self.data_count}\n")
                                    self.data_display.see("end")
                                    
                                    # Limpiar buffer del textbox si es muy grande
                                    if int(self.data_display.index("end-1c").split('.')[0]) > 500:
                                        self.data_display.delete("1.0", "250.0")
                        
                        # Procesar mensajes de estado
                        elif decoded.startswith("STATUS:"):
                            status_msg = decoded[7:].strip()
                            self.data_display.insert("end", f"{timestamp}ℹ️ {status_msg}\n")
                            self.data_display.see("end")
                        
                        # Otros mensajes
                        else:
                            if self.data_count % 50 == 0:  # Solo mostrar ocasionalmente
                                self.data_display.insert("end", f"{timestamp}Raw: {decoded}\n")
                                self.data_display.see("end")
                        
                    except UnicodeDecodeError:
                        pass
                else:
                    time.sleep(0.01)
                    
            except serial.SerialException:
                self.data_display.insert("end", "Error de conexión serial\n")
                self.disconnect()
                break

    def clear_display(self):
        """Limpia el monitor de datos"""
        self.data_display.delete("0.0", "end")

if __name__ == "__main__":
    app = GPSGy91Monitor()
    app.root.protocol("WM_DELETE_WINDOW", app.root.quit)
    app.root.mainloop()