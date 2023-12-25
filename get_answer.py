from pd_utils import pd_excel_read,pd_concat
from llm_chat import ask_llm


def question_and_content_excel_to_answer(excel_file_path):
    data = pd_excel_read(excel_file_path)
    df = get_answer_from_question_and_content(data)
    if df is None:
        df = data
    else:
        df = pd_concat([df, data])
    df.to_excel(excel_file_path, engine='xlsxwriter')
    return excel_file_path


def get_answer_from_question_and_content(df):
    df["回答"] = df.apply(lambda x: _get_answer_from_question_and_content(x["问题"], x["原文"],x["来源"]),
                          axis=1)



def _get_answer_from_question_and_content(question, content,title):
    print(question, '===============================Q')
    s_prompt = f'下面的文本来自于xx，主题是{title}'

    if s_prompt:
        s_prompt = s_prompt
    else:
        s_prompt = '你是一位善于阅读文章并回答问题的学者。请根据下面的文章内容给出回答，回答不超过500字'

    prompt = f'''x`x`{s_prompt}：

---

{content}
---

说明：
- xxx
- yyy

---
问题：
{question}
---

'''
    try:
        result = ask_llm(prompt, channel='Chato')
    except Exception as e:
        print(result, "++++")
    return result


if __name__ == '__main__':
    excel_file_path = '/app/services/xxx.xlsx' # xlsx文件需要有 问题、原文和来源3个字段
    question_and_content_excel_to_answer(excel_file_path)