import os

from PIL import Image
from PIL import ImageEnhance
from pdf2image import convert_from_path

if not os.path.exists('jpg'):
    os.mkdir('jpg')


def pdf_2jpg(pdf_file: str, save_name: str, combine=True) -> None:
    def enhance(pic: Image.Image) -> Image.Image:
        # 锐度增强
        enh_sha = ImageEnhance.Sharpness(pic)
        sharpness = 0.1
        image_sharped = enh_sha.enhance(sharpness)
        # 对比度增强
        enh_con = ImageEnhance.Contrast(image_sharped)
        contrast = 2
        return enh_con.enhance(contrast)

    pages = convert_from_path(pdf_file, dpi=500, jpegopt={'quality': 90}, thread_count=16, grayscale=True)

    if combine is False:
        for j in range(len(pages)):
            result = Image.new('L', (pages[j].width, pages[j].height))  # 生成灰度图
            if save_name[-4:] == '.jpg':
                if not os.path.exists('jpg/' + save_name[:-4]):
                    os.mkdir('jpg/' + save_name)
                save_file = 'jpg/' + save_name[:-4] + '/' + str(j) + '.jpg'
            else:
                if not os.path.exists('jpg/' + save_name):
                    os.mkdir('jpg/' + save_name)
                save_file = 'jpg/' + save_name + '/' + str(j) + '.jpg'

            image_enhanced = enhance(pages[j])
            result.paste(image_enhanced)

            with open(save_file, 'w'):
                pass
            result.save(save_file, 'jpeg')
    else:
        result = Image.new('L', (pages[0].width * 1, pages[0].height * len(pages)))  # 创建成品图的画布
        for j in range(len(pages)):
            image_enhanced = enhance(pages[j])
            result.paste(image_enhanced, (0, j * pages[j].height))
        with open(save_name, 'w'):
            pass
        result.save(save_name, 'JPEG')


if __name__ == "__main__":
    for i in range(1, 101):
        print("converting " + str(i))
        pdf_2jpg('pdfs/' + str(i) + '.pdf', str(i))
