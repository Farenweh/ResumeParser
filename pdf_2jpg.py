import os

from PIL import Image
from PIL import ImageEnhance
from pdf2image import convert_from_path

if not os.path.exists('jpg'):
    os.mkdir('jpg')


def pdf_2jpg(pdf_file: str, save_name: str) -> None:
    pages = convert_from_path(pdf_file, dpi=300, jpegopt={'quality': 90}, thread_count=16, grayscale=True)
    # result = Image.new('RGB', (pages[0].width * 1, pages[0].height * len(pages)))  # 创建成品图的画布
    for j in range(len(pages)):
        if save_name[-4:] == '.jpg':
            if not os.path.exists('jpg/' + save_name[:-4]):
                os.mkdir('jpg/' + save_name)
            save_file = 'jpg/' + save_name[:-4] + '/' + str(j) + '.jpg'
        else:
            if not os.path.exists('jpg/' + save_name):
                os.mkdir('jpg/' + save_name)
            save_file = 'jpg/' + save_name + '/' + str(j) + '.jpg'
        # result.paste(pages[j], (0, j * pages[j].height))

        # 锐度增强
        enh_sha = ImageEnhance.Sharpness(pages[j])
        sharpness = 0.1
        image_sharped = enh_sha.enhance(sharpness)
        # 对比度增强
        enh_con = ImageEnhance.Contrast(image_sharped)
        contrast = 2
        image_contrasted = enh_con.enhance(contrast)

        with open(save_file, 'w'):
            pass
        image_contrasted.save(save_file, 'jpeg')
    # result.save(save_file, 'JPEG')


def pdf_2jpg_allin1(pdf_file: str, save_name: str) -> None:
    pages = convert_from_path(pdf_file, dpi=500, jpegopt={'quality': 90}, thread_count=16, grayscale=True)
    result = Image.new('RGB', (pages[0].width * 1, pages[0].height * len(pages)))  # 创建成品图的画布
    if save_name[-4:] != '.jpg':
        save_name = 'jpg/' + save_name + '.jpg'
    for j in range(len(pages)):
        # 锐度增强
        enh_sha = ImageEnhance.Sharpness(pages[j])
        sharpness = 0.1
        image_sharped = enh_sha.enhance(sharpness)
        # 对比度增强
        enh_con = ImageEnhance.Contrast(image_sharped)
        contrast = 2
        image_contrasted = enh_con.enhance(contrast)
        result.paste(image_contrasted, (0, j * pages[j].height))
    with open(save_name, 'w'):
        pass
    # image_contrasted.save(save_file, 'jpeg')
    result.save(save_name, 'JPEG')


if __name__ == "__main__":
    for i in range(1, 101):
        print("converting " + str(i))
        pdf_2jpg_allin1('pdf/' + str(i) + '.pdf', str(i))
