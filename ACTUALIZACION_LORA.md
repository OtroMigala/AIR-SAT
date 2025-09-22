# Actualización Sistema AIR-SAT - Nuevo Formato de Paquetes LoRa

## 📡 Resumen de Cambios

El sistema AIR-SAT ha sido actualizado para manejar el nuevo formato de transmisión por paquetes LoRa. Ahora cada tipo de sensor envía datos en paquetes independientes con información específica.

## 🔄 Formato de Comunicación

### Formato General de Recepción LoRa
```
+RCV=ADDRESS,LENGTH,PAYLOAD,-RSSI,SNR
```

**Componentes:**
- `+RCV` = Indicador de paquete recibido
- `ADDRESS` = Dirección del transmisor (12)
- `LENGTH` = Longitud del payload en bytes
- `PAYLOAD` = Datos del paquete específico
- `RSSI` = Fuerza de señal (dBm, negativo)
- `SNR` = Relación señal/ruido (dB)

## 📦 Tipos de Paquetes

### P1 - GPS + Sistema
```
P1,SEQ_ID,TIMESTAMP,LAT,LON,ALT,SPEED,SATS,FIX_QUAL,COURSE,HDOP,STATUS_MASK
```
**Ejemplo:**
```
+RCV=12,67,P1,79,835418,19.432600,-99.133200,2240.5,2.3,8,3,45.2,1.85,63,-45,12.5
```

**Campos:**
- `SEQ_ID`: ID de secuencia del paquete
- `TIMESTAMP`: Timestamp del sistema (ms)
- `LAT,LON`: Coordenadas GPS (grados decimales)
- `ALT`: Altitud GPS (metros)
- `SPEED`: Velocidad (km/h)
- `SATS`: Número de satélites
- `FIX_QUAL`: Calidad de fix GPS (0=Sin fix, 1=2D, 2=3D, 3=DGPS)
- `COURSE`: Rumbo (grados)
- `HDOP`: Dilución horizontal de precisión
- `STATUS_MASK`: Máscara de estado de sensores (bitmask)

### P2 - GY91 Básico (BMP280 + Acelerómetro)
```
P2,SEQ_ID,TIMESTAMP,TEMP_BMP,PRESSURE,ALT_BMP,TEMP_MPU,ACCEL_X,ACCEL_Y,ACCEL_Z,TOTAL_ACCEL
```
**Ejemplo:**
```
+RCV=12,59,P2,79,835418,28.17,831.75,2239.8,32.4,-0.052,0.013,0.998,1.00,-42,11.8
```

### P3 - MPU9250 Extendido (Giroscopio + Magnetómetro)
```
P3,SEQ_ID,TIMESTAMP,GYRO_X,GYRO_Y,GYRO_Z,MAG_X,MAG_Y,MAG_Z,ROLL,PITCH,YAW,HEADING
```
**Ejemplo:**
```
+RCV=12,61,P3,79,835418,-0.04,-0.05,0.04,4.1,6.0,-15.0,0.76,2.96,58.01,58.0,-38,9.2
```

### P4 - SPS30 (Sensor de Partículas)
```
P4,SEQ_ID,TIMESTAMP,PM1.0,PM2.5,PM4.0,PM10,NC0.5,NC1.0,NC2.5,NC4.0,NC10,SIZE
```
**Ejemplo:**
```
+RCV=12,69,P4,79,835418,6.61,8.99,8.99,9.45,44.9,52.6,52.8,52.8,52.8,0.46,-41,8.7
```

