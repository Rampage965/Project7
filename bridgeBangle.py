import asyncio
import json
import collections
import matplotlib.pyplot as plt
import csv
import time
from datetime import datetime
from bleak import BleakScanner, BleakClient

# --- CONFIGURATION ---
WATCH_NAME = "Bangle.js b5b2"
WATCH_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
MAX_POINTS = 800 

# Data storage
bpm_raw_data = collections.deque([0]*MAX_POINTS, maxlen=MAX_POINTS)
accel_data = collections.deque([1.0]*MAX_POINTS, maxlen=MAX_POINTS)
start_time = time.time()  
new_data_received = False

# --- CSV LOGGER SETUP ---
timestamp_str = datetime.now().strftime('%B_%d_%Y_%H%M%S')
log_filename = f"data_{timestamp_str}.csv"

csv_file = open(log_filename, mode='w', newline='', buffering=1)
csv_writer = csv.writer(csv_file)

# Clean Table Headers
csv_writer.writerow(["Time_Sec", "Raw_BPM", "BPM_Status", "Accel_G", "Motion_Status"]) 

# --- MATPLOTLIB SETUP ---
plt.style.use('dark_background') 
fig, (ax_bpm, ax_accel) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig.subplots_adjust(hspace=0.3, bottom=0.15)

# Heart Rate Plot
line_bpm, = ax_bpm.plot(range(MAX_POINTS), [0]*MAX_POINTS, color='#00ff00', linewidth=2, animated=True)
ax_bpm.set_ylim(40, 160)
ax_bpm.set_title("Heart Rate (Raw BPM)")
ax_bpm.axhline(y=100, color='red', linestyle='--', alpha=0.7) # High Stress Line

# Movement Plot
line_accel, = ax_accel.plot(range(MAX_POINTS), [1.0]*MAX_POINTS, color='#00ffff', linewidth=2, animated=True)
ax_accel.set_ylim(0, 5.0) 
ax_accel.set_title("Movement (Raw G-Force)")
ax_accel.axhline(y=1.5, color='red', linestyle='--', alpha=0.7) # High Motion Threshold
ax_accel.axhline(y=0.5, color='red', linestyle='--', alpha=0.7) # Low Motion Threshold

time_text = fig.text(0.5, 0.05, "Elapsed Time (Seconds)", ha="center", fontsize=12, color="white", animated=True)

plt.show(block=False)
plt.pause(0.1)
bg = None 

def handle_data(sender, raw_bytes):
    global new_data_received
    try:
        text = raw_bytes.decode("utf-8").strip()
        if "}{" in text:
            text = "{" + text.split("}{")[-1].split("}")[0] + "}"
        
        data = json.loads(text)
        
        elapsed_seconds = round(time.time() - start_time, 3)
        bpm = data.get("bpm", 0)
        acc = float(data.get("accel", 1.0))

        # Heart Rate Status
        if bpm > 100: bpm_status = "STRESS  "
        elif bpm > 85: bpm_status = "MODERATE"
        else:          bpm_status = "NORMAL  "

        # Motion Status (Updated Wording)
        diff = abs(acc - 1.0)
        if diff > 0.5: mov_status = "HIGH_MOTION"
        elif diff > 0.1: mov_status = "LOW_MOTION "
        else:          mov_status = "STILL      "

        bpm_raw_data.append(bpm)
        accel_data.append(acc)
        
        # Log to CSV with formatted spacing
        csv_writer.writerow([
            f"{elapsed_seconds:10.3f}", 
            f"{bpm:8}", 
            f"{bpm_status:10}", 
            f"{acc:8.3f}", 
            f"{mov_status:12}"
        ])
        csv_file.flush() 
        
        new_data_received = True
    except:
        pass 

async def main():
    global bg, new_data_received
    print(f"Connecting to {WATCH_NAME}...")
    device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name and WATCH_NAME in d.name, timeout=10.0)
    
    if not device:
        print("Watch not found!")
        return

    async with BleakClient(device) as client:
        await client.start_notify(WATCH_UUID, handle_data)
        
        fig.canvas.draw()
        bg = fig.canvas.copy_from_bbox(fig.bbox)
        last_size = fig.get_size_inches().tolist()

        while True:
            if fig.get_size_inches().tolist() != last_size:
                plt.pause(0.1)
                fig.canvas.draw()
                bg = fig.canvas.copy_from_bbox(fig.bbox)
                last_size = fig.get_size_inches().tolist()

            if new_data_received and bg is not None:
                fig.canvas.restore_region(bg)
                
                line_bpm.set_ydata(list(bpm_raw_data))
                line_accel.set_ydata(list(accel_data))
                
                ax_bpm.draw_artist(line_bpm)
                ax_accel.draw_artist(line_accel)
                fig.draw_artist(time_text)
                
                fig.canvas.blit(fig.bbox)
                fig.canvas.flush_events()
                new_data_received = False
            
            await asyncio.sleep(0.005)
            if not plt.fignum_exists(fig.number):
                break

    csv_file.close()
    print(f"Final Data saved to: {log_filename}")

if __name__ == "__main__":
    asyncio.run(main())