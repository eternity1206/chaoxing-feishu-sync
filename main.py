from datetime import datetime
import fetcher
import feishu_sync
import login
import config


def _display_homework(homework_list):
    print(f"\n{'='*70}")
    print(f"  共找到 {len(homework_list)} 个未完成作业")
    print(f"{'='*70}")
    print(f"{'序号':<4} {'课程名称':<16} {'作业标题':<20} {'作业ID':<12} {'截止时间'}")
    print(f"{'-'*70}")
    for i, hw in enumerate(homework_list, 1):
        deadline_str = hw['deadline'].strftime('%Y-%m-%d %H:%M')
        remaining = hw['deadline'] - datetime.now()
        days = remaining.days
        hours = remaining.seconds // 3600
        countdown = f"剩余 {days}天{hours}小时"
        print(f"{i:<4} {hw['course_name']:<16} {hw['title']:<20} {hw['hw_id']:<12} {deadline_str} ({countdown})")
    print(f"{'='*70}")


def main():
    """主函数：登录学习通 → 抓取作业 → 同步到飞书多维表格"""
    print("=" * 50)
    print(f"[main] 开始执行，时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 第一步：登录学习通，获取有效的 Session
    print("\n[main] 正在登录学习通...")
    session = login.login_with_config()

    # 第二步：从学习通抓取所有未完成作业
    print("\n[main] 正在从学习通抓取作业...")
    homework_list = fetcher.fetch_all_homework(session)
    if not homework_list:
        print("[main] 未抓取到任何待同步作业，流程结束")
        return

    # 显示作业详情
    _display_homework(homework_list)

    # 第三步：检查飞书配置，同步到飞书多维表格
    if not config.FEISHU_APP_ID or not config.FEISHU_APP_SECRET:
        print("\n[main] 飞书凭证未配置，跳过飞书同步（仅显示作业列表）")
        print("[main] 如需同步到飞书，请在 config.py 中配置 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
    else:
        print("\n[main] 正在获取飞书访问令牌...")
        token = feishu_sync.get_tenant_access_token()
        print("\n[main] 正在同步作业到飞书多维表格...")
        feishu_sync.sync_homework(token, homework_list)

    print("\n" + "=" * 50)
    print("[main] 全部流程执行完毕")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[main] 程序执行出错: {e}")
        raise
