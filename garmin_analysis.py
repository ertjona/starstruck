#!/usr/bin/env python3
"""
Garmin 活動分析工具
使用 garmin-cli (https://github.com/ching-kuo/garmin-cli) 讀取並分析 Garmin Connect 資料

安裝方式：
    git clone https://github.com/ching-kuo/garmin-cli.git
    cd garmin-cli
    pip install .

認證方式（擇一）：
    1. 互動登入：garmin-cli login
    2. 環境變數：export GARMIN_EMAIL=xxx GARMIN_PASSWORD=xxx
"""
import json
import subprocess
import sys
from datetime import date, timedelta


def run_garmin_cli(*args: str) -> list[dict] | dict | None:
    """執行 garmin-cli 指令，回傳 JSON 結果。"""
    cmd = ["garmin-cli", "--json"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[錯誤] {result.stderr.strip()}", file=sys.stderr)
        return None
    try:
        output = json.loads(result.stdout)
        # garmin-cli --json 輸出包裝在 {"data": [...], ...} 格式
        if isinstance(output, dict) and "data" in output:
            return output["data"]
        return output
    except json.JSONDecodeError:
        print(f"[錯誤] 無法解析輸出：{result.stdout[:200]}", file=sys.stderr)
        return None


# ── 活動相關 ────────────────────────────────────────────────────────────────

def get_recent_activities(limit: int = 20, activity_type: str | None = None) -> list[dict]:
    """取得最近的活動清單。

    activity_type 範例：running, cycling, swimming, hiking, strength_training
    欄位：id, date, name, type, distance_km, duration_min, avg_hr
    """
    args = ["activity", "list", "--limit", str(limit)]
    if activity_type:
        args += ["--type", activity_type]
    return run_garmin_cli(*args) or []


def get_activity_detail(activity_id: str) -> dict | None:
    """取得單一活動的詳細資料。"""
    return run_garmin_cli("activity", "get", activity_id)


def get_activity_weather(activity_id: str) -> dict | None:
    """取得活動當時的天氣資料。"""
    return run_garmin_cli("activity", "weather", activity_id)


# ── 健康指標 ────────────────────────────────────────────────────────────────

def get_sleep_data(days: int = 7) -> list[dict]:
    """取得睡眠資料。

    欄位：date, duration_hours, deep_min, light_min, rem_min, awake_min, score
    """
    return run_garmin_cli("health", "sleep", "--days", str(days)) or []


def get_hrv_data(days: int = 7) -> list[dict]:
    """取得 HRV（心率變異性）資料。

    欄位：date, weekly_avg, last_night, status
    """
    return run_garmin_cli("health", "hrv", "--days", str(days)) or []


def get_resting_hr(days: int = 30) -> list[dict]:
    """取得靜止心率資料。欄位：date, resting_hr"""
    return run_garmin_cli("health", "resting-hr", "--days", str(days)) or []


def get_body_battery(days: int = 7) -> list[dict]:
    """取得 Body Battery 資料。欄位：date, start_level, end_level"""
    return run_garmin_cli("health", "body-battery", "--days", str(days)) or []


def get_stress(days: int = 7) -> list[dict]:
    """取得壓力資料。欄位：date, avg_stress, max_stress"""
    return run_garmin_cli("health", "stress", "--days", str(days)) or []


def get_readiness(days: int = 7) -> list[dict]:
    """取得訓練準備度。欄位：date, score, level"""
    return run_garmin_cli("health", "readiness", "--days", str(days)) or []


def get_training_status(target_date: str | None = None) -> list[dict]:
    """取得訓練狀態（今日或指定日期）。欄位：date, training_status, load_type"""
    args = ["health", "status"]
    if target_date:
        args += ["--date", target_date]
    return run_garmin_cli(*args) or []


# ── 運動表現 ────────────────────────────────────────────────────────────────

def get_vo2max() -> list[dict]:
    """取得最新 VO2 Max。欄位：date, vo2max, sport"""
    return run_garmin_cli("performance", "vo2max") or []


def get_zones() -> list[dict]:
    """取得心率與配速區間。欄位：sport, lt_hr_bpm, lt_pace"""
    return run_garmin_cli("performance", "zones") or []


def get_thresholds() -> list[dict]:
    """取得閾值資料。欄位：sport, lt_hr_bpm, lt_pace, ftp_watts, weight_kg"""
    return run_garmin_cli("performance", "thresholds") or []


# ── 分析功能 ────────────────────────────────────────────────────────────────

def analyze_activities(days: int = 30):
    """分析最近的活動統計。"""
    print(f"\n=== 最近 {days} 天活動分析 ===")
    activities = get_recent_activities(limit=100)

    if not activities:
        print("無活動資料")
        return

    # 依運動類型分類
    by_type: dict[str, list[dict]] = {}
    for act in activities:
        sport = act.get("type") or "unknown"
        by_type.setdefault(sport, []).append(act)

    for sport, acts in sorted(by_type.items()):
        distances = [a["distance_km"] for a in acts if a.get("distance_km")]
        durations = [a["duration_min"] for a in acts if a.get("duration_min")]
        avg_hrs = [a["avg_hr"] for a in acts if a.get("avg_hr")]

        print(f"\n{sport.upper()} ({len(acts)} 次)")
        if distances:
            print(f"  總距離：{sum(distances):.1f} km  |  平均：{sum(distances)/len(distances):.1f} km")
        if durations:
            print(f"  總時間：{sum(durations)/60:.1f} hr  |  平均：{sum(durations)/len(durations):.0f} min")
        if avg_hrs:
            print(f"  平均心率：{sum(avg_hrs)/len(avg_hrs):.0f} bpm")


def analyze_sleep(days: int = 7):
    """分析睡眠品質。"""
    print(f"\n=== 最近 {days} 天睡眠分析 ===")
    records = get_sleep_data(days)

    if not records:
        print("無睡眠資料")
        return

    for r in records:
        score = r.get("score") or "-"
        hours = f"{r.get('duration_hours', 0):.1f}" if r.get("duration_hours") else "-"
        deep = f"{r.get('deep_min', 0):.0f}" if r.get("deep_min") else "-"
        rem = f"{r.get('rem_min', 0):.0f}" if r.get("rem_min") else "-"
        print(f"  {r.get('date')}  睡眠{hours}h  深睡{deep}min  REM{rem}min  評分:{score}")


def analyze_health_overview(days: int = 7):
    """健康總覽。"""
    print(f"\n=== 最近 {days} 天健康總覽 ===")

    hrv = get_hrv_data(days)
    if hrv:
        last = hrv[-1]
        print(f"HRV：最新 {last.get('last_night')} ms（週均 {last.get('weekly_avg')}），狀態：{last.get('status')}")

    rhr = get_resting_hr(days)
    if rhr:
        values = [r["resting_hr"] for r in rhr if r.get("resting_hr")]
        if values:
            print(f"靜止心率：均值 {sum(values)/len(values):.0f} bpm，最低 {min(values)} bpm")

    battery = get_body_battery(days)
    if battery:
        avg_end = [b["end_level"] for b in battery if b.get("end_level")]
        if avg_end:
            print(f"Body Battery：日均結束電量 {sum(avg_end)/len(avg_end):.0f}%")

    readiness = get_readiness(days)
    if readiness:
        scores = [r["score"] for r in readiness if r.get("score")]
        if scores:
            print(f"訓練準備度：均分 {sum(scores)/len(scores):.0f}")


# ── 主程式 ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Garmin 活動分析工具")
    parser.add_argument("--days", type=int, default=7, help="分析天數（預設 7）")
    parser.add_argument(
        "--mode",
        choices=["all", "activities", "sleep", "health", "vo2max"],
        default="all",
        help="分析模式",
    )
    args = parser.parse_args()

    if args.mode in ("all", "activities"):
        analyze_activities(args.days)
    if args.mode in ("all", "sleep"):
        analyze_sleep(args.days)
    if args.mode in ("all", "health"):
        analyze_health_overview(args.days)
    if args.mode in ("all", "vo2max"):
        print("\n=== VO2 Max ===")
        for row in get_vo2max():
            print(f"  {row.get('sport')}: {row.get('vo2max')}  ({row.get('date')})")
