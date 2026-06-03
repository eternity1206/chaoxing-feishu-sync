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

# 获取应用信息
app_info_url = "https://open.feishu.cn/open-apis/application/v6/applications"
resp2 = requests.get(app_info_url, headers=headers)
print(f"应用信息: {resp2.json()}")

# 尝试用另一种方式添加协作者
# 使用 drive:file:write 权限
add_collab_url = f"https://open.feishu.cn/open-apis/drive/v1/files/{config.FEISHU_APP_TOKEN}/collaborators"
payload = {
    "collaborator_type": "app",
    "app_id": config.FEISHU_APP_ID,
    "perm": "edit"
}
resp3 = requests.post(add_collab_url, headers=headers, json=payload)
print(f"\n添加协作者响应: {resp3.status_code}")
print(f"响应内容: {resp3.text[:500]}")
