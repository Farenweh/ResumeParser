import os

import cv2
import numpy as np
from PIL import Image
from PIL import ImageEnhance
from pdf2image import convert_from_path

if not os.path.exists('jpgs'):
    os.mkdir('jpgs')


def pdf_2jpg(pdf_file: str, save_name='', demo=False) -> None:
    def enhance(pic: Image.Image) -> Image.Image:
        # 锐度增强
        enh_sha = ImageEnhance.Sharpness(pic)
        sharpness = 0.1
        image_sharped = enh_sha.enhance(sharpness)
        # 对比度增强
        enh_con = ImageEnhance.Contrast(image_sharped)
        contrast = 2
        return enh_con.enhance(contrast)

    if save_name == '':
        save_name = pdf_file.split('/')[-1].split('.')[0]

    pages = convert_from_path(pdf_file, dpi=400, jpegopt={'quality': 80}, thread_count=16, grayscale=True)

    for j in range(len(pages)):
        if save_name[-4:] == '.jpg':
            if not os.path.exists('jpgs/' + save_name[:-4]):
                os.mkdir('jpgs/' + save_name)
            save_file_l = 'jpgs/' + save_name[:-4] + '/' + str(j) + '.l' + '.jpg'
            save_file_r = 'jpgs/' + save_name[:-4] + '/' + str(j) + '.r' + '.jpg'
        else:
            if not os.path.exists('jpgs/' + save_name):
                os.mkdir('jpgs/' + save_name)
            save_file_l = 'jpgs/' + save_name + '/' + str(j) + '.l' + '.jpg'
            save_file_r = 'jpgs/' + save_name + '/' + str(j) + '.r' + '.jpg'

        image_enhanced = enhance(pages[j])
        that_line, count = find_min_change_column(image_enhanced, demo=demo)
        if count > 9:
            that_line = 1

        result0 = Image.new('L', (that_line, pages[j].height))  # 生成灰度图
        result1 = Image.new('L', (pages[j].width - that_line, pages[j].height))  # 生成灰度图
        result0.paste(image_enhanced.crop([0, 0, that_line, pages[j].height]))
        result1.paste(image_enhanced.crop([that_line, 0, pages[j].width, pages[j].height]))
        result0.save(save_file_l, 'jpeg')
        result1.save(save_file_r, 'jpeg')


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
    img[:, min_change_column_index-3:min_change_column_index+3] = [0, 0, 255]
    binary = cv2.resize(binary, (0, 0), fx=0.25, fy=0.25)
    cv2.imshow('形态学膨胀', binary)
    img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    cv2.imshow('纵列分割', img)
    cv2.waitKey(1)

    return min_change_column_index, change_count[min_change_column_index - start]


if __name__ == "__main__":
    for f in os.listdir('pdfs'):
        print("converting " + f)
        # pdf_2jpg('pdfs/' + str(i) + '.pdf', str(i))
        # pdf_2jpg('pdfs/' + f, f.split('.')[0])
        pdf_2jpg('pdfs/109.pdf')
