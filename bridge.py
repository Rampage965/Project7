import asyncio
import json
import collections
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from bleak import BleakScanner, BleakClient

# --- CONFIG ---
WATCH_ID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
MAX_POINTS = 50  

# Data storage: 'deque' keeps the last 50 readings automatically
bpm_data = collections.deque([80]*MAX_POINTS, maxlen=MAX_POINTS)

# --- MATPLOTLIB SETUP ---
plt.style.use('dark_background') 
fig, ax = plt.subplots()
line, = ax.plot(range(MAX_POINTS), bpm_data, color='#00ff00', linewidth=2)
ax.set_ylim(60, 120) 
ax.set_title("Bangle.js Live Heart Rate")
ax.set_ylabel("BPM")

def handle_data(sender, raw_bytes):
    try:
        # Decode the JSON from the watch
        text = raw_bytes.decode("utf-8").strip()
        data = json.loads(text)
        bpm = data.get("bpm", 0)
        
        # Update the list for the graph
        bpm_data.append(bpm)
        
        # Print to terminal so you know it's working in real-time
        print(f"❤️ Heart Rate: {bpm} BPM")
    except Exception as e:
        pass

def update_plot(frame):
    # This refreshes the line on the screen
    line.set_ydata(bpm_data)
    return line,

async def main():
    print("--- Searching for Bangle.js ---")
    # Original connection logic that worked for you
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and "Bangle" in d.name,
        timeout=10.0
    )
    
    if not device:
        print("Watch not found. Make sure Bluetooth is on and tap the watch screen!")
        return

    async with BleakClient(device) as client:
        print(f"Connected to {device.name}")
        await client.start_notify(WATCH_ID, handle_data)
        
        # THE FIX: This loop keeps Bluetooth alive AND updates the Graph
        while True:
            await asyncio.sleep(0.01) # Let Bluetooth breathe
            plt.pause(0.01)           # Let the Graph draw
            
            # Stop the script if the window is closed
            if not plt.fignum_exists(fig.number):
                print("Window closed. Stopping...")
                break

if __name__ == "__main__":
    # cache_frame_data=False stops the warning you were getting
    ani = FuncAnimation(fig, update_plot, interval=100, blit=True, cache_frame_data=False)
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Stopped: {e}")