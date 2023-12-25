import json
import os
import re

import openai
import pandas as pd
import requests


def pd_concat(df_list):
    return pd.concat(df_list)


def pd_from_dict(data):
    return pd.DataFrame.from_dict(data)


def read_txt_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def split_text(text, max_length=1000):
    sentences = re.split(r'[。]', text)
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) <= max_length:
            chunk += sentence
        else:
            chunks.append(chunk)
            chunk = sentence
    chunks.append(chunk)
    return chunks


def question_json_to_dataframe(json_obj):
    data = {"问题": [], "标签": []}  # 标签：文中提到的事例/主要回答的问题/还能回答的问题
    for tag, questions in json_obj.items():
        data["问题"].extend(questions)
        data["标签"].extend([tag] * len(questions))
    return pd_from_dict(data)


def ask_llm(content, channel, model=None):
    # Chato非流式
    if channel == 'Chato':
        Slug = 'Chato bot slug'
        url = f"https://api.chato.cn/chato/api-public/domains/{Slug}/chat"
        headers = {
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            "p": content,
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        return json.loads(response.text)['data']['content']

    # 微软Openai
    if channel == 'Azure':
        openai.api_base = "Azure base url"
        openai.api_key = "Azure Key"
        openai.api_type = "azure"
        messages = [
            {"role": "user", "content": content},
        ]
        # print(messages,model)
        response = openai.ChatCompletion.create(
            engine=model,
            messages=messages,
            temperature=0.1,
        )
        return response['choices'][0]['message']['content']
    # Openai
    if channel == 'Openai':
        openai.api_base = "https://api.openai.com/v1/" # 或者用代理地址
        openai.api_key = "Openai Key"
        messages = [
            {"role": "user", "content": content},
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.1,
        )
        return response['choices'][0]['message']['content']


def directory_files_to_tag_and_question(directory_file, document):
    df = None
    for filename in os.listdir(directory_file):
        if filename == '.DS_Store':
            continue
        file_path = os.path.join(directory_file, filename)
        print(file_path)
        df1 = extract_question(file_path, title=filename, url=None, filename=filename)
        if df1 is None:
            continue
        if df is None:
            df = df1
        else:
            df = pd_concat([df, df1])

    df.to_excel("%s.xlsx" % document, index=False)
    return "%s.xlsx"


def extract_question(file_path, title=None, url=None):
    content = read_txt_from_file(file_path)
    length = len(content)
    if length == 0:
        return None
    if length > 1000:
        contents = split_text(content, 1000)
    else:
        contents = [content]
    df_list = []
    for chunk in contents:
        s_prompt = f'''《口袋方舟》是面向全年龄段的UGC互动内容体验平台,平台提供功能强大的编辑器,便捷易用的特点,让创作者可以轻松制作出任何类型的互动内容,实现想法,发挥创意,与朋友们一起创造多彩的虚拟体验!下面的文本来自于他们的教程文档，主题是{title}，请仔细分析，告诉我这个文本可以回答哪些问题，后续这些问题会作为「口袋方舟」的客服FAQ'''
        df = extract_question_from_content(chunk, s_prompt=s_prompt)
        if df is not None:
            df["原文"] = chunk
            df_list.append(df)
    df = pd_concat(df_list)
    if title:
        file_path = title
    df["来源"] = file_path
    if url:
        df["原文链接"] = url

    return df


def extract_question_from_content(content, retries=3, s_prompt=None):
    length = len(content)
    c1 = round(length / 1000)
    c2 = round(length / 800)
    final_prompt = '你是一位善于读书的学者。下面这篇这段文本来自书本扫描件，有比较多的ocr识别错误，也有不必要的页眉页脚干扰。请忽略所有的干扰项，通读文档，告诉我这篇文档可以回答哪些问题。'
    if s_prompt:
        final_prompt = s_prompt
    print(content)
    prompt = f'''{final_prompt}请提供至少{c1}个主要问题，和{c2}个次要问题。

……

--- 

{content}


---
注意：
1. 「口袋方舟」是面向于开发者的，所以问题尽量考虑技术方向
2.请以json 格式给出可能的问题,问题里不要带“这段对话”““这个文本”“这个”等信息，问题要尽可能的覆盖文本的各个部分
3.问题最终会作为「口袋方舟」的FAQ给到客服部门，所以我需要用到这个编辑器的游戏开发者会真实问到的问题，问题要具体

{{
"主要回答的问题":[],
"还能回答的问题":[]
}}
'''
    for retry_count in range(retries):
        try:
            result = json.loads(ask_llm(prompt, channel='Chato'))
            print(result)
            df = question_json_to_dataframe(result)
            return df
        except:
            if retry_count == retries - 1:
                print("An error occurred and all retries failed.")
                return None
            else:
                print(f"An error has occurred. Retrying in 5 seconds. ({retries - retry_count - 1} attempts left)")
    return None


if __name__ == '__main__':
    base_directory = '/Users/baixing/Desktop/'
    document = 'sample_folder'
    directory_file = base_directory + document
    directory_files_to_tag_and_question(directory_file, document)