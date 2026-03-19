import asyncio
import json
import collections
import matplotlib.pyplot as plt
import csv
from datetime import datetime
from bleak import BleakScanner, BleakClient

# --- CONFIG ---
WATCH_NAME = "Bangle.js b5b2"
WATCH_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
MAX_POINTS = 800 
SMOOTHING_WINDOW = 10 

# Data storage
bpm_raw_data = collections.deque([0]*MAX_POINTS, maxlen=MAX_POINTS)
accel_data = collections.deque([1.0]*MAX_POINTS, maxlen=MAX_POINTS)
current_watch_ms = 0  # Raw value from watch
new_data_received = False

# --- CSV LOGGER SETUP ---
# Filename format: data_March_19_2026_143005.csv
timestamp_str = datetime.now().strftime('%B_%d_%Y_%H%M%S')
log_filename = f"data_{timestamp_str}.csv"

csv_file = open(log_filename, mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Timestamp_MS", "Raw_BPM", "Accel_G"]) 

# --- MATPLOTLIB SETUP ---
plt.style.use('dark_background') 
fig, (ax_bpm, ax_accel) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig.subplots_adjust(hspace=0.3, bottom=0.15)

line_bpm, = ax_bpm.plot(range(MAX_POINTS), [0]*MAX_POINTS, color='#00ff00', linewidth=2, animated=True)
ax_bpm.set_ylim(40, 160)
ax_bpm.set_title("Heart Rate (Smoothed BPM)")

line_accel, = ax_accel.plot(range(MAX_POINTS), [1.0]*MAX_POINTS, color='#00ffff', linewidth=2, animated=True)
ax_accel.set_ylim(0, 5.0) 
ax_accel.set_title("Movement (Raw G-Force)")

# Simplified Time Text
time_text = fig.text(0.5, 0.05, "Time (ms)", ha="center", fontsize=12, color="white", animated=True)

plt.show(block=False)
plt.pause(0.1)
bg = None 

def handle_data(sender, raw_bytes):
    global new_data_received, current_watch_ms
    try:
        text = raw_bytes.decode("utf-8").strip()
        # Clean up Bluetooth "mash"
        if "}{" in text:
            text = "{" + text.split("}{")[-1].split("}")[0] + "}"
        
        data = json.loads(text)
        
        # Extract values
        ms = data.get("ms", 0)
        bpm = data.get("bpm", 0)
        acc = float(data.get("accel", 1.0))

        # Update globals
        current_watch_ms = ms
        bpm_raw_data.append(bpm)
        accel_data.append(acc)
        
        # Log to CSV
        csv_writer.writerow([ms, bpm, acc])
        
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
            # Handle Resize/Fullscreen
            if fig.get_size_inches().tolist() != last_size:
                plt.pause(0.1)
                fig.canvas.draw()
                bg = fig.canvas.copy_from_bbox(fig.bbox)
                last_size = fig.get_size_inches().tolist()

            if new_data_received and bg is not None:
                fig.canvas.restore_region(bg)
                
                # Smoothed BPM for graph
                raw_list = list(bpm_raw_data)
                smoothed_bpm = []
                for i in range(len(raw_list)):
                    start = max(0, i - SMOOTHING_WINDOW)
                    chunk = raw_list[start : i + 1]
                    smoothed_bpm.append(sum(chunk) / len(chunk))

                line_bpm.set_ydata(smoothed_bpm)
                line_accel.set_ydata(accel_data)
                
                # Direct display of watch MS
                time_text.set_text(f"Time (ms)")
                
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
    print(f"Data saved to: {log_filename}")

if __name__ == "__main__":
    asyncio.run(main())