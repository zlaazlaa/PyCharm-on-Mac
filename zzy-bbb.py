# -*- coding: utf-8 -*-
import asyncio
import binascii
import threading

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

# 设备的Characteristic UUID
par_notification_characteristic = "0000ffe1-0000-1000-8000-00805f9b34fb"
# 设备的MAC地址
par_device_addr = "94:A9:A8:34:76:66"
par_write_characteristic = "0000ffe1-0000-1000-8000-00805f9b34fb"

# 7B 00 00 00 C8 00 00 00 00 B3 7D
send_str = bytearray([0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7B, 0x7D])

dict_move = {'go': '7B 00 00 00 C8 00 00 00 00 B3 7D', 'back': '7B 00 00 FF 38 00 00 00 00 BC 7D',
             'left': '7B 00 00 00 C8 00 00 00 55 E6 7D', 'right': '7B 00 00 00 C8 00 00 FF AB E7 7D', \
             'stop': '7B 00 00 00 00 00 00 00 00 7B 7D'}


# 监听回调函数，此处为打印消息
def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    hex_data = binascii.hexlify(data).decode('utf-8')
    # print("rev data:",hex_data)


async def ble_connect():
    print("starting scan...")

    # 基于MAC地址查找设备
    device = await BleakScanner.find_device_by_address(
        par_device_addr, cb=dict(use_bdaddr=False)  # use_bdaddr判断是否是MOC系统
    )
    if device is None:
        print("could not find device with address '%s'", par_device_addr)
        return

    # 事件定义
    disconnected_event = asyncio.Event()

    # 断开连接事件回调
    def disconnected_callback(client):
        print("Disconnected callback called!")
        disconnected_event.set()

    print("connecting to device...")
    async with BleakClient(device, disconnected_callback=disconnected_callback) as client:
        print("Connected")
        await client.connect()
        while True:
            await client.write_gatt_char(par_write_characteristic, send_str)
            await asyncio.sleep(0.5)  # 每休眠1秒发送一次


def change_move(data):
    global send_str
    try:
        send_str = bytearray.fromhex(dict_move[data].strip())
        print('OK')
    except KeyError:
        print("Invalid input. Please enter a valid hexadecimal string.")


if __name__ == '__main__':
    ble_thread = threading.Thread(target=asyncio.run, args=(ble_connect(),))
    ble_thread.start()
    print("111")
    change_move('go')
