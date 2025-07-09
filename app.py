import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- UIデザイン ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(120deg, #182a45 0%, #27345b 100%) !important; color: #f6f7fa; }
    .stDataFrame th, .stDataFrame td { color: #2fefff !important; background: #161f35 !important; font-size: 15px !important; }
    .stButton>button {
        background: linear-gradient(90deg, #26e0fc 30%, #2d7cf7 100%);
        color: #fff !important;
        border-radius: 16px !important;
        font-weight: bold;
        font-size: 1.08em !important;
        box-shadow: 0 0 5px #2fefff88;
        margin-top: 4px;
        margin-bottom: 6px;
        transition: 0.15s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #fff03d 30%, #f87d2a 100%);
        color: #101c2e !important;
        border: 2px solid #fff03d;
        transform: scale(1.07);
    }
    .css-1n76uvr, .stRadio [role='radiogroup'] label, .stTabs [role='tablist'] {
        background: #26386d !important;
        color: #fff !important;
        font-weight: 700 !important;
        border-radius: 16px;
        margin-bottom: 10px;
        padding: 8px 14px;
        font-size: 1.09em;
    }
    .player-card {
        background: #f8fafe;
        color: #1a233b;
        border-radius: 15px;
        padding: 18px 15px 10px 15px;
        margin: 6px 3px;
        box-shadow: 0 0 12px #13204233;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 170px; max-width: 220px;
        transition: 0.13s;
    }
    .player-card:hover {
        background: #fff03d33;
        color: #183d8c;
        transform: scale(1.05);
    }
    .clickable-name {color: #29d4ff; font-weight:700; text-decoration: underline; cursor:pointer;}
    .clickable-name:hover {color: #fff03d; background: #1c1f29;}
    .highlight-table {background: #1c263b !important;}
    </style>
""", unsafe_allow_html=True)

# --- 名前リスト ---
name_pools = {
    "日本": [
        "佐藤 翔","木村 隼人","西村 陸","大谷 陽平","本田 悠真","松岡 悠人","飯田 啓太","吉田 海斗","白石 翼","黒田 隆成",
        "長谷川 海斗","松本 凛","森本 優","斉藤 颯太","安藤 匠","高橋 拓真","小林 蓮","山本 大輝","田中 光","加藤 大和",
        "福島 光希","中村 慎吾","山崎 陸斗","藤井 悠馬","三浦 洸太","伊藤 楓","近藤 洋平","山口 航","岡田 駿","清水 晴斗",
        "柴田 航太","高田 樹","今村 拓海","遠藤 翔太","岡本 隼人","大野 涼太","矢野 海斗","原田 優太","内田 颯太","川口 航","岩本 誠"
    ],
    "ブラジル": [
        "マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ",
        "ブルーノ","レアンドロ","ファビオ","ダニーロ","グスタボ","ガブリエル","レナン","ヴィトル","ラファエル","ジョルジ",
        "チアゴ","エンリケ","レナト","カイオ","ジエゴ","ジウベルト","カルロス","イゴール","ラファ","ジュニオル"
    ],
    "スペイン": [
        "サンチェス","ロペス","マルティン","ミゲル","フェルナンド","フアン","カルロス","ダビド","ルイス","ペレス",
        "パブロ","ロドリゴ","アルバロ","セルヒオ","イバン","マリオ","マヌエル","ラウル","ヘスス","ゴンサロ",
        "マルコス","ディエゴ","サエス","サモラ","アドリアン","エステバン","アルベルト","イサーク","ジェラルド"
    ],
    "フランス": [
        "ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク",
        "ミカエル","ジュリアン","カミーユ","バスティアン","ロマン","アドリアン","ロイック","ガエル","ジョルダン","バンジャマン"
    ],
    "イタリア": [
        "ファビオ","マルコ","アレッサンドロ","ロッシ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ",
        "ルイジ","アントニオ","シモーネ","ジジ","パオロ","フランチェスコ","クラウディオ","ステファノ","クリスティアン","ニコラ"
    ],
    "ドイツ": [
        "クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル",
        "トビアス","フローリアン","クリストフ","ユリアン","モリッツ","フィリップ","アレクサンダー","シモン","フランク","オリバー"
    ],
    "イングランド": [
        "トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ルーカス",
        "ヘンリー","エドワード","ベンジャミン","ジョシュア","サミュエル","メイソン","ジョセフ","マシュー","リアム","アーチー"
    ],
}

def get_unique_name_by_nationality(nationality, used_names):
    pool = name_pools.get(nationality, [])
    for name in pool:
        if name not in used_names:
            return name
    return f"{nationality}Name{random.randint(100,999)}"

PLAYER_TEAM = "ストライバーFC"
AI_CLUB_NAMES = ["ブルーウルブズ", "ファルコンズ", "レッドスターズ", "ヴォルティス", "ユナイテッドFC", "オーシャンズ", "タイガース", "スカイバード"]
TEAM_NUM = 8
random.seed(42)
AI_TEAMS = AI_CLUB_NAMES[:TEAM_NUM-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_TEAMS
labels = ['Speed','Pass','Physical','Stamina','Defense','Technique','Mental','Shoot','Power']
currency_unit = "€"

def format_money(euro):
    if euro >= 1_000_000_000:
        return f"{euro/1_000_000_000:.2f}b{currency_unit}"
    elif euro >= 1_000_000:
        return f"{euro/1_000_000:.2f}m{currency_unit}"
    elif euro >= 1_000:
        return f"{euro/1_000:.1f}k{currency_unit}"
    return f"{int(euro)}{currency_unit}"

def calc_overall(row):
    return int(np.mean([float(row[l]) for l in labels]))

# --- セッション初期化 ---
if "current_round" not in st.session_state: st.session_state.current_round = 1
if "scout_list" not in st.session_state: st.session_state.scout_list = []
if "youth_scout_list" not in st.session_state: st.session_state.youth_scout_list = []
if "budget" not in st.session_state: st.session_state.budget = 1_000_000
if "team_points" not in st.session_state: st.session_state.team_points = {t: 0 for t in ALL_TEAMS}
if "match_log" not in st.session_state: st.session_state.match_log = []
if "ai_players" not in st.session_state:
    ai_players = []
    used_names = set()
    AI_TYPES = ["攻撃型", "守備型", "バランス型"]
    for t in AI_TEAMS:
        ai_type = random.choice(AI_TYPES)
        for i in range(20):
            nationality = random.choice(list(name_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            used_names.add(name)
            ai_players.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(19,32), "国籍": nationality,
                "Speed": random.randint(60,85), "Pass": random.randint(60,85),
                "Physical": random.randint(60,85), "Stamina": random.randint(60,85),
                "Defense": random.randint(60,85), "Technique": random.randint(60,85),
                "Mental": random.randint(60,85), "Shoot": random.randint(60,85),
                "Power": random.randint(60,85), "所属クラブ": t, "AIタイプ": ai_type,
                "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

df = pd.read_csv("players.csv")
column_rename = {
    'スピード': 'Speed',
    'パス': 'Pass',
    'フィジカル': 'Physical',
    'スタミナ': 'Stamina',
    'ディフェンス': 'Defense',
    'テクニック': 'Technique',
    'メンタル': 'Mental',
    'シュート': 'Shoot',
    'パワー': 'Power'
}
df = df.rename(columns=column_rename)
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000
df["Overall"] = df.apply(calc_overall, axis=1)
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)

if "selected_player" not in st.session_state: st.session_state.selected_player = None

st.title("Soccer Club Management Sim v10 (UI Ultra Upgrade/Touch/No Errors)")
main_tab = st.radio("View", ("Senior", "Youth", "Match", "Scout", "Standings", "Save"), horizontal=True)

def show_player_detail(row):
    st.markdown(f"<div class='player-card'>"
        f"<h4>{row['名前']} <span style='color:#0ca8e7;'>OVR:{row['Overall']}</span></h4>"
        f"<b>{row['ポジション']}</b> / {row['年齢']} / {row['国籍']}<br>"
        f"Contract:{row['契約年数']}｜Wage:{format_money(row['年俸'])}<br>"
        f"Club: {row.get('所属クラブ','-')}<br>", unsafe_allow_html=True)
    stats = [float(row[l]) for l in labels]
    stats += stats[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels)+1)
    fig, ax = plt.subplots(figsize=(2.6,2.6), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, color="#1c53d6", linewidth=2)
    ax.fill(angles, stats, color="#87d4ff", alpha=0.20)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9, color='#234')
    ax.set_yticklabels([])
    fig.patch.set_alpha(0.0)
    st.pyplot(fig, transparent=True)
    st.markdown("</div>", unsafe_allow_html=True)

def clickable(name): return f"<span class='clickable-name'>{name}</span>"

# Seniorタブ
if main_tab == "Senior":
    st.subheader("Senior Player List (Table + Cards)")
    show_df = df_senior[["名前","ポジション","年齢","国籍","契約年数","年俸","Overall"]+labels].copy()
    show_df["年俸"] = show_df["年俸"].apply(format_money)
    show_df["名前"] = show_df["名前"] + show_df["Overall"].apply(lambda ovr: f" <span style='color:#6cf;font-size:0.97em'>OVR:{ovr}</span>")
    show_df["名前"] = show_df["名前"].apply(clickable)
    st.markdown(show_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.caption("Touch a player name for detail below.")
    st.markdown("---")
    st.subheader("Card Grid View")
    cols = st.columns(4)
    for idx, row in df_senior.iterrows():
        with cols[idx%4]:
            if st.button(row['名前'], key=f"card_{idx}"):
                st.session_state.selected_player = row
            st.markdown(f"<div class='player-card'>{row['名前']}<br>{row['ポジション']} / {row['年齢']} / {row['国籍']}<br>OVR:{row['Overall']}｜Wage:{format_money(row['年俸'])}</div>", unsafe_allow_html=True)
    if st.session_state.selected_player is not None:
        st.markdown("---")
        st.subheader("Selected Player Detail")
        show_player_detail(st.session_state.selected_player)

# Youthタブ
if main_tab == "Youth":
    st.subheader("Youth Player List (Table + Cards)")
    show_df = df_youth[["名前","ポジション","年齢","国籍","契約年数","年俸","Overall"]+labels].copy()
    show_df["年俸"] = show_df["年俸"].apply(format_money)
    show_df["名前"] = show_df["名前"] + show_df["Overall"].apply(lambda ovr: f" <span style='color:#6cf;font-size:0.97em'>OVR:{ovr}</span>")
    show_df["名前"] = show_df["名前"].apply(clickable)
    st.markdown(show_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.caption("Touch a player name for detail below.")
    st.markdown("---")
    st.subheader("Card Grid View")
    cols = st.columns(4)
    for idx, row in df_youth.iterrows():
        with cols[idx%4]:
            if st.button(row['名前'], key=f"ycard_{idx}"):
                st.session_state.selected_player = row
            st.markdown(f"<div class='player-card'>{row['名前']}<br>{row['ポジション']} / {row['年齢']} / {row['国籍']}<br>OVR:{row['Overall']}｜Wage:{format_money(row['年俸'])}</div>",

print("もちろんです!")
**選手の総合値（平均）を表やカードで表示、詳細表示、背景色修正、すべて統合版**です。  
**app.pyにまるごとコピペでOKです。**

---

```python
import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- UIデザイン ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(120deg, #182a45 0%, #27345b 100%) !important; color: #f6f7fa; }
    .stDataFrame th, .stDataFrame td { color: #2fefff !important; background: #161f35 !important; font-size: 15px !important; }
    .stButton>button {
        background: linear-gradient(90deg, #26e0fc 30%, #2d7cf7 100%);
        color: #fff !important;
        border-radius: 16px !important;
        font-weight: bold;
        font-size: 1.08em !important;
        box-shadow: 0 0 5px #2fefff88;
        margin-top: 4px;
        margin-bottom: 6px;
        transition: 0.15s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #fff03d 30%, #f87d2a 100%);
        color: #101c2e !important;
        border: 2px solid #fff03d;
        transform: scale(1.07);
    }
    .css-1n76uvr, .stRadio [role='radiogroup'] label, .stTabs [role='tablist'] {
        background: #26386d !important;
        color: #fff !important;
        font-weight: 700 !important;
        border-radius: 16px;
        margin-bottom: 10px;
        padding: 8px 14px;
        font-size: 1.09em;
    }
    .player-card {
        background: #f8fafe !important;
        color: #122042 !important;
        border-radius: 16px !important;
        padding: 18px 15px 10px 15px;
        margin: 6px 3px;
        box-shadow: 0 0 12px #1cefff55;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 170px; max-width: 220px;
        transition: 0.13s;
    }
    .player-card:hover {
        background: #fff03d44 !important;
        color: #183d8c !important;
        transform: scale(1.05);
    }
    .clickable-name {color: #29d4ff; font-weight:700; text-decoration: underline; cursor:pointer;}
    .clickable-name:hover {color: #fff03d; background: #1c1f29;}
    .highlight-table {background: #1c263b !important;}
    </style>
""", unsafe_allow_html=True)

# --- 名前リスト ---
name_pools = {
    "日本": [
        "佐藤 翔","木村 隼人","西村 陸","大谷 陽平","本田 悠真","松岡 悠人","飯田 啓太","吉田 海斗","白石 翼","黒田 隆成",
        "長谷川 海斗","松本 凛","森本 優","斉藤 颯太","安藤 匠","高橋 拓真","小林 蓮","山本 大輝","田中 光","加藤 大和",
        "福島 光希","中村 慎吾","山崎 陸斗","藤井 悠馬","三浦 洸太","伊藤 楓","近藤 洋平","山口 航","岡田 駿","清水 晴斗",
        "柴田 航太","高田 樹","今村 拓海","遠藤 翔太","岡本 隼人","大野 涼太","矢野 海斗","原田 優太","内田 颯太","川口 航","岩本 誠"
    ],
    "ブラジル": [
        "マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ",
        "ブルーノ","レアンドロ","ファビオ","ダニーロ","グスタボ","ガブリエル","レナン","ヴィトル","ラファエル","ジョルジ",
        "チアゴ","エンリケ","レナト","カイオ","ジエゴ","ジウベルト","カルロス","イゴール","ラファ","ジュニオル"
    ],
    "スペイン": [
        "サンチェス","ロペス","マルティン","ミゲル","フェルナンド","フアン","カルロス","ダビド","ルイス","ペレス",
        "パブロ","ロドリゴ","アルバロ","セルヒオ","イバン","マリオ","マヌエル","ラウル","ヘスス","ゴンサロ",
        "マルコス","ディエゴ","サエス","サモラ","アドリアン","エステバン","アルベルト","イサーク","ジェラルド"
    ],
    "フランス": [
        "ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク",
        "ミカエル","ジュリアン","カミーユ","バスティアン","ロマン","アドリアン","ロイック","ガエル","ジョルダン","バンジャマン"
    ],
    "イタリア": [
        "ファビオ","マルコ","アレッサンドロ","ロッシ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ",
        "ルイジ","アントニオ","シモーネ","ジジ","パオロ","フランチェスコ","クラウディオ","ステファノ","クリスティアン","ニコラ"
    ],
    "ドイツ": [
        "クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル",
        "トビアス","フローリアン","クリストフ","ユリアン","モリッツ","フィリップ","アレクサンダー","シモン","フランク","オリバー"
    ],
    "イングランド": [
        "トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ルーカス",
        "ヘンリー","エドワード","ベンジャミン","ジョシュア","サミュエル","メイソン","ジョセフ","マシュー","リアム","アーチー"
    ],
}
def get_unique_name_by_nationality(nationality, used_names):
    pool = name_pools.get(nationality, [])
    for name in pool:
        if name not in used_names:
            return name
    return f"{nationality}Name{random.randint(100,999)}"

PLAYER_TEAM = "ストライバーFC"
AI_CLUB_NAMES = ["ブルーウルブズ", "ファルコンズ", "レッドスターズ", "ヴォルティス", "ユナイテッドFC", "オーシャンズ", "タイガース", "スカイバード"]
TEAM_NUM = 8
random.seed(42)
AI_TEAMS = AI_CLUB_NAMES[:TEAM_NUM-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_TEAMS
labels = ['Speed','Pass','Physical','Stamina','Defense','Technique','Mental','Shoot','Power']
currency_unit = "€"

def format_money(euro):
    if euro >= 1_000_000_000:
        return f"{euro/1_000_000_000:.2f}b{currency_unit}"
    elif euro >= 1_000_000:
        return f"{euro/1_000_000:.2f}m{currency_unit}"
    elif euro >= 1_000:
        return f"{euro/1_000:.1f}k{currency_unit}"
    return f"{int(euro)}{currency_unit}"

if "current_round" not in st.session_state: st.session_state.current_round = 1
if "scout_list" not in st.session_state: st.session_state.scout_list = []
if "youth_scout_list" not in st.session_state: st.session_state.youth_scout_list = []
if "budget" not in st.session_state: st.session_state.budget = 1_000_000
if "team_points" not in st.session_state: st.session_state.team_points = {t: 0 for t in ALL_TEAMS}
if "match_log" not in st.session_state: st.session_state.match_log = []
if "ai_players" not in st.session_state:
    ai_players = []
    used_names = set()
    AI_TYPES = ["攻撃型", "守備型", "バランス型"]
    for t in AI_TEAMS:
        ai_type = random.choice(AI_TYPES)
        for i in range(20):
            nationality = random.choice(list(name_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            used_names.add(name)
            ai_players.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(19,32), "国籍": nationality,
                "Speed": random.randint(60,85), "Pass": random.randint(60,85),
                "Physical": random.randint(60,85), "Stamina": random.randint(60,85),
                "Defense": random.randint(60,85), "Technique": random.randint(60,85),
                "Mental": random.randint(60,85), "Shoot": random.randint(60,85),
                "Power": random.randint(60,85), "所属クラブ": t, "AIタイプ": ai_type,
                "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

df = pd.read_csv("players.csv")
column_rename = {
    'スピード': 'Speed', 'パス': 'Pass', 'フィジカル': 'Physical', 'スタミナ': 'Stamina',
    'ディフェンス': 'Defense', 'テクニック': 'Technique', 'メンタル': 'Mental',
    'シュート': 'Shoot', 'パワー': 'Power'
}
df = df.rename(columns=column_rename)
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000

df["総合"] = df[labels].mean(axis=1).astype(int)
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)

if "selected_player" not in st.session_state: st.session_state.selected_player = None

st.title("Soccer Club Management Sim v10 (Ultra UI/Touch/No Error)")

main_tab = st.radio("View", ("Senior", "Youth", "Match", "Scout", "Standings", "Save"), horizontal=True)

def show_player_detail(row):
    st.markdown(f"<div class='player-card'>"
        f"<h4>{row['名前']}</h4>"
        f"<b>{row['ポジション']}</b> / {row['年齢']} / {row['国籍']}<br>"
        f"Overall: <b style='color:#2b98ef;'>{row['総合']}</b>｜Contract:{row['契約年数']}｜Wage:{format_money(row['年俸'])}<br>"
        f"Club: {row.get('所属クラブ','-')}<br>", unsafe_allow_html=True)
    stats = [float(row[l]) for l in labels]
    stats += stats[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels)+1)
    fig, ax = plt.subplots(figsize=(2.5,2.5), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, color="#26e0fc", linewidth=2)
    ax.fill(angles, stats, color="#29d4ff", alpha=0.13)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9, color='#182a45')
    ax.set_yticklabels([])
    fig.patch.set_alpha(0.0)
    st.pyplot(fig, transparent=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Seniorタブ
if main_tab == "Senior":
    st.subheader("Senior Player List (Table + Cards)")
    show_df = df_senior[["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]+labels].copy()
    show_df["年俸"] = show_df["年俸"].apply(format_money)
    def clickable(name): return f"<span class='clickable-name'>{name}</span>"
    show_df["名前"] = [clickable(n)+f" <span style='color:#5feaff;'>{o}</span>" for n,o in zip(df_senior["名前"],df_senior["総合"])]
    st.markdown(show_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.caption("タップで選手詳細（下部）")
    # カードグリッド
    st.markdown("---")
    st.subheader("Card Grid View")
    cols = st.columns(4)
    for idx, row in df_senior.iterrows():
        with cols[idx%4]:
            if st.button(f"{row['名前']}({row['総合']})", key=f"card_{idx}"):
                st.session_state.selected_player = row
            st.markdown(
                f"<div class='player-card'>{row['名前']} <span style='color:#27b0e7;'>({row['総合']})</span><br>"
                f"{row['ポジション']} / {row['年齢']} / {row['国籍']}<br>Wage:{format_money(row['年俸'])}</div>", 
                unsafe_allow_html=True)
    if st.session_state.selected_player is not None:
        st.markdown("---")
        st.subheader("Selected Player Detail")
        show_player_detail(st.session_state.selected_player)

# Youthタブ
if main_tab == "Youth":
    st.subheader("Youth Player List (Table + Cards)")
    show_df = df_youth[["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]+labels].copy()
    show_df["年俸"] = show_df["年俸"].apply(format_money)
    show_df["名前"] = [clickable(n)+f" <span style='color:#5feaff;'>{o}</span>" for n,o in zip(df_youth["名前"],df_youth["総合"])]
    st.markdown(show_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.caption("タップで選手詳細（下部）")
    st.markdown("---")
    st.subheader("Card Grid View")
    cols = st.columns(4)
    for idx, row in df_youth.iterrows():
        with cols[idx%4]:
            if st.button(f"{row['名前']}({row['総合']})", key=f"ycard_{idx}"):
                st.session_state.selected_player = row
            st.markdown(
                f"<div class='player-card'>{row['名前']} <span style='color:#27b0e7;'>({row['総合']})</span><br>"
                f"{row['ポジション']} / {row['年齢']} / {row['国籍']}<br>Wage:{format_money(row['年俸'])}</div>",
                unsafe_allow_html=True)
    if st.session_state.selected_player is not None:
        st.markdown("---")
        st.subheader("Selected Player Detail")
        show_player_detail(st.session_state.selected_player)

# Matchタブ
if main_tab == "Match":
    st.subheader("Match Simulation")
    round_idx = (st.session_state.current_round-1)%len(AI_TEAMS)
    enemy = AI_TEAMS[round_idx]
    st.write(f"今節: {PLAYER_TEAM} vs {enemy}")
    auto_starters = df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist()
    starters = st.multiselect("Starting XI", df_senior["名前"].tolist(), default=auto_starters)
    if len(starters) != 11:
        st.warning("11人ちょうど選んでください")
    else:
        tactics = st.selectbox("Tactics", ["Attack", "Balanced", "Defensive", "Counter", "Possession"])
        team_strength = df_senior[df_senior["名前"].isin(starters)][labels].mean().mean()
        ai_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==enemy]
        ai_strength = ai_df[labels].mean().mean()
        if tactics=="Attack": team_strength *= 1.08
        elif tactics=="Defensive": team_strength *= 0.93
        elif tactics=="Counter": team_strength *= 1.04
        elif tactics=="Possession": team_strength *= 1.03
        pwin = (team_strength / (team_strength+ai_strength)) if (team_strength+ai_strength)>0 else 0.5
        fig, ax = plt.subplots(figsize=(4,1.4))
        ax.bar(["You","AI"], [team_strength, ai_strength], color=["#22e","#ccc"])
        ax.set_xticks([0,1]); ax.set_ylabel("平均能力")
        ax.set_title(f"チーム力比較（推定勝率: {int(100*pwin)}%）", color="#f4f8fc")
        fig.patch.set_alpha(0)
        st.pyplot(fig, transparent=True)
        if st.button("Kickoff!"):
            my_goals = max(0, int(random.gauss((team_strength-60)/8, 1.0)))
            op_goals = max(0, int(random.gauss((ai_strength-60)/8, 1.0)))
            if my_goals > op_goals:
                result = "Win"
                st.session_state.team_points[PLAYER_TEAM] += 3
            elif my_goals < op_goals:
                result = "Lose"
                st.session_state.team_points[enemy] += 3
            else:
                result = "Draw"
                st.session_state.team_points[PLAYER_TEAM] += 1
                st.session_state.team_points[enemy] += 1
            st.success(f"{result}! {my_goals}-{op_goals}")
            st.session_state.current_round += 1
            st.session_state.match_log.append(f"Round {st.session_state.current_round-1}: {PLAYER_TEAM} vs {enemy}: {my_goals}-{op_goals}")

# Scoutタブ
if main_tab == "Scout":
    st.subheader("Scout Candidates")
    st.info(f"Budget: {format_money(st.session_state.budget)}")
    if st.button("Refresh List"):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_list = []
        for _ in range(5):
            nationality = random.choice(list(name_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            used_names.add(name)
            st.session_state.scout_list.append({
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(19, 29),
                "国籍": nationality,
                "Speed": random.randint(60, 80),
                "Pass": random.randint(60, 80),
                "Physical": random.randint(60, 80),
                "Stamina": random.randint(60, 80),
                "Defense": random.randint(60, 80),
                "Technique": random.randint(60, 80),
                "Mental": random.randint(60, 80),
                "Shoot": random.randint(60, 80),
                "Power": random.randint(60, 80),
                "契約年数": 2,
                "年俸": random.randint(100_000,180_000),
                "得点": 0,
                "出場数": 0,
                "所属クラブ": PLAYER_TEAM
            })
    cols = st.columns(5)
    for idx, player in enumerate(st.session_state.scout_list):
        with cols[idx%5]:
            ovr = int(np.mean([player[l] for l in labels]))
            st.markdown(
                f"<div class='player-card'><b>{player['名前']}</b> <span style='color:#2cabe8;'>(OVR:{ovr})</span><br>"
                f"{player['ポジション']} / {player['年齢']} / {player['国籍']}<br>"
                f"契約:{player['契約年数']}年｜年俸:{format_money(player['年俸'])}</div>", 
                unsafe_allow_html=True)
            if st.button("加入", key=f"scout_{idx}"):
                df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                df.to_csv("players.csv", index=False)
                st.session_state.budget -= player['年俸']
                st.success(f"{player['名前']} signed!")

# Standingsタブ
if main_tab == "Standings":
    st.subheader("League Standings")
    tbl = []
    for t in ALL_TEAMS:
        total_goals = 0
        if t == PLAYER_TEAM:
            total_goals = df_senior["得点"].sum()
        else:
            ai_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==t]
            total_goals = ai_df["得点"].sum() if "得点" in ai_df.columns else 0
        tbl.append([t, st.session_state.team_points.get(t,0), total_goals])
    dft = pd.DataFrame(tbl, columns=["Club","Pts","Goals"])
    dft = dft.sort_values(["Pts","Goals"], ascending=[False,False]).reset_index(drop=True)
    dft["Rank"] = dft.index + 1
    st.markdown(dft[["Rank","Club","Pts","Goals"]].to_html(index=False), unsafe_allow_html=True)
    if st.session_state.match_log:
        st.markdown("**Recent Matches**")
        for l in st.session_state.match_log[-5:][::-1]:
            st.text(l)

# Saveタブ
if main_tab == "Save":
    st.subheader("Data Save")
    if st.button("Save (players.csv)"):
        df.to_csv("players.csv", index=False)
        st.success("Saved! (players.csv)")
    if st.button("Save AI Players List"):
        st.session_state.ai_players.to_csv("ai_players.csv", index=False)
        st.success("AI Players list saved.")
