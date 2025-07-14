# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- ページ設定 ---
st.set_page_config(page_title="Soccer Club Manager", layout="wide")
random.seed(42)
np.random.seed(42)

# --- CSSカスタム ---
st.markdown("""
<style>
body, .stApp {background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; font-family:'Meiryo','Arial',sans-serif;}
h1,h2,h3,h4,h5,h6, .stTabs button {color:#fff!important;}
.stTabs [aria-selected="true"] {border-bottom:2px solid #f7df70!important;}
.stTabs button {background:transparent!important;}
.stButton>button, .stDownloadButton>button {background:#27e3b9!important; color:#202b41!important; font-weight:bold; border-radius:8px;}
.stButton>button:active {background:#ffee99!important;}
.player-card {background:#fff; border-radius:12px; padding:10px; margin:4px; color:#132346; position:relative;}
.detail-popup {position:absolute; top:100%; left:50%; transform:translateX(-50%); background:rgba(36,54,84,0.9); color:#fff; padding:8px; border-radius:8px; z-index:10;}
.mobile-table, .mobile-scroll {overflow-x:auto; white-space:nowrap;}
.mobile-table th, .mobile-table td {padding:4px 8px; color:#fff; border-bottom:1px solid rgba(255,255,255,0.1);}
.stDataFrame {background:rgba(20,30,50,0.7)!important; color:#fff!important;}
.red {color:#ff3a3a!important; font-weight:bold;}
.stage-label {background:rgba(0,0,0,0.3); color:#fff; padding:4px 8px; border-radius:6px; display:inline-block;}
</style>
""", unsafe_allow_html=True)

st.title("🏆 Soccer Club Manager")

# --- 定数 ---
CLUBS = ["Strive FC","Oxford Utd","Viking SC","Lazio Town","Munich Stars","Lille City","Sevilla Reds","Verona Blues"]
MY_CLUB = CLUBS[0]
NATIONS = {"UK":"🇬🇧","Germany":"🇩🇪","Italy":"🇮🇹","Spain":"🇪🇸","France":"🇫🇷","Brazil":"🇧🇷","Netherlands":"🇳🇱","Portugal":"🇵🇹"}

# --- 画像リスト & 名前プール ---
face_urls = [f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in range(10,60)]
surnames = ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker","White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris","Baker","Moore","Wright","Hill","Cooper","Edwards","Ward","King","Parker","Campbell"]
givens   = ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William","James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin","Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"]

def make_name(used):
    while True:
        n = f"{random.choice(givens)} {random.choice(surnames)}"
        if n not in used:
            used.add(n)
            return n

# --- 助手 ---
def fmt_money(v):
    if v>=1_000_000: return f"{v//1_000_000}m€"
    if v>=1_000:     return f"{v//1_000}k€"
    return f"{v}€"

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

def gen_players(n, youth=False):
    used = set()
    lst = []
    for i in range(n):
        name = make_name(used)
        stats = {l: random.randint(52 if youth else 60,82 if youth else 90) for l in labels}
        ovr = int(np.mean(list(stats.values())))
        lst.append({
            "Name": name,
            "Nat": random.choice(list(NATIONS.keys())),
            "Pos": random.choice(["GK","DF","MF","FW"]),
            "Age": random.randint(15 if youth else 18,18 if youth else 34),
            **stats,
            "Goals": 0, "Assists": 0, "Form": random.randint(60,90), "MVPs": 0,
            "Salary": random.randint(30_000 if youth else 120_000, 250_000 if youth else 1_200_000),
            "Contract": random.randint(1,2 if youth else 3),
            "OVR": ovr,
            "Youth": youth
        })
    return pd.DataFrame(lst)

# --- セッション初期化 ---
if "senior" not in st.session_state:
    st.session_state.senior = gen_players(30, youth=False)
if "youth" not in st.session_state:
    st.session_state.youth = gen_players(20, youth=True)
if "scout_s" not in st.session_state:
    st.session_state.scout_s = pd.DataFrame()
if "scout_y" not in st.session_state:
    st.session_state.scout_y = pd.DataFrame()
if "budget" not in st.session_state:
    st.session_state.budget = 3_000_000
if "stand" not in st.session_state:
    st.session_state.stand = pd.DataFrame({"Club":CLUBS,"W":0,"D":0,"L":0,"Pts":0})
if "week" not in st.session_state:
    st.session_state.week = 1
if "opp" not in st.session_state:
    st.session_state.opp = random.choice([c for c in CLUBS if c!=MY_CLUB])
if "detail" not in st.session_state:
    st.session_state.detail = None
if "starters" not in st.session_state:
    st.session_state.starters = []

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# ===== 1. Senior =====
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    df1 = st.session_state.senior.copy()
    df1["Nat"] = df1["Nat"].map(NATIONS)
    # 検索
    key = st.text_input("Search Name", "")
    if key: df1 = df1[df1["Name"].str.contains(key, case=False)]
    # 表示
    df_disp = df1[["Name","Nat","Pos","Age","Contract","Salary","OVR","Goals","Assists","Form","MVPs"]].copy()
    df_disp["Salary"] = df_disp["Salary"].map(fmt_money)
    st.dataframe(df_disp.style.set_table_styles([
        {"selector":"thead","props":[("background","rgba(20,30,50,0.9)"),("color","#fff")]},
        {"selector":"tbody td","props":[("background","rgba(20,30,50,0.6)"),("color","#fff")]},
    ]), use_container_width=True)

