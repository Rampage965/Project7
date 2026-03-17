import json
import time
import random

def simulate_watch():
    print("--- Starting Watch Simulation ---")
    while True:
        # Simulate a random heart rate and a random confidence score
        bpm = random.randint(60, 110)
        conf = random.randint(50, 100) # Some will be low (noise), some high
        
        data = {"type": "HRM", "bpm": bpm, "conf": conf}
        
        if conf >= 80:
            print(f"Sending Valid Data: {bpm} BPM")
        else:
            print(f"Filtering Noise: Low confidence ({conf}%)")
            
        time.sleep(1) # Send every second just like the real watch

if __name__ == "__main__":
    simulate_watch()