**Campos:**
- `PM1.0,PM2.5,PM4.0,PM10`: Concentraciones de masa (µg/m³)
- `NC0.5,NC1.0,NC2.5,NC4.0,NC10`: Concentraciones numéricas (#/cm³)
- `SIZE`: Tamaño típico de partícula (µm)

### P5 - MQ135 (Calidad del Aire)
```
P5,SEQ_ID,TIMESTAMP,LPG,CO,SMOKE,NH4,CO2,ALCOHOL,RO,SYS_TICK
```
**Ejemplo:**
```
+RCV=12,57,P5,79,835418,15.2,178.8,67.8,27.3,450.9,19.4,1.61,841906,-44,7.3
```

**Campos:**
- `LPG,CO,SMOKE,NH4,CO2,ALCOHOL`: Concentraciones de gases (ppm)
- `RO`: Valor de calibración Ro
- `SYS_TICK`: Timestamp del sistema

### P6 - MH-Z19 (CO₂ NDIR)
```
P6,SEQ_ID,TIMESTAMP,CO2_PPM,TEMP,RANGE,STATUS,WARMED,SYS_TICK
```
**Ejemplo:**
```
+RCV=12,48,P6,78,825389,1187,38.0,5000,R,Y,833499,-39,10.5
```

**Campos:**
- `CO2_PPM`: Concentración CO₂ (ppm)
- `TEMP`: Temperatura del sensor (°C)
- `RANGE`: Rango configurado (0-5000 ppm)
- `STATUS`: Estado (R=Ready, W=Warming, E=Error)
- `WARMED`: Sensor calentado (Y=Yes, N=No)

## 🎯 Máscara de Estado de Sensores (P1)

```c
#define SENSOR_STATUS_GPS      0x01  // Bit 0
#define SENSOR_STATUS_GY91     0x02  // Bit 1  
#define SENSOR_STATUS_SPS30    0x04  // Bit 2
#define SENSOR_STATUS_MQ135    0x08  // Bit 3
#define SENSOR_STATUS_LORA     0x10  // Bit 4
#define SENSOR_STATUS_MHZ19    0x20  // Bit 5
```

**Ejemplo:** `63 = 0x3F` = Todos los sensores activos

## 🔧 Cambios en el Código

### 1. hardware/serial_handler.py
- ✅ Nuevo método `_process_lora_packet()` para manejar formato `+RCV`
- ✅ Compatibilidad con formato anterior (`DATA:`)
- ✅ Extracción de RSSI y SNR de comunicación LoRa

### 2. core/data_manager.py
- ✅ Nuevas estructuras de datos para sensores adicionales:
  - `sps30_data` (SPS30 - Partículas)
  - `mq135_data` (MQ135 - Gases)
  - `mhz19_data` (MH-Z19 - CO₂)
  - `lora_data` (Información de comunicación)
- ✅ Métodos de parseo específicos:
  - `parse_packet_p1()` - GPS + Sistema
  - `parse_packet_p2()` - GY91 Básico
  - `parse_packet_p3()` - MPU9250 Extendido
  - `parse_packet_p4()` - SPS30 Partículas
  - `parse_packet_p5()` - MQ135 Gases
  - `parse_packet_p6()` - MH-Z19 CO₂
- ✅ Método `decode_sensor_status_mask()` para interpretar estado
- ✅ Método `get_air_quality_index()` para índice de calidad del aire

### 3. ui/realtime_monitor.py
- ✅ Interfaz reorganizada en pestañas:
  - **🛰️ GPS + GY91**: Sensores básicos originales
  - **🌬️ Calidad Aire**: SPS30, MQ135, MH-Z19
  - **📡 Comunicación**: LoRa, estado de sensores
- ✅ Nuevos displays para todos los sensores
- ✅ Indicadores visuales de calidad de señal LoRa
- ✅ Estado en tiempo real de cada sensor
- ✅ Índice de calidad del aire

## 🧪 Pruebas

### Ejecutar Simulador de Paquetes
```bash
python test_lora_packets.py
```

### Probar Decodificación
```bash
python test_lora_packets.py decode
```

## 📊 Nuevas Funcionalidades

### 1. Monitoreo de Calidad del Aire
- **PM1.0, PM2.5, PM10**: Concentraciones de partículas
- **Gases tóxicos**: CO, NH₄, humo, alcohol
- **CO₂ preciso**: Sensor NDIR MH-Z19
- **Índice de calidad**: BUENA, MODERADA, MALA, PELIGROSA

### 2. Comunicación LoRa
- **RSSI**: Indicador de fuerza de señal
- **SNR**: Relación señal/ruido
- **Estadísticas de paquetes**: Secuencia, timestamps
- **Estado de sensores**: Indicadores visuales en tiempo real

### 3. Compatibilidad
- ✅ **Retrocompatible** con formato anterior `DATA:`
- ✅ **Todas las funciones originales** mantenidas
- ✅ **Mapas GPS** funcionan igual
- ✅ **Gráficas** incluyen nuevos sensores

## 🚀 Beneficios

1. **Modularidad**: Cada sensor envía datos independientes
2. **Escalabilidad**: Fácil agregar nuevos tipos de paquetes
3. **Robustez**: Pérdida de un paquete no afecta otros sensores
4. **Información rica**: RSSI, SNR, timestamps del sistema
5. **Monitoreo ambiental**: Calidad del aire completa
6. **Diagnóstico**: Estado individual de cada sensor

## 📈 Próximos Pasos

1. **Logging avanzado**: Guardar datos por tipo de sensor
2. **Alertas**: Notificaciones por calidad del aire
3. **Gráficas específicas**: Plots para nuevos sensores
4. **Exportación**: CSV con datos de todos los sensores
5. **Configuración**: Parámetros ajustables por sensor

---

**Versión**: 2.0 - Formato Paquetes LoRa  
**Fecha**: Septiembre 2025  
**Compatibilidad**: Python 3.8+, CustomTkinter 5.0+
