# 这个toolkit集成OCR功能，来实现PDF和JPG转STR，按照要求使用移动云API实现
# PDF2STR 先转换为jpg，再调jpd2str
# JPG2STR
import json
import os
import time

import numpy as np
import pdfplumber
from ecloud import CMSSEcloudOcrClient
from sklearn.cluster import DBSCAN

access_key = '24ddbf072db74f57b0afdf26a9be9048'
secret_key = '3610c16b398d4f6c90184ef91cd98910'
url = 'https://api-wuxi-1.cmecloud.cn:8443'


def pics_ocr(image_file_WenJianJia: str, save_name: str,
             synthesize_between_pages=True) -> str | list:  # image_file是文件夹！文件夹！默认会一次性把文件夹下面的所有图片都OCR一遍然后粘成一个str，否则按图片分开放进list
    def ECloud_ocr_request(image_path: str) -> None | list:
        time.sleep(1)  # 防止被当成ddos
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
                return None
            words_info = response_dict.get('body')['content']['prism_wordsInfo']

            # done 通过每个character的置信度筛查，阈值待定，但对数字和.除外（一律保留，OCR API的0置信率低BUG）
            # threshold没P用，再弱智的错误Prob都有0.95，要检查confidence
            # confidence有P用 但是一点，因为他太自信了
            linePopIndexList = []
            for i in range(len(words_info)):
                lineDict = words_info[i]
                # if element['prob'] >= threshold:
                #     words += element['word'] + ' '
                charPopIndexList = []
                # 检查confidence，收集不为数字和'.'并且confidence小于0的index
                # 这不会导致吞字 吞字是移动云OCR太垃圾了
                for j in range(len(lineDict['chars'])):
                    charDict = lineDict['chars'][j]
                    if charDict['char'].isdigit() or charDict['char'] == '.':
                        continue
                    if charDict['confidence'] < 0:
                        charPopIndexList.append(j)
                # done 根据popIndexList重构word和chars
                # 将popIndexList排序，从后往前切片，防止下标错位
                charPopIndexList.sort(reverse=True)
                # 循环删除指定位置的字符
                for j in charPopIndexList:
                    words_info[i]['word'] = words_info[i]['word'][:j] + words_info[i]['word'][j + 1:]
                    words_info[i]['chars'].pop(j)
                # done 根据新的chars重构"position"
                try:
                    words_info[i]['position'][0] = words_info[i]['chars'][0]['pos'][0]  # 左上下-第一个左上下
                    words_info[i]['position'][3] = words_info[i]['chars'][0]['pos'][3]
                    words_info[i]['position'][1] = words_info[i]['chars'][-1]['pos'][1]  # 右上下-最后一个右上下
                    words_info[i]['position'][2] = words_info[i]['chars'][-1]['pos'][2]
                except:  # 空了就删
                    linePopIndexList.append(i)
            linePopIndexList.sort(reverse=True)
            for i in linePopIndexList:
                words_info.pop(i)

            # done Layout Analyze
            final_words = layoutAnalyze(words_info)
            # # debug
            # with open('101.json', 'w') as debug:
            #     json.dump(words_info, debug)
            # # debug
            return final_words
        except ValueError as error:
            print(error)

    def layoutAnalyze(input_Words_Info: list, threshold=220) -> list:
        # 将传入的words_info进行layout分析，然后重排序并回传
        def distance(rect1, rect2) -> float:
            x1 = [p['x'] for p in rect1]
            y1 = [p['y'] for p in rect1]
            x2 = [p['x'] for p in rect2]
            y2 = [p['y'] for p in rect2]
            dx = np.max([np.min(x2) - np.max(x1), 0, np.min(x1) - np.max(x2), 0])
            dy = np.max([np.min(y2) - np.max(y1), 0, np.min(y1) - np.max(y2), 0])
            return np.sqrt(dx * dx + dy * dy)

        rects = []
        for each in input_Words_Info:
            rects.append(each['position'])
        # 将每个矩形表示为一个点
        # 数据格式为：[[{'x': x1, 'y': y1}, {'x': x2, 'y': y2}, {'x': x3, 'y': y3}, {'x': x4, 'y': y4}], ...]

        # 数据转换为NumPy数组
        data = np.array(rects)
        # 计算矩形之间的距离矩阵
        dist_matrix = np.zeros((len(data), len(data)))
        for i in range(len(data)):
            for j in range(len(data)):
                if i == j:
                    dist_matrix[i, j] = 0
                else:
                    dist_matrix[i, j] = distance(data[i], data[j])
        # 使用DBSCAN进行聚类
        dbscan = DBSCAN(eps=threshold, min_samples=1, metric='precomputed')
        labels = dbscan.fit_predict(dist_matrix)
        # 重排
        clusters = {}
        for i, cluster in enumerate(labels):
            if cluster not in clusters:
                clusters[cluster] = []
            clusters[cluster].append(input_Words_Info[i])

        # 将字典转换为列表，并按照聚类结果顺序排序
        sorted_clusters = []
        for cluster in labels:
            if cluster not in sorted_clusters:
                sorted_clusters.append(cluster)

        # 重新排列原始列表
        reordered_list = []
        for cluster in sorted_clusters:
            reordered_list.extend(clusters[cluster])

        return reordered_list

    if not os.path.exists('jpg_txt'):
        os.mkdir('jpg_txt')
    if synthesize_between_pages is True:
        result = ''
    else:
        result = []
    for pic in os.listdir(image_file_WenJianJia):
        content_list = ECloud_ocr_request(image_file_WenJianJia + '/' + pic)
        temp = ''
        for content in content_list:
            temp += content['word'] + ' '
        if synthesize_between_pages is True:
            result += temp
        else:
            result.append(temp)

    if save_name[-4:] == '.txt':
        save_file = 'jpg_txt/' + save_name
    else:
        save_file = 'jpg_txt/' + save_name + ".txt"

    if synthesize_between_pages is True:
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(result)
    else:
        s = ''
        for e in result:
            s += e + '\n'
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(s)
    return result


def pdf_ocr(pdf_file: str, save_name: str) -> str:
    if pdf_file[-3:] != 'pdf':
        pdf_file += '.pdf'
    if save_name[-4:] == '.pdf':
        save_name = save_name[:-4]
    if not os.path.exists('pdf_txt'):
        os.mkdir('pdf_txt')

    with pdfplumber.open(pdf_file) as pdf:
        final_result = ''
        for page in pdf.pages:
            final_result += page.extract_text().replace('\n', ' ')

    if save_name[-4:] == '.txt':
        save_name = save_name[:-4]

    with open('./pdf_txt/' + save_name + '.txt', 'w', encoding='utf-8') as f:
        f.write(final_result)
    return final_result


if __name__ == "__main__":
    # for f in os.listdir('jpgs'):
    #     for pic in os.listdir('jpgs/' + f):
    #         pics_ocr('jpgs/' + f, f)
    #         print(f)

    # for f in os.listdir('pdfs'):
    #     a = pdf_ocr('pdfs/' + f, f.split('.')[0])
    #     print(f)

    pics_ocr('jpgs/170', '170')

    pass
