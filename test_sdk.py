import os
from volcenginesdkarkruntime import Ark

# 手动配置API Key
client = Ark(base_url='https://ark.cn-beijing.volces.com/api/v3', api_key=os.getenv('ARK_API_KEY'))
MODEL_ID = "doubao-seed-1-6-lite-251015"

# 测试简单调用
try:
    resp = client.responses.create(
        model=MODEL_ID,
        input="测试",
        temperature=0.3,
        stream=False
    )
    print("SDK调用成功：", resp)
except Exception as e:
    print("SDK调用失败：", e)
    import traceback
    print(traceback.format_exc())