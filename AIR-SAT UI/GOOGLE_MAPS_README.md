# 🗺️ AIR-SAT Google Maps Integration

This document explains the new Google Maps integration for the AIR-SAT environmental mapping system.

## 🚀 Features

### Real-Time Environmental Mapping
- **GPS Tracking**: Real-time GPS position display with precision indicators
- **Environmental Zones**: Color-coded zones based on air quality data (PM2.5, CO₂, etc.)
- **Track Visualization**: Complete GPS track with time stamps and precision data
- **Waypoint Management**: Interactive waypoints with detailed information
- **Sensor Integration**: Real-time display of all sensor data (SPS30, MQ135, MH-Z19, etc.)

### Interactive Map Features
- **Satellite/Hybrid View**: High-resolution satellite imagery
- **Zoom & Pan**: Full Google Maps interaction
- **Info Windows**: Click on markers for detailed sensor information
- **Auto-Update**: Real-time updates every 5 seconds
- **Precision Circles**: Visual representation of GPS accuracy (HDOP-based)

### Zone Classification
Environmental zones are automatically generated based on sensor readings:

| Zone Color | Air Quality | PM2.5 (µg/m³) | CO₂ (ppm) | Description |
|------------|-------------|---------------|-----------|-------------|
| 🟢 Green   | Good        | ≤ 12          | ≤ 1000    | Safe for outdoor activities |
| 🟡 Yellow  | Moderate    | 13-35         | 1001-2000 | Sensitive groups may experience symptoms |
| 🟠 Orange  | Unhealthy   | 36-55         | 2001-5000 | Everyone may experience health effects |
| 🔴 Red     | Hazardous   | > 55          | > 5000    | Emergency conditions, avoid exposure |

## 📋 Setup Instructions

### 1. Google Maps API Key Setup

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable APIs**:
   - Enable "Maps JavaScript API"
   - Enable "Places API" (optional, for enhanced features)

3. **Create API Key**:
   - Go to "Credentials" → "Create Credentials" → "API Key"
   - Copy your API key

4. **Configure in AIR-SAT**:
   - Run the application
   - Switch to "Google Maps" mode
   - Click "🔑 API Key" button
   - Enter your API key when prompted

5. **Optional Security**:
   - Restrict your API key to your domain/IP for security
   - Set daily usage limits to control costs

### 2. Usage Instructions

1. **Switch to Google Maps Mode**:
   - In the GPS Map tab, change "Map Type" from "Canvas" to "Google Maps"

2. **Configure API Key**:
   - Click "🔑 API Key" and enter your Google Maps API key

3. **Open Interactive Map**:
   - Click "🌐 Open in Browser" to open the full interactive map

4. **Real-Time Monitoring**:
   - GPS position updates automatically
   - Environmental zones appear as you collect data
   - Track points show your movement history

## 🔧 Technical Details

### Architecture
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Data Manager      │    │  Google Maps        │    │   Web Browser       │
│                     │    │  Renderer           │    │                     │
│ • GPS Data          │───▶│                     │───▶│ • Interactive Map   │
│ • Sensor Data       │    │ • HTML Generation   │    │ • Real-time Updates │
│ • Environmental     │    │ • HTTP Server       │    │ • Zone Visualization│
│   Calculations      │    │ • JSON API          │    │ • Precision Circles │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Data Flow
1. **Sensor Data**: Raw GPS and environmental sensor data
2. **Processing**: Data manager calculates air quality zones
3. **Rendering**: Google Maps renderer generates HTML with embedded data
4. **Serving**: Local HTTP server serves the map to the browser
5. **Updates**: Real-time updates via JSON API every 5 seconds

### Files Structure
```
mapping/
├── google_maps_renderer.py     # Main Google Maps integration
├── google_maps_config.py       # API key management
├── gps_map.py                 # Updated to support both modes
├── map_renderer.py            # Original canvas renderer
└── image_handler.py           # Background image support
```

## 🧪 Testing

### Test Script
Run the included test script to verify the integration:

