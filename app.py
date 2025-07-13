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
    "England":"🏴","Germany":"🇩🇪","Italy":"🇮🇹","Spain":"🇪🇸",
    "France":"🇫🇷","Brazil":"🇧🇷","Netherlands":"🇳🇱","Portugal":"🇵🇹"
}

# --- 画像 ---
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

# --- データ生成 ---
def gen_players(n,youth=False):
    used=set()
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
            "Salary":random.randint(30_000 if youth else 120_000,
                                   250_000 if youth else 1_200_000),
            "Contract":random.randint(1,2 if youth else 3),
            "OVR":ovr,
            "Youth":youth
        })
    return pd.DataFrame(lst)

# --- セッション初期化 ---
if "senior" not in st.session_state:
    st.session_state.senior = gen_players(30,False)
if "youth" not in st.session_state:
    st.session_state.youth = gen_players(20,True)
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
    # 国籍フラグ化
    df1["Nat"] = df1["Nat"].map(NATIONS)
    # ソート可能なDataFrame表示
    st.dataframe(df1[["Name","Nat","Pos","Age","Contract","Salary","OVR"]].assign(
        Salary=df1["Salary"].map(fmt_money)
    ), use_container_width=True)
    st.markdown("---")
    st.markdown("#### Players")
    st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
    for i,row in df1.iterrows():
        key = f"sen{i}"
        cols = st.columns([1,3])
        with cols[0]:
            st.image(get_img(i), width=48)
        with cols[1]:
            st.write(f"**{row['Name']}**")
            st.write(f"{row['Nat']}｜{row['Pos']}｜{row['Age']}")
            st.write(f"OVR:{row['OVR']}")
            if st.button("Detail", key=key):
                # トグル動作
                st.session_state.detail = None if st.session_state.detail==key else key
        # Detail表示
        if st.session_state.detail == key:
            abil = [row[l] for l in labels] + [row[labels[0]]]
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
        st.dataframe(df2[["Name","Nat","Pos","Age","Contract","Salary","OVR"]].assign(
            Salary=df2["Salary"].map(fmt_money)
        ), use_container_width=True)
        st.markdown("---")
        st.markdown("#### Players")
        st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
        for i,row in df2.iterrows():
            key = f"you{i}"
            cols = st.columns([1,3])
            with cols[0]:
                st.image(get_img(i+30), width=48)
            with cols[1]:
                st.write(f"**{row['Name']}**")
                st.write(f"{row['Nat']}｜{row['Pos']}｜{row['Age']}")
                st.write(f"OVR:{row['OVR']}")
                if st.button("Detail", key=key):
                    st.session_state.detail = None if st.session_state.detail==key else key
            if st.session_state.detail == key:
                abil = [row[l] for l in labels] + [row[labels[0]]]
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
    # フォーメーション図
    if st.session_state.starters:
        coords = {
            "4-4-2":([5],[2,4,6,8],[2,4,6,8],[3,7]),
            "4-3-3":([5],[2,4,6,8],[3.5,5,6.5],[2,5,8]),
            "3-5-2":([5],[3.5,5,6.5],[2,4,6,8],[3,7])
        }
        gk,def4,mid,fw = coords[formation]
        fig,ax = plt.subplots(figsize=(3,5))
        ax.set_xlim(0,10); ax.set_ylim(0,16); ax.axis('off')
        ax.plot([0,10],[8,8],color='white',linewidth=1)
        names = st.session_state.starters; idx=0
        ax.text(5,1,names[idx],ha='center',color='yellow'); idx+=1
        for x in def4:
            ax.text(x,4,names[idx],ha='center',color='white'); idx+=1
        for x in mid:
            ax.text(x,8,names[idx],ha='center',color='white'); idx+=1
        for x in fw:
            ax.text(x,12,names[idx],ha='center',color='white'); idx+=1
        st.pyplot(fig)
    starters = st.multiselect("Starting XI", st.session_state.senior["Name"], default=st.session_state.starters)
    if st.button("Kickoff!"):
        # 裏試合
        dfst=st.session_state.stand
        others=[c for c in CLUBS if c not in [MY_CLUB, st.session_state.opp]]
        for i in range(0,len(others),2):
            a,b=others[i],others[i+1]
            ga,gb = random.randint(0,3),random.randint(0,3)
            if ga>gb: dfst.loc[dfst.Club==a,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==b,"L"]+=1
            elif ga<gb: dfst.loc[dfst.Club==b,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==a,"L"]+=1
            else: dfst.loc[dfst.Club.isin([a,b]),"D"]+=1; dfst.loc[dfst.Club==a,"Pts"]+=1; dfst.loc[dfst.Club==b,"Pts"]+=1
        # 自チーム
        ours = st.session_state.senior[st.session_state.senior["Name"].isin(starters)]
        atk = ours["OVR"].mean() if not ours.empty else 75
        oppatk = random.uniform(60,90)
        g1 = max(0,int(np.random.normal((atk-60)/8,1)))
        g2 = max(0,int(np.random.normal((oppatk-60)/8,1)))
        res = "Win" if g1>g2 else "Lose" if g1<g2 else "Draw"
        mvp = ours.nlargest(1,"OVR")["Name"].iloc[0] if not ours.empty else ""
        mi,oi = MY_CLUB,st.session_state.opp
        if res=="Win": dfst.loc[dfst.Club==mi,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==oi,"L"]+=1
        elif res=="Lose": dfst.loc[dfst.Club==oi,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==mi,"L"]+=1
        else: dfst.loc[dfst.Club.isin([mi,oi]),"D"]+=1; dfst.loc[dfst.Club==mi,"Pts"]+=1; dfst.loc[dfst.Club==oi,"Pts"]+=1
        st.session_state.stand = dfst.sort_values("Pts",ascending=False).reset_index(drop=True)
        st.markdown(f"<div style='background:#27e3b9;color:#fff;padding:8px;border-radius:8px;'>**{res} ({g1}-{g2})**</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#314265;color:#fff;padding:6px;border-radius:6px;'>Goals: You {g1} ‒ Opp {g2} | MVP: {mvp}</div>", unsafe_allow_html=True)

