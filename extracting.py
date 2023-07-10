import os
import re
import time

import openai
import requests

import dataMasker
from config import Config

# os.environ["HTTP_PROXY"] = proxyConfig.proxy
# os.environ["HTTPS_PROXY"] = proxyConfig.proxy  # 在更换系统后修改为正确的代理
isLogging = False
openai_key_file = 'config/key'

with open(openai_key_file, 'r', encoding='utf-8') as f_:
    openai_key = f_.read()
openai.api_key = openai_key
openai.api_base = Config.url
a = openai.api_base


def extracting(contentFile: str, promptFile='prompts/extract.pmt', model=Config.model,
               role="You're an information extracting function",
               reset=True) -> dict or None:
    def trim(raw_content: str) -> str:
        # 1 去除前后缀
        raw_content = raw_content[raw_content.find('{'):raw_content.rfind('}') + 1]
        # 2 null、未提供替换为None
        raw_content = raw_content.replace("null", "None").replace('未提供', 'None')
        # 3 学士换成本科
        raw_content = raw_content.replace("学士", "本科")
        # 4 false,true替换成False,True
        raw_content = raw_content.replace('false', 'False').replace('true', 'True')
        return raw_content

    def logger(progress, progress_tag):
        if isLogging is True:
            with open('extractLog.txt', 'w'):  # 清空
                pass
            with open('extractLog.txt', 'a') as log:
                log.write(progress_tag + '\n')
                log.writelines(progress)
                log.write('\n\n')

    def getResumeTxt(File: str) -> str:
        with open(File, 'r', encoding='utf-8') as f:
            return f.read()

    def getPrompt(File: str) -> str:
        with open(File, 'r', encoding='utf-8') as f__:
            return f__.read()

    def workAgeCalculator(workExpList: list) -> int:
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
        return workYear

    # 掩去电话和邮箱
    contentFile = getResumeTxt(contentFile)
    promptFile = getPrompt(promptFile)
    resource_masked = dataMasker.mask(contentFile)

    question = resource_masked["content_masked"] + '\n' + promptFile
    if reset is True:
        with open('prompts/reset.pmt', 'r', encoding='utf-8') as resetPrompt:
            question = resetPrompt.read() + '\n' + question

    if reset is True:
        with open('prompts/reset.pmt', 'r', encoding='utf-8') as resetPrompt:
            question = resetPrompt.read() + '\n' + question

    try:
        rsp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "function", "content": role, 'name': 'Extractor'},
                {"role": "user", "content": question},
            ],
            temperature=0.1,
        )
    except:
        time.sleep(5)
        rsp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "function", "content": role, 'name': 'Extractor'},
                {"role": "user", "content": question},
            ],
            temperature=0.1,
        )
    content = rsp['choices'][0]["message"]["content"]
    logger(content, '_____________________raw_____________________')
    content = trim(content)
    logger(content, '_____________________trimmed_____________________')
    # 解码电话和邮箱
    content = dataMasker.demask(content, resource_masked)
    logger(content, '_____________________de_masked_____________________')
    reportDict = eval(content)
    reportDict['工作年限'] = workAgeCalculator(reportDict['工作经历'])
    return reportDict


def viaPoe(question, model="gpt-3.5-turbo", role="资深HR"):  # Not available
    # Not available
    headers = {"Content-Type": "application/json", "Authorization": "chinchilla None"}
    data = {"model": model,
            "messages": [
                {"role": "system", "content": role},
                {"role": "user", "content": question}],
            "temperature": 0.1}
    rsp = requests.post("https://http://167.172.65.148:3700/v1/chat/completions", headers=headers, data=data)
    return rsp


def check_proxy():
    proxies = {
        "http": os.environ["HTTP_PROXY"],
        "https": os.environ["HTTPS_PROXY"]
    }
    try:
        r = requests.get("https://ipapi.co/json/", proxies=proxies, timeout=4)
        data = r.json()
        country = data['country_name']
        # city = data['city']
        result = f"代理所在地：{country}"
        print(result)
        return result
    except:
        result = "代理所在地查询超时，代理可能无效"
        print(result)
        return result
