import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --------- 設定 ---------
PLAYER_TEAM = "ストライバーFC"
labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
positions = ['GK','DF','MF','FW']
n_teams = 8
AI_CLUBS = ["ブルーウルブズ","ファルコンズ","レッドスターズ","ヴォルティス","ユナイテッドFC","オーシャンズ","タイガース","スカイバード"][:n_teams-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_CLUBS

# --------- 国籍→人種APIマッピング ---------
def player_img(nat, seed="1"):
    nat_map = {
        "日本":"asian", "イングランド":"male", "ドイツ":"male", "スペイン":"male", "イタリア":"male", "フランス":"male", "ブラジル":"male"
    }
    # nationalityごとに画像API（randomuser.me）で割り当て
    group = nat_map.get(nat, "male")
    return f"https://randomuser.me/api/portraits/{group}/{int(seed)%99}.jpg"

def format_money(val):
    if val >= 1_000_000_000:
        return f"{val//1_000_000_000}b€"
    elif val >= 1_000_000:
        return f"{val//1_000_000}m€"
    elif val >= 1_000:
        return f"{val//1_000}k€"
    return f"{int(val)}€"

# --------- データロード ---------
@st.cache_data
def load_players():
    df = pd.read_csv("players.csv")
    if "年俸" in df.columns:
        df["年俸表示"] = df["年俸"].apply(format_money)
    return df

def save_players(df):
    df.to_csv("players.csv", index=False)

# --------- セッション初期化 ---------
if "players" not in st.session_state:
    st.session_state.players = load_players()
if "youth" not in st.session_state:
    st.session_state.youth = st.session_state.players[st.session_state.players["年齢"] < 19].reset_index(drop=True)
if "senior" not in st.session_state:
    st.session_state.senior = st.session_state.players[st.session_state.players["年齢"] >= 19].reset_index(drop=True)
if "selected" not in st.session_state:
    st.session_state.selected = None
if "budget" not in st.session_state:
    st.session_state.budget = 1_000_000
if "scout_youth" not in st.session_state:
    st.session_state.scout_youth = []
if "scout_senior" not in st.session_state:
    st.session_state.scout_senior = []
if "auto_selected" not in st.session_state:
    st.session_state.auto_selected = []

# --------- CSS ---------
st.markdown("""
<style>
.stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff;}
.player-scroll {display:flex;overflow-x:auto;}
.player-card {background:#fff;color:#113269;border-radius:15px;padding:10px 14px;margin:9px 7px;min-width:160px;max-width:160px;box-shadow:0 0 8px #19cdf6cc;}
.player-card img{border-radius:50%;width:55px;height:55px;margin-bottom:5px;}
.detail-btn{background:#ffea3a;color:#182841;border:none;border-radius:12px;padding:3px 14px;font-weight:bold;margin:7px 0;}
.detail-btn:hover{background:#f2be21;color:#2a275b;}
.squad-btn{background:#fffde7;color:#1c2e4d;border-radius:11px;padding:5px 16px;font-weight:bold;}
.squad-btn:hover{background:#ffe800;color:#2a275b;}
.tabber .stTabs [data-baseweb="tab"] {color:#fff;}
.pos-label{background:#182841;color:#fff;padding:2px 15px;border-radius:9px;font-weight:bold;display:inline-block;}
.save-btn{background:#1caad7;color:#fff;border-radius:10px;padding:6px 18px;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# --------- メインUI ---------
st.title("Soccer Club Management Sim")
tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save", "SNS"])

# --- Seniorタブ ---
with tabs[0]:
    st.subheader("Senior Squad")
    df = st.session_state.senior
    st.markdown("<div class='player-scroll'>" +
        "".join([
            f"<div class='player-card'><img src='{player_img(row['国籍'], row['名前'])}' />"
            f"<b>{row['名前']}</b><div class='pos-label'>{row['ポジション']}</div>"
            f"<br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}<br>契約:{row['契約年数']} | 年俸:{format_money(row['年俸'])}"
            f"<br><button class='detail-btn' onclick='window.detail={idx}' >詳細</button>"
            f"</div>"
        for idx, row in df.iterrows()]) + "</div>", unsafe_allow_html=True)
    # 詳細ボタン(サンプル:本来はjs→st.session_state.selectedで)

# --- Youthタブ ---
with tabs[1]:
    st.subheader("Youth Squad")
    df = st.session_state.youth
    st.markdown("<div class='player-scroll'>" +
        "".join([
            f"<div class='player-card'><img src='{player_img(row['国籍'], row['名前'])}' />"
            f"<b>{row['名前']}</b><div class='pos-label'>{row['ポジション']}</div>"
            f"<br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}<br>契約:{row['契約年数']} | 年俸:{format_money(row['年俸'])}"
            f"<br><button class='detail-btn' onclick='window.detail={idx}' >詳細</button>"
            f"</div>"
        for idx, row in df.iterrows()]) + "</div>", unsafe_allow_html=True)

# --- Matchタブ ---
with tabs[2]:
    st.subheader("Match Simulation")
    st.markdown("##### [推奨]『オススメ編成』ボタンですぐ11人をセット可能")
    if st.button("オススメ編成", key="auto_sel", help="最適11人を自動選出"):
        df = st.session_state.senior.sort_values("総合", ascending=False)
        st.session_state.auto_selected = df.head(11)["名前"].tolist()
    names = st.session_state.senior["名前"].tolist()
    sel = st.multiselect("Starting XI", names, default=st.session_state.auto_selected, key="sel_starter")
    st.markdown("<div class='player-scroll'>" +
        "".join([
            f"<div class='player-card'><img src='{player_img(row['国籍'], row['名前'])}' />"
            f"<b>{row['名前']}</b><div class='pos-label'>{row['ポジション']}</div>"
            f"<br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}<br></div>"
        for _, row in st.session_state.senior[st.session_state.senior['名前'].isin(sel)].iterrows()
    ]) + "</div>", unsafe_allow_html=True)
    # ボタン色調整済

# --- Scoutタブ ---
with tabs[3]:
    st.subheader("Scout Candidates (Senior / Youth)")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("シニアスカウト更新", key="scout_senior", help="新しいシニア候補を表示", type="primary"):
            # ダミー生成（ランダム/国籍ごと）
            st.session_state.scout_senior = []
            for _ in range(5):
                nat = random.choice(list(["日本","イングランド","ドイツ","スペイン","フランス","イタリア","ブラジル"]))
                name = f"SC{random.randint(1000,9999)}"
                st.session_state.scout_senior.append({
                    "名前": name,
                    "ポジション": random.choice(positions),
                    "年齢": random.randint(20,30),
                    "国籍": nat,
                    "総合": random.randint(60,85),
                    "契約年数":2,
                    "年俸": random.randint(120_000,350_000)
                })
        st.markdown("<div class='player-scroll'>" +
            "".join([
                f"<div class='player-card'><img src='{player_img(x['国籍'], x['名前'])}' />"
                f"<b>{x['名前']}</b><div class='pos-label'>{x['ポジション']}</div>"
                f"<br>OVR:{x['総合']} / {x['年齢']} / {x['国籍']}<br>契約:{x['契約年数']} | 年俸:{format_money(x['年俸'])}"
                f"<br><button class='detail-btn'>加入</button></div>"
            for x in st.session_state.scout_senior]) + "</div>", unsafe_allow_html=True)
    with c2:
        if st.button("ユーススカウト更新", key="scout_youth", help="新しいユース候補を表示", type="primary"):
            st.session_state.scout_youth = []
            for _ in range(4):
                nat = random.choice(list(["日本","イングランド","ドイツ","スペイン","フランス","イタリア","ブラジル"]))
                name = f"YTH{random.randint(1000,9999)}"
                st.session_state.scout_youth.append({
                    "名前": name,
                    "ポジション": random.choice(positions),
                    "年齢": random.randint(15,18),
                    "国籍": nat,
                    "総合": random.randint(54,75),
                    "契約年数":2,
                    "年俸": random.randint(60_000,130_000)
                })
        st.markdown("<div class='player-scroll'>" +
            "".join([
                f"<div class='player-card'><img src='{player_img(x['国籍'], x['名前'])}' />"
                f"<b>{x['名前']}</b><div class='pos-label'>{x['ポジション']}</div>"
                f"<br>OVR:{x['総合']} / {x['年齢']} / {x['国籍']}<br>契約:{x['契約年数']} | 年俸:{format_money(x['年俸'])}"
                f"<br><button class='detail-btn'>加入</button></div>"
            for x in st.session_state.scout_youth]) + "</div>", unsafe_allow_html=True)

# --- Standingsタブ ---
with tabs[4]:
    st.subheader("League Standings")
    # サンプル表示
    tbl = [[t,random.randint(3,25),random.randint(5,60)] for t in ALL_TEAMS]
    dft = pd.DataFrame(tbl, columns=["Club","Pts","Goals"])
    dft["Rank"] = dft["Pts"].rank(ascending=False,method="min").astype(int)
    st.dataframe(dft.sort_values("Rank"))

# --- Saveタブ ---
with tabs[5]:
    st.subheader("データ保存")
    if st.button("Save All", type="primary"):
        save_players(st.session_state.players)
        st.success("保存完了")

# --- SNS ---
with tabs[6]:
    st.subheader("SNS")
    st.write("イベント履歴・トピック・移籍情報など")

st.caption("短縮統合版 v2025-07/サッカー選手写真・国籍/人種反映/横スクロール/全ボタン調整/オススメ編成/スカウト完全分離")
