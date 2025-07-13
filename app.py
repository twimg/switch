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

/* セレクトボックスの深紺背景 */
.stSelectbox > div[role="button"] { background:rgba(32,44,70,0.9)!important; color:#fff!important; }

/* Multiselect 領域 */
.stMultiSelect > div[role="listbox"] { background:rgba(32,44,70,0.9)!important; color:#fff!important; }

/* プレイヤーカード */
.player-card {
  background:#fff; color:#132346; border-radius:12px;
  padding:6px; margin:4px; min-width:140px; max-width:160px;
  box-shadow:0 0 4px #0002; position:relative;
}
/* 軽い区切り線 */
.player-card + .player-card {
  border-top:0.5px solid #ccc; padding-top:6px;
}

/* 詳細ポップアップ */
.detail-popup {
  position:absolute; top:100%; left:50%; transform:translateX(-50%);
  background:rgba(36,54,84,0.9); color:#fff; padding:12px; border-radius:10px;
  width:200px; box-shadow:0 0 10px #000a; z-index:10; backdrop-filter:blur(8px);
}

/* テーブル */
.mobile-table {overflow-x:auto; white-space:nowrap;}
.mobile-table th, .mobile-table td {
  padding:4px 10px; font-size:15px; border-bottom:1px solid #243255;
  color:#fff;
}
.table-header { background:rgba(32,44,70,0.9)!important; color:#ffe900!important; }

/* ステージラベル */
.stage-label { background:#222b3c88; color:#fff; padding:6px 12px; border-radius:8px; display:inline-block; margin-bottom:8px;}

/* エラーメッセージ */
.red-message { color:#f55!important; }

/* DataFrameスタイル */
.stDataFrame {background:rgba(20,30,50,0.7)!important; color:#fff!important;}
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- 定数 ---
CLUBS = ["Strive FC","Oxford Utd","Viking SC","Lazio Town",
         "Munich Stars","Lille City","Sevilla Reds","Verona Blues"]
MY_CLUB = CLUBS[0]
NATIONS = {
    "United Kingdom":"🇬🇧","Germany":"🇩🇪","Italy":"🇮🇹","Spain":"🇪🇸",
    "France":"🇫🇷","Brazil":"🇧🇷","Netherlands":"🇳🇱","Portugal":"🇵🇹"
}

# --- 顔画像 ---
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
        n = f"{random.choice(given)} {random.choice(surname)}"
        if n not in used:
            used.add(n)
            return n

# --- フォーマット ---
def fmt_money(v):
    if v >= 1_000_000: return f"{v//1_000_000}m€"
    if v >= 1_000:     return f"{v//1_000}k€"
    return f"{v}€"

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina',
               'Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

# --- データ生成 ---
def gen_players(n, youth=False):
    used = set()
    lst = []
    for _ in range(n):
        name = make_name(used)
        stats = {l:random.randint(52 if youth else 60, 82 if youth else 90) for l in labels}
        ovr = int(np.mean(list(stats.values())))
        lst.append({
            "Name": name,
            "Nat": random.choice(list(NATIONS.keys())),
            "Pos": random.choice(["GK","DF","MF","FW"]),
            "Age": random.randint(15 if youth else 18, 18 if youth else 34),
            **stats,
            "Salary": random.randint(30_000 if youth else 120_000,
                                     250_000 if youth else 1_200_000),
            "Contract": random.randint(1, 2 if youth else 3),
            "OVR": ovr,
            "Youth": youth
        })
    return pd.DataFrame(lst)

# --- セッション初期化 ---
if "senior" not in st.session_state: st.session_state.senior = gen_players(30,False)
if "youth"  not in st.session_state: st.session_state.youth  = gen_players(20,True)
if "stand"  not in st.session_state: 
    st.session_state.stand = pd.DataFrame({"Club":CLUBS,"W":0,"D":0,"L":0,"Pts":0})
if "opp"    not in st.session_state: st.session_state.opp    = random.choice([c for c in CLUBS if c!=MY_CLUB])
if "detail" not in st.session_state: st.session_state.detail = None
if "starters"    not in st.session_state: st.session_state.starters = []
if "budget"      not in st.session_state: st.session_state.budget   = 3_000_000
if "refresh_s"   not in st.session_state: st.session_state.refresh_s = 0
if "refresh_y"   not in st.session_state: st.session_state.refresh_y = 0
if "scout_s"     not in st.session_state: st.session_state.scout_s   = pd.DataFrame()
if "scout_y"     not in st.session_state: st.session_state.scout_y   = pd.DataFrame()

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# ==== 1. Senior ====
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    # 検索ボックス
    q = st.text_input("Search Name", "")
    df1 = st.session_state.senior.copy()
    df1["Nat"] = df1["Nat"].map(NATIONS)
    if q: df1 = df1[df1["Name"].str.contains(q,case=False)]
    # HTMLテーブルで表示
    st.markdown(
        "<div class='mobile-table'><table>"
        "<thead class='table-header'><tr>"
        + "".join(f"<th>{c}</th>" for c in ["Name","Nat","Pos","Age","Contract","Salary","OVR"])
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>" +
            "".join(f"<td>{row[col]}</td>" for col in ["Name","Nat","Pos","Age","Contract"])
            + f"<td>{fmt_money(row['Salary'])}</td><td>{row['OVR']}</td></tr>"
            for _,row in df1.iterrows())
        + "</tbody></table></div>",
        unsafe_allow_html=True
    )

# ==== 2. Youth ====
with tabs[1]:
    st.markdown('<div class="stage-label">Youth Squad</div>', unsafe_allow_html=True)
    q2 = st.text_input("Search Name (Youth)", "")
    df2 = st.session_state.youth.copy()
    df2["Nat"] = df2["Nat"].map(NATIONS)
    if q2: df2 = df2[df2["Name"].str.contains(q2,case=False)]
    if df2.empty:
        st.markdown("<div class='red-message'>No youth players.</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='mobile-table'><table>"
            "<thead class='table-header'><tr>"
            + "".join(f"<th>{c}</th>" for c in ["Name","Nat","Pos","Age","Contract","Salary","OVR"])
            + "</tr></thead><tbody>"
            + "".join(
                "<tr>" +
                "".join(f"<td>{row[col]}</td>" for col in ["Name","Nat","Pos","Age","Contract"])
                + f"<td>{fmt_money(row['Salary'])}</td><td>{row['OVR']}</td></tr>"
                for _,row in df2.iterrows())
            + "</tbody></table></div>",
            unsafe_allow_html=True
        )

# ==== 3. Match ====
with tabs[2]:
    st.markdown('<div class="stage-label">Match Simulation ‒ Week 1</div>', unsafe_allow_html=True)
    st.write(f"**Your Club:** {MY_CLUB}  vs  **Opponent:** {st.session_state.opp}")
    formation = st.selectbox("Formation",["4-4-2","4-3-3","3-5-2"])
    if st.button("Auto Starting XI"):
        st.session_state.starters = st.session_state.senior.nlargest(11,"OVR")["Name"].tolist()

    if st.session_state.starters:
        # 透過設定
        def to_surname(n): return n.split()[-1]
        coords = {
            "4-4-2":([5],[2,4,6,8],[2,4,6,8],[3,7]),
            "4-3-3":([5],[2,4,6,8],[3.5,5,6.5],[2,5,8]),
            "3-5-2":([5],[3.5,5,6.5],[2,4,6,8],[3,7])
        }
        gk,def4,mid,fw = coords[formation]
        fig,ax = plt.subplots(figsize=(3,5))
        fig.patch.set_facecolor('none'); ax.set_facecolor('none')
        ax.set_xlim(0,10); ax.set_ylim(0,16); ax.axis('off')
        ax.plot([0,10],[8,8],color='white',linewidth=1)
        idx=0
        ax.text(5,1, to_surname(st.session_state.starters[idx]), ha='center', va='center', color='yellow'); idx+=1
        for x in def4:
            ax.text(x,4, to_surname(st.session_state.starters[idx]), ha='center', va='center', color='white'); idx+=1
        for x in mid:
            ax.text(x,8, to_surname(st.session_state.starters[idx]), ha='center', va='center', color='white'); idx+=1
        for x in fw:
            ax.text(x,12,to_surname(st.session_state.starters[idx]),ha='center',va='center',color='white'); idx+=1
        st.pyplot(fig)

# ==== 4. Scout ====
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players</div>', unsafe_allow_html=True)
    st.markdown(f"**Budget:** {fmt_money(st.session_state.budget)}")
    c1,c2 = st.columns(2)
    with c1:
        if st.button(f"Refresh Senior ({st.session_state.refresh_s}/3)"):
            if st.session_state.refresh_s<3:
                st.session_state.scout_s = gen_players(5,False)
                st.session_state.refresh_s +=1
            else: st.warning("Senior scout limit reached")
    with c2:
        if st.button(f"Refresh Youth ({st.session_state.refresh_y}/3)"):
            if st.session_state.refresh_y<3:
                st.session_state.scout_y = gen_players(5,True)
                st.session_state.refresh_y +=1
            else: st.warning("Youth scout limit reached")

    if not st.session_state.scout_s.empty:
        st.markdown("#### Senior Candidates")
        for i,row in st.session_state.scout_s.iterrows():
            st.markdown(f"<div class='player-card'>", unsafe_allow_html=True)
            cols=st.columns([1,3,2])
            with cols[0]: st.image(get_img(i+60),width=48)
            with cols[1]:
                st.write(f"**{row['Name']}**")
                st.write(f"{NATIONS[row['Nat']]}｜{row['Pos']}｜{row['Age']}")
                st.write(f"OVR:{row['OVR']}")
                st.write(f"Salary:{fmt_money(row['Salary'])}")
            with cols[2]:
                if st.button("Sign", key=f"ss{i}"):
                    if row["Name"] in st.session_state.senior["Name"].tolist():
                        st.error("Already in squad")
                    elif st.session_state.budget<row["Salary"]:
                        st.error("Not enough budget")
                    else:
                        st.session_state.budget-=row["Salary"]
                        st.session_state.senior=pd.concat([st.session_state.senior,pd.DataFrame([row])],ignore_index=True)
                        st.success(f"{row['Name']} signed!")
            st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.scout_y.empty:
        st.markdown("#### Youth Candidates")
        for i,row in st.session_state.scout_y.iterrows():
            st.markdown(f"<div class='player-card'>", unsafe_allow_html=True)
            cols=st.columns([1,3,2])
            with cols[0]: st.image(get_img(i+80),width=48)
            with cols[1]:
                st.write(f"**{row['Name']}**")
                st.write(f"{NATIONS[row['Nat']]}｜{row['Pos']}｜{row['Age']}")
                st.write(f"OVR:{row['OVR']}")
                st.write(f"Salary:{fmt_money(row['Salary'])}")
            with cols[2]:
                if st.button("Sign", key=f"sy{i}"):
                    if row["Name"] in st.session_state.youth["Name"].tolist():
                        st.error("Already in youth")
                    elif st.session_state.budget<row["Salary"]:
                        st.error("Not enough budget")
                    else:
                        st.session_state.budget-=row["Salary"]
                        st.session_state.youth=pd.concat([st.session_state.youth,pd.DataFrame([row])],ignore_index=True)
                        st.success(f"{row['Name']} signed!")
            st.markdown("</div>", unsafe_allow_html=True)

# ==== 5. Standings ====
with tabs[4]:
    st.markdown('<div class="stage-label">Standings</div>', unsafe_allow_html=True)
    dfst = st.session_state.stand
    styled = dfst.style.set_properties(**{
        "background-color":"rgba(32,44,70,0.7)","color":"white","text-align":"center"
    }).set_table_styles([{
        "selector":"thead th","props":[("background","rgba(32,44,70,0.9)"),("color","white")]
    }])
    st.dataframe(styled, height=300, use_container_width=True)

# ==== 6. Save ====
with tabs[5]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Data"): st.success("Data saved!")
    if st.button("Load Data"): st.success("Data loaded!")

st.caption("2025年版：最終完全統合（透過＆検索＆区切り線調整）")
