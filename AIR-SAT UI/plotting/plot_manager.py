# plotting/plot_manager.py
"""
Gestión de gráficas matplotlib para el sistema GPS + GY91
Mantiene la funcionalidad exacta del código original
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import customtkinter as ctk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import PLOT_CONFIG, DATA_CONFIG

class PlotManager:
    """
    Gestiona todas las gráficas del sistema
    MANTIENE LA FUNCIONALIDAD EXACTA DEL CÓDIGO ORIGINAL
    """
    
    def __init__(self, parent_frame, data_manager):
        self.parent = parent_frame
        self.data_manager = data_manager
        
        # Variables de control - EXACTAMENTE IGUAL AL ORIGINAL
        self.plotting_enabled = True
        self.plot_update_counter = 0
        self.plot_update_interval = DATA_CONFIG['plot_update_interval']
        
        # Referencias matplotlib
        self.fig = None
        self.axes = None
        self.canvas = None
        self.animation = None
        
        # Configurar matplotlib - EXACTAMENTE IGUAL AL ORIGINAL
        self.setup_matplotlib_config()
        
        # Configurar la interfaz
        self.setup_plots_interface()
        
    def setup_matplotlib_config(self):
        """Configura matplotlib - EXACTAMENTE IGUAL AL ORIGINAL"""
        plt.style.use(PLOT_CONFIG['style'])
        plt.rcParams.update(PLOT_CONFIG['rcParams'])
    
    def setup_plots_interface(self):
        """
        Configura la interfaz de gráficas
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        # Control panel para gráficas
        control_frame = ctk.CTkFrame(self.parent)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(control_frame, text="🎛️ CONTROLES DE GRÁFICAS",
                   font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
        
        # Buffer size control - EXACTAMENTE IGUAL AL ORIGINAL
        ctk.CTkLabel(control_frame, text="Buffer:", font=ctk.CTkFont(size=10)).pack(side="left", padx=5)
        self.buffer_var = ctk.StringVar(value="500")
        buffer_select = ctk.CTkOptionMenu(control_frame, variable=self.buffer_var,
                                        values=["250", "500", "1000"],
                                        command=self.update_buffer_size)
        buffer_select.pack(side="left", padx=5)
        
        ctk.CTkButton(control_frame, text="🗑️ Limpiar Datos",
                    command=self.clear_plot_data).pack(side="left", padx=10)
        
        # Crear figura con subplots - EXACTAMENTE IGUAL AL ORIGINAL
        self.fig, self.axes = plt.subplots(3, 3, figsize=PLOT_CONFIG['figure_size'])
        self.fig.patch.set_facecolor(PLOT_CONFIG['rcParams']['figure.facecolor'])
        self.fig.suptitle('Sistema GPS + GY91 - Datos Tiempo Real', fontsize=12, color='white')
        
        # Configurar subplots - EXACTAMENTE IGUAL AL ORIGINAL
        plot_titles = PLOT_CONFIG['titles']
        
        for i, (row, col) in enumerate([(r, c) for r in range(3) for c in range(3)]):
            ax = self.axes[row, col]
            ax.set_title(plot_titles[i], fontsize=9, color='white')
            ax.set_facecolor(PLOT_CONFIG['rcParams']['axes.facecolor'])
            ax.tick_params(colors='white', labelsize=7)
            ax.grid(True, alpha=0.2)
            
            for spine in ax.spines.values():
                spine.set_color('white')
        
        plt.tight_layout()
        
        # Integrar matplotlib con tkinter - EXACTAMENTE IGUAL AL ORIGINAL
        self.canvas = FigureCanvasTkAgg(self.fig, self.parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurar animación - EXACTAMENTE IGUAL AL ORIGINAL
        self.animation = FuncAnimation(
            self.fig, 
            self.update_plots, 
            interval=PLOT_CONFIG.get('animation_interval', DATA_CONFIG['plot_animation_interval']), 
            blit=False
        )
    
    def update_buffer_size(self, new_size):
        """
        Actualiza el tamaño del buffer de datos
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        success = self.data_manager.update_buffer_size(new_size)
        if not success:
            print(f"Error actualizando buffer size: {new_size}")
    
    def clear_plot_data(self):
        """
        Limpia todos los datos de las gráficas
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        self.data_manager.clear_plot_data()
    
    def set_plotting_enabled(self, enabled):
        """Configura si las gráficas están habilitadas"""
        self.plotting_enabled = enabled
    
    def update_plots(self, frame):
        """
        Actualiza gráficas
        MANTIENE LA LÓGICA EXACTA DEL CÓDIGO ORIGINAL
        """
        if (not self.plotting_enabled or 
            len(self.data_manager.time_buffer) < 5):
            return
        
        try:
            times = list(self.data_manager.time_buffer)
            step = max(1, len(times) // 200)
            times_sampled = times[::step]
            
            # Limpiar plots - EXACTAMENTE IGUAL AL ORIGINAL
            for ax in self.axes.flat:
                ax.clear()
                ax.set_facecolor(PLOT_CONFIG['rcParams']['axes.facecolor'])
                ax.tick_params(colors='white', labelsize=7)
                ax.grid(True, alpha=0.2)
                for spine in ax.spines.values():
                    spine.set_color('white')
            
            # Plot datos GPS y sensores - EXACTAMENTE IGUAL AL ORIGINAL
            if len(self.data_manager.gps_data['latitude']) > 0:
                self._plot_gps_data(times_sampled, step)
                self._plot_bmp280_data(times_sampled, step)
                
                if len(self.data_manager.mpu9250_data['accel_x']) > 0:
                    self._plot_mpu9250_data(times_sampled, step)
                
                self._plot_altitude_comparison(times_sampled, step)
            
            # Formateo de fecha - EXACTAMENTE IGUAL AL ORIGINAL
            self._format_time_axes(times_sampled)
            
            plt.tight_layout()
            self.canvas.draw_idle()
            
        except Exception as e:
            # Silenciar errores como en el original
            pass
    
    def _plot_gps_data(self, times_sampled, step):
        """Plot datos GPS - EXACTAMENTE IGUAL AL ORIGINAL"""
        # GPS Coordenadas
        self.axes[0, 0].plot(times_sampled, list(self.data_manager.gps_data['latitude'])[::step], 'g-', label='Lat', linewidth=1)
        self.axes[0, 0].plot(times_sampled, list(self.data_manager.gps_data['longitude'])[::step], 'r-', label='Lon', linewidth=1)
        self.axes[0, 0].set_title("GPS - Latitud/Longitud", fontsize=9, color='white')
        self.axes[0, 0].legend(fontsize=7)
        
        # GPS Altitud/Velocidad
        ax2 = self.axes[0, 1].twinx()
        self.axes[0, 1].plot(times_sampled, list(self.data_manager.gps_data['altitude'])[::step], 'b-', label='Alt (m)', linewidth=1)
        ax2.plot(times_sampled, list(self.data_manager.gps_data['speed'])[::step], 'orange', label='Vel (km/h)', linewidth=1)
        self.axes[0, 1].set_title("GPS - Altitud/Velocidad", fontsize=9, color='white')
        self.axes[0, 1].legend(loc='upper left', fontsize=7)
        ax2.legend(loc='upper right', fontsize=7)
        
        # Configurar colores del eje twin
        ax2.tick_params(colors='white', labelsize=7)
        for spine in ax2.spines.values():
            spine.set_color('white')
    
    def _plot_bmp280_data(self, times_sampled, step):
        """Plot datos BMP280 - EXACTAMENTE IGUAL AL ORIGINAL"""
        ax3 = self.axes[0, 2].twinx()
        self.axes[0, 2].plot(times_sampled, list(self.data_manager.bmp280_data['temp'])[::step], 'r-', label='Temp (°C)', linewidth=1)
        ax3.plot(times_sampled, list(self.data_manager.bmp280_data['pressure'])[::step], 'b-', label='Pres (mbar)', linewidth=1)
        self.axes[0, 2].set_title("BMP280 - Temp/Presión", fontsize=9, color='white')
        self.axes[0, 2].legend(loc='upper left', fontsize=7)
        ax3.legend(loc='upper right', fontsize=7)
        
        # Configurar colores del eje twin
        ax3.tick_params(colors='white', labelsize=7)
        for spine in ax3.spines.values():
            spine.set_color('white')
    
    def _plot_mpu9250_data(self, times_sampled, step):
        """Plot datos MPU9250 - EXACTAMENTE IGUAL AL ORIGINAL"""
        # Acelerómetro
        self.axes[1, 0].plot(times_sampled, list(self.data_manager.mpu9250_data['accel_x'])[::step], 'r-', linewidth=1, alpha=0.8)
        self.axes[1, 0].plot(times_sampled, list(self.data_manager.mpu9250_data['accel_y'])[::step], 'g-', linewidth=1, alpha=0.8)
        self.axes[1, 0].plot(times_sampled, list(self.data_manager.mpu9250_data['accel_z'])[::step], 'b-', linewidth=1, alpha=0.8)
        self.axes[1, 0].set_title("Acelerómetro (g)", fontsize=9, color='white')
        
        # Giroscopio
        self.axes[1, 1].plot(times_sampled, list(self.data_manager.mpu9250_data['gyro_x'])[::step], 'r-', linewidth=1, alpha=0.8)
        self.axes[1, 1].plot(times_sampled, list(self.data_manager.mpu9250_data['gyro_y'])[::step], 'g-', linewidth=1, alpha=0.8)
        self.axes[1, 1].plot(times_sampled, list(self.data_manager.mpu9250_data['gyro_z'])[::step], 'b-', linewidth=1, alpha=0.8)
        self.axes[1, 1].set_title("Giroscopio (dps)", fontsize=9, color='white')
        
        # Magnetómetro
        self.axes[1, 2].plot(times_sampled, list(self.data_manager.mpu9250_data['mag_x'])[::step], 'r-', linewidth=1, alpha=0.8)
        self.axes[1, 2].plot(times_sampled, list(self.data_manager.mpu9250_data['mag_y'])[::step], 'g-', linewidth=1, alpha=0.8)
        self.axes[1, 2].plot(times_sampled, list(self.data_manager.mpu9250_data['mag_z'])[::step], 'b-', linewidth=1, alpha=0.8)
        self.axes[1, 2].set_title("Magnetómetro (µT)", fontsize=9, color='white')
        
        # Orientación
        self.axes[2, 0].plot(times_sampled, list(self.data_manager.mpu9250_data['roll'])[::step], 'r-', linewidth=1)
        self.axes[2, 0].plot(times_sampled, list(self.data_manager.mpu9250_data['pitch'])[::step], 'g-', linewidth=1)
        self.axes[2, 0].plot(times_sampled, list(self.data_manager.mpu9250_data['yaw'])[::step], 'b-', linewidth=1)
        self.axes[2, 0].set_title("Orientación (°)", fontsize=9, color='white')
        
        # Rumbo
        self.axes[2, 1].plot(times_sampled, list(self.data_manager.mpu9250_data['heading'])[::step], 'lime', linewidth=1)
        self.axes[2, 1].set_title("Rumbo Magnético (°)", fontsize=9, color='white')
        self.axes[2, 1].set_ylim(0, 360)
    
    def _plot_altitude_comparison(self, times_sampled, step):
        """Plot comparación altitudes - EXACTAMENTE IGUAL AL ORIGINAL"""
        self.axes[2, 2].plot(times_sampled, list(self.data_manager.gps_data['altitude'])[::step], 'g-', label='GPS', linewidth=1)
        self.axes[2, 2].plot(times_sampled, list(self.data_manager.bmp280_data['altitude'])[::step], 'orange', label='BMP280', linewidth=1)
        self.axes[2, 2].set_title("Altitudes GPS vs BMP280", fontsize=9, color='white')
        self.axes[2, 2].legend(fontsize=7)
    
    def _format_time_axes(self, times_sampled):
        """Formateo de ejes de tiempo - EXACTAMENTE IGUAL AL ORIGINAL"""
        for i, ax in enumerate([self.axes[2, 0], self.axes[2, 1], self.axes[2, 2]]):
            if len(times_sampled) > 1:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=6)
    
    def cleanup(self):
        """Limpieza al cerrar la aplicación"""
        if self.animation:
            self.animation.event_source.stop()
        
        if self.fig:
            plt.close(self.fig)