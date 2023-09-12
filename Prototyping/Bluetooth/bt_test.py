import asyncio
from bleak import BleakScanner
from bleak import BleakClient
import sys
from bleak import BleakError

async def main(loop):
    wanted_name = "CAR20"
    
    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_rx(_: int, data: bytearray):
        print(data.decode())
    
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and d.name.lower() == wanted_name.lower()
    )
    print(device)
    if not device:
        raise BleakError(f"{wanted_name} could not be found.")
    async with BleakClient(device, loop=loop) as client:
        svcs = await client.get_services()
        uuid=None
        for service in svcs:
            for c in service.characteristics:
                if(c.description == "DSD TECH"): uuid=c.uuid
        
        await client.start_notify(uuid, handle_rx)

        print("Connected, start typing and press ENTER...")

        loop = asyncio.get_running_loop()

        while True:
            # This waits until you type a line and press ENTER.
            # A real terminal program might put stdin in raw mode so that things
            # like CTRL+C get passed to the remote device.
            data = await loop.run_in_executor(None, sys.stdin.buffer.readline)

            # data will be empty on EOF (e.g. CTRL+D on *nix)
            if not data:
                break

            # some devices, like devices running MicroPython, expect Windows
            # line endings (uncomment line below if needed)
            # data = data.replace(b"\n", b"\r\n")

            await client.write_gatt_char(uuid, data)
            #print("sent:", data)

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))