# import asyncio
# from bleak import BleakScanner
#
#
# async def main():
#     devices = await BleakScanner.discover()
#     for d in devices:
#         print(d)
#
#
# asyncio.run(main())
#
# import asyncio
# from bleak import BleakClient
#
# address = "94:A9:A8:34:76:66"
# MODEL_NBR_UUID = "538A35C5-5C56-831A-D065-A4993F921DC5"
#
#
# async def main(address):
#     async with BleakClient(address) as client:
#         model_number = await client.read_gatt_char(MODEL_NBR_UUID)
#         print("Model Number: {0}".format("".join(map(chr, model_number))))
#
#
# asyncio.run(main(address))

import asyncio
import threading
import time

from bleak import BleakClient, BleakScanner

par_write_characteristic = "0000ffe1-0000-1000-8000-00805f9b34fb"
send_str = bytearray([0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7B, 0x7D])
dict_move = {'go': '7B 00 00 00 C8 00 00 00 00 B3 7D', 'back': '7B 00 00 FF 38 00 00 00 00 BC 7D',
             'left': '7B 00 00 00 C8 00 00 00 55 E6 7D', 'right': '7B 00 00 00 C8 00 00 FF AB E7 7D',
             'stop': '7B 00 00 00 00 00 00 00 00 7B 7D'}
shared_data = None
data_lock = threading.Lock()


async def connect_to_device(device_address):
    async with BleakClient(device_address) as client:
        try:
            # 连接到蓝牙设备
            await client.connect()
            global shared_data
            while True:
                with data_lock:
                    if shared_data == "STOP":
                        break
                    if shared_data is not None:
                        print(shared_data)
                        global send_str
                        send_str = bytearray.fromhex(dict_move[shared_data].strip())
                        await client.write_gatt_char(par_write_characteristic, send_str)
                        shared_data = None
            await client.disconnect()
        except Exception as e:
            print(e)


def go_to(move):
    global shared_data
    with data_lock:
        shared_data = move


async def main():
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name == "SREPGEAT":
            print(f"Connecting to device: {device.name} ({device.address})")
            await connect_to_device(device.address)


if __name__ == '__main__':
    ble_thread = threading.Thread(target=asyncio.run, args=(main(),))
    ble_thread.start()
    time.sleep(5)





    for a in dict_move:
        print("sending " + a)
        go_to(a)
        time.sleep(5)
    go_to("STOP")

