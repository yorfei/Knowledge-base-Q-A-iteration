import pandas as pd


def pd_from_dict(data):
    return pd.DataFrame.from_dict(data)


def pd_concat(df_list):
    return pd.concat(df_list)


def pd_excel_read(file_path):
    return pd.read_excel(file_path)


def pd_to_excel(df, file_path):
    return df.to_excel(file_path)