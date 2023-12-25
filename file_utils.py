import re


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