import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# --- デザイン ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    html, body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
    .stApp { background: linear-gradient(120deg, #182a45 0%, #27345b 100%) !important; color: #eaf6ff; }
    .stTabs [data-baseweb="tab-list"] { color: #fff !important; }
    .stTabs [data-baseweb="tab"] { color: #fff !important; }
    .player-scroll { display: flex; flex-direction: row; gap: 18px; overflow-x: auto; padding: 0 4px 18px 0;}
    .player-card {
        min-width: 170px; max-width: 200px;
        background: #fff; color: #133469; border-radius: 15px;
        padding: 12px 10px 8px 10px; margin: 10px 2vw 15px 0;
        box-shadow: 0 0 13px #20b6ff33;
        display: flex; flex-direction: column; align-items: center;
        font-size:1.02em;
        border: 2px solid #25b5ff20; position: relative;
        transition: 0.14s;
    }
    .player-card img {border-radius:50%;margin-bottom:8px;border:2.3px solid #3398d7;background:#fff;width:68px;height:68px;object-fit:cover;}
    .player-card .pos-label {
        margin: 6px 0 2px 0; padding: 2px 15px; border-radius: 12px;
        background: #132651; color: #fff; font-weight: bold;
        font-size: 0.98em; display:inline-block;
    }
    .player-card .detail-btn {
        margin-top:9px; background:#fffdc4; color:#154a91; border:none;
        border-radius:12px; padding: 4px 16px; font-weight: bold; font-size:1em;
        cursor:pointer; box-shadow:0 0 5px #e2dfab66;
    }
    .player-card .detail-btn:active { background:#f3ef9e; }
    .budget-box {
        background: #fffad2; color:#183159; padding: 8px 22px; border-radius: 14px; font-weight:bold;
        display: inline-block; margin-bottom: 14px; font-size: 1.07em;
    }
    .save-btn, .refresh-btn {
        background: linear-gradient(90deg, #fbe57e 30%, #ffe78a 100%);
        color: #1c364f !important; border-radius: 16px !important;
        font-weight: bold; font-size: 1.09em !important;
        margin-top: 2px; margin-bottom: 12px;
        border: none !important; box-shadow: 0 0 7px #f6f4b755;
    }
    .stButton > button:active { background: #f6ea8c !important; }
    .mobile-table {overflow-x:auto; white-space:nowrap;}
    .mobile-table th, .mobile-table td {padding: 4px 9px; font-size: 14px;}
    .table-highlight th, .table-highlight td {background: #182649 !important; color: #ffe45a !important;}
    </style>
""", unsafe_allow_html=True)
st.title("Soccer Club Management Sim")

# --- 国籍別リアル顔割当 ---
def get_realistic_face(nationality, idx=0):
    nat_map = {
        "日本":    ("men", 50, 20),  # Asian画像API数が限られるため仮対応→"men"
        "イングランド": ("men", 99, 10),
        "ドイツ":     ("men", 99, 20),
        "スペイン":   ("men", 99, 30),
        "イタリア":   ("men", 99, 40),
        "フランス":   ("men", 99, 50),
        "ブラジル":   ("men", 99, 60)
    }
    group, n_max, offset = nat_map.get(nationality, ("men", 99, 0))
    num = (abs(hash(str(idx)+nationality)) % n_max) + offset
    # randomuser.me/api/portraits/men/1.jpg ～ /men/99.jpg (欧米系、番号被り無しに調整)
    return f"https://randomuser.me/api/portraits/{group}/{num}.jpg"

# --- 年俸フォーマット ---
def format_money(val):
    if val >= 1_000_000_000: return f"{val//1_000_000_000}b€"
    elif val >= 1_000_000: return f"{val//1_000_000}m€"
    elif val >= 1_000: return f"{val//1_000}k€"
    return f"{int(val)}€"

# --- 選手データ読み込み or 仮生成 ---
PLAYER_TEAM = "ストライバーFC"
labels = ['スピード','パス','フィジカル','スタミナ','ディフェンス','テクニック','メンタル','シュート','パワー']
try:
    df = pd.read_csv("players.csv")
except:
    # ダミーデータ自動生成
    df = pd.DataFrame([
        {"名前":f"木村 隼人","ポジション":"DF","年齢":27,"国籍":"日本","契約年数":2,"年俸":2_400_000,
         "スピード":67,"パス":67,"フィジカル":66,"スタミナ":65,"ディフェンス":68,"テクニック":61,"メンタル":67,"シュート":51,"パワー":63},
        {"名前":f"白石 翼","ポジション":"MF","年齢":23,"国籍":"日本","契約年数":1,"年俸":2_700_000,
         "スピード":71,"パス":70,"フィジカル":63,"スタミナ":66,"ディフェンス":57,"テクニック":75,"メンタル":65,"シュート":60,"パワー":62}
    ])
if "総合" not in df.columns:
    df["総合"] = df[labels].mean(axis=1).astype(int)
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000
df["所属クラブ"] = PLAYER_TEAM

# --- ユース分離 ---
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)

# --- Session State ---
if "selected_detail" not in st.session_state: st.session_state.selected_detail = None
if "budget" not in st.session_state: st.session_state.budget = 1_000_000
if "scout_list" not in st.session_state: st.session_state.scout_list = []
if "scout_list_youth" not in st.session_state: st.session_state.scout_list_youth = []
if "current_round" not in st.session_state: st.session_state.current_round = 1
if "team_points" not in st.session_state: st.session_state.team_points = {PLAYER_TEAM: 0}
if "match_log" not in st.session_state: st.session_state.match_log = []
if "移籍履歴" not in st.session_state: st.session_state["移籍履歴"] = []

# --- 横スクロール選手カード ---
def show_players(df, is_youth=False):
    # 横スクロールエリア
    st.markdown("<div class='player-scroll'>" +
        "".join([
            f"""
            <div class='player-card'>
                <img src='{get_realistic_face(row['国籍'], row['名前'])}'>
                <b>{row['名前']}</b>
                <div class='pos-label'>{row['ポジション']}</div>
                <br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}
                <br>契約:{row['契約年数']} | 年俸:{format_money(row['年俸'])}
                <form action="#" method="get">
                    <button class='detail-btn' name='det{row.name}_{'y' if is_youth else 's'}' type='submit'>詳細</button>
                </form>
            </div>
            """
            for _, row in df.iterrows()
        ]) + "</div>", unsafe_allow_html=True
    )

# --- 詳細クリック処理（仮:選手名をstate保存し再描画時に下部表示）---
if st.query_params:
    for k in st.query_params:
        if k.startswith("det"):
            idx, tag = k[3:].split("_")
            idx = int(idx)
            if tag == "y":
                st.session_state.selected_detail = ("youth", idx)
            else:
                st.session_state.selected_detail = ("senior", idx)
            st.experimental_set_query_params()  # クリア

# --- レーダーチャート ---
def show_radar(row):
    data = [row[l] for l in labels]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    data += data[:1]; angles += angles[:1]
    fig, ax = plt.subplots(figsize=(3.5,3), subplot_kw=dict(polar=True))
    ax.plot(angles, data, linewidth=2, marker='o')
    ax.fill(angles, data, alpha=0.27)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    ax.set_title(row["名前"], size=14)
    st.pyplot(fig)

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
    st.markdown("#### Players")
    show_players(df_senior, is_youth=False)
    # 詳細表示
    if st.session_state.selected_detail and st.session_state.selected_detail[0]=="senior":
        idx = st.session_state.selected_detail[1]
        if idx < len(df_senior):
            row = df_senior.iloc[idx]
            st.markdown(f"### {row['名前']}（{row['ポジション']}）詳細")
            st.write({l:row[l] for l in labels})
            show_radar(row)

# --- Youthタブ ---
with tabs[1]:
    st.subheader("Youth Squad")
    if len(df_youth) == 0:
        st.info("ユース選手はいません")
    else:
        main_cols = ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]
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
        st.markdown("#### Players")
        show_players(df_youth, is_youth=True)
        # 詳細表示
        if st.session_state.selected_detail and st.session_state.selected_detail[0]=="youth":
            idx = st.session_state.selected_detail[1]
            if idx < len(df_youth):
                row = df_youth.iloc[idx]
                st.markdown(f"### {row['名前']}（{row['ポジション']}）詳細")
                st.write({l:row[l] for l in labels})
                show_radar(row)

# --- Matchタブ ---
with tabs[2]:
    st.subheader("Match Simulation")
    # 自動編成 or 手動選択
    st.markdown("**おすすめ編成で自動選出**：")
    if st.button("おすすめ編成", key="auto_pick"):
        auto_starters = df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist()
        st.session_state["starters"] = auto_starters
    else:
        auto_starters = st.session_state.get("starters", df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist())
    starters = st.multiselect("Starting XI", df_senior["名前"].tolist(), default=auto_starters, key="starters")
    st.markdown("<span style='color:#fff;font-weight:bold;'>ポジション：GK/DF/MF/FW（手動で調整可）</span>", unsafe_allow_html=True)
    if len(starters) != 11:
        st.warning("11人ちょうど選んでください")
    else:
        tactics = st.selectbox("Tactics", ["Attack", "Balanced", "Defensive", "Counter", "Possession"])
        if st.button("Kickoff!", key=f"kick_{datetime.now().isoformat()}_{random.random()}"):
            team_strength = df_senior[df_senior["名前"].isin(starters)][labels].mean().mean() + random.uniform(-2, 2)
            ai_strength = 73 + random.uniform(-2, 2)
            pwin = (team_strength / (team_strength+ai_strength)) if (team_strength+ai_strength)>0 else 0.5
            st.markdown(f"<span style='color:#fff;font-size:1.1em;font-weight:bold;'>推定勝率：{int(pwin*100)}%</span>", unsafe_allow_html=True)
            my_goals = max(0, int(np.random.normal((team_strength-60)/8, 1.0)))
            op_goals = max(0, int(np.random.normal((ai_strength-60)/8, 1.0)))
            if my_goals > op_goals:
                result = "Win"
                st.session_state.team_points[PLAYER_TEAM] += 3
            elif my_goals < op_goals:
                result = "Lose"
            else:
                result = "Draw"
                st.session_state.team_points[PLAYER_TEAM] += 1
            st.success(f"{result}! {my_goals}-{op_goals}")
            st.session_state.match_log.append(f"Match: {result}! {my_goals}-{op_goals}")
    st.markdown("#### 最近の試合ログ")
    for l in st.session_state.match_log[-5:][::-1]:
        st.write(l)

# --- Scoutタブ（シニア・ユース） ---
with tabs[3]:
    st.subheader("Scout Candidates")
    st.markdown(f"<span class='budget-box'>Budget: {format_money(st.session_state.budget)}</span>", unsafe_allow_html=True)
    if st.button("Refresh List", key="refresh_scout", help="新しいシニアスカウト候補を生成", type="primary"):
        st.session_state.scout_list = []
        for i in range(5):
            nationality = random.choice(["日本","ブラジル","スペイン","フランス","イタリア","ドイツ","イングランド"])
            name = f"スカウト{i+1} {nationality}"
            st.session_state.scout_list.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(20, 28), "国籍": nationality,
                "契約年数": 2, "年俸": random.randint(110_000,200_000),
                "総合": random.randint(64,80)
            })
    # --- シニアスカウト ---
    st.markdown("##### シニア候補")
    show_players(pd.DataFrame(st.session_state.scout_list), is_youth=False)
    # --- ユーススカウト ---
    st.markdown("##### ユース候補")
    if st.button("ユースRefresh", key="refresh_scout_youth", help="新しいユーススカウト候補を生成", type="primary"):
        st.session_state.scout_list_youth = []
        for i in range(4):
            nationality = random.choice(["日本","ブラジル","スペイン","フランス","イタリア","ドイツ","イングランド"])
            name = f"ユーススカウト{i+1} {nationality}"
            st.session_state.scout_list_youth.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(14, 18), "国籍": nationality,
                "契約年数": 2, "年俸": random.randint(80_000,140_000),
                "総合": random.randint(59,75)
            })
    show_players(pd.DataFrame(st.session_state.scout_list_youth), is_youth=True)

# --- Standings ---
with tabs[4]:
    st.subheader("League Standings")
    tbl = [[PLAYER_TEAM, st.session_state.team_points[PLAYER_TEAM], df_senior["得点"].sum()]]
    dft = pd.DataFrame(tbl, columns=["Club","Pts","Goals"])
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

# --- Save ---
with tabs[5]:
    st.subheader("Data Save")
    if st.button("Save (players.csv)", key="save_btn", help="選手データを保存", type="primary"):
        df.to_csv("players.csv", index=False)
        st.success("Saved! (players.csv)")

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

st.caption("2025年最新版：国籍別リアル顔＋横スクロール＋編成補助＋全機能一体統合・エラー防止")
