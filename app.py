# app.py
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
/* タブ */
.stTabs [data-baseweb="tab"] > button { color:#fff!important; background:transparent!important;}
.stTabs [data-baseweb="tab"] > button[aria-selected="true"] { border-bottom:2px solid #f7df70!important;}
/* ボタン */
.stButton>button { background:#27e3b9!important; color:#202b41!important; font-weight:bold; border-radius:11px; }
.stButton>button:active { background:#ffee99!important; }
/* アラート */
.red-message { color:#ff3a3a; font-weight:bold; font-size:1.1em;}
/* テーブル */
.mobile-table { overflow-x:auto; white-space:nowrap; }
.mobile-table th, .mobile-table td { padding:4px 10px; font-size:0.95em; border-bottom:1px solid #243255; }
.stDataFrame { background: #202c46cc!important; color:#fff!important; }
/* プレイヤーカード */
.player-card { background:#fff; color:#132346; border-radius:12px; padding:10px; margin:8px; text-align:center;
    box-shadow:0 0 10px #0003; position:relative;}
.player-card img { border-radius:50%; margin-bottom:6px; width:64px; height:64px; object-fit:cover; }
.player-card .pos { display:inline-block; background:#1b4f83; color:#fff; padding:2px 6px; border-radius:6px; margin:4px 0; }
/* Detail ポップアップ */
.detail-popup { background: rgba(36,54,84,0.8); color:#fff; padding:12px; border-radius:8px;
    position:relative; margin-top:6px; backdrop-filter:blur(8px); }
/* ピッチ */
.pitch { background: #228B22; position: relative; width:100%; padding-top:56%; margin:8px 0; }
.pitch svg { position:absolute; top:0; left:0; width:100%; height:100%; }
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- 定数・設定 ---
CLUBS = ["Strive FC","Oxford Utd","Viking SC","Lazio Town","Munich Stars","Lille City","Sevilla Reds","Verona Blues"]
MY_CLUB = CLUBS[0]
FORMATION_MAP = {
    "4-4-2":[[1,4,5,2,3],[6,7,8,9],[10,11]],
    "4-3-3":[[1,4,5,2,3],[6,7,8],[9,10,11]],
    "3-5-2":[[1,3,2],[4,5,6,7,8],[9,10],[11]],
}
face_imgs=[f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in range(10,50)]
def get_img(i): return face_imgs[i%len(face_imgs)]

# --- ネームプール＋国籍絵文字 ---
surname=["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker","White","Hall","Green","Wood","Martin","Lewis","Scott","Clark","Harris","Baker","Moore","Wright","Hill","Cooper","Edwards","Turner","Parker","Adams","Campbell","Mitchell"]
given=["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William","James","Henry","Leo","Lucas","Ethan","Mason","Samuel","Benjamin","Dylan","Joseph","Logan","Alexander","Alfie","Freddie","Oscar","Ryan","Liam","Connor","Aiden"]
nats=[("🇬🇧","England"),("🇩🇪","Germany"),("🇪🇸","Spain"),("🇫🇷","France"),("🇮🇹","Italy"),("🇧🇷","Brazil"),("🇪🇺","Europe")]
def make_name(used):
    while True:
        nm=f"{random.choice(given)} {random.choice(surname)}"
        if nm not in used:
            used.add(nm); return nm

# --- データ生成関数 ---
labels=['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
def gen_players(n, youth=False, used=None):
    df=[]
    if used is None: used=set()
    for i in range(n):
        nm=make_name(used)
        nat_emoji,_ = random.choice(nats)
        pos=random.choice(["GK","DF","MF","FW"])
        # ←ここを修正
        if youth:
            age = random.randint(15,18)
        else:
            age = random.randint(18,34)
        vals={l:random.randint(50 + (0 if youth else 10),90) for l in labels}
        ovr=int(np.mean(list(vals.values())))
        ctr=random.randint(1,2 if youth else 3)
        sal=random.randint(30_000 if youth else 120_000,250_000 if youth else 1_200_000)
        row = {"Name":nm, "Nat":nat_emoji, "Pos":pos, "Age":age,
               "Contract":ctr, "Salary":sal, "OVR":ovr, "Youth":int(youth)}
        row.update(vals)
        df.append(row)
    return pd.DataFrame(df)

# --- セッションステート初期化 ---
if "senior_df" not in st.session_state:
    used_names=set()
    st.session_state.senior_df = gen_players(30, False, used_names)
    st.session_state.youth_df  = gen_players(20, True, used_names)
    st.session_state.budget     = 1_000_000
    st.session_state.scout_cnt  = 0
    st.session_state.match_wk   = 1
    st.session_state.standings  = pd.DataFrame({
        "Club":CLUBS,"W":[0]*8,"D":[0]*8,"L":[0]*8,"Pts":[0]*8
    })
    st.session_state.det_s = None
    st.session_state.det_y = None

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# 1. Senior
with tabs[0]:
    st.subheader("Senior Squad")
    st.dataframe(st.session_state.senior_df, use_container_width=True)
    st.markdown("#### Players")
    cols = st.columns(3)
    for idx,row in st.session_state.senior_df.reset_index().iterrows():
        c = cols[idx%3]
        with c:
            st.markdown(f"""
                <div class="player-card">
                    <img src="{get_img(idx)}">
                    <b>{row['Name']} {row['Nat']}</b><br>
                    <span class="pos">{row['Pos']}</span> / {row['Age']}<br>
                    Contract:{row['Contract']} | Salary:{row['Salary']:,}€<br>
                    <b>OVR:{row['OVR']}</b>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Detail", key=f"s_det_{idx}"):
                st.session_state.det_s = None if st.session_state.det_s==idx else idx
            if st.session_state.det_s == idx:
                vals = [row[l] for l in labels]
                angles = np.linspace(0,2*np.pi,len(labels)+1)
                vals2 = vals+[vals[0]]
                fig,ax = plt.subplots(subplot_kw=dict(polar=True),figsize=(3,3))
                ax.plot(angles,vals2,linewidth=2,linestyle='solid')
                ax.fill(angles,vals2,alpha=0.3)
                ax.set_yticklabels([]);ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels, color='w');ax.grid(color="#3ad6c9",alpha=0.2)
                fig.patch.set_alpha(0);ax.patch.set_alpha(0)
                st.pyplot(fig)
                st.markdown("<div class='detail-popup'>",unsafe_allow_html=True)
                for l,v in zip(labels,vals):
                    col="#1aacef"
                    if v>=90: col="#20e660"
                    elif v>=75: col="#ffe600"
                    st.markdown(f"<span style='color:{col}'>{l}: {v}</span><br>",unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)

# 2. Youth
with tabs[1]:
    st.subheader("Youth Squad")
    if st.session_state.youth_df.empty:
        st.markdown("<div class='red-message'>No youth players.</div>",unsafe_allow_html=True)
    else:
        st.dataframe(st.session_state.youth_df, use_container_width=True)

# 3. Match
with tabs[2]:
    st.subheader(f"Match Simulation – Week {st.session_state.match_wk}")
    form = st.selectbox("Choose Formation", list(FORMATION_MAP.keys()))
    if st.button("Auto Starting XI"):
        opp = random.choice([c for c in CLUBS if c!=MY_CLUB])
        s, o = sorted([random.randint(0,4),random.randint(0,4)])
        df = st.session_state.standings
        im = df.index[df["Club"]==MY_CLUB][0]
        io = df.index[df["Club"]==opp][0]
        if s>o:
            df.at[im,"W"]+=1; df.at[im,"Pts"]+=3; df.at[io,"L"]+=1; res="Win"
        elif s<o:
            df.at[io,"W"]+=1; df.at[io,"Pts"]+=3; df.at[im,"L"]+=1; res="Lose"
        else:
            df.at[im,"D"]+=1; df.at[im,"Pts"]+=1; df.at[io,"D"]+=1; df.at[io,"Pts"]+=1; res="Draw"
        st.success(f"Result: {res} ({s}-{o}) vs {opp}")
        scorer = random.choice(st.session_state.senior_df["Name"])
        mvp = random.choice(st.session_state.senior_df["Name"])
        st.info(f"Scorer: {scorer} | MVP: {mvp}")
        st.session_state.match_wk += 1
    st.markdown("#### Formation")
    st.markdown(f"""
    <div class="pitch">
      <svg viewBox="0 0 120 80" preserveAspectRatio="none">
        <rect width="120" height="80" fill="#228B22"/>
        <line x1="60" y1="0" x2="60" y2="80" stroke="#fff"/>
        <circle cx="60" cy="40" r="10" fill="none" stroke="#fff"/>
        {"".join([
            f'<circle cx="{20+80*(p%5)/4}" cy="{10+60*(i+1)/(len(FORMATION_MAP[form])+1)}" r="3" fill="#0055ff"/>'
            for i,row in enumerate(FORMATION_MAP[form])
            for p in row
        ])}
      </svg>
    </div>
    """,unsafe_allow_html=True)

# 4. Scout
with tabs[3]:
    st.subheader("Scout Players")
    st.markdown(f"**Budget:** {st.session_state.budget:,}€")
    c1,c2=st.columns(2)
    if c1.button("Scout Senior") and st.session_state.scout_cnt<3:
        new = gen_players(1,False)[0]
        df = st.session_state.senior_df
        if new["Name"] not in df["Name"].values:
            st.session_state.senior_df = pd.concat([df,pd.DataFrame([new])],ignore_index=True)
            st.session_state.budget -= new["Salary"]
            st.session_state.scout_cnt += 1
            st.success(f"Signed {new['Name']}!")
        else: st.warning("Already in squad.")
    if c2.button("Scout Youth") and st.session_state.scout_cnt<3:
        new = gen_players(1,True)[0]
        df = st.session_state.youth_df
        if new["Name"] not in df["Name"].values:
            st.session_state.youth_df = pd.concat([df,pd.DataFrame([new])],ignore_index=True)
            st.session_state.budget -= new["Salary"]
            st.session_state.scout_cnt += 1
            st.success(f"Signed Youth {new['Name']}!")
        else: st.warning("Already in youth.")
    if st.session_state.scout_cnt>=3:
        st.markdown("<div class='red-message'>Scout limit reached this week.</div>",unsafe_allow_html=True)

# 5. Standings
with tabs[4]:
    st.subheader("League Standings")
    df = st.session_state.standings.sort_values("Pts",ascending=False).reset_index(drop=True)
    df.index += 1
    styled = df.style.set_properties(**{"background-color":"#192844","color":"#fff"}) \
                    .set_table_styles([{"selector":"thead","props":[("background","#243255"),("color","#ffe900")]}])
    st.dataframe(styled, use_container_width=True)

# 6. Save
with tabs[5]:
    st.subheader("Save / Load")
    if st.button("Save Data"): st.success("Data saved (仮).")
    if st.button("Load Data"): st.success("Data loaded (仮).")

st.caption("2025最新版：SyntaxError修正＋全要素完全統合版 🎉")
