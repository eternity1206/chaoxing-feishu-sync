import base64
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import config


# 学习通 AES 加密的固定密钥和 IV（从前端 JS 逆向得到）
_TRANSFER_KEY = "u2oh6Vu^HWe4_AES"

# 登录页面 URL，用于获取初始 Cookie
_LOGIN_PAGE_URL = "https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https://i.chaoxing.com"

# 登录接口 URL
_LOGIN_API_URL = "https://passport2.chaoxing.com/fanyalogin"


def _encrypt_aes(plaintext):
    """
    使用 AES-CBC 加密明文字符串，返回 base64 编码后的密文。
    加密参数：
        - 密钥: u2oh6Vu^HWe4_AES (16字节)
        - IV:   u2oh6Vu^HWe4_AES (16字节)
        - 模式: CBC
        - 填充: PKCS7
    """
    key = _TRANSFER_KEY.encode("utf-8")
    iv = _TRANSFER_KEY.encode("utf-8")
    data = plaintext.encode("utf-8")
    cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return base64.b64encode(encrypted).decode("utf-8")


def login(username, password):
    """
    自动登录学习通，返回登录成功的 requests.Session 对象。
    该 Session 已包含有效的登录 Cookie，可直接用于后续 API 请求。
    """
    session = requests.Session()

    # 第一步：访问登录页面，获取初始 Cookie（route、JSESSIONID 等）
    print("[login] 正在访问登录页面获取初始 Cookie...")
    session.get(_LOGIN_PAGE_URL, headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    })

    # 第二步：对用户名和密码进行 AES 加密
    encrypted_uname = _encrypt_aes(username)
    encrypted_password = _encrypt_aes(password)

    # 第三步：构造登录请求
    login_data = {
        "fid": "-1",
        "uname": encrypted_uname,
        "password": encrypted_password,
        "refer": "https%3A%2F%2Fi.chaoxing.com",
        "t": "true",
        "forbidotherlogin": "0",
        "validate": "",
        "doubleFactorLogin": "0",
        "independentId": "0",
    }

    login_headers = {
        "Host": "passport2.chaoxing.com",
        "Connection": "keep-alive",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Origin": "https://passport2.chaoxing.com",
        "Referer": "https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https://i.chaoxing.com",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    # 第四步：发送登录请求
    print("[login] 正在发送登录请求...")
    resp = session.post(_LOGIN_API_URL, headers=login_headers, data=login_data)

    # 第五步：检查登录结果
    result = resp.json()
    if result.get("status"):
        print("[login] 登录成功！")
        # 登录成功后访问相关域名，让 Cookie 完整生效
        ua = login_headers["User-Agent"]
        for url in [
            "https://i.chaoxing.com",
            "https://mooc1.chaoxing.com",
            "https://mooc2-ans.chaoxing.com",
        ]:
            try:
                session.get(url, headers={"User-Agent": ua}, timeout=10)
            except Exception:
                pass
        return session
    else:
        msg = result.get("msg", "未知错误")
        raise RuntimeError(f"学习通登录失败: {msg}")


def login_with_config():
    """
    使用 config.py 中配置的账号密码进行登录。
    如果 config 中已有有效的 CHAOXING_COOKIE（手动填写的），
    则直接构建 Session 使用该 Cookie，不进行自动登录。
    """
    # 调试信息：打印读取到的配置
    print(f"[login] 读取到的配置: CHAOXING_USERNAME={repr(config.CHAOXING_USERNAME)}, CHAOXING_PASSWORD={'*'*len(config.CHAOXING_PASSWORD) if config.CHAOXING_PASSWORD else ''}, CHAOXING_COOKIE={'已配置' if config.CHAOXING_COOKIE else '未配置'}")

    # 如果已手动配置了 Cookie，则直接使用，跳过自动登录
    if config.CHAOXING_COOKIE:
        print("[login] 检测到已配置 CHAOXING_COOKIE，直接使用手动 Cookie")
        session = requests.Session()
        session.headers.update({
            "Cookie": config.CHAOXING_COOKIE,
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        })
        return session

    # 否则使用账号密码自动登录
    if not config.CHAOXING_USERNAME or not config.CHAOXING_PASSWORD:
        raise RuntimeError(
            "请在 config.py 或环境变量中配置 CHAOXING_USERNAME 和 CHAOXING_PASSWORD，"
            "或者手动填写 CHAOXING_COOKIE"
        )

    print("[login] 使用账号密码自动登录学习通...")
    return login(config.CHAOXING_USERNAME, config.CHAOXING_PASSWORD)
