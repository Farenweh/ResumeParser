import os
import pickle
import re

import openai
import requests

import data_masker

# 需要设置代理才可以访问 api
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"  #  在更换系统后修改为正确的代理
isLogging = True


def gpt3_original(resource: str, prompt_: str, model="gpt-3.5-turbo", role="资深HR") -> dict or None:
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
        return raw_content

    def logger(progress, progress_tag):
        if isLogging is True:
            with open('log.txt', 'a') as log:
                log.write(progress_tag + '\n')
                log.writelines(progress)
                log.write('\n\n')

    def lengthChecker(content_masked: str, limit=1000) -> list:  # 3.5的单次Token上限是4096
        # 检查文字长度，超过1000的，向前匹配句号和分号，从其之前断开。
        if len(content_masked) > limit:
            levLength = len(content_masked)
            pattern = r"[。；;]"
            return_ = []
            p = 0
            while levLength > 0:
                sub_text = content_masked[p: p + limit]  # 从第1000位开始截取子串，并反转子串，以便从后往前匹配
                reversed_sub_text = sub_text[::-1]
                match_obj = re.search(pattern, reversed_sub_text)

                if match_obj:
                    start_pos = limit - match_obj.end() + p  # 计算匹配到的子串在原字符串中的起始位置
                    return_.append(content_masked[p:start_pos + 1])
                    p = start_pos + 1
                    levLength -= limit - match_obj.end()

                else:  # 否则，按照limit进行切分
                    return_.append(content_masked[p:limit])
                    p = limit
                    levLength -= limit
            return return_
        else:
            return [content_masked]

    def senseDisambiguate(pieces: list) -> dict:
        report_ = pieces.pop(0)
        if len(pieces) > 0:
            report_ = pieces.pop(0)
            for d in pieces:
                for k, values in d.items():
                    if values is None:
                        continue
                    if k in report_:

                        if k not in ['教育经历', '工作经历']:
                            if values is not list:
                                continue
                            for value in values:
                                report_[k].append(value)

                        elif k == '教育经历':
                            if values is not list:
                                continue
                            for value in values:
                                flag = True
                                for e in report_[k]:
                                    if e['院校名称'] == value['院校名称'] and e['学位'] == value['学位'] and e['专业'] == value['专业']:
                                        flag = False
                                        break
                                if flag is True:
                                    report_[k].append(value)

                        elif k == '工作经历':
                            if values is not list:
                                continue
                            for value in values:
                                flag = True
                                for e in report_[k]:
                                    if e['公司名称'] == value['公司名称'] and e['职位'] == value['职位'] and e['工作时间'] == value[
                                        '工作时间']:
                                        flag = False
                                        break
                                if flag is True:
                                    report_[k].append(value)

                    else:
                        report_[k] = values
        return report_

    openai.api_key = get_api_key()
    # 掩去电话和邮箱
    resource_masked = data_masker.mask(resource)
    # 检查文字长度，超过1000的，向前匹配句号分号，从其之前断开。
    # 若未能匹配到（真的会匹配不到吗！？），则按照limit断开。
    resource_masked["content_masked"] = lengthChecker(resource_masked["content_masked"])
    content_pieces = []
    # resource_masked["content_masked"]=[piece1,piece2,piece3]
    for piece in resource_masked["content_masked"]:
        question = piece + prompt_
        try:
            rsp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": question},
                    {"max_tokens": 16000},
                ],
                temperature=0.1
            )
        except:
            return None
        content = rsp['choices'][0]["message"]["content"]
        logger(content, 'raw')
        content = trim(content)
        logger(content, 'trimmed')
        # 解码电话和邮箱
        content = data_masker.demask(content, resource_masked)
        logger(content, 'de_masked')

        content_pieces.append(eval(content))
    return senseDisambiguate(content_pieces)


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


if __name__ == '__main__':
    # check_proxy()
    reports = {}
    for i in range(4, 5):
        prompt = get_prompt('prompts/extract_prompt')
        raw_resume = get_resume_txt('pdf_txt/' + str(i) + '.txt')
        report = gpt3_original(raw_resume, prompt)
        reports[str(i)] = report
        print(report)

    with open('test_dict', 'wb') as f:
        pickle.dump(reports, f)
    print()
