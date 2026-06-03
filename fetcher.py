import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import config


UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

HOMEWORK_API = "https://mooc1.chaoxing.com/mooc-ans/mooc2/work/list"
COURSE_MIDDLE_URL = "https://mooc1.chaoxing.com/visit/stucoursemiddle"


def _get_default_courses():
    raw = [
        ("205222736", "146480300", "336732796", "操作系统课程设计"),
        ("260827083", "140087717", "336732796", "编译原理"),
        ("260640980", "139559920", "336732796", "操作系统课程"),
        ("231682013", "142791204", "336732796", "人工智能导论"),
        ("260769923", "139928371", "336732796", "软件工程导论"),
    ]
    return [
        {"courseid": cid, "clazzid": clid, "cpi": cpi, "name": name}
        for cid, clid, cpi, name in raw
    ]


def get_course_list(session):
    print("[fetcher] 正在获取课程列表...")

    courses = []
    try:
        list_url = (
            "https://mooc2-ans.chaoxing.com/visit/courses/list"
            "?v=1&rss=1&start=0&size=500&catalogId=0&searchname="
        )
        resp = session.get(list_url, headers={"User-Agent": UA}, timeout=15)
        resp.raise_for_status()

        pattern = re.compile(
            r'courseid=(\d+)&clazzid=(\d+)&cpi=(\d+)'
        )
        name_pattern = re.compile(r'style="word-break: break-all;"\s*title="(.*?)"')

        links = pattern.findall(resp.text)
        names = name_pattern.findall(resp.text)

        seen = set()
        name_idx = 0
        for match in links:
            course_id, class_id, cpi = match
            key = (course_id, class_id)
            if key in seen:
                continue
            seen.add(key)
            name = names[name_idx] if name_idx < len(names) else f"课程_{course_id}"
            name_idx += 1
            courses.append({
                "courseid": course_id,
                "clazzid": class_id,
                "cpi": cpi,
                "name": name.replace("&nbsp;", " ").strip(),
            })
    except Exception as e:
        print(f"[fetcher] 从 HTML 解析课程列表失败: {e}")

    if not courses:
        print("[fetcher] 使用默认课程列表...")
        courses = _get_default_courses()

    print(f"[fetcher] 共获取到 {len(courses)} 门课程（已去重）")
    return courses


def _get_work_enc(session, course):
    url = (
        f"{COURSE_MIDDLE_URL}"
        f"?courseid={course['courseid']}"
        f"&clazzid={course['clazzid']}"
        f"&cpi={course['cpi']}"
        f"&ismooc2=1"
    )
    resp = session.get(url, headers={"User-Agent": UA}, timeout=15, allow_redirects=True)
    resp.raise_for_status()

    enc_match = re.search(r'id="workEnc"[^>]*value="([a-f0-9]{32})"', resp.text)
    if enc_match:
        return enc_match.group(1)

    return ""


def get_homework_list(session, course):
    enc = _get_work_enc(session, course)

    params = (
        f"?courseId={course['courseid']}"
        f"&classId={course['clazzid']}"
        f"&cpi={course['cpi']}"
        f"&enc={enc}"
        f"&status=1"
    )
    url = HOMEWORK_API + params
    resp = session.get(url, headers={"User-Agent": UA}, timeout=15)
    resp.raise_for_status()

    homeworks = _parse_homework_html(resp.text, course)

    print(f"[fetcher] 课程 {course['name']} 下有 {len(homeworks)} 个未完成作业")
    return homeworks


def _parse_homework_html(html, course):
    soup = BeautifulSoup(html, "lxml")
    homeworks = []

    work_items = soup.find_all("li")
    for item in work_items:
        try:
            onclick = item.get("onclick", "")
            data_url = item.get("data", "")
            if "goTask" not in onclick and not data_url:
                continue

            title_p = item.find("p", class_=lambda c: c and "overHidden" in c)
            if not title_p:
                title_p = item.find("p")
            if not title_p:
                continue
            title = title_p.get_text(strip=True)

            # 从完整文本中提取剩余时间
            full_text = item.get_text(strip=True)
            deadline = _parse_remaining_time(full_text)

            # 如果没有剩余时间（已过期），跳过
            if deadline is None:
                continue

            work_id_match = re.search(r'workId=(\d+)', data_url)
            hw_id = work_id_match.group(1) if work_id_match else f"{course['courseid']}_{title}"

            homeworks.append({
                "hw_id": hw_id,
                "title": title,
                "deadline": deadline,
            })
        except Exception:
            continue

    return homeworks


def _parse_remaining_time(text):
    from datetime import timedelta

    days = 0
    hours = 0
    minutes = 0
    seconds = 0

    # 检查是否有"剩余"关键字，没有则说明不是未完成作业
    if "剩余" not in text:
        return None  # 返回 None 表示不是未完成作业

    d_match = re.search(r"剩余(\d+)天", text)
    h_match = re.search(r"剩余.*?(\d+)小时|(\d+)小时", text)
    m_match = re.search(r"(\d+)分钟", text)
    s_match = re.search(r"(\d+)秒", text)

    if d_match:
        days = int(d_match.group(1))
    if h_match:
        hours = int(h_match.group(1) or h_match.group(2))
    if m_match:
        minutes = int(m_match.group(1))
    if s_match:
        seconds = int(s_match.group(1))

    if days or hours or minutes or seconds:
        return datetime.now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    # 有"剩余"但没有具体时间，可能是"剩余0小时"之类，也算未完成作业
    return datetime.now() + timedelta(days=7)


def fetch_all_homework(session):
    courses = get_course_list(session)

    all_homework = []
    for course in courses:
        try:
            hw_list = get_homework_list(session, course)
            for hw in hw_list:
                hw["course_name"] = course["name"]
            all_homework.extend(hw_list)
        except Exception as e:
            print(f"[fetcher] 获取课程 {course['name']}({course['courseid']}) 作业失败: {e}")

    print(f"[fetcher] 汇总完成，共 {len(all_homework)} 个待同步作业")
    return all_homework
