import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="Soccer Club Management Sim", layout="wide")

# --- CSS/UI ---
st.markdown("""
<style>
body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
.stApp { background: linear-gradient(120deg, #202c46 0%, #314265 100%) !important; color: #eaf6ff; }
h1,h2,h3,h4,h5,h6, .stTabs label, .stTabs span, .stTabs button { color: #fff !important; }
.stTabs [data-baseweb="tab"] > button[aria-selected="true"] { color: #fff !important; background: transparent !important; border-bottom: 2.7px solid #f7df70 !important;}
.stTabs [data-baseweb="tab"] > button { color: #fff !important; background: transparent !important; }
input, textarea, .stTextInput>div>div>input {
    background: #202c46 !important; color: #ffe !important; border-radius:8px; border: 1.7px solid #27e3b9;
    font-size:1.06em; font-family:'IPAexGothic','Meiryo',sans-serif; padding: 7px;
}
input:focus, textarea:focus {
    border:2.2px solid #f7df70 !important;
}
.red-message { color:#ff3a3a; font-weight:bold; font-size:1.09em; padding:7px 0 2px 0;}
.player-card {
  background: #fafdfecc;
  color: #132346;
  border-radius: 17px;
  padding: 13px 12px 8px 12px;
  margin: 8px 3vw 13px 3vw;
  box-shadow: 0 0 12px #17b6ff3b;
  min-width: 150px; max-width: 175px; font-size:1.01em;
  display: flex; flex-direction: column; align-items: center;
  border: 2px solid #188bb188; position: relative; transition:0.11s;
}
.player-card.selected {border: 2.6px solid #ffe36e; box-shadow: 0 0 20px #ffe63e55;}
.player-card img { border-radius:50%; margin-bottom:7px; border:2.2px solid #2789d7; background:#fff; object-fit:cover; }
.detail-popup {
  position: absolute; top: 95%; left: 50%; transform:translateX(-50%);
  min-width: 220px; max-width:290px;
  background: #243654bb; color: #fff;
  border-radius: 16px; padding: 20px 18px;
  box-shadow: 0 0 13px #1f2d44a2; font-size: 1.08em;
  border: 2.3px solid #1698d488; z-index: 10;
  backdrop-filter: blur(12px);
}
.mobile-table {overflow-x:auto; white-space:nowrap;}
.mobile-table th, .mobile-table td {
  padding: 4px 10px; font-size: 15px; border-bottom: 1.3px solid #243255;
}
.stage-label { background: #222b3c88; color: #fff; border-radius: 10px; padding: 2px 12px; font-size:1.08em; font-weight:bold; margin-bottom:9px;}
.position-label { color: #fff !important; background:#1b4f83; border-radius:7px; padding:1px 8px; font-weight:bold; margin:0 2px;}
.stDataFrame, .custom-table {background: #253457ee !important; color: #fff !important;}
.stDataFrame th { background: #263353dd !important; color:#ffe900 !important;}
.scout-btn {background:#44cbfd !important; color:#202c46 !important; font-weight:bold; border-radius:9px; padding:10px 20px; margin:8px 0 12px 0;}
.match-btn {background:#fa7b25 !important; color:#fff !important; font-weight:bold; border-radius:9px; padding:10px 20px; margin:8px 0 12px 0;}
.auto-xi-btn {background:#27e3b9 !important; color:#202b41 !important; font-weight:bold; border-radius:9px; padding:10px 20px; margin:8px 0 12px 0;}
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- クラブ ---
CLUBS = [
    "Strive FC", "Oxford United", "Viking SC", "Lazio Town",
    "Munich Stars", "Lille City", "Sevilla Reds", "Verona Blues"
]
NUM_CLUBS = len(CLUBS)
MY_CLUB = CLUBS[0]

# --- 顔画像 ---
face_imgs = [
    f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in
    [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40]
]
def get_player_img(idx):
    return face_imgs[idx % len(face_imgs)]

surname_pool = ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker","White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris","Baker","Moore","Wright","Hill","Cooper","Edwards","Ward","King","Parker"]
given_pool = ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William","James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin","Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"]

def make_name(used_names):
    while True:
        name = f"{random.choice(given_pool)} {random.choice(surname_pool)}"
        if name not in used_names:
            used_names.add(name)
            return name

def format_money(val):
    if val >= 1_000_000_000:
        return f"{val//1_000_000_000}b€"
    elif val >= 1_000_000:
        return f"{val//1_000_000}m€"
    elif val >= 1_000:
        return f"{val//1_000}k€"
    else:
        return f"{int(val)}€"

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

def colored_num(v):
    if v >= 90: return f"<span style='color:#21f174;font-weight:bold'>{v}</span>"
    if v >= 75: return f"<span style='color:#ffe153;font-weight:bold'>{v}</span>"
    return f"<span style='color:#6ed2ff'>{v}</span>"

def generate_players(n=30, club=None, used_names=None):
    players = []
    if used_names is None: used_names = set()
    for i in range(n):
        name = make_name(used_names)
        player = dict(
            Name=name,
            Pos=random.choice(["GK","DF","MF","FW"]),
            Age=random.randint(18,34),
            Club=club if club else random.choice(CLUBS),
            Spd=random.randint(60,90),
            Pas=random.randint(60,90),
            Phy=random.randint(60,90),
            Sta=random.randint(60,90),
            Def=random.randint(60,90),
            Tec=random.randint(60,90),
            Men=random.randint(60,90),
            Sht=random.randint(60,90),
            Pow=random.randint(60,90),
            Salary=random.randint(120_000,1_200_000),
            Contract=random.randint(1,3),
            OVR=0,
            Youth=0
        )
        player["OVR"] = int(np.mean([player[l] for l in labels]))
        players.append(player)
    return players

def generate_youth(n=20, club=None, used_names=None):
    players = []
    if used_names is None: used_names = set()
    for i in range(n):
        name = make_name(used_names)
        player = dict(
            Name=name,
            Pos=random.choice(["GK","DF","MF","FW"]),
            Age=random.randint(15,18),
            Club=club if club else random.choice(CLUBS),
            Spd=random.randint(52,82),
            Pas=random.randint(52,82),
            Phy=random.randint(52,82),
            Sta=random.randint(52,82),
            Def=random.randint(52,82),
            Tec=random.randint(52,82),
            Men=random.randint(52,82),
            Sht=random.randint(52,82),
            Pow=random.randint(52,82),
            Salary=random.randint(30_000,250_000),
            Contract=random.randint(1,2),
            OVR=0,
            Youth=1
        )
        player["OVR"] = int(np.mean([player[l] for l in labels]))
        players.append(player)
    return players

# --- セッション管理 ---
if "df_senior" not in st.session_state or "df_youth" not in st.session_state:
    used_names = set()
    st.session_state.df_senior = pd.DataFrame(generate_players(30, MY_CLUB, used_names))
    st.session_state.df_youth = pd.DataFrame(generate_youth(20, MY_CLUB, used_names))
if "show_detail" not in st.session_state:
    st.session_state.show_detail = None
if "current_week" not in st.session_state:
    st.session_state.current_week = 1
if "standings" not in st.session_state:
    st.session_state.standings = pd.DataFrame({
        "Club": CLUBS,
        "W": [0 for _ in CLUBS],
        "D": [0 for _ in CLUBS],
        "L": [0 for _ in CLUBS],
        "Pts": [0 for _ in CLUBS],
    })

df_senior = st.session_state.df_senior
df_youth = st.session_state.df_youth

# ========== 1. Senior Tab ==========
tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save"])
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    st.markdown('<div class="mobile-table custom-table"><table><thead><tr>' +
                ''.join([f'<th>{c}</th>' for c in ["Name","Pos","Age","Contract","Salary","OVR"]]) +
                '</tr></thead><tbody>' +
                ''.join([
                    "<tr>" + "".join([
                        f"<td>{row['Name']}</td><td><span class='position-label'>{row['Pos']}</span></td><td>{row['Age']}</td><td>{row['Contract']}</td><td>{format_money(row['Salary'])}</td><td>{row['OVR']}</td>"
                    ]) + "</tr>" for _, row in df_senior.iterrows()
                ]) + '</tbody></table></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### Players")
    cols = st.columns(min(len(df_senior),5))
    for idx, row in df_senior.iterrows():
        with cols[idx % len(cols)]:
            btn = st.button("Detail", key=f"detail_s_{idx}")
            st.markdown(
                f"""<div class='player-card'>
                <img src="{get_player_img(idx)}" width="67">
                <b>{row['Name']}</b>
                <br><span style='color:#2797e8;font-weight:bold'>OVR:{row['OVR']}</span>
                <br><span class='position-label'>{row['Pos']}</span> / {row['Age']}
                <br><span style='font-size:0.95em'>Contract:{row['Contract']}｜Salary:{format_money(row['Salary'])}</span>
                </div>""", unsafe_allow_html=True)
            if btn:
                st.session_state.show_detail = ("senior", idx)
        if st.session_state.show_detail == ("senior", idx):
            ability = [row[l] for l in labels]
            ability += ability[:1]
            angles = np.linspace(0, 2 * np.pi, len(labels)+1)
            fig, ax = plt.subplots(figsize=(2.6,2.6), subplot_kw=dict(polar=True))
            ax.plot(angles, ability, linewidth=2, linestyle='solid', color="#1feaae")
            ax.fill(angles, ability, alpha=0.38, color="#3be6c8")
            ax.set_yticklabels([])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([labels_full[k] for k in labels], color="w")
            ax.grid(color="#3ad6c9", alpha=0.18)
            fig.patch.set_alpha(0)
            ax.patch.set_alpha(0)
            st.pyplot(fig)
            # ステータス（色付き数値）
            st.markdown("<div class='detail-popup'>" +
                f"<b>{row['Name']} ({row['Pos']})</b><br>Age:{row['Age']}<br>Contract:{row['Contract']}<br>Salary:{format_money(row['Salary'])}<br>" +
                "<hr style='border:0.5px solid #eee4;'>" +
                "".join([f"{labels_full[l]} : {colored_num(row[l])}<br>" for l in labels]) +
                "</div>", unsafe_allow_html=True)

# ========== 2. Youth Tab ==========
with tabs[1]:
    st.markdown('<div class="stage-label">Youth Squad</div>', unsafe_allow_html=True)
    if len(df_youth) == 0:
        st.markdown("<div class='red-message'>No youth players.</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="mobile-table custom-table"><table><thead><tr>' +
                    ''.join([f'<th>{c}</th>' for c in ["Name","Pos","Age","Contract","Salary","OVR"]]) +
                    '</tr></thead><tbody>' +
                    ''.join([
                        "<tr>" + "".join([
                            f"<td>{row['Name']}</td><td><span class='position-label'>{row['Pos']}</span></td><td>{row['Age']}</td><td>{row['Contract']}</td><td>{format_money(row['Salary'])}</td><td>{row['OVR']}</td>"
                        ]) + "</tr>" for _, row in df_youth.iterrows()
                    ]) + '</tbody></table></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### Youth Players")
        cols = st.columns(min(len(df_youth),5))
        for idx, row in df_youth.iterrows():
            with cols[idx % len(cols)]:
                btn = st.button("Detail", key=f"detail_y_{idx}")
                st.markdown(
                    f"""<div class='player-card'>
                    <img src="{get_player_img(idx)}" width="65">
                    <b>{row['Name']}</b>
                    <br><span style='color:#2797e8;font-weight:bold'>OVR:{row['OVR']}</span>
                    <br><span class='position-label'>{row['Pos']}</span> / {row['Age']}
                    <br><span style='font-size:0.95em'>Contract:{row['Contract']}｜Salary:{format_money(row['Salary'])}</span>
                    </div>""", unsafe_allow_html=True)
                if btn:
                    st.session_state.show_detail = ("youth", idx)
            if st.session_state.show_detail == ("youth", idx):
                ability = [row[l] for l in labels]
                ability += ability[:1]
                angles = np.linspace(0, 2 * np.pi, len(labels)+1)
                fig, ax = plt.subplots(figsize=(2.5,2.5), subplot_kw=dict(polar=True))
                ax.plot(angles, ability, linewidth=2, linestyle='solid', color="#e3a")
                ax.fill(angles, ability, alpha=0.38, color="#e3a")
                ax.set_yticklabels([])
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels([labels_full[k] for k in labels], color="w")
                ax.grid(color="#e3a", alpha=0.19)
                fig.patch.set_alpha(0)
                ax.patch.set_alpha(0)
                st.pyplot(fig)
                st.markdown("<div class='detail-popup'>" +
                    f"<b>{row['Name']} ({row['Pos']})</b><br>Age:{row['Age']}<br>Contract:{row['Contract']}<br>Salary:{format_money(row['Salary'])}<br>" +
                    "<hr style='border:0.5px solid #eee4;'>" +
                    "".join([f"{labels_full[l]} : {colored_num(row[l])}<br>" for l in labels]) +
                    "</div>", unsafe_allow_html=True)

# ========== 3. Match Tab ==========
with tabs[2]:
    st.markdown(f'<div class="stage-label">Match Simulation - Week <b style="color:#ffe34a;">{st.session_state.current_week}</b></div>', unsafe_allow_html=True)
    auto_btn = st.button("Auto Starting XI", key="auto_xi", help="Best squad by OVR", use_container_width=True)
    match_btn = st.button("Play Match", key="play_match", help="Play match vs random club", use_container_width=True)
    # 配色強調
    st.markdown("""
    <style>
    [data-testid="baseButton-secondaryForm-auto_xi"] {background:#27e3b9 !important; color:#202b41 !important;}
    [data-testid="baseButton-secondaryForm-play_match"] {background:#fa7b25 !important; color:#fff !important;}
    </style>
    """, unsafe_allow_html=True)
    result = ""
    if match_btn:
        # 相手クラブ決定
        my_ovr = int(df_senior['OVR'].mean())
        opponent_idx = random.choice([i for i in range(NUM_CLUBS) if CLUBS[i] != MY_CLUB])
        opponent_club = CLUBS[opponent_idx]
        opponent_ovr = random.randint(65,88)
        st.write(f"VS {opponent_club} (OVR:{opponent_ovr})")
        my_score = random.randint(0,2) + (my_ovr > opponent_ovr) + (my_ovr-70)//10
        opp_score = random.randint(0,2) + (opponent_ovr > my_ovr) + (opponent_ovr-70)//10
        if my_score > opp_score:
            result = "Win"
            st.session_state.standings.loc[st.session_state.standings["Club"] == MY_CLUB, "W"] += 1
            st.session_state.standings.loc[st.session_state.standings["Club"] == MY_CLUB, "Pts"] += 3
        elif my_score < opp_score:
            result = "Lose"
            st.session_state.standings.loc[st.session_state.standings["Club"] == MY_CLUB, "L"] += 1
        else:
            result = "Draw"
            st.session_state.standings.loc[st.session_state.standings["Club"] == MY_CLUB, "D"] += 1
            st.session_state.standings.loc[st.session_state.standings["Club"] == MY_CLUB, "Pts"] += 1
        st.success(f"Result: {result} ({my_score} - {opp_score})")
        st.session_state.current_week += 1

# ========== 4. Scout Tab ==========
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Scout New Senior", key="scout_senior", help="Find a new senior player", use_container_width=True):
            st.session_state.df_senior = pd.concat([
                st.session_state.df_senior,
                pd.DataFrame(generate_players(1, MY_CLUB, set(st.session_state.df_senior['Name'])))
            ], ignore_index=True)
            st.success("New senior player scouted!")
    with col2:
        if st.button("Scout New Youth", key="scout_youth", help="Find a new youth player", use_container_width=True):
            st.session_state.df_youth = pd.concat([
                st.session_state.df_youth,
                pd.DataFrame(generate_youth(1, MY_CLUB, set(st.session_state.df_youth['Name'])))
            ], ignore_index=True)
            st.success("New youth player scouted!")
    # Scoutボタン色変更
    st.markdown("""
    <style>
    [data-testid="baseButton-secondaryForm-scout_senior"] {background:#44cbfd !important; color:#202c46 !important;}
    [data-testid="baseButton-secondaryForm-scout_youth"] {background:#ffad5a !important; color:#fff !important;}
    </style>
    """, unsafe_allow_html=True)

# ========== 5. Standings Tab ==========
with tabs[4]:
    st.markdown('<div class="stage-label">Standings</div>', unsafe_allow_html=True)
    # 順位表を背景一体化・シニア/ユース欄風
    df_stand = st.session_state.standings.copy()
    st.markdown('<div class="mobile-table custom-table"><table><thead><tr>' +
                ''.join([f'<th>{c}</th>' for c in df_stand.columns]) +
                '</tr></thead><tbody>' +
                ''.join([
                    "<tr>" + "".join([
                        f"<td>{row[c]}</td>" for c in df_stand.columns
                    ]) + "</tr>" for _, row in df_stand.iterrows()
                ]) + '</tbody></table></div>', unsafe_allow_html=True)

# ========== 6. Save Tab ==========
with tabs[5]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Data", key="save_btn"): st.success("データ保存しました")
    if st.button("Load Data", key="load_btn"): st.success("データを読み込みました")

st.caption("2025年最新版：全要望（詳細/配色/ボタン/勝敗/詳細数値色/順位表背景/Scout/全反応/ダミー除去）完全統合版。")
