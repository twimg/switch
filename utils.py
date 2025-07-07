import random

# === ポジション別・総合評価 ===
def calculate_total_score(player):
    weights = {
        "GK": {"フィジカル":0.2, "ディフェンス":0.4, "メンタル":0.4},
        "DF": {"フィジカル":0.3, "ディフェンス":0.4, "スピード":0.2, "メンタル":0.1},
        "MF": {"パス":0.3, "テクニック":0.3, "スタミナ":0.2, "メンタル":0.2},
        "FW": {"シュート":0.4, "スピード":0.3, "テクニック":0.2, "パワー":0.1}
    }
    pos = player.get("ポジション", "MF")
    total = 0
    for key, weight in weights.get(pos, {}).items():
        total += player.get(key, 0) * weight
    return int(total)

# === 汎用総合値計算（全能力の平均も残す） ===
def calculate_overall(stats: dict) -> int:
    weights = {
        'スピード': 1.0, 'パス': 1.0, 'シュート': 1.1, 'パワー': 1.1, 'スタミナ': 1.0,
        'ディフェンス': 1.0, 'テクニック': 1.1, 'メンタル': 1.0, 'フィジカル': 1.0
    }
    total = sum(stats[k] * weights.get(k, 1.0) for k in stats if k in weights)
    return int(total / sum(weights.values()))

# === レーダーチャート用データ変換 ===
def get_radar_data(player: dict) -> dict:
    return {
        "スピード": player.get("スピード", 0),
        "パス": player.get("パス", 0),
        "シュート": player.get("シュート", 0),
        "パワー": player.get("パワー", 0),
        "スタミナ": player.get("スタミナ", 0),
        "ディフェンス": player.get("ディフェンス", 0),
        "テクニック": player.get("テクニック", 0),
        "メンタル": player.get("メンタル", 0),
        "フィジカル": player.get("フィジカル", 0)
    }

# === 国旗画像パス取得 ===
def get_flag_image(nationality: str) -> str:
    flag_paths = {
        "日本": "flags/japan.png",
        "イングランド": "flags/england.png",
        "ドイツ": "flags/germany.png",
        "スペイン": "flags/spain.png",
        "フランス": "flags/france.png",
        "ブラジル": "flags/brazil.png",
        "アルゼンチン": "flags/argentina.png",
    }
    return flag_paths.get(nationality, "flags/default.png")

# === 総当たりリーグスケジュール生成 ===
def generate_league_schedule(teams: list) -> list:
    schedule = []
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            schedule.append((teams[i], teams[j]))
    random.shuffle(schedule)
    return schedule

# === ユース判定 ===
def is_youth(age: int) -> bool:
    return age < 19

# === 年俸推定 ===
def estimate_salary(overall: int, nationality: str) -> int:
    base = 300 + overall * 5
    if nationality in ["日本", "韓国", "タイ"]:
        return int(base * 0.8)
    elif nationality in ["ブラジル", "アルゼンチン"]:
        return int(base * 0.9)
    else:
        return int(base)

# === スカウト候補の自動生成（定期入れ替え） ===
def generate_scout_candidates(period, last_update_period, n=6):
    """n人のスカウト候補をperiod（例:3）ごとに自動生成"""
    if period % 3 != 1 and period != last_update_period:
        return None  # まだ更新しない

    names = ["アレックス", "マルコ", "リカルド", "タカシ", "ジョアン", "ミゲル", "ダビド", "ロレンツォ", "レオン", "ソウタ"]
    nationalities = ["ブラジル", "アルゼンチン", "日本", "ドイツ", "イングランド", "フランス", "スペイン", "イタリア"]
    candidates = []
    for _ in range(n):
        name = random.choice(names)
        nationality = random.choice(nationalities)
        age = random.randint(17, 22)
        stats = {
            "スピード": random.randint(50, 85),
            "パス": random.randint(50, 85),
            "フィジカル": random.randint(50, 85),
            "スタミナ": random.randint(50, 85),
            "ディフェンス": random.randint(50, 85),
            "テクニック": random.randint(50, 85),
            "メンタル": random.randint(50, 85),
            "シュート": random.randint(50, 85),
            "パワー": random.randint(50, 85),
        }
        pos = random.choice(["GK", "DF", "MF", "FW"])
        candidate = {
            "名前": name,
            "国籍": nationality,
            "年齢": age,
            "ポジション": pos,
            **stats
        }
        candidate["総合評価"] = calculate_total_score({**candidate, **stats, "ポジション": pos})
        candidates.append(candidate)
    return candidates

# === 移籍金計算 ===
def estimate_transfer_fee(player):
    """年齢・能力・潜在値で移籍金を算出（万円単位）"""
    age_factor = max(1, (30 - player["年齢"]) / 10)
    total_score = calculate_total_score(player)
    # 潜在能力を平均化
    potential = 0
    count = 0
    for key in player:
        if key.endswith("_潜在"):
            potential += player[key]
            count += 1
    if count > 0:
        potential = potential / count
    else:
        potential = total_score
    fee = int((total_score + potential) * 2000 * age_factor)
    return fee
