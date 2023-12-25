from pd_utils import pd_from_dict


def question_json_to_dataframe(json_obj):
    data = {"问题": [], "标签": []}  # 标签：文中提到的事例/主要回答的问题/还能回答的问题
    for tag, questions in json_obj.items():
        data["问题"].extend(questions)
        data["标签"].extend([tag] * len(questions))
    return pd_from_dict(data)
