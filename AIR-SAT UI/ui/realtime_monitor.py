# ui/realtime_monitor.py
"""
Monitor de tiempo real para el sistema GPS + GY91
Mantiene exactamente la misma interfaz y funcionalidad del código original
"""

import customtkinter as ctk
from core.config import QUALITY_COLORS, GPS_PRECISION, DEBUG_CONFIG

class RealtimeMonitor:
    """
    Monitor de datos en tiempo real
    MANTIENE LA INTERFAZ EXACTA DEL CÓDIGO ORIGINAL
    """
    
    def __init__(self, parent_frame, data_manager):
        self.parent = parent_frame
        self.data_manager = data_manager
        
        # Referencias a elementos UI (se mantienen los mismos nombres)
        self.ui_elements = {}
        
        # Configurar la interfaz
        self.setup_realtime_interface()
    
    def setup_realtime_interface(self):
        """
        Configura la interfaz de monitor en tiempo real
        Ahora incluye nuevos sensores en formato de pestañas
        """
        # Crear notebook para organizar los sensores en pestañas
        self.notebook = ctk.CTkTabview(self.parent)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # === PESTAÑA 1: SENSORES BÁSICOS (GPS + GY91) ===
        self.tab_basic = self.notebook.add("🛰️ GPS + GY91")
        self.setup_basic_sensors_tab()
        
        # === PESTAÑA 2: CALIDAD DEL AIRE ===
        self.tab_air = self.notebook.add("🌬️ Calidad Aire")
        self.setup_air_quality_tab()
        
        # === PESTAÑA 3: COMUNICACIÓN ===
        self.tab_comm = self.notebook.add("📡 Comunicación")
        self.setup_communication_tab()
        
        # Frame inferior con monitor y estado
        self.setup_bottom_frame()
    
    def setup_basic_sensors_tab(self):
        """Configura la pestaña de sensores básicos (GPS + GY91)"""
        # Frame principal de datos con 3 columnas
        sensors_frame = ctk.CTkFrame(self.tab_basic)
        sensors_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # === COLUMNA 1: GPS ===
        self.setup_gps_column(sensors_frame)
        
        # === COLUMNA 2: BMP280 ===  
        self.setup_bmp280_column(sensors_frame)
        
        # === COLUMNA 3: MPU9250 ===
        self.setup_mpu9250_column(sensors_frame)
    
    def setup_air_quality_tab(self):
        """Configura la pestaña de calidad del aire"""
        air_frame = ctk.CTkFrame(self.tab_air)
        air_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # === COLUMNA 1: SPS30 (Partículas) ===
        self.setup_sps30_column(air_frame)
        
        # === COLUMNA 2: MQ135 (Gases) ===
        self.setup_mq135_column(air_frame)
        
        # === COLUMNA 3: MH-Z19 (CO₂) ===
        self.setup_mhz19_column(air_frame)
    
    def setup_communication_tab(self):
        """Configura la pestaña de comunicación"""
        comm_frame = ctk.CTkFrame(self.tab_comm)
        comm_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # === INFORMACIÓN LORA ===
        self.setup_lora_column(comm_frame)
        
        # === ESTADO DE SENSORES ===
        self.setup_sensor_status_column(comm_frame)
    
    def setup_gps_column(self, parent):
        """Configura columna GPS - EXACTAMENTE IGUAL AL ORIGINAL"""
        gps_frame = ctk.CTkFrame(parent)
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
        self.ui_elements['lat_label'] = ctk.CTkLabel(lat_frame, text="0.000000°",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    text_color="#ff6600")
        self.ui_elements['lat_label'].pack(side="right", padx=5)
        
        # Longitud
        lon_frame = ctk.CTkFrame(gps_frame)
        lon_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(lon_frame, text="Longitud:", width=80).pack(side="left", padx=5)
        self.ui_elements['lon_label'] = ctk.CTkLabel(lon_frame, text="0.000000°",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    text_color="#ff6600")
        self.ui_elements['lon_label'].pack(side="right", padx=5)
        
        # Altitud GPS
        gps_alt_frame = ctk.CTkFrame(gps_frame)
        gps_alt_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(gps_alt_frame, text="🏔️ Alt GPS:", width=80).pack(side="left", padx=5)
        self.ui_elements['gps_alt_label'] = ctk.CTkLabel(gps_alt_frame, text="0.0 m",
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        text_color="#aa00ff")
        self.ui_elements['gps_alt_label'].pack(side="right", padx=5)
        
        # Velocidad
        speed_frame = ctk.CTkFrame(gps_frame)
        speed_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(speed_frame, text="🚀 Velocidad:", width=80).pack(side="left", padx=5)
        self.ui_elements['speed_label'] = ctk.CTkLabel(speed_frame, text="0.0 km/h",
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      text_color="#0066ff")
        self.ui_elements['speed_label'].pack(side="right", padx=5)
        
        # Estado GPS
        gps_status_title = ctk.CTkLabel(gps_frame, text="🔧 ESTADO GPS",
                                      font=ctk.CTkFont(size=12, weight="bold"))
        gps_status_title.pack(pady=(10, 2))
        
        # Satélites
        sat_frame = ctk.CTkFrame(gps_frame)
        sat_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(sat_frame, text="Satélites:", width=80).pack(side="left", padx=5)
        self.ui_elements['sat_label'] = ctk.CTkLabel(sat_frame, text="0",
                                    font=ctk.CTkFont(size=12, weight="bold"))
        self.ui_elements['sat_label'].pack(side="right", padx=5)
        
        # Calidad Fix
        fix_frame = ctk.CTkFrame(gps_frame)
        fix_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(fix_frame, text="Fix:", width=80).pack(side="left", padx=5)
        self.ui_elements['fix_label'] = ctk.CTkLabel(fix_frame, text="0",
                                    font=ctk.CTkFont(size=12, weight="bold"))
        self.ui_elements['fix_label'].pack(side="right", padx=5)
        
        # HDOP/VDOP
        dop_frame = ctk.CTkFrame(gps_frame)
        dop_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(dop_frame, text="HDOP/VDOP:", width=80).pack(side="left", padx=5)
        self.ui_elements['dop_label'] = ctk.CTkLabel(dop_frame, text="0.0 / 0.0",
                                    font=ctk.CTkFont(size=11, weight="bold"))
        self.ui_elements['dop_label'].pack(side="right", padx=5)
        
        # Tiempo UTC
        utc_frame = ctk.CTkFrame(gps_frame)
        utc_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(utc_frame, text="UTC:", width=80).pack(side="left", padx=5)
        self.ui_elements['utc_label'] = ctk.CTkLabel(utc_frame, text="--:--:--",
                                    font=ctk.CTkFont(size=12, weight="bold"),
                                    text_color="#00dd00")
        self.ui_elements['utc_label'].pack(side="right", padx=5)
        
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
    
    def setup_bmp280_column(self, parent):
        """Configura columna BMP280 - EXACTAMENTE IGUAL AL ORIGINAL"""
        bmp_frame = ctk.CTkFrame(parent)
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
        self.ui_elements['bmp_temp_label'] = ctk.CTkLabel(bmp_temp_frame, text="0.00 °C",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         text_color="#ff6600")
        self.ui_elements['bmp_temp_label'].pack(side="right", padx=5)
        
        # Presión BMP280
        bmp_pres_frame = ctk.CTkFrame(bmp_frame)
        bmp_pres_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(bmp_pres_frame, text="📏 Presión:", width=100).pack(side="left", padx=5)
        self.ui_elements['bmp_pres_label'] = ctk.CTkLabel(bmp_pres_frame, text="0.00 mbar",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         text_color="#0066ff")
        self.ui_elements['bmp_pres_label'].pack(side="right", padx=5)
        
        # Altitud BMP280
        bmp_alt_frame = ctk.CTkFrame(bmp_frame)
        bmp_alt_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(bmp_alt_frame, text="🏔️ Alt Baro:", width=100).pack(side="left", padx=5)
        self.ui_elements['bmp_alt_label'] = ctk.CTkLabel(bmp_alt_frame, text="0.0 m",
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        text_color="#aa00ff")
        self.ui_elements['bmp_alt_label'].pack(side="right", padx=5)
        
        # Diferencia de Altitudes
        alt_comp_title = ctk.CTkLabel(bmp_frame, text="📏 COMPARACIÓN ALTITUD",
                                    font=ctk.CTkFont(size=12, weight="bold"))
        alt_comp_title.pack(pady=(10, 2))
        
        diff_alt_frame = ctk.CTkFrame(bmp_frame)
        diff_alt_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(diff_alt_frame, text="ΔH (GPS-Baro):", width=100).pack(side="left", padx=5)
        self.ui_elements['diff_alt_label'] = ctk.CTkLabel(diff_alt_frame, text="0.0 m",
                                         font=ctk.CTkFont(size=14, weight="bold"))
        self.ui_elements['diff_alt_label'].pack(side="right", padx=5)
        
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
    
    def setup_mpu9250_column(self, parent):
        """Configura columna MPU9250 - EXACTAMENTE IGUAL AL ORIGINAL"""
        mpu_frame = ctk.CTkFrame(parent)
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
        self.ui_elements['mpu_temp_label'] = ctk.CTkLabel(mpu_temp_frame, text="0.0 °C",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         text_color="#ff6600")
        self.ui_elements['mpu_temp_label'].pack(side="right", padx=5)
        
        # Acelerómetro
        accel_title = ctk.CTkLabel(mpu_frame, text="🎯 ACELERÓMETRO",
                                 font=ctk.CTkFont(size=12, weight="bold"))
        accel_title.pack(pady=(5, 2))
        
        accel_xyz_frame = ctk.CTkFrame(mpu_frame)
        accel_xyz_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(accel_xyz_frame, text="X,Y,Z:", width=50).pack(side="left", padx=5)
        self.ui_elements['accel_label'] = ctk.CTkLabel(accel_xyz_frame, text="0.000, 0.000, 0.000 g",
                                      font=ctk.CTkFont(size=11, weight="bold"),
                                      text_color="#ff8800")
        self.ui_elements['accel_label'].pack(side="right", padx=5)
        
        accel_total_frame = ctk.CTkFrame(mpu_frame)
        accel_total_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(accel_total_frame, text="|A|:", width=50).pack(side="left", padx=5)
        self.ui_elements['accel_total_label'] = ctk.CTkLabel(accel_total_frame, text="0.000 g",
                                            font=ctk.CTkFont(size=12, weight="bold"),
                                            text_color="#ff4400")
        self.ui_elements['accel_total_label'].pack(side="right", padx=5)
        
        # Giroscopio
        gyro_title = ctk.CTkLabel(mpu_frame, text="🌀 GIROSCOPIO",
                                font=ctk.CTkFont(size=12, weight="bold"))
        gyro_title.pack(pady=(5, 2))
        
        gyro_xyz_frame = ctk.CTkFrame(mpu_frame)
        gyro_xyz_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(gyro_xyz_frame, text="X,Y,Z:", width=50).pack(side="left", padx=5)
        self.ui_elements['gyro_label'] = ctk.CTkLabel(gyro_xyz_frame, text="0.00, 0.00, 0.00 dps",
                                     font=ctk.CTkFont(size=11, weight="bold"),
                                     text_color="#0088ff")
        self.ui_elements['gyro_label'].pack(side="right", padx=5)
        
        gyro_total_frame = ctk.CTkFrame(mpu_frame)
        gyro_total_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(gyro_total_frame, text="|G|:", width=50).pack(side="left", padx=5)
        self.ui_elements['gyro_total_label'] = ctk.CTkLabel(gyro_total_frame, text="0.00 dps",
                                           font=ctk.CTkFont(size=12, weight="bold"),
                                           text_color="#0066dd")
        self.ui_elements['gyro_total_label'].pack(side="right", padx=5)
        
        # Magnetómetro
        mag_title = ctk.CTkLabel(mpu_frame, text="🧲 MAGNETÓMETRO",
                               font=ctk.CTkFont(size=12, weight="bold"))
        mag_title.pack(pady=(5, 2))
        
        mag_xyz_frame = ctk.CTkFrame(mpu_frame)
        mag_xyz_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(mag_xyz_frame, text="X,Y,Z:", width=50).pack(side="left", padx=5)
        self.ui_elements['mag_label'] = ctk.CTkLabel(mag_xyz_frame, text="0.0, 0.0, 0.0 µT",
                                    font=ctk.CTkFont(size=11, weight="bold"),
                                    text_color="#aa00ff")
        self.ui_elements['mag_label'].pack(side="right", padx=5)
        
        # Orientación
        orient_title = ctk.CTkLabel(mpu_frame, text="📐 ORIENTACIÓN",
                                  font=ctk.CTkFont(size=12, weight="bold"))
        orient_title.pack(pady=(5, 2))
        
        # Roll, Pitch, Yaw
        rpy_frame = ctk.CTkFrame(mpu_frame)
        rpy_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(rpy_frame, text="R,P,Y:", width=50).pack(side="left", padx=5)
        self.ui_elements['rpy_label'] = ctk.CTkLabel(rpy_frame, text="0.0°, 0.0°, 0.0°",
                                    font=ctk.CTkFont(size=11, weight="bold"),
                                    text_color="#00aa44")
        self.ui_elements['rpy_label'].pack(side="right", padx=5)
        
        # Heading
        heading_frame = ctk.CTkFrame(mpu_frame)
        heading_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(heading_frame, text="Rumbo:", width=50).pack(side="left", padx=5)
        self.ui_elements['heading_label'] = ctk.CTkLabel(heading_frame, text="0.0° (N)",
                                        font=ctk.CTkFont(size=12, weight="bold"),
                                        text_color="#00dd00")
        self.ui_elements['heading_label'].pack(side="right", padx=5)
    
    def setup_bottom_frame(self):
        """Configura frame inferior - EXACTAMENTE IGUAL AL ORIGINAL"""
        bottom_frame = ctk.CTkFrame(self.parent)
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Monitor de datos
        monitor_frame = ctk.CTkFrame(bottom_frame)
        monitor_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        monitor_title = ctk.CTkLabel(monitor_frame, text="📄 Monitor de Datos",
                                   font=ctk.CTkFont(size=14, weight="bold"))
        monitor_title.pack(pady=5)
        
        self.ui_elements['data_display'] = ctk.CTkTextbox(monitor_frame, height=120)
        self.ui_elements['data_display'].pack(fill="both", expand=True, padx=5, pady=5)
        
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
        self.ui_elements['last_update_label'] = ctk.CTkLabel(update_frame, text="No hay datos",
                                            font=ctk.CTkFont(size=10),
                                            text_color="#888888")
        self.ui_elements['last_update_label'].pack()
        
        # Calidad de datos
        quality_frame = ctk.CTkFrame(status_frame)
        quality_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(quality_frame, text="📊 Calidad de datos:",
                   font=ctk.CTkFont(size=10)).pack()
        self.ui_elements['quality_label'] = ctk.CTkLabel(quality_frame, text="N/A",
                                        font=ctk.CTkFont(size=10, weight="bold"))
        self.ui_elements['quality_label'].pack()
        
        # Botones de control
        ctk.CTkButton(status_frame, text="Limpiar Monitor",
                    command=self.clear_display).pack(pady=5)
    
    def update_displays(self):
        """
        Actualiza todos los displays con datos actuales
        Incluye sensores originales + nuevos sensores
        """
        data = self.data_manager.sensor_data
        
        # ===== SENSORES BÁSICOS (GPS + GY91) =====
        
        # GPS - EXACTAMENTE IGUAL AL ORIGINAL
        if 'lat_label' in self.ui_elements:
            self.ui_elements['lat_label'].configure(text=f"{data['latitude']:.6f}° {data['lat_dir']}")
            self.ui_elements['lon_label'].configure(text=f"{data['longitude']:.6f}° {data['lon_dir']}")
            self.ui_elements['gps_alt_label'].configure(text=f"{data['gps_altitude']:.1f} m")
            self.ui_elements['speed_label'].configure(text=f"{data['speed']:.1f} km/h")
            
            # Estado GPS con colores
            sat_count = data['satellites']
            sat_color = QUALITY_COLORS['excellent'] if sat_count >= GPS_PRECISION['excellent_satellites'] else QUALITY_COLORS['good'] if sat_count >= GPS_PRECISION['good_satellites'] else QUALITY_COLORS['poor']
            self.ui_elements['sat_label'].configure(text=str(sat_count), text_color=sat_color)
            
            fix_quality = data['fix_quality']
            fix_color = QUALITY_COLORS['excellent'] if fix_quality >= 2 else QUALITY_COLORS['good'] if fix_quality == 1 else QUALITY_COLORS['poor']
            fix_text = "3D Fix" if fix_quality >= 2 else "2D Fix" if fix_quality == 1 else "No Fix"
            self.ui_elements['fix_label'].configure(text=fix_text, text_color=fix_color)
            
            self.ui_elements['dop_label'].configure(text=f"{data['hdop']:.1f} / {data['vdop']:.1f}")
            self.ui_elements['utc_label'].configure(text=data['utc_time'])
        
        # BMP280 - EXACTAMENTE IGUAL AL ORIGINAL
        if 'bmp_temp_label' in self.ui_elements:
            self.ui_elements['bmp_temp_label'].configure(text=f"{data['bmp_temp']:.2f} °C")
            self.ui_elements['bmp_pres_label'].configure(text=f"{data['pressure']:.2f} mbar")
            self.ui_elements['bmp_alt_label'].configure(text=f"{data['bmp_altitude']:.1f} m")
            
            # Diferencia de altitudes
            alt_diff = abs(data['altitude_diff'])
            alt_color = QUALITY_COLORS['excellent'] if alt_diff < 5.0 else QUALITY_COLORS['good'] if alt_diff < 15.0 else QUALITY_COLORS['poor']
            self.ui_elements['diff_alt_label'].configure(text=f"{data['altitude_diff']:.1f} m", text_color=alt_color)
        
        # MPU9250 - EXACTAMENTE IGUAL AL ORIGINAL
        if 'mpu_temp_label' in self.ui_elements:
            self.ui_elements['mpu_temp_label'].configure(text=f"{data['mpu_temp']:.1f} °C")
            self.ui_elements['accel_label'].configure(text=f"{data['accel_x']:.3f}, {data['accel_y']:.3f}, {data['accel_z']:.3f} g")
            self.ui_elements['accel_total_label'].configure(text=f"{data['total_accel']:.3f} g")
            self.ui_elements['gyro_label'].configure(text=f"{data['gyro_x']:.2f}, {data['gyro_y']:.2f}, {data['gyro_z']:.2f} dps")
            self.ui_elements['gyro_total_label'].configure(text=f"{data['total_gyro']:.2f} dps")
            self.ui_elements['mag_label'].configure(text=f"{data['mag_x']:.1f}, {data['mag_y']:.1f}, {data['mag_z']:.1f} µT")
            self.ui_elements['rpy_label'].configure(text=f"{data['roll']:.1f}°, {data['pitch']:.1f}°, {data['yaw']:.1f}°")
            
            # Heading con dirección cardinal
            cardinal = self.data_manager.get_cardinal_direction(data['heading'])
            self.ui_elements['heading_label'].configure(text=f"{data['heading']:.1f}° ({cardinal})")
        
        # ===== NUEVOS SENSORES =====
        
        # SPS30 (Partículas)
        if 'pm1_label' in self.ui_elements:
            self.ui_elements['pm1_label'].configure(text=f"{data['pm1_0']:.1f} µg/m³")
            self.ui_elements['pm25_label'].configure(text=f"{data['pm2_5']:.1f} µg/m³")
            self.ui_elements['pm10_label'].configure(text=f"{data['pm10']:.1f} µg/m³")
            self.ui_elements['nc05_label'].configure(text=f"{data['nc0_5']:.1f} #/cm³")
            self.ui_elements['nc25_label'].configure(text=f"{data['nc2_5']:.1f} #/cm³")
            self.ui_elements['particle_size_label'].configure(text=f"{data['typical_particle_size']:.2f} µm")
        
        # MQ135 (Gases)
        if 'co_label' in self.ui_elements:
            self.ui_elements['co_label'].configure(text=f"{data['co_ppm']:.1f} ppm")
            self.ui_elements['co2_mq_label'].configure(text=f"{data['co2_ppm_mq135']:.1f} ppm")
            self.ui_elements['nh4_label'].configure(text=f"{data['nh4_ppm']:.1f} ppm")
            self.ui_elements['lpg_label'].configure(text=f"{data['lpg_ppm']:.1f} ppm")
            self.ui_elements['smoke_label'].configure(text=f"{data['smoke_ppm']:.1f} ppm")
            self.ui_elements['alcohol_label'].configure(text=f"{data['alcohol_ppm']:.1f} ppm")
        
        # MH-Z19 (CO₂)
        if 'co2_mhz_label' in self.ui_elements:
            self.ui_elements['co2_mhz_label'].configure(text=f"{data['co2_ppm_mhz19']} ppm")
            self.ui_elements['temp_mhz_label'].configure(text=f"{data['mhz19_temp']:.1f} °C")
            
            # Estado del sensor con colores
            status = data['mhz19_status']
            status_color = QUALITY_COLORS['excellent'] if status == 'R' else QUALITY_COLORS['good'] if status == 'W' else QUALITY_COLORS['poor']
            status_text = "Ready" if status == 'R' else "Warming" if status == 'W' else "Error"
            self.ui_elements['status_mhz_label'].configure(text=status_text, text_color=status_color)
            
            # Sensor calentado
            warmed_color = QUALITY_COLORS['excellent'] if data['mhz19_warmed'] else QUALITY_COLORS['poor']
            warmed_text = "Sí" if data['mhz19_warmed'] else "No"
            self.ui_elements['warmed_label'].configure(text=warmed_text, text_color=warmed_color)
            
            self.ui_elements['range_label'].configure(text=f"0-{data['co2_range']} ppm")
        
        # ===== COMUNICACIÓN LORA =====
        
        if 'rssi_label' in self.ui_elements:
            # RSSI con colores según calidad de señal
            rssi = data['lora_rssi']
            rssi_color = QUALITY_COLORS['excellent'] if rssi > -70 else QUALITY_COLORS['good'] if rssi > -85 else QUALITY_COLORS['poor']
            self.ui_elements['rssi_label'].configure(text=f"{rssi} dBm", text_color=rssi_color)
            
            # SNR
            snr = data['lora_snr']
            snr_color = QUALITY_COLORS['excellent'] if snr > 5 else QUALITY_COLORS['good'] if snr > 0 else QUALITY_COLORS['poor']
            self.ui_elements['snr_label'].configure(text=f"{snr:.1f} dB", text_color=snr_color)
            
            self.ui_elements['packet_type_label'].configure(text=data['last_packet_type'])
            self.ui_elements['seq_id_label'].configure(text=str(data['sequence_id']))
            self.ui_elements['sys_time_label'].configure(text=f"{data['system_timestamp']} ms")
        
        # ===== ESTADO DE SENSORES =====
        
        if 'gps_status' in self.ui_elements:
            # Decodificar máscara de sensores
            sensors_status = self.data_manager.decode_sensor_status_mask(data['sensor_status_mask'])
            
            for sensor, status in sensors_status.items():
                status_key = f'{sensor.lower()}_status'
                if status_key in self.ui_elements:
                    color = QUALITY_COLORS['excellent'] if status else QUALITY_COLORS['poor']
                    self.ui_elements[status_key].configure(text="●", text_color=color)
        
        # ===== CALIDAD DEL AIRE =====
        
        if 'air_quality_label' in self.ui_elements:
            air_quality, air_color = self.data_manager.get_air_quality_index()
            self.ui_elements['air_quality_label'].configure(text=air_quality, text_color=air_color)
        
        # ===== ESTADO DEL SISTEMA =====
        
        if 'last_update_label' in self.ui_elements:
            self.ui_elements['last_update_label'].configure(text=data['last_update'])
            
            # Calidad de datos
            quality_text, quality_color = self.data_manager.get_data_quality()
            self.ui_elements['quality_label'].configure(text=quality_text, text_color=quality_color)
    
    def add_status_message(self, message):
        """
        Añade mensaje al monitor de datos
        MANTIENE LA LÓGICA EXACTA DEL ORIGINAL
        """
        self.ui_elements['data_display'].insert("end", f"{message}\n")
        self.ui_elements['data_display'].see("end")
        
        # Limpiar buffer si es muy grande - EXACTAMENTE IGUAL AL ORIGINAL
        lines = int(self.ui_elements['data_display'].index("end-1c").split('.')[0])
        if lines > DEBUG_CONFIG['max_textbox_lines']:
            self.ui_elements['data_display'].delete("1.0", f"{DEBUG_CONFIG['clear_at_lines']}.0")
    
    def clear_display(self):
        """Limpia el monitor de datos - EXACTAMENTE IGUAL AL ORIGINAL"""
        self.ui_elements['data_display'].delete("0.0", "end")
    
    # ===== NUEVOS MÉTODOS PARA SENSORES ADICIONALES =====
    
    def setup_sps30_column(self, parent):
        """Configura columna SPS30 (Sensor de Partículas)"""
        sps_frame = ctk.CTkFrame(parent)
        sps_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        sps_title = ctk.CTkLabel(sps_frame, 
                               text="💨 SPS30 - PARTÍCULAS",
                               font=ctk.CTkFont(size=16, weight="bold"),
                               text_color="#8B4513")
        sps_title.pack(pady=5)
        
        # Concentraciones de masa (µg/m³)
        mass_title = ctk.CTkLabel(sps_frame, text="⚖️ CONCENTRACIÓN MASA",
                                font=ctk.CTkFont(size=12, weight="bold"))
        mass_title.pack(pady=(5, 2))
        
        # PM1.0
        pm1_frame = ctk.CTkFrame(sps_frame)
        pm1_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(pm1_frame, text="PM1.0:", width=70).pack(side="left", padx=5)
        self.ui_elements['pm1_label'] = ctk.CTkLabel(pm1_frame, text="0.0 µg/m³",
                                    font=ctk.CTkFont(size=12, weight="bold"),
                                    text_color="#654321")
        self.ui_elements['pm1_label'].pack(side="right", padx=5)
        
        # PM2.5
        pm25_frame = ctk.CTkFrame(sps_frame)
        pm25_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(pm25_frame, text="PM2.5:", width=70).pack(side="left", padx=5)
        self.ui_elements['pm25_label'] = ctk.CTkLabel(pm25_frame, text="0.0 µg/m³",
                                     font=ctk.CTkFont(size=12, weight="bold"),
                                     text_color="#8B4513")
        self.ui_elements['pm25_label'].pack(side="right", padx=5)
        
        # PM10
        pm10_frame = ctk.CTkFrame(sps_frame)
        pm10_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(pm10_frame, text="PM10:", width=70).pack(side="left", padx=5)
        self.ui_elements['pm10_label'] = ctk.CTkLabel(pm10_frame, text="0.0 µg/m³",
                                     font=ctk.CTkFont(size=12, weight="bold"),
                                     text_color="#A0522D")
        self.ui_elements['pm10_label'].pack(side="right", padx=5)
        
        # Concentraciones numéricas
        num_title = ctk.CTkLabel(sps_frame, text="🔢 CONCENTRACIÓN NUMÉRICA",
                               font=ctk.CTkFont(size=12, weight="bold"))
        num_title.pack(pady=(10, 2))
        
        # NC0.5
        nc05_frame = ctk.CTkFrame(sps_frame)
        nc05_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(nc05_frame, text="NC0.5:", width=70).pack(side="left", padx=5)
        self.ui_elements['nc05_label'] = ctk.CTkLabel(nc05_frame, text="0.0 #/cm³",
                                     font=ctk.CTkFont(size=11))
        self.ui_elements['nc05_label'].pack(side="right", padx=5)
        
        # NC2.5
        nc25_frame = ctk.CTkFrame(sps_frame)
        nc25_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(nc25_frame, text="NC2.5:", width=70).pack(side="left", padx=5)
        self.ui_elements['nc25_label'] = ctk.CTkLabel(nc25_frame, text="0.0 #/cm³",
                                     font=ctk.CTkFont(size=11))
        self.ui_elements['nc25_label'].pack(side="right", padx=5)
        
        # Tamaño típico
        size_frame = ctk.CTkFrame(sps_frame)
        size_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(size_frame, text="Tamaño típico:", width=70).pack(side="left", padx=5)
        self.ui_elements['particle_size_label'] = ctk.CTkLabel(size_frame, text="0.0 µm",
                                                              font=ctk.CTkFont(size=11, weight="bold"),
                                                              text_color="#8B4513")
        self.ui_elements['particle_size_label'].pack(side="right", padx=5)
    
    def setup_mq135_column(self, parent):
        """Configura columna MQ135 (Calidad del Aire)"""
        mq_frame = ctk.CTkFrame(parent)
        mq_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        mq_title = ctk.CTkLabel(mq_frame, 
                              text="🌫️ MQ135 - GASES",
                              font=ctk.CTkFont(size=16, weight="bold"),
                              text_color="#4B0082")
        mq_title.pack(pady=5)
        
        # Gases principales
        main_gases_title = ctk.CTkLabel(mq_frame, text="🚨 GASES PRINCIPALES",
                                      font=ctk.CTkFont(size=12, weight="bold"))
        main_gases_title.pack(pady=(5, 2))
        
        # CO
        co_frame = ctk.CTkFrame(mq_frame)
        co_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(co_frame, text="CO:", width=70).pack(side="left", padx=5)
        self.ui_elements['co_label'] = ctk.CTkLabel(co_frame, text="0.0 ppm",
                                   font=ctk.CTkFont(size=12, weight="bold"),
                                   text_color="#FF4500")
        self.ui_elements['co_label'].pack(side="right", padx=5)
        
        # CO₂ (MQ135)
        co2_mq_frame = ctk.CTkFrame(mq_frame)
        co2_mq_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(co2_mq_frame, text="CO₂:", width=70).pack(side="left", padx=5)
        self.ui_elements['co2_mq_label'] = ctk.CTkLabel(co2_mq_frame, text="0.0 ppm",
                                       font=ctk.CTkFont(size=12, weight="bold"),
                                       text_color="#8B0000")
        self.ui_elements['co2_mq_label'].pack(side="right", padx=5)
        
        # NH₄ (Amonio)
        nh4_frame = ctk.CTkFrame(mq_frame)
        nh4_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(nh4_frame, text="NH₄:", width=70).pack(side="left", padx=5)
        self.ui_elements['nh4_label'] = ctk.CTkLabel(nh4_frame, text="0.0 ppm",
                                    font=ctk.CTkFont(size=12, weight="bold"),
                                    text_color="#32CD32")
        self.ui_elements['nh4_label'].pack(side="right", padx=5)
        
        # Otros gases
        other_gases_title = ctk.CTkLabel(mq_frame, text="🔥 OTROS GASES",
                                       font=ctk.CTkFont(size=12, weight="bold"))
        other_gases_title.pack(pady=(10, 2))
        
        # LPG
        lpg_frame = ctk.CTkFrame(mq_frame)
        lpg_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(lpg_frame, text="LPG:", width=70).pack(side="left", padx=5)
        self.ui_elements['lpg_label'] = ctk.CTkLabel(lpg_frame, text="0.0 ppm",
                                    font=ctk.CTkFont(size=11))
        self.ui_elements['lpg_label'].pack(side="right", padx=5)
        
        # Humo
        smoke_frame = ctk.CTkFrame(mq_frame)
        smoke_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(smoke_frame, text="Humo:", width=70).pack(side="left", padx=5)
        self.ui_elements['smoke_label'] = ctk.CTkLabel(smoke_frame, text="0.0 ppm",
                                      font=ctk.CTkFont(size=11))
        self.ui_elements['smoke_label'].pack(side="right", padx=5)
        
        # Alcohol
        alcohol_frame = ctk.CTkFrame(mq_frame)
        alcohol_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(alcohol_frame, text="Alcohol:", width=70).pack(side="left", padx=5)
        self.ui_elements['alcohol_label'] = ctk.CTkLabel(alcohol_frame, text="0.0 ppm",
                                        font=ctk.CTkFont(size=11))
        self.ui_elements['alcohol_label'].pack(side="right", padx=5)
    
    def setup_mhz19_column(self, parent):
        """Configura columna MH-Z19 (CO₂ Preciso)"""
        mhz_frame = ctk.CTkFrame(parent)
        mhz_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        mhz_title = ctk.CTkLabel(mhz_frame, 
                               text="🏭 MH-Z19 - CO₂ NDIR",
                               font=ctk.CTkFont(size=16, weight="bold"),
                               text_color="#DC143C")
        mhz_title.pack(pady=5)
        
        # CO₂ Principal
        co2_frame = ctk.CTkFrame(mhz_frame)
        co2_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(co2_frame, text="💨 CO₂ (NDIR):", width=100).pack(side="top")
        self.ui_elements['co2_mhz_label'] = ctk.CTkLabel(co2_frame, text="0 ppm",
                                        font=ctk.CTkFont(size=18, weight="bold"),
                                        text_color="#DC143C")
        self.ui_elements['co2_mhz_label'].pack(side="top", pady=5)
        
        # Temperatura del sensor
        temp_mhz_frame = ctk.CTkFrame(mhz_frame)
        temp_mhz_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(temp_mhz_frame, text="🌡️ Temp Sensor:", width=100).pack(side="left", padx=5)
        self.ui_elements['temp_mhz_label'] = ctk.CTkLabel(temp_mhz_frame, text="0.0 °C",
                                         font=ctk.CTkFont(size=12, weight="bold"),
                                         text_color="#FF6600")
        self.ui_elements['temp_mhz_label'].pack(side="right", padx=5)
        
        # Estado del sensor
        status_mhz_frame = ctk.CTkFrame(mhz_frame)
        status_mhz_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(status_mhz_frame, text="🔧 Estado:", width=100).pack(side="left", padx=5)
        self.ui_elements['status_mhz_label'] = ctk.CTkLabel(status_mhz_frame, text="---",
                                           font=ctk.CTkFont(size=12, weight="bold"))
        self.ui_elements['status_mhz_label'].pack(side="right", padx=5)
        
        # Sensor calentado
        warmed_frame = ctk.CTkFrame(mhz_frame)
        warmed_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(warmed_frame, text="🔥 Calentado:", width=100).pack(side="left", padx=5)
        self.ui_elements['warmed_label'] = ctk.CTkLabel(warmed_frame, text="No",
                                      font=ctk.CTkFont(size=12, weight="bold"))
        self.ui_elements['warmed_label'].pack(side="right", padx=5)
        
        # Rango de medición
        range_frame = ctk.CTkFrame(mhz_frame)
        range_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(range_frame, text="📏 Rango:", width=100).pack(side="left", padx=5)
        self.ui_elements['range_label'] = ctk.CTkLabel(range_frame, text="0-5000 ppm",
                                      font=ctk.CTkFont(size=11))
        self.ui_elements['range_label'].pack(side="right", padx=5)
        
        # Especificaciones
        mhz_specs_frame = ctk.CTkFrame(mhz_frame)
        mhz_specs_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(mhz_specs_frame, text="📋 ESPECIFICACIONES",
                   font=ctk.CTkFont(size=12, weight="bold")).pack(pady=2)
        ctk.CTkLabel(mhz_specs_frame, text="• Precisión: ±(50ppm+5%)",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
        ctk.CTkLabel(mhz_specs_frame, text="• Resolución: 1 ppm",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
        ctk.CTkLabel(mhz_specs_frame, text="• Tiempo resp: <120s",
                   font=ctk.CTkFont(size=10)).pack(anchor="w", padx=5)
    
    def setup_lora_column(self, parent):
        """Configura columna información LoRa"""
        lora_frame = ctk.CTkFrame(parent)
        lora_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        lora_title = ctk.CTkLabel(lora_frame, 
                                text="📡 COMUNICACIÓN LORA",
                                font=ctk.CTkFont(size=16, weight="bold"),
                                text_color="#FF1493")
        lora_title.pack(pady=5)
        
        # RSSI
        rssi_frame = ctk.CTkFrame(lora_frame)
        rssi_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(rssi_frame, text="📶 RSSI:", width=100).pack(side="left", padx=5)
        self.ui_elements['rssi_label'] = ctk.CTkLabel(rssi_frame, text="0 dBm",
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     text_color="#FF1493")
        self.ui_elements['rssi_label'].pack(side="right", padx=5)
        
        # SNR
        snr_frame = ctk.CTkFrame(lora_frame)
        snr_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(snr_frame, text="📊 SNR:", width=100).pack(side="left", padx=5)
        self.ui_elements['snr_label'] = ctk.CTkLabel(snr_frame, text="0.0 dB",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    text_color="#FF69B4")
        self.ui_elements['snr_label'].pack(side="right", padx=5)
        
        # Último paquete
        packet_frame = ctk.CTkFrame(lora_frame)
        packet_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(packet_frame, text="📦 Último paquete:", width=100).pack(side="left", padx=5)
        self.ui_elements['packet_type_label'] = ctk.CTkLabel(packet_frame, text="---",
                                              font=ctk.CTkFont(size=12, weight="bold"),
                                              text_color="#FFB6C1")
        self.ui_elements['packet_type_label'].pack(side="right", padx=5)
        
        # Sequence ID
        seq_frame = ctk.CTkFrame(lora_frame)
        seq_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(seq_frame, text="🔢 Sequence ID:", width=100).pack(side="left", padx=5)
        self.ui_elements['seq_id_label'] = ctk.CTkLabel(seq_frame, text="0",
                                       font=ctk.CTkFont(size=12, weight="bold"))
        self.ui_elements['seq_id_label'].pack(side="right", padx=5)
        
        # Timestamp del sistema
        sys_time_frame = ctk.CTkFrame(lora_frame)
        sys_time_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(sys_time_frame, text="⏱️ Sys Time:", width=100).pack(side="left", padx=5)
        self.ui_elements['sys_time_label'] = ctk.CTkLabel(sys_time_frame, text="0 ms",
                                          font=ctk.CTkFont(size=11))
        self.ui_elements['sys_time_label'].pack(side="right", padx=5)
    
    def setup_sensor_status_column(self, parent):
        """Configura columna estado de sensores"""
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        status_title = ctk.CTkLabel(status_frame, 
                                  text="⚡ ESTADO SENSORES",
                                  font=ctk.CTkFont(size=16, weight="bold"),
                                  text_color="#32CD32")
        status_title.pack(pady=5)
        
        # Crear indicadores para cada sensor
        sensors = ['GPS', 'GY91', 'SPS30', 'MQ135', 'LORA', 'MHZ19']
        
        for sensor in sensors:
            sensor_frame = ctk.CTkFrame(status_frame)
            sensor_frame.pack(fill="x", padx=5, pady=2)
            
            ctk.CTkLabel(sensor_frame, text=f"{sensor}:", width=80).pack(side="left", padx=5)
            status_label = ctk.CTkLabel(sensor_frame, text="●",
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      text_color="#ff4444")
            status_label.pack(side="right", padx=5)
            self.ui_elements[f'{sensor.lower()}_status'] = status_label
        
        # Índice de calidad del aire
        air_quality_title = ctk.CTkLabel(status_frame, text="🌬️ CALIDAD AIRE",
                                       font=ctk.CTkFont(size=12, weight="bold"))
        air_quality_title.pack(pady=(10, 2))
        
        air_quality_frame = ctk.CTkFrame(status_frame)
        air_quality_frame.pack(fill="x", padx=5, pady=3)
        self.ui_elements['air_quality_label'] = ctk.CTkLabel(air_quality_frame, text="N/A",
                                            font=ctk.CTkFont(size=14, weight="bold"))
        self.ui_elements['air_quality_label'].pack(pady=5)
    
    def setup_bottom_frame(self):
        """Configura frame inferior fuera del sistema de pestañas"""
        bottom_frame = ctk.CTkFrame(self.parent)
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Monitor de datos
        monitor_frame = ctk.CTkFrame(bottom_frame)
        monitor_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
        
        monitor_title = ctk.CTkLabel(monitor_frame, text="📄 Monitor de Datos",
                                   font=ctk.CTkFont(size=14, weight="bold"))
        monitor_title.pack(pady=5)
        
        self.ui_elements['data_display'] = ctk.CTkTextbox(monitor_frame, height=120)
        self.ui_elements['data_display'].pack(fill="both", expand=True, padx=5, pady=5)
        
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
        self.ui_elements['last_update_label'] = ctk.CTkLabel(update_frame, text="No hay datos",
                                            font=ctk.CTkFont(size=10),
                                            text_color="#888888")
        self.ui_elements['last_update_label'].pack()
        
        # Calidad de datos
        quality_frame = ctk.CTkFrame(status_frame)
        quality_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(quality_frame, text="📊 Calidad de datos:",
                   font=ctk.CTkFont(size=10)).pack()
        self.ui_elements['quality_label'] = ctk.CTkLabel(quality_frame, text="N/A",
                                        font=ctk.CTkFont(size=10, weight="bold"))
        self.ui_elements['quality_label'].pack()
        
        # Botones de control
        ctk.CTkButton(status_frame, text="Limpiar Monitor",
                    command=self.clear_display).pack(pady=5)