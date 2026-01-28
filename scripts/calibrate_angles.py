import socket
import json
import time
import base64
import cv2
import numpy as np
import urllib.request
import urllib.error
import math

# Configuration
ROBOT_IP = "192.168.165.100"
ROBOT_PORT = 9000
HTTP_PORT = 8000

class CalibrationClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        print(f"Connecting to {self.host}:{self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10.0)
        self.sock.connect((self.host, self.port))
        print("Connected.")

    def close(self):
        if self.sock:
            self.sock.close()

    def send_command(self, cmd_dict):
        if not self.sock:
            # Try to reconnect
            try:
                 self.connect()
            except:
                 pass
            if not self.sock:
                print("❌ Not connected")
                return {}
        
        try:
            cmd_str = json.dumps(cmd_dict)
            self.sock.sendall(cmd_str.encode('utf-8'))
            response = self.sock.recv(4096)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            print(f"Socket error: {e}")
            self.sock = None
            return {}

    def capture_image_http(self):
        url = f"http://{self.host}:{HTTP_PORT}/api/v1/capture?format=jpeg"
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data['status'] == 'success':
                        img_bytes = base64.b64decode(data['image_base64'])
                        nparr = np.frombuffer(img_bytes, np.uint8)
                        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            pass # Suppress generic capture errors to avoid spamming console in loop
        return None

    def detect_yolo_http(self):
        url = f"http://{self.host}:{HTTP_PORT}/api/v1/yolo/detect?save_image=false"
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data['status'] == 'success':
                        return data.get('detections', [])
        except Exception:
            pass
        return []

    def set_servos(self, enable=True):
        cmd = "power_on" if enable else "power_off"
        print(f"Sending {cmd}...")
        res = self.send_command({"command": cmd})
        print(f"Result: {res.get('message', 'Unknown')}")

    def get_current_angles(self):
        res = self.send_command({"command": "get_angles"})
        if res.get("status") == "success":
            return res.get("angles", [])
        # Fallback for some server versions asking via 'get_angles' command might return list directly
        # But based on server code read, it returns dict with 'angles' (line 1571)
        # However, line 1401 calls self._cmd_get_angles(cmd)
        # Let's check _cmd_get_angles implementation in memory...
        # It returned {"status": "success", "angles": ...}
        return []

def calculate_stag_quality(corners):
    # corners is list of 4 points [[x,y], [x,y]...]
    pts = np.array(corners, dtype=np.float32)
    
    # 1. Edge lengths
    edges = []
    for i in range(4):
        p1 = pts[i]
        p2 = pts[(i+1)%4]
        edges.append(np.linalg.norm(p1 - p2))
    
    # 2. Aspect Ratio (Should be 1.0 for square)
    # Simple approx: (e0+e2)/2 vs (e1+e3)/2
    w = (edges[0] + edges[2]) / 2.0
    h = (edges[1] + edges[3]) / 2.0
    aspect_ratio = w / h if h > 0 else 0
    if aspect_ratio > 1.0: aspect_ratio = 1.0 / aspect_ratio
    
    # 3. Area
    area = cv2.contourArea(pts)
    
    return aspect_ratio, area

def main():
    client = CalibrationClient(ROBOT_IP, ROBOT_PORT)
    client.connect()
    
    print("\n" + "="*50)
    print("🤖 Robot Arm Angle Calibration Tool")
    print("="*50)
    print("Controls (Focus on the image window):")
    print("  [r] Release Servos (Enter Manual Mode)")
    print("  [f] Focus/Lock Servos (Hold Position)")
    print("  [s] Save Current Angles")
    print("  [q] Quit")
    print("="*50)

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    last_yolo_time = 0
    detections = []
    
    servo_state = "LOCKED" # Assume locked initially

    try:
        while True:
            # 1. Capture
            frame = client.capture_image_http()
            if frame is None:
                print("Waiting for camera...")
                time.sleep(0.5)
                continue

            # 2. YOLO (Rate limited to every 1.0s to save bandwidth)
            if time.time() - last_yolo_time > 1.0:
                detections = client.detect_yolo_http()
                last_yolo_time = time.time()

            # 3. ArUco
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejected = detector.detectMarkers(gray)
            
            # --- Visualization ---
            display_frame = frame.copy()
            
            # Draw Status
            cv2.putText(display_frame, f"Servos: {servo_state}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255) if servo_state=="RELEASED" else (0, 255, 0), 2)

            # Draw YOLO
            for det in detections:
                box = det.get('box', {}) or det.get('bbox', {})
                if box:
                    x, y = int(box.get('x',0)), int(box.get('y',0))
                    w, h = int(box.get('w',0)), int(box.get('h',0))
                    x1, y1 = x - w//2, y - h//2
                    x2, y2 = x + w//2, y + h//2
                    label = f"{det.get('class','?')}: {det.get('confidence',0):.2f}"
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(display_frame, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            # Draw ArUco & Quality
            if ids is not None:
                cv2.aruco.drawDetectedMarkers(display_frame, corners, ids)
                for i in range(len(ids)):
                    c = corners[i][0]
                    center = np.mean(c, axis=0)
                    
                    # Quality Metrics
                    flatness, area = calculate_stag_quality(c)
                    
                    info = f"ID:{ids[i][0]} Flat:{flatness:.2f} px:{int(area)}"
                    cv2.putText(display_frame, info, (int(center[0]), int(center[1])), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    
                    # Console log for better visibility
                    # print(f"Marker {ids[i][0]}: Flatness={flatness:.2f}, Area={area}")

            cv2.imshow("Robot Arm Calibration", display_frame)
            
            # Input Handling
            key = cv2.waitKey(100) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('r'):
                client.set_servos(False)
                servo_state = "RELEASED"
            elif key == ord('f'):
                client.set_servos(True)
                servo_state = "LOCKED"
            elif key == ord('s'):
                angles = client.get_current_angles()
                if angles:
                    print("\n" + "*"*40)
                    print("💾 SAVED ANGLES:")
                    fmt = ", ".join([f"{a:.2f}" for a in angles])
                    print(f"[{fmt}]")
                    # Also format for YAML copy-paste
                    print("YAML Format:")
                    print(f"observe_angles: [{', '.join([f'{a:.1f}' for a in angles])}]")
                    print("*"*40 + "\n")
                else:
                    print("\n❌ Failed to get angles")

    except KeyboardInterrupt:
        pass
    finally:
        client.close()
        cv2.destroyAllWindows()
        print("Calibration Tool Exit.")

if __name__ == "__main__":
    main()
