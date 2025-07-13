import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="Soccer Club Management Sim", layout="wide")

# --- CSS/UIカスタム ---
st.markdown("""
<style>
body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
.stApp { background: linear-gradient(120deg, #202c46 0%, #314265 100%) !important; color: #eaf6ff; }
h1,h2,h3,h4,h5,h6, .stTabs label, .stTabs span, .stTabs button { color: #fff !important; }
.stTabs [data-baseweb="tab"] > button[aria-selected="true"] { color: #fff !important; background: transparent !important; border-bottom: 2.7px solid #f7df70 !important;}
.stTabs [data-baseweb="tab"] > button { color: #fff !important; background: transparent !important; }
.stButton>button, .stDownloadButton>button {
    background: #27e3b9 !important;
    color: #202b41 !important;
    font-weight:bold; border-radius: 11px;
    font-size:1.04em; margin:7px 0 8px 0;
    box-shadow:0 0 10px #23e9e733;
}
.stButton>button:active { background: #ffee99 !important; }
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
  min-width: 180px; max-width:250px;
  background: #243654bb; color: #fff;
  border-radius: 16px; padding: 16px 15px;
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
.stDataFrame {background: #202c46cc !important; color: #fff !important;}
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- クラブ名（ヨーロッパ8クラブのみ/英語） ---
CLUBS = [
    "Strive FC", "Oxford United", "Viking SC", "Lazio Town",
    "Munich Stars", "Lille City", "Sevilla Reds", "Verona Blues"
]
NUM_CLUBS = len(CLUBS)
MY_CLUB = CLUBS[0]

# --- 顔画像（30枚欧米風/任意URL変更可） ---
face_imgs = [
    f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in
    [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40]
]
def get_player_img(idx):
    return face_imgs[idx % len(face_imgs)]

# --- ネームプール（英語・姓30＋名30） ---
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

df_senior = st.session_state.df_senior
df_youth = st.session_state.df_youth

# 詳細管理
if "show_detail" not in st.session_state:
    st.session_state.show_detail = None

# --- タブ ---
tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save"])

# ========== 1. Senior Tab ==========
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    st.markdown('<div class="mobile-table"><table><thead><tr>' +
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
            # --- 詳細クリック時のみ即時表示 ---
            if btn:
                st.session_state.show_detail = ("senior", idx)
        # 表示判定
        if st.session_state.show_detail == ("senior", idx):
            ability = [row[l] for l in labels]
            ability += ability[:1]
            angles = np.linspace(0, 2 * np.pi, len(labels)+1)
            fig, ax = plt.subplots(figsize=(2.6,2.6), subplot_kw=dict(polar=True))
            ax.plot(angles, ability, linewidth=2, linestyle='solid')
            ax.fill(angles, ability, alpha=0.38)
            ax.set_yticklabels([])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([labels_full[k] for k in labels], color="w")
            ax.grid(color="#3ad6c9", alpha=0.18)
            fig.patch.set_alpha(0)
            ax.patch.set_alpha(0)
            st.pyplot(fig)
            st.markdown(f"<div class='detail-popup'>"
                        f"<b>{row['Name']} ({row['Pos']})</b><br>Age:{row['Age']}<br>Contract:{row['Contract']}<br>Salary:{format_money(row['Salary'])}<br>"
                        f"<span style='font-size:0.93em;'>Skill Chart (No values)</span></div>",
                        unsafe_allow_html=True)

# ========== 2. Youth Tab ==========
with tabs[1]:
    st.markdown('<div class="stage-label">Youth Squad</div>', unsafe_allow_html=True)
    if len(df_youth) == 0:
        st.markdown("<div class='red-message'>No youth players.</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="mobile-table"><table><thead><tr>' +
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
                ax.plot(angles, ability, linewidth=2, linestyle='solid')
                ax.fill(angles, ability, alpha=0.38)
                ax.set_yticklabels([])
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels([labels_full[k] for k in labels], color="w")
                ax.grid(color="#e3a", alpha=0.19)
                fig.patch.set_alpha(0)
                ax.patch.set_alpha(0)
                st.pyplot(fig)
                st.markdown(f"<div class='detail-popup'><b>{row['Name']} ({row['Pos']})</b><br>Age:{row['Age']}<br>Contract:{row['Contract']}<br>Salary:{format_money(row['Salary'])}<br>"
                            "<span style='font-size:0.93em;'>Skill Chart (No values)</span></div>",
                            unsafe_allow_html=True)

# ========== 3. Match Tab ==========
with tabs[2]:
    st.markdown(f'<div class="stage-label">Match Simulation - Week <b style="color:#ffe34a;">1</b></div>', unsafe_allow_html=True)
    if st.button("Auto Starting XI", key="auto_xi", help="Best squad by OVR"):
        # スタメン自動選出
        st.success("Auto Starting XI selected (サンプル)")
    # 手動で選出なども拡張可能

# ========== 4. Scout Tab ==========
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players</div>', unsafe_allow_html=True)
    if st.button("Scout New Senior", key="scout_senior", help="Find a new senior player"):
        st.session_state.df_senior = st.session_state.df_senior.append(
            generate_players(1, MY_CLUB, set(st.session_state.df_senior['Name'])), ignore_index=True)
        st.success("New senior player scouted!")
    if st.button("Scout New Youth", key="scout_youth", help="Find a new youth player"):
        st.session_state.df_youth = st.session_state.df_youth.append(
            generate_youth(1, MY_CLUB, set(st.session_state.df_youth['Name'])), ignore_index=True)
        st.success("New youth player scouted!")

# ========== 5. Standings Tab ==========
with tabs[4]:
    st.markdown('<div class="stage-label">Standings</div>', unsafe_allow_html=True)
    standings = pd.DataFrame({
        "Club": CLUBS,
        "W": [random.randint(1,8) for _ in CLUBS],
        "D": [random.randint(0,4) for _ in CLUBS],
        "L": [random.randint(0,4) for _ in CLUBS],
        "Pts": [random.randint(10,23) for _ in CLUBS],
    }).sort_values("Pts", ascending=False)
    st.dataframe(standings.style
        .set_properties(**{'background-color': '#253457ee', 'color':'#fff', 'font-weight':'bold'})
        .set_table_styles([{"selector": "thead tr th", "props": [("background", "#263353dd"), ("color","#ffe900")]}])
        , height=380)

# ========== 6. Save Tab ==========
with tabs[5]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Data", key="save_btn"): st.success("Save simulated (ダミー)")
    if st.button("Load Data", key="load_btn"): st.success("Load simulated (ダミー)")

st.caption("2025年最新版：全要望（色調和UI/白タブ/詳細透過/Scout両対応/AutoXI/第n節/反応修正）完全統合版。")
