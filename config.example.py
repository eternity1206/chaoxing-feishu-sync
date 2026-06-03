import os

# ============================================================
# 学习通配置
# ============================================================

# 方式一：使用账号密码自动登录（推荐）
CHAOXING_USERNAME = os.environ.get("CHAOXING_USERNAME", "你的手机号或学号")
CHAOXING_PASSWORD = os.environ.get("CHAOXING_PASSWORD", "你的密码")

# 方式二：手动填入 Cookie 字符串（如果自动登录失败，可改用此方式）
CHAOXING_COOKIE = os.environ.get("CHAOXING_COOKIE", "")

# ============================================================
# 飞书多维表格配置
# ============================================================

# 飞书开放平台应用的 App ID
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "你的飞书App ID")

# 飞书开放平台应用的 App Secret
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "你的飞书App Secret")

# 飞书多维表格的 app_token（从多维表格 URL 中获取）
# 例如 URL 为 https://xxx.feishu.cn/base/BITABLExxxx，则 app_token 为 BITABLExxxx
FEISHU_APP_TOKEN = os.environ.get("FEISHU_APP_TOKEN", "你的多维表格app_token")

# 飞书多维表格的 table_id（从多维表格 URL 中获取，点击表格名称旁的感叹号可看到）
FEISHU_TABLE_ID = os.environ.get("FEISHU_TABLE_ID", "你的多维表格table_id")
