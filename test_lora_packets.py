#!/usr/bin/env python3
"""
Script de prueba para el nuevo formato de paquetes LoRa
Simula la llegada de diferentes tipos de paquetes desde el CanSat
"""

import time
import random

def generate_test_packets():
    """Genera paquetes de prueba simulando datos reales del CanSat"""
    
    seq_id = random.randint(1, 1000)
    timestamp = int(time.time() * 1000) % 1000000  # Timestamp simulado
    
    packets = []
    
    # P1 - GPS + Sistema
    lat = 19.4326 + random.uniform(-0.001, 0.001)  # Simular México DF
    lon = -99.1332 + random.uniform(-0.001, 0.001)
    alt = 2240 + random.uniform(-10, 50)  # Altitud de México DF + variación
    speed = random.uniform(0, 5)  # km/h
    sats = random.randint(4, 12)
    fix_qual = 3 if sats >= 6 else 2 if sats >= 4 else 1
    course = random.uniform(0, 360)
    hdop = random.uniform(1.0, 3.0)
    status_mask = 63  # Todos los sensores activos (0x3F)
    
    p1_payload = f"P1,{seq_id},{timestamp},{lat:.6f},{lon:.6f},{alt:.1f},{speed:.1f},{sats},{fix_qual},{course:.1f},{hdop:.2f},{status_mask}"
    packets.append(f"+RCV=12,{len(p1_payload)},{p1_payload},-{random.randint(30, 80)},{random.uniform(5, 15):.1f}")
    
    # P2 - GY91 Básico (BMP280 + Acelerómetro)
    temp_bmp = random.uniform(20, 35)  # °C
    pressure = random.uniform(750, 850)  # mbar (altitud México DF)
    alt_bmp = alt + random.uniform(-5, 5)  # Altitud barométrica
    temp_mpu = temp_bmp + random.uniform(-2, 5)  # MPU suele estar más caliente
    accel_x = random.uniform(-0.1, 0.1)  # g
    accel_y = random.uniform(-0.1, 0.1)  # g
    accel_z = random.uniform(0.9, 1.1)  # g (gravedad + ruido)
    total_accel = (accel_x**2 + accel_y**2 + accel_z**2)**0.5
    
    p2_payload = f"P2,{seq_id},{timestamp},{temp_bmp:.2f},{pressure:.2f},{alt_bmp:.1f},{temp_mpu:.1f},{accel_x:.3f},{accel_y:.3f},{accel_z:.3f},{total_accel:.3f}"
    packets.append(f"+RCV=12,{len(p2_payload)},{p2_payload},-{random.randint(30, 80)},{random.uniform(5, 15):.1f}")
    
    # P3 - MPU9250 Extendido (Giroscopio + Magnetómetro)
    gyro_x = random.uniform(-1, 1)  # dps
    gyro_y = random.uniform(-1, 1)  # dps
    gyro_z = random.uniform(-1, 1)  # dps
    mag_x = random.uniform(0, 10)  # µT
    mag_y = random.uniform(0, 10)  # µT
    mag_z = random.uniform(-20, 0)  # µT (componente vertical)
    roll = random.uniform(-5, 5)  # grados
    pitch = random.uniform(-5, 5)  # grados
    yaw = random.uniform(0, 360)  # grados
    heading = yaw  # Rumbo magnético
    
    p3_payload = f"P3,{seq_id},{timestamp},{gyro_x:.2f},{gyro_y:.2f},{gyro_z:.2f},{mag_x:.1f},{mag_y:.1f},{mag_z:.1f},{roll:.2f},{pitch:.2f},{yaw:.2f},{heading:.1f}"
    packets.append(f"+RCV=12,{len(p3_payload)},{p3_payload},-{random.randint(30, 80)},{random.uniform(5, 15):.1f}")
    
    # P4 - SPS30 (Sensor de Partículas)
    pm1_0 = random.uniform(5, 15)  # µg/m³
    pm2_5 = pm1_0 + random.uniform(2, 8)  # µg/m³
    pm4_0 = pm2_5 + random.uniform(1, 3)  # µg/m³
    pm10 = pm4_0 + random.uniform(1, 5)  # µg/m³
    nc0_5 = random.uniform(40, 60)  # #/cm³
    nc1_0 = nc0_5 + random.uniform(5, 15)  # #/cm³
    nc2_5 = nc1_0 + random.uniform(2, 8)  # #/cm³
    nc4_0 = nc2_5 + random.uniform(0, 2)  # #/cm³
    nc10 = nc4_0 + random.uniform(0, 1)  # #/cm³
    size = random.uniform(0.4, 0.6)  # µm
    
    p4_payload = f"P4,{seq_id},{timestamp},{pm1_0:.2f},{pm2_5:.2f},{pm4_0:.2f},{pm10:.2f},{nc0_5:.1f},{nc1_0:.1f},{nc2_5:.1f},{nc4_0:.1f},{nc10:.1f},{size:.2f}"
    packets.append(f"+RCV=12,{len(p4_payload)},{p4_payload},-{random.randint(30, 80)},{random.uniform(5, 15):.1f}")
    
    # P5 - MQ135 (Calidad del Aire)
    lpg = random.uniform(10, 20)  # ppm
    co = random.uniform(100, 200)  # ppm
    smoke = random.uniform(50, 100)  # ppm
    nh4 = random.uniform(20, 40)  # ppm
    co2_mq = random.uniform(400, 600)  # ppm
    alcohol = random.uniform(15, 25)  # ppm
    ro = random.uniform(1.5, 2.0)  # Valor Ro
    sys_tick = timestamp + 1000
    
    p5_payload = f"P5,{seq_id},{timestamp},{lpg:.1f},{co:.1f},{smoke:.1f},{nh4:.1f},{co2_mq:.1f},{alcohol:.1f},{ro:.2f},{sys_tick}"
    packets.append(f"+RCV=12,{len(p5_payload)},{p5_payload},-{random.randint(30, 80)},{random.uniform(5, 15):.1f}")
    
    # P6 - MH-Z19 (CO₂)
    co2_ppm = random.randint(400, 1500)  # ppm
    temp_mhz = temp_bmp + random.uniform(0, 5)  # °C
    range_val = 5000  # ppm
    status = random.choice(['R', 'R', 'R', 'W'])  # Mostly Ready
    warmed = 'Y' if status == 'R' else random.choice(['Y', 'N'])
    sys_tick = timestamp + 2000
    
    p6_payload = f"P6,{seq_id},{timestamp},{co2_ppm},{temp_mhz:.1f},{range_val},{status},{warmed},{sys_tick}"
    packets.append(f"+RCV=12,{len(p6_payload)},{p6_payload},-{random.randint(30, 80)},{random.uniform(5, 15):.1f}")
    
    return packets

