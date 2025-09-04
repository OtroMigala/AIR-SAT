# core/config.py
"""
Configuraciones centralizadas del sistema GPS + GY91
Mantiene todas las configuraciones sin cambiar funcionalidad
"""

# Configuración de la ventana principal
WINDOW_CONFIG = {
    'title': "Sistema GPS + GY91 - Monitor de Navegación | GPS + BMP280 + MPU9250",
    'geometry': "1600x1000"
}

# Configuración de datos y buffers
DATA_CONFIG = {
    'max_data_points': 500,
    'max_track_points': 1000,
    'ui_update_interval': 0.1,  # 100ms máximo
    'plot_update_interval': 10,
    'plot_animation_interval': 2000  # ms
}

# Configuración de puerto serial
SERIAL_CONFIG = {
    'default_baud': "115200",
    'available_bauds': ["9600", "115200"],
    'timeout': 0.1
}

# Configuración del mapa GPS
MAP_CONFIG = {
    'colors': {
        "background": "#1a1a1a",
        "grid": "#333333", 
        "track": "#00ff00",
        "current": "#ff4444",
        "precision_circle": "#ffaa00",
        "waypoint": "#00aaff",
        "text": "#ffffff"
    },
    'default_zoom_scale': 20,  # metros
    'zoom_presets': [100, 50, 20, 10, 5, 2],  # metros
    'default_opacity': 0.8
}

# Configuración de matplotlib
PLOT_CONFIG = {
    'style': 'fast',
    'rcParams': {
        'font.size': 8,
        'figure.facecolor': '#212121',
        'axes.facecolor': '#2b2b2b',
        'text.color': 'white',
        'axes.labelcolor': 'white',
        'xtick.color': 'white',
        'ytick.color': 'white'
    },
    'figure_size': (12, 8),
    'titles': [
        "GPS - Latitud/Longitud", "GPS - Altitud/Velocidad", "BMP280 - Temp/Presión",
        "Acelerómetro (g)", "Giroscopio (dps)", "Magnetómetro (µT)",
        "Orientación (°)", "Rumbo/Heading (°)", "Altitudes GPS vs BMP280"
    ]
}

# Configuración de texto y etiquetas
LABELS = {
    'tabs': {
        'realtime': "📊 Monitor Tiempo Real",
        'plots': "📈 Gráficas Tiempo Real", 
        'map': "🗺️ Mapa GPS"
    },
    'status': {
        'disconnected': "🔴 Desconectado",
        'connected': "🟢 Conectado a {}",
        'no_data': "No hay datos",
        'no_ports': "No hay puertos"
    },
    'gps_fix': {
        0: "No Fix",
        1: "2D Fix", 
        2: "3D Fix"
    }
}

# Configuración de formatos de archivo
FILE_FORMATS = {
    'image_types': [
        ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
        ("PNG", "*.png"),
        ("JPEG", "*.jpg *.jpeg"),
        ("Todos", "*.*")
    ],
    'export_types': [
        ("GPX", "*.gpx"),
        ("CSV", "*.csv"), 
        ("KML", "*.kml"),
        ("Texto", "*.txt")
    ]
}

# Configuración de precisión GPS
GPS_PRECISION = {
    'base_error_meters': 3.0,  # Error base para HDOP = 1
    'excellent_hdop': 2.0,
    'good_hdop': 5.0,
    'excellent_satellites': 8,
    'good_satellites': 4,
    'accel_tolerance': (0.95, 1.05)  # Rango normal de aceleración
}

# Configuración de colores para calidad de datos
QUALITY_COLORS = {
    'excellent': "#00aa00",
    'good': "#ffaa00", 
    'poor': "#ff4444",
    'neutral': "#888888"
}

# Configuración de la grilla del mapa
GRID_CONFIG = {
    'spacing_rules': [
        (0.1, 1.0),    # zoom muy alto: 1 metro
        (0.5, 5.0),    # zoom alto: 5 metros
        (1.0, 10.0),   # zoom medio: 10 metros
        (5.0, 50.0),   # zoom bajo: 50 metros
        (float('inf'), 100.0)  # zoom muy bajo: 100 metros
    ]
}

# Configuración de exportación
EXPORT_CONFIG = {
    'gpx_creator': "Sistema GPS + GY91",
    'track_name': "Satélite Track",
    'coordinate_precision': 8,  # decimales
    'time_format': '%Y-%m-%dT%H:%M:%SZ'
}

# Configuración de calibración de imagen
IMAGE_CALIBRATION = {
    'default_radius_meters': 500.0,
    'estimation_radius_meters': 200.0,
    'lat_degree_meters': 111000,  # metros por grado de latitud
    'dialog_size': "450x350"
}

# Configuración de threading
THREADING_CONFIG = {
    'serial_sleep_interval': 0.01,  # segundos
    'ui_after_idle': True,  # usar after_idle para UI updates
    'daemon_threads': True
}

# Configuración de logging y debug
DEBUG_CONFIG = {
    'log_every_n_samples': 100,
    'show_raw_every_n': 50,
    'max_textbox_lines': 500,
    'clear_at_lines': 250
}