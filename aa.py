import math
import random
import threading
import turtle

import easyocr
import time
import concurrent.futures
import pyscreenshot as ImageGrab
import keyboard
from matplotlib import pyplot as plt, patches

car_width = 80  # cm
car_height = 50  # cm

# 创建一个条件变量，用于线程同步
pause_resume_condition = threading.Condition()
# 用于标识线程是否暂停的变量
paused = False


# 设置识别中英文两种语言
# reader = easyocr.Reader(['ch_sim','en'], gpu = False) # need to run only once to load model into memory
# result = reader.readtext("img1.png", detail = 0)
# print(result)

def get_ocr(img_no):
    result = reader.readtext("img" + str(img_no) + ".png", detail=0)
    # print(result)
    for re in result:
        re = re.replace(" ", "")
        if "米" in re:
            return float(re[:-1])
    return float(result[0][:-1])


# 计算三角形面积
def calculate_triangle_area(a, b, c):
    s = (a + b + c) / 2
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    return area


# 已知两边和夹角（弧度），求对边长度
def calculate_opposite_edges(a, b, theta_degrees):
    c = math.sqrt(a ** 2 + b ** 2 - 2 * a * b * math.cos(theta_degrees))
    return c


# 已知两边和对边，求角度θ（弧度）
def calculate_angle_given_sides(a, b, c):
    cos_theta = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
    theta_radians = math.acos(cos_theta)
    return theta_radians


def save_img(left, top, width, height, filename):
    im = ImageGrab.grab(bbox=(left, top, width, height))  # X1,Y1,X2,Y2
    im.save(filename)


def get_2_img():
    while True:
        save_img(10, 400, 200, 700, "img1.png")
        save_img(1200, 400, 1500, 700, "img2.png")
        # print("fresh img")
        time.sleep(0.2)


def fresh_img_all_the_time():
    my_thread = threading.Thread(target=get_2_img)
    my_thread.start()


def draw(x, y):
    print("empty")
    # 创建一个新的图形
    fig, ax = plt.subplots()

    # 创建一个矩形对象
    rectangle = patches.Rectangle((150, 100), 80, 50, linewidth=2, edgecolor='r', facecolor='none')

    # 添加矩形到图形中
    ax.add_patch(rectangle)
    # 在坐标 (150, 150) 处绘制一个点
    ax.plot(x, y, 'bo', markersize=20, label='点')
    # 设置坐标轴范围
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 600)

    # 设置坐标轴标签
    ax.set_xlabel('X轴')
    ax.set_ylabel('Y轴')

    # 显示图形
    plt.show()


def get_location():
    # -1 -> error
    # 0 -> stop
    # 1 -> left
    # 2 -> right
    # 3 -> top
    try:
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future1 = executor.submit(get_ocr, 1)
            future2 = executor.submit(get_ocr, 2)
            concurrent.futures.wait([future1, future2])
        end_time = time.time()
        # 计算函数执行时间
        execution_time = end_time - start_time
        print(f"函数执行时间: {execution_time} 秒")

        len1 = future1.result() * 100  # cm
        len2 = future2.result() * 100  # cm
        print("len1 = " + str(len1) + ", len2 = " + str(len2))
        # print("============")
        triangle_area = calculate_triangle_area(car_height, len1, len2)
        # print(triangle_area)
        top_angle = calculate_angle_given_sides(car_height, len1, len2)
        # print(top_angle)
        mid_len = calculate_opposite_edges(car_height / 2, len1, top_angle)
        # print(mid_len)
        mid_top_angle = calculate_angle_given_sides(car_height / 2, mid_len, len1)
        # print(mid_top_angle)
        vertical_distance = triangle_area / car_height  # 人与小车的垂直距离
        # print(vertical_distance)
        # print("============")
        # print(mid_top_angle * (180 / math.pi))
        if random.randint(1, 10) < 7:
            draw(230 + vertical_distance, 150 - mid_len * math.cos(top_angle))
        max_len = max(max(len1, len2), car_height)
        min_len = min(min(len1, len2), car_height)
        mid_len = len1 + len2 + car_height - max_len - min_len

        if min_len + mid_len <= max_len:
            print("不是一个三角形，舍弃")
            return -1
        if vertical_distance < 50:
            return 0
        if math.pi * 5 / 12 <= mid_top_angle <= math.pi * 7 / 12:
            return 3
        if math.pi * 5 / 12 > mid_top_angle:
            return 1
        if mid_top_angle > math.pi * 7 / 12:
            return 2
    except Exception as e:
        print("get location ERROR : " + str(e))
        return -1