# ===== 2. Youth =====
with tabs[1]:
    st.markdown('<div class="stage-label">Youth Squad</div>', unsafe_allow_html=True)
    df2 = st.session_state.youth.copy()
    df2["Nat"] = df2["Nat"].map(NATIONS)
    key2 = st.text_input("Search Name (Youth)", "")
    if key2: df2 = df2[df2["Name"].str.contains(key2, case=False)]
    df_disp2 = df2[["Name","Nat","Pos","Age","Contract","Salary","OVR","Goals","Assists","Form","MVPs"]].copy()
    df_disp2["Salary"] = df_disp2["Salary"].map(fmt_money)
    st.dataframe(df_disp2.style.set_table_styles([
        {"selector":"thead","props":[("background","rgba(20,30,50,0.9)"),("color","#fff")]},
        {"selector":"tbody td","props":[("background","rgba(20,30,50,0.6)"),("color","#fff")]},
    ]), use_container_width=True)

# ===== 3. Match =====
with tabs[2]:
    st.markdown(f'<div class="stage-label">Match – Week {st.session_state.week}</div>', unsafe_allow_html=True)
    st.write(f"**Your Club:** {MY_CLUB}   vs   **Opponent:** {st.session_state.opp}")
    formation = st.selectbox("Choose Formation", ["4-4-2","4-3-3","3-5-2"])
    if st.button("Auto Starting XI"):
        # FW2 MF4 DF4 GK1 順に選ぶ
        df_s = st.session_state.senior
        star = []
        star += df_s[df_s.Pos=="FW"].nlargest(2,"OVR")["Name"].tolist()
        star += df_s[df_s.Pos=="MF"].nlargest(4,"OVR")["Name"].tolist()
        star += df_s[df_s.Pos=="DF"].nlargest(4,"OVR")["Name"].tolist()
        star += df_s[df_s.Pos=="GK"].nlargest(1,"OVR")["Name"].tolist()
        st.session_state.starters = star
    # 縦表示
    if st.session_state.starters:
        st.markdown("**Starting XI**")
        for nm in st.session_state.starters:
            p = st.session_state.senior[st.session_state.senior.Name==nm].iloc[0]
            st.markdown(f"- {p.Pos} {p.Name}  ⚽{p.Goals}  🎯{p.Assists}  🔥{p.Form}  🏅{p.MVPs}")

    if st.button("Kickoff!"):
        # 裏試合
        dfst = st.session_state.stand
        others = [c for c in CLUBS if c not in [MY_CLUB, st.session_state.opp]]
        for i in range(0,len(others),2):
            a,b = others[i], others[i+1]
            ga,gb = random.randint(0,3), random.randint(0,3)
            if ga>gb: dfst.loc[dfst.Club==a,["W","Pts"]] += [1,3]; dfst.loc[dfst.Club==b,"L"]+=1
            elif ga<gb: dfst.loc[dfst.Club==b,["W","Pts"]] += [1,3]; dfst.loc[dfst.Club==a,"L"]+=1
            else: dfst.loc[dfst.Club.isin([a,b]),"D"]+=1; dfst.loc[dfst.Club.isin([a,b]),"Pts"]+=1
        # 自チーム
        ours = st.session_state.senior[st.session_state.senior.Name.isin(st.session_state.starters)]
        atk = ours.Form.mean()
        opp_form = random.uniform(60,90)
        g1 = max(0,int(np.random.normal(atk/30,1)))
        g2 = max(0,int(np.random.normal(opp_form/30,1)))
        # 更新
        res = "Win" if g1>g2 else "Lose" if g1<g2 else "Draw"
        mi,oi = MY_CLUB, st.session_state.opp
        if res=="Win": dfst.loc[dfst.Club==mi,["W","Pts"]]+=[1,3]; dfst.loc[dfst.Club==oi,"L"]+=1
        elif res=="Lose": dfst.loc[dfst.Club==oi,["W","Pts"]]+=[1,3]; dfst.loc[dfst.Club==mi,"L"]+=1
        else: dfst.loc[dfst.Club.isin([mi,oi]),"D"]+=1; dfst.loc[dfst.Club.isin([mi,oi]),"Pts"]+=1
        st.session_state.stand = dfst.sort_values("Pts",ascending=False).reset_index(drop=True)
        # スタッツ増加
        scorer = ours.sample(1).Name.iloc[0] if g1>0 else None
        assist = ours.sample(1).Name.iloc[0] if g1>0 else None
        if scorer:
            st.session_state.senior.loc[st.session_state.senior.Name==scorer,"Goals"] += 1
            st.session_state.senior.loc[st.session_state.senior.Name==assist,"Assists"] += 1
        mvp = ours.nlargest(1,"OVR").Name.iloc[0]
        st.session_state.senior.loc[st.session_state.senior.Name==mvp,"MVPs"] += 1
        # OK 表示
        st.success(f"{res} ({g1}-{g2})")
        st.info(f"Goals: You {g1} – Opp {g2} | MVP: {mvp}")
        # 週進行
        if st.session_state.week < 14:
            st.session_state.week += 1
            st.session_state.opp = random.choice([c for c in CLUBS if c!=MY_CLUB])
        else:
            # シーズン終了
            topG = st.session_state.senior.nlargest(1,"Goals")[["Name","Goals"]]
            topA = st.session_state.senior.nlargest(1,"Assists")[["Name","Assists"]]
            topM = st.session_state.senior.nlargest(1,"MVPs")[["Name","MVPs"]]
            st.balloons()
            st.success("🏆 Season End!")
            st.write("**得点王**:", topG.to_dict(orient="records")[0])
            st.write("**アシスト王**:", topA.to_dict(orient="records")[0])
            st.write("**年間MVP**:", topM.to_dict(orient="records")[0])

