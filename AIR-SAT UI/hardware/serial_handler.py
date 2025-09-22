# hardware/serial_handler.py
"""
Manejo de comunicación serial con el sistema GPS + GY91
Mantiene la funcionalidad exacta del código original con mejor organización
"""

import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime
from core.config import SERIAL_CONFIG, DEBUG_CONFIG, THREADING_CONFIG

class SerialHandler:
    """Maneja toda la comunicación serial de manera optimizada y thread-safe"""
    
    def __init__(self, data_manager, ui_callback=None):
        self.data_manager = data_manager
        self.ui_callback = ui_callback  # Callback para actualizar UI
        
        # Variables de control - MANTIENE LA ESTRUCTURA ORIGINAL
        self.is_running = False
        self.serial_port = None
        self.read_thread = None
        
        # Callbacks para diferentes tipos de eventos
        self.on_data_received = None
        self.on_status_message = None
        self.on_connection_changed = None
        self.on_error = None
        
    def get_available_ports(self):
        """
        Obtiene lista de puertos seriales disponibles
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else ["No hay puertos"]
    
    def connect(self, port, baudrate):
        """
        Conecta al puerto serial especificado
        MANTIENE LA LÓGICA EXACTA DEL ORIGINAL
        """
        if self.is_running:
            return False, "Ya hay una conexión activa"
            
        try:
            # Intentar conexión - EXACTAMENTE IGUAL AL ORIGINAL
            self.serial_port = serial.Serial(
                port=port, 
                baudrate=int(baudrate), 
                timeout=SERIAL_CONFIG['timeout']
            )
            
            self.is_running = True
            
            # Iniciar thread de lectura - EXACTAMENTE IGUAL AL ORIGINAL
            self.read_thread = threading.Thread(target=self._read_serial_loop)
            self.read_thread.daemon = THREADING_CONFIG['daemon_threads']
            self.read_thread.start()
            
            # Notificar conexión exitosa
            if self.on_connection_changed:
                self.on_connection_changed(True, port)
                
            # Mensaje de inicio - EXACTAMENTE IGUAL AL ORIGINAL
            timestamp = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
            if self.on_status_message:
                self.on_status_message(f"{timestamp}Sistema GPS + GY91 conectado a {port}")
                self.on_status_message(f"{timestamp}Monitoreo en tiempo real activado")
                
            return True, f"Conectado a {port}"
            
        except serial.SerialException as e:
            error_msg = f"No se pudo conectar: {str(e)}"
            if self.on_error:
                self.on_error(error_msg)
            return False, error_msg
    
    def disconnect(self):
        """
        Desconecta el puerto serial
        EXACTAMENTE IGUAL AL CÓDIGO ORIGINAL
        """
        self.is_running = False
        
        if self.serial_port:
            try:
                self.serial_port.close()
            except:
                pass
            self.serial_port = None
        
        # Esperar a que termine el hilo de lectura
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)
        
        # Notificar desconexión
        if self.on_connection_changed:
            self.on_connection_changed(False, None)
            
        # Mensaje de desconexión - EXACTAMENTE IGUAL AL ORIGINAL
        timestamp = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
        if self.on_status_message:
            self.on_status_message(f"{timestamp}Sistema desconectado")
    
    def _read_serial_loop(self):
        """
        Loop principal de lectura serial
        MANTIENE LA LÓGICA EXACTA DEL CÓDIGO ORIGINAL
        """
        while self.is_running:
            try:
                if self.serial_port and self.serial_port.in_waiting:
                    data = self.serial_port.readline()
                    try:
                        decoded = data.decode().strip()
                        self._process_serial_data(decoded)
                        
                    except UnicodeDecodeError:
                        # Ignorar errores de decodificación - IGUAL AL ORIGINAL
                        pass
                else:
                    # Pequeña pausa para reducir uso de CPU - IGUAL AL ORIGINAL
                    time.sleep(THREADING_CONFIG['serial_sleep_interval'])
                    
            except serial.SerialException as e:
                # Error de conexión serial - IGUAL AL ORIGINAL
                if self.on_error:
                    self.on_error("Error de conexión serial")
                self.disconnect()
                break
            except Exception as e:
                # Error inesperado
                if self.on_error:
                    self.on_error(f"Error inesperado en lectura serial: {str(e)}")
                break
    
    def _process_serial_data(self, decoded_line):
        """
        Procesa datos recibidos del puerto serial
        Ahora maneja el formato de paquetes LoRa: +RCV=ADDRESS,LENGTH,PAYLOAD,-RSSI,SNR
        """
        timestamp = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
        
        # Procesar paquetes LoRa con formato +RCV
        if decoded_line.startswith("+RCV="):
            if self._process_lora_packet(decoded_line, timestamp):
                # Notificar que hay nuevos datos disponibles
                if self.on_data_received:
                    self.on_data_received()
                
                # Logging cada 100 muestras
                if self.data_manager.data_count % DEBUG_CONFIG['log_every_n_samples'] == 0:
                    if self.on_status_message:
                        self.on_status_message(f"{timestamp}📊 Sistema actualizado - Muestra {self.data_manager.data_count}")
        
        # Procesar líneas que comienzan con "DATA:" - Compatibilidad con formato anterior
        elif decoded_line.startswith("DATA:"):
            csv_data = decoded_line[5:].strip()  # Remover "DATA:" del inicio
            
            if self.data_manager.parse_gps_gy91_data(csv_data):
                # Notificar que hay nuevos datos disponibles
                if self.on_data_received:
                    self.on_data_received()
                
                # Logging cada 100 muestras
                if self.data_manager.data_count % DEBUG_CONFIG['log_every_n_samples'] == 0:
                    if self.on_status_message:
                        self.on_status_message(f"{timestamp}📊 Sistema actualizado - Muestra {self.data_manager.data_count}")
        
        # Procesar mensajes de estado
        elif decoded_line.startswith("STATUS:"):
            status_msg = decoded_line[7:].strip()
            if self.on_status_message:
                self.on_status_message(f"{timestamp}ℹ️ {status_msg}")
        
        # Otros mensajes
        else:
            # Solo mostrar ocasionalmente
            if self.data_manager.data_count % DEBUG_CONFIG['show_raw_every_n'] == 0:
                if self.on_status_message:
                    self.on_status_message(f"{timestamp}Raw: {decoded_line}")
    
    def _process_lora_packet(self, lora_line, timestamp):
        """
        Procesa paquetes LoRa con formato: +RCV=ADDRESS,LENGTH,PAYLOAD,-RSSI,SNR
        """
        try:
            # Remover "+RCV=" del inicio
            packet_data = lora_line[5:].strip()
            parts = packet_data.split(',')
            
            if len(parts) < 5:
                if self.on_status_message:
                    self.on_status_message(f"{timestamp}❌ Paquete LoRa incompleto: {len(parts)} partes")
                return False
            
            # Extraer ADDRESS y LENGTH
            address = parts[0]
            length = int(parts[1])
            
            # Encontrar donde termina el payload (antes del RSSI negativo)
            payload_parts = []
            rssi = None
            snr = None
            
            for i in range(2, len(parts)):
                part = parts[i]
                # Si encontramos un número negativo que parece RSSI
                if part.startswith('-') and len(part) > 1 and part[1:].isdigit():
                    rssi = int(part)
                    # El siguiente debe ser SNR
                    if i + 1 < len(parts):
                        snr = float(parts[i + 1])
                    break
                else:
                    payload_parts.append(part)
            
            if rssi is None or snr is None:
                if self.on_status_message:
                    self.on_status_message(f"{timestamp}❌ No se pudo extraer RSSI/SNR")
                return False
            
            # Reconstruir payload
            payload = ','.join(payload_parts)
            
            # DEBUG: Mostrar información del paquete
            if self.on_status_message:
                self.on_status_message(f"{timestamp}🔍 DEBUG: Payload='{payload}', RSSI={rssi}, SNR={snr}")
            
            # Procesar el payload según su tipo
            result = False
            if payload.startswith('P1,'):
                result = self.data_manager.parse_packet_p1(payload, rssi, snr, timestamp)
            elif payload.startswith('P2,'):
                result = self.data_manager.parse_packet_p2(payload, rssi, snr, timestamp)
            elif payload.startswith('P3,'):
                result = self.data_manager.parse_packet_p3(payload, rssi, snr, timestamp)
            elif payload.startswith('P4,'):
                result = self.data_manager.parse_packet_p4(payload, rssi, snr, timestamp)
            elif payload.startswith('P5,'):
                result = self.data_manager.parse_packet_p5(payload, rssi, snr, timestamp)
            elif payload.startswith('P6,'):
                result = self.data_manager.parse_packet_p6(payload, rssi, snr, timestamp)
            else:
                # Payload desconocido
                if self.on_status_message:
                    self.on_status_message(f"{timestamp}❓ Payload desconocido: {payload[:20]}...")
                return False
            
            # DEBUG: Mostrar resultado del parseo
            if self.on_status_message:
                status = "✅ OK" if result else "❌ FALLO"
                self.on_status_message(f"{timestamp}🔍 DEBUG: Parseo {payload[:2]} -> {status}")
                
            return result
                
        except (ValueError, IndexError) as e:
            if self.on_status_message:
                self.on_status_message(f"{timestamp}❌ Error procesando paquete LoRa: {str(e)}")
            return False
    
    def is_connected(self):
        """Verifica si hay conexión activa"""
        return self.is_running and self.serial_port is not None
    
    def get_connection_info(self):
        """Retorna información de la conexión actual"""
        if self.is_connected():
            try:
                return {
                    'port': self.serial_port.port,
                    'baudrate': self.serial_port.baudrate,
                    'timeout': self.serial_port.timeout,
                    'connected': True
                }
            except:
                return {'connected': False}
        return {'connected': False}
    
    def set_callbacks(self, on_data=None, on_status=None, on_connection=None, on_error=None):
        """
        Configura los callbacks para diferentes eventos
        Permite al código principal reaccionar a eventos sin acoplamiento fuerte
        """
        if on_data:
            self.on_data_received = on_data
        if on_status:
            self.on_status_message = on_status
        if on_connection:
            self.on_connection_changed = on_connection
        if on_error:
            self.on_error = on_error


class SerialDataProcessor:
    """
    Procesador adicional para datos seriales complejos
    Puede extenderse para protocolos específicos sin cambiar SerialHandler
    """
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.protocol_handlers = {}
    
    def register_protocol_handler(self, prefix, handler_func):
        """Registra un manejador para un prefijo de protocolo específico"""
        self.protocol_handlers[prefix] = handler_func
    
    def process_custom_protocol(self, data_line):
        """Procesa protocolos de datos personalizados"""
        for prefix, handler in self.protocol_handlers.items():
            if data_line.startswith(prefix):
                try:
                    return handler(data_line)
                except Exception as e:
                    print(f"Error procesando protocolo {prefix}: {e}")
                    return False
        return False
    
    def validate_gps_data(self, gps_data):
        """
        Valida datos GPS recibidos
        Puede extenderse para validaciones más complejas
        """
        try:
            lat = float(gps_data.get('latitude', 0))
            lon = float(gps_data.get('longitude', 0))
            
            # Validar rango de coordenadas
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return False, "Coordenadas fuera de rango válido"
                
            # Validar HDOP
            hdop = float(gps_data.get('hdop', 99))
            if hdop > 20:
                return False, "HDOP demasiado alto (señal GPS pobre)"
                
            return True, "Datos GPS válidos"
            
        except (ValueError, TypeError):
            return False, "Error en formato de datos GPS"


# Funciones de utilidad para compatibilidad con código original
def get_ports():
    """Función de compatibilidad - mantiene la interfaz original"""
    handler = SerialHandler(None)
    return handler.get_available_ports()