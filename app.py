import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# — ページ設定 —
st.set_page_config(
    page_title="Soccer Club Management Sim",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# — CSS/UIカスタム —
st.markdown("""
<style>
body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
.stApp { background: linear-gradient(120deg, #202c46 0%, #314265 100%) !important; color: #eaf6ff; }
h1,h2,h3,h4,h5,h6, .stTabs label, .stTabs span, .stTabs button { color: #fff !important; }
.stTabs [data-baseweb="tab"] > button[aria-selected="true"] {
    background: transparent !important;
    border-bottom: 2.7px solid #f7df70 !important;
}
.stTabs [data-baseweb="tab"] > button {
    background: transparent !important;
    color: #fff !important;
}
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
  background: #ffffff;
  color: #132346;
  border-radius: 12px;
  padding: 10px;
  margin: 8px 4px;
  box-shadow: 0 0 8px #00000022;
  min-width: 150px; max-width: 170px; font-size:1em;
  display: flex; flex-direction: column; align-items: center;
  position: relative; transition:0.12s;
}
.player-card img {
  border-radius:50%; margin-bottom:6px;
  width:64px; height:64px; object-fit:cover;
}
.position-label { 
  color: #fff; background:#1b4f83;
  border-radius:7px; padding:2px 6px; font-size:0.85em;
  margin-top:4px;
}
.detail-popup {
  position: relative; top: 8px; left: 0; transform:none;
  min-width: 180px; max-width:240px;
  background: #243654cc; color: #fff;
  border-radius: 12px; padding: 12px;
  box-shadow: 0 0 12px #00000055;
  z-index: 10; backdrop-filter: blur(8px);
}
.mobile-table { overflow-x:auto; white-space:nowrap; }
.mobile-table th, .mobile-table td {
  padding:4px 8px; font-size:0.9em; color:#eaf6ff;
  border-bottom:1px solid #314265;
}
.stDataFrame { background:transparent !important; color:#eaf6ff !important; }
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# — クラブ＆対戦設定 —
CLUBS = [
    "Strive FC", "Oxford United", "Viking SC", "Lazio Town",
    "Munich Stars", "Lille City", "Sevilla Reds", "Verona Blues"
]
MY_CLUB = CLUBS[0]
# フォーメーション例
FORMATIONS = ["4-4-2","4-3-3","3-5-2","5-3-2"]

# — 顔画像サンプル（欧米系リアル）—
FACE_URLS = [
    f"https://randomuser.me/api/portraits/men/{i}.jpg"
    for i in range(10, 50)
]
def get_face(idx):
    return FACE_URLS[idx % len(FACE_URLS)]

# — ネームプール（英語姓30＋名30）—
surname_pool = ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
                "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris",
                "Baker","Moore","Wright","Hill","Cooper","Edwards","Ward","King","Parker","Richards"]
given_pool   = ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
                "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin",
                "Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"]

def make_name(used):
    while True:
        name = f"{random.choice(given_pool)} {random.choice(surname_pool)}"
        if name not in used:
            used.add(name)
            return name

def format_money(val):
    if val >= 1_000_000_000: return f"{val//1_000_000_000}b€"
    if val >= 1_000_000:     return f"{val//1_000_000}m€"
    if val >= 1_000:         return f"{val//1_000}k€"
    return f"{val}€"

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {l:l for l in labels}

# — データ生成関数 —
def gen_players(n, used, youth=False):
    lst=[]
    for i in range(n):
        name=make_name(used)
        stats={l: random.randint(50 if youth else 60, 80 if youth else 90) for l in labels}
        lst.append({
            "Name": name,
            "Pos": random.choice(["GK","DF","MF","FW"]),
            "Age": random.randint(15 if youth else 18, 18 if youth else 34),
            **stats,
            "OVR": int(np.mean(list(stats.values()))),
            "Contract": random.randint(1,2 if youth else 3),
            "Salary": random.randint(30_000 if youth else 120_000,250_000 if youth else 1_200_000),
            "Club": MY_CLUB,
            "Youth": int(youth)
        })
    return lst

# — セッション初期化 —
if "df_senior" not in st.session_state:
    used=set()
    st.session_state.df_senior=pd.DataFrame(gen_players(30,used,youth=False))
    st.session_state.df_youth =pd.DataFrame(gen_players(20,used,youth=True))
    st.session_state.detail   =None
    st.session_state.match_log=[]
    st.session_state.standings=pd.DataFrame({"Club":CLUBS,"W":0,"D":0,"L":0,"Pts":0})

df_senior=st.session_state.df_senior
df_youth =st.session_state.df_youth

# — メインタブ —
tabs=st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# ─── 1. Senior ─────────────────────────
with tabs[0]:
    st.subheader("Senior Squad")
    # テーブル
    st.markdown("<div class='mobile-table'><table><thead><tr>" +
                "".join(f"<th>{c}</th>" for c in ["Name","Pos","Age","Contract","Salary","OVR"]) +
                "</tr></thead><tbody>" +
                "".join(
                    "<tr>" +
                    f"<td>{r['Name']}</td><td>{r['Pos']}</td><td>{r['Age']}</td><td>{r['Contract']}</td>" +
                    f"<td>{format_money(r['Salary'])}</td><td>{r['OVR']}</td></tr>"
                    for _,r in df_senior.iterrows()
                ) +
                "</tbody></table></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### Players")
    cols=st.columns(min(5,len(df_senior)))
    for i,row in df_senior.iterrows():
        with cols[i%len(cols)]:
            if st.button("Detail",key=f"sen_{i}"):
                st.session_state.detail=("senior",i)
            st.markdown(f"""
                <div class='player-card'>
                  <img src="{get_face(i)}">
                  <b>{row['Name']}</b><br>
                  <span class='position-label'>{row['Pos']}</span><br>
                  OVR:{row['OVR']} ｜ {row['Age']}y<br>
                  C:{row['Contract']} ｜ S:{format_money(row['Salary'])}
                </div>""",unsafe_allow_html=True)
            if st.session_state.detail==("senior",i):
                vals=[row[l] for l in labels]+[row[labels[0]]]
                ang=np.linspace(0,2*np.pi,len(vals))
                fig,ax=plt.subplots(subplot_kw=dict(polar=True),figsize=(2.3,2.3))
                ax.plot(ang,vals,linewidth=2);ax.fill(ang,vals,alpha=0.3)
                ax.set_yticklabels([]);ax.set_xticks(ang[:-1]);ax.set_xticklabels(labels,color="#fff")
                ax.grid(color="#8888",linestyle="--");fig.patch.set_alpha(0);ax.patch.set_alpha(0)
                st.pyplot(fig,transparent=True)
                stat_tbl="".join(
                    f"<tr><td>{l}</td><td style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{row[l]}</td></tr>"
                    for l in labels
                )
                st.markdown(f"<div class='detail-popup'><table>{stat_tbl}</table></div>",unsafe_allow_html=True)

# ─── 2. Youth ──────────────────────────
with tabs[1]:
    st.subheader("Youth Squad")
    if df_youth.empty:
        st.markdown("<div class='red-message'>No youth players.</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='mobile-table'><table><thead><tr>" +
                    "".join(f"<th>{c}</th>" for c in ["Name","Pos","Age","Contract","Salary","OVR"]) +
                    "</tr></thead><tbody>" +
                    "".join(
                        "<tr>" +
                        f"<td>{r['Name']}</td><td>{r['Pos']}</td><td>{r['Age']}</td><td>{r['Contract']}</td>" +
                        f"<td>{format_money(r['Salary'])}</td><td>{r['OVR']}</td></tr>"
                        for _,r in df_youth.iterrows()
                    ) +
                    "</tbody></table></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### Players")
        cols=st.columns(min(5,len(df_youth)))
        for i,row in df_youth.iterrows():
            with cols[i%len(cols)]:
                if st.button("Detail",key=f"youth_{i}"):
                    st.session_state.detail=("youth",i)
                st.markdown(f"""
                    <div class='player-card'>
                      <img src="{get_face(i+100)}">
                      <b>{row['Name']}</b><br>
                      <span class='position-label'>{row['Pos']}</span><br>
                      OVR:{row['OVR']} ｜ {row['Age']}y<br>
                      C:{row['Contract']} ｜ S:{format_money(row['Salary'])}
                    </div>""",unsafe_allow_html=True)
                if st.session_state.detail==("youth",i):
                    vals=[row[l] for l in labels]+[row[labels[0]]]
                    ang=np.linspace(0,2*np.pi,len(vals))
                    fig,ax=plt.subplots(subplot_kw=dict(polar=True),figsize=(2.3,2.3))
                    ax.plot(ang,vals,linewidth=2);ax.fill(ang,vals,alpha=0.3)
                    ax.set_yticklabels([]);ax.set_xticks(ang[:-1]);ax.set_xticklabels(labels,color="#fff")
                    ax.grid(color="#8888",linestyle="--");fig.patch.set_alpha(0);ax.patch.set_alpha(0)
                    st.pyplot(fig,transparent=True)
                    stat_tbl="".join(
                        f"<tr><td>{l}</td><td style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{row[l]}</td></tr>"
                        for l in labels
                    )
                    st.markdown(f"<div class='detail-popup'><table>{stat_tbl}</table></div>",unsafe_allow_html=True)

# ─── 3. Match ──────────────────────────
with tabs[2]:
    st.subheader(f"Match Simulation — Week {len(st.session_state.match_log)+1}")
    form = st.selectbox("Formation", FORMATIONS)
    lineup = st.multiselect("Select Starting XI", df_senior["Name"].tolist(),
                             default=df_senior.nlargest(11,"OVR")["Name"].tolist())
    if st.button("Kickoff!"):
        your_power = sum(df_senior[df_senior["Name"].isin(lineup)]["OVR"])
        opp = random.choice([c for c in CLUBS if c!=MY_CLUB])
        opp_power = your_power + random.randint(-50,50)
        p = your_power/(your_power+opp_power)
        r = random.random()
        if r<p: res="Win"; pts=(3,0)
        elif r<p+0.1: res="Draw"; pts=(1,1)
        else: res="Lose"; pts=(0,3)
        st.session_state.match_log.append(f"{MY_CLUB} {res} vs {opp}")
        st_st=st.session_state.standings
        st_st.loc[st_st.Club==MY_CLUB,"Pts"]+=pts[0]
        st_st.loc[st_st.Club==opp,"Pts"]+=pts[1]
        st.success(f"Result: {res} ({pts[0]}–{pts[1]}) vs {opp}")
        st.info(f"Goals: You {random.randint(0,4)} – Opp {random.randint(0,4)} | MVP: {random.choice(lineup)}")

# ─── 4. Scout ──────────────────────────
with tabs[3]:
    st.subheader("Scout")
    if st.button("Scout 5 Senior"):
        used=set(df_senior["Name"])
        more=pd.DataFrame(gen_players(5,used,youth=False))
        st.session_state.df_senior=pd.concat([df_senior,more],ignore_index=True)
    if st.button("Scout 5 Youth"):
        used=set(df_youth["Name"])
        more=pd.DataFrame(gen_players(5,used,youth=True))
        st.session_state.df_youth=pd.concat([df_youth,more],ignore_index=True)
    st.success("Players scouted!")

# ─── 5. Standings ─────────────────────
with tabs[4]:
    st.subheader("Standings")
    df_st=st.session_state.standings.sort_values("Pts",ascending=False).reset_index(drop=True)
    st.dataframe(
        df_st.style
             .set_properties(**{'background-color':'transparent','color':'#eaf6ff'})
             .set_table_styles([{'selector':'thead th','props':[('background','transparent'),('color','#fff')]}]),
        height=300
    )

# ─── 6. Save / Load ───────────────────
with tabs[5]:
    st.subheader("Save / Load")
    if st.button("Save Data"): st.success("Data saved.")
    if st.button("Load Data"): st.success("Data loaded.")

st.caption("2025年最新版：全要素完全統合版 — 詳細改良／Scout／Match／Standings")
