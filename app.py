import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- UIデザイン + ボタン強調・ラジオ色・表・タッチ性 ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(120deg, #122042 0%, #202f52 100%) !important; color: #f6f7fa; }
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
        background: #162245;
        color: #f6f7fa;
        border-radius: 15px;
        padding: 16px 14px 7px 14px;
        margin: 6px 3px;
        box-shadow: 0 0 8px #12204244;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 160px; max-width: 200px;
        transition: 0.13s;
    }
    .player-card:hover {
        background: #fff03d22;
        color: #fff03d;
        transform: scale(1.05);
    }
    .clickable-name {color: #29d4ff; font-weight:700; text-decoration: underline; cursor:pointer;}
    .clickable-name:hover {color: #fff03d; background: #1c1f29;}
    .highlight-table {background: #1c263b !important;}
    </style>
""", unsafe_allow_html=True)

# --- 名前リスト（そのまま拡張可能） ---
name_pools ="日本": [
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
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)

# 詳細選手選択用
if "selected_player" not in st.session_state: st.session_state.selected_player = None

st.title("Soccer Club Management Sim v10 (UI Upgrade/Touch/Detail)")
main_tab = st.radio("View", ("Senior", "Youth", "Match", "Scout", "Standings", "Save"), horizontal=True)

def show_player_detail(row):
    st.markdown(f"<div class='player-card'>"
        f"<h4>{row['名前']}</h4>"
        f"<b>{row['ポジション']}</b> / {row['年齢']} / {row['国籍']}<br>"
        f"Contract:{row['契約年数']}｜Wage:{format_money(row['年俸'])}<br>"
        f"Club: {row.get('所属クラブ','-')}<br>", unsafe_allow_html=True)
    stats = [float(row[l]) for l in labels]
    stats += stats[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels)+1)
    fig, ax = plt.subplots(figsize=(2.7,2.7), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, color="#fff03d", linewidth=2)
    ax.fill(angles, stats, color="#fff03d", alpha=0.11)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9, color='#e9eaea')
    ax.set_yticklabels([])
    fig.patch.set_alpha(0.0)
    st.pyplot(fig, transparent=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Seniorタブ
if main_tab == "Senior":
    st.subheader("Senior Player List (Table + Cards)")
    show_df = df_senior[["名前","ポジション","年齢","国籍","契約年数","年俸"]+labels].copy()
    show_df["年俸"] = show_df["年俸"].apply(format_money)
    def clickable(name): return f"<span class='clickable-name'>{name}</span>"
    show_df["名前"] = show_df["名前"].apply(clickable)
    st.markdown(show_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.caption("Touch a player name for detail below.")
    # カードグリッド
    st.markdown("---")
    st.subheader("Card Grid View")
    cols = st.columns(4)
    for idx, row in df_senior.iterrows():
        with cols[idx%4]:
            if st.button(row['名前'], key=f"card_{idx}"):
                st.session_state.selected_player = row
            st.markdown(f"<div class='player-card'>{row['名前']}<br>{row['ポジション']} / {row['年齢']} / {row['国籍']}<br>Wage:{format_money(row['年俸'])}</div>", unsafe_allow_html=True)
    if st.session_state.selected_player is not None:
        st.markdown("---")
        st.subheader("Selected Player Detail")
        show_player_detail(st.session_state.selected_player)

# Youthタブ
if main_tab == "Youth":
    st.subheader("Youth Player List (Table + Cards)")
    show_df = df_youth[["名前","ポジション","年齢","国籍","契約年数","年俸"]+labels].copy()
    show_df["年俸"] = show_df["年俸"].apply(format_money)
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
            st.markdown(f"<div class='player-card'>{row['名前']}<br>{row['ポジション']} / {row['年齢']} / {row['国籍']}<br>Wage:{format_money(row['年俸'])}</div>", unsafe_allow_html=True)
    if st.session_state.selected_player is not None:
        st.markdown("---")
        st.subheader("Selected Player Detail")
        show_player_detail(st.session_state.selected_player)

# 順位表タブ（リッチ表示）
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

# 他タブ(Match, Scout, Save)はあなたの現状のままでOK
