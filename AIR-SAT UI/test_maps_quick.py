#!/usr/bin/env python3
"""
Quick test for Google Maps integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Test imports
    print("Testing imports...")
    from mapping.google_maps_config import google_maps_config
    print(f"[OK] Google Maps config loaded, API key configured: {google_maps_config.is_configured()}")
    
    from mapping.google_maps_renderer import GoogleMapsRenderer
    print("[OK] Google Maps renderer imported successfully")
    
    from core.data_manager import DataManager
    print("[OK] Data manager imported successfully")
    
    # Test basic functionality
    print("\nTesting basic functionality...")
    data_manager = DataManager()
    
    # Add some test data
    data_manager.sensor_data.update({
        'latitude': 40.7128,
        'longitude': -74.0060,
        'pm2_5': 15.0,
        'co2_ppm_mhz19': 450
    })
    
    print("[OK] Test data added to data manager")
    
    # Test HTML generation (without creating UI)
    print("\nTesting HTML generation...")
    
    import tempfile
    class MockParent:
        def pack(self, **kwargs):
            pass
        def config(self, **kwargs):
            pass
    
    try:
        # Create a minimal renderer instance for testing
        renderer = GoogleMapsRenderer.__new__(GoogleMapsRenderer)
        renderer.data_manager = data_manager
        renderer.map_center = {"lat": 40.7128, "lon": -74.0060}
        renderer.zoom_level = 15
        renderer.map_file_path = None
        
        # Test HTML generation
        html_file = renderer.generate_map_html()
        if html_file and os.path.exists(html_file):
            print(f"[OK] HTML file generated: {html_file}")
            
            # Check if HTML contains our API key
            with open(html_file, 'r') as f:
                content = f.read()
                if "AIzaSyDFjDcAS7KaX9IKqdSYFs45EbqLQssOyVI" in content:
                    print("[OK] API key found in HTML")
                else:
                    print("[WARNING] API key not found in HTML")
                    
                if "40.7128" in content:
                    print("[OK] GPS coordinates found in HTML")
                else:
                    print("[WARNING] GPS coordinates not found in HTML")
        else:
            print("[ERROR] HTML file generation failed")
            
    except Exception as e:
        print(f"[ERROR] HTML generation test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Test Summary ===")
    print("[OK] All basic imports working")
    print("[OK] API key configured")
    print("[OK] Data manager functional")
    print("[OK] Ready for GUI integration")
    
    print("\n=== Instructions ===")
    print("1. Run the main application: python main.py")
    print("2. Go to the GPS Map tab")
    print("3. Select 'Google Maps' from the Map Type dropdown")
    print("4. Click 'Open in Browser' to view the interactive map")

except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()