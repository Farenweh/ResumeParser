import hashlib
import json
import os

import extracting
import matching

# txt或IO输入直接放入jpg_txt文件夹

# # docx/doc转pdf功能，用以支持docx/doc输入
# for d in os.listdir('docxs'):
#     docx_2pdf.docx_2pdf('docxs/' + d)
#
# # pdf转jpg功能，用以支持jpg输入
# for p in os.listdir('pdfs'):
#     pdf_2jpg.pdf_2jpg('pdfs/' + p)
#
# jpg转txt的ocr功能，通过移动云OCR API实现，同时整合了置信度筛查和Layout Analyze流程，从而通过版面分析来重排OCR结果，为NLP提供清洁数据
# for p in os.listdir('jpgs'):
#     OCR_Analyzed_result = OCRkit.pics_ocr('jpgs/' + p)
#     print(p)
#     print(OCR_Analyzed_result)

with open('TEST_SET_RESULT_DICT.json', 'r', encoding='utf-8') as f:
    test_set = json.load(f)
extracted = os.listdir('reports')
matched = os.listdir('matches')
for r in os.listdir('jpg_txt'):
    # try:
        with open('jpg_txt/' + r, encoding='utf-8') as txt:
            OCR_Analyzed_result = txt.read()
            report_name = hashlib.md5(OCR_Analyzed_result.encode(encoding='UTF-8')).hexdigest() + '.json'
            if report_name in extracted:
                print('已缓存')
                with open('reports/' + str(report_name)) as f:
                    report = json.load(f)
            else:
                report = extracting.extracting(OCR_Analyzed_result)
            print(r)
            print(report)

        # 岗位匹配功能，根据求职者信息，遍历所有岗位要求，返回其同所有岗位的匹配情况
        match_name = hashlib.md5(str(report).encode(encoding='UTF-8')).hexdigest() + '.json'
        if match_name in matched:
            print('已缓存')
            with open('matches/' + match_name, 'r') as f:
                match = json.load(f)
        else:
            match = matching.matching(report)

        match_position = ""
        for k in match.keys():
            if match[k] is True:
                match_position += k + '、'
        match_position = match_position[:-1]

        print(match)
        try:
            test_set[r.split('.')[0]] = {"name": report['姓名'],
                                         "age": str(report['年龄']),
                                         "education": report['最高学位']['学位'],
                                         "school": report['最高学位']['授予院校'],
                                         "work_time": str(report['工作年限']),
                                         "match_position": match_position}
        except:
            test_set[r.split('.')[0]] = {"name": report['姓名'],
                                         "age": str(report['年龄']),
                                         "education": None,
                                         "school": None,
                                         "work_time": str(report['工作年限']),
                                         "match_position": match_position}
        finally:
            with open('TEST_SET_RESULT_DICT.json', 'w', encoding='utf-8') as f:
                json.dump(test_set, f)
    # except:
    #     with open('TEST_SET_RESULT_DICT.json', 'w', encoding='utf-8') as f:
    #         json.dump(test_set, f)
    #     import winsound
    #
    #     duration = 2000  # millisecond
    #     freq = 720  # Hz
    #     winsound.Beep(freq, duration)
    #     print('Error!')
    #     exit()

"""
参考格式
{
    "101": {
        "name": "潘孝东",
        "age": "23",
        "education": "本科",
        "school": "中央戏曲学院",
        "work_time": "0",
        "match_position": ""
    },
"""
