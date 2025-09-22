# main.py
"""
Sistema GPS + GY91 - Monitor de Navegación
Versión modularizada para mejor rendimiento y mantenimiento

MANTIENE TODA LA FUNCIONALIDAD ORIGINAL
Todas las dependencias y características se preservan exactamente
"""

import customtkinter as ctk
import threading
from datetime import datetime
import time

# Importar módulos del sistema - Lazy loading para mejor rendimiento
from core.config import WINDOW_CONFIG, LABELS, SERIAL_CONFIG
from core.data_manager import DataManager
from hardware.serial_handler import SerialHandler

# Imports lazy de módulos pesados (se cargan solo cuando se necesitan)
plot_manager = None
map_system = None

class GPSGy91Monitor:
    """
    Aplicación principal del sistema GPS + GY91
    Coordina todos los módulos pero mantiene la funcionalidad exacta
    """
    
    def __init__(self):
        # Configuración de la ventana principal - EXACTAMENTE IGUAL AL ORIGINAL
        self.root = ctk.CTk()
        self.root.title(WINDOW_CONFIG['title'])
        self.root.geometry(WINDOW_CONFIG['geometry'])
        
        # Inicializar gestores principales
        self.data_manager = DataManager()
        self.serial_handler = SerialHandler(self.data_manager)
        
        # Variables de control - MANTIENE ESTRUCTURA ORIGINAL
        self.plotting_enabled = True
        self.current_tab = LABELS['tabs']['realtime']
        
        # Módulos lazy-loaded (se cargan solo cuando se usan)
        self.plots_manager = None
        self.map_renderer = None
        self.plots_initialized = False
        self.map_initialized = False
        
        # Configurar callbacks del serial handler
        self.serial_handler.set_callbacks(
            on_data=self.on_serial_data_received,
            on_status=self.on_status_message,
            on_connection=self.on_connection_changed,
            on_error=self.on_error_message
        )
        
        # Crear la interfaz
        self.setup_gui()
        
    def setup_gui(self):
        """Configura la interfaz principal - MANTIENE ESTRUCTURA EXACTA"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header con información del sistema - EXACTAMENTE IGUAL AL ORIGINAL
        self.setup_header(main_frame)
        
        # Frame de conexión - EXACTAMENTE IGUAL AL ORIGINAL  
        self.setup_connection_frame(main_frame)
        
        # Sistema de pestañas - EXACTAMENTE IGUAL AL ORIGINAL
        self.setup_tab_system(main_frame)
        
    def setup_header(self, parent):
        """Configura el header - EXACTAMENTE IGUAL AL ORIGINAL"""
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        title_label = ctk.CTkLabel(header_frame, 
                                 text="SISTEMA GPS + GY91 - NAVEGACION AVANZADA",
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=5)
        
        subtitle_label = ctk.CTkLabel(header_frame,
                                    text="GPS (Posicionamiento Global) + BMP280 (Barometro) + MPU9250 (IMU 9-DOF)",
                                    font=ctk.CTkFont(size=12))
        subtitle_label.pack(pady=2)
    
    def setup_connection_frame(self, parent):
        """Configura frame de conexión - EXACTAMENTE IGUAL AL ORIGINAL"""
        conn_frame = ctk.CTkFrame(parent)
        conn_frame.pack(fill="x", padx=5, pady=5)
        
        # Botón refrescar puertos
        ctk.CTkButton(conn_frame, text="Refresh", width=60,
                    command=self.update_ports).pack(side="left", padx=5)
        
        # Selector de puerto
        self.port_var = ctk.StringVar()
        self.port_select = ctk.CTkOptionMenu(conn_frame, 
                                        variable=self.port_var,
                                        values=self.serial_handler.get_available_ports())
        self.port_select.pack(side="left", padx=5)
        
        # Selector de baudrate
        self.baud_var = ctk.StringVar(value=SERIAL_CONFIG['default_baud'])
        baud_select = ctk.CTkOptionMenu(conn_frame,
                                    variable=self.baud_var,
                                    values=SERIAL_CONFIG['available_bauds'])
        baud_select.pack(side="left", padx=5)
        
        # Botón conectar
        self.connect_btn = ctk.CTkButton(conn_frame, text="Conectar",
                                    command=self.toggle_connection)
        self.connect_btn.pack(side="left", padx=5)
        
        # Status y contadores - EXACTAMENTE IGUAL AL ORIGINAL
        self.status_label = ctk.CTkLabel(conn_frame, text=LABELS['status']['disconnected'], 
                                       font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.pack(side="left", padx=20)
        
        self.data_count_label = ctk.CTkLabel(conn_frame, text="Muestras: 0", 
                                           font=ctk.CTkFont(size=12))
        self.data_count_label.pack(side="left", padx=10)
        
        # Control de gráficas
        self.plot_toggle = ctk.CTkButton(conn_frame, text="Pausar Graficas",
                                       command=self.toggle_plotting)
        self.plot_toggle.pack(side="left", padx=10)
    
    def setup_tab_system(self, parent):
        """Configura sistema de pestañas - EXACTAMENTE IGUAL AL ORIGINAL"""
        self.tabview = ctk.CTkTabview(parent, command=self.tab_changed)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Pestaña 1: Monitor en tiempo real
        self.tabview.add(LABELS['tabs']['realtime'])
        self.setup_realtime_tab()
        
        # Pestaña 2: Gráficas (lazy loaded)
        self.tabview.add(LABELS['tabs']['plots'])
        
        # Pestaña 3: Mapa GPS (lazy loaded)
        self.tabview.add(LABELS['tabs']['map'])
    
    def setup_realtime_tab(self):
        """Configura pestaña tiempo real - IMPORTA MÓDULO DEDICADO"""
        from ui.realtime_monitor import RealtimeMonitor
        
        realtime_frame = self.tabview.tab(LABELS['tabs']['realtime'])
        self.realtime_monitor = RealtimeMonitor(realtime_frame, self.data_manager)
        
    def tab_changed(self):
        """Callback cuando cambia de pestaña - LAZY LOADING"""
        self.current_tab = self.tabview.get()
        
        # Lazy loading de gráficas
        if self.current_tab == LABELS['tabs']['plots'] and not self.plots_initialized:
            self.setup_plots_tab()
            self.plots_initialized = True
            
        # Lazy loading del mapa
        elif self.current_tab == LABELS['tabs']['map'] and not self.map_initialized:
            self.setup_map_tab()
            self.map_initialized = True
    
    def setup_plots_tab(self):
        """Lazy loading de módulo de gráficas"""
        global plot_manager
        if plot_manager is None:
            # Import lazy para no cargar matplotlib hasta que se necesite
            from plotting.plot_manager import PlotManager
            plot_manager = PlotManager
            
        plots_frame = self.tabview.tab(LABELS['tabs']['plots'])
        self.plots_manager = plot_manager(plots_frame, self.data_manager)
        
        # Configurar callbacks
        self.plots_manager.set_plotting_enabled(self.plotting_enabled)
    
    def setup_map_tab(self):
        """Lazy loading de módulo de mapas"""
        global map_system
        if map_system is None:
            # Import lazy para no cargar PIL/imagen hasta que se necesite
            from mapping.gps_map import GPSMapSystem
            map_system = GPSMapSystem
            
        map_frame = self.tabview.tab(LABELS['tabs']['map'])
        self.map_renderer = map_system(map_frame, self.data_manager)
    
    def toggle_connection(self):
        """Conectar/Desconectar puerto serial - EXACTAMENTE IGUAL AL ORIGINAL"""
        if not self.serial_handler.is_connected():
            port = self.port_var.get()
            baud = self.baud_var.get()
            
            success, message = self.serial_handler.connect(port, baud)
            if not success:
                self.show_error_message(message)
        else:
            self.serial_handler.disconnect()
    
    def update_ports(self):
        """Actualiza lista de puertos disponibles"""
        ports = self.serial_handler.get_available_ports()
        self.port_select.configure(values=ports)
    
    def toggle_plotting(self):
        """Toggle para pausar/reanudar gráficas - EXACTAMENTE IGUAL AL ORIGINAL"""
        self.plotting_enabled = not self.plotting_enabled
        
        if self.plotting_enabled:
            self.plot_toggle.configure(text="Pausar Graficas")
        else:
            self.plot_toggle.configure(text="Reanudar Graficas")
            
        # Notificar al manager de plots si está cargado
        if self.plots_manager:
            self.plots_manager.set_plotting_enabled(self.plotting_enabled)
    
    # Callbacks del SerialHandler
    def on_serial_data_received(self):
        """Callback cuando se reciben nuevos datos seriales"""
        # Usar after_idle para thread-safety - EXACTAMENTE IGUAL AL ORIGINAL
        self.root.after_idle(self.update_all_displays)
        
        # Actualizar contador menos frecuentemente
        if self.data_manager.data_count % 10 == 0:
            self.root.after_idle(
                lambda: self.data_count_label.configure(
                    text=f"Muestras: {self.data_manager.data_count}"
                )
            )
    
    def on_status_message(self, message):
        """Callback para mensajes de estado"""
        self.root.after_idle(lambda: self.realtime_monitor.add_status_message(message))
    
    def on_connection_changed(self, connected, port):
        """Callback cuando cambia el estado de conexión"""
        if connected:
            self.root.after_idle(lambda: self.connect_btn.configure(text="Desconectar"))
            self.root.after_idle(lambda: self.status_label.configure(text=LABELS['status']['connected'].format(port)))
        else:
            self.root.after_idle(lambda: self.connect_btn.configure(text="Conectar"))
            self.root.after_idle(lambda: self.status_label.configure(text=LABELS['status']['disconnected']))
    
    def on_error_message(self, error):
        """Callback para mensajes de error"""
        self.root.after_idle(lambda: self.show_error_message(error))
    
    def show_error_message(self, message):
        """Muestra mensaje de error al usuario"""
        self.realtime_monitor.add_status_message(f"[ERROR]: {message}")
    
    def update_all_displays(self):
        """
        Actualiza todos los displays
        MANTIENE LA LÓGICA DE THROTTLING ORIGINAL
        """
        if not self.data_manager.should_update_ui():
            return
        
        # Actualizar monitor tiempo real
        self.realtime_monitor.update_displays()
        
        # Actualizar plots si está cargado y en pestaña activa
        if (self.plots_manager and 
            self.current_tab == LABELS['tabs']['plots'] and 
            self.plotting_enabled):
            # Agregar datos a buffers para plotting
            current_time = datetime.now()
            self.data_manager.add_to_plot_buffers(current_time)
        
        # Actualizar mapa si está cargado y en pestaña activa
        if (self.map_renderer and 
            self.current_tab == LABELS['tabs']['map']):
            # Agregar punto al track y actualizar mapa
            if self.data_manager.add_track_point():
                self.map_renderer.update_map()
    
    def run(self):
        """Inicia la aplicación - EXACTAMENTE IGUAL AL ORIGINAL"""
        # Configurar cierre de aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar loop principal
        self.root.mainloop()
    
    def on_closing(self):
        """Maneja el cierre de la aplicación - LIMPIEZA ADECUADA"""
        # Desconectar puerto serial
        if self.serial_handler.is_connected():
            self.serial_handler.disconnect()
        
        # Cerrar módulos si están cargados
        if self.plots_manager:
            self.plots_manager.cleanup()
            
        if self.map_renderer:
            self.map_renderer.cleanup()
        
        # Cerrar aplicación
        self.root.quit()
        self.root.destroy()


def main():
    """Función principal - MISMA ESTRUCTURA ORIGINAL"""
    print("=== Sistema GPS + GY91 - Monitor de Navegación ===")
    print("Versión modularizada para mejor rendimiento")
    print("Inicializando sistema...")
    
    try:
        app = GPSGy91Monitor()
        print("[OK] Sistema inicializado correctamente")
        print("[STARTUP] Iniciando interfaz grafica...")
        app.run()
        
    except Exception as e:
        print(f"[ERROR] Error fatal al inicializar: {e}")
        import traceback
        traceback.print_exc()
    
    print("[EXIT] Sistema cerrado")


if __name__ == "__main__":
    main()  