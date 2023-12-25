from pd_utils import pd_excel_read,pd_concat
import pandas as pd
import json
from llm_chat import ask_llm


def answer_check(excel_file_path):
    data = pd_excel_read(excel_file_path)
    df = answer_analysis(data)
    if df is None:
        df = data
    else:
        df = pd_concat([df, data])
    df.to_excel(excel_file_path, engine='xlsxwriter')
    return excel_file_path

def answer_analysis(df):
    df[["回答一致性", "修正方案"]] = df.apply(
        lambda x: pd.Series(_answer_analysis(x["q"], x["a"], x["content"])),
        axis=1)


def _answer_analysis(q, a, content):
    prompt = f'''下面是一组问答
    ---
    问题：
    {q}

    回答：
    {a}
    ---

    其中回答是根据背景知识生成的。
    ---
    {content}
    ---

    请思考：
    1.上述回答中，是否有无法从背景知识对应原文推导得出的内容？从而得到回答靠谱率，数值1-100。
    2.如果有无法推导得出的内容，请帮忙修改上述回答，去除不一致的地方或者去除无法推导的出的内容。

    结果请以json 格式给出，格式如下：
    {{
    "回答一致性":分数, 
    "修正方案":新的答案
    }}

    回复要求：
    1.如果「回答一致性」为100，「修正方案」无需提供，「修正方案」应回复，"修正方案":"无需修正"
    2.如果无法从背景知识推导出问题的答案，「修正方案」应回复，"修正方案":"背景知识不相关"

    '''
    retries = 1

    for retry_count in range(retries):

        try:
            result = json.loads(ask_llm(prompt, channel='Chato'))
            print(result)
            return result["回答一致性"], result["修正方案"]

        except:
            if retry_count == (retries - 1):
                print("An error occurred and all retries failed.")
                return None
            else:
                print(f"An error has occurred. Retrying in 5 seconds. ({retries - retry_count - 1} attempts left)")
    return None