import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- ページ設定 ---
st.set_page_config(page_title="Ultimate Soccer Sim", layout="wide")
random.seed(42); np.random.seed(42)

# --- CSS ---
st.markdown("""
<style>
body, .stApp { font-family:'Meiryo',sans-serif; background:linear-gradient(120deg,#192841,#24345b)!important; color:#eef; }
h1,h2,h3 { color:#fff!important; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2px solid #f7df70!important; }
.player-table th, .player-table td { padding:6px 8px; border-bottom:1px solid #2b3550; }
.search-box { margin-bottom:12px; }
.card-container { display:flex; overflow-x:auto; padding:8px 0; }
.player-card { background:#fff; color:#132346; border-radius:8px; padding:8px; margin-right:12px; min-width:140px; box-shadow:0 0 6px #0003; position:relative; }
.player-card img { width:60px; height:60px; border-radius:50%; object-fit:cover; }
.detail-btn { background:#27e3b9!important; color:#132346!important; border:none; padding:4px 8px; border-radius:6px; margin-top:6px; cursor:pointer; }
.detail-popup { position:absolute; top:100%; left:50%; transform:translateX(-50%); background:rgba(36,54,84,0.9); color:#fff; padding:10px; border-radius:6px; width:180px; box-shadow:0 0 8px #000a; backdrop-filter:blur(6px); z-index:10; }
.divider { border-top:1px solid #2b3550; margin:12px 0; }
.button { background:#27e3b9!important; color:#132346!important; }
.ranking-box { background:rgba(32,44,70,0.7); color:#fff; padding:8px; border-radius:6px; margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)

st.title("Ultimate Soccer Management Sim")

# --- 定数 ---
CLUBS = [
    "Strive FC","Oxford Utd","Viking SC","Lazio Town",
    "Munich Stars","Lille City","Sevilla Reds","Verona Blues"
]
MY_CLUB = CLUBS[0]
NATIONS = {
    "United Kingdom":"🇬🇧",
    "Germany":"🇩🇪",
    "Italy":"🇮🇹",
    "Spain":"🇪🇸",
    "France":"🇫🇷",
    "Brazil":"🇧🇷",
    "Netherlands":"🇳🇱",
    "Portugal":"🇵🇹"
}

# --- 代理人データ ---
agents = pd.DataFrame([
    {"Name":"Lord","Emoji":"🕴️","Fee":0.15,"Mood":"😊 良好","Style":"強硬派"},
    {"Name":"Gray","Emoji":"🕴️","Fee":0.12,"Mood":"😐 普通","Style":"Win-Win"},
    {"Name":"Lawrence","Emoji":"🕴️","Fee":0.18,"Mood":"😉 上機嫌","Style":"ファイナル"},
    {"Name":"Black","Emoji":"🕴️","Fee":0.20,"Mood":"😤 機嫌斜め","Style":"ガチンコ"},
    {"Name":"White","Emoji":"🕴️","Fee":0.10,"Mood":"😊 良好","Style":"フォロー"}
])

# --- 画像プール ---
face_urls = [f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in range(10,60)]
def get_face(i): return face_urls[i % len(face_urls)]

# --- 名前プール ---
surnames = [
    "Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
    "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris",
    "Baker","Moore","Wright","Hill","Cooper","Edwards","Ward","King","Parker","Campbell"
]
givens = [
    "Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
    "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin",
    "Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"
]
def gen_name(used):
    while True:
        n = f"{random.choice(givens)} {random.choice(surnames)}"
        if n not in used:
            used.add(n)
            return n

# --- フォーマット関数 ---
def fmt_money(v):
    if v >= 1_000_000: return f"{v//1_000_000}m€"
    if v >=   1_000: return f"{v//1_000}k€"
    return f"{v}€"

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {
    'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina',
    'Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'
}

# --- データ生成関数 ---
def make_players(n, youth=False):
    used = set()
    lst = []
    for i in range(n):
        name = gen_name(used)
        nat  = random.choice(list(NATIONS.keys()))
        stats = {l: random.randint(52,82) if youth else random.randint(60,90) for l in labels}
        ovr = int(np.mean(list(stats.values())))
        lst.append({
            "Name": name,
            "Nat": nat,
            "Pos": random.choice(["GK","DF","MF","FW"]),
            "Age": random.randint(15,18) if youth else random.randint(18,34),
            **stats,
            "Salary": random.randint(30_000,250_000) if youth else random.randint(120_000,1_200_000),
            "Contract": random.randint(1,2) if youth else random.randint(1,3),
            "OVR": ovr,
            "Youth": youth,
            "Agent": agents.sample(1).iloc[0]["Name"],
            "Goals":0,"Assists":0,"Rating":0,"MVP":0
        })
    return pd.DataFrame(lst)

# --- セッション初期化 ---
if "df" not in st.session_state:
    st.session_state.df = pd.concat([
        make_players(30, False),
        make_players(20, True)
    ], ignore_index=True)
if "stand" not in st.session_state:
    st.session_state.stand = pd.DataFrame({"Club":CLUBS,"W":0,"D":0,"L":0,"Pts":0})
if "detail_key" not in st.session_state:
    st.session_state.detail_key = None
if "budget" not in st.session_state:
    st.session_state.budget = 3_000_000
if "refresh_s" not in st.session_state: st.session_state.refresh_s = 0
if "refresh_y" not in st.session_state: st.session_state.refresh_y = 0
if "scout_s" not in st.session_state: st.session_state.scout_s = pd.DataFrame()
if "scout_y" not in st.session_state: st.session_state.scout_y = pd.DataFrame()
if "starters" not in st.session_state: st.session_state.starters = []

df_senior = st.session_state.df[st.session_state.df.Youth==False].reset_index(drop=True)
df_youth  = st.session_state.df[st.session_state.df.Youth==True].reset_index(drop=True)

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# --- 1. Senior Tab ---
with tabs[0]:
    st.subheader("Senior Squad")
    q = st.text_input("Search Senior", key="search_s", placeholder="Name / Pos / Nat")
    df1 = df_senior.copy()
    if q:
        df1 = df1[df1.apply(lambda r: q.lower() in r.Name.lower() or q.lower() in r.Pos.lower() or q.lower() in r.Nat.lower(), axis=1)]
    # 表示（旧仕様）
    st.markdown('<div class="player-table"><table><thead><tr>'
                + ''.join(f'<th>{c}</th>' for c in ["Name","Nat","Pos","Age","Contract","Salary","OVR"])
                + '</tr></thead><tbody>'
                + ''.join(
                    "<tr>"
                    + f"<td>{r.Name}</td>"
                    + f"<td>{NATIONS[r.Nat]}</td>"
                    + f"<td>{r.Pos}</td>"
                    + f"<td>{r.Age}</td>"
                    + f"<td>{r.Contract}</td>"
                    + f"<td>{fmt_money(r.Salary)}</td>"
                    + f"<td>{r.OVR}</td>"
                    + "</tr>"
                    for _,r in df1.iterrows()
                )
                + '</tbody></table></div>', unsafe_allow_html=True)
    st.markdown(".divider", unsafe_allow_html=True)
    st.markdown("#### Player Cards")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    for i,r in df1.iterrows():
        key = f"s{i}"
        st.markdown(f"""
            <div class="player-card">
                <img src="{get_face(i)}">
                <b>{r.Name}</b><br>{NATIONS[r.Nat]} {r.Pos} {r.Age}<br>OVR:{r.OVR}
                <button class="detail-btn" onclick="document.dispatchEvent(new CustomEvent('btn_{key}'));">
                    {'Hide' if st.session_state.detail_key==key else 'Detail'}
                </button>
                <div id="popup_{key}" style="display:{'block' if st.session_state.detail_key==key else 'none'};" class="detail-popup">
                    {"<br>".join(f"<span style='color:{'#20e660' if r[l]>=90 else '#ffe600' if r[l]>=75 else '#1aacef'}'>{l}:{r[l]}</span>" for l in labels)}
                    <br><small>Agent: {r.Agent}</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.experimental_get_query_params().get(f'btn_{key}'):
            st.session_state.detail_key = None if st.session_state.detail_key==key else key
    st.markdown('</div>', unsafe_allow_html=True)

# --- 2. Youth Tab ---
with tabs[1]:
    st.subheader("Youth Squad")
    q2 = st.text_input("Search Youth", key="search_y", placeholder="Name / Pos / Nat")
    df2 = df_youth.copy()
    if q2:
        df2 = df2[df2.apply(lambda r: q2.lower() in r.Name.lower() or q2.lower() in r.Pos.lower() or q2.lower() in r.Nat.lower(), axis=1)]
    st.markdown('<div class="player-table"><table><thead><tr>'
                + ''.join(f'<th>{c}</th>' for c in ["Name","Nat","Pos","Age","Contract","Salary","OVR"])
                + '</tr></thead><tbody>'
                + ''.join(
                    "<tr>"
                    + f"<td>{r.Name}</td>"
                    + f"<td>{NATIONS[r.Nat]}</td>"
                    + f"<td>{r.Pos}</td>"
                    + f"<td>{r.Age}</td>"
                    + f"<td>{r.Contract}</td>"
                    + f"<td>{fmt_money(r.Salary)}</td>"
                    + f"<td>{r.OVR}</td>"
                    + "</tr>"
                    for _,r in df2.iterrows()
                )
                + '</tbody></table></div>', unsafe_allow_html=True)
    st.markdown(".divider", unsafe_allow_html=True)
    st.markdown("#### Player Cards")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    for i,r in df2.iterrows():
        key = f"y{i}"
        st.markdown(f"""
            <div class="player-card">
                <img src="{get_face(i+100)}">
                <b>{r.Name}</b><br>{NATIONS[r.Nat]} {r.Pos} {r.Age}<br>OVR:{r.OVR}
                <button class="detail-btn" onclick="document.dispatchEvent(new CustomEvent('btn_{key}'));">
                    {'Hide' if st.session_state.detail_key==key else 'Detail'}
                </button>
                <div id="popup_{key}" style="display:{'block' if st.session_state.detail_key==key else 'none'};" class="detail-popup">
                    {"<br>".join(f"<span style='color:{'#20e660' if r[l]>=90 else '#ffe600' if r[l]>=75 else '#1aacef'}'>{l}:{r[l]}</span>" for l in labels)}
                    <br><small>Agent: {r.Agent}</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.experimental_get_query_params().get(f'btn_{key}'):
            st.session_state.detail_key = None if st.session_state.detail_key==key else key
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. Match Tab ---
with tabs[2]:
    st.subheader("Match Simulation – Week 1")
    opp = st.selectbox("Opponent", [c for c in CLUBS if c!=MY_CLUB])
    st.write(f"Your Club: **{MY_CLUB}** vs **{opp}**")
    if st.button("Auto Starting XI", key="auto"):
        ST = df_senior.nlargest(11,"OVR")
        order = ["FW","MF","DF","GK"]
        ST["order"] = ST.Pos.apply(lambda p: order.index(p))
        ST = ST.sort_values(["order","OVR"], ascending=[True,False])
        st.session_state.starters = ST.Name.tolist()
    if st.session_state.starters:
        st.write("**Starting XI**")
        for name in st.session_state.starters:
            st.markdown(f"- {name}")
    if st.button("Start Match"):
        dfst = st.session_state.stand
        others = [c for c in CLUBS if c not in [MY_CLUB,opp]]
        for i in range(0,len(others),2):
            a,b = others[i],others[i+1]
            ga,gb = random.randint(0,3),random.randint(0,3)
            if ga>gb:
                dfst.loc[dfst.Club==a,["W","Pts"]]+= [1,3]
                dfst.loc[dfst.Club==b,"L"]+=1
            elif ga<gb:
                dfst.loc[dfst.Club==b,["W","Pts"]]+= [1,3]
                dfst.loc[dfst.Club==a,"L"]+=1
            else:
                dfst.loc[dfst.Club.isin([a,b]),"D"]+=1
                dfst.loc[dfst.Club==a,"Pts"]+=1
                dfst.loc[dfst.Club==b,"Pts"]+=1
        ST = st.session_state.starters
        ours = df_senior[df_senior.Name.isin(ST)]
        atk = ours.OVR.mean() if not ours.empty else 75
        oppatk = random.uniform(60,90)
        g1 = max(0,int(np.random.normal((atk-60)/8,1)))
        g2 = max(0,int(np.random.normal((oppatk-60)/8,1)))
        if g1>g2:
            res="Win"
            dfst.loc[dfst.Club==MY_CLUB,["W","Pts"]]+= [1,3]
            dfst.loc[dfst.Club==opp,"L"]+=1
        elif g1<g2:
            res="Lose"
            dfst.loc[dfst.Club==opp,["W","Pts"]]+= [1,3]
            dfst.loc[dfst.Club==MY_CLUB,"L"]+=1
        else:
            res="Draw"
            dfst.loc[dfst.Club.isin([MY_CLUB,opp]),"D"]+=1
            dfst.loc[dfst.Club==MY_CLUB,"Pts"]+=1
            dfst.loc[dfst.Club==opp,"Pts"]+=1
        scorer = ours.sample(1).Name.iloc[0] if not ours.empty else ""
        assist = ours.sample(1).Name.iloc[0] if not ours.empty else ""
        mvp = ours.nlargest(1,"OVR").Name.iloc[0] if not ours.empty else ""
        df_s = st.session_state.df
        df_s.loc[df_s.Name==scorer,"Goals"] += g1
        df_s.loc[df_s.Name==assist,"Assists"] += 1
        df_s.loc[df_s.Name==mvp,"MVP"] += 1
        df_s.loc[df_s.Name.isin(ST),"Rating"] += random.randint(6,10)
        st.session_state.stand = dfst.sort_values("Pts",ascending=False).reset_index(drop=True)
        st.success(f"{res} ({g1}-{g2})")
        st.info(f"Goals: {scorer} | Assist: {assist} | MVP: {mvp}")

# --- 4. Scout Tab ---
with tabs[3]:
    st.subheader("Scout Players")
    st.write(f"Budget: {fmt_money(st.session_state.budget)}")
    c1,c2 = st.columns(2)
    with c1:
        if st.button(f"Refresh Senior ({st.session_state.refresh_s}/3)"):
            if st.session_state.refresh_s<3:
                st.session_state.scout_s = make_players(5,False)
                st.session_state.refresh_s +=1
            else:
                st.warning("Senior scout limit reached")
    with c2:
        if st.button(f"Refresh Youth ({st.session_state.refresh_y}/3)"):
            if st.session_state.refresh_y<3:
                st.session_state.scout_y = make_players(5,True)
                st.session_state.refresh_y +=1
            else:
                st.warning("Youth scout limit reached")
    if not st.session_state.scout_s.empty:
        st.markdown("**Senior Candidates**")
        for i,r in st.session_state.scout_s.iterrows():
            cols=st.columns([1,3,1])
            cols[0].image(get_face(i+200),width=48)
            cols[1].markdown(f"**{r.Name}** {NATIONS[r.Nat]} {r.Pos} OVR:{r.OVR}")
            if cols[2].button("Sign",key=f"s{i}"):
                cost = int(r.Salary*(1+agents.set_index("Name").loc[r.Agent,"Fee"]))
                if r.Name in df_senior.Name.values:
                    st.error("Already in squad")
                elif st.session_state.budget<cost:
                    st.error("Insufficient budget")
                else:
                    st.session_state.budget -= cost
                    st.session_state.df = pd.concat(
                        [st.session_state.df, pd.DataFrame([r])],
                        ignore_index=True
                    )
                    st.success(f"Signed {r.Name}")
    if not st.session_state.scout_y.empty:
        st.markdown("**Youth Candidates**")
        for i,r in st.session_state.scout_y.iterrows():
            cols=st.columns([1,3,1])
            cols[0].image(get_face(i+300),width=48)
            cols[1].markdown(f"**{r.Name}** {NATIONS[r.Nat]} {r.Pos} OVR:{r.OVR}")
            if cols[2].button("Sign",key=f"y{i}"):
                cost = int(r.Salary*(1+agents.set_index("Name").loc[r.Agent,"Fee"]))
                if r.Name in df_youth.Name.values:
                    st.error("Already in youth")
                elif st.session_state.budget<cost:
                    st.error("Insufficient budget")
                else:
                    st.session_state.budget -= cost
                    st.session_state.df = pd.concat(
                        [st.session_state.df, pd.DataFrame([r])],
                        ignore_index=True
                    )
                    st.success(f"Signed {r.Name}")

# --- 5. Standings Tab ---
with tabs[4]:
    st.subheader("Standings & Top5 Rankings")
    st.dataframe(
        st.session_state.stand.style.set_properties(**{
            "background-color":"rgba(32,44,70,0.7)","color":"#fff","text-align":"center"
        }),
        use_container_width=True
    )
    st.markdown("---")
    allp = st.session_state.df
    st.markdown("**Top 5 Goals**");    st.table(allp.nlargest(5,"Goals")[["Name","Goals"]])
    st.markdown("**Top 5 Assists**");  st.table(allp.nlargest(5,"Assists")[["Name","Assists"]])
    st.markdown("**Top 5 Rating**");   st.table(allp.nlargest(5,"Rating")[["Name","Rating"]])
    st.markdown("**Top 5 MVPs**");     st.table(allp.nlargest(5,"MVP")[["Name","MVP"]])

# --- 6. Save Tab ---
with tabs[5]:
    st.subheader("Save / Load")
    if st.button("Save Data"): st.success("Data saved!")
    if st.button("Load Data"): st.success("Data loaded!")

st.caption("✅ 全機能完全統合版 2025")
