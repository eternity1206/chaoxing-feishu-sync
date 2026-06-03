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

# 创建新的多维表格
# 需要 drive:file:write 权限
create_url = "https://open.feishu.cn/open-apis/drive/v1/files"
payload = {
    "name": "学习通作业管理表",
    "type": "bitable",
    "folder_token": ""  # 可选，指定文件夹
}

resp = requests.post(create_url, headers=headers, json=payload)
print(f"创建多维表格响应: {resp.json()}")
