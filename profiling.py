import json
import os
import time

import openai

import proxyConfig

os.environ["HTTP_PROXY"] = proxyConfig.proxy
os.environ["HTTPS_PROXY"] = proxyConfig.proxy
isLogging = False
openai_key_file = 'key'

with open(openai_key_file, 'r', encoding='utf-8') as f_:
    openai_key = f_.read()
openai.api_key = openai_key


def summarize(report: dict, promptFile='prompts/profiling.pmt', model="gpt-3.5-turbo-16k",
              role="You're a summarizing function",
              reset=True) -> dict:
    def getPrompt(prompt_file: str) -> str:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()

    question = str(report['工作经历']) + "\n" + getPrompt(promptFile)
    if reset is True:
        with open('prompts/reset.pmt', 'r', encoding='utf-8') as resetPrompt:
            question = resetPrompt.read() + '\n' + question

    try:
        rsp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "function", "content": role, 'name': 'Summarize'},
                {"role": "user", "content": question},
            ],
            temperature=0.1,
        )
    except:
        time.sleep(20)
        rsp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "function", "content": role, 'name': 'Summarize'},
                {"role": "user", "content": question},
            ],
            temperature=0.1,
        )
    content = rsp['choices'][0]["message"]["content"]
    return eval(content)


def profiling(reportFile: str) -> dict:
    profile = {}
    with open(reportFile, 'r', encoding='utf-8') as reportJson:
        report = json.load(reportJson)
    print(report)
    profile['姓名'] = report['姓名']
    profile['年龄'] = report['年龄']
    profile['教育背景'] = report['最高学位']
    profile['工作经历'] = []
    for e in report['工作经历']:
        profile['工作经历'].append({'公司': e['公司名称'], '职位': e['职位'], '工作时间': e['工作时间']})
    profile['行业经验'] = summarize(report)
    return profile
