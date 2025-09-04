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
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        # Frame principal de datos con 3 columnas
        sensors_frame = ctk.CTkFrame(self.parent)
        sensors_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # === COLUMNA 1: GPS === - EXACTAMENTE IGUAL AL ORIGINAL
        self.setup_gps_column(sensors_frame)
        
        # === COLUMNA 2: BMP280 === - EXACTAMENTE IGUAL AL ORIGINAL  
        self.setup_bmp280_column(sensors_frame)
        
        # === COLUMNA 3: MPU9250 === - EXACTAMENTE IGUAL AL ORIGINAL
        self.setup_mpu9250_column(sensors_frame)
        
        # Frame inferior con monitor y estado - EXACTAMENTE IGUAL AL ORIGINAL
        self.setup_bottom_frame()
    
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
        MANTIENE LA LÓGICA EXACTA DEL CÓDIGO ORIGINAL
        """
        data = self.data_manager.sensor_data
        
        # GPS - EXACTAMENTE IGUAL AL ORIGINAL
        self.ui_elements['lat_label'].configure(text=f"{data['latitude']:.6f}° {data['lat_dir']}")
        self.ui_elements['lon_label'].configure(text=f"{data['longitude']:.6f}° {data['lon_dir']}")
        self.ui_elements['gps_alt_label'].configure(text=f"{data['gps_altitude']:.1f} m")
        self.ui_elements['speed_label'].configure(text=f"{data['speed']:.1f} km/h")
        
        # Estado GPS con colores - EXACTAMENTE IGUAL AL ORIGINAL
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
        self.ui_elements['bmp_temp_label'].configure(text=f"{data['bmp_temp']:.2f} °C")
        self.ui_elements['bmp_pres_label'].configure(text=f"{data['pressure']:.2f} mbar")
        self.ui_elements['bmp_alt_label'].configure(text=f"{data['bmp_altitude']:.1f} m")
        
        # Diferencia de altitudes - EXACTAMENTE IGUAL AL ORIGINAL
        alt_diff = abs(data['altitude_diff'])
        alt_color = QUALITY_COLORS['excellent'] if alt_diff < 5.0 else QUALITY_COLORS['good'] if alt_diff < 15.0 else QUALITY_COLORS['poor']
        self.ui_elements['diff_alt_label'].configure(text=f"{data['altitude_diff']:.1f} m", text_color=alt_color)
        
        # MPU9250 - EXACTAMENTE IGUAL AL ORIGINAL
        self.ui_elements['mpu_temp_label'].configure(text=f"{data['mpu_temp']:.1f} °C")
        self.ui_elements['accel_label'].configure(text=f"{data['accel_x']:.3f}, {data['accel_y']:.3f}, {data['accel_z']:.3f} g")
        self.ui_elements['accel_total_label'].configure(text=f"{data['total_accel']:.3f} g")
        self.ui_elements['gyro_label'].configure(text=f"{data['gyro_x']:.2f}, {data['gyro_y']:.2f}, {data['gyro_z']:.2f} dps")
        self.ui_elements['gyro_total_label'].configure(text=f"{data['total_gyro']:.2f} dps")
        self.ui_elements['mag_label'].configure(text=f"{data['mag_x']:.1f}, {data['mag_y']:.1f}, {data['mag_z']:.1f} µT")
        self.ui_elements['rpy_label'].configure(text=f"{data['roll']:.1f}°, {data['pitch']:.1f}°, {data['yaw']:.1f}°")
        
        # Heading con dirección cardinal - EXACTAMENTE IGUAL AL ORIGINAL
        cardinal = self.data_manager.get_cardinal_direction(data['heading'])
        self.ui_elements['heading_label'].configure(text=f"{data['heading']:.1f}° ({cardinal})")
        
        # Estado del sistema - EXACTAMENTE IGUAL AL ORIGINAL
        self.ui_elements['last_update_label'].configure(text=data['last_update'])
        
        # Calidad de datos - EXACTAMENTE IGUAL AL ORIGINAL
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