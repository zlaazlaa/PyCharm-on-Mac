import math
import threading

import easyocr
import time
import concurrent.futures
import pyscreenshot as ImageGrab

car_width = 80  # cm
car_height = 50  # cm


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
        print(mid_top_angle * (180 / math.pi))
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
    while True:
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
