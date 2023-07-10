# 这个toolkit集成OCR功能，来实现PDF和JPG转STR，按照要求使用移动云API实现
# PDF2STR 先转换为jpg，再调jpd2str
# JPG2STR
import json
import os

import pdfplumber
from ecloud import CMSSEcloudOcrClient

access_key = '24ddbf072db74f57b0afdf26a9be9048'
secret_key = '3610c16b398d4f6c90184ef91cd98910'
url = 'https://api-wuxi-1.cmecloud.cn:8443'


def jpg_ocr(image_file: str, save_name: str, threshold=0.8) -> str:
    def ECloud_ocr_request(image_path: str, threshold: float) -> str:
        request_url = '/api/ocr/v1/generic'
        try:
            ocr_client = CMSSEcloudOcrClient(access_key, secret_key, url)
            response = ocr_client.request_ocr_service_file(requestpath=request_url, imagepath=image_path)
            response_dict = json.loads(response.text)
            print(image_path + '    ' + response_dict['requestId'])
            #  完成后取消DEBUG模式
            # with open('./response.jpg_txt', 'rb') as response:
            #     response_dict = json.loads(response.read())
            #     print(response_dict.items())

            if response_dict.get('body') is None:
                return ''
            words_info = response_dict.get('body')['content']['prism_wordsInfo']
            words = ''
            for element in words_info:
                if element['prob'] >= threshold:
                    words += element['word'] + ' '
            # print(words)
            return words
        except ValueError as e:
            print(e)

    if not os.path.exists('jpg_txt'):
        os.mkdir('jpg_txt')
    result = ''
    for pics in os.listdir(image_file):
        result += ECloud_ocr_request(image_file + '/' + pics, threshold)

    if save_name[-4:] == '.txt':
        save_file = 'jpg_txt/' + save_name
    else:
        save_file = 'jpg_txt/' + save_name + ".txt"
    with open(save_file, 'w', encoding='utf-8') as f:
        f.write(result)
    return result


# def _pdf_ocr(pdf_file: str, save_name: str, threshold: float) -> str:
#     if save_name[-4:] == '.txt':
#         save_name = save_name[:-4]
#     pdf_2jpg(pdf_file, save_name)
#     result = jpg_ocr('jpg/' + save_name + '.jpg', save_name, threshold)
#     return result


def pdf_ocr(pdf_file: str, save_name: str) -> str:
    if save_name[-4:] == '.pdf':
        save_name = save_name[:-4]
    if not os.path.exists('pdf_txt'):
        os.mkdir('pdf_txt')

    with pdfplumber.open(pdf_file + '.pdf') as pdf:
        final_result = ''
        for page in pdf.pages:
            final_result += page.extract_text().replace('\n', ' ')

    if save_name[-4:] == '.txt':
        save_name = save_name[:-4]
    with open('./pdf_txt/' + save_name + '.txt', 'w', encoding='utf-8') as f:
        f.write(final_result)
    return final_result


if __name__ == "__main__":
    # jpg_ocr('./jpg/1.jpg', '1')
    for i in range(101, 102):
        jpg_ocr('jpgs/' + str(i), str(i))
        print(i)
        # time.sleep(1)
