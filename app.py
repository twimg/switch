import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import os

# --- デザイン（紺色背景＋白系フォント強調） ---
st.markdown("""
    <style>
    .stApp { background-color: #122042; color: #f4f8fc; }
    .css-1cypcdb, .css-ffhzg2, .css-10trblm, .st-emotion-cache-1cypcdb, .st-emotion-cache-ffhzg2 { color: #f4f8fc !important; }
    .stDataFrame th, .stDataFrame td { color: #1cefff !important; background: #101a33 !important; }
    .stButton>button { background: #0e3959; color: #fff; font-weight: 600; border-radius:8px; }
    .st-b6, .st-emotion-cache-1wmy9hl, .stRadio>div>label { color: #fff !important; }
    </style>
""", unsafe_allow_html=True)

# --- 定数 ---
PLAYER_TEAM = "ストライバーFC"
AI_CLUB_NAMES = ["ブルーウルブズ", "ファルコンズ", "レッドスターズ", "ヴォルティス", "ユナイテッドFC", "オーシャンズ", "タイガース", "スカイバード"]
TEAM_NUM = 8
random.seed(42)
AI_TEAMS = AI_CLUB_NAMES[:TEAM_NUM-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_TEAMS
labels = ['スピード','パス','フィジカル','スタミナ','ディフェンス','テクニック','メンタル','シュート','パワー']
currency_unit = "€"

# --- 名前データ ---
name_pools = {
    "日本": ["佐藤 翔","木村 隼人","西村 陸","大谷 陽平","本田 悠真","松岡 悠人","飯田 啓太","吉田 海斗","白石 翼","黒田 隆成","長谷川 海斗","松本 凛","森本 優","斉藤 颯太","安藤 匠"],
    "ブラジル": ["マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ"],
    "スペイン": ["サンチェス","ロペス","マルティン","ミゲル","フェルナンド","フアン","カルロス","ダビド","ルイス","ペレス"],
    "フランス": ["ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク"],
    "イタリア": ["ファビオ","マルコ","アレッサンドロ","ロッシ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ"],
    "ドイツ": ["クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル"],
    "イングランド": ["トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ルーカス"]
}
def get_unique_name_by_nationality(nationality, used_names):
    pool = name_pools.get(nationality, [])
    for name in pool:
        if name not in used_names:
            return name
    # 枯渇時は「国名ネーム+乱数」
    return f"{nationality}ネーム{random.randint(100,999)}"

# --- ユーロ表記(k,m,b) ---
def format_money(euro):
    if euro >= 1_000_000_000:
        return f"{euro/1_000_000_000:.2f}b{currency_unit}"
    elif euro >= 1_000_000:
        return f"{euro/1_000_000:.2f}m{currency_unit}"
    elif euro >= 1_000:
        return f"{euro/1_000:.1f}k{currency_unit}"
    return f"{int(euro)}{currency_unit}"

# --- 初期セッション ---
if "current_round" not in st.session_state:
    st.session_state.current_round = 1
if "scout_list" not in st.session_state:
    st.session_state.scout_list = []
if "youth_scout_list" not in st.session_state:
    st.session_state.youth_scout_list = []
if "budget" not in st.session_state:
    st.session_state.budget = 1_000_000  # =1M€
if "team_points" not in st.session_state:
    st.session_state.team_points = {t: 0 for t in ALL_TEAMS}
if "match_log" not in st.session_state:
    st.session_state.match_log = []
if "contract_years" not in st.session_state:
    st.session_state.contract_years = {}
if "salary" not in st.session_state:
    st.session_state.salary = {}
if "starters" not in st.session_state:
    st.session_state.starters = []
if "ai_players" not in st.session_state:
    # 20人多国籍AI
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
                "スピード": random.randint(60,85), "パス": random.randint(60,85),
                "フィジカル": random.randint(60,85), "スタミナ": random.randint(60,85),
                "ディフェンス": random.randint(60,85), "テクニック": random.randint(60,85),
                "メンタル": random.randint(60,85), "シュート": random.randint(60,85),
                "パワー": random.randint(60,85), "所属クラブ": t, "AIタイプ": ai_type,
                "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

# --- データ読込＆初期分割 ---
df = pd.read_csv("players.csv")
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)

# === タイトル・UI ===
st.title("サッカー運営シミュレーション v8+（統合/新UI）")
st.markdown(f"**現在 {st.session_state.current_round} 節｜予算**: {format_money(st.session_state.budget)}")
main_tab = st.radio("表示", ("シニア", "ユース", "試合", "スカウト", "順位表", "セーブ"), horizontal=True)