```bash
cd "AIR-SAT UI"
python test_google_maps.py
```

### Test Features
- **Simulated GPS Movement**: Circular movement pattern
- **Environmental Data**: Simulated air quality variations
- **Real-time Updates**: Data changes every 2 seconds
- **Interactive Controls**: Add waypoints, clear track, pause simulation

### Verification Steps
1. ✅ API key configuration works
2. ✅ Map loads in browser
3. ✅ GPS position displays correctly
4. ✅ Environmental zones appear
5. ✅ Track points are visible
6. ✅ Waypoints are interactive
7. ✅ Real-time updates function
8. ✅ Precision circles display

## 🌍 Use Cases

### Environmental Monitoring
- **Air Quality Mapping**: Track pollution levels across different areas
- **Particulate Matter**: Monitor PM2.5 and PM10 concentrations
- **CO₂ Monitoring**: Track carbon dioxide levels
- **Multi-Gas Detection**: Monitor LPG, CO, smoke, NH₄, alcohol

### Scientific Research
- **Data Collection**: Precise GPS tracking with environmental correlation
- **Zone Mapping**: Visual representation of environmental conditions
- **Time-Series Analysis**: Track changes over time
- **Quality Control**: HDOP-based precision indicators

### Emergency Response
- **Hazard Mapping**: Identify dangerous areas quickly
- **Evacuation Planning**: Visual guidance for safe routes
- **Real-time Monitoring**: Immediate updates on changing conditions
- **Documentation**: Automatic track and waypoint logging

## 🔄 Compatibility

### Backward Compatibility
- **Canvas Mode**: Original tkinter canvas rendering still available
- **Data Format**: All existing data formats preserved
- **Export Options**: GPX, CSV, KML, TXT export unchanged
- **API Interface**: Same methods for integration

### Toggle Between Modes
Users can switch between Google Maps and Canvas modes:
- **Google Maps**: For interactive, satellite-based mapping
- **Canvas**: For offline use or systems without API access

## 🛠️ Troubleshooting

### Common Issues

**Map doesn't load**:
- Verify API key is correctly configured
- Check internet connection
- Ensure JavaScript API is enabled in Google Cloud Console

**"For development purposes only" watermark**:
- This appears with unrestricted API keys
- Add domain/IP restrictions to remove watermark
- For local testing, this is normal and can be ignored

**HTTP server port conflicts**:
- The system automatically finds available ports (8765-8775)
- If all ports are busy, restart the application

**Environmental zones not appearing**:
- Ensure sensor data is being received
- Check that PM2.5 and CO₂ values are non-zero
- Verify track points are being generated

### Performance Optimization
- **Zone Count**: System limits to last 10 track points for performance
- **Update Frequency**: 5-second intervals balance real-time vs. performance
- **Data Caching**: Track points cached to reduce server load

## 📝 Future Enhancements

### Planned Features
- **Offline Maps**: Tile caching for offline operation
- **Heat Maps**: Density visualization for environmental data
- **Historical Data**: Time-slider for historical track review
- **Export Integration**: Direct map image export
- **Mobile Support**: Responsive design for mobile devices
- **Custom Markers**: Enhanced marker styles for different data types

### API Extensions
- **Places API**: Location name resolution
- **Directions API**: Route planning and optimization
- **Elevation API**: Terrain profile integration

## 📊 Data Privacy

### Local Processing
- All sensor data processing happens locally
- No environmental data sent to Google servers
- Only GPS coordinates used for map positioning

### API Key Security
- API keys stored locally in encrypted format
- Optional domain/IP restrictions supported
- Usage monitoring available through Google Cloud Console

---

## 🤝 Support

For issues or questions about the Google Maps integration:

1. Check this README for troubleshooting steps
2. Verify your Google Cloud Console configuration
3. Test with the included test script
4. Check the console output for error messages

The integration maintains full compatibility with the existing AIR-SAT system while adding powerful real-time mapping capabilities for environmental monitoring and research applications.