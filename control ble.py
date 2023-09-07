import asyncio
from bleak import BleakClient, BleakScanner

# 全局变量用于保存连接后的客户端对象
global_bleak_client = None
par_write_characteristic = "0000ffe1-0000-1000-8000-00805f9b34fb"
send_str = bytearray([0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7B, 0x7D])
dict_move = {'go': '7B 00 00 00 C8 00 00 00 00 B3 7D', 'back': '7B 00 00 FF 38 00 00 00 00 BC 7D',
             'left': '7B 00 00 00 C8 00 00 00 55 E6 7D', 'right': '7B 00 00 00 C8 00 00 FF AB E7 7D',
             'stop': '7B 00 00 00 00 00 00 00 00 7B 7D'}


async def connect_to_device(device_address):
    global global_bleak_client

    async with BleakClient(device_address) as client:
        try:
            # 连接到蓝牙设备
            await client.connect()

            # 保存客户端对象到全局变量
            global_bleak_client = client

            # 在这里，您可以执行与蓝牙设备通信的操作
            # 等待指令的到来

        except Exception as e:
            print(e)


async def control_vehicle(command):
    global global_bleak_client

    if global_bleak_client is not None:
        send_str = None

        if command == 'go':
            send_str = bytearray.fromhex(dict_move['go'].strip())
        elif command == 'stop':
            send_str = bytearray.fromhex(dict_move['stop'].strip())
        elif command == 'left':
            send_str = bytearray.fromhex(dict_move['left'].strip())
        elif command == 'right':
            send_str = bytearray.fromhex(dict_move['right'].strip())

        if send_str is not None:
            # 使用全局的客户端对象发送指令
            await global_bleak_client.write_gatt_char(par_write_characteristic, send_str)


def main():
    devices = asyncio.run(BleakScanner.discover())
    for device in devices:
        print(f"Connecting to device: {device.name} ({device.address})")

        # 在主线程中连接到设备
        asyncio.run(connect_to_device(device.address))


if __name__ == "__main__":
    main()