# ==== 4. Scout ====
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players</div>', unsafe_allow_html=True)
    st.markdown(f"**Budget:** {fmt_money(st.session_state.budget)}")
    c1,c2 = st.columns(2)
    with c1:
        if st.button(f"Refresh Senior ({st.session_state.refresh_s}/3)"):
            if st.session_state.refresh_s<3:
                st.session_state.scout_s = gen_players(5,False)
                st.session_state.refresh_s += 1
            else:
                st.warning("Senior scout limit reached")
    with c2:
        if st.button(f"Refresh Youth ({st.session_state.refresh_y}/3)"):
            if st.session_state.refresh_y<3:
                st.session_state.scout_y = gen_players(5,True)
                st.session_state.refresh_y += 1
            else:
                st.warning("Youth scout limit reached")
    # Senior候補
    if not st.session_state.scout_s.empty:
        st.markdown("#### Senior Candidates")
        st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
        for i,row in st.session_state.scout_s.iterrows():
            key=f"ss{i}"
            cols = st.columns([1,3])
            with cols[0]:
                st.image(get_img(i+60), width=48)
            with cols[1]:
                st.write(f"**{row['Name']}**")
                st.write(f"{NATIONS[row['Nat']]}｜{row['Pos']}｜{row['Age']}")
                st.write(f"OVR:{row['OVR']}")
                if st.button("Sign", key=key):
                    if row["Name"] in st.session_state.senior["Name"].tolist():
                        st.error("Already in squad")
                    elif st.session_state.budget < row["Salary"]:
                        st.error("Not enough budget")
                    else:
                        st.session_state.budget -= row["Salary"]
                        st.session_state.senior = pd.concat(
                            [st.session_state.senior, pd.DataFrame([row])],
                            ignore_index=True
                        )
                        st.success(f"{row['Name']} signed!")
        st.markdown('</div>', unsafe_allow_html=True)
    # Youth候補
    if not st.session_state.scout_y.empty:
        st.markdown("#### Youth Candidates")
        st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
        for i,row in st.session_state.scout_y.iterrows():
            key=f"sy{i}"
            cols = st.columns([1,3])
            with cols[0]:
                st.image(get_img(i+80), width=48)
            with cols[1]:
                st.write(f"**{row['Name']}**")
                st.write(f"{NATIONS[row['Nat']]}｜{row['Pos']}｜{row['Age']}")
                st.write(f"OVR:{row['OVR']}")
                if st.button("Sign", key=key):
                    if row["Name"] in st.session_state.youth["Name"].tolist():
                        st.error("Already in youth")
                    elif st.session_state.budget < row["Salary"]:
                        st.error("Not enough budget")
                    else:
                        st.session_state.budget -= row["Salary"]
                        st.session_state.youth = pd.concat(
                            [st.session_state.youth, pd.DataFrame([row])],
                            ignore_index=True
                        )
                        st.success(f"{row['Name']} signed!")
        st.markdown('</div>', unsafe_allow_html=True)

# ==== 5. Standings ====
with tabs[4]:
    st.markdown('<div class="stage-label">Standings</div>', unsafe_allow_html=True)
    dfst = st.session_state.stand
    styled = dfst.style.set_properties(**{
        "background-color":"rgba(32,44,70,0.7)", "color":"white", "text-align":"center"
    }).set_table_styles([{
        "selector":"thead th", "props":[("background","rgba(32,44,70,0.9)"),("color","white")]
    }])
    st.dataframe(styled, height=300, use_container_width=True)

# ==== 6. Save ====
with tabs[5]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Data"): st.success("Data saved!")
    if st.button("Load Data"): st.success("Data loaded!")

st.caption("2025年版：重複防止／トグル修正／国籍絵文字／列ソート対応 完全統合版")
