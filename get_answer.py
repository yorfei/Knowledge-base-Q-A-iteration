from pd_utils import pd_excel_read,pd_concat
from llm_chat import ask_llm


def get_answer_from_question_and_content(df):
    s_prompt = '《口袋方舟》是面向全年龄段的UGC互动内容体验平台,平台提供功能强大的编辑器,便捷易用的特点,让创作者可以轻松制作出任何类型的互动内容,实现想法,发挥创意,与朋友们一起创造多彩的虚拟体验!下面的文本来自于他们的Api文档，主题是{title}，请仔细分析这些文本，告诉我这个文本可以回答哪些问题，后续这些问题会作为「口袋方舟」的客服FAQ'

    df["回答"] = df.apply(lambda x: _get_answer_from_question_and_content(x["问题"], x["原文"],x["来源"], s_prompt=s_prompt),
                          axis=1)


def question_and_content_excel_to_answer(excel_file_path):
    data = pd_excel_read(excel_file_path)
    df = get_answer_from_question_and_content(data)
    if df is None:
        df = data
    else:
        df = pd_concat([df, data])
    df.to_excel(excel_file_path, engine='xlsxwriter')
    return excel_file_path


def _get_answer_from_question_and_content(question, content,title, s_prompt=None):
    print(question, '===============================Q')

    s_prompt = f'《口袋方舟》是面向全年龄段的UGC互动内容体验平台,平台提供功能强大的编辑器,便捷易用的特点,让创作者可以轻松制作出任何类型的互动内容,实现想法,发挥创意,与朋友们一起创造多彩的虚拟体验!下面的文本来自于他们的教程，主题是{title}'

    if s_prompt:
        s_prompt = s_prompt
    else:
        s_prompt = '你是一位善于阅读文章并回答问题的学者。请根据下面的文章内容给出回答，回答不超过500字'

    prompt = f'''x`x`{s_prompt}：

---

{content}
---

说明：
- 从《口袋方舟》客服的角度回答问题，请严格基于上方的文本内容回答，内容会用于FAQ。
- 如果内容不足以回答问题，请回复“无法回复这个问题”。
- 如果你觉得这个问题用户不会问到，请直接回复“无法回复这个问题！”。
- 请严格的确保问题表达的含义和上面文本内容是一致的，如果不一致则纠正问题后，再根据推测可能想要问的问题来回答
- 使用TS语言编写所有相关代码。
- 当需要你提供代码时，但教程中没有相应函数或代码示例，请回复“缺少知识，无法回答”。
- 避免引入非《口袋方舟》的游戏引擎代码或概念。
- 如果回答中需要代码示例，且教程内容包含，应加上示例；如果不需要或教程不包含相关代码，不要加示例。
- 《口袋方舟》API默认可用，无需使用import导入，所以不要在代码示例中出现import口袋方舟的任何API。

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