# ===== 4. Scout =====
with tabs[3]:
    st.markdown('<div class="stage-label">Scout</div>', unsafe_allow_html=True)
    st.write(f"Budget: {fmt_money(st.session_state.budget)}")
    col1,col2 = st.columns(2)
    with col1:
        if st.button("Refresh Senior"):
            st.session_state.scout_s = gen_players(5, youth=False)
    with col2:
        if st.button("Refresh Youth"):
            st.session_state.scout_y = gen_players(5, youth=True)
    # Senior候補
    if not st.session_state.scout_s.empty:
        st.subheader("Senior Candidates")
        for i,row in st.session_state.scout_s.iterrows():
            cols = st.columns([1,4,1])
            with cols[0]: st.image(face_urls[i%len(face_urls)], width=48)
            with cols[1]:
                st.write(f"**{row.Name}** ({NATIONS[row.Nat]} {row.Pos}) Age:{row.Age}")
                st.write(f"OVR:{row.OVR}  ⚽{row.Goals}  🎯{row.Assists}  💶{fmt_money(row.Salary)}")
            with cols[2]:
                if st.button("Sign", key=f"s{i}"):
                    if row.Name in st.session_state.senior.Name.values:
                        st.error("Already in squad")
                    elif st.session_state.budget < row.Salary:
                        st.error("Not enough budget")
                    else:
                        st.session_state.budget -= row.Salary
                        st.session_state.senior = pd.concat([st.session_state.senior, pd.DataFrame([row])], ignore_index=True)
                        st.success("Signed!")
    # Youth候補
    if not st.session_state.scout_y.empty:
        st.subheader("Youth Candidates")
        for i,row in st.session_state.scout_y.iterrows():
            cols = st.columns([1,4,1])
            with cols[0]: st.image(face_urls[(i+10)%len(face_urls)], width=48)
            with cols[1]:
                st.write(f"**{row.Name}** ({NATIONS[row.Nat]} {row.Pos}) Age:{row.Age}")
                st.write(f"OVR:{row.OVR}  ⚽{row.Goals}  🎯{row.Assists}  💶{fmt_money(row.Salary)}")
            with cols[2]:
                if st.button("Sign", key=f"y{i}"):
                    if row.Name in st.session_state.youth.Name.values:
                        st.error("Already in youth")
                    elif st.session_state.budget < row.Salary:
                        st.error("Not enough budget")
                    else:
                        st.session_state.budget -= row.Salary
                        st.session_state.youth = pd.concat([st.session_state.youth, pd.DataFrame([row])], ignore_index=True)
                        st.success("Signed!")

# ===== 5. Standings =====
with tabs[4]:
    st.markdown('<div class="stage-label">Standings</div>', unsafe_allow_html=True)
    dfst = st.session_state.stand
    st.dataframe(dfst.style.set_properties(**{"background":"rgba(20,30,50,0.7)","color":"#fff"}), use_container_width=True)
    # Top5 Rankings
    st.subheader("📊 Top 5 Rankings")
    allp = pd.concat([st.session_state.senior, st.session_state.youth], ignore_index=True)
    cols = st.columns(4)
    with cols[0]:
        st.write("**⚽ Top Scorers**")
        st.table(allp.nlargest(5,"Goals")[["Name","Goals","Club"]].style.hide_index())
    with cols[1]:
        st.write("**🎯 Top Assists**")
        st.table(allp.nlargest(5,"Assists")[["Name","Assists","Club"]].style.hide_index())
    with cols[2]:
        st.write("**🏅 MVPs**")
        st.table(allp.nlargest(5,"MVPs")[["Name","MVPs","Club"]].style.hide_index())
    with cols[3]:
        st.write("**🔥 Form**")
        st.table(allp.nlargest(5,"Form")[["Name","Form","Club"]].style.hide_index())

# ===== 6. Save =====
with tabs[5]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Game"): st.success("Game saved!")
    if st.button("Load Game"): st.success("Game loaded!")
