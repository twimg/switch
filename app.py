import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# --- 国別サッカー選手風顔写真セット ---
player_photos = {
    "日本": [
        "https://randomuser.me/api/portraits/men/40.jpg",
        "https://randomuser.me/api/portraits/men/41.jpg",
        "https://randomuser.me/api/portraits/men/42.jpg",
        "https://randomuser.me/api/portraits/men/43.jpg",
        "https://randomuser.me/api/portraits/men/44.jpg",
    ],
    "ブラジル": [
        "https://randomuser.me/api/portraits/men/82.jpg",
        "https://randomuser.me/api/portraits/men/83.jpg",
        "https://randomuser.me/api/portraits/men/84.jpg",
        "https://randomuser.me/api/portraits/men/85.jpg",
        "https://randomuser.me/api/portraits/men/86.jpg",
    ],
    "スペイン": [
        "https://randomuser.me/api/portraits/men/15.jpg",
        "https://randomuser.me/api/portraits/men/16.jpg",
        "https://randomuser.me/api/portraits/men/17.jpg",
        "https://randomuser.me/api/portraits/men/18.jpg",
        "https://randomuser.me/api/portraits/men/19.jpg",
    ],
    "フランス": [
        "https://randomuser.me/api/portraits/men/61.jpg",
        "https://randomuser.me/api/portraits/men/62.jpg",
        "https://randomuser.me/api/portraits/men/63.jpg",
        "https://randomuser.me/api/portraits/men/64.jpg",
        "https://randomuser.me/api/portraits/men/65.jpg",
    ],
    "イタリア": [
        "https://randomuser.me/api/portraits/men/36.jpg",
        "https://randomuser.me/api/portraits/men/37.jpg",
        "https://randomuser.me/api/portraits/men/38.jpg",
        "https://randomuser.me/api/portraits/men/39.jpg",
        "https://randomuser.me/api/portraits/men/47.jpg",
    ],
    "ドイツ": [
        "https://randomuser.me/api/portraits/men/51.jpg",
        "https://randomuser.me/api/portraits/men/52.jpg",
        "https://randomuser.me/api/portraits/men/53.jpg",
        "https://randomuser.me/api/portraits/men/54.jpg",
        "https://randomuser.me/api/portraits/men/55.jpg",
    ],
    "イングランド": [
        "https://randomuser.me/api/portraits/men/21.jpg",
        "https://randomuser.me/api/portraits/men/22.jpg",
        "https://randomuser.me/api/portraits/men/23.jpg",
        "https://randomuser.me/api/portraits/men/24.jpg",
        "https://randomuser.me/api/portraits/men/25.jpg",
    ],
}
photo_fallback = "https://randomuser.me/api/portraits/men/99.jpg"

def get_player_photo(nationality, name):
    urls = player_photos.get(nationality, None)
    if not urls: urls = list(player_photos.values())[0]
    idx = abs(hash(name)) % len(urls)
    return urls[idx] if urls else photo_fallback

