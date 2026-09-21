# Bu kodu direkt terminalden çalıştırmayın! 
# Blender'ı açın, Scripting sekmesine gelin, bu dosyayı orada açıp "Run Script" butonuna basın.


import bpy
import socket
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5051
smooth_factor = 0.15

if "active_timer" in globals() and bpy.app.timers.is_registered(globals()["active_timer"]):
    bpy.app.timers.unregister(globals()["active_timer"])

if "sock" not in globals() or sock is None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass
    
    try:
        sock.bind((UDP_IP, UDP_PORT))
        print("Yeni soket başarıyla bağlandı (Bind).")
    except OSError:
        pass

sock.setblocking(False)

target_object = bpy.data.objects.get("Cube")

def listen_to_mediapipe():
    try:
        data, addr = sock.recvfrom(1024)
        packet = json.loads(data.decode('utf-8'))
        gesture = packet.get("gesture", "Idle") 
        x = packet.get("x", 0.5)
        y = packet.get("y", 0.5)
        
        if target_object:
            
            if gesture == "Pinch":
                target_object.location.x = (x - 0.5) * -10 
                target_object.location.z = (y - 0.5) * -10 
                
                target_object.location.x += (target_x - target_object.location.x) * smooth_factor
                target_object.location.z += (target_z - target_object.location.z) * smooth_factor
                
            elif gesture == "Rotate":
                target_object.rotation_euler[0] = (y - 0.5) * 5  
                target_object.rotation_euler[2] = (x - 0.5) * 5  
                
                target_object.rotation_euler[0] += (target_rot_x - target_object.rotation_euler[0]) * smooth_factor
                target_object.rotation_euler[2] += (target_rot_z - target_object.rotation_euler[2]) * smooth_factor
                
            elif gesture == "Extrude":
                scale_factor = 1.0 + (0.5 - y) * 5 
                if scale_factor < 0.1: scale_factor = 0.1
                target_object.scale = (scale_factor, scale_factor, scale_factor)
                
                current_scale = target_object.scale[0]
                new_scale = current_scale + (target_scale - current_scale) * smooth_factor
                target_object.scale = (new_scale, new_scale, new_scale)
                
            elif gesture == "Idle":
                pass
                
    except Exception:
        pass
        
    return 0.01  

globals()["active_timer"] = listen_to_mediapipe
bpy.app.timers.register(listen_to_mediapipe)

print("Blender LSTM modelinden 4 farklı hareketi dinlemeye hazır!")
