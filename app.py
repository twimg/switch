import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# --- UI/CSS ---
st.set_page_config(page_title="Soccer Club Management", layout="wide")
st.markdown("""
<style>
html, body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
.stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff; }
.player-card-row {display: flex; flex-direction: row; overflow-x: auto; white-space: nowrap; padding-bottom: 10px;}
.player-card {flex: 0 0 175px; margin-right: 20px; background: #fff; color: #133469;
    border-radius: 15px; box-shadow: 0 0 13px #20b6ff33; padding: 13px 10px 9px 10px;
    font-size:1.02em; position: relative;}
.player-card img {border-radius:50%;margin-bottom:10px;border:2px solid #3398d7;background:#fff;}
.player-card.selected {border: 2.7px solid #f5e353; box-shadow: 0 0 16px #f5e35399;}
.player-card:hover {background: #f8fcff; color: #1b54a4; transform: scale(1.03);
    box-shadow: 0 0 13px #1cefff55; border:2px solid #42d8ff;}
.detail-btn {margin-top: 6px; margin-bottom: 2px; background: #2348b4; color: #fff; border: none;
    border-radius: 11px; font-size: 1.01em; padding: 4px 15px;}
.detail-btn:hover {background: #ffe45a; color: #162a58;}
.player-detail-popup {position:absolute; top:14px; left:180px; min-width:230px; max-width:300px;
    z-index:11; background: #202c49; color:#ffe; border-radius:13px; padding:15px 15px;
    box-shadow:0 0 19px #132038c8; border:2.5px solid #1698d488;}
.budget-box {background: #f7e770; color: #202c49; font-weight:bold; border-radius:11px;
    display:inline-block; padding:6px 22px; margin-bottom: 6px; font-size: 1.1em;}
.match-pos-label {color: #fff !important; background: #314a90; padding: 2px 8px; border-radius: 7px; font-weight: bold;}
.stButton>button, .save-btn, .refresh-btn {
    background: linear-gradient(90deg,#3185ff 0%,#ffe45a 100%);
    color: #181d26 !important; border-radius: 13px !important; font-weight: bold;
    font-size: 1.08em !important; box-shadow: 0 0 5px #2fefff88;
    margin-top: 7px; margin-bottom: 8px; border: none !important;
    transition: 0.14s;}
.stButton>button:hover, .save-btn:hover, .refresh-btn:hover {
    background: linear-gradient(90deg,#ffe45a 0%,#3185ff 100%);
    color: #2348b4 !important;}
.stTabs [data-baseweb="tab-list"] { color: #fff !important; }
.stTabs [data-baseweb="tab"]:not([aria-selected="true"]) { color: #fff !important;}
.stTabs [aria-selected="true"] { color: #ffe45a !important; }
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- 国籍リスト・名前辞書 ---
NATIONS = ["日本","ブラジル","スペイン","フランス","イタリア","ドイツ","イングランド"]
surname_pool = {
    "日本":["佐藤","鈴木","高橋","田中","伊藤","渡辺","山本","中村","小林","加藤","吉田","山田","佐々木","山口","松本","井上","木村","林","斎藤","清水","山崎","池田","阿部","森","橋本","石川","前田","藤田","後藤","長谷川"],
    "ブラジル":["シウバ","サントス","コスタ","リマ","ゴメス","マルチンス","ペレイラ","ロペス","アウベス","メンドンサ","カルドーゾ","カブラル","ピント","バルボーザ","ラモス","サラザール","テイシェイラ","ドスサントス"],
    "スペイン":["ガルシア","ロペス","マルティネス","ゴンザレス","ロドリゲス","フェルナンデス","サンチェス","ペレス","ゴメス","ヒメネス","ルイス","ディアス","アルバレス","ナバロ","ドミンゲス","ベガ"],
    "フランス":["マルタン","ベルナール","デュラン","プティ","ロベール","リシャール","ガルシア","ルイ","ルフェーブル","モロー","ルルー","アンドレ","ルジェ","ジョリー","フィリップ"],
    "イタリア":["ロッシ","ルッソ","フェラーリ","エスポジト","ビアンキ","ロマーノ","コロンボ","リッチ","マリーニ","ブルーノ","ガッリ","モレッティ","バルディーニ","マルティーニ"],
    "ドイツ":["ミュラー","シュミット","シュナイダー","フィッシャー","ヴェーバー","マイヤー","ヴァーグナー","ベッカー","ホフマン","シュルツ","ケラー","リヒター","バウアー"],
    "イングランド":["スミス","ジョンソン","ウィリアムズ","ブラウン","ジョーンズ","ミラー","デイビス","テイラー","クラーク","ホワイト","ハリス","マーチン","ロビンソン"]
}
given_pool = {
    "日本":["翔","隼人","陸","陽平","悠真","悠人","啓太","海斗","翼","隆成","凛","優","颯太","匠","拓真","蓮","大輝","光","大和","慎吾"],
    "ブラジル":["マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ","ブルーノ","レアンドロ"],
    "スペイン":["アレハンドロ","パブロ","ダニエル","ミゲル","アドリアン","ハビエル","イバン","ルイス","マヌエル","ディエゴ","アルバロ"],
    "フランス":["ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","ミカエル"],
    "イタリア":["ファビオ","マルコ","アレッサンドロ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","ルイジ","パオロ"],
    "ドイツ":["クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","ダニエル"],
    "イングランド":["トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー"]
}

def random_name(nation, used_names=set()):
    for _ in range(30):
        surname = random.choice(surname_pool[nation])
        given = random.choice(given_pool[nation])
        if nation=="日本":
            name = f"{surname} {given}"
        else:
            name = f"{given} {surname}"
        if name not in used_names:
            return name
    # Fallback
    return name

# --- 顔画像生成（国籍ごとに違う写真感・人種感でDiceBear APIを再現/簡易実装） ---
def get_player_avatar_url(name, nation):
    # 別のスタイルも含め自動で国籍と合わせて切り替え
    base = "notionists" if nation == "日本" else "adventurer" if nation=="ブラジル" else "micah" if nation=="イングランド" else "avataaars"
    seed = name.replace(" ","_")
    # 男性のみ指定・国籍によるパターン変化
    style = f"https://api.dicebear.com/7.x/{base}/png?seed={seed}&gender=male"
    return style

def ability_col(v):
    if v >= 90: return f"<span style='color:#20e660;font-weight:bold'>{v}</span>"
    if v >= 75: return f"<span style='color:#ffe600;font-weight:bold'>{v}</span>"
    return f"<span style='color:#1aacef'>{v}</span>"

def format_money(euro):
    if euro >= 1_000_000_000:
        return f"{euro/1_000_000_000:.2f}b€"
    elif euro >= 1_000_000:
        return f"{euro/1_000_000:.2f}m€"
    elif euro >= 1_000:
        return f"{euro/1_000:.1f}k€"
    return f"{int(euro)}€"

# --- AIクラブ ---
PLAYER_TEAM = "ストライバーFC"
AI_CLUB_NAMES = ["ブルーウルブズ", "ファルコンズ", "レッドスターズ", "ヴォルティス", "ユナイテッドFC", "オーシャンズ", "タイガース", "スカイバード"]
TEAM_NUM = 8
AI_TEAMS = AI_CLUB_NAMES[:TEAM_NUM-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_TEAMS

# --- セッション初期化 ---
if "current_round" not in st.session_state: st.session_state.current_round = 1
if "scout_list" not in st.session_state: st.session_state.scout_list = []
if "scout_youth_list" not in st.session_state: st.session_state.scout_youth_list = []
if "budget" not in st.session_state: st.session_state.budget = 1_000_000
if "team_points" not in st.session_state: st.session_state.team_points = {t: 0 for t in ALL_TEAMS}
if "match_log" not in st.session_state: st.session_state.match_log = []
if "移籍履歴" not in st.session_state: st.session_state["移籍履歴"] = []
if "ai_players" not in st.session_state:
    ai_players = []
    used_names = set()
    for t in AI_TEAMS:
        for i in range(20):
            nation = random.choice(NATIONS)
            name = random_name(nation, used_names)
            used_names.add(name)
            ai_players.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(19,32), "国籍": nation,
                "Spd": random.randint(60,85), "Pas": random.randint(60,85),
                "Phy": random.randint(60,85), "Sta": random.randint(60,85),
                "Def": random.randint(60,85), "Tec": random.randint(60,85),
                "Men": random.randint(60,85), "Sht": random.randint(60,85),
                "Pow": random.randint(60,85), "所属クラブ": t, "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {
    'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense',
    'Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'
}

# --- データ読込 ---
try:
    df = pd.read_csv("players.csv")
except:
    # サンプル初期データ
    rows = []
    used_names = set()
    for i in range(20):
        nat = random.choice(NATIONS)
        name = random_name(nat, used_names)
        used_names.add(name)
        row = {"名前":name, "ポジション":random.choice(["GK","DF","MF","FW"]),
               "年齢":random.randint(19,34), "国籍":nat,
               "Spd":random.randint(65,88),"Pas":random.randint(65,88),"Phy":random.randint(65,88),"Sta":random.randint(65,88),
               "Def":random.randint(65,88),"Tec":random.randint(65,88),"Men":random.randint(65,88),"Sht":random.randint(65,88),
               "Pow":random.randint(65,88), "契約年数":2, "年俸":random.randint(100_000,200_000), "得点":0, "出場数":0, "所属クラブ":PLAYER_TEAM}
        rows.append(row)
    df = pd.DataFrame(rows)
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000
df["総合"] = df[labels].mean(axis=1).astype(int)
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)
if "selected_player_idx" not in st.session_state: st.session_state.selected_player_idx = None
if "selected_player_tab" not in st.session_state: st.session_state.selected_player_tab = "senior"

# --- タブ ---
tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save", "SNS"])

# --- Seniorタブ ---
with tabs[0]:
    st.subheader("Senior Squad")
    main_cols = ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]
    st.markdown(
        "<div class='mobile-table'><table><thead><tr>" +
        "".join([f"<th>{col}</th>" for col in main_cols]) +
        "</tr></thead><tbody>" +
        "".join([
            "<tr>" + "".join([f"<td>{row[col]}</td>" for col in main_cols]) + "</tr>"
            for _, row in df_senior.iterrows()
        ]) +
        "</tbody></table></div>", unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("#### Player Cards")
    st.markdown("<div class='player-card-row'>", unsafe_allow_html=True)
    for idx, row in df_senior.iterrows():
        avatar_url = get_player_avatar_url(row["名前"], row["国籍"])
        is_sel = st.session_state.selected_player_idx == idx and st.session_state.selected_player_tab=="senior"
        card_html = f"""
        <div class="player-card{' selected' if is_sel else ''}">
            <img src="{avatar_url}" width="64">
            <b>{row['名前']}</b><br>
            <span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span><br>
            <span class='match-pos-label'>{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}<br>
            <span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span><br>
        </div>
        """
        st.markdown(
            card_html +
            (f"""<button class="detail-btn" onclick="window.location.href='#{idx}_senior'">詳細</button>""" if not is_sel else ""),
            unsafe_allow_html=True
        )
        if st.button("詳細", key=f"senior_detail_{idx}"):
            st.session_state.selected_player_idx = idx
            st.session_state.selected_player_tab = "senior"
    st.markdown("</div>", unsafe_allow_html=True)
    # 詳細ポップアップ
    if st.session_state.selected_player_tab=="senior" and st.session_state.selected_player_idx is not None:
        row = df_senior.iloc[st.session_state.selected_player_idx]
        avatar_url = get_player_avatar_url(row["名前"], row["国籍"])
        st.markdown(f"<div class='player-detail-popup'><img src='{avatar_url}' width='70'><br><b>{row['名前']}</b><br>{row['国籍']} / {row['ポジション']}<br>年齢:{row['年齢']}<br>契約:{row['契約年数']}年｜年俸:{format_money(row['年俸'])}<hr style='border-color:#ffe45a'>", unsafe_allow_html=True)
        stats = [float(row[l]) for l in labels] + [float(row[labels[0]])]
        angles = np.linspace(0, 2 * np.pi, len(labels)+1)
        fig, ax = plt.subplots(figsize=(2.4,2.4), subplot_kw=dict(polar=True))
        ax.plot(angles, stats, color="#1c53d6", linewidth=2)
        ax.fill(angles, stats, color="#87d4ff", alpha=0.21)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=9, color='#ffe45a')
        ax.set_yticklabels([])
        fig.patch.set_alpha(0.0)
        st.pyplot(fig, transparent=True)
        ab_table = "<table>"
        for l in labels:
            v = int(row[l])
            ab_table += f"<tr><td style='color:#b7e2ff;font-weight:bold'>{l}</td><td>{ability_col(v)}</td><td style='color:#bbb;font-size:0.92em'>{labels_full[l]}</td></tr>"
        ab_table += "</table>"
        st.markdown(ab_table, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- Youthタブ ---
with tabs[1]:
    st.subheader("Youth Players")
    main_cols = ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]
    if len(df_youth) == 0:
        st.info("ユース選手はいません")
    else:
        st.markdown(
            "<div class='mobile-table'><table><thead><tr>" +
            "".join([f"<th>{col}</th>" for col in main_cols]) +
            "</tr></thead><tbody>" +
            "".join([
                "<tr>" + "".join([f"<td>{row[col]}</td>" for col in main_cols]) + "</tr>"
                for _, row in df_youth.iterrows()
            ]) +
            "</tbody></table></div>", unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown("#### Youth Player Cards")
        st.markdown("<div class='player-card-row'>", unsafe_allow_html=True)
        for idx, row in df_youth.iterrows():
            avatar_url = get_player_avatar_url(row["名前"], row["国籍"])
            is_sel = st.session_state.selected_player_idx == idx and st.session_state.selected_player_tab=="youth"
            card_html = f"""
            <div class="player-card{' selected' if is_sel else ''}">
                <img src="{avatar_url}" width="64">
                <b>{row['名前']}</b><br>
                <span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span><br>
                <span class='match-pos-label'>{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}<br>
                <span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span><br>
            </div>
            """
            st.markdown(
                card_html +
                (f"""<button class="detail-btn" onclick="window.location.href='#{idx}_youth'">詳細</button>""" if not is_sel else ""),
                unsafe_allow_html=True
            )
            if st.button("詳細", key=f"youth_detail_{idx}"):
                st.session_state.selected_player_idx = idx
                st.session_state.selected_player_tab = "youth"
        st.markdown("</div>", unsafe_allow_html=True)
        if st.session_state.selected_player_tab=="youth" and st.session_state.selected_player_idx is not None:
            row = df_youth.iloc[st.session_state.selected_player_idx]
            avatar_url = get_player_avatar_url(row["名前"], row["国籍"])
            st.markdown(f"<div class='player-detail-popup'><img src='{avatar_url}' width='70'><br><b>{row['名前']}</b><br>{row['国籍']} / {row['ポジション']}<br>年齢:{row['年齢']}<br>契約:{row['契約年数']}年｜年俸:{format_money(row['年俸'])}<hr style='border-color:#ffe45a'>", unsafe_allow_html=True)
            stats = [float(row[l]) for l in labels] + [float(row[labels[0]])]
            angles = np.linspace(0, 2 * np.pi, len(labels)+1)
            fig, ax = plt.subplots(figsize=(2.4,2.4), subplot_kw=dict(polar=True))
            ax.plot(angles, stats, color="#1c53d6", linewidth=2)
            ax.fill(angles, stats, color="#87d4ff", alpha=0.21)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=9, color='#ffe45a')
            ax.set_yticklabels([])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, transparent=True)
            ab_table = "<table>"
            for l in labels:
                v = int(row[l])
                ab_table += f"<tr><td style='color:#b7e2ff;font-weight:bold'>{l}</td><td>{ability_col(v)}</td><td style='color:#bbb;font-size:0.92em'>{labels_full[l]}</td></tr>"
            ab_table += "</table>"
            st.markdown(ab_table, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- Matchタブ ---
with tabs[2]:
    st.subheader("Match Simulation")
    st.markdown(f"<span class='budget-box'>Budget: {format_money(st.session_state.budget)}</span>", unsafe_allow_html=True)
    round_idx = (st.session_state.current_round-1)%len(AI_TEAMS)
    enemy = AI_TEAMS[round_idx]
    st.write(f"今節: {PLAYER_TEAM} vs {enemy}")
    auto_starters = df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist()
    pos_options = ["GK","DF","MF","FW"]
    pos_select = {}
    st.markdown("**ポジション（白文字表示）を選択:**")
    cols = st.columns(11)
    for i, name in enumerate(auto_starters):
        pos = st.selectbox(f"{name}", pos_options, key=f"match_pos_{i}")
        pos_select[name] = pos
        st.markdown(f"<span class='match-pos-label'>{pos}</span>", unsafe_allow_html=True)
    starters = auto_starters
    tactics = st.selectbox("Tactics", ["Attack", "Balanced", "Defensive", "Counter", "Possession"])
    if st.button("Kickoff!", key=f"kick_{datetime.now().isoformat()}_{random.random()}"):
        seed_val = random.randint(1,1_000_000)
        np.random.seed(seed_val)
        random.seed(seed_val)
        team_strength = df_senior[df_senior["名前"].isin(starters)][labels].mean().mean() + random.uniform(-2, 2)
        ai_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==enemy]
        ai_strength = ai_df[labels].mean().mean() + random.uniform(-2, 2)
        if tactics=="Attack": team_strength *= 1.08
        elif tactics=="Defensive": team_strength *= 0.93
        elif tactics=="Counter": team_strength *= 1.04
        elif tactics=="Possession": team_strength *= 1.03
        pwin = (team_strength / (team_strength+ai_strength)) if (team_strength+ai_strength)>0 else 0.5
        fig, ax = plt.subplots(figsize=(4,1.3))
        ax.bar(["You","AI"], [team_strength, ai_strength], color=["#22e","#ccc"])
        ax.set_xticks([0,1]); ax.set_ylabel("平均能力")
        ax.set_title(f"チーム力比較（推定勝率: {int(100*pwin)}%）", color="#f4f8fc")
        fig.patch.set_alpha(0)
        st.pyplot(fig, transparent=True)
        my_goals = max(0, int(np.random.normal((team_strength-60)/8, 1.0)))
        op_goals = max(0, int(np.random.normal((ai_strength-60)/8, 1.0)))
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
        scorer = random.choice(starters) if my_goals > 0 else "なし"
        ai_scorer = random.choice(ai_df["名前"].tolist()) if op_goals > 0 else "なし"
        st.success(f"{result}! {my_goals}-{op_goals}")
        st.info(f"得点者: {scorer} / 相手: {ai_scorer}")
        st.session_state.current_round += 1
        st.session_state.match_log.append(f"Round {st.session_state.current_round-1}: {PLAYER_TEAM} vs {enemy}: {my_goals}-{op_goals}, 得点: {scorer}")

    st.markdown("#### 最近の試合ログ")
    for l in st.session_state.match_log[-5:][::-1]:
        st.write(l)

# --- Scout ---
with tabs[3]:
    st.subheader("Scout Candidates")
    st.markdown(f"<span class='budget-box'>Budget: {format_money(st.session_state.budget)}</span>", unsafe_allow_html=True)
    if st.button("Refresh List", key="refresh_scout", help="新しいスカウト候補を生成", args=(), kwargs={}, type="primary"):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_list = []
        for _ in range(5):
            nat = random.choice(NATIONS)
            name = random_name(nat, used_names)
            used_names.add(name)
            st.session_state.scout_list.append({
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(19, 29),
                "国籍": nat,
                "Spd": random.randint(60, 80),
                "Pas": random.randint(60, 80),
                "Phy": random.randint(60, 80),
                "Sta": random.randint(60, 80),
                "Def": random.randint(60, 80),
                "Tec": random.randint(60, 80),
                "Men": random.randint(60, 80),
                "Sht": random.randint(60, 80),
                "Pow": random.randint(60, 80),
                "契約年数": 2,
                "年俸": random.randint(100_000,180_000),
                "得点": 0,
                "出場数": 0,
                "所属クラブ": PLAYER_TEAM
            })
    if st.button("Refresh Youth List", key="refresh_scout_youth", help="新しいユース候補", args=(), kwargs={}, type="primary"):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_youth_list = []
        for _ in range(3):
            nat = random.choice(NATIONS)
            name = random_name(nat, used_names)
            used_names.add(name)
            st.session_state.scout_youth_list.append({
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(14, 18),
                "国籍": nat,
                "Spd": random.randint(60, 80),
                "Pas": random.randint(60, 80),
                "Phy": random.randint(60, 80),
                "Sta": random.randint(60, 80),
                "Def": random.randint(60, 80),
                "Tec": random.randint(60, 80),
                "Men": random.randint(60, 80),
                "Sht": random.randint(60, 80),
                "Pow": random.randint(60, 80),
                "契約年数": 2,
                "年俸": random.randint(60_000,120_000),
                "得点": 0,
                "出場数": 0,
                "所属クラブ": PLAYER_TEAM
            })
    cols = st.columns(3)
    already = set(df["名前"].tolist())
    for idx, player in enumerate(st.session_state.scout_list):
        with cols[idx%3]:
            ovr = int(np.mean([player[l] for l in labels]))
            avatar_url = get_player_avatar_url(player["名前"], player["国籍"])
            st.markdown(
                f"<div class='player-card'><img src='{avatar_url}' width='48'><b>{player['名前']}</b> <span style='color:#2cabe8;'>(OVR:{ovr})</span><br>"
                f"<span class='match-pos-label'>{player['ポジション']}</span> / {player['年齢']} / {player['国籍']}<br>"
                f"契約:{player['契約年数']}年｜年俸:{format_money(player['年俸'])}</div>", 
                unsafe_allow_html=True)
            if player["名前"] not in already:
                if st.button("加入", key=f"scout_{idx}"):
                    df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                    df.to_csv("players.csv", index=False)
                    st.session_state.budget -= player['年俸']
                    st.success(f"{player['名前']} signed!")
                    st.session_state["移籍履歴"].append(f"{player['名前']}（{player['国籍']}）をスカウトで獲得！")
            else:
                st.markdown("🟦<span style='color:#888'>既に在籍</span>", unsafe_allow_html=True)
    # Youth
    st.markdown("### Youth Scout Candidates")
    for idx, player in enumerate(st.session_state.scout_youth_list):
        with cols[idx%3]:
            ovr = int(np.mean([player[l] for l in labels]))
            avatar_url = get_player_avatar_url(player["名前"], player["国籍"])
            st.markdown(
                f"<div class='player-card'><img src='{avatar_url}' width='48'><b>{player['名前']}</b> <span style='color:#2cabe8;'>(OVR:{ovr})</span><br>"
                f"<span class='match-pos-label'>{player['ポジション']}</span> / {player['年齢']} / {player['国籍']}<br>"
                f"契約:{player['契約年数']}年｜年俸:{format_money(player['年俸'])}</div>", 
                unsafe_allow_html=True)
            if player["名前"] not in already:
                if st.button("ユース加入", key=f"scout_youth_{idx}"):
                    df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                    df.to_csv("players.csv", index=False)
                    st.session_state.budget -= player['年俸']
                    st.success(f"{player['名前']} signed!")
                    st.session_state["移籍履歴"].append(f"{player['名前']}（{player['国籍']}）をユースで獲得！")
            else:
                st.markdown("🟦<span style='color:#888'>既に在籍</span>", unsafe_allow_html=True)

# --- Standings ---
with tabs[4]:
    st.subheader("League Standings")
    tbl = []
    for t in ALL_TEAMS:
        total_goals = 0
        if t == PLAYER_TEAM:
            total_goals = df_senior["得点"].sum()
        else:
            ai_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==t]
            total_goals = ai_df["得点"].sum() if "得点" in ai_df.columns else 0
        pts = st.session_state.team_points.get(t,0)
        tbl.append([t, pts, total_goals])
    dft = pd.DataFrame(tbl, columns=["Club","Pts","Goals"])
    dft = dft.sort_values(["Pts","Goals"], ascending=[False,False]).reset_index(drop=True)
    dft["Rank"] = dft.index + 1
    dft = dft[["Rank","Club","Pts","Goals"]]
    st.markdown(
        "<div class='mobile-table table-highlight'><table><thead><tr>" +
        "".join([f"<th>{col}</th>" for col in dft.columns]) +
        "</tr></thead><tbody>" +
        "".join([
            "<tr>" + "".join([f"<td>{row[col]}</td>" for col in dft.columns]) + "</tr>"
            for _, row in dft.iterrows()
        ]) +
        "</tbody></table></div>", unsafe_allow_html=True
    )
    if st.session_state.match_log:
        st.markdown("**Recent Matches**")
        for l in st.session_state.match_log[-5:][::-1]:
            st.text(l)

# --- Save ---
with tabs[5]:
    st.subheader("Data Save")
    if st.button("Save (players.csv)", key="save_btn"):
        df.to_csv("players.csv", index=False)
        st.success("Saved! (players.csv)")
    if st.button("Save AI Players List", key="save_ai_btn"):
        st.session_state.ai_players.to_csv("ai_players.csv", index=False)
        st.success("AI Players list saved.")

# --- SNS ---
with tabs[6]:
    st.subheader("SNS / Event Feed")
    if st.session_state["移籍履歴"]:
        st.write("### Recent Transfers")
        for news in st.session_state["移籍履歴"][-5:][::-1]:
            st.info(news)
    if st.session_state.match_log:
        st.write("### Recent Matches")
        for l in st.session_state.match_log[-5:][::-1]:
            st.write(l)

st.caption("横スクロールカード・詳細・国籍顔・ユース/スカウト/セーブ/白文字ポジション・予算枠・全統合最新版")
