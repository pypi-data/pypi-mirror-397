#!/usr/bin/env python3
"""
死鎖監控工具 - Deadlock Monitor Tool

用於運行時檢查SpeakUB的鎖定狀態和死鎖風險。
提供命令行界面來診斷並發問題。
"""

from speakub.utils.deadlock_detector import get_deadlock_detector
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# 添加專案路徑以便匯入模組
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def format_stats_for_display(stats: Dict[str, Any]) -> str:
    """格式化統計信息為易讀格式"""
    lines = []
    lines.append("🔒 SpeakUB 鎖定監控統計")
    lines.append("=" * 50)

    # 整體統計
    summary = stats.get("summary", {})
    lines.append(f"總鎖定數量: {summary.get('total_locks', 0)}")
    lines.append(f"總獲取次數: {summary.get('total_acquires', 0)}")
    lines.append(f"總競爭時間: {summary.get('total_contention_time', 0):.3f}s")
    lines.append(
        f"平均競爭時間: {summary.get('avg_contention_per_acquire', 0)*1000:.1f}ms")
    lines.append("")

    # 各鎖定詳細信息
    locks = stats.get("locks", {})
    if locks:
        lines.append("鎖定詳細信息:")
        lines.append("-" * 30)
        for lock_name, lock_stats in locks.items():
            lines.append(
                f"🔑 {lock_name} ({lock_stats.get('type', 'unknown')})")
            lines.append(f"  獲取次數: {lock_stats.get('acquire_count', 0)}")
            lines.append(f"  等待次數: {lock_stats.get('wait_count', 0)}")
            lines.append(
                f"  競爭時間: {lock_stats.get('contention_time', 0):.3f}s")
            lines.append(
                f"  平均競爭: {lock_stats.get('avg_contention_ms', 0):.1f}ms")
            lines.append(f"  當前持有: {lock_stats.get('holding_thread') or '無'}")
            lines.append(
                f"  等待隊列: {len(lock_stats.get('waiting_threads', []))}")
            lines.append("")

    # 警告信息
    warnings = stats.get("warnings", [])
    if warnings:
        lines.append("⚠️  警告信息:")
        lines.append("-" * 30)
        for warning in warnings[:10]:  # 只顯示前10個警告
            lines.append(f"  {warning}")
        if len(warnings) > 10:
            lines.append(f"  ...還有{len(warnings) - 10}個警告")
        lines.append("")

    # 死鎖檢測
    deadlock_info = stats.get("deadlock_detection", [])
    if deadlock_info:
        lines.append("🚨 潛在死鎖風險:")
        lines.append("-" * 30)
        for deadlock in deadlock_info[:5]:  # 只顯示前5個
            lines.append(f"  {deadlock}")
        lines.append("")

    # 時間戳
    timestamp = stats.get("timestamp", 0)
    if timestamp:
        lines.append(
            f"檢查時間: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}")

    return "\n".join(lines)


def check_health() -> int:
    """檢查系統健康狀態，返回退出碼"""
    detector = get_deadlock_detector()
    stats = detector.get_monitoring_stats()

    warnings = stats.get("warnings", [])
    deadlock_risks = stats.get("deadlock_detection", [])

    exit_code = 0

    if deadlock_risks:
        print("🚨 發現潛在死鎖風險！")
        exit_code = 2  # 嚴重錯誤
    elif warnings:
        print(f"⚠️  發現{len(warnings)}個鎖定異常")
        exit_code = 1  # 警告
    else:
        print("✅ 系統健康，無明顯問題")
    return exit_code


def continuous_monitor(interval: float = 5.0, duration: Optional[float] = None) -> None:
    """持續監控模式"""
    detector = get_deadlock_detector()
    start_time = time.time()

    print(f"🔄 開始持續監控 (間隔: {interval}s)")
    print("按 Ctrl+C 停止監控")
    print("=" * 60)

    try:
        while True:
            if duration and (time.time() - start_time) > duration:
                break

            stats = detector.get_monitoring_stats()
            print(format_stats_for_display(stats))
            print("-" * 60)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n🛑 監控已停止")


def export_stats(output_file: str) -> None:
    """匯出統計信息到文件"""
    detector = get_deadlock_detector()
    stats = detector.get_monitoring_stats()

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"✅ 統計信息已匯出到: {output_file}")

    except Exception as e:
        print(f"❌ 匯出失敗: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="SpeakUB 死鎖監控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python deadlock_monitor.py status          # 顯示當前狀態
  python deadlock_monitor.py health          # 檢查系統健康
  python deadlock_monitor.py monitor         # 持續監控
  python deadlock_monitor.py export stats.json  # 匯出統計
        """
    )

    parser.add_argument(
        'command',
        choices=['status', 'health', 'monitor', 'export'],
        help='要執行的命令'
    )

    parser.add_argument(
        'output_file',
        nargs='?',
        help='匯出命令的輸出文件路徑'
    )

    parser.add_argument(
        '--interval', '-i',
        type=float,
        default=5.0,
        help='監控間隔秒數 (預設: 5.0)'
    )

    parser.add_argument(
        '--duration', '-d',
        type=float,
        help='監控持續時間秒數 (預設: 無限)'
    )

    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='以JSON格式輸出'
    )

    args = parser.parse_args()

    # 執行命令
    if args.command == 'status':
        detector = get_deadlock_detector()
        stats = detector.get_monitoring_stats()

        if args.json:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print(format_stats_for_display(stats))

    elif args.command == 'health':
        exit_code = check_health()
        sys.exit(exit_code)

    elif args.command == 'monitor':
        continuous_monitor(args.interval, args.duration)

    elif args.command == 'export':
        if not args.output_file:
            print("❌ export 命令需要指定輸出文件")
            sys.exit(1)
        export_stats(args.output_file)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
