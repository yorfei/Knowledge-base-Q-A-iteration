import json, requests, openai


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
        openai.api_base = "https://api.openai.com/v1/"  # 或者用代理地址
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
