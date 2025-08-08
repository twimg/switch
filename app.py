# app.py — Full Integrated Build (JA UI + Navy Theme + GD fix)
# ------------------------------------------------------------
# pip install streamlit pandas numpy
# Run: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import random
from typing import List, Optional, Dict

st.set_page_config(page_title="Football Sim — Full (JA)", layout="wide")

# -----------------------
# 軽量 i18n
# -----------------------
LANG = "ja"   # "en" に変えると英語キー
TEXTS = {
  "ja": {
    "AppTitle": "⚽ フットボール・シム — フル版",
    "Market": "移籍市場",
    "LoansFA": "レンタル & フリー",
    "Scouting": "スカウト & アカデミー",
    "Squad": "スカッド",
    "Finance": "財務",
    "Settings": "設定",
    "Weekly": "週進行",
    "News": "ニュース",
    "TransferMarket": "移籍市場",
    "ContractNegotiation": "契約交渉（代理人）",
    "MakeOffer": "オファー作成",
    "IncomingOutgoing": "入出オファー一覧",
    "LoansAndFA": "レンタル & フリーエージェント",
    "ScoutingAcademy": "スカウト & アカデミー",
    "Assignments": "スカウト割当",
    "Recommendations": "推奨候補（推定OV順）",
    "Academy": "アカデミー",
    "ScoutReports": "スカウトレポート",
    "SquadHdr": "スカッド",
    "Tactics": "戦術（あなたのクラブ）",
    "Training": "個別トレーニング & ポジ転向",
    "Mentoring": "メンタリング",
    "ContractExt": "契約延長（あなたの選手）",
    "FinanceHdr": "財務",
    "SponsorsActive": "スポンサー契約（有効）",
    "SponsorOffers": "スポンサーオファー",
    "BudgetLedger": "予算 & 仕訳",
    "SettingsHdr": "設定",
    "TicketPrice": "チケット価格（ホーム）",
    "WeeklyHdr": "週進行 & リーグ",
    "FixturesThisWeek": "今週の対戦",
    "LastResults": "前週の結果",
    "StandingsD1": "順位表 D1",
    "StandingsD2": "順位表 D2",
    "ContinentalHdr": "大陸大会 — グループ / 準決（2戦）/ 決勝",
    "NewsHdr": "ニュース & 噂",
    "NextWeek": "次の週へ進める",
    "Save": "保存",
    "SignSponsor": "スポンサー契約する",
    "RefreshOffers": "オファー更新",
  },
  "en": {}
}
def t(key:str) -> str:
    return TEXTS.get(LANG, {}).get(key, key)

