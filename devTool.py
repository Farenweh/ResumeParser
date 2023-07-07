# check_proxy()
import csv
import time

from nlpRequest import get_prompt, csv_path, get_resume_txt, gpt3_original

T1 = time.time()

reports = {}
with open(csv_path, "w", newline="") as csv_file:  # 清除文件
    title = False
    pass
for i in range(1, 101):
    prompt = get_prompt('prompts/extract_prompt')
    raw_resume = get_resume_txt('pdf_txt/' + str(i) + '.txt')
    report = gpt3_original(raw_resume, prompt)
    reports[str(i)] = report
    print(i)
    print(report)
    with open(csv_path, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        # 写入标题行
        if title is False:
            writer.writerow(report.keys())
            title = True
        # 写入数据行
        writer.writerow(report.values())

T2 = time.time()
t = (T2 - T1)
print('程序运行时间::%.2f秒' % t)

# with open('test_reports_dict', 'wb') as f:
#     pickle.dump(reports, f)
# print()
