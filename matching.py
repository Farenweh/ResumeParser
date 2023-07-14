import hashlib
import json
import os
import time

import openai

from config import Config

isLogging = False


def matching(report: dict) -> dict:
    def selected_dict_to_str(d, selected_keys):
        # 将字典中被选定的键值对转换为字符串并拼接起来
        return ", ".join([f"{k}: {v}" for k, v in d.items() if k in selected_keys])

    def analyze(features: str, requirements: str, promptFile='prompts/matching.pmt', model=Config.model5,
                role="You're an HR",
                reset=False, progressSign=False) -> bool:
        def getPrompt(prompt_file: str) -> str:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()

        if progressSign is False:
            question = features + "\n" + "记住这位求职者的信息" + "\n" + requirements + '\n' + getPrompt(promptFile)
        else:
            question = requirements + '\n' + "根据刚刚的求职者信息。" + getPrompt(promptFile)

        if reset is True:
            with open('prompts/reset.pmt', 'r', encoding='utf-8') as resetPrompt:
                question = resetPrompt.read() + '\n' + question

        if not os.path.exists('matches'):
            os.mkdir('matches')
        openai.api_key = Config.key0
        openai.api_base = Config.url0

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
            time.sleep(30)
            rsp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "function", "content": role, 'name': 'Matching'},
                    {"role": "user", "content": question},
                ],
                temperature=0.1,
            )
        content = rsp['choices'][0]["message"]["content"].replace('true', 'True').replace('false', 'False')
        try:
            eval(content)
        except:
            # time.sleep(30)
            question = features + "\n" + "记住这位求职者的信息" + "\n" + requirements + '\n' + getPrompt(promptFile)
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
                time.sleep(30)
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
    # done 让模型记忆features 以节省token
    inProgress = False
    for jobFile in os.listdir('jobTitles'):
        with open('jobTitles/' + jobFile, 'r', encoding='utf-8') as f:
            jobTitleRequirement = f.read()
            matchingResult[jobFile.split('.')[0]] = analyze(repoForAnalyze, jobTitleRequirement,
                                                            progressSign=inProgress)
        # print(jobFile, matchingResult[jobFile.split('.')[0]])
        inProgress = True
    with open('matches/' + hashlib.md5(str(report).encode(encoding='UTF-8')).hexdigest() + '.json', 'w') as f:
        json.dump(matchingResult, f)
    return matchingResult  # 只返回配对结果字典，形似{'Title1':True,'Title2':False}


if __name__ == '__main__':
    with open('reports/' + '0' + '.json') as repoFile:
        repo = json.load(repoFile)
    a = matching(repo)
    print(a)