# --- UIデザイン ---
st.markdown("""
    <style>
    html, body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
    .stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff; }
    .stTabs [data-baseweb="tab-list"] button { color: #fff !important; background: none !important; font-weight: 700;}
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #ffe45a !important; color: #ffe45a !important; }
    .player-card {
        background: #fff; color: #133469; border-radius: 15px;
        padding: 10px 10px 7px 10px; margin: 6px 8px 15px 8px;
        box-shadow: 0 0 13px #20b6ff33;
        min-width: 135px; max-width: 145px; font-size:0.98em;
        border: 2px solid #25b5ff20; position: relative; display:inline-block;
    }
    .player-card img {border-radius:50%;margin-bottom:6px;border:2px solid #3398d7;background:#fff;}
    .player-card.selected {border: 2.2px solid #f5e353; box-shadow: 0 0 14px #f5e35399;}
    .player-card:hover {background: #f8fcff; color: #1b54a4; box-shadow: 0 0 13px #1cefff55;}
    .detail-btn {background:#fff;color:#192841;border-radius:14px;padding:3px 13px;margin:6px 0 2px 0;border:2px solid #ffe45a;font-weight:bold;cursor:pointer;}
    .detail-btn:hover {background:#ffe45a;color:#1b243a;}
    .mobile-table {overflow-x:auto; white-space:nowrap;}
    .mobile-table th, .mobile-table td {
        padding: 4px 9px; font-size: 14px; border-bottom: 1.3px solid #1c2437;
    }
    .table-highlight th, .table-highlight td {
        background: #182649 !important; color: #ffe45a !important; border-bottom: 1.4px solid #24335d !important;
    }
    .pos-label { color: #fff; background: #1c243a; border-radius: 9px; padding: 2px 7px; font-size: 0.95em; }
    .budget-box {background:#fff6c2;color:#24345b;border-radius:12px;padding:7px 13px;display:inline-block;font-weight:700;margin:5px 0 10px 0;}
    .kickoff-btn {background:#fff;color:#1c233d;border:2px solid #ffe45a;border-radius:20px;font-size:1.09em;font-weight:bold;padding:5px 24px;margin:8px 0;}
    .kickoff-btn:hover {background:#ffe45a;color:#192841;}
    .save-btn, .scout-btn {background:#ffe45a;color:#1c233d;border:2px solid #fff6c2;border-radius:14px;font-weight:bold;padding:4px 18px;margin:4px 0;}
    </style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {
    'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense',
    'Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'
}
def ability_col(v):
    if v >= 90: return f"<span style='color:#20e660;font-weight:bold'>{v}</span>"
    if v >= 75: return f"<span style='color:#ffe600;font-weight:bold'>{v}</span>"
    return f"<span style='color:#1aacef'>{v}</span>"

# --- 名前生成（苗字＋名前／国籍ごと30程度） ---
name_pools = {
    "日本": (["佐藤","田中","鈴木","高橋","山本"],["翔","隼人","陽平","翼","凛"]),
    "ブラジル": (["シウバ","サントス","コスタ","ソウザ","ロペス"],["マテウス","パブロ","ルーカス","リカルド","ブルーノ"]),
    "スペイン": (["ガルシア","ロペス","マルティネス","ゴンザレス","サンチェス"],["アレハンドロ","パブロ","ダニエル","ミゲル","ルイス"]),
    "フランス": (["マルタン","ベルナール","プティ","ロベール","リシャール"],["ピエール","ジャン","トマ","レオン","アントワン"]),
    "イタリア": (["ロッシ","フェラーリ","マリーニ","ブルーノ","マンチーニ"],["ファビオ","マルコ","アレッサンドロ","ダニエレ","トーマス"]),
    "ドイツ": (["ミュラー","シュミット","シュナイダー","フィッシャー","ベッカー"],["クラウス","ティモ","ミヒャエル","ルーカス","マティアス"]),
    "イングランド": (["スミス","ジョンソン","ブラウン","ジョーンズ","ウィリアムズ"],["トーマス","ジェームズ","ウィリアム","ハリー","ジョージ"]),
}
def get_unique_name(nationality, used):
    surs, given = name_pools.get(nationality, (["Smith"],["Tom"]))
    for _ in range(100):
        name = f"{surs[random.randint(0,len(surs)-1)]} {given[random.randint(0,len(given)-1)]}"
        if name not in used: return name
    return f"{nationality}Player{random.randint(100,999)}"

PLAYER_TEAM = "ストライバーFC"
AI_CLUB_NAMES = ["ブルーウルブズ", "ファルコンズ", "レッドスターズ", "ヴォルティス", "ユナイテッドFC", "オーシャンズ", "タイガース", "スカイバード"]
TEAM_NUM = 8
AI_TEAMS = AI_CLUB_NAMES[:TEAM_NUM-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_TEAMS

if "current_round" not in st.session_state: st.session_state.current_round = 1
if "scout_list" not in st.session_state: st.session_state.scout_list = []
if "budget" not in st.session_state: st.session_state.budget = 1_000_000
if "team_points" not in st.session_state: st.session_state.team_points = {t: 0 for t in ALL_TEAMS}
if "match_log" not in st.session_state: st.session_state.match_log = []
if "移籍履歴" not in st.session_state: st.session_state["移籍履歴"] = []
if "sns_news" not in st.session_state: st.session_state["sns_news"] = []
if "ai_players" not in st.session_state:
    ai_players = []
    used_names = set()
    for t in AI_TEAMS:
        for i in range(20):
            nat = random.choice(list(name_pools.keys()))
            name = get_unique_name(nat, used_names)
            used_names.add(name)
            ai_players.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(19,32), "国籍": nat,
                "Spd": random.randint(60,85), "Pas": random.randint(60,85),
                "Phy": random.randint(60,85), "Sta": random.randint(60,85),
                "Def": random.randint(60,85), "Tec": random.randint(60,85),
                "Men": random.randint(60,85), "Sht": random.randint(60,85),
                "Pow": random.randint(60,85), "所属クラブ": t, "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

# --- データ読込 ---
df = pd.read_csv("players.csv")
col_map = {'スピード':'Spd','パス':'Pas','フィジカル':'Phy','スタミナ':'Sta',
    'ディフェンス':'Def','テクニック':'Tec','メンタル':'Men','シュート':'Sht','パワー':'Pow'}
df = df.rename(columns=col_map)
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000
df["総合"] = df[labels].mean(axis=1).astype(int)
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)
if "selected_player" not in st.session_state: st.session_state.selected_player = None

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
    st.markdown("#### Player Cards (横スクロール)")
    scroll_html = "<div style='white-space:nowrap;overflow-x:auto;'>"
    for idx, row in df_senior.iterrows():
        img_url = get_player_photo(row["国籍"], row["名前"])
        card_html = f"""
        <div class='player-card' style='display:inline-block;margin-right:15px;'>
            <img src="{img_url}" width="68">
            <b>{row['名前']}</b>
            <div class="pos-label">{row['ポジション']}</div>
            <br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}
            <br><span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{int(row['年俸'])}€</span>
            <form action='#'><button class='detail-btn' type='button' onclick="window.dispatchEvent(new CustomEvent('card_click_{idx}'));">詳細</button></form>
        </div>
        """
        scroll_html += card_html
    scroll_html += "</div>"
    st.markdown(scroll_html, unsafe_allow_html=True)

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
        st.markdown("#### Youth Player Cards (横スクロール)")
        scroll_html = "<div style='white-space:nowrap;overflow-x:auto;'>"
        for idx, row in df_youth.iterrows():
            img_url = get_player_photo(row["国籍"], row["名前"])
            card_html = f"""
            <div class='player-card' style='display:inline-block;margin-right:15px;'>
                <img src="{img_url}" width="68">
                <b>{row['名前']}</b>
                <div class="pos-label">{row['ポジション']}</div>
                <br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}
                <br><span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{int(row['年俸'])}€</span>
                <form action='#'><button class='detail-btn' type='button' onclick="window.dispatchEvent(new CustomEvent('card_click_y_{idx}'));">詳細</button></form>
            </div>
            """
            scroll_html += card_html
        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)

# --- Matchタブ ---
with tabs[2]:
    st.subheader("Match Simulation")
    round_idx = (st.session_state.current_round-1)%len(AI_TEAMS)
    enemy = AI_TEAMS[round_idx]
    st.write(f"今節: {PLAYER_TEAM} vs {enemy}")
    auto_starters = df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist()
    # ポジションごとの人数指定
    st.markdown("**スタメンを選択（ポジション別／11人）**")
    gks = [n for n in df_senior[df_senior["ポジション"]=="GK"]["名前"].tolist()]
    dfs = [n for n in df_senior[df_senior["ポジション"]=="DF"]["名前"].tolist()]
    mfs = [n for n in df_senior[df_senior["ポジション"]=="MF"]["名前"].tolist()]
    fws = [n for n in df_senior[df_senior["ポジション"]=="FW"]["名前"].tolist()]
    starters = []
    starters += st.multiselect("GK (1名)", gks, default=gks[:1], key="start_gk")
    starters += st.multiselect("DF (4名)", dfs, default=dfs[:4], key="start_df")
    starters += st.multiselect("MF (4名)", mfs, default=mfs[:4], key="start_mf")
    starters += st.multiselect("FW (2名)", fws, default=fws[:2], key="start_fw")
    starters = [s for s in starters if s in df_senior["名前"].tolist()]
    st.markdown("---")
    if len(starters) != 11:
        st.warning("合計11名を選んでください（現在: {}名）".format(len(starters)))
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
        st.markdown(f"<div class='budget-box'>勝率予想: <b>{int(pwin*100)}%</b></div>", unsafe_allow_html=True)
        if st.button("Kickoff!", key=f"kick_{datetime.now().isoformat()}_{random.random()}", help="試合開始", use_container_width=True):
            seed_val = random.randint(1,1_000_000)
            np.random.seed(seed_val)
            random.seed(seed_val)
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
    st.markdown(f"<div class='budget-box'>Budget: <b>{int(st.session_state.budget)}€</b></div>", unsafe_allow_html=True)
    if st.button("Refresh List", key="refresh", help="スカウト候補を更新", use_container_width=True):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_list = []
        for _ in range(5):
            nat = random.choice(list(name_pools.keys()))
            name = get_unique_name(nat, used_names)
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
    if st.session_state.scout_list:
        scroll_html = "<div style='white-space:nowrap;overflow-x:auto;'>"
        already = set(df["名前"].tolist())
        for idx, player in enumerate(st.session_state.scout_list):
            avatar_url = get_player_photo(player["国籍"], player["名前"])
            ovr = int(np.mean([player[l] for l in labels]))
            card_html = f"""
            <div class='player-card' style='display:inline-block;margin-right:15px;'>
                <img src="{avatar_url}" width="64">
                <b>{player['名前']}</b>
                <div class="pos-label">{player['ポジション']}</div>
                <br>OVR:{ovr} / {player['年齢']} / {player['国籍']}
                <br><span style='font-size:0.92em'>契約:{player['契約年数']}｜年俸:{int(player['年俸'])}€</span>
            """
            if player["名前"] not in already:
                card_html += f"""<form action='#'><button class='scout-btn' type='submit'>加入</button></form>"""
            else:
                card_html += "<span style='color:#aaa'>既に在籍</span>"
            card_html += "</div>"
            scroll_html += card_html
        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)

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
    if st.button("Save (players.csv)", key="save_btn", help="選手データ保存", use_container_width=True):
        df.to_csv("players.csv", index=False)
        st.success("Saved! (players.csv)")
    if st.button("Save AI Players List", key="save_ai_btn", help="AIデータ保存", use_container_width=True):
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

st.caption("UI/選手写真/国籍/横スクロール/詳細/ボタン色修正版（2025-07 最新）")
