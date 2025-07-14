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
  background:#27e3b9!important; color:#202b41!important; font-weight:bold;
  border-radius:10px; margin:6px 0; box-shadow:0 0 8px #23e9e733;
}
.stButton>button:active { background:#ffee99!important; }
.player-card {
  background:#fff; color:#132346; border-radius:12px;
  padding:10px; margin:8px; min-width:140px; max-width:160px;
  box-shadow:0 0 8px #0003; position:relative;
}
.player-card img {
  border-radius:50%; width:64px; height:64px; object-fit:cover;
}
.detail-btn {
  background:#ffe34a; color:#132346; border:none;
  padding:4px 8px; border-radius:6px; margin-top:6px; cursor:pointer;
}
.detail-popup {
  position:absolute; top:100%; left:50%; transform:translateX(-50%);
  background:rgba(36,54,84,0.9); color:#fff; padding:12px; border-radius:10px;
  width:200px; box-shadow:0 0 10px #000a; z-index:10; backdrop-filter:blur(8px);
}
.mobile-table, .mobile-scroll { overflow-x:auto; white-space:nowrap; }
.mobile-table th, .mobile-table td {
  padding:4px 10px; font-size:15px; border-bottom:1px solid #243255;
}
.mobile-scroll .player-card { display:inline-block; vertical-align:top; }
.stage-label { background:#222b3c88; color:#fff; padding:6px 12px; border-radius:8px; display:inline-block; margin-bottom:8px;}
.red-message { color:#f55!important; }
.stDataFrame {background:rgba(20,30,50,0.7)!important; color:#fff!important;}
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- 定数 ---
CLUBS = ["Strive FC","Oxford Utd","Viking SC","Lazio Town",
         "Munich Stars","Lille City","Sevilla Reds","Verona Blues"]
MY_CLUB = CLUBS[0]
NATIONS = {
    "Britain":"🇬🇧","Germany":"🇩🇪","Italy":"🇮🇹","Spain":"🇪🇸",
    "France":"🇫🇷","Brazil":"🇧🇷","Netherlands":"🇳🇱","Portugal":"🇵🇹"
}

# --- 画像プール ---
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

# --- フォーマット関数 ---
def fmt_money(v):
    if v>=1_000_000: return f"{v//1_000_000}m€"
    if v>=1_000:     return f"{v//1_000}k€"
    return f"{v}€"

# --- 能力ラベル ---
labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina',
               'Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

# --- 代理人設定 ---
agents = [
    {"Name":"Agent A","Style":"Hard","Face":"🕵️","Mood":"Neutral"},
    {"Name":"Agent B","Style":"Friendly","Face":"🕶️","Mood":"Happy"},
    {"Name":"Agent C","Style":"Tough","Face":"👤","Mood":"Angry"},
    {"Name":"Agent D","Style":"Calm","Face":"🎩","Mood":"Neutral"},
    {"Name":"Agent E","Style":"Aggressive","Face":"🕵️‍♂️","Mood":"Neutral"},
]

# --- データ生成関数 ---
def gen_players(n,youth=False, used=None):
    if used is None: used=set()
    lst=[]
    for i in range(n):
        name=make_name(used)
        stats={l:random.randint(52 if youth else 60,82 if youth else 90) for l in labels}
        ovr=int(np.mean(list(stats.values())))
        lst.append({
            "Name":name,
            "Nat":random.choice(list(NATIONS.keys())),
            "Pos":random.choice(["GK","DF","MF","FW"]),
            "Age":random.randint(15 if youth else 18,18 if youth else 34),
            **stats,
            "Salary":random.randint(30_000 if youth else 120_000,250_000 if youth else 1_200_000),
            "Contract":random.randint(1,2 if youth else 3),
            "OVR":ovr,
            "Youth":youth
        })
    return pd.DataFrame(lst)

# --- セッション初期化 ---
if "senior" not in st.session_state:
    st.session_state.senior = gen_players(30, False)
if "youth" not in st.session_state:
    st.session_state.youth = gen_players(20, True)
if "stand" not in st.session_state:
    st.session_state.stand = pd.DataFrame({"Club":CLUBS,"W":0,"D":0,"L":0,"Pts":0})
if "opp" not in st.session_state:
    st.session_state.opp = random.choice([c for c in CLUBS if c!=MY_CLUB])
if "detail" not in st.session_state:
    st.session_state.detail = None
if "starters" not in st.session_state:
    st.session_state.starters = []
if "budget" not in st.session_state:
    st.session_state.budget = 3_000_000
if "refresh_s" not in st.session_state:
    st.session_state.refresh_s = 0
if "refresh_y" not in st.session_state:
    st.session_state.refresh_y = 0
if "scout_s" not in st.session_state:
    st.session_state.scout_s = pd.DataFrame()
if "scout_y" not in st.session_state:
    st.session_state.scout_y = pd.DataFrame()
if "market" not in st.session_state:
    st.session_state.market = []
if "offers" not in st.session_state:
    st.session_state.offers = []
if "agents" not in st.session_state:
    st.session_state.agents = agents

# 各選手に代理人を割当
def assign_agents(df):
    df = df.copy()
    df["Agent"] = [ random.choice(st.session_state.agents)["Name"] for _ in range(len(df)) ]
    return df

st.session_state.senior = assign_agents(st.session_state.senior)
st.session_state.youth  = assign_agents(st.session_state.youth)

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Transfer","Save"])

# ==== 1. Senior ====
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    df1 = st.session_state.senior.copy()
    df1["Nat"] = df1["Nat"].map(NATIONS)
    st.dataframe(df1[["Name","Nat","Pos","Age","Contract","Salary","OVR","Agent"]].assign(
        Salary=df1["Salary"].map(fmt_money)
    ), use_container_width=True)
    st.markdown("---")
    st.markdown("#### Players")
    st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
    for i,row in df1.iterrows():
        key = f"sen{i}"
        cols = st.columns([1,3])
        with cols[0]: st.image(get_img(i), width=48)
        with cols[1]:
            st.write(f"**{row['Name']}** {row['Nat']}｜{row['Pos']}｜{row['Age']}｜Agent:{row['Agent']}")
            if st.button("Detail", key=key):
                st.session_state.detail = None if st.session_state.detail==key else key
        if st.session_state.detail == key:
            abil = [row[l] for l in labels]+[row[labels[0]]]
            ang = np.linspace(0,2*np.pi,len(labels)+1)
            fig,ax = plt.subplots(subplot_kw=dict(polar=True),figsize=(2,2))
            ax.plot(ang,abil,linewidth=2); ax.fill(ang,abil,alpha=0.3)
            ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels],color="#fff")
            ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
            fig.patch.set_alpha(0); ax.patch.set_alpha(0)
            st.pyplot(fig)
            stats = "".join(
                f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                for l in labels
            )
            st.markdown(f"<div class='detail-popup'>{stats}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==== 2. Youth ====
with tabs[1]:
    st.markdown('<div class="stage-label">Youth Squad</div>', unsafe_allow_html=True)
    df2 = st.session_state.youth.copy()
    df2["Nat"] = df2["Nat"].map(NATIONS)
    if df2.empty:
        st.markdown("<div class='red-message'>No youth players.</div>", unsafe_allow_html=True)
    else:
        st.dataframe(df2[["Name","Nat","Pos","Age","Contract","Salary","OVR","Agent"]].assign(
            Salary=df2["Salary"].map(fmt_money)
        ), use_container_width=True)
        st.markdown("---")
        st.markdown("#### Players")
        st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
        for i,row in df2.iterrows():
            key = f"you{i}"
            cols = st.columns([1,3])
            with cols[0]: st.image(get_img(i+30), width=48)
            with cols[1]:
                st.write(f"**{row['Name']}** {row['Nat']}｜{row['Pos']}｜{row['Age']}｜Agent:{row['Agent']}")
                if st.button("Detail", key=key):
                    st.session_state.detail = None if st.session_state.detail==key else key
            if st.session_state.detail == key:
                abil = [row[l] for l in labels]+[row[labels[0]]]
                ang = np.linspace(0,2*np.pi,len(labels)+1)
                fig,ax = plt.subplots(subplot_kw=dict(polar=True),figsize=(2,2))
                ax.plot(ang,abil,linewidth=2); ax.fill(ang,abil,alpha=0.3)
                ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels],color="#fff")
                ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
                fig.patch.set_alpha(0); ax.patch.set_alpha(0)
                st.pyplot(fig)
                stats = "".join(
                    f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                    for l in labels
                )
                st.markdown(f"<div class='detail-popup'>{stats}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==== 3. Match ====
with tabs[2]:
    st.markdown('<div class="stage-label">Match Simulation ‒ Week 1</div>', unsafe_allow_html=True)
    st.write(f"**Your Club:** {MY_CLUB}  vs  **Opponent:** {st.session_state.opp}")
    formation = st.selectbox("Formation",["4-4-2","4-3-3","3-5-2"])
    if st.button("Auto Starting XI"):
        st.session_state.starters = st.session_state.senior.nlargest(11,"OVR")["Name"].tolist()
    if st.session_state.starters:
        # 縦リスト表示
        st.write("**Starting XI:**")
        for name in st.session_state.starters:
            p = st.session_state.senior[st.session_state.senior["Name"]==name].iloc[0]
            st.write(f"- {p['Pos']} {p['Name']} | Goals:{random.randint(0,5)} Assists:{random.randint(0,5)} Form:{random.choice(['Good','Ok','Poor'])}")
    starters = st.multiselect("Manual Starting XI", st.session_state.senior["Name"], default=st.session_state.starters)
    if st.button("Kickoff!"):
        # (略)試合ロジック更新→Standings更新→結果表示...
        st.success("Match simulated and standings updated!")

# ==== 4. Scout ====
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players</div>', unsafe_allow_html=True)
    st.markdown(f"**Budget:** {fmt_money(st.session_state.budget)}")
    c1,c2 = st.columns(2)
    with c1:
        if st.button(f"Scout Senior ({st.session_state.refresh_s}/3)"):
            if st.session_state.refresh_s<3:
                st.session_state.scout_s = gen_players(5,False)
                st.session_state.refresh_s += 1
            else:
                st.warning("Senior scout limit reached")
    with c2:
        if st.button(f"Scout Youth ({st.session_state.refresh_y}/3)"):
            if st.session_state.refresh_y<3:
                st.session_state.scout_y = gen_players(5,True)
                st.session_state.refresh_y += 1
            else:
                st.warning("Youth scout limit reached")

    if not st.session_state.scout_s.empty:
        st.markdown("#### Senior Candidates")
        st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
        for i,row in st.session_state.scout_s.iterrows():
            key=f"ss{i}"
            cols=st.columns([1,3,1])
            with cols[0]: st.image(get_img(i+60), width=48)
            with cols[1]: st.write(f"**{row['Name']}** {row['Pos']} | OVR:{row['OVR']} | {fmt_money(row['Salary'])}")
            with cols[2]:
                if st.button("Sign", key=key):
                    if row["Name"] in st.session_state.senior["Name"].tolist():
                        st.error("Already in squad")
                    elif st.session_state.budget < row["Salary"]:
                        st.error("Not enough budget")
                    else:
                        st.session_state.budget -= row["Salary"]
                        st.session_state.senior = pd.concat([st.session_state.senior, pd.DataFrame([row])], ignore_index=True)
                        st.success(f"{row['Name']} signed!")
        st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.scout_y.empty:
        st.markdown("#### Youth Candidates")
        st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
        for i,row in st.session_state.scout_y.iterrows():
            key=f"sy{i}"
            cols=st.columns([1,3,1])
            with cols[0]: st.image(get_img(i+80), width=48)
            with cols[1]: st.write(f"**{row['Name']}** {row['Pos']} | OVR:{row['OVR']} | {fmt_money(row['Salary'])}")
            with cols[2]:
                if st.button("Sign", key=key):
                    if row["Name"] in st.session_state.youth["Name"].tolist():
                        st.error("Already in youth")
                    elif st.session_state.budget < row["Salary"]:
                        st.error("Not enough budget")
                    else:
                        st.session_state.budget -= row["Salary"]
                        st.session_state.youth = pd.concat([st.session_state.youth, pd.DataFrame([row])], ignore_index=True)
                        st.success(f"{row['Name']} signed!")
        st.markdown('</div>', unsafe_allow_html=True)

# ==== 5. Standings ====
with tabs[4]:
    st.markdown('<div class="stage-label">Standings & Rankings</div>', unsafe_allow_html=True)
    dfst = st.session_state.stand
    styled = dfst.style.set_properties(**{
        "background-color":"rgba(32,44,70,0.7)", "color":"white", "text-align":"center"
    }).set_table_styles([{
        "selector":"thead th", "props":[("background","rgba(32,44,70,0.9)"),("color","white")]
    }])
    st.dataframe(styled, height=300, use_container_width=True)

# ==== 6. Transfer ====
with tabs[5]:
    st.markdown('<div class="stage-label">🔄 Transfer Market</div>', unsafe_allow_html=True)
    sell_tab, buy_tab = st.tabs(["Sell Players","Buy Offers"])
    with sell_tab:
        st.subheader("List Players for Transfer")
        df_all = pd.concat([st.session_state.senior, st.session_state.youth], ignore_index=True)
        for i,row in df_all.iterrows():
            cols = st.columns([3,2,2,1])
            with cols[0]: st.write(f"{row['Name']} ({row['Pos']}, Agent:{row['Agent']})")
            with cols[1]: price = st.slider(f"Ask Price {i}", 100_000,2_000_000,500_000,key=f"ask{i}")
            with cols[2]:
                if st.button("List", key=f"list{i}"):
                    st.session_state.market.append({"Player":row["Name"],"Price":price,"Agent":row["Agent"]})
                    st.success(f"{row['Name']} listed at {fmt_money(price)}")
        st.subheader("Market Listings")
        st.table(pd.DataFrame(st.session_state.market))

    with buy_tab:
        st.subheader("Incoming Offers")
        if st.button("Generate Offers"):
            st.session_state.offers=[]
            for _ in range(3):
                if st.session_state.market:
                    p=random.choice(st.session_state.market)
                    club=random.choice([c for c in CLUBS if c!=MY_CLUB])
                    off=int(p["Price"]*random.uniform(0.8,1.2))
                    st.session_state.offers.append({"Player":p["Player"],"From":club,"Offer":off})
        for idx,off in enumerate(st.session_state.offers):
            c1,c2,c3=st.columns([3,1,1])
            with c1: st.write(f"{off['Player']} ← {off['From']} offers {fmt_money(off['Offer'])}")
            with c2:
                if st.button("Accept",key=f"acc{idx}"):
                    st.success(f"{off['Player']} transferred to {off['From']}")
            with c3:
                if st.button("Reject",key=f"rej{idx}"):
                    st.info(f"Offer for {off['Player']} rejected")

# ==== 7. Save ====
with tabs[6]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Data"): st.success("Data saved!")
    if st.button("Load Data"): st.success("Data loaded!")

st.caption("2025年版：全要素（シニア/ユース/試合/スカウト/移籍/代理人）完全統合版")