def simulate_cansat_transmission():
    """Simula la transmisión de datos del CanSat"""
    print("🛰️  Simulador de Transmisión CanSat - Nuevo Formato de Paquetes")
    print("=" * 80)
    print("Formato: +RCV=ADDRESS,LENGTH,PAYLOAD,-RSSI,SNR")
    print("Tipos de paquetes: P1(GPS), P2(GY91), P3(MPU), P4(SPS30), P5(MQ135), P6(MHZ19)")
    print("=" * 80)
    
    cycle = 1
    try:
        while True:
            print(f"\n🔄 Ciclo de transmisión #{cycle}")
            print("-" * 40)
            
            packets = generate_test_packets()
            
            for i, packet in enumerate(packets, 1):
                print(f"📦 Paquete {i}/6: {packet}")
                time.sleep(0.5)  # Simular intervalo entre paquetes
            
            print(f"✅ Ciclo #{cycle} completado")
            cycle += 1
            
            # Pausa entre ciclos
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Simulación detenida por el usuario")
        print("Gracias por usar el simulador CanSat!")

def decode_packet_info(packet):
    """Decodifica y muestra información detallada de un paquete"""
    try:
        # Extraer componentes del paquete LoRa
        if not packet.startswith("+RCV="):
            return "❌ Formato inválido"
        
        packet_data = packet[5:]  # Remover "+RCV="
        parts = packet_data.split(',')
        
        if len(parts) < 5:
            return "❌ Paquete incompleto"
        
        address = parts[0]
        length = int(parts[1])
        payload = parts[2]
        rssi = int(parts[3])
        snr = float(parts[4])
        
        info = f"📡 Dirección: {address}, Longitud: {length}, RSSI: {rssi}dBm, SNR: {snr}dB\n"
        
        # Decodificar payload según tipo
        payload_parts = payload.split(',')
        packet_type = payload_parts[0]
        
        if packet_type == "P1":
            info += "🛰️  P1 - GPS + Sistema\n"
            info += f"   📍 Lat: {payload_parts[3]}°, Lon: {payload_parts[4]}°\n"
            info += f"   🏔️  Alt: {payload_parts[5]}m, Vel: {payload_parts[6]}km/h\n"
            info += f"   🛰️  Satélites: {payload_parts[7]}, Fix: {payload_parts[8]}\n"
        elif packet_type == "P2":
            info += "📊 P2 - GY91 Básico (BMP280 + Acel)\n"
            info += f"   🌡️  Temp BMP: {payload_parts[3]}°C, Presión: {payload_parts[4]}mbar\n"
            info += f"   🎯 Aceleración total: {payload_parts[10]}g\n"
        elif packet_type == "P3":
            info += "🧭 P3 - MPU9250 Extendido (Gyro + Mag)\n"
            info += f"   🔄 Orientación: R{payload_parts[9]}° P{payload_parts[10]}° Y{payload_parts[11]}°\n"
            info += f"   🧭 Rumbo: {payload_parts[12]}°\n"
        elif packet_type == "P4":
            info += "💨 P4 - SPS30 (Partículas)\n"
            info += f"   ⚖️  PM2.5: {payload_parts[4]}µg/m³, PM10: {payload_parts[6]}µg/m³\n"
        elif packet_type == "P5":
            info += "🌫️  P5 - MQ135 (Gases)\n"
            info += f"   🚨 CO: {payload_parts[4]}ppm, CO₂: {payload_parts[7]}ppm\n"
        elif packet_type == "P6":
            info += "🏭 P6 - MH-Z19 (CO₂ NDIR)\n"
            info += f"   💨 CO₂: {payload_parts[3]}ppm, Estado: {payload_parts[6]}\n"
        
        return info
        
    except Exception as e:
        return f"❌ Error decodificando: {str(e)}"

def test_packet_decoding():
    """Prueba la decodificación de paquetes"""
    print("🔍 Prueba de Decodificación de Paquetes")
    print("=" * 50)
    
    test_packets = generate_test_packets()
    
    for i, packet in enumerate(test_packets, 1):
        print(f"\n📦 Paquete {i}:")
        print(f"Raw: {packet}")
        print(decode_packet_info(packet))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "decode":
        test_packet_decoding()
    else:
        simulate_cansat_transmission()
