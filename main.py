import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.interpolate import griddata
import time
import atexit
import os
import cv2

class KalmanFilter:
    def __init__(self, initial_value=-60.0, process_noise=0.3, measurement_noise=2.0, estimate_error=1.0):
        self.q = process_noise         # Process noise
        self.r = measurement_noise     # Measurement noise
        self.p = estimate_error        # Estimate error
        self.x = initial_value         # Initial estimate

    def update(self, measurement):
        self.p += self.q
        k = self.p / (self.p + self.r)
        self.x += k * (measurement - self.x)
        self.p *= (1 - k)
        return self.x


# ======= Serial Port Settings =======
ser = serial.Serial('COM6', 115200)
log_file = open("rssi_log.txt", "a")
atexit.register(lambda: log_file.close())

# ======= Folders for Saving =======
image_folder = "image10x10"
cam_folder = "camera_frames"
os.makedirs(image_folder, exist_ok=True)
os.makedirs(cam_folder, exist_ok=True)

# ======= Grid Setup =======
fig, ax = plt.subplots()
heatmap_data = np.zeros((10, 10))
im = ax.imshow(heatmap_data, cmap='hot', interpolation='nearest', vmin=-70, vmax=-45)
plt.title("Interpolated RSSI Heatmap (10x10)")
plt.colorbar(im, label="RSSI (dBm)")
grid_x, grid_y = np.mgrid[0:1:10j, 0:1:10j]

# ======= Webcam Setup =======
camera = cv2.VideoCapture("http://192.168.1.35:8080/video")

esp_positions = []
first_click_done = False
first_frame_saved = False

# ======= Mouse Click Handler =======
def mouse_click(event, x, y, flags, param):
    global esp_positions
    if event == cv2.EVENT_LBUTTONDOWN and len(esp_positions) < 4:
        esp_positions.append((x, y))
        print(f"[+] Marked ESP{len(esp_positions)} at ({x}, {y})")

cv2.namedWindow("Click ESP Positions", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Click ESP Positions", 1920, 1080)
cv2.setMouseCallback("Click ESP Positions", mouse_click)

# ======= Kalman Filter Instances (1 per ESP) =======
# Kalman filters with better starting values
kalman_filters = [KalmanFilter(initial_value=-60.0) for _ in range(4)]


# ======= Main Update Function =======
def update(frame):
    global first_click_done, esp_positions, first_frame_saved

    try:
        line = ser.readline().decode().strip()
        raw_rssi_values = list(map(int, line.split(',')))
        if len(raw_rssi_values) != 4:
            return [im]

        # Filter RSSI
        filtered_rssi = [kalman_filters[i].update(raw_rssi_values[i]) for i in range(4)]
        filtered_rssi_int = list(map(int, filtered_rssi))

        # Timestamp
        timestamp = time.strftime('%H-%M-%S')
        timestamp_label = f"[{time.strftime('%M:%S')}]"

        # Log data
        log_entry = f"{timestamp_label} RSSI Values:\n"
        for i in range(4):
            log_entry += f"ESP{i+1} Raw: {raw_rssi_values[i]}, Filtered: {filtered_rssi_int[i]}\n"
        log_entry += "-" * 20 + "\n"
        print(log_entry, end="")
        log_file.write(log_entry)
        log_file.flush()

        # Interpolation for heatmap
        points = np.array([
            [0, 0],   # ESP1 (top-left)
            [1, 0],   # ESP2 (bottom-left)
            [0, 1],   # ESP3 (top-right)
            [1, 1]    # ESP4 (bottom-right)
        ])
        values = np.array(filtered_rssi_int)
        grid_rssi = griddata(points, values, (grid_x, grid_y), method='linear')
        im.set_data(grid_rssi)

        # Detect strongest signal (filtered)
        strongest_index = int(np.argmax(np.abs(filtered_rssi)))+ 1
        signal_label = f"ESP{strongest_index}"

        # Save heatmap image
        heatmap_filename = f"heatmap_{timestamp}_{signal_label}.png"
        heatmap_path = os.path.join(image_folder, heatmap_filename)
        plt.savefig(heatmap_path)
        print(f"[+] Saved heatmap: {heatmap_path}")

        # Capture webcam frame
        ret, frame = camera.read()
        if ret:
            if not first_click_done:
                if not first_frame_saved:
                    cv2.imwrite("first_frame.jpg", frame)
                    first_frame_saved = True
                    print("[*] First camera frame saved. Click to label ESP1–ESP4.")

                while len(esp_positions) < 4:
                    cv2.imshow("Click ESP Positions", frame)
                    if cv2.waitKey(1) & 0xFF == 27:
                        break
                if len(esp_positions) == 4:
                    print("[✓] ESP positions set.")
                    first_click_done = True
                    cv2.destroyWindow("Click ESP Positions")

            # Draw ESP markers
            for i, (x, y) in enumerate(esp_positions):
                cv2.circle(frame, (x, y), 10, (0, 0, 255), -1)
                cv2.putText(frame, f"ESP{i+1}", (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 1, cv2.LINE_AA)

            # Save camera frame with label
            cam_filename = f"cam_{timestamp}_{signal_label}.jpg"
            cam_path = os.path.join(cam_folder, cam_filename)
            cv2.imwrite(cam_path, frame)
            print(f"[+] Saved camera frame: {cam_path}")
        else:
            print("[!] Failed to read webcam frame.")

    except Exception as e:
        print("Error:", e)

    return [im]

# ======= Animation Setup =======
ani = animation.FuncAnimation(fig, update, interval=100, cache_frame_data=False)
plt.show()

camera.release()
log_file.write("End of log\n")
