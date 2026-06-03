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

# 尝试用 bitable 的协作者接口
# 注意：这个接口需要 bitable:app:collaborator:add 权限
add_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/collaborators"
payload = {
    "collaborator_type": "app",
    "app_id": config.FEISHU_APP_ID,
    "perm": "edit"
}

resp2 = requests.post(add_url, headers=headers, json=payload)
print(f"状态码: {resp2.status_code}")
print(f"响应: {resp2.text}")

# 尝试 GET 现有协作者
get_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/collaborators"
resp3 = requests.get(get_url, headers=headers)
print(f"\n现有协作者: {resp3.text[:500]}")
