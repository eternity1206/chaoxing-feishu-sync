import time
import requests
import config


FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"


def get_tenant_access_token():
    """
    使用 App ID 和 App Secret 获取飞书的 tenant_access_token。
    该 token 用于调用飞书开放平台的其他 API。
    """
    url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": config.FEISHU_APP_ID,
        "app_secret": config.FEISHU_APP_SECRET,
    }
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 0:
        raise RuntimeError(f"获取 tenant_access_token 失败: {data}")

    token = data["tenant_access_token"]
    print(f"[feishu] 成功获取 tenant_access_token")
    return token


def _auth_headers(token):
    """构建带 Authorization 的请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def list_existing_records(token):
    """
    获取飞书多维表格中已存在的所有记录的「作业ID」字段值。
    返回一个集合，方便后续快速判断某条作业是否已录入。
    """
    existing_ids = set()
    page_token = None
    app_token = config.FEISHU_APP_TOKEN
    table_id = config.FEISHU_TABLE_ID

    while True:
        url = (
            f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}"
            f"/tables/{table_id}/records"
        )
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token

        resp = requests.get(url, headers=_auth_headers(token), params=params)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != 0:
            raise RuntimeError(f"获取已有记录失败: {data}")

        items = data.get("data", {}).get("items", [])
        for item in items:
            fields = item.get("fields", {})
            hw_id = fields.get("作业ID", "")
            # 飞书多维表格的文本字段可能返回列表格式
            if isinstance(hw_id, list):
                hw_id = hw_id[0].get("text", "") if hw_id else ""
            if hw_id:
                existing_ids.add(str(hw_id))

        # 判断是否有下一页
        has_more = data.get("data", {}).get("has_more", False)
        if not has_more:
            break
        page_token = data.get("data", {}).get("page_token")

    print(f"[feishu] 多维表格中已有 {len(existing_ids)} 条记录")
    return existing_ids


def sync_homework(token, homework_list):
    """
    将作业列表同步写入飞书多维表格。
    - 先查询已有记录，过滤掉重复作业
    - 使用批量创建接口写入新作业
    - 每批最多 500 条，超过则分批
    """
    # 获取已存在的作业 ID 集合
    existing_ids = list_existing_records(token)

    # 过滤出新作业
    new_homework = [hw for hw in homework_list if hw["hw_id"] not in existing_ids]
    print(f"[feishu] 待写入新作业: {len(new_homework)} 条（已过滤 {len(homework_list) - len(new_homework)} 条重复）")

    if not new_homework:
        print("[feishu] 没有需要同步的新作业")
        return

    # 构建飞书记录列表
    records = []
    for hw in new_homework:
        # 将 datetime 转为毫秒时间戳（飞书日期时间字段要求）
        deadline_str = hw["deadline"].strftime("%Y-%m-%d %H:%M")
        records.append({
            "fields": {
                "作业ID": int(hw["hw_id"]),
                "课程名称": hw["course_name"],
                "作业标题": hw["title"],
                "截止时间": deadline_str,
            }
        })

    # 分批写入，每批最多 500 条
    batch_size = 500
    total_created = 0
    app_token = config.FEISHU_APP_TOKEN
    table_id = config.FEISHU_TABLE_ID

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        url = (
            f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}"
            f"/tables/{table_id}/records/batch_create"
        )
        payload = {"records": batch}

        resp = requests.post(url, headers=_auth_headers(token), json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != 0:
            raise RuntimeError(f"批量创建记录失败: {data}")

        created = len(data.get("data", {}).get("records", []))
        total_created += created
        print(f"[feishu] 第 {i // batch_size + 1} 批写入成功，本批 {created} 条")

        # 批量写入间隔 200ms，避免触发频率限制
        if i + batch_size < len(records):
            time.sleep(0.2)

    print(f"[feishu] 同步完成，共写入 {total_created} 条新记录")
