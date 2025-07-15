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
  background:#1f2c4bcc; color:#fff; border-radius:12px;
  padding:10px; margin:6px 3px; min-width:140px; max-width:160px;
  box-shadow:0 0 8px #0003; position:relative;
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
.mobile-scroll { display:flex; }
.stage-label { background:#222b3c88; color:#fff; padding:6px 12px; border-radius:8px; display:inline-block; margin-bottom:8px;}
.red-message { color:#f55!important; }
.stDataFrame {background:rgba(20,30,50,0.7)!important; color:#fff!important;}
.separator { border-top:1px solid #446; margin:6px 0; }
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

# --- 金額フォーマット ---
def fmt_money(v):
    if v >= 1_000_000: return f"{v//1_000_000}m€"
    if v >=   1_000: return f"{v//1_000}k€"
    return f"{v}€"

# --- 能力項目 ---
labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina',
               'Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

# --- データ生成関数 ---
def gen_players(n,youth=False):
    used = set()
    lst = []
    for _ in range(n):
        name = make_name(used)
        nat  = random.choice(list(NATIONS.keys()))
        stats = {l: random.randint(52 if youth else 60, 82 if youth else 90) for l in labels}
        ovr = int(np.mean(list(stats.values())))
        lst.append({
            "Name": name,
            "Nat":  nat,
            "Pos":  random.choice(["GK","DF","MF","FW"]),
            "Age":  random.randint(15 if youth else 18, 18 if youth else 34),
            **stats,
            "Salary":   random.randint(30_000 if youth else 120_000,
                                      250_000 if youth else 1_200_000),
            "Contract": random.randint(1,2 if youth else 3),
            "OVR":       ovr,
            "Goals":     0,
            "Assists":   0,
            "Rating":    [],  # 試合ごとの評価点リスト
            "MVPs":      0,
            "Youth":     youth
        })
    return pd.DataFrame(lst)

# --- セッション初期化 ---
if "senior" not in st.session_state:
    st.session_state.senior = gen_players(30, False)
if "youth" not in st.session_state:
    st.session_state.youth = gen_players(20, True)
if "stand" not in st.session_state:
    st.session_state.stand = pd.DataFrame({
        "Club": CLUBS, "W":0,"D":0,"L":0,"Pts":0
    })
if "opp" not in st.session_state:
    st.session_state.opp = random.choice([c for c in CLUBS if c!=MY_CLUB])
if "detail_key" not in st.session_state:
    st.session_state.detail_key = None
if "starters" not in st.session_state:
    st.session_state.starters = []
if "week" not in st.session_state:
    st.session_state.week = 1

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# ==== 1. Senior ====
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    df1 = st.session_state.senior.copy()
    df1["Nat"] = df1["Nat"].map(NATIONS)
    # テーブル（検索ボックス付き）
    st.dataframe(df1[["Name","Nat","Pos","Age","Contract","Salary","OVR"]].assign(
        Salary=df1["Salary"].map(fmt_money)
    ), use_container_width=True)
    st.markdown("---")
    st.markdown("#### Players")
    for i,row in df1.iterrows():
        key = f"sen{i}"
        st.markdown('<div class="player-card">', unsafe_allow_html=True)
        st.write(f"**{row['Name']}**  {row['Nat']}｜{row['Pos']}｜{row['Age']}歳")
        if st.button("Detail", key=key):
            st.session_state.detail_key = None if st.session_state.detail_key==key else key
        if st.session_state.detail_key == key:
            # レーダーチャート
            abil = [row[l] for l in labels] + [row[labels[0]]]
            ang = np.linspace(0,2*np.pi,len(labels)+1)
            fig,ax = plt.subplots(subplot_kw=dict(polar=True),figsize=(2,2))
            ax.plot(ang,abil,linewidth=2); ax.fill(ang,abil,alpha=0.3)
            ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels],color="#fff")
            ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
            fig.patch.set_alpha(0); ax.patch.set_alpha(0)
            st.pyplot(fig)
            # 縦並びステータス
            stats_md = "\n".join(
                f"- <span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}: {row[l]}</span>"
                for l in labels
            )
            st.markdown(f"<div class='detail-popup'>{stats_md}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

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
        for i,row in df2.iterrows():
            key = f"you{i}"
            st.markdown('<div class="player-card">', unsafe_allow_html=True)
            st.write(f"**{row['Name']}**  {row['Nat']}｜{row['Pos']}｜{row['Age']}歳")
            if st.button("Detail", key=key):
                st.session_state.detail_key = None if st.session_state.detail_key==key else key
            if st.session_state.detail_key == key:
                abil = [row[l] for l in labels] + [row[labels[0]]]
                ang = np.linspace(0,2*np.pi,len(labels)+1)
                fig,ax = plt.subplots(subplot_kw=dict(polar=True),figsize=(2,2))
                ax.plot(ang,abil,linewidth=2); ax.fill(ang,abil,alpha=0.3)
                ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels],color="#fff")
                ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
                fig.patch.set_alpha(0); ax.patch.set_alpha(0)
                st.pyplot(fig)
                stats_md = "\n".join(
                    f"- <span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}: {row[l]}</span>"
                    for l in labels
                )
                st.markdown(f"<div class='detail-popup'>{stats_md}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# ==== 3. Match ====
with tabs[2]:
    st.markdown(f'<div class="stage-label">Match Simulation ‒ Week {st.session_state.week} / 14</div>', unsafe_allow_html=True)
    st.write(f"**Your Club:** {MY_CLUB}  vs  **Opponent:** {st.session_state.opp}")
    form = st.selectbox("Formation", ["4-4-2","4-3-3","3-5-2"])
    if st.button("Auto Starting XI"):
        # 自動選出：OVR上位11人、かつポジションごと必要数
        df = st.session_state.senior
        nums = {"4-4-2":(2,4,4,1),"4-3-3":(3,3,4,1),"3-5-2":(2,5,3,1)}
        fw, mf, dfc, gk = nums[form]
        chosen = []
        for pos,cnt in zip(["FW","MF","DF","GK"], [fw,mf,dfc,gk]):
            top = df[df["Pos"]==pos].nlargest(cnt,"OVR")["Name"].tolist()
            chosen += top
        st.session_state.starters = chosen

    # 縦並び表示
    if st.session_state.starters:
        st.markdown("#### Starting XI")
        for name in st.session_state.starters:
            row = st.session_state.senior.loc[st.session_state.senior["Name"]==name].iloc[0]
            st.write(f"- **{name}** ({row['Pos']})  Goals:{row['Goals']}  Ast:{row['Assists']}  AvgR:{(np.mean(row['Rating']) if row['Rating'] else 0):.1f}  MVPs:{row['MVPs']}")

    if st.button("Kickoff!"):
        # 他試合を暫定的に進行
        stand = st.session_state.stand
        others = [c for c in CLUBS if c not in [MY_CLUB, st.session_state.opp]]
        for i in range(0,len(others),2):
            a,b = others[i],others[i+1]
            ga,gb = random.randint(0,3), random.randint(0,3)
            if ga>gb:
                stand.loc[stand.Club==a,["W","Pts"]] += [1,3]
                stand.loc[stand.Club==b,"L"] += 1
            elif ga<gb:
                stand.loc[stand.Club==b,["W","Pts"]] += [1,3]
                stand.loc[stand.Club==a,"L"] += 1
            else:
                stand.loc[stand.Club.isin([a,b]),"D"] += 1
                stand.loc[stand.Club==a,"Pts"] += 1
                stand.loc[stand.Club==b,"Pts"] += 1

        # 自チーム試合
        ours = st.session_state.senior[st.session_state.senior["Name"].isin(st.session_state.starters)]
        atk = ours["OVR"].mean() if not ours.empty else 70
        oppatk = random.uniform(60,90)
        g1 = max(0,int(np.random.normal((atk-60)/8,1)))
        g2 = max(0,int(np.random.normal((oppatk-60)/8,1)))
        if g1>g2: res="Win"
        elif g1<g2: res="Lose"
        else: res="Draw"
        # 勝敗反映
        if res=="Win":
            stand.loc[stand.Club==MY_CLUB,["W","Pts"]] += [1,3]
            stand.loc[stand.Club==st.session_state.opp,"L"] += 1
        elif res=="Lose":
            stand.loc[stand.Club==st.session_state.opp,["W","Pts"]] += [1,3]
            stand.loc[stand.Club==MY_CLUB,"L"] += 1
        else:
            stand.loc[stand.Club.isin([MY_CLUB,st.session_state.opp]),"D"] += 1
            stand.loc[stand.Club==MY_CLUB,"Pts"] += 1
            stand.loc[stand.Club==st.session_state.opp,"Pts"] += 1

        # 得点・アシスト・MVPをランダム振り分け
        scorers = random.choices(st.session_state.starters, k=g1)
        assisters= random.choices(st.session_state.starters, k=g1)
        for p in scorers:
            st.session_state.senior.loc[st.session_state.senior["Name"]==p,"Goals"] += 1
        for p in assisters:
            st.session_state.senior.loc[st.session_state.senior["Name"]==p,"Assists"] += 1
        if ours.shape[0]:
            mvp = ours.nlargest(1,"OVR")["Name"].iloc[0]
            st.session_state.senior.loc[st.session_state.senior["Name"]==mvp,"MVPs"] += 1
        else:
            mvp = ""
        # 評価点追加
        for p in ours["Name"]:
            score = round(random.uniform(6.0, 9.0),1)
            st.session_state.senior.loc[st.session_state.senior["Name"]==p,"Rating"].iloc[0].append(score)

        st.session_state.stand = stand.sort_values("Pts",ascending=False).reset_index(drop=True)
        st.session_state.week += 1
        st.session_state.opp = random.choice([c for c in CLUBS if c!=MY_CLUB])

        # 結果表示
        st.markdown(f"<div style='background:#27e3b9;color:#fff;padding:8px;border-radius:8px;'>**{res} ({g1}-{g2})**</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#314265;color:#fff;padding:6px;border-radius:6px;'>Goals: You {g1} ‒ Opp {g2} | MVP: {mvp}</div>", unsafe_allow_html=True)

# ==== 4. Scout ====
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players</div>', unsafe_allow_html=True)
    # 毎回全員刷新
    if st.button("Refresh Senior Scouts"):
        st.session_state.senior = pd.concat([st.session_state.senior, gen_players(5,False)], ignore_index=True)
    if st.button("Refresh Youth Scouts"):
        st.session_state.youth = pd.concat([st.session_state.youth, gen_players(5,True)], ignore_index=True)

# ==== 5. Standings & Rankings ====
with tabs[4]:
    st.markdown('<div class="stage-label">Standings & Top Rankings</div>', unsafe_allow_html=True)
    # 順位表
    dfst = st.session_state.stand
    styled = dfst.style.set_properties(**{
        "background-color":"rgba(32,44,70,0.7)", "color":"white", "text-align":"center"
    }).set_table_styles([{
        "selector":"thead th", "props":[("background","rgba(32,44,70,0.9)"),("color","white")]
    }])
    st.dataframe(styled, height=300, use_container_width=True)

    # トップ5ランキング
    allp = pd.concat([st.session_state.senior, st.session_state.youth], ignore_index=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Top Goals")
        top = allp.nlargest(5,"Goals")[["Name","Goals"]]
        st.write(top.to_string(index=False))
    with col2:
        st.subheader("Top Assists")
        top = allp.nlargest(5,"Assists")[["Name","Assists"]]
        st.write(top.to_string(index=False))
    with col3:
        st.subheader("Top MVPs")
        top = allp.nlargest(5,"MVPs")[["Name","MVPs"]]
        st.write(top.to_string(index=False))
    with col4:
        st.subheader("Top Rating")
        allp["AvgR"] = allp["Rating"].apply(lambda x: np.mean(x) if x else 0)
        top = allp.nlargest(5,"AvgR")[["Name","AvgR"]]
        st.write(top.to_string(index=False))

# ==== 6. Save ====
with tabs[5]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Data"): st.success("Data saved.")
    if st.button("Load Data"): st.success("Data loaded.")

st.caption("2025年版：顔写真削除／完全テキスト表示／14節制シーズン／最終ランキング発表対応版")
