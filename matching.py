import json
import os
import time

import openai

from config import Config

# os.environ["HTTP_PROXY"] = proxyConfig.proxy
# os.environ["HTTPS_PROXY"] = proxyConfig.proxy
isLogging = False
openai_key_file = 'config/key'

with open(openai_key_file, 'r', encoding='utf-8') as f_:
    openai_key = f_.read()
openai.api_key = openai_key
openai.api_base = Config.url


def matching(report: dict) -> dict:
    def selected_dict_to_str(d, selected_keys):
        # 将字典中被选定的键值对转换为字符串并拼接起来
        return ", ".join([f"{k}: {v}" for k, v in d.items() if k in selected_keys])

    def analyze(features: str, requirements: str, promptFile='prompts/matching.pmt', model=Config.model,
                role="You're an HR",
                reset=True) -> bool:
        def getPrompt(prompt_file: str) -> str:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()

        question = requirements + "\n" + features + '\n' + getPrompt(promptFile)
        if reset is True:
            with open('prompts/reset.pmt', 'r', encoding='utf-8') as resetPrompt:
                question = resetPrompt.read() + '\n' + question

        try:
            rsp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "function", "content": role, 'name': 'Matching'},
                    {"role": "user", "content": question},
                ],
                temperature=0.1,
            )
        except:
            time.sleep(20)
            rsp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "function", "content": role, 'name': 'Matching'},
                    {"role": "user", "content": question},
                ],
                temperature=0.1,
            )
        content = rsp['choices'][0]["message"]["content"].replace('true', 'True').replace('false', 'False')
        return eval(content)

    selected = ["年龄", "教育背景", '工作经历', '能力证书和技能等级认证', '个人技能']
    repoForAnalyze = selected_dict_to_str(report, selected)

    matchingResult = {}
    for jobFile in os.listdir('jobTitles'):
        with open('jobTitles/' + jobFile, 'r', encoding='utf-8') as f:
            jobTitleRequirement = f.read()
            matchingResult[jobFile] = analyze(repoForAnalyze, jobTitleRequirement)
        print(jobFile, matchingResult[jobFile])
    return matchingResult


if __name__ == '__main__':
    with open('reports/' + '1' + '.json') as repoFile:
        repo = json.load(repoFile)
    a = matching(repo)
    print(a)
