#!/usr/bin/env python3
"""
Script simple para probar el formato de paquetes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from test_lora_packets import generate_test_packets

def test_packet_format():
    packets = generate_test_packets()
    
    for i, packet in enumerate(packets[:2]):
        print(f"=== Paquete {i+1} ===")
        print(f"Raw: {packet}")
        print(f"Partes separadas por coma:")
        
        parts = packet.split(',')
        for j, part in enumerate(parts):
            print(f"  [{j}]: '{part}'")
        
        # Simulación de lo que hace el serial handler
        if packet.startswith("+RCV="):
            packet_data = packet[5:]  # Remover "+RCV="
            rcv_parts = packet_data.split(',')
            print(f"\nAnálisis LoRa:")
            print(f"  Address: {rcv_parts[0] if len(rcv_parts) > 0 else 'N/A'}")
            print(f"  Length: {rcv_parts[1] if len(rcv_parts) > 1 else 'N/A'}")
            if len(rcv_parts) >= 3:
                # El payload debería estar desde la posición 2 hasta antes del RSSI
                payload_start = 2
                # Buscar donde empieza el RSSI (número negativo)
                payload_parts = []
                rssi_snr_parts = []
                found_rssi = False
                
                for k in range(payload_start, len(rcv_parts)):
                    part = rcv_parts[k]
                    # Si encontramos un número que empieza con - y parece ser RSSI
                    if not found_rssi and part.startswith('-') and part[1:].isdigit():
                        found_rssi = True
                        rssi_snr_parts.append(part)
                    elif found_rssi:
                        rssi_snr_parts.append(part)
                    else:
                        payload_parts.append(part)
                
                payload = ','.join(payload_parts)
                print(f"  Payload reconstruido: '{payload}'")
                print(f"  RSSI/SNR: {rssi_snr_parts}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_packet_format()
