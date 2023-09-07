# -*- coding: utf-8 -*-
import asyncio
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

#设备的Characteristic UUID
par_notification_characteristic="0000ffe1-0000-1000-8000-00805f9b34fb"
#设备的Characteristic UUID（具备写属性Write）
par_write_characteristic="0000ffe1-0000-1000-8000-00805f9b34fb"
#设备的MAC地址
par_device_addr="94:A9:A8:34:76:66"

#准备发送的消息，为“hi world\n”的HEX形式（包括回车符0x0A 0x0D）
send_str=bytearray([0x68,0x69,0x20,0x77,0x6F,0x72,0x6C,0x64,0x0A,0x0D])

#监听回调函数，此处为打印消息
def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    print("rev data:",data)

async def main():
    print("starting scan...")

    #基于MAC地址查找设备
    device = await BleakScanner.find_device_by_address(
        par_device_addr, cb=dict(use_bdaddr=False)  #use_bdaddr判断是否是MOC系统
    )
    if device is None:
        print("could not find device with address '%s'", par_device_addr)
        return

    #事件定义
    disconnected_event = asyncio.Event()

    #断开连接事件回调
    def disconnected_callback(client):
        print("Disconnected callback called!")
        disconnected_event.set()

    print("connecting to device...")
    async with BleakClient(device,disconnected_callback=disconnected_callback) as client:
        print("Connected")
        await client.start_notify(par_notification_characteristic, notification_handler)
        while True:
            await client.write_gatt_char(par_write_characteristic, send_str)
            await asyncio.sleep(1.0)           #每休眠1秒发送一次
        # await disconnected_event.wait()       #休眠直到设备断开连接，有延迟。此处为监听设备直到断开为止
        # await asyncio.sleep(10.0)           #程序监听的时间，此处为10秒
        # await client.stop_notify(par_notification_characteristic)

asyncio.run(main())