# === シニア選手リスト ===
if main_tab == "シニア":
    st.subheader("【シニア選手一覧】")
    dfv = df_senior.sort_values("得点", ascending=False).reset_index(drop=True)
    for idx, row in dfv.iterrows():
        col1, col2 = st.columns([2,4])
        with col1:
            st.markdown(f"<span style='font-size:1.1em;font-weight:bold;'>{row['名前']}</span> ({row['ポジション']}/{row['年齢']}歳/{row['国籍']})", unsafe_allow_html=True)
            st.text(f"契約:{row['契約年数']}年｜年俸:{format_money(row['年俸'])}")
        with col2:
            labels8 = labels
            stats = [float(row[l]) for l in labels8]
            stats += stats[:1]
            angles = np.linspace(0, 2 * np.pi, len(labels8)+1)
            fig, ax = plt.subplots(figsize=(2.6,2.6), subplot_kw=dict(polar=True))
            ax.plot(angles, stats, color="#1cefff", linewidth=2)
            ax.fill(angles, stats, color="#1cefff", alpha=0.13)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels8, fontsize=8, color='#f4f8fc')
            ax.set_yticklabels([])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, transparent=True)
        st.divider()

# === ユースリスト & スカウト ===
if main_tab == "ユース":
    st.subheader("【ユース選手一覧】")
    dfv = df_youth.sort_values("年齢").reset_index(drop=True)
    for idx, row in dfv.iterrows():
        col1, col2 = st.columns([2,4])
        with col1:
            st.markdown(f"<span style='font-size:1.1em;font-weight:bold;'>{row['名前']}</span> ({row['ポジション']}/{row['年齢']}歳/{row['国籍']})", unsafe_allow_html=True)
            st.text(f"契約:{row['契約年数']}年｜年俸:{format_money(row['年俸'])}")
        with col2:
            stats = [float(row[l]) for l in labels]
            stats += stats[:1]
            angles = np.linspace(0, 2 * np.pi, len(labels)+1)
            fig, ax = plt.subplots(figsize=(2.6,2.6), subplot_kw=dict(polar=True))
            ax.plot(angles, stats, color="#ffef41", linewidth=2)
            ax.fill(angles, stats, color="#ffef41", alpha=0.13)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=8, color='#f4f8fc')
            ax.set_yticklabels([])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, transparent=True)
        st.divider()
    st.subheader("【ユーススカウト】")
    if st.button("ユーススカウトリストを更新"):
        used_names = set(df_youth["名前"].tolist()) | set(df["名前"].tolist())
        st.session_state.youth_scout_list = []
        for _ in range(5):
            nationality = random.choice(list(name_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            is_ituzai = random.random() < 0.05
            used_names.add(name)
            st.session_state.youth_scout_list.append({
                "名前": name,
                "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(14,17),
                "国籍": nationality,
                "スピード": random.randint(55, 80),
                "パス": random.randint(55, 80),
                "フィジカル": random.randint(55, 80),
                "スタミナ": random.randint(55, 80),
                "ディフェンス": random.randint(55, 80),
                "テクニック": random.randint(55, 80),
                "メンタル": random.randint(55, 80),
                "シュート": random.randint(55, 80),
                "パワー": random.randint(55, 80),
                "逸材": is_ituzai,
                "契約年数": 3,
                "年俸": random.randint(60_000,90_000),
                "得点": 0,
                "出場数": 0,
                "所属クラブ": PLAYER_TEAM
            })
    for idx, player in enumerate(st.session_state.youth_scout_list):
        col1, col2 = st.columns([3,1])
        with col1:
            mark = "【逸材!!】" if player.get("逸材") else ""
            st.write(f"{player['名前']} ({player['ポジション']}/{player['年齢']}歳/{player['国籍']}) {mark}")
            st.write({k: v for k,v in player.items() if k not in ["名前","ポジション","年齢","国籍","逸材"]})
        with col2:
            btn_key = f"youthscout_{idx}"
            if st.button("加入", key=btn_key):
                df_youth = pd.concat([df_youth, pd.DataFrame([player])], ignore_index=True)
                df_youth.to_csv("players.csv", index=False)
                st.success(f"{player['名前']}がユース加入！")

# === 試合（スタメン選択/チーム力比較/戦術増） ===
if main_tab == "試合":
    st.subheader("【スタメン11人を選択】")
    candidates = df_senior["名前"].tolist()
    starters = st.multiselect("出場メンバー（11人）", candidates, default=candidates[:11])
    if len(starters) != 11:
        st.warning("11人ちょうど選んでください")
    st.subheader("【戦術選択】")
    tactics = st.selectbox("チーム戦術", ["攻撃的", "バランス", "守備的", "カウンター", "ポゼッション"])
    st.subheader("【対戦相手AI選択】")
    enemy = st.selectbox("対戦相手", AI_TEAMS)
    # チーム力比較グラフ
    team_strength = df_senior[df_senior["名前"].isin(starters)][labels].mean().mean()
    ai_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==enemy]
    ai_strength = ai_df[labels].mean().mean()
    if tactics=="攻撃的": team_strength *= 1.08
    elif tactics=="守備的": team_strength *= 0.93
    elif tactics=="カウンター": team_strength *= 1.04
    elif tactics=="ポゼッション": team_strength *= 1.03
    # 勝率計算（ざっくり）
    pwin = (team_strength / (team_strength+ai_strength)) if (team_strength+ai_strength)>0 else 0.5
    fig, ax = plt.subplots(figsize=(4,1.5))
    ax.bar(["自クラブ","AI"], [team_strength, ai_strength], color=["#28f","#eee"])
    ax.set_xticks([0,1]); ax.set_ylabel("平均能力")
    ax.set_title(f"チーム力比較（推定勝率: {int(100*pwin)}%）", color="w")
    fig.patch.set_alpha(0)
    st.pyplot(fig, transparent=True)
    if st.button("試合開始！"):
        my_goals = max(0, int(random.gauss((team_strength-60)/8, 1.0)))
        op_goals = max(0, int(random.gauss((ai_strength-60)/8, 1.0)))
        # 勝ち点
        if my_goals > op_goals:
            result = "勝利"
            st.session_state.team_points[PLAYER_TEAM] += 3
        elif my_goals < op_goals:
            result = "敗北"
            st.session_state.team_points[enemy] += 3
        else:
            result = "引き分け"
            st.session_state.team_points[PLAYER_TEAM] += 1
            st.session_state.team_points[enemy] += 1
        st.success(f"{result}！ {my_goals}-{op_goals}")
        st.session_state.current_round += 1
        st.session_state.match_log.append(f"{st.session_state.current_round-1}節 {PLAYER_TEAM} vs {enemy}: {my_goals}-{op_goals}")

# === スカウト（シニア） ===
if main_tab == "スカウト":
    st.subheader("【シニアスカウト】")
    st.info(f"予算: {format_money(st.session_state.budget)}")
    if st.button("スカウトリストを更新"):
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
                "スピード": random.randint(60, 80),
                "パス": random.randint(60, 80),
                "フィジカル": random.randint(60, 80),
                "スタミナ": random.randint(60, 80),
                "ディフェンス": random.randint(60, 80),
                "テクニック": random.randint(60, 80),
                "メンタル": random.randint(60, 80),
                "シュート": random.randint(60, 80),
                "パワー": random.randint(60, 80),
                "契約年数": 2,
                "年俸": random.randint(100_000,180_000),
                "得点": 0,
                "出場数": 0,
                "所属クラブ": PLAYER_TEAM
            })
    for idx, player in enumerate(st.session_state.scout_list):
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"{player['名前']} ({player['ポジション']}/{player['年齢']}歳/{player['国籍']})")
            st.write({k: v for k,v in player.items() if k not in ["名前","ポジション","年齢","国籍"]})
        with col2:
            btn_key = f"scout_{idx}"
            if st.button("加入", key=btn_key):
                df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                df.to_csv("players.csv", index=False)
                st.session_state.budget -= player['年俸']
                st.success(f"{player['名前']}が加入！")

# === 順位表/リーグ管理 ===
if main_tab == "順位表":
    st.subheader("【リーグ順位表】")
    tbl = []
    for t in ALL_TEAMS:
        tbl.append([t, st.session_state.team_points.get(t,0)])
    dft = pd.DataFrame(tbl, columns=["クラブ","勝ち点"])
    st.dataframe(dft.sort_values("勝ち点", ascending=False), use_container_width=True)
    if st.session_state.match_log:
        st.markdown("**直近試合ログ**")
        for l in st.session_state.match_log[-5:][::-1]:
            st.text(l)

# === セーブ機能 ===
if main_tab == "セーブ":
    st.subheader("【セーブ】")
    if st.button("データ保存（players.csv）"):
        df.to_csv("players.csv", index=False)
        st.success("セーブ完了！（players.csv）")
    if st.button("AIクラブ選手リスト保存"):
        st.session_state.ai_players.to_csv("ai_players.csv", index=False)
        st.success("AIクラブ選手リストも保存しました")

# === END ===