# -----------------------
# 濃紺テーマ（CSS）
# -----------------------
def apply_theme():
    st.markdown("""
    <style>
      .stApp { background-color:#18203A; color:#eaf6ff; }
      .stButton>button { background:#27e3b9; color:#18203A; border:0; }
      .stButton>button:hover { filter:brightness(0.92); }
      label, .stMarkdown, .stText, .stCaption, .stMetric { color:#eaf6ff !important; }
      .stDataFrame, .stTable { background: rgba(255,255,255,0.04); }
      .stTextInput>div>div>input, .stNumberInput input, textarea {
        color:#eaf6ff !important;
        background: rgba(255,255,255,0.06) !important;
      }
      .stSelectbox div[data-baseweb="select"] > div { background: rgba(255,255,255,0.06); }
      .stSlider { color:#eaf6ff; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------
# Global Constants
# -----------------------
SEASON_WEEKS = 14
USER_CLUB = "Your FC"
CPU_CLUBS = [
    "Northbridge United", "Riverton City", "Highland Rovers", "Blueport FC",
    "Kingsfield Athletic", "Westvale Rangers", "Ironlake Wolves", "Sunshore Stars",
    "Oldbury Titans", "Eagleview Jets", "Crystal Comets", "Maple Mariners",
    "Emerald Knights", "Aurora Sparks", "Grand Valley Hearts"
]
POSITIONS = ["GK","CB","LB","RB","DM","CM","AM","LW","RW","ST"]

# -----------------------
# Utility / Finance Log
# -----------------------
def log_finance(amount:int, memo:str):
    D = st.session_state.data
    D.setdefault("finance_log", [])
    D["finance_log"].append({
        "season": D["season"], "week": D["week"], "amount": int(amount), "memo": str(memo)
    })

def next_player_id() -> int:
    D = st.session_state.data
    D["next_player_id"] += 1
    return int(D["next_player_id"])

def mv_from_ov_strict(ov:int) -> int:
    v = int((ov**2) * 1000 / 12)
    return (v // 5000) * 5000

# -----------------------
# Names（各国）
# -----------------------
NAME_DB = {
    "ENG": (["Smith","Johnson","Brown","Taylor","Wilson","Evans","King","Wright","Walker","Harris"],
            ["Jack","Oliver","Harry","George","Leo","Oscar","Noah","Jacob","James","Thomas"]),
    "ESP": (["Garcia","Martinez","Lopez","Sanchez","Perez","Gomez","Fernandez","Diaz","Hernandez","Ruiz"],
            ["Javier","Carlos","Miguel","Diego","Luis","Sergio","Raul","Pablo","Alvaro","Antonio"]),
    "ITA": (["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco"],
            ["Luca","Marco","Andrea","Giuseppe","Matteo","Francesco","Davide","Stefano","Alessandro","Antonio"]),
    "GER": (["Muller","Schmidt","Schneider","Fischer","Weber","Wagner","Becker","Hoffmann","Koch","Schultz"],
            ["Lukas","Leon","Finn","Ben","Jonas","Paul","Felix","Noah","Tim","Maximilian"]),
    "FRA": (["Martin","Bernard","Dubois","Durand","Lefevre","Moreau","Girard","Renard","Fontaine","Chevalier"],
            ["Lucas","Hugo","Nathan","Louis","Jules","Theo","Mathis","Noah","Ethan","Antoine"]),
    "NED": (["de Jong","van Dijk","de Boer","Bakker","Visser","Smit","Mulder","Kok","Bos","Meijer"],
            ["Daan","Sem","Levi","Bram","Lucas","Milan","Finn","Lars","Thijs","Max"]),
    "POR": (["Silva","Santos","Ferreira","Pereira","Oliveira","Gomes","Costa","Rodrigues","Martins","Sousa"],
            ["Joao","Miguel","Tiago","Rafael","Diogo","Andre","Bruno","Goncalo","Pedro","Ricardo"]),
    "BEL": (["Peeters","Janssens","Dubois","Willems","Maes","Jacobs","Goossens","Leroy","Michiels","Dupont"],
            ["Liam","Noah","Arthur","Louis","Jules","Lucas","Mohamed","Milan","Victor","Adam"]),
    "CRO": (["Kovacic","Perisic","Brozovic","Petrovic","Kovacevic","Ilic","Jovic","Ivanovic","Maric","Babin"],
            ["Ivan","Luka","Marko","Ante","Nikola","Mateo","Mario","Josip","Stipe","Domagoj"]),
    "SUI": (["Meyer","Muller","Weber","Schmid","Keller","Huber","Fischer","Zimmermann","Baumann","Graf"],
            ["Lars","Noah","Leon","Luca","Nico","Jan","Timo","Joel","Jonas","Fabian"]),
    "TUR": (["Yilmaz","Demir","Sahin","Celik","Arslan","Kaya","Aydin","Yildiz","Ozturk","Kurt"],
            ["Burak","Emre","Mehmet","Can","Yusuf","Mert","Cenk","Hakan","Ozan","Oguz"]),
    "RUS": (["Ivanov","Smirnov","Kuznetsov","Popov","Vasiliev","Sokolov","Mikhailov","Fedorov","Morozov","Volkov"],
            ["Dmitri","Sergei","Alexei","Ivan","Nikolai","Maksim","Andrei","Pavel","Viktor","Yuri"]),
    "BRA": (["Silva","Souza","Oliveira","Santos","Lima","Costa","Pereira","Goncalves","Rodrigues","Almeida"],
            ["Lucas","Gabriel","Arthur","Rafael","Pedro","Bruno","Thiago","Felipe","Caio","Joao"]),
    "ARG": (["Gonzalez","Rodriguez","Lopez","Martinez","Perez","Sanchez","Diaz","Fernandez","Gomez","Romero"],
            ["Juan","Matias","Nicolas","Santiago","Luciano","Agustin","Joaquin","Franco","Facundo","Bruno"]),
    "URU": (["Suarez","Nunez","Cavani","Gomez","Rodriguez","Pereira","Gonzalez","Fernandez","Lopez","Sanchez"],
            ["Carlos","Diego","Luis","Martin","Maxi","Lucas","Pablo","Sebastian","Matias","Bruno"]),
    "USA": (["Johnson","Williams","Jones","Brown","Davis","Miller","Wilson","Moore","Taylor","Anderson"],
            ["Liam","Noah","Elijah","James","William","Benjamin","Lucas","Henry","Alexander","Michael"]),
    "CAN": (["Smith","Martin","Brown","Tremblay","Roy","Wilson","Campbell","Lee","Anderson","Taylor"],
            ["Liam","Jackson","Noah","Logan","Lucas","William","Benjamin","Oliver","Ethan","Leo"]),
    "MEX": (["Hernandez","Garcia","Martinez","Lopez","Gonzalez","Perez","Sanchez","Ramirez","Cruz","Flores"],
            ["Jose","Juan","Luis","Carlos","Jorge","Miguel","Angel","Diego","Alejandro","Eduardo"]),
    "JPN": (["佐藤","鈴木","高橋","田中","伊藤","渡辺","山本","中村","小林","加藤"],
            ["太一","蓮","陽翔","蒼","大和","湊","樹","海斗","颯","朝陽"]),
    "KOR": (["Kim","Lee","Park","Choi","Jung","Cho","Kang","Yoon","Jang","Lim"],
            ["Minjae","Jisoo","Seungwoo","Taeyang","Jimin","Hyunwoo","Jaemin","Donghyun","Joon","Yong"]),
    "CHN": (["Wang","Li","Zhang","Liu","Chen","Yang","Zhao","Huang","Zhou","Wu"],
            ["Wei","Jun","Ming","Tao","Lei","Qiang","Bo","Hao","Jian","Feng"]),
    "AUS": (["Smith","Jones","Williams","Brown","Taylor","Wilson","White","Martin","Anderson","Thompson"],
            ["Jack","Noah","William","James","Henry","Lucas","Thomas","Charlie","Leo","Harrison"]),
    "EGY": (["Hassan","Hussein","Mahmoud","Ibrahim","Ali","Youssef","Khaled","Mostafa","Ahmed","Said"],
            ["Omar","Ahmed","Youssef","Mostafa","Ali","Mahmoud","Kareem","Hassan","Ibrahim","Amr"]),
    "GHA": (["Mensah","Owusu","Appiah","Boateng","Asamoah","Osei","Addo","Ankrah","Baah","Amankwah"],
            ["Kwame","Kofi","Yaw","Kojo","Kwesi","Yawson","Michael","Joseph","Daniel","Samuel"]),
    "NGA": (["Okafor","Balogun","Ogunleye","Ibrahim","Muhammad","Ojo","Okeke","Abiola","Lawal","Adebayo"],
            ["Emeka","Chinedu","Oluwaseun","Ayodele","Ifeanyi","Tobi","Kelechi","Sodiq","Samuel","Daniel"]),
}
NATION_POOL = list(NAME_DB.keys())

def pick_name(nat: Optional[str]=None) -> str:
    nat = nat or random.choice(NATION_POOL)
    last, first = NAME_DB.get(nat, NAME_DB["ENG"])
    # 東アジアは 姓 名 表記っぽく
    if nat in ("JPN","KOR","CHN"):
        return f"{random.choice(last)} {random.choice(first)}"
    return f"{random.choice(first)} {random.choice(last)}"

# -----------------------
# Player Generation
# -----------------------
GROWTH_TYPES = ["早熟","標準","晩成"]

def generate_player(pid:int, club:Optional[str], nat: Optional[str]=None) -> dict:
    ov = random.randint(58, 82)
    pot= min(99, ov + random.randint(5,20))
    pos= random.choice(POSITIONS)
    age= random.randint(17, 33)
    growth = random.choice(GROWTH_TYPES)
    nat = nat or random.choice(NATION_POOL)
    spd = max(30, min(99, int(np.random.normal(ov, 8))))
    dfn = max(30, min(99, int(np.random.normal(ov, 8))))
    fin = max(30, min(99, int(np.random.normal(ov, 8))))
    morale = random.randint(50, 75)
    return {
        "ID": pid,
        "Name": pick_name(nat),
        "Pos": pos,
        "OV": ov,
        "POT": pot,
        "Age": age,
        "Club": club,
        "MV": mv_from_ov_strict(ov),
        "Apps": 0,
        "Goals": 0,
        "OnLoan": False,
        "LoanFrom": None,
        "LoanAppearances": 0,
        "Growth": growth,
        "SPD": spd, "DEF": dfn, "FIN": fin,
        "PosRoles": [pos],
        "Nat": nat,
        "HGYearsClub": random.randint(0, 6) if club == USER_CLUB else 0,
        "Morale": morale
    }

def base_players_for_club(club:str, n:int=20, nat_hint:Optional[str]=None) -> List[dict]:
    rows = []
    for _ in range(n):
        pid = next_player_id()
        nat = nat_hint or random.choice(NATION_POOL)
        rows.append(generate_player(pid, club, nat))
    return rows

# -----------------------
# 初期化（後で定義する関数を呼ぶが、実行はUI末尾）
# -----------------------
def init_session():
    if "data" in st.session_state:
        return
    st.session_state.data = {}
    D = st.session_state.data
    D["season"] = 1
    D["week"] = 1
    D["club_name"] = USER_CLUB
    D["next_player_id"] = 1000
    D["budget"] = 25_000_000

    # Players & Free Agents
    cols = ["ID","Name","Pos","OV","POT","Age","Club","MV","Apps","Goals","OnLoan","LoanFrom","LoanAppearances",
            "Growth","SPD","DEF","FIN","PosRoles","Nat","HGYearsClub","Morale"]
    D["players"] = pd.DataFrame(columns=cols)
    D["free_agents"] = pd.DataFrame(columns=cols)

    # Seed squads
    you = base_players_for_club(USER_CLUB, n=22, nat_hint="JPN")
    cpu_all = []
    for c in CPU_CLUBS:
        nat_hint = random.choice(["ENG","ESP","ITA","GER","FRA","NED","BRA","ARG","USA","MEX","POR","BEL","CRO","SUI","TUR","RUS"])
        cpu_all += base_players_for_club(c, n=22, nat_hint=nat_hint)
    D["players"] = pd.DataFrame(you + cpu_all)

    # Free agents
    fa = []
    for _ in range(40):
        pid = next_player_id()
        fa.append(generate_player(pid, None, random.choice(NATION_POOL)))
    D["free_agents"] = pd.DataFrame(fa)

    # Markets / Offers / Installments
    D["transfer_offers"] = []
    D["installment_out"] = []
    D["installment_in"] = []
    D["sold_sellon"] = {}
    D["finance_log"] = []

    # League / Cup / Scouting etc. は UI起動時にまとめて呼ぶ
    D["club_meta"] = {}
    D["divisions"] = {}
    D["fixtures"] = []
    D["standings"] = {}
    D["results_by_week"] = {}

# ============================================
# League (Two Divisions) + Tactics + Registration + Demand Model
# ============================================

# 国籍ごとの微ボーナス（クラブ強度に加算）
NATION_TRAIT_BONUS = {
    "BRA": +2, "ARG": +2, "URU": +1,
    "ESP": +2, "POR": +1, "ITA": +1, "FRA": +1, "GER": +2, "NED": +1, "BEL": +1, "CRO": +1, "SUI": 0, "TUR": 0,
    "ENG": +1, "RUS": 0,
    "JPN": +1, "KOR": 0, "CHN": 0, "AUS": 0,
    "USA": 0, "CAN": 0, "MEX": +1, "EGY": 0, "GHA": 0, "NGA": 0
}
def _nat_bonus(nat: str) -> int:
    return NATION_TRAIT_BONUS.get(nat, 0)

def _make_extra_club_names(n: int) -> list:
    prefixes = ["Aurora","Iron","Valley","Royal","Eastern","Western","Northern","Southern","Grand","Crystal",
                "Liberty","Cedar","Silver","Golden","Emerald","Atlantic","Pacific","Central","United","City"]
    suffixes = ["FC","SC","Rovers","Athletic","Dynamos","Hearts","Wolves","Rangers","Stars","Titans",
                "Comets","Falcons","Giants","Jets","Phoenix","Knights","Sparks","Mariners","Suns","Bulls"]
    out = []
    used = set(CPU_CLUBS + [USER_CLUB])
    tries = 0
    while len(out) < n and tries < 500:
        tries += 1
        name = f"{random.choice(prefixes)} {random.choice(suffixes)}"
        if name not in used:
            used.add(name)
            out.append(name)
    return out

def _assign_nations_to_clubs(clubs: list) -> dict:
    nat_pool = [
        "ENG","GER","FRA","ITA","ESP","POR","NED","BEL","CRO","SUI",
        "BRA","ARG","URU","MEX","USA","CAN","JPN","KOR","TUR","AUS"
    ]
    meta = {}
    for c in clubs:
        nat = random.choice(nat_pool)
        meta[c] = {"nation": nat, "pop": random.randint(45, 90), "ticket": random.randint(18, 36)}
    return meta

def init_league():
    """D1/D2 各8クラブ、二回戦総当たり（全14週）"""
    D = st.session_state.data
    if D.get("league_ready"):
        return
    base = [USER_CLUB] + CPU_CLUBS[:]
    if len(base) < 16:
        base += _make_extra_club_names(16 - len(base))
    clubs16 = base[:16]
    club_meta = _assign_nations_to_clubs(clubs16)

    others = [c for c in clubs16 if c != USER_CLUB]
    random.shuffle(others)
    d1 = others[:8]
    d2 = [USER_CLUB] + others[8:15]
    while len(d1) < 8:
        d1.append(_make_extra_club_names(1)[0])
    while len(d2) < 8:
        newc = _make_extra_club_names(1)[0]
        d2.append(newc); club_meta[newc] = {"nation": random.choice(list(NATION_TRAIT_BONUS.keys())), "pop":60, "ticket":24}

    def _round_robin(teams):
        n = len(teams)
        arr = teams[:]
        rounds = []
        for r in range(n-1):
            pairs=[]
            for i in range(n//2):
                h=arr[i]; a=arr[-1-i]
                pairs.append((h,a) if r%2==0 else (a,h))
            arr = [arr[0]] + [arr[-1]] + arr[1:-1]
            rounds.append(pairs)
        return rounds

    def _make_fixtures(teams, div_name, start_week=1):
        rr = _round_robin(teams); rr2 = _round_robin(teams[::-1])
        fixtures=[]; w=start_week
        for pairs in rr+rr2:
            for (h,a) in pairs:
                fixtures.append({"week": w, "div": div_name, "home": h, "away": a})
            w += 1
        return fixtures

    fixtures = _make_fixtures(d1, "D1", 1) + _make_fixtures(d2, "D2", 1)

    def _blank_table(teams):
        return pd.DataFrame([{
            "Club": t, "P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0
        } for t in teams]).set_index("Club")

    standings = {"D1": _blank_table(d1), "D2": _blank_table(d2)}

    D["club_meta"] = club_meta
    D["divisions"] = {"D1": d1, "D2": d2}
    D["fixtures"] = fixtures
    D["standings"] = standings
    D["results_by_week"] = {}
    D["league_ready"] = True

# ------- 登録ルール & 需要モデル ----------
def ensure_registration_rules():
    D = st.session_state.data
    D.setdefault("registration_rules", {"max_foreigners":5, "min_homegrown":2})

def _is_domestic(club:str, nat:str) -> bool:
    D = st.session_state.data
    club_nat = D["club_meta"].get(club, {}).get("nation")
    return nat == club_nat

def _is_homegrown_at_club(row) -> bool:
    return int(row.get("HGYearsClub",0)) >= 3 and row.get("Club") == st.session_state.data["club_name"]

def select_lineup_respecting_rules(club:str) -> pd.Index:
    D = st.session_state.data
    ensure_registration_rules()
    pool = D["players"][D["players"]["Club"]==club].copy()
    if pool.empty:
        return pool.index
    rules = D["registration_rules"]
    pool["isHG"] = pool.apply(_is_homegrown_at_club, axis=1)
    pool["isDomestic"] = pool["Nat"].apply(lambda n: _is_domestic(club, n))
    pool["prio"] = np.where(pool["isHG"], 3, np.where(pool["isDomestic"], 2, 1)) + pool["OV"]/200.0
    pick = []
    foreigners = 0
    for _, r in pool.sort_values("prio", ascending=False).iterrows():
        if len(pick) >= 11: break
        is_foreign = not _is_domestic(club, r["Nat"])
        if is_foreign and foreigners >= rules["max_foreigners"]:
            continue
        pick.append(r.name)
        foreigners += int(is_foreign)
    sel = pool.loc[pick]
    need = max(0, rules["min_homegrown"] - int(sel["isHG"].sum()))
    if need > 0:
        reserves = pool[~pool.index.isin(pick) & (pool["isHG"]==True)].index.tolist()
        i=0
        for idx in sel.sort_values("prio").index:
            if i>=need or not reserves: break
            if not sel.loc[idx,"isHG"]:
                pick.remove(idx); pick.append(reserves.pop(0)); i+=1
    return pd.Index(pick[:11])

def ensure_ticket_price():
    D = st.session_state.data
    base = D["club_meta"][D["club_name"]]["ticket"]
    D.setdefault("ticket_price", base)

def demand_attendance(home:str, away:str, price:int) -> int:
    D = st.session_state.data
    meta_h = D["club_meta"][home]; meta_a = D["club_meta"][away]
    cap = 30000
    allure = (meta_h["pop"]/100) * (0.8 + meta_a["pop"]/120)
    p0 = meta_h["ticket"]
    elasticity = -0.35
    price_factor = (price/p0) ** elasticity
    div = "D1" if home in D["divisions"]["D1"] else "D2"
    tbl = D["standings"][div]
    def get_rank(club):
        if club not in tbl.index: return 8
        tbs = tbl.sort_values(["Pts","GD","GF"], ascending=[False,False,False]).reset_index()
        return int(tbs.index[tbs["Club"]==club][0]) + 1
    rank_h, rank_a = get_rank(home), get_rank(away)
    rank_factor = 1.0 + (max(0, 9 - rank_h) + max(0, 9 - rank_a))/40.0
    base_fill = 0.35 + allure * 0.6
    fill = base_fill * price_factor * rank_factor * random.uniform(0.9, 1.05)
    return int(max(1200, min(cap, cap*fill)))

# ------------- 戦術AI -------------
DEFAULT_TACTIC = {"style":"balanced","line":50,"press":50,"tempo":50}
def ensure_tactics_state():
    D = st.session_state.data
    D.setdefault("tactics", {})
    D["tactics"].setdefault(D["club_name"], dict(DEFAULT_TACTIC))

def _club_nat(club:str) -> str:
    D = st.session_state.data
    meta = D.get("club_meta", {})
    return meta.get(club, {}).get("nation", "ENG")

def _club_strength(club:str) -> float:
    D = st.session_state.data
    pl = D["players"][D["players"]["Club"] == club]
    base = float(pl["OV"].mean()) if not pl.empty else random.randint(60, 75)
    morale = float(pl["Morale"].mean()) if "Morale" in pl.columns and not pl.empty else 60.0
    chem = float(D.get("chemistry_bonus", {}).get(club, 0.0))
    return base + _nat_bonus(_club_nat(club)) + (morale-60)/20.0 + chem

def _team_plan(club:str, opp:str) -> dict:
    D = st.session_state.data
    ensure_tactics_state()
    base = dict(D["tactics"].get(club, DEFAULT_TACTIC))
    s_self = _club_strength(club); s_opp = _club_strength(opp)
    diff = s_self - s_opp
    plan = dict(base)
    if diff < -5:
        plan["style"]="counter"; plan["line"]=max(20, base["line"]-15); plan["press"]=min(80, base["press"]+10); plan["tempo"]=min(80, base["tempo"]+10)
    elif diff > 5:
        plan["style"]="possession" if base["style"]!="direct" else "direct"
        plan["line"]=min(80, base["line"]+10); plan["press"]=min(85, base["press"]+5); plan["tempo"]=min(85, base["tempo"]+5)
    atk = dfn = 1.0
    if plan["style"]=="possession": atk*=1.10; dfn*=1.06
    elif plan["style"]=="counter": atk*=1.08; dfn*=1.12
    elif plan["style"]=="direct": atk*=1.15; dfn*=0.96
    elif plan["style"]=="press": atk*=1.12; dfn*=1.00
    atk *= 1.0 + (plan["tempo"]-50)/500.0
    dfn *= 1.0 + (plan["press"]-50)/600.0
    return {"plan":plan, "atk":atk, "dfn":dfn}

# ------------- Match Sim -------------
def _simulate_match(home:str, away:str) -> dict:
    D = st.session_state.data
    ph = _team_plan(home, away); pa = _team_plan(away, home)
    sh = _club_strength(home) * ph["atk"] / max(0.5, pa["dfn"])
    sa = _club_strength(away) * pa["atk"] / max(0.5, ph["dfn"])
    sh *= 1.03  # ホーム微補正
    lam_h = max(0.15, 1.10 + (sh - sa)/55.0)
    lam_a = max(0.15, 1.10 + (sa - sh)/55.0)
    gh = np.random.poisson(lam=lam_h)
    ga = np.random.poisson(lam=lam_a)

    # ルールを満たす先発選出（経験値カウント）
    for club in [home, away]:
        lineup = select_lineup_respecting_rules(club)
        if len(lineup)>0:
            D["players"].loc[lineup, "Apps"] += 1

    # 得点者記録（簡易）
    if gh > 0:
        home_squad = D["players"][D["players"]["Club"]==home]
        if not home_squad.empty:
            for _ in range(min(3, gh)):
                idx = home_squad.sample(1).index
                D["players"].loc[idx, "Goals"] += 1
    if ga > 0:
        away_squad = D["players"][D["players"]["Club"]==away]
        if not away_squad.empty:
            for _ in range(min(3, ga)):
                idx = away_squad.sample(1).index
                D["players"].loc[idx, "Goals"] += 1

    # ゲート収入
    if home == USER_CLUB:
        ensure_ticket_price()
        price = int(D["ticket_price"])
        attendance = demand_attendance(home, away, price)
        income = attendance * price
        log_finance(+income, f"Gate ({home} vs {away}) [{attendance:,} x €{price}]")
    return {"home":home,"away":away,"gh":int(gh),"ga":int(ga)}

# ❗GD 計算を修正したリーグテーブル更新
def _apply_result_to_table(div:str, res:dict):
    D = st.session_state.data
    tb = D["standings"][div]
    h,a,gh,ga = res["home"], res["away"], res["gh"], res["ga"]
    for club, gf, ga_ in [(h, gh, ga), (a, ga, gh)]:
        tb.at[club, "P"]  = int(tb.at[club, "P"]) + 1
        tb.at[club, "GF"] = int(tb.at[club, "GF"]) + int(gf)
        tb.at[club, "GA"] = int(tb.at[club, "GA"]) + int(ga_)
        tb.at[club, "GD"] = int(tb.at[club, "GF"]) - int(tb.at[club, "GA"])
    if gh > ga:
        tb.at[h, "W"] += 1; tb.at[a, "L"] += 1; tb.at[h, "Pts"] += 3
    elif gh < ga:
        tb.at[a, "W"] += 1; tb.at[h, "L"] += 1; tb.at[a, "Pts"] += 3
    else:
        tb.at[h, "D"] += 1; tb.at[a, "D"] += 1; tb.at[h, "Pts"] += 1; tb.at[a, "Pts"] += 1

def _promote_relegate():
    """シーズン終了時の自動昇降格と次季日程再生成"""
    D = st.session_state.data
    d1 = D["standings"]["D1"].sort_values(["Pts","GD","GF"], ascending=[False,False,False])
    d2 = D["standings"]["D2"].sort_values(["Pts","GD","GF"], ascending=[False,False,False])
    down = d1.tail(2).index.tolist()
    up   = d2.head(2).index.tolist()
    new_d1 = [c for c in D["divisions"]["D1"] if c not in down] + up
    new_d2 = [c for c in D["divisions"]["D2"] if c not in up] + down
    D["divisions"]["D1"] = new_d1; D["divisions"]["D2"] = new_d2

    def _blank_table(teams):
        return pd.DataFrame([{
            "Club": t, "P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0
        } for t in teams]).set_index("Club")
    D["standings"]["D1"] = _blank_table(new_d1)
    D["standings"]["D2"] = _blank_table(new_d2)

    # 次季の対戦を再生成
    def _round_robin(teams):
        n=len(teams); arr=teams[:]; rounds=[]
        for r in range(n-1):
            pairs=[]
            for i in range(n//2):
                h=arr[i]; a=arr[-1-i]
                pairs.append((h,a) if r%2==0 else (a,h))
            arr = [arr[0]] + [arr[-1]] + arr[1:-1]
            rounds.append(pairs)
        return rounds
    def _make_fixtures(teams, div_name):
        rr=_round_robin(teams); rr2=_round_robin(teams[::-1])
        fixtures=[]; w=1
        for pairs in rr+rr2:
            for (h,a) in pairs:
                fixtures.append({"week":w,"div":div_name,"home":h,"away":a})
            w+=1
        return fixtures
    fixtures = _make_fixtures(new_d1, "D1") + _make_fixtures(new_d2, "D2")
    D["fixtures"] = fixtures
    D["results_by_week"] = {}

# ============================================
# Transfers / Installments / Add-ons / Loans / Sponsors / Rights / Rumors
# ============================================

def next_offer_id() -> int:
    D = st.session_state.data
    D.setdefault("next_offer_id", 1)
    oid = D["next_offer_id"]; D["next_offer_id"] += 1
    return int(oid)

def make_offer(
    player_id:int, from_club:str, to_club:str, kind:str,
    fee_total:int, upfront:int, inst_count:int,
    sell_on_pct:float,
    add_ons:List[dict],
    loan:Optional[dict],
    inst_frequency:str="yearly",
    buyback:Optional[dict]=None,
    matching_right:Optional[dict]=None
):
    offer = {
        "id": next_offer_id(),
        "player_id": int(player_id),
        "from_club": from_club,
        "to_club": to_club,
        "kind": kind,                               # "permanent" | "loan"
        "fee_total": int(fee_total),
        "upfront": int(upfront),
        "installments": {"count": int(inst_count), "frequency": inst_frequency},
        "sell_on_pct": float(sell_on_pct),
        "add_ons": add_ons or [],
        "loan": loan,                               # {"weeks":26,"option_fee":X,"obligation":False}
        "buyback": buyback,                         # {"fee":X,"expires":season+N}
        "matching_right": matching_right,           # {"holder":str,"expires":season+N}
        "status": "pending"
    }
    st.session_state.data["transfer_offers"].append(offer)
    return offer

def schedule_installments(deal_id:int, total:int, count:int, start_week:int, direction:str, frequency:str="yearly"):
    if count <= 0 or total <= 0: return
    if frequency == "monthly": step = 4
    elif frequency == "halfyear": step = 7
    else: step = SEASON_WEEKS
    amt = total // count
    for k in range(count):
        due = start_week + k*step
        rec = {"deal_id":deal_id, "due_week":due, "amount":amt, "remaining":count-k}
        if direction=="out": st.session_state.data["installment_out"].append(rec)
        else: st.session_state.data["installment_in"].append(rec)

def apply_installments_this_week():
    D = st.session_state.data
    wk = D["week"]
    outs = [x for x in D["installment_out"] if x["due_week"]==wk]
    for r in outs:
        D["budget"] -= int(r["amount"])
        log_finance(-int(r["amount"]), f"Installment payment (deal {r['deal_id']})")
    D["installment_out"] = [x for x in D["installment_out"] if x["due_week"]!=wk]
    ins = [x for x in D["installment_in"] if x["due_week"]==wk]
    for r in ins:
        D["budget"] += int(r["amount"])
        log_finance(+int(r["amount"]), f"Installment received (deal {r['deal_id']})")
    D["installment_in"] = [x for x in D["installment_in"] if x["due_week"]!=wk]

def maybe_trigger_add_on(kind:str, pid:int, value:int):
    # 例: {"kind":"appearances","threshold":20,"amount":500000}
    # 実際の紐付けは簡略化（将来: deal_id 紐付け）
    pass

def simulate_cpu_resale(prob_per_week:float=0.30, max_deals:int=1):
    D = st.session_state.data
    pool = D["players"][D["players"]["Club"].isin(CPU_CLUBS)]
    if pool.empty or random.random()>prob_per_week: return
    for _ in range(max_deals):
        cand = pool.sample(1).iloc[0]
        old_club = cand["Club"]
        price = int(cand["MV"] * random.uniform(1.1, 1.8))
        ensure_rights_state()
        mr = D["matching_rights"].get(int(cand["ID"]))
        if mr and mr["holder"]==USER_CLUB and D["season"] <= mr["expires_season"]:
            add_news({"type":"match_right","week":D["week"],"title":"Matching Right Opportunity",
                      "body":f"You may match €{price:,} to sign {cand['Name']}.",
                      "player_id": int(cand["ID"]), "price": int(price), "from_club": old_club})
        new_club = random.choice([c for c in CPU_CLUBS if c != old_club])
        idx = D["players"][D["players"]["ID"]==int(cand["ID"])].index[0]
        D["players"].at[idx,"Club"] = new_club

def loan_weekly_tick():
    # （拡張用スタブ）
    pass

def is_window_open() -> bool:
    D = st.session_state.data
    return D["week"] in [1,2,8,9,10]

def generate_cpu_offers_for_your_players(prob:float=0.40):
    if not is_window_open(): return
    if random.random() > prob: return
    D = st.session_state.data
    you = D["players"][D["players"]["Club"]==USER_CLUB]
    if you.empty: return
    target_club = random.choice(CPU_CLUBS)
    pool = D["players"][D["players"]["Club"]==target_club]
    cnt = pool["Pos"].value_counts() if not pool.empty else pd.Series(dtype=int)
    need_order = ["ST","CB","CM","GK","LW","RW","AM","LB","RB","DM"]
    need_pos = next((p for p in need_order if cnt.get(p,0) < 2), random.choice(need_order))
    cand = you[you["Pos"]==need_pos]
    if cand.empty: cand = you
    p = cand.sample(1).iloc[0]
    fee = int(p["MV"] * random.uniform(1.15, 1.9))
    upfront = int(fee * random.uniform(0.35, 0.6))
    inst_n  = random.choice([0,2,3])
    sellon  = random.choice([0.0, 0.1, 0.15])
    addons  = [{"kind":"appearances","threshold":random.choice([15,20,25]),"amount":int(fee*0.05)}]
    if p["Pos"] in ("ST","LW","RW","AM"):
        addons.append({"kind":"goals","threshold":random.choice([10,15]),"amount":int(fee*0.04)})
    make_offer(
        player_id=int(p["ID"]),
        from_club=target_club,
        to_club=USER_CLUB,
        kind="permanent",
        fee_total=fee, upfront=upfront, inst_count=inst_n,
        sell_on_pct=sellon, add_ons=addons, loan=None,
        inst_frequency="yearly", buyback=None, matching_right=None
    )

# ------- Sponsors -------
def ensure_sponsor_state():
    D = st.session_state.data
    D.setdefault("sponsors_available", [])
    D.setdefault("sponsors_active", [])
    D.setdefault("next_sponsor_id", 1)
    if not D["sponsors_available"]:
        generate_sponsor_offers()

def _user_division() -> str:
    D = st.session_state.data
    for div, clubs in D.get("divisions", {}).items():
        if USER_CLUB in clubs:
            return div
    return "D2"

def generate_sponsor_offers():
    D = st.session_state.data
    meta = D.get("club_meta", {})
    pop = meta.get(USER_CLUB, {}).get("pop", 60)
    div = _user_division()
    tier_mult = 1.2 if div == "D1" else 1.0
    brands = ["VectorX", "Hikari Bank", "Futura Energy", "Yamazaki Foods", "NovaTech", "Sunrise Mobile", "Atlas Air"]
    offers = []
    for _ in range(3):
        brand = random.choice(brands)
        weekly = int(20_000 * tier_mult * (0.8 + pop/100))
        bonus_top = int(750_000 * tier_mult)
        bonus_win = int(1_500_000 * tier_mult)
        seasons = random.choice([1,2])
        offers.append({"id": D["next_sponsor_id"], "brand": brand, "tier": "Standard" if seasons==1 else "Premium",
                       "weekly": weekly, "bonus_top": bonus_top, "bonus_win": bonus_win, "seasons": seasons})
        D["next_sponsor_id"] += 1
    D["sponsors_available"].extend(offers)

def accept_sponsor(offer_id:int) -> str:
    D = st.session_state.data
    rec = next((x for x in D["sponsors_available"] if x["id"] == offer_id), None)
    if not rec: return "not_found"
    c = dict(rec); c["seasons_left"] = c["seasons"]
    D["sponsors_active"].append(c)
    D["sponsors_available"] = [x for x in D["sponsors_available"] if x["id"] != offer_id]
    log_finance(0, f"Sponsor signed: {rec['brand']} ({rec['tier']})")
    return "ok"

def apply_sponsor_income():
    D = st.session_state.data
    total = sum(s["weekly"] for s in D.get("sponsors_active", []))
    if total:
        D["budget"] += total
        log_finance(+total, f"Sponsors weekly income ({len(D['sponsors_active'])} deals)")

def sponsor_on_season_end():
    D = st.session_state.data
    div = _user_division()
    tbl = D["standings"][div].sort_values(["Pts","GD","GF"], ascending=[False,False,False]).reset_index()
    pos = tbl.index[tbl["Club"] == USER_CLUB][0] + 1
    paid = 0
    for s in D.get("sponsors_active", []):
        if pos == 1:
            paid += s["bonus_win"]
        elif pos <= 2 and div == "D2":
            paid += s["bonus_top"]
        elif pos <= 4 and div == "D1":
            paid += int(s["bonus_top"] * 0.75)
    if paid:
        D["budget"] += paid
        log_finance(+paid, f"Sponsor season bonus (pos={pos} in {div})")
    new_active=[]
    for s in D.get("sponsors_active", []):
        s = dict(s); s["seasons_left"] = max(0, int(s.get("seasons_left", 1))-1)
        if s["seasons_left"]>0: new_active.append(s)
        else: log_finance(0, f"Sponsor ended: {s['brand']}")
    D["sponsors_active"] = new_active
    generate_sponsor_offers()

# ------- Rights & News -------
def ensure_rights_state():
    D = st.session_state.data
    D.setdefault("buyback_rights", {})
    D.setdefault("matching_rights", {})

def exercise_matching_right(pid:int, price:int, from_club:str) -> str:
    D = st.session_state.data
    row = D["players"][D["players"]["ID"]==pid]
    if row.empty: return "not_found"
    if D["budget"] < price: return "insufficient_budget"
    D["budget"] -= int(price)
    log_finance(-int(price), f"Matching Right exercised (PID {pid})")
    idx = row.index[0]
    D["players"].at[idx, "Club"] = D["club_name"]
    D["matching_rights"].pop(pid, None)
    return "ok"

def ensure_news_state():
    D = st.session_state.data
    D.setdefault("news", [])

def add_news(item:dict):
    ensure_news_state()
    st.session_state.data["news"].append(item)

def generate_rumors_weekly():
    D = st.session_state.data
    ensure_news_state()
    pool = D["players"][D["players"]["Club"].isin(CPU_CLUBS)]
    if pool.empty or random.random()>0.5: return
    p = pool.sample(1).iloc[0]
    club = random.choice(CPU_CLUBS)
    truth = random.random()<0.4
    body = f"{club} are {'seriously ' if truth else ''}monitoring {p['Name']} ({p['Club']})."
    add_news({"type":"rumor","week":D["week"],"title":"Transfer Rumor","body":body})

# ============================================
# Scouting + FoW + Grades + Reports
# ============================================

REGION_OF = {
    "ENG":"EU","ESP":"EU","ITA":"EU","GER":"EU","FRA":"EU","NED":"EU","POR":"EU","BEL":"EU","CRO":"EU","SUI":"EU","TUR":"EU",
    "BRA":"SA","ARG":"SA","URU":"SA","MEX":"NA","USA":"NA","CAN":"NA",
    "JPN":"AS","KOR":"AS","CHN":"AS","AUS":"OC","RUS":"EU","EGY":"AF","GHA":"AF","NGA":"AF"
}
def nation_to_region(nat:str) -> str:
    return REGION_OF.get(nat, "GLB")

def ensure_scout_reports():
    st.session_state.data.setdefault("scout_reports", {})

def write_scout_report(pid:int, scout:dict, est_ov:int):
    ensure_scout_reports()
    p = st.session_state.data["players"][st.session_state.data["players"]["ID"]==pid].iloc[0]
    summary = f"{p['Name']} ({p['Pos']}, {p['Age']}y, Nat {p['Nat']})\n" \
              f"Strength: {'Finishing' if p['FIN']>=p['DEF'] and p['FIN']>=p['SPD'] else ('Defense' if p['DEF']>=p['SPD'] else 'Speed')}\n" \
              f"Risk: {'Low' if scout['grade']>=4 else 'Medium' if scout['grade']==3 else 'High'}\n" \
              f"Estimated OV: {est_ov}"
    rec = {"week": st.session_state.data["week"], "scout": scout["name"], "grade": scout["grade"], "summary": summary, "est_ov": est_ov}
    st.session_state.data["scout_reports"].setdefault(int(pid), []).append(rec)

def ensure_scouting_state():
    D = st.session_state.data
    D.setdefault("scout_knowledge", {})
    D.setdefault("scouts", [])
    D.setdefault("next_scout_id", 1)
    D.setdefault("scout_assignments", {})
    D.setdefault("scout_shortlist", set())
    if not D["scouts"]:
        def add_scout(name, region, grade, coverage_base):
            sid = D["next_scout_id"]; D["next_scout_id"] += 1
            sigma_floor_map = {1:8.0, 2:6.0, 3:4.5, 4:3.0, 5:2.0}
            cov = int(coverage_base * (0.8 + 0.1*grade))
            D["scouts"].append({
                "id": sid, "name": name, "region": region,
                "grade": int(grade),
                "sigma_floor": sigma_floor_map[int(grade)],
                "coverage": cov,
                "salary": 8000 + grade*4000
            })
            D["scout_assignments"][sid] = {"type":"region", "value":region}
        add_scout("K. Morita", "AS", 3, 20)
        add_scout("R. Alvarez","SA", 4, 18)
    if not D["scout_knowledge"]:
        for _, p in D["players"].iterrows():
            pid = int(p["ID"])
            if p["Club"] == D["club_name"]:
                D["scout_knowledge"][pid] = {"mu": int(p["OV"]), "sigma": 0.0, "last_seen": D["week"]}
            else:
                mu = int(p["OV"] + np.random.normal(0, 8))
                D["scout_knowledge"][pid] = {"mu": mu, "sigma": 12.0, "last_seen": 0}
        for _, p in D["free_agents"].iterrows():
            pid = int(p["ID"])
            mu = int(p["OV"] + np.random.normal(0, 10))
            D["scout_knowledge"][pid] = {"mu": mu, "sigma": 14.0, "last_seen": 0}

def visible_ov_for_user(pid:int) -> int:
    D = st.session_state.data
    if pid not in D["scout_knowledge"]:
        row = D["players"][D["players"]["ID"]==pid]
        if row.empty: row = D["free_agents"][D["free_agents"]["ID"]==pid]
        if row.empty: return 60
        ov = int(row.iloc[0]["OV"])
        D["scout_knowledge"][pid] = {"mu": int(ov + np.random.normal(0, 10)), "sigma": 14.0, "last_seen": 0}
    row = D["players"][D["players"]["ID"]==pid]
    if not row.empty and row.iloc[0]["Club"] == D["club_name"]:
        return int(row.iloc[0]["OV"])
    k = D["scout_knowledge"][pid]
    return int(max(30, min(99, int(round(k["mu"])))))

def apply_staff_weekly_costs():
    D = st.session_state.data
    total = sum(s["salary"] for s in D.get("scouts", []))
    if total:
        D["budget"] -= total
        log_finance(-total, f"Scouting staff wages ({len(D['scouts'])} scouts)")

def scouting_weekly_tick():
    D = st.session_state.data
    if not D.get("scouts"): return
    meta = D.get("club_meta", {})
    club_nat = {c: meta.get(c, {}).get("nation","ENG") for c in list(meta.keys())}
    def pool_for(assign:dict):
        t = assign["type"]; v = assign["value"]
        if t == "region":
            clubs = [c for c,n in club_nat.items() if nation_to_region(n)==v]
            p1 = D["players"][D["players"]["Club"].isin(clubs)]
            p2 = D["free_agents"]
            return pd.concat([p1, p2], ignore_index=True)
        elif t == "club":
            return D["players"][D["players"]["Club"]==v]
        elif t == "shortlist":
            ids = list(D.get("scout_shortlist", set()))
            return D["players"][D["players"]["ID"].isin(ids)]
        return D["players"].head(0)

    for s in D["scouts"]:
        assign = D["scout_assignments"].get(s["id"], {"type":"region","value":s["region"]})
        pool = pool_for(assign)
        if pool.empty: continue
        pool = pool[(pool["Club"] != D["club_name"]) | (pool["Club"].isna())]
        if pool.empty: continue
        shortlist_ids = set(D.get("scout_shortlist", set()))
        pri = pool[pool["ID"].isin(shortlist_ids)]
        sec = pool[~pool["ID"].isin(shortlist_ids)]
        cap = int(s["coverage"])
        take = pd.concat([pri.head(cap//2), sec.head(cap - len(pri.head(cap//2)))])
        for _, p in take.iterrows():
            pid = int(p["ID"]); true = int(p["OV"])
            k = D["scout_knowledge"].setdefault(pid, {"mu": int(true + np.random.normal(0,10)), "sigma": 14.0, "last_seen": 0})
            nat = None
            if isinstance(p["Club"], str) and p["Club"] in club_nat:
                nat = club_nat[p["Club"]]
            reg = nation_to_region(nat) if nat else "GLB"
            alpha = 0.35 + (0.1 if reg == s["region"] else 0.0) + (0.15 if pid in shortlist_ids else 0.0)
            k["mu"] = float(k["mu"] + alpha * (true - k["mu"]))
            k["sigma"] = float(max(s["sigma_floor"], k["sigma"] * (0.90 if pid not in shortlist_ids else 0.85)))
            k["last_seen"] = D["week"]
            if random.random() < 0.20:
                est = int(round(k["mu"]))
                write_scout_report(int(p["ID"]), s, est)

# ============================================
# Youth / Growth
# ============================================
YOUTH_INTAKE_WEEK = 2

def ensure_player_nations_and_hg():
    D = st.session_state.data
    if D["players"].empty: return
    need_cols = {"Nat","HGYearsClub","Morale","SPD","DEF","FIN","PosRoles"}
    for c in need_cols:
        if c not in D["players"].columns:
            D["players"][c] = None
    for idx, p in D["players"].iterrows():
        if pd.isna(p.get("Nat")):
            D["players"].at[idx,"Nat"] = random.choice(NATION_POOL)
        if pd.isna(p.get("HGYearsClub")):
            D["players"].at[idx,"HGYearsClub"] = random.randint(0,6) if p["Club"]==USER_CLUB else 0
        if pd.isna(p.get("Morale")):
            D["players"].at[idx,"Morale"] = random.randint(50,75)
        if pd.isna(p.get("SPD")):
            ov = int(p["OV"])
            D["players"].at[idx,"SPD"] = max(30, min(99, int(np.random.normal(ov,8))))
            D["players"].at[idx,"DEF"] = max(30, min(99, int(np.random.normal(ov,8))))
            D["players"].at[idx,"FIN"] = max(30, min(99, int(np.random.normal(ov,8))))
        if pd.isna(p.get("PosRoles")):
            D["players"].at[idx,"PosRoles"] = [p["Pos"]]

def youth_intake():
    D = st.session_state.data
    D.setdefault("academy", pd.DataFrame(columns=D["players"].columns.tolist() + ["IsYouth"]))
    n = random.randint(6,8)
    base_id = 90000 + D["season"]*1000
    kids=[]
    for i in range(n):
        pid = base_id + i
        p = generate_player(pid, None, random.choice(NATION_POOL))
        p["OV"] = random.randint(45,60); p["MV"]=mv_from_ov_strict(p["OV"])
        p["Age"] = random.randint(15,17); p["IsYouth"]=True
        kids.append(p)
        st.session_state.data["scout_knowledge"][pid] = {"mu": int(p["OV"] + np.random.normal(0, 6)), "sigma": 8.0, "last_seen": 0}
    if kids:
        D["academy"] = pd.concat([D["academy"], pd.DataFrame(kids)], ignore_index=True)

def promote_from_academy(pid:int) -> str:
    D = st.session_state.data
    ac = D.get("academy", pd.DataFrame())
    row = ac[ac["ID"]==pid]
    if row.empty: return "not_found"
    player = row.iloc[0].to_dict()
    player["IsYouth"] = False; player["Club"] = D["club_name"]
    player["MV"] = mv_from_ov_strict(int(player["OV"]))
    D["players"] = pd.concat([D["players"], pd.DataFrame([player])], ignore_index=True)
    D["academy"] = ac[ac["ID"]!=pid]
    D["scout_knowledge"][pid] = {"mu": int(player["OV"]), "sigma": 0.0, "last_seen": D["week"]}
    return "ok"

def release_from_academy(pid:int) -> str:
    D = st.session_state.data
    ac = D.get("academy", pd.DataFrame())
    row = ac[ac["ID"]==pid]
    if row.empty: return "not_found"
    pl = row.iloc[0].to_dict()
    pl["Club"] = None; pl["IsYouth"]=False
    D["free_agents"] = pd.concat([D["free_agents"], pd.DataFrame([pl])], ignore_index=True)
    D["academy"] = ac[ac["ID"]!=pid]
    return "ok"

def _growth_delta(age:int, gtype:str, pot:int, ov:int) -> float:
    peak = {"早熟":22, "標準":25, "晩成":28}.get(gtype, 25)
    d = peak - age
    base = 0.20 + max(0, (10 - abs(d))) * 0.04
    headroom = max(0, pot - ov)
    damp = 0.3 + 0.7*(headroom/ max(1, pot-30))
    val = base * damp
    return float(max(-0.25, min(0.8, val)))

def apply_growth_weekly():
    D = st.session_state.data
    for idx, p in D["players"].iterrows():
        ov, pot, age, g = int(p["OV"]), int(p["POT"]), int(p["Age"]), p.get("Growth","標準")
        delta = _growth_delta(age, g, pot, ov)
        new_ov = int(max(30, min(99, ov + np.random.normal(delta, 0.1))))
        if new_ov != ov:
            D["players"].at[idx, "OV"] = new_ov
            D["players"].at[idx, "MV"] = mv_from_ov_strict(new_ov)
        pid = int(p["ID"])
        if pid in D["scout_knowledge"]:
            k = D["scout_knowledge"][pid]
            k["mu"] = k["mu"] + 0.05*(new_ov - k["mu"])
    ac = D.get("academy", pd.DataFrame())
    for idx, p in ac.iterrows():
        ov, pot, age, g = int(p["OV"]), int(p["POT"]), int(p["Age"]), p.get("Growth","標準")
        delta = _growth_delta(age, g, pot, ov) * 1.1
        new_ov = int(max(25, min(95, ov + np.random.normal(delta, 0.15))))
        if new_ov != ov:
            D["academy"].at[idx, "OV"] = new_ov
            D["academy"].at[idx, "MV"] = mv_from_ov_strict(new_ov)

# ============================================
# Training & Position Conversion
# ============================================
POS_WEIGHTS = {
    "GK": (0.15,0.50,0.05), "CB": (0.10,0.65,0.10), "LB": (0.20,0.50,0.15),
    "RB": (0.20,0.50,0.15), "DM": (0.20,0.55,0.15), "CM": (0.25,0.45,0.20),
    "AM": (0.25,0.35,0.30), "LW": (0.30,0.25,0.35), "RW": (0.30,0.25,0.35), "ST": (0.25,0.20,0.45)
}
def ensure_training_state():
    D = st.session_state.data
    D.setdefault("training_plans", {})

def _recalc_ov_by_substats(row) -> int:
    w = POS_WEIGHTS.get(row["Pos"], (0.25,0.35,0.40))
    ov = int(round(w[0]*int(row["SPD"]) + w[1]*int(row["DEF"]) + w[2]*int(row["FIN"])))
    return max(30, min(99, ov))

def apply_training_weekly():
    D = st.session_state.data
    ensure_training_state()
    for pid, plan in list(D["training_plans"].items()):
        idxs = D["players"][D["players"]["ID"]==int(pid)].index
        if len(idxs)==0:
            D["training_plans"].pop(pid, None); continue
        idx = idxs[0]
        f = plan.get("focus","speed")
        inc = {"speed":("SPD",1.2),"defense":("DEF",1.3),"finishing":("FIN",1.35)}[f]
        col, base = inc
        cur = int(D["players"].at[idx, col])
        gain = max(0, np.random.normal(base, 0.3))
        D["players"].at[idx, col] = int(min(99, cur + gain))
        row = D["players"].loc[idx]
        new_ov = _recalc_ov_by_substats(row)
        if new_ov != int(row["OV"]):
            D["players"].at[idx, "OV"] = new_ov
            D["players"].at[idx, "MV"] = mv_from_ov_strict(new_ov)
        if plan.get("pos_target"):
            plan["weeks_left"] = int(plan.get("weeks_left",0)) - 1
            if plan["weeks_left"] <= 0:
                roles = set(row.get("PosRoles", [row["Pos"]]) or [row["Pos"]])
                roles.add(plan["pos_target"])
                D["players"].at[idx, "PosRoles"] = list(roles)
                D["players"].at[idx, "Pos"] = plan["pos_target"]
                plan["pos_target"] = None; plan["weeks_left"] = 0
    for pid in list(D["training_plans"].keys()):
        pl = D["training_plans"][pid]
        if pl.get("pos_target") is None and pl.get("focus") is None:
            D["training_plans"].pop(pid, None)

# ============================================
# Mentoring / Chemistry
# ============================================
def ensure_mentoring_state():
    D = st.session_state.data
    D.setdefault("mentoring_pairs", [])
    D.setdefault("chemistry_bonus", {})

def apply_mentoring_weekly():
    D = st.session_state.data
    ensure_mentoring_state()
    boost_team = {}
    for pair in D["mentoring_pairs"]:
        m = int(pair["mentor"]); t = int(pair["mentee"])
        pr_m = D["players"][D["players"]["ID"]==m]
        pr_t = D["players"][D["players"]["ID"]==t]
        if pr_m.empty or pr_t.empty: continue
        pm = pr_m.iloc[0]; pt = pr_t.iloc[0]
        if pm["Club"] != pt["Club"]: continue
        if int(pm["Age"])>=28 or int(pm["OV"])>=75:
            if int(pt["Age"])<=22:
                idx = pr_t.index[0]
                new_morale = int(min(99, int(pt["Morale"])+2))
                D["players"].at[idx,"Morale"] = new_morale
                for c in ["SPD","DEF","FIN"]:
                    D["players"].at[idx,c] = int(min(99, int(pt[c])+np.random.uniform(0.1,0.3)))
                same_nat = 1 if pm["Nat"]==pt["Nat"] else 0
                same_pos = 1 if pm["Pos"]==pt["Pos"] else 0
                club = pm["Club"]
                boost_team[club] = boost_team.get(club, 0.0) + 0.03 + 0.02*same_nat + 0.02*same_pos
    for c, v in boost_team.items():
        prev = float(D["chemistry_bonus"].get(c, 0.0))
        D["chemistry_bonus"][c] = float(min(2.0, prev*0.7 + v))

# ============================================
# Contracts & Payroll
# ============================================
def ensure_contract_state():
    D = st.session_state.data
    D.setdefault("contracts", {})
    D.setdefault("pending_terms", {})
    D.setdefault("agent_profiles", {})

def ensure_player_wages():
    D = st.session_state.data
    ensure_contract_state()
    for _, p in D["players"].iterrows():
        pid = int(p["ID"])
        if p["Club"] != D["club_name"]:
            continue
        if pid not in D["contracts"]:
            ov = int(p["OV"])
            wage = int(ov * 900)
            terms = {"wage": wage,"signing": 0,"apps_bonus": 0,"goals_bonus": 0,"length_weeks": 52*3,"release_clause": int(p["MV"]*1.8)}
            D["contracts"][pid] = terms

def apply_player_wages_weekly():
    D = st.session_state.data
    if not D.get("contracts"): return
    you_ids = D["players"][D["players"]["Club"]==D["club_name"]]["ID"].astype(int).tolist()
    payroll = 0; bonus = 0
    for pid in you_ids:
        t = D["contracts"].get(int(pid))
        if not t: continue
        payroll += t["wage"]
        row = D["players"][D["players"]["ID"]==pid].iloc[0]
        if int(row["Apps"]) > 0 and t["apps_bonus"]>0: bonus += t["apps_bonus"]
        if int(row["Goals"]) > 0 and t["goals_bonus"]>0: bonus += t["goals_bonus"]
        t["length_weeks"] = max(0, int(t["length_weeks"]) - 1)
    total = payroll + bonus
    if total:
        D["budget"] -= total
        log_finance(-total, f"Player wages ({len(you_ids)} players) + bonuses")

def _agent_profile(pid:int):
    D = st.session_state.data
    ensure_contract_state()
    if pid not in D["agent_profiles"]:
        D["agent_profiles"][pid] = {
            "tough": round(random.uniform(0.3, 0.9), 2),
            "risk":  round(random.uniform(0.2, 0.8), 2),
            "patience": random.randint(2, 5)
        }
    return D["agent_profiles"][pid]

def baseline_terms_for(pid:int) -> dict:
    D = st.session_state.data
    p = D["players"][D["players"]["ID"]==pid].iloc[0]
    ov, pos = int(p["OV"]), str(p["Pos"])
    is_att = pos in ("ST","LW","RW","AM")
    base_wage = int((ov**1.1) * (1.05 if is_att else 0.95) * 12)
    base_sign = int(p["MV"] * 0.08)
    base_apps = 0 if ov>=80 else int(1000 + ov*50)
    base_goals= int(2000 + ov*60) if is_att else 0
    base_clause = int(p["MV"] * (1.8 if ov<80 else 2.4))
    return {"wage": base_wage, "signing": base_sign, "apps_bonus": base_apps, "goals_bonus": base_goals,
            "length_weeks": 52*random.choice([2,3,4]), "release_clause": base_clause}

def evaluate_contract_offer(pid:int, offer:dict, round_i:int) -> dict:
    prof = _agent_profile(pid)
    target = baseline_terms_for(pid)
    ask = {k: int(target[k] * (1.10 + prof["tough"]*0.25)) for k in target}
    def ratio(k, w=1.0):
        if k in ("apps_bonus","goals_bonus"):
            t = ask[k]; o = offer.get(k,0)
            return (t / max(1,o+1)) * w
        else:
            t = ask[k]; o = offer.get(k,t)
            return (t / max(1,o)) * w
    score = 0.0
    score += ratio("wage", 1.6)
    score += ratio("signing", 1.2)
    score += max(0.5, (offer.get("length_weeks", ask["length_weeks"]) / ask["length_weeks"])) * 0.8
    score += (ask["release_clause"] / max(1, offer.get("release_clause", ask["release_clause"]))) * 1.4
    bonus_term = (max(1, offer.get("apps_bonus",1)) / max(1, ask["apps_bonus"])) + (max(1, offer.get("goals_bonus",1)) / max(1, ask["goals_bonus"])+0.01)
    score *= (1.0 - min(0.3, 0.1*(bonus_term-1)))
    thresh = 2.8 - 0.3*round_i + (prof["risk"]-0.5)
    if score <= thresh:
        return {"decision":"accept", "counter":None, "ask":ask, "profile":prof}
    if round_i >= prof["patience"]:
        return {"decision":"walkaway", "counter":None, "ask":ask, "profile":prof}
    counter = {}
    for k in ask:
        if k in ("apps_bonus","goals_bonus"):
            counter[k] = int(max(ask[k], offer.get(k,0)))
        elif k=="release_clause":
            counter[k] = int(max(ask[k], offer.get(k, ask[k])))
        elif k=="length_weeks":
            counter[k] = int(max(ask[k], offer.get(k, ask[k])))
        else:
            want = int(ask[k]* (0.95 + 0.25*random.random()))
            counter[k] = max(want, offer.get(k,0))
    return {"decision":"counter", "counter":counter, "ask":ask, "profile":prof}

def finalize_contract_on_join(pid:int, terms:dict):
    D = st.session_state.data
    ensure_contract_state()
    t = dict(terms)
    D["contracts"][pid] = t
    sign = int(t.get("signing",0))
    if sign>0:
        D["budget"] -= sign
        log_finance(-sign, f"Signing bonus (PID {pid})")

# ============================================
# Continental Cup – Groups + H2H + 2-leg SF + Final
# ============================================
CC_WEEKS_GROUP = [2,4,6,7,9,11]
CC_SF_LEGS     = (12,13)
CC_WEEK_FINAL  = 14

def init_continental_groups_for_season():
    D = st.session_state.data
    cand = D["divisions"]["D1"][:] + D["divisions"]["D2"][:]
    uniq = []
    for c in cand:
        if c not in uniq:
            uniq.append(c)
    if USER_CLUB not in uniq:
        uniq.insert(0, USER_CLUB)
    uniq = sorted(uniq, key=lambda c: D["club_meta"][c]["pop"], reverse=True)[:16]
    pots = [uniq[i:i+4] for i in range(0, 16, 4)]
    groups = {"A":[], "B":[], "C":[], "D":[]}
    nations_by_g = {g:set() for g in groups}
    for pot in pots:
        random.shuffle(pot)
        for team in pot:
            nat = D["club_meta"][team]["nation"]
            choices = sorted(groups.keys(), key=lambda g: (nat in nations_by_g[g], len(groups[g])))
            placed = False
            for g in choices:
                if len(groups[g])<4 and (nat not in nations_by_g[g] or all(len(groups[x])==4 for x in groups)):
                    groups[g].append(team); nations_by_g[g].add(nat); placed=True; break
            if not placed:
                g = min(groups.keys(), key=lambda k: len(groups[k]))
                groups[g].append(team); nations_by_g[g].add(nat)
    def group_fixtures(teams, weeks):
        pairs_rounds = [
            [(teams[0],teams[1]),(teams[2],teams[3])],
            [(teams[0],teams[2]),(teams[1],teams[3])],
            [(teams[0],teams[3]),(teams[1],teams[2])]
        ]
        fixtures=[]
        for r, pairs in enumerate(pairs_rounds):
            w = weeks[r]
            for (h,a) in pairs:
                fixtures.append({"week":w,"round":"G","home":h,"away":a})
        for r, pairs in enumerate(pairs_rounds):
            w = weeks[r+3]
            for (h,a) in pairs:
                fixtures.append({"week":w,"round":"G","home":a,"away":h})
        return fixtures
    fixtures=[]
    for g, teams in groups.items():
        fixtures += [dict(x, group=g) for x in group_fixtures(teams, CC_WEEKS_GROUP)]
    def blank_table(ts):
        return pd.DataFrame([{"Club":t,"P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0} for t in ts]).set_index("Club")
    tables = {g: blank_table(t) for g,t in groups.items()}
    D["cc"] = {"groups": groups,"fixtures": fixtures,"tables": tables,"results": [],"state": "GROUP"}

def _cc_apply_result(group:str, res:dict):
    D = st.session_state.data
    tb = D["cc"]["tables"][group]
    h,a,gh,ga = res["home"], res["away"], res["gh"], res["ga"]
    for club, gf, ga_ in [(h, gh, ga), (a, ga, gh)]:
        tb.at[club, "P"]  = int(tb.at[club, "P"]) + 1
        tb.at[club, "GF"] = int(tb.at[club, "GF"]) + int(gf)
        tb.at[club, "GA"] = int(tb.at[club, "GA"]) + int(ga_)
        tb.at[club, "GD"] = int(tb.at[club, "GF"]) - int(tb.at[club, "GA"])
    if gh > ga:
        tb.at[h,"W"] += 1; tb.at[a,"L"] += 1; tb.at[h,"Pts"] += 3
    elif gh < ga:
        tb.at[a,"W"] += 1; tb.at[h,"L"] += 1; tb.at[a,"Pts"] += 3
    else:
        tb.at[h,"D"] += 1; tb.at[a,"D"] += 1; tb.at[h,"Pts"] += 1; tb.at[a,"Pts"] += 1

def _cc_h2h_metrics(group:str, clubs:list) -> dict:
    D = st.session_state.data
    pts = {c:0 for c in clubs}; gd={c:0 for c in clubs}; gf={c:0 for c in clubs}
    for r in D["cc"]["results"]:
        if r["round"]!="G" or r.get("group")!=group: continue
        h,a,gh,ga = r["home"], r["away"], int(r["gh"]), int(r["ga"])
        if h in clubs and a in clubs:
            if gh>ga: pts[h]+=3
            elif gh<ga: pts[a]+=3
            else: pts[h]+=1; pts[a]+=1
            gd[h]+= (gh-ga); gd[a]+= (ga-gh)
            gf[h]+= gh; gf[a]+= ga
    return {c:(pts[c], gd[c], gf[c]) for c in clubs}

def _cc_group_rank(group:str) -> pd.DataFrame:
    D = st.session_state.data
    tb = D["cc"]["tables"][group].copy()
    tb = tb.sort_values(["Pts","GD","GF"], ascending=[False,False,False])
    ordered = []; clubs = tb.index.tolist(); i=0
    while i < len(clubs):
        same = [clubs[i]]; j=i+1
        while j < len(clubs) and tb.loc[clubs[j],"Pts"] == tb.loc[clubs[i],"Pts"]:
            same.append(clubs[j]); j+=1
        if len(same)==1: ordered += same
        else:
            h2h = _cc_h2h_metrics(group, same)
            same_sorted = sorted(
                same,
                key=lambda c: (h2h[c][0], h2h[c][1], h2h[c][2], tb.loc[c,"GD"], tb.loc[c,"GF"]),
                reverse=True
            )
            ordered += same_sorted
        i = j
    return tb.loc[ordered]

def _cc_seed_knockout_from_groups():
    D = st.session_state.data
    winners = {g: _cc_group_rank(g).head(1).index[0] for g in "ABCD"}
    sf = [
        {"week":CC_SF_LEGS[0], "round":"SF", "home": winners["A"], "away": winners["D"], "group":None, "slot":"SF1", "leg":1},
        {"week":CC_SF_LEGS[1], "round":"SF", "home": winners["D"], "away": winners["A"], "group":None, "slot":"SF1", "leg":2},
        {"week":CC_SF_LEGS[0], "round":"SF", "home": winners["B"], "away": winners["C"], "group":None, "slot":"SF2", "leg":1},
        {"week":CC_SF_LEGS[1], "round":"SF", "home": winners["C"], "away": winners["B"], "group":None, "slot":"SF2", "leg":2},
    ]
    fin = [{"week":CC_WEEK_FINAL, "round":"F", "home":"WSF1", "away":"WSF2", "group":None, "slot":"F1", "leg":1}]
    D["cc"]["fixtures"] += sf + fin
    D["cc"]["state"] = "KO"

def _cc_resolve_placeholder(name:str, winners:dict) -> str:
    if isinstance(name,str) and name.startswith("WSF"):
        return winners.get(name, name)
    return name

def simulate_continental_week(wk:int):
    D = st.session_state.data
    if "cc" not in D or not D["cc"]: return
    cc = D["cc"]
    todays = [f for f in cc["fixtures"] if f["week"] == wk]
    if not todays: return
    winners_map = {}
    for r in cc["results"]:
        if r["round"]=="SF" and r.get("winner"):
            winners_map["WSF1" if r["slot"]=="SF1" else "WSF2"] = r["winner"]
    for fx in todays:
        home = _cc_resolve_placeholder(fx.get("home"), winners_map)
        away = _cc_resolve_placeholder(fx.get("away"), winners_map)
        if not isinstance(home,str) or not isinstance(away,str) or home.startswith("W") or away.startswith("W"):
            continue
        if fx["round"]=="G":
            res = _simulate_match(home, away)
            winner = None if res["gh"]==res["ga"] else (home if res["gh"]>res["ga"] else away)
            if winner == USER_CLUB:
                D["budget"] += 200_000; log_finance(+200_000, "CC Group win bonus")
            elif res["gh"]==res["ga"] and (home==USER_CLUB or away==USER_CLUB):
                D["budget"] += 100_000; log_finance(+100_000, "CC Group draw bonus")
            _cc_apply_result(fx["group"], {"home":home,"away":away,"gh":res["gh"],"ga":res["ga"]})
            cc["results"].append({"week": wk, "round":"G", "group": fx.get("group"),
                                  "home": home, "away": away, "gh": int(res["gh"]), "ga": int(res["ga"]),
                                  "winner": winner, "slot": None, "leg": None})
        elif fx["round"]=="SF":
            res = _simulate_match(home, away)
            slot = fx["slot"]; leg = fx.get("leg",1)
            if leg == 1:
                cc["results"].append({"week": wk, "round":"SF", "group": None, "slot": slot, "leg": 1,
                                      "home": home, "away": away, "gh": int(res["gh"]), "ga": int(res["ga"]),
                                      "winner": None, "agg_h": int(res["gh"]), "agg_a": int(res["ga"])})
            else:
                first = next(r for r in cc["results"] if r["round"]=="SF" and r["slot"]==slot and r.get("leg")==1)
                agg_h = first["gh"] + res["ga"]
                agg_a = first["ga"] + res["gh"]
                if agg_h == agg_a:
                    if random.random()<0.5: agg_h += 1
                    else: agg_a += 1
                winner = first["home"] if agg_h > agg_a else first["away"]
                if winner == USER_CLUB:
                    D["budget"] += 1_200_000; log_finance(+1_200_000, "CC SF win bonus")
                cc["results"].append({"week": wk, "round":"SF", "group": None, "slot": slot, "leg": 2,
                                      "home": home, "away": away, "gh": int(res["gh"]), "ga": int(res["ga"]),
                                      "winner": winner, "agg_h": int(agg_h), "agg_a": int(agg_a)})
                winners_map["WSF1" if slot=="SF1" else "WSF2"] = winner
        else:
            res = _simulate_match(home, away)
            if res["gh"] == res["ga"]:
                if random.random()<0.5: res["gh"]+=1
                else: res["ga"]+=1
            winner = home if res["gh"]>res["ga"] else away
            if winner == USER_CLUB:
                D["budget"] += 3_000_000; log_finance(+3_000_000, "CC Final win bonus")
            cc["results"].append({"week": wk, "round":"F", "group": None, "slot":"F1", "leg":1,
                                  "home": home, "away": away, "gh": int(res["gh"]), "ga": int(res["ga"]),
                                  "winner": winner})

# ============================================
# Weekly Flow
# ============================================
def play_week():
    D = st.session_state.data
    apply_sponsor_income()
    apply_staff_weekly_costs()
    apply_player_wages_weekly()
    apply_installments_this_week()
    loan_weekly_tick()

    wk = D["week"]
    this_round = [m for m in D.get("fixtures", []) if m["week"] == wk]
    round_logs=[]
    for m in this_round:
        res = _simulate_match(m["home"], m["away"])
        _apply_result_to_table(m["div"], res)
        round_logs.append(f"{m['div']}  {res['home']} {res['gh']}-{res['ga']} {res['away']}")
    if round_logs:
        D["results_by_week"][wk] = round_logs

    simulate_continental_week(wk)
    scouting_weekly_tick()
    apply_mentoring_weekly()
    apply_growth_weekly()
    apply_training_weekly()
    generate_cpu_offers_for_your_players()
    simulate_cpu_resale()
    generate_rumors_weekly()

    D["week"] += 1
    if D["week"] > SEASON_WEEKS:
        sponsor_on_season_end()
        _promote_relegate()
        init_continental_groups_for_season()
        D["season"] += 1
        D["week"] = 1
        log_finance(0, "Season ended: Promotion/Relegation & new Cup seeded")
        youth_intake()

# ============================================
# UI
# ============================================
init_session()
apply_theme()  # テーマ適用

# ここで一度だけ初期化チェーンを完了
init_league()
ensure_ticket_price()
ensure_sponsor_state()
init_continental_groups_for_season()
ensure_scouting_state()
ensure_scout_reports()
ensure_registration_rules()
ensure_contract_state()
ensure_player_wages()
ensure_player_nations_and_hg()
ensure_rights_state()
ensure_news_state()

D = st.session_state.data

st.title(t("AppTitle"))

tabs = st.tabs([
    t("Market"),
    t("LoansFA"),
    t("Scouting"),
    t("Squad"),
    t("Finance"),
    t("Settings"),
    t("Weekly"),
    t("News")
])
tab_market, tab_loans, tab_scout, tab_squad, tab_fin, tab_set, tab_week, tab_news = tabs

# ------------- Market -------------
with tab_market:
    st.header("🛒 " + t("TransferMarket"))
    cpu_roster = D["players"][D["players"]["Club"]!=D["club_name"]].copy()
    if not cpu_roster.empty:
        cpu_roster["EstOV"] = cpu_roster["ID"].apply(visible_ov_for_user)
        cpu_roster["Label"] = cpu_roster["Name"] + " (" + cpu_roster["Club"] + ")  OV~" + cpu_roster["EstOV"].astype(str)
        st.dataframe(cpu_roster[["ID","Label","Pos","MV","Nat"]].set_index("ID").sort_values("MV", ascending=False).head(40))
        sel_id = st.number_input("Target Player ID", min_value=int(cpu_roster["ID"].min()),
                                 max_value=int(cpu_roster["ID"].max()),
                                 value=int(cpu_roster["ID"].min()))
    else:
        st.write("他クラブの選手がいません。")
        sel_id = None

    st.markdown("---")
    st.subheader("🤝 " + t("ContractNegotiation"))
    if sel_id is not None:
        base = baseline_terms_for(int(sel_id))
        c1,c2,c3 = st.columns(3)
        with c1:
            wage = st.number_input("週給 (€)", 0, 1_000_000, int(base["wage"]), 1000)
            signing = st.number_input("サインボーナス (€)", 0, 50_000_000, int(base["signing"]), 50_000)
        with c2:
            appsb = st.number_input("出場ボーナス/週 (€)", 0, 500_000, int(base["apps_bonus"]), 1000)
            goalsb= st.number_input("得点ボーナス/週 (€)", 0, 500_000, int(base["goals_bonus"]), 1000)
        with c3:
            years = st.slider("契約年数", 1, 5, max(2, base["length_weeks"]//52))
            clause= st.number_input("放出条項 (€)", 0, 500_000_000, int(base["release_clause"]), 100000)
        if "neg_round" not in st.session_state: st.session_state.neg_round = 1
        if st.button("🗣️ オファー提示"):
            offer = {"wage":int(wage), "signing":int(signing), "apps_bonus":int(appsb), "goals_bonus":int(goalsb),
                     "length_weeks": int(years*52), "release_clause": int(clause)}
            verdict = evaluate_contract_offer(int(sel_id), offer, st.session_state.neg_round)
            if verdict["decision"]=="accept":
                st.success("代理人が合意。条件を仮保存しました。")
                D["pending_terms"][int(sel_id)] = offer
                st.session_state.neg_round = 1
            elif verdict["decision"]=="counter":
                st.warning(f"カウンター提案: {verdict['counter']}")
                st.session_state.neg_round += 1
            else:
                st.error("交渉決裂。次のウィンドウで再挑戦。")
                st.session_state.neg_round = 1

    st.markdown("---")
    st.subheader("✍️ " + t("MakeOffer"))
    if sel_id is not None:
        with st.form("offer_form"):
            fee_total = st.number_input("移籍金 合計 (€)", 0, 500_000_000, 10_000_000, 100_000)
            upfront   = st.number_input("前金 (€)", 0, 500_000_000, 4_000_000, 100_000)
            inst_n    = st.number_input("分割回数", 0, 12, 2, 1)
            inst_freq = st.selectbox("分割頻度", ["yearly","halfyear","monthly"], index=0)
            sell_on   = st.slider("転売条項 %", 0.0, 0.3, 0.1, 0.05)
            with st.expander("高度な条項"):
                bb_on = st.checkbox("買い戻し条項を追加")
                bb_fee= st.number_input("買い戻し金額 (€)", 0, 200_000_000, 0, 100_000, disabled=not bb_on)
                bb_exp= st.number_input("買い戻し期限（シーズン）", 1, 20, D["season"]+3, disabled=not bb_on)
                mr_on = st.checkbox("マッチングライト（自クラブ保持）")
                mr_exp= st.number_input("マッチング期限（シーズン）", 1, 20, D["season"]+3, disabled=not mr_on)
            submitted = st.form_submit_button("送信")
            if submitted:
                if fee_total < upfront:
                    st.error("前金が合計を超えています。")
                else:
                    off = make_offer(
                        player_id=sel_id,
                        from_club=cpu_roster[cpu_roster["ID"]==sel_id].iloc[0]["Club"],
                        to_club=USER_CLUB, kind="permanent",
                        fee_total=int(fee_total), upfront=int(upfront), inst_count=int(inst_n),
                        sell_on_pct=float(sell_on), add_ons=[], loan=None,
                        inst_frequency=inst_freq,
                        buyback=({"fee":int(bb_fee),"expires":int(bb_exp)} if bb_on else None),
                        matching_right=({"holder":USER_CLUB,"expires":int(mr_exp)} if mr_on else None)
                    )
                    st.success(f"オファー #{off['id']} を送信しました。")

    st.markdown("---")
    st.subheader("📨 " + t("IncomingOutgoing"))
    st.dataframe(pd.DataFrame(D["transfer_offers"]) if D["transfer_offers"] else pd.DataFrame(columns=["id","player_id","from_club","to_club","fee_total"]))

# ------------- Loans & Free Agents -------------
with tab_loans:
    st.header("🔄 " + t("LoansAndFA"))
    fa = D["free_agents"].copy()
    if not fa.empty:
        fa["EstOV"] = fa["ID"].apply(visible_ov_for_user)
        st.dataframe(fa[["ID","Name","Pos","EstOV","MV","Nat"]].set_index("ID").sort_values("MV", ascending=False))
    else:
        st.write("フリーエージェントはいません。")

# ------------- Scouting & Academy -------------
with tab_scout:
    st.header("🔎 " + t("ScoutingAcademy"))
    ensure_scouting_state()
    sc_df = pd.DataFrame(D["scouts"])
    st.dataframe(sc_df.set_index("id"))

    st.markdown("**" + t("Assignments") + "**")
    for s in D["scouts"]:
        c1, c2, c3 = st.columns([1.2,1.2,2])
        with c1:
            atype = st.selectbox(f"Type #{s['id']}", ["region","club","shortlist"],
                                 index=["region","club","shortlist"].index(D["scout_assignments"][s["id"]]["type"]),
                                 key=f"atype_{s['id']}")
        with c2:
            if atype=="region":
                val = st.selectbox(f"Value #{s['id']}", ["EU","SA","AS","NA","AF","OC","GLB"], key=f"aval_{s['id']}")
            elif atype=="club":
                all_clubs = list(D["club_meta"].keys())
                val = st.selectbox(f"Value #{s['id']}", all_clubs, key=f"aval_{s['id']}")
            else:
                val = "shortlist"
        with c3:
            if st.button(f"{t('Save')} #{s['id']}", key=f"save_asg_{s['id']}"):
                D["scout_assignments"][s["id"]] = {"type": atype, "value": val}
                st.success("保存しました。")

    st.markdown("---")
    st.subheader(t("Recommendations"))
    pool = D["players"][D["players"]["Club"] != D["club_name"]].copy()
    if not pool.empty:
        pool["EstOV"] = pool["ID"].apply(visible_ov_for_user)
        rec = pool.sort_values("EstOV", ascending=False).head(20)[["ID","Name","Pos","Club","EstOV","MV"]]
        st.dataframe(rec.set_index("ID"))
        pick = st.number_input("ショートリストに追加 (ID)", min_value=int(rec.index.min()), max_value=int(rec.index.max()), value=int(rec.index.min()))
        if st.button("ショートリスト追加"):
            D["scout_shortlist"].add(int(pick))
            st.info("追加しました。")
    else:
        st.write("対象選手なし。")

    st.markdown("---")
    st.subheader(t("Academy"))
    ac = D.get("academy", pd.DataFrame())
    if ac is None or ac.empty:
        st.write("アカデミー選手はいません。")
        if st.button("ユース獲得を実行"):
            youth_intake(); st.success("実行しました。")
    else:
        show = ac[["ID","Name","Age","Pos","OV","POT","MV"]].copy()
        st.dataframe(show.set_index("ID"))
        c1, c2 = st.columns(2)
        with c1:
            if not show.empty:
                pid = st.number_input("昇格させるID", min_value=int(show.index.min()), max_value=int(show.index.max()), value=int(show.index.min()))
                if st.button("⬆️ 昇格"):
                    r = promote_from_academy(int(pid)); st.success("昇格しました。") if r=="ok" else st.error(r)
        with c2:
            if not show.empty:
                pid2 = st.number_input("解雇してFAへ (ID)", min_value=int(show.index.min()), max_value=int(show.index.max()), value=int(show.index.min()), key="rel_id")
                if st.button("🗑 解雇"):
                    r = release_from_academy(int(pid2)); st.success("フリーエージェントに移動。") if r=="ok" else st.error(r)

    st.markdown("---")
    st.subheader("🗂 " + t("ScoutReports"))
    if not D["players"].empty:
        pid_rep = st.number_input("レポートを見る選手ID", min_value=int(D["players"]["ID"].min()), max_value=int(D["players"]["ID"].max()), value=int(D["players"]["ID"].min()))
        reps = D["scout_reports"].get(int(pid_rep), [])
        if reps:
            for r in sorted(reps, key=lambda x:x["week"], reverse=True)[:5]:
                st.markdown(f"**W{r['week']} – {r['scout']} (⭐{r['grade']})**")
                st.code(r["summary"])
        else:
            st.write("レポートはありません。")

# ------------- Squad -------------
with tab_squad:
    st.header("👥 " + t("SquadHdr"))
    you = D["players"][D["players"]["Club"]==D["club_name"]]
    st.dataframe(you[["ID","Name","Pos","OV","POT","Age","MV","Nat","Morale","SPD","DEF","FIN","PosRoles"]].set_index("ID").sort_values("OV", ascending=False))

    st.markdown("---")
    st.subheader("🧠 " + t("Tactics"))
    ensure_tactics_state()
    tac = D["tactics"].get(D["club_name"], {"style":"balanced","line":50,"press":50,"tempo":50})
    t1,t2,t3,t4 = st.columns(4)
    with t1:
        style = st.selectbox("スタイル", ["balanced","possession","counter","direct","press"],
                             index=["balanced","possession","counter","direct","press"].index(tac["style"]))
    with t2:
        line = st.slider("ライン", 0, 100, int(tac["line"]))
    with t3:
        press= st.slider("プレス", 0, 100, int(tac["press"]))
    with t4:
        tempo= st.slider("テンポ", 0, 100, int(tac["tempo"]))
    if st.button("戦術を保存"):
        D["tactics"][D["club_name"]] = {"style":style,"line":int(line),"press":int(press),"tempo":int(tempo)}
        st.success("保存しました。")

    st.markdown("---")
    st.subheader("🏋️ " + t("Training"))
    ensure_training_state()
    if not you.empty:
        pid_tr = st.number_input("選手ID", min_value=int(you["ID"].min()), max_value=int(you["ID"].max()), value=int(you["ID"].min()), key="tp_pid")
        focus = st.selectbox("重点", ["speed","defense","finishing"])
        pos_t  = st.selectbox("ポジション転向（任意）", ["(なし)"]+POSITIONS)
        weeks  = st.slider("転向に必要な週", 0, 20, 8)
        if st.button("トレーニング保存"):
            plan = {"focus":focus}
            if pos_t != "(なし)":
                plan["pos_target"] = pos_t; plan["weeks_left"] = int(weeks)
            D["training_plans"][int(pid_tr)] = plan
            st.success("保存しました。")

    st.markdown("---")
    st.subheader("🤝 " + t("Mentoring"))
    ensure_mentoring_state()
    if not you.empty:
        mentor = st.selectbox("メンター", you["ID"].astype(int))
        mentee = st.selectbox("メンティ（≤22歳推奨）", you["ID"].astype(int), key="mentee_sel")
        if st.button("ペア追加"):
            if int(mentor)!=int(mentee):
                D["mentoring_pairs"].append({"mentor":int(mentor), "mentee":int(mentee)})
                st.success("追加しました。")
    st.caption(f"チーム化学ボーナス: {D.get('chemistry_bonus',{}).get(D['club_name'],0.0):.2f}")

    st.markdown("---")
    st.subheader("📝 " + t("ContractExt"))
    if not you.empty:
        pidx = st.number_input("自クラブ選手ID", min_value=int(you["ID"].min()), max_value=int(you["ID"].max()), value=int(you["ID"].min()), key="ext_pid")
        cur = D["contracts"].get(int(pidx))
        st.write("現在:", cur if cur else "(なし)")
        if cur:
            bw = baseline_terms_for(int(pidx))
            e1,e2,e3 = st.columns(3)
            with e1:
                nwage = st.number_input("週給 (€)", 0, 1_000_000, int(max(cur["wage"], bw["wage"]*0.9)), 1000, key="nw1")
                nsign = st.number_input("サインボーナス (€)", 0, 50_000_000, 0, 50_000, key="ns1")
            with e2:
                napp  = st.number_input("出場ボーナス (€)", 0, 500_000, cur["apps_bonus"], 1000, key="na1")
                ngoal = st.number_input("得点ボーナス (€)", 0, 500_000, cur["goals_bonus"], 1000, key="ng1")
            with e3:
                nyears= st.slider("延長年数", 1, 5, 2, key="ny1")
                ncl   = st.number_input("放出条項 (€)", 0, 500_000_000, cur["release_clause"], 100000, key="nc1")
            if st.button("交渉する"):
                off = {"wage":int(nwage), "signing":int(nsign), "apps_bonus":int(napp), "goals_bonus":int(ngoal),
                       "length_weeks": cur["length_weeks"] + int(nyears*52), "release_clause":int(ncl)}
                vd = evaluate_contract_offer(int(pidx), off, 1)
                if vd["decision"]=="accept":
                    finalize_contract_on_join(int(pidx), off); st.success("延長合意しました。")
                elif vd["decision"]=="counter":
                    st.info(f"代理人カウンター: {vd['counter']}")
                else:
                    st.warning("拒否されました。")

# ------------- Finance -------------
with tab_fin:
    st.header("💶 " + t("FinanceHdr"))
    ensure_sponsor_state()
    act = pd.DataFrame(D["sponsors_active"]) if D["sponsors_active"] else pd.DataFrame(columns=["brand","tier","weekly","bonus_top","bonus_win","seasons_left"])
    st.subheader("🤝 " + t("SponsorsActive"))
    st.dataframe(act)

    st.subheader("📝 " + t("SponsorOffers"))
    av = pd.DataFrame(D["sponsors_available"]) if D["sponsors_available"] else pd.DataFrame(columns=["id","brand","tier","weekly","bonus_top","bonus_win","seasons"])
    st.dataframe(av.set_index("id") if not av.empty else av)
    if D["sponsors_available"]:
        c1,c2 = st.columns(2)
        with c1:
            sid = st.number_input("契約するオファーID", min_value=int(min(x["id"] for x in D["sponsors_available"])),
                                  max_value=int(max(x["id"] for x in D["sponsors_available"])),
                                  value=int(min(x["id"] for x in D["sponsors_available"])))
            if st.button("✅ " + t("SignSponsor")):
                r = accept_sponsor(int(sid))
                st.success("契約しました。") if r=="ok" else st.error(r)
        with c2:
            if st.button("♻️ " + t("RefreshOffers")):
                generate_sponsor_offers(); st.info("更新しました。")

    st.subheader("💳 " + t("BudgetLedger"))
    st.metric("予算", f"€{D['budget']:,}")
    st.dataframe(pd.DataFrame(D["finance_log"]))

    you_ids = D["players"][D["players"]["Club"]==D["club_name"]]["ID"].astype(int).tolist()
    payroll_now = sum(D["contracts"].get(int(pid),{}).get("wage",0) for pid in you_ids)
    st.metric("週次給与（選手）", f"€{payroll_now:,}")

# ------------- Settings -------------
with tab_set:
    st.header("⚙️ " + t("SettingsHdr"))
    st.write(f"Season {D['season']} / Week {D['week']}")
    st.subheader("🎫 " + t("TicketPrice"))
    ensure_ticket_price()
    tp = st.slider("価格 (€)", 10, 80, int(D["ticket_price"]))
    if st.button("保存（チケット）"):
        D["ticket_price"] = int(tp)
        st.success("更新しました。")

# ------------- Weekly Tick -------------
with tab_week:
    st.header("⏭ " + t("WeeklyHdr"))
    col = st.columns(2)
    with col[0]:
        st.write(f"Season {D['season']} / Week {D['week']} — ウィンドウ: {'🟢 OPEN' if is_window_open() else '🔴 CLOSED'}")
        if st.button("▶️ " + t("NextWeek")):
            play_week(); st.success("1週進みました。")
    with col[1]:
        if st.button("CPU転売を即時シミュレート"):
            simulate_cpu_resale(prob_per_week=1.0, max_deals=1); st.success("実行しました。")

    st.markdown("---")
    st.subheader("📅 " + t("FixturesThisWeek"))
    wk = D["week"]
    fwk = [m for m in D.get("fixtures", []) if m["week"] == wk]
    if fwk:
        df_f = pd.DataFrame(fwk)[["div","home","away"]].rename(columns={"div":"Div","home":"Home","away":"Away"})
        st.table(df_f)
    else:
        st.write("今週は試合がありません。")

    st.subheader("📝 " + t("LastResults"))
    last = D["results_by_week"].get(wk-1, [])
    if last:
        for line in last: st.write(line)
    else:
        st.write("まだ結果はありません。")

    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("🏆 " + t("StandingsD1"))
        st.dataframe(D["standings"]["D1"].sort_values(["Pts","GD","GF"], ascending=[False,False,False]))
    with c2:
        st.subheader("🏆 " + t("StandingsD2"))
        st.dataframe(D["standings"]["D2"].sort_values(["Pts","GD","GF"], ascending=[False,False,False]))

    st.markdown("---")
    st.subheader("🌍 " + t("ContinentalHdr"))
    cc = D.get("cc")
    if cc:
        today = [f for f in cc["fixtures"] if f["week"]==D["week"]]
        if today:
            df_t = pd.DataFrame(today)[["round","group","slot","leg","home","away"]]
            st.caption("今週の大陸大会：")
            st.table(df_t)
        lastc = [r for r in cc["results"] if r["week"]==D["week"]-1]
        if lastc:
            df_l = pd.DataFrame(lastc)
            cols = ["round","group","slot","leg","home","gh","ga","away","winner"]
            if "agg_h" in df_l.columns and "agg_a" in df_l.columns:
                cols += ["agg_h","agg_a"]
            st.caption("前週の大陸大会結果：")
            st.table(df_l[cols])
        if cc["state"] in ("GROUP","KO"):
            c1,c2 = st.columns(2)
            with c1:
                st.write("Group A"); st.dataframe(_cc_group_rank("A"))
                st.write("Group B"); st.dataframe(_cc_group_rank("B"))
            with c2:
                st.write("Group C"); st.dataframe(_cc_group_rank("C"))
                st.write("Group D"); st.dataframe(_cc_group_rank("D"))

# ------------- News -------------
with tab_news:
    st.header("📰 " + t("NewsHdr"))
    if not D["news"]:
        st.write("ニュースはありません。")
    else:
        for i, n in enumerate(sorted(D["news"], key=lambda x:x["week"], reverse=True)[:30]):
            st.markdown(f"**W{n['week']} — {n.get('title','News')}**")
            st.write(n.get("body",""))
            if n.get("type")=="match_right":
                pid = int(n["player_id"]); price = int(n["price"]); frm = n["from_club"]
                if st.button(f"€{price:,} でマッチング（PID {pid}）", key=f"act_mr_{i}"):
                    r = exercise_matching_right(pid, price, frm)
                    st.success("マッチングして獲得！") if r=="ok" else st.error(r)
