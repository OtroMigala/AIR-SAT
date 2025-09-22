# mapping/google_maps_config.py
"""
Google Maps API configuration for AIR-SAT mapping system
"""

import os
import json
from tkinter import messagebox, simpledialog

class GoogleMapsConfig:
    """Handles Google Maps API key configuration"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'google_maps_api.json')
        # Use provided API key as default
        self.api_key = "AIzaSyDFjDcAS7KaX9IKqdSYFs45EbqLQssOyVI"
        self.load_config()
    
    def load_config(self):
        """Load API key from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    loaded_key = config.get('api_key', '')
                    if loaded_key:  # Only use loaded key if it exists
                        self.api_key = loaded_key
            # If no config file or empty key, keep the default API key
        except Exception as e:
            print(f"Error loading Google Maps config: {e}")
            # Keep the default API key on error
    
    def save_config(self):
        """Save API key to config file"""
        try:
            config = {'api_key': self.api_key}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving Google Maps config: {e}")
            return False
    
    def get_api_key(self):
        """Get the API key, prompt user if not set"""
        if not self.api_key:
            self.prompt_for_api_key()
        return self.api_key
    
    def prompt_for_api_key(self):
        """Prompt user to enter Google Maps API key"""
        instructions = (
            "Para usar Google Maps necesita una API Key gratuita:\n\n"
            "1. Vaya a: https://console.cloud.google.com/\n"
            "2. Cree un proyecto nuevo o seleccione uno existente\n"
            "3. Active la API de Google Maps JavaScript\n"
            "4. Vaya a 'Credenciales' y cree una API Key\n"
            "5. (Opcional) Restrinja la key a su dominio/IP\n\n"
            "Ingrese su API Key de Google Maps:"
        )
        
        messagebox.showinfo("Google Maps API Key", instructions)
        
        api_key = simpledialog.askstring(
            "Google Maps API Key",
            "Ingrese su API Key:",
            show='*'  # Hide the key for security
        )
        
        if api_key:
            self.api_key = api_key.strip()
            if self.save_config():
                messagebox.showinfo(
                    "Configuración Guardada",
                    "API Key guardada exitosamente.\nEl mapa se actualizará automáticamente."
                )
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración.")
        else:
            messagebox.showwarning(
                "Sin API Key",
                "Sin API Key, el mapa mostrará un mensaje de error.\n"
                "Puede configurarlo más tarde desde el menú de configuración."
            )
    
    def is_configured(self):
        """Check if API key is configured"""
        return bool(self.api_key)
    
    def reset_config(self):
        """Reset the configuration"""
        self.api_key = ''
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
        except:
            pass

# Global instance
google_maps_config = GoogleMapsConfig()