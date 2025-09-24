from openai import OpenAI

# 初始化OpenAI客户端
client = OpenAI(
    base_url="https://apihk.unifyllm.top/v1",
    api_key="sk-kGlFBKwr3YQieh9dtWAF0hgkaLV7UcmJA1xJ9qZXOOQfvura"
)

# 调用聊天完成接口
try:
    result = client.chat.completions.create(
        model="claude-sonnet-4-20250514",  # 或者使用其他可用模型
        messages=[
            {"role": "system", "content": "你是一个有用的AI助手。"},
            {"role": "user", "content": "你好，请介绍一下自己。"}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    # 输出结果
    print("AI回复:")
    print(result.choices[0].message.content)
    
except Exception as e:
    print(f"调用失败: {e}")