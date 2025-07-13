import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- ページ設定 ---
st.set_page_config(page_title="Soccer Club Management Sim", layout="wide")
random.seed(42)
np.random.seed(42)

# --- CSSカスタム ---
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff;}
h1,h2,h3,h4,h5,h6 { color:#fff!important; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }
.stButton>button, .stDownloadButton>button {
  background:#192841!important; color:#eaf6ff!important; font-weight:bold;
  border-radius:10px; margin:6px 0; box-shadow:0 0 8px #0005;
}
.stButton>button:active { background:#314265!important; }
.player-card {
  background:#fff; color:#132346; border-radius:12px;
  padding:10px; margin:8px; width:160px; display:inline-block; vertical-align:top;
  box-shadow:0 0 8px #0003; position:relative;
}
.player-card img {
  border-radius:50%; width:64px; height:64px; object-fit:cover;
}
.detail-popup {
  position:absolute; top:calc(100% + 6px); left:50%; transform:translateX(-50%);
  background:rgba(36,54,84,0.9); color:#fff; padding:12px; border-radius:10px;
  width:200px; box-shadow:0 0 10px #000a; z-index:10; backdrop-filter:blur(8px);
}
.mobile-scroll { overflow-x:auto; white-space:nowrap; padding-bottom:12px; }
.stage-label { background:#222b3c88; color:#fff; padding:6px 12px; border-radius:8px; display:inline-block; margin-bottom:8px;}
.red-message { color:#f55!important; }
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- 定数 ---
CLUBS = ["Strive FC","Oxford Utd","Viking SC","Lazio Town",
         "Munich Stars","Lille City","Sevilla Reds","Verona Blues"]
MY_CLUB = CLUBS[0]
NATIONS = {
    "England":"🏴","Germany":"🇩🇪","Italy":"🇮🇹","Spain":"🇪🇸",
    "France":"🇫🇷","Brazil":"🇧🇷","Netherlands":"🇳🇱","Portugal":"🇵🇹"
}

# --- 画像リスト ---
face_imgs = [f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in range(10,50)]
def get_img(i): return face_imgs[i % len(face_imgs)]

# --- 名前プール ---
surname = ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
           "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris",
           "Baker","Moore","Wright","Hill","Cooper","Edwards","Ward","King","Parker","Campbell"]
given   = ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
           "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin",
           "Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"]
def make_name(used):
    while True:
        n=f"{random.choice(given)} {random.choice(surname)}"
        if n not in used:
            used.add(n)
            return n

# --- フォーマット ---
def fmt_money(v):
    if v>=1_000_000: return f"{v//1_000_000}m€"
    if v>=1_000:     return f"{v//1_000}k€"
    return f"{v}€"

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina',
               'Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

# --- データ生成関数 ---
def gen_players(n, youth=False):
    used=set()
    lst=[]
    for i in range(n):
        name=make_name(used)
        stats={l:random.randint(52 if youth else 60,82 if youth else 90) for l in labels}
        ovr=int(np.mean(list(stats.values())))
        fee=random.randint(50_000 if youth else 200_000,300_000 if youth else 1_500_000)
        salary=random.randint(30_000 if youth else 120_000,250_000 if youth else 1_200_000)
        contract=random.randint(1,2 if youth else 3)
        nat=random.choice(list(NATIONS.keys()))
        lst.append({
            "Name":name, "Nat":nat, "Pos":random.choice(["GK","DF","MF","FW"]),
            "Age":random.randint(15 if youth else 18,18 if youth else 34),
            **stats, "OVR":ovr,
            "Salary":salary, "Contract":contract, "Fee":fee,
            "Youth":youth
        })
    return pd.DataFrame(lst)

# --- セッション初期化 ---
if "senior" not in st.session_state:
    st.session_state.senior = gen_players(30, False)
if "youth" not in st.session_state:
    st.session_state.youth  = gen_players(20, True)
if "stand" not in st.session_state:
    st.session_state.stand   = pd.DataFrame({"Club":CLUBS,"W":0,"D":0,"L":0,"Pts":0})
if "opp" not in st.session_state:
    st.session_state.opp     = random.choice([c for c in CLUBS if c!=MY_CLUB])
if "detail" not in st.session_state:
    st.session_state.detail  = None
if "starters" not in st.session_state:
    st.session_state.starters = []
if "budget" not in st.session_state:
    st.session_state.budget   = 3_000_000
if "scout_s" not in st.session_state:
    st.session_state.scout_s = pd.DataFrame()
if "scout_y" not in st.session_state:
    st.session_state.scout_y = pd.DataFrame()

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# ==== Senior タブ ====
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    df1 = st.session_state.senior.copy()
    df1["Nat"] = df1["Nat"].map(NATIONS)
    # 紺背景＆白文字のDataFrame
    styled = df1[["Name","Nat","Pos","Age","Contract","Salary","Fee","OVR"]].assign(
        Salary=df1["Salary"].map(fmt_money), Fee=df1["Fee"].map(fmt_money)
    ).style.set_properties(**{
        "background-color":"#192841","color":"white","text-align":"center"
    }).set_table_styles([{
        "selector":"thead","props":[("background","#192841"),("color","white")]
    }])
    st.dataframe(styled, use_container_width=True)
    st.markdown("---")
    st.markdown("#### Players")
    st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
    for i,row in df1.iterrows():
        key=f"sen_det_{i}"
        st.markdown(f"""
          <div class="player-card">
            <img src="{get_img(i)}"><br>
            <b>{row['Name']} {row['Nat']}</b><br>
            {row['Pos']}｜{row['Age']}<br>
            OVR:{row['OVR']}<br>
            Contract:{row['Contract']}y | Salary:{fmt_money(row['Salary'])}<br>
            Fee:{fmt_money(row['Fee'])}
          </div>
        """, unsafe_allow_html=True)
        if st.button("Detail", key=key):
            st.session_state.detail = None if st.session_state.detail==key else key
        if st.session_state.detail==key:
            vals=[row[l] for l in labels]+[row[labels[0]]]
            ang=np.linspace(0,2*np.pi,len(labels)+1)
            fig,ax=plt.subplots(subplot_kw=dict(polar=True),figsize=(2,2))
            ax.plot(ang,vals,linewidth=2); ax.fill(ang,vals,alpha=0.3)
            ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels],color="#fff")
            ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
            fig.patch.set_alpha(0); ax.patch.set_alpha(0)
            st.pyplot(fig)
            stats="".join(
                f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                for l in labels
            )
            st.markdown(f"<div class='detail-popup'>{stats}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==== Youth タブ ====
with tabs[1]:
    st.markdown('<div class="stage-label">Youth Squad</div>', unsafe_allow_html=True)
    df2 = st.session_state.youth.copy()
    df2["Nat"] = df2["Nat"].map(NATIONS)
    if df2.empty:
        st.markdown("<div class='red-message'>No youth players.</div>", unsafe_allow_html=True)
    else:
        styled2 = df2[["Name","Nat","Pos","Age","Contract","Salary","Fee","OVR"]].assign(
            Salary=df2["Salary"].map(fmt_money), Fee=df2["Fee"].map(fmt_money)
        ).style.set_properties(**{
            "background-color":"#192841","color":"white","text-align":"center"
        }).set_table_styles([{
            "selector":"thead","props":[("background","#192841"),("color","white")]
        }])
        st.dataframe(styled2, use_container_width=True)

# ==== Match タブ ====
with tabs[2]:
    # ... 省略／前回と同様実装

# ==== Scout タブ ====
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players</div>', unsafe_allow_html=True)
    st.markdown(f"**Budget:** {fmt_money(st.session_state.budget)}")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("Refresh Senior"):
            st.session_state.scout_s = gen_players(5, False)
    with c2:
        if st.button("Refresh Youth"):
            st.session_state.scout_y = gen_players(5, True)
    if not st.session_state.scout_s.empty:
        st.markdown("#### Senior Candidates")
        st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
        for i,row in st.session_state.scout_s.iterrows():
            key=f"sign_s{i}"
            st.markdown(f"""
              <div class="player-card">
                <img src="{get_img(i+60)}"><br>
                <b>{row['Name']} {NATIONS[row['Nat']]}</b><br>
                {row['Pos']}｜{row['Age']}｜OVR:{row['OVR']}<br>
                Fee:{fmt_money(row['Fee'])}
              </div>
            """, unsafe_allow_html=True)
            if st.button("Sign", key=key):
                if row["Name"] in st.session_state.senior["Name"].tolist():
                    st.error("Already in squad")
                elif st.session_state.budget < row["Fee"]:
                    st.error("Not enough budget")
                else:
                    st.session_state.budget -= row["Fee"]
                    st.session_state.senior = pd.concat(
                        [st.session_state.senior, pd.DataFrame([row])],
                        ignore_index=True
                    )
                    st.success(f"Signed {row['Name']}!")
        st.markdown('</div>', unsafe_allow_html=True)
    if not st.session_state.scout_y.empty:
        st.markdown("#### Youth Candidates")
        st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
        for i,row in st.session_state.scout_y.iterrows():
            key=f"sign_y{i}"
            st.markdown(f"""
              <div class="player-card">
                <img src="{get_img(i+80)}"><br>
                <b>{row['Name']} {NATIONS[row['Nat']]}</b><br>
                {row['Pos']}｜{row['Age']}｜OVR:{row['OVR']}<br>
                Fee:{fmt_money(row['Fee'])}
              </div>
            """, unsafe_allow_html=True)
            if st.button("Sign", key=key):
                if row["Name"] in st.session_state.youth["Name"].tolist():
                    st.error("Already in youth")
                elif st.session_state.budget < row["Fee"]:
                    st.error("Not enough budget")
                else:
                    st.session_state.budget -= row["Fee"]
                    st.session_state.youth = pd.concat(
                        [st.session_state.youth, pd.DataFrame([row])],
                        ignore_index=True
                    )
                    st.success(f"Signed {row['Name']}!")
        st.markdown('</div>', unsafe_allow_html=True)

# ==== Standings タブ ====
with tabs[4]:
    # ... 省略／前回と同様実装

# ==== Save タブ ====
with tabs[5]:
    # ... 省略／前回と同様実装

st.caption("2025年版：詳細＆契約ボタン再生成＋スカッド紺背景・白文字 完全反映版")
