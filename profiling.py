import hashlib
import json
import os
import time

import openai

from config import Config

isLogging = False


def profiling(reportDict: dict) -> dict:
    def summarize(report: dict, promptFile='prompts/profiling.pmt', model=Config.model1,
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
            if not os.path.exists('profiles'):
                os.mkdir('profiles')

            openai.api_key = Config.key0
            openai.api_base = Config.url0
            rsp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "function", "content": role, 'name': 'Summarize'},
                    {"role": "user", "content": question},
                ],
                temperature=0.1,
            )
        except:
            time.sleep(30)
            rsp = openai.ChatCompletion.create(
                model=Config.model5,
                messages=[
                    {"role": "function", "content": role, 'name': 'Summarize'},
                    {"role": "user", "content": question},
                ],
                temperature=0.1,
            )
        content = rsp['choices'][0]["message"]["content"]
        return eval(content)

    profile = {}
    report = reportDict
    # print(report)
    profile['姓名'] = report['姓名']
    profile['年龄'] = report['年龄']
    profile['教育背景'] = report['最高学位']
    profile['工作经历'] = []
    for e in report['工作经历']:
        profile['工作经历'].append({'公司': e['公司名称'], '职位': e['职位'], '工作时间': e['工作时间']})
    rsp = summarize(report)
    profile['行业经验'] = rsp.get('行业')
    profile['领域方向'] = rsp.get('领域')
    with open('profiles/' + hashlib.md5(str(report).encode(encoding='UTF-8')).hexdigest() + '.json', 'w') as f:
        json.dump(profile, f)
    return profile


if __name__ == '__main__':
    with open('reports/3.json', 'r') as f:
        print(profiling(json.load(f)))
    pass
