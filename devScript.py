# checkProxy()
import ast
import csv
import json
import re

from extracting import extracting
from pdf_2jpg import pdf_2jpg
from profiling import profiling

csv_path = "test1.csv"


def extractDev(start: int, endNotIncluded: int, src: str) -> dict:
    reports = {}

    with open(csv_path, "w", newline=""):  # 清除文件
        title = False
        pass

    for i in range(start, endNotIncluded):
        report = extracting(src + '/' + str(i) + '.txt')
        with open('reports/' + str(i) + '.json', 'w') as reportJson:
            json.dump(report, reportJson)
        reports[i] = report
        print(i)
        print(report)  # 显示进度和当前情况

        with open(csv_path, "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            # 写入标题行
            if title is False:
                writer.writerow(report.keys())
                title = True
            # 写入数据行
            writer.writerow(report.values())
    return reports

    # with open('test_reports_dict', 'wb') as f:
    #     pickle.dump(reports, f)
    # print()


def pdf2jpgDev():
    for i in range(1, 101):
        print("converting " + str(i))
        pdf_2jpg('pdf/' + str(i) + '.pdf', str(i))


def restoreReportsDictFromCSV(csvFile: str) -> list:
    data = []
    with open(csvFile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            for key, value in row.items():
                if value == "":
                    # Convert empty string to None
                    row[key] = None
                else:
                    try:
                        # Try to evaluate the value as a Python expression
                        row[key] = ast.literal_eval(value)
                    except (ValueError, SyntaxError):
                        # If evaluation fails, leave the value as-is
                        pass
            data.append(row)

    print(data)
    return data


def workAgeCalculator(workExpList: list) -> int:  # 已迁移
    # pattern = r"\d{4}\.\d{1,2}"
    yearPattern = r"\d{4}"
    monthPattern = r"(?<![0-9])\d{1,2}(?![0-9])"
    workYear = 0
    workMonth = 0
    if workExpList is None:
        return 0
    for exp in workExpList:
        if exp['工作时间'] is None:
            continue
        if exp['是否为实习经历'] is True:
            continue
        if exp['职位'] is not None:
            if '实习' in exp['职位']:
                continue
        if '至今' in exp['工作时间']:
            exp['工作时间'] = exp['工作时间'].replace('至今', '-2023.4').replace('年', '.').replace('月', '')

        yearPoints = list(map(int, re.findall(yearPattern, exp['工作时间'])))
        monthPoints = list(map(int, re.findall(monthPattern, exp['工作时间'])))
        try:
            if len(yearPoints) < 2:  # workaround for 2021年4月到6月
                yearPoints.append(yearPoints[1])
            workYear += yearPoints[1] - yearPoints[0]
            workMonth += monthPoints[1] - monthPoints[0]
        except:
            return -1
    if workMonth < 0:
        workYear += int(workMonth / 12)
    else:
        workYear += int(workMonth / 12) + 1
    return workYear  # 已迁移


def profilingDev(start: int, endNotIncluded: int) -> dict:
    profiles = {}
    for i in range(start, endNotIncluded):
        profile = profiling('reports/' + str(i) + '.json')
        with open('profiles/' + str(i) + '.json', 'w') as reportJson:
            json.dump(profile, reportJson)
        profiles[i] = profile
        print(i)
        print(profile)  # 显示进度和当前情况
    return profiles


if __name__ == '__main__':
    # with open('reports/4.json') as f:
    #     a = json.load(f)
    #     print(a)
    # T1 = time.time()
    # a = profilingDev(1, 2)
    # T2 = time.time()
    # t = (T2 - T1)
    # print('程序运行时间:%.2f秒' % t)
    # print()

    # print('may need 60 seconds for per content')
    # T1 = time.time()
    # extractDev(101, 102, 'pdf_txt')
    # T2 = time.time()
    # t = (T2 - T1)
    # print('程序运行时间:%.2f秒' % t)

    # a = restoreReportsDictFromCSV('test1.csv')
    # print()

    # with open('cal.csv', "w", newline=""):  # 清除文件
    #     title = False
    #     pass
    # a = restoreReportsDictFromCSV('test.csv')
    # for i in range(len(a)):
    #     if i == 47:  # for debug
    #         pass
    #     a[i]['工作年限'] = workAgeCalculator(a[i]['工作经历'])
    #
    #     with open('cal.csv', "a", newline="") as csv_file:
    #         writer = csv.writer(csv_file)
    #         # 写入标题行
    #         if title is False:
    #             writer.writerow(a[i].keys())
    #             title = True
    #         # 写入数据行
    #         writer.writerow(a[i].values())
    # print()




    pass
