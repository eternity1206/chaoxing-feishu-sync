# 学习通作业同步到飞书多维表格

自动抓取学习通未完成作业，同步到飞书多维表格并显示倒计时。

## 功能特性

- 自动登录学习通（支持账号密码或 Cookie）
- 抓取所有未完成作业（课程名、作业标题、截止时间）
- 自动同步到飞书多维表格
- 支持 GitHub Actions 定时自动同步

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/eternity1206/chaoxing-feishu-sync
pip install -r requirements.txt
```

### 2. 配置凭据

复制示例配置文件为 `config.py`，然后填写你的凭据：

```bash
cp config.example.py config.py
```

编辑 `config.py`，填写你的学习通账号和飞书配置：

```python
CHAOXING_USERNAME = "你的手机号或学号"
CHAOXING_PASSWORD = "你的密码"

FEISHU_APP_ID = "你的飞书App ID"
FEISHU_APP_SECRET = "你的飞书App Secret"
FEISHU_APP_TOKEN = "你的多维表格app_token"
FEISHU_TABLE_ID = "你的多维表格table_id"
```

> 也可以通过设置环境变量来配置（优先级高于 config.py），参见 `.env.example`。

### 3. 配置飞书多维表格

#### 3.1 创建飞书应用

1. 打开 [飞书开放平台](https://open.feishu.cn/app)
2. 创建「企业自建应用」→ 名称随意（如"作业同步"）
3. 进入应用 → 「凭证与基础信息」→ 记下 **App ID** 和 **App Secret**
4. 「权限管理」→ 添加权限 `bitable:app`
5. 「版本管理与发布」→ 创建版本 → 发布

#### 3.2 创建多维表格

1. 飞书左侧栏「多维表格」→「新建空白表格」
2. 添加 4 个字段：
   - 作业ID（**数字**）
   - 课程名称（文本）
   - 作业标题（文本）
   - 截止时间（多行文本）

3. 点击右上角「分享」→ 复制链接，提取：
   - `app_token`：URL 中 `base/` 后面的字符串
   - `table_id`：URL 中 `table=` 后面的字符串

#### 3.3 添加应用为协作者（关键步骤）

1. 打开多维表格 → 右上角「分享」
2. 搜索你创建的应用名称（如"作业同步"）
3. 权限设为「可编辑」→ 确认添加

> **必须完成此步骤**，否则应用无法写入数据

### 4. 运行同步

```bash
python main.py
```

看到 `同步完成，共写入 X 条新记录` 即表示成功！

## GitHub Actions 自动同步

1. Fork 本项目到你的 GitHub
2. 进入仓库 → Settings → Secrets and variables → Actions
3. 添加以下 Secrets：
   - `CHAOXING_USERNAME`
   - `CHAOXING_PASSWORD`
   - `FEISHU_APP_ID`
   - `FEISHU_APP_SECRET`
   - `FEISHU_APP_TOKEN`
   - `FEISHU_TABLE_ID`

4. 每 2 小时会自动同步一次，也可手动触发

## 项目结构

```
.
├── config.py              # 本地配置文件（不提交，请从 config.example.py 复制）
├── config.example.py      # 配置文件示例
├── login.py               # 学习通登录模块
├── fetcher.py             # 作业抓取模块
├── feishu_sync.py         # 飞书同步模块
├── main.py                # 主程序
├── export_csv.py          # CSV导出（备用）
├── requirements.txt       # 依赖
├── .env.example           # 环境变量示例
└── .github/workflows/
    └── sync.yml           # GitHub Actions 配置
```

## 常见问题

**Q: 为什么提示"应用未添加为协作者"？**
A: 必须手动在多维表格分享设置中添加应用为协作者，这是飞书的安全机制。

**Q: 如何获取 Cookie 方式登录？**
A: 浏览器 F12 → Network → 找到学习通请求 → 复制 Cookie 字符串到 `CHAOXING_COOKIE`。

**Q: 支持哪些学习通账号类型？**
A: 支持手机号、学号等常见账号类型。

## License

MIT
