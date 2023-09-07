import random
import time

import matplotlib.pyplot as plt
import matplotlib.patches as patches

while True:
    # 创建一个新的图形
    fig, ax = plt.subplots()

    # 创建一个矩形对象
    rectangle = patches.Rectangle((150, 100), 80, 50, linewidth=2, edgecolor='r', facecolor='none')

    # 添加矩形到图形中
    ax.add_patch(rectangle)
    # 在坐标 (150, 150) 处绘制一个点
    ax.plot(random.randint(1, 100), random.randint(100, 200), 'bo', markersize=20, label='点')
    # 设置坐标轴范围
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 300)

    # 设置坐标轴标签
    ax.set_xlabel('X轴')
    ax.set_ylabel('Y轴')

    # 显示图形
    plt.show()
    time.sleep(0.5)