def get_instruct():
    global paused

    while True:
        with pause_resume_condition:
            while paused:
                pause_resume_condition.wait()

            instruct = get_location()
            if instruct == -1:
                print("错误，但没有处理")
                # go_to("stop")
            elif instruct == 0:
                go_to("stop")
                print("停止")
            elif instruct == 1:
                go_to("left")
                print("左转")
            elif instruct == 2:
                go_to("right")
                print("右转")
            elif instruct == 3:
                go_to("go")
                print("前进")
            else:
                go_to("stop")
                print("未知指令")
        time.sleep(0.3)


def get_instruct_all_the_time():
    my_thread = threading.Thread(target=get_instruct)
    my_thread.start()
    # 创建并启动键盘监听线程
    thread_keyboard_listener = threading.Thread(target=keyboard_listener)
    thread_keyboard_listener.start()


def keyboard_listener():
    global paused
    print("开始监听键盘")
    while True:
        try:
            key_event = keyboard.read_event()
            if key_event.event_type == keyboard.KEY_DOWN:
                if str(key_event) == "KeyboardEvent(shift down)":
                    print("按下了 'left shift' 键，开始手动执行")
                    paused = True
                elif str(key_event) == "KeyboardEvent(right shift down)":
                    print("按下了 'right shift' 键，开始自动执行")
                    paused = False
                    with pause_resume_condition:
                        pause_resume_condition.notify()  # 通知线程继续执行
                if paused:  # 当前为手动状态
                    print(key_event)
                    if str(key_event) == "KeyboardEvent(Unknown 34 down)":
                        print("按下了 'i' 键，前进")
                        go_to("go")
                    elif str(key_event) == "KeyboardEvent(Unknown 40 down)":
                        print("按下了 'k' 键，停止")
                        go_to("stop")
                    elif str(key_event) == "KeyboardEvent(Unknown 38 down)":
                        print("按下了 'j' 键，左转")
                        go_to("left")
                    elif str(key_event) == "KeyboardEvent(Unknown 37 down)":
                        print("按下了 'l' 键，右转")
                        go_to("right")
                    elif str(key_event) == "KeyboardEvent(Unknown 47 down)":
                        print("按下了 '，' 键，后退")
                        go_to("back")


        except keyboard.KeyboardEvent as e:
            print(e)


##########
import asyncio
import threading
import time

from bleak import BleakClient, BleakScanner

par_write_characteristic = "0000ffe1-0000-1000-8000-00805f9b34fb"
send_str = bytearray([0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7B, 0x7D])
dict_move = {'go': '7B 00 00 01 BB 00 00 00 00 C1 7D', 'back': '7B 00 00 FF 38 00 00 00 00 BC 7D',
             'left': '7B 00 00 00 C8 00 00 00 55 E6 7D', 'right': '7B 00 00 00 C8 00 00 FF A0 EC 7D',
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
                print("Entering while loop")
                with data_lock:
                    # print("Car get a ", shared_data)
                    if shared_data == "STOP":
                        print("disconnect")
                        break
                    if shared_data is not None:
                        print("Car receive   ", shared_data)
                        global send_str
                        send_str = bytearray.fromhex(dict_move[shared_data].strip())
                        await client.write_gatt_char(par_write_characteristic, send_str)
                        shared_data = None
                print("out while loop")
                time.sleep(0.4)
            await client.disconnect()
        except Exception as e:
            print("shared data ERROR" + str(e))


def go_to(move):
    global shared_data
    # print("move is :" + str(shared_data))
    with data_lock:
        print("_-))))))000000000")
        shared_data = move


async def main():
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name == "SREPGEAT":
            print(f"Connecting to device: {device.name} ({device.address})")
            await connect_to_device(device.address)


##########


if __name__ == '__main__':
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  # need to run only once to load model into memory

    #########
    ble_thread = threading.Thread(target=asyncio.run, args=(main(),))
    ble_thread.start()
    time.sleep(5)
    fresh_img_all_the_time()
    get_instruct_all_the_time()
    # for a in dict_move:
    #     print("sending " + a)
    #     go_to(a)
    #     time.sleep(5)
    # go_to("STOP")
    #########
    while True:
        print("666")
        time.sleep(100)

    # reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  # need to run only once to load model into memory
    # start_time = time.time()  # 记录开始时间
    # get_location()
    # end_time = time.time()  # 记录结束时间
    # elapsed_time = end_time - start_time  # 计算执行时间
    # print(f"Execution time: {elapsed_time} seconds")
