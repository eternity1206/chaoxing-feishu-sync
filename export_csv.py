import csv
from datetime import datetime
import login
import fetcher


def export_homework_to_csv():
    """将作业数据导出为 CSV 文件"""
    print("[export] 正在登录学习通...")
    session = login.login_with_config()

    print("[export] 正在抓取作业...")
    homework_list = fetcher.fetch_all_homework(session)

    if not homework_list:
        print("[export] 没有作业需要导出")
        return

    # 生成文件名
    filename = f"学习通作业_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # 写入 CSV
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(['作业ID', '课程名称', '作业标题', '截止时间', '倒计时'])
        # 写入数据
        for hw in homework_list:
            deadline_str = hw['deadline'].strftime('%Y-%m-%d %H:%M')
            remaining = hw['deadline'] - datetime.now()
            days = remaining.days
            hours = remaining.seconds // 3600
            countdown = f"剩余{days}天{hours}小时"
            writer.writerow([
                hw['hw_id'],
                hw['course_name'],
                hw['title'],
                deadline_str,
                countdown
            ])

    print(f"[export] 成功导出 {len(homework_list)} 条作业到: {filename}")
    print("[export] 你可以手动将此 CSV 文件导入飞书多维表格")


if __name__ == "__main__":
    export_homework_to_csv()
