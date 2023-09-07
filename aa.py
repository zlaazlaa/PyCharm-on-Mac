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
        print("fresh img")
        time.sleep(1)


def fresh_img_all_the_time():
    my_thread = threading.Thread(target=get_2_img)
    my_thread.start()


def draw(x, y):
    # 创建一个新的图形
    fig, ax = plt.subplots()

    # 创建一个矩形对象
    rectangle = patches.Rectangle((150, 100), 80, 50, linewidth=2, edgecolor='r', facecolor='none')

    # 添加矩形到图形中
    ax.add_patch(rectangle)
    # 在坐标 (150, 150) 处绘制一个点
    ax.plot(x, y, 'bo', markersize=20, label='点')
    # 设置坐标轴范围
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 300)

    # 设置坐标轴标签
    ax.set_xlabel('X轴')
    ax.set_ylabel('Y轴')

    # 显示图形
    plt.show()
    time.sleep(0.5)


def get_location():
    # -1 -> error
    # 0 -> stop
    # 1 -> left
    # 2 -> right
    # 3 -> top
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future1 = executor.submit(get_ocr, 1)
            future2 = executor.submit(get_ocr, 2)
            concurrent.futures.wait([future1, future2])
        len1 = future1.result() * 100  # cm
        len2 = future2.result() * 100  # cm
        print("len1 = " + str(len1) + ", len2 = " + str(len2))
        print("============")
        triangle_area = calculate_triangle_area(car_height, len1, len2)
        # print(triangle_area)
        top_angle = calculate_angle_given_sides(car_height, len1, len2)
        # print(top_angle)
        mid_len = calculate_opposite_edges(car_height / 2, len1, top_angle)
        # print(mid_len)
        mid_top_angle = calculate_angle_given_sides(car_height / 2, mid_len, len1)
        print(mid_top_angle)
        vertical_distance = triangle_area / car_height  # 人与小车的垂直距离
        # print(vertical_distance)
        print("============")
        print(mid_top_angle * (180 / math.pi))
        draw(230 + vertical_distance, 150 - mid_len * math.cos(top_angle))
        if vertical_distance < 50:
            return 0
        if math.pi / 3 <= mid_top_angle <= math.pi * 2 / 3:
            return 3
        if math.pi / 3 > mid_top_angle:
            return 1
        if mid_top_angle > math.pi * 2 / 3:
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
                print("错误")
            elif instruct == 0:
                print("停止")
            elif instruct == 1:
                print("左转")
            elif instruct == 2:
                print("右转")
            elif instruct == 3:
                print("前进")
            else:
                print("未知指令")
        time.sleep(1)


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
                    if str(key_event) == "KeyboardEvent(Unknown 34 down)":
                        print("按下了 'i' 键，前进")
                    elif str(key_event) == "KeyboardEvent(Unknown 40 down)":
                        print("按下了 'k' 键，后退")
                    elif str(key_event) == "KeyboardEvent(Unknown 38 down)":
                        print("按下了 'j' 键，左转")
                    elif str(key_event) == "KeyboardEvent(Unknown 37 down)":
                        print("按下了 'l' 键，右转")

        except keyboard.KeyboardEvent as e:
            print(e)


if __name__ == '__main__':
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  # need to run only once to load model into memory
    fresh_img_all_the_time()
    get_instruct_all_the_time()
    while True:
        print("666")
        time.sleep(100)

    # reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  # need to run only once to load model into memory
    # start_time = time.time()  # 记录开始时间
    # get_location()
    # end_time = time.time()  # 记录结束时间
    # elapsed_time = end_time - start_time  # 计算执行时间
    # print(f"Execution time: {elapsed_time} seconds")
