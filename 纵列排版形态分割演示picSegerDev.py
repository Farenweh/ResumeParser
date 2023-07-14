import cv2
import numpy as np


def find_min_change_column(img, demo=False):
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    # 将图像转为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为二值图
    ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 获取二值图的宽度和高度
    height, width = binary.shape[:2]
    # 膨胀
    binary = cv2.bitwise_not(binary)
    kernel = np.ones((6, 6), np.uint8)
    binary = cv2.dilate(binary, kernel, iterations=2)
    # 获取中间80%的宽度
    start = int(width * 0.1)
    end = int(width * 0.9)
    # 计算每一列的像素值变化次数
    change_count = []
    for i in range(start, end):
        column = binary[:, i]
        change_count.append(np.sum(column[:-1] != column[1:]))
    # 找到变化次数最少的列号
    min_change_column_index = np.argmin(change_count)
    # 如果有多个变化次数同为最小的列，优先返回最贴近图片正中间的那一列
    if len(change_count) > 1:
        middle_column_index = width // 2
        min_distance = abs(min_change_column_index - middle_column_index)
        for i in range(len(change_count)):
            if i == min_change_column_index:
                continue
            distance = abs(i - middle_column_index)
            if change_count[i] == change_count[min_change_column_index] and distance < min_distance:
                min_change_column_index = i
                min_distance = distance
    min_change_column_index += start
    # 在图像上标记变化次数最少的那一列像素
    img[:, min_change_column_index - 3:min_change_column_index + 3] = [0, 0, 255]
    binary = cv2.resize(binary, (0, 0), fx=0.25, fy=0.25)
    cv2.imshow('形态学膨胀', binary)
    img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    cv2.imshow('纵列分割', img)
    cv2.waitKey(0)

    return min_change_column_index, change_count[min_change_column_index - start]


if __name__ == '__main__':
    # 加载图像
    img = cv2.imread('109.jpg')
    # 找到变化次数最少的那一列像素，返回其列号和变化次数，并将其用红色竖线标记在图像上
    find_min_change_column(img, demo=True)
    # print('变化次数最少的那一列像素所在的列号为：', column_index)
    # print('变化次数最少的那一列像素的变化次数为：', change_count)
