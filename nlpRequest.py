import csv
import os
import time

import openai
import requests

import dataMasker

# 需要设置代理才可以访问 api
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"  # 在更换系统后修改为正确的代理
isLogging = False
csv_path = "test.csv"


def gpt3_original(resource: str, prompt_: str, model="gpt-3.5-turbo-16k", role="资深HR") -> dict or None:
    def get_api_key():
        openai_key_file = 'key'
        with open(openai_key_file, 'r', encoding='utf-8') as f_:
            openai_key = f_.read()
        return openai_key

    def trim(raw_content: str) -> str:
        #     1 去除前缀
        raw_content = raw_content[raw_content.find('{'):]
        # 2 null、未提供替换为None
        raw_content = raw_content.replace("null", "None").replace('未提供', 'None')
        # 3 学士换成本科
        raw_content = raw_content.replace("学士", "本科")
        # 4 false,true替换成False,True
        raw_content = raw_content.replace('false', 'False').replace('true', 'True')
        return raw_content

    def logger(progress, progress_tag):
        if isLogging is True:
            with open('log.txt', 'w') as log:  # 清空
                pass
            with open('log.txt', 'a') as log:
                log.write(progress_tag + '\n')
                log.writelines(progress)
                log.write('\n\n')

    openai.api_key = get_api_key()
    # 掩去电话和邮箱
    resource_masked = data_masker.mask(resource)

    question = resource_masked["content_masked"] + '\n' + prompt_
    # try:
    rsp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": question},
        ],
        temperature=0.1,
    )
    # except:
    # return None
    content = rsp['choices'][0]["message"]["content"]
    logger(content, 'raw')
    content = trim(content)
    logger(content, 'trimmed')
    # 解码电话和邮箱
    content = data_masker.demask(content, resource_masked)
    logger(content, 'de_masked')

    return eval(content)


def get_resume_txt(txt_file: str) -> str:
    with open(txt_file, 'r', encoding='utf-8') as f_:
        return f_.read()


def get_prompt(prompt_file: str) -> str:
    with open(prompt_file, 'r', encoding='utf-8') as f_:
        return f_.read()


def gpt_via_poe(question, model="gpt-3.5-turbo", role="资深HR"):
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