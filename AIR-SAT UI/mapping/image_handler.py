# mapping/image_handler.py
"""
Manejo de imágenes de fondo para el sistema de mapas GPS - VERSIÓN CORREGIDA
Corrige el problema de renderizado de imágenes de fondo
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import FILE_FORMATS, IMAGE_CALIBRATION

class ImageHandler:
    """
    Maneja todas las operaciones con imágenes de fondo
    VERSIÓN CORREGIDA - Arregla el problema de renderizado
    """
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
        # Variables para imagen de fondo
        self.background_image = None
        self.background_photo = None  # Mantener referencia fuerte
        self.image_calibrated = False
        self.image_bounds = {
            "top_left": {"lat": 0.0, "lon": 0.0},
            "bottom_right": {"lat": 0.0, "lon": 0.0}
        }
        self.image_opacity = 0.8
        self.show_background = True
        
        # NUEVO: Cache para evitar regenerar imagen constantemente
        self._cached_photo = None
        self._cached_params = None
    
    def load_background_image(self, parent_window=None):
        """Carga una imagen de fondo para el mapa"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen de mapa",
            filetypes=FILE_FORMATS['image_types']
        )
        
        if file_path:
            try:
                self.background_image = Image.open(file_path)
                self.image_calibrated = False
                self._cached_photo = None  # Limpiar cache
                
                # Mostrar información de la imagen
                width, height = self.background_image.size
                print(f"Imagen cargada: {width}x{height} píxeles")  # DEBUG
                
                messagebox.showinfo(
                    "Imagen Cargada",
                    f"Imagen cargada exitosamente:\n"
                    f"Archivo: {file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]}\n"
                    f"Dimensiones: {width} x {height} píxeles\n\n"
                    f"Ahora debe CALIBRAR la imagen con coordenadas GPS\n"
                    f"usando el botón 'Calibrar'"
                )
                
                # Auto-calibrar si hay posición GPS actual válida
                if self.data_manager.sensor_data['latitude'] != 0.0 and self.data_manager.sensor_data['longitude'] != 0.0:
                    return self.auto_calibrate_image()
                else:
                    return self.calibrate_image(parent_window)
                    
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{str(e)}")
                return False
        
        return False
    
    def auto_calibrate_image(self):
        """Auto-calibra la imagen centrada en la posición GPS actual"""
        if not self.background_image:
            return False
            
        # Usar la posición actual como centro de la imagen
        current_lat = self.data_manager.sensor_data['latitude']
        current_lon = self.data_manager.sensor_data['longitude']
        
        print(f"Auto-calibrando en: {current_lat}, {current_lon}")  # DEBUG
        
        # Estimar el área que cubre la imagen (asumir ~500m de radio por defecto)
        estimated_radius_meters = IMAGE_CALIBRATION['default_radius_meters']
        
        # Convertir a grados aproximadamente
        lat_degree_meters = IMAGE_CALIBRATION['lat_degree_meters']
        lon_degree_meters = lat_degree_meters * math.cos(math.radians(current_lat))
        
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
        self._cached_photo = None  # Limpiar cache
        
        print(f"Bounds configurados: {self.image_bounds}")  # DEBUG
        
        messagebox.showinfo(
            "Auto-Calibración",
            f"Imagen auto-calibrada centrada en:\n"
            f"Lat: {current_lat:.6f}°\n"
            f"Lon: {current_lon:.6f}°\n"
            f"Área estimada: ±{estimated_radius_meters}m\n\n"
            f"Use 'Calibrar' para ajustar manualmente si es necesario."
        )
        
        return True
    
    def calibrate_image(self, parent_window=None):
        """Calibra la imagen con coordenadas GPS específicas"""
        if not self.background_image:
            messagebox.showwarning("Sin Imagen", "Primero debe cargar una imagen de fondo")
            return False
            
        dialog = ImageCalibrationDialog(parent_window, self.data_manager.sensor_data)
        
        if parent_window:
            parent_window.wait_window(dialog.dialog)
        else:
            temp_root = tk.Tk()
            temp_root.withdraw()
            temp_root.wait_window(dialog.dialog)
            temp_root.destroy()
        
        if dialog.result:
            self.image_bounds = dialog.result
            self.image_calibrated = True
            self._cached_photo = None  # Limpiar cache
            return True
            
        return False
    
    def update_opacity(self, value):
        """Actualiza la opacidad de la imagen de fondo"""
        self.image_opacity = float(value)
        self._cached_photo = None  # Limpiar cache cuando cambia opacidad
    
    def get_background_photo_for_canvas(self, canvas_width, canvas_height, map_center, meters_per_pixel):
        """
        Genera la imagen redimensionada para el canvas
        VERSIÓN CORREGIDA - Arregla problemas de renderizado
        """
        if not (self.background_image and self.image_calibrated and self.show_background):
            return None
            
        try:
            print(f"Generando imagen para canvas {canvas_width}x{canvas_height}")  # DEBUG
            print(f"Centro del mapa: {map_center}")  # DEBUG
            print(f"Metros por píxel: {meters_per_pixel}")  # DEBUG
            
            # Verificar cache
            current_params = (canvas_width, canvas_height, map_center['lat'], map_center['lon'], meters_per_pixel, self.image_opacity)
            if self._cached_photo and self._cached_params == current_params:
                print("Usando imagen desde cache")  # DEBUG
                return self._cached_photo
            
            # Calcular coordenadas de canvas para las esquinas de la imagen
            top_left_x, top_left_y = self._geo_to_canvas(
                self.image_bounds["top_left"]["lat"], 
                self.image_bounds["top_left"]["lon"],
                canvas_width, canvas_height, map_center, meters_per_pixel
            )
            bottom_right_x, bottom_right_y = self._geo_to_canvas(
                self.image_bounds["bottom_right"]["lat"], 
                self.image_bounds["bottom_right"]["lon"],
                canvas_width, canvas_height, map_center, meters_per_pixel
            )
            
            print(f"Coordenadas imagen en canvas: ({top_left_x},{top_left_y}) -> ({bottom_right_x},{bottom_right_y})")  # DEBUG
            
            # Calcular el tamaño necesario de la imagen en píxeles
            image_width = abs(bottom_right_x - top_left_x)
            image_height = abs(bottom_right_y - top_left_y)
            
            print(f"Tamaño calculado: {image_width}x{image_height}")  # DEBUG
            
            if image_width > 10 and image_height > 10:  # Verificar que sea visible
                # Redimensionar imagen para que encaje en el área calibrada
                resized_image = self.background_image.resize(
                    (int(image_width), int(image_height)), 
                    Image.Resampling.LANCZOS
                )
                
                # Aplicar opacidad
                if self.image_opacity < 1.0:
                    if resized_image.mode != 'RGBA':
                        resized_image = resized_image.convert('RGBA')
                    
                    # Crear máscara de alpha
                    alpha = int(255 * self.image_opacity)
                    # Crear nueva imagen con alpha
                    alpha_image = Image.new('RGBA', resized_image.size, (255, 255, 255, 0))
                    alpha_image.paste(resized_image, (0, 0))
                    
                    # Aplicar transparencia
                    pixels = alpha_image.load()
                    for y in range(alpha_image.height):
                        for x in range(alpha_image.width):
                            r, g, b, a = pixels[x, y]
                            pixels[x, y] = (r, g, b, int(a * self.image_opacity))
                    
                    resized_image = alpha_image
                
                # Convertir a PhotoImage para tkinter
                self.background_photo = ImageTk.PhotoImage(resized_image)
                
                result = {
                    'photo': self.background_photo,
                    'x': min(top_left_x, bottom_right_x),  # Asegurar coordenada mínima
                    'y': min(top_left_y, bottom_right_y)   # Asegurar coordenada mínima
                }
                
                # Guardar en cache
                self._cached_photo = result
                self._cached_params = current_params
                
                print(f"Imagen generada exitosamente en posición ({result['x']}, {result['y']})")  # DEBUG
                return result
            else:
                print(f"Imagen demasiado pequeña o fuera del canvas: {image_width}x{image_height}")  # DEBUG
                
        except Exception as e:
            print(f"Error generando imagen de fondo: {e}")
            import traceback
            traceback.print_exc()  # DEBUG completo
            
        return None
    
    def _geo_to_canvas(self, lat, lon, canvas_width, canvas_height, map_center, meters_per_pixel):
        """Convierte coordenadas geográficas a píxeles del canvas"""
        # Calcular offset en metros desde el centro del mapa
        dx_meters, dy_meters = self._lat_lon_to_meters(
            map_center["lat"], map_center["lon"], lat, lon
        )
        
        # Convertir a píxeles
        dx_pixels = dx_meters / meters_per_pixel
        dy_pixels = -dy_meters / meters_per_pixel  # Y negativo porque canvas Y crece hacia abajo
        
        # Posición en canvas
        x = canvas_width / 2 + dx_pixels
        y = canvas_height / 2 + dy_pixels
        
        return x, y
    
    def _lat_lon_to_meters(self, lat1, lon1, lat2, lon2):
        """Convierte diferencia lat/lon a metros usando fórmula haversine simplificada"""
        R = 6371000  # Radio de la Tierra en metros
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        # Aproximación para distancias cortas
        lat_avg = math.radians((lat1 + lat2) / 2)
        
        dx = R * dlon * math.cos(lat_avg)
        dy = R * dlat
        
        return dx, dy


class ImageCalibrationDialog:
    """Diálogo para calibrar imagen con coordenadas GPS"""
    def __init__(self, parent, sensor_data):
        self.result = None
        self.sensor_data = sensor_data
        
        # Crear ventana de diálogo
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title("Calibrar Imagen con GPS")
        self.dialog.geometry(IMAGE_CALIBRATION['dialog_size'])
        self.dialog.resizable(False, False)
        
        if parent:
            self.dialog.grab_set()
            self.dialog.transient(parent)
        
        self.setup_dialog_content()
        
    def setup_dialog_content(self):
        """Configura el contenido del diálogo"""
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
                font=("Arial", 9, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=5, pady=5)
        
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
                font=("Arial", 9, "bold")).grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=(10,5))
        
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
        lat_offset = IMAGE_CALIBRATION['estimation_radius_meters'] / IMAGE_CALIBRATION['lat_degree_meters']
        lon_offset = lat_offset / math.cos(math.radians(self.sensor_data['latitude']))
        
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
            
            # Validar coordenadas
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