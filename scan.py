import asyncio
from bleak import BleakScanner, BleakClient

async def run():
    print("Searching for Bangle...")
    device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name and "Bangle" in d.name)
    if device:
        async with BleakClient(device) as client:
            print(f"Connected to {device.name}")
            for service in client.services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"  - Characteristic: {char.uuid} ({','.join(char.properties)})")

asyncio.run(run())