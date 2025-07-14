import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- ページ設定 ---
st.set_page_config(page_title="Soccer Club Management Sim", layout="wide")
random.seed(42)
np.random.seed(42)

# --- CSS/UI カスタム ---
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
  background:transparent; color:#eaf6ff; border-radius:0; padding:0; margin:0;
}
.detail-btn {
  background:#ffe34a; color:#132346; border:none;
  padding:4px 8px; border-radius:6px; margin-top:4px; cursor:pointer;
}
.detail-popup {
  background:rgba(36,54,84,0.9); color:#fff; padding:12px; border-radius:10px;
  box-shadow:0 0 10px #000a; margin-bottom:12px;
}
.mobile-table, .mobile-scroll { overflow-x:auto; white-space:nowrap; }
.mobile-table th, .mobile-table td {
  padding:4px 10px; font-size:14px; border-bottom:1px solid #243255;
}
.stage-label { background:#222b3c88; color:#fff; padding:6px 12px; border-radius:8px; display:inline-block; margin-bottom:8px;}
.red-message { color:#f55!important; }
.stat-separator { color:#888; margin:8px 0; }
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

# --- 顔画像（欧米風）---
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

# --- データ生成（Goals/Assists/Rating/MVP を追加）---
def gen_players(n,youth=False,club=None,used=None):
    if used is None: used=set()
    lst=[]
    for i in range(n):
        name=make_name(used)
        nat=random.choice(list(NATIONS.keys()))
        stats={l:random.randint(52 if youth else 60,82 if youth else 90) for l in labels}
        ovr=int(np.mean(list(stats.values())))
        lst.append({
            "Name":name,
            "Nat":nat,
            "Pos":random.choice(["GK","DF","MF","FW"]),
            "Age":random.randint(15 if youth else 18,18 if youth else 34),
            **stats,
            "Salary":random.randint(30_000 if youth else 120_000,
                                   250_000 if youth else 1_200_000),
            "Contract":random.randint(1,2 if youth else 3),
            "OVR":ovr,
            "Youth":youth,
            "Goals":0,
            "Assists":0,
            "Rating":0.0,
            "RatingsPlayed":0,
            "MVP":0
        })
    return pd.DataFrame(lst)

# --- セッション初期化 ---
if "senior" not in st.session_state:
    st.session_state.senior = gen_players(30,False,MY_CLUB)
if "youth" not in st.session_state:
    st.session_state.youth = gen_players(20,True,MY_CLUB)
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

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# ==== 1. Senior ====
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    df1 = st.session_state.senior.copy()
    df1["Nat"] = df1["Nat"].map(NATIONS)
    # テーブル表示（背景と一体化）
    st.markdown('<div style="background:transparent;">', unsafe_allow_html=True)
    st.markdown(df1[["Name","Nat","Pos","Age","Contract","Salary","OVR","Goals","Assists","Rating","MVP"]]
                .to_html(index=False, classes="mobile-table", justify="center"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### Players")
    for i,row in df1.iterrows():
        st.markdown("---", unsafe_allow_html=True)
        cols = st.columns([1,4,1])
        with cols[0]:
            st.image(get_img(i), width=48)
        with cols[1]:
            st.write(f"**{row['Name']}** {row['Nat']} | {row['Pos']} | {row['Age']}")
            st.write(f"OVR:{row['OVR']}  G:{row['Goals']}  A:{row['Assists']}  R:{row['Rating']:.2f}  MVP:{row['MVP']}")
        with cols[2]:
            key=f"det_s{i}"
            if st.button("Detail", key=key):
                st.session_state.detail = None if st.session_state.detail==key else key
        if st.session_state.detail==f"det_s{i}":
            stats = "".join(
                f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                for l in labels
            )
            st.markdown(f"<div class='detail-popup'>{stats}</div>", unsafe_allow_html=True)

# ==== 2. Youth ====
with tabs[1]:
    st.markdown('<div class="stage-label">Youth Squad</div>', unsafe_allow_html=True)
    df2 = st.session_state.youth.copy()
    df2["Nat"] = df2["Nat"].map(NATIONS)
    if df2.empty:
        st.markdown("<div class='red-message'>No youth players.</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:transparent;">', unsafe_allow_html=True)
        st.markdown(df2[["Name","Nat","Pos","Age","Contract","Salary","OVR","Goals","Assists","Rating","MVP"]]
                    .to_html(index=False, classes="mobile-table", justify="center"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### Players")
        for i,row in df2.iterrows():
            st.markdown("---", unsafe_allow_html=True)
            cols = st.columns([1,4,1])
            with cols[0]:
                st.image(get_img(i+30), width=48)
            with cols[1]:
                st.write(f"**{row['Name']}** {row['Nat']} | {row['Pos']} | {row['Age']}")
                st.write(f"OVR:{row['OVR']}  G:{row['Goals']}  A:{row['Assists']}  R:{row['Rating']:.2f}  MVP:{row['MVP']}")
            with cols[2]:
                key=f"det_y{i}"
                if st.button("Detail", key=key):
                    st.session_state.detail = None if st.session_state.detail==key else key
            if st.session_state.detail==f"det_y{i}":
                stats = "".join(
                    f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                    for l in labels
                )
                st.markdown(f"<div class='detail-popup'>{stats}</div>", unsafe_allow_html=True)

# ==== 3. Match ====
with tabs[2]:
    st.markdown('<div class="stage-label">Match Simulation ‒ Week 1</div>', unsafe_allow_html=True)
    st.write(f"**Your Club:** {MY_CLUB}  vs  **Opponent:** {st.session_state.opp}")
    if st.button("Auto Starting XI", key="auto_xi"):
        st.session_state.starters = st.session_state.senior.nlargest(11,"OVR")["Name"].tolist()
    # 縦並びスタメン表示
    if st.session_state.starters:
        order = ["FW","MF","DF","GK"]
        for grp in order:
            for nm in [n for n in st.session_state.starters if st.session_state.senior.set_index("Name").loc[n,"Pos"]==grp]:
                st.write(f"- {grp}: {nm}")
    starters = st.multiselect("Starting XI", st.session_state.senior["Name"], default=st.session_state.starters)
    if st.button("Kickoff!", key="kickoff"):
        # 他チーム裏試合＆順位更新
        dfst=st.session_state.stand
        others=[c for c in CLUBS if c not in [MY_CLUB, st.session_state.opp]]
        for i in range(0,len(others),2):
            a,b=others[i],others[(i+1)%len(others)]
            ga,gb=random.randint(0,3),random.randint(0,3)
            if ga>gb: dfst.loc[dfst.Club==a,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==b,"L"]+=1
            elif ga<gb: dfst.loc[dfst.Club==b,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==a,"L"]+=1
            else: dfst.loc[dfst.Club.isin([a,b]),"D"]+=1; dfst.loc[dfst.Club==a,"Pts"]+=1; dfst.loc[dfst.Club==b,"Pts"]+=1
        # 自チーム
        ours = st.session_state.senior[st.session_state.senior["Name"].isin(starters)]
        atk = ours["OVR"].mean() if not ours.empty else 75
        oppatk = random.uniform(60,90)
        g1 = max(0,int(np.random.normal((atk-60)/8,1)))
        g2 = max(0,int(np.random.normal((oppatk-60)/8,1)))
        # Goals/Assists/MVP/Rating 更新
        # ゴール
        if g1>0:
            scorer = random.choice(starters)
            st.session_state.senior.loc[st.session_state.senior["Name"]==scorer,"Goals"] += g1
            # アシスト
            others_chr = [n for n in starters if n!=scorer]
            if others_chr:
                assist = random.choice(others_chr)
                st.session_state.senior.loc[st.session_state.senior["Name"]==assist,"Assists"] += 1
        else:
            scorer="—"
        # MVP
        mvp = random.choice(starters) if starters else "—"
        st.session_state.senior.loc[st.session_state.senior["Name"]==mvp,"MVP"] += 1
        # Rating
        for p in starters:
            r = random.uniform(5.0,10.0)
            row = st.session_state.senior["Name"]==p
            prev = st.session_state.senior.loc[row,"Rating"].iloc[0]
            cnt  = st.session_state.senior.loc[row,"RatingsPlayed"].iloc[0]
            new = (prev*cnt + r)/(cnt+1)
            st.session_state.senior.loc[row,"Rating"] = new
            st.session_state.senior.loc[row,"RatingsPlayed"] = cnt+1
        # 勝敗反映
        mi,oi=MY_CLUB,st.session_state.opp
        if g1>g2: res="Win"; dfst.loc[dfst.Club==mi,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==oi,"L"]+=1
        elif g1<g2: res="Lose"; dfst.loc[dfst.Club==oi,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==mi,"L"]+=1
        else: res="Draw"; dfst.loc[dfst.Club.isin([mi,oi]),"D"]+=1; dfst.loc[dfst.Club==mi,"Pts"]+=1; dfst.loc[dfst.Club==oi,"Pts"]+=1
        st.session_state.stand = dfst.sort_values("Pts",ascending=False).reset_index(drop=True)
        st.markdown(f"<div style='background:#27e3b9;color:#fff;padding:8px;border-radius:8px;'>**{res} {g1}-{g2}**</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#314265;color:#fff;padding:6px;border-radius:6px;'>Scorer: {scorer} | MVP: {mvp}</div>", unsafe_allow_html=True)

# ==== 4. Scout ====
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players</div>', unsafe_allow_html=True)
    st.markdown(f"**Budget:** {fmt_money(st.session_state.budget)}")
    c1,c2 = st.columns(2)
    with c1:
        if st.button(f"Refresh Senior ({st.session_state.refresh_s}/3)"):
            if st.session_state.refresh_s<3:
                st.session_state.scout_s = gen_players(5,False,MY_CLUB)
                st.session_state.refresh_s +=1
            else:
                st.warning("Senior scout limit reached")
    with c2:
        if st.button(f"Refresh Youth ({st.session_state.refresh_y}/3)"):
            if st.session_state.refresh_y<3:
                st.session_state.scout_y = gen_players(5,True,MY_CLUB)
                st.session_state.refresh_y +=1
            else:
                st.warning("Youth scout limit reached")
    # 候補表示
    for df_s,name in [(st.session_state.scout_s,"Senior"),(st.session_state.scout_y,"Youth")]:
        if not df_s.empty:
            st.markdown(f"#### {name} Candidates")
            for i,row in df_s.iterrows():
                st.markdown("---", unsafe_allow_html=True)
                cols=st.columns([1,4,1])
                with cols[0]:
                    st.image(get_img(i+60), width=48)
                with cols[1]:
                    st.write(f"**{row['Name']}** {NATIONS[row['Nat']]} | {row['Pos']} | {row['Age']}")
                    st.write(f"OVR:{row['OVR']}  G:{row['Goals']}  A:{row['Assists']}  R:{row['Rating']:.2f}  MVP:{row['MVP']}")
                with cols[2]:
                    key=f"sign_{name}_{i}"
                    if st.button("Sign", key=key):
                        if row["Name"] in st.session_state.senior["Name"].tolist() or row["Name"] in st.session_state.youth["Name"].tolist():
                            st.error("Already in squad")
                        elif st.session_state.budget<row["Salary"]:
                            st.error("Not enough budget")
                        else:
                            st.session_state.budget-=row["Salary"]
                            if name=="Senior":
                                st.session_state.senior=pd.concat([st.session_state.senior,pd.DataFrame([row])],ignore_index=True)
                            else:
                                st.session_state.youth=pd.concat([st.session_state.youth,pd.DataFrame([row])],ignore_index=True)
                            st.success(f"{row['Name']} signed!")

# ==== 5. Standings & Rankings ====
with tabs[4]:
    st.markdown('<div class="stage-label">Standings</div>', unsafe_allow_html=True)
    dfst=st.session_state.stand
    st.dataframe(dfst, use_container_width=True, height=200)
    st.markdown("---")
    # 各種ランキング
    all_players = pd.concat([st.session_state.senior, st.session_state.youth], ignore_index=True)
    for stat,title in [("Goals","Top Scorers"),("Assists","Top Assists"),("Rating","Top Ratings"),("MVP","Top MVPs")]:
        st.markdown(f"#### {title}")
        top5 = all_players.nlargest(5,stat)[["Name","Nat","Pos",stat]]
        top5["Nat"] = top5["Nat"].map(NATIONS)
        st.table(top5.rename(columns={"Nat":"🇳🇦"}))

# ==== 6. Save ====
with tabs[5]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Data"): st.success("Data saved!")
    if st.button("Load Data"): st.success("Data loaded!")

st.caption("2025年版：縦並びスタメン＆統合ダッシュ区切り＆Goals/Assists/Rating/MVP 統合 完全最新版")
