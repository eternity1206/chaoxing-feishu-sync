import requests
import config

# 1. 获取 tenant_access_token
token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
resp = requests.post(token_url, json={
    "app_id": config.FEISHU_APP_ID,
    "app_secret": config.FEISHU_APP_SECRET,
})
print(f"获取token响应: {resp.json()}")

data = resp.json()
if data.get("code") != 0:
    print("获取token失败！请检查App ID和App Secret是否正确")
    exit(1)

token = data["tenant_access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 2. 尝试从 wiki URL 获取信息
wiki_token = "你的wiki_token"
wiki_url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={wiki_token}"
resp2 = requests.get(wiki_url, headers=headers)
print(f"\nWiki节点信息: {resp2.json()}")

# 3. 尝试列出所有可用的 Bitable
# 用 wiki token 作为 app_token 试试
test_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{wiki_token}/tables"
resp3 = requests.get(test_url, headers=headers)
print(f"\n尝试wiki token作为app_token: {resp3.json()}")
