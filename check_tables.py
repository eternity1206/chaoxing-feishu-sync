import requests
import config

# 获取 tenant_access_token
token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
resp = requests.post(token_url, json={
    "app_id": config.FEISHU_APP_ID,
    "app_secret": config.FEISHU_APP_SECRET,
})
data = resp.json()
if data.get("code") != 0:
    print(f"获取token失败: {data}")
    exit(1)

token = data["tenant_access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 列出多维表格中的所有 table
list_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables"
resp2 = requests.get(list_url, headers=headers)
print(f"状态码: {resp2.status_code}")
print(f"响应: {resp2.json()}")
