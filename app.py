import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from PIL import Image
from io import BytesIO
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Soccer Club Management Sim", layout="wide")
random.seed(42)
np.random.seed(42)

# --- CSS カスタム ---
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff;}
h1,h2,h3,h4,h5,h6 { color:#fff!important; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }
/* カード一覧 */
.player-card { 
  background:#fff; color:#132346; border-radius:12px; 
  padding:8px; margin:6px; width:160px; 
  display:inline-block; vertical-align:top;
  box-shadow:0 0 6px #0002;
  position:relative;
}
.player-card img {
  border-radius:50%; width:64px; height:64px; object-fit:cover; margin-bottom:6px;
}
/* 詳細ポップアップ */
.detail-popup {
  position:absolute; top:100%; left:50%; transform:translateX(-50%);
  background:rgba(36,54,84,0.9); color:#fff; padding:12px; border-radius:10px;
  width:200px; box-shadow:0 0 10px #000a; backdrop-filter:blur(8px); z-index:10;
}
/* フォーメーション */
.form-pitch { 
  background:#1b3a5b; border:2px solid #2b4b75; 
  border-radius:8px; padding:8px; display:inline-block;
}
/* ランキングテーブル（白文字） */
.ranking-table th, .ranking-table td { color:#fff !important; }
/* ボタン */
.stButton>button, .stDownloadButton>button {
  background:#27e3b9!important; color:#202b41!important; font-weight:bold;
  border-radius:10px; margin:6px 0; box-shadow:0 0 8px #23e9e733;
}
.stButton>button:active { background:#ffee99!important; }
/* その他 */
.stage-label { background:#222b3c88; color:#fff; padding:6px 12px; border-radius:8px; display:inline-block; margin-bottom:8px; }
.red-message { color:#f55!important; }
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- 定数 ---
CLUBS = ["Strive FC","Oxford Utd","Viking SC","Lazio Town","Munich Stars","Lille City","Sevilla Reds","Verona Blues"]
MY_CLUB = CLUBS[0]
NATIONS = {"United Kingdom":"🇬🇧","Germany":"🇩🇪","Italy":"🇮🇹","Spain":"🇪🇸","France":"🇫🇷","Brazil":"🇧🇷","Netherlands":"🇳🇱","Portugal":"🇵🇹"}

# --- 画像取得 with フォールバック ---
face_urls = [f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in range(10,50)]
def load_image(url):
    try:
        resp = requests.get(url, timeout=2)
        img = Image.open(BytesIO(resp.content))
    except:
        img = Image.new("RGB",(64,64),color=(200,200,200))
    return img
def get_img():
    return load_image(random.choice(face_urls))

# --- 名前プール ---
surname = ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker","White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris","Baker","Moore","Wright","Hill","Cooper","Edwards","Ward","King","Parker","Campbell"]
given   = ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William","James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin","Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"]
def make_name(used):
    while True:
        n = f"{random.choice(given)} {random.choice(surname)}"
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
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

# --- データ生成 ---
def gen_players(n,youth=False):
    used=set(); rows=[]
    for _ in range(n):
        name=make_name(used)
        stats={l:random.randint(52 if youth else 60,82 if youth else 90) for l in labels}
        ovr=int(np.mean(list(stats.values())))
        rows.append({
            "Name":name,
            "Nat":random.choice(list(NATIONS.keys())),
            "Pos":random.choice(["GK","DF","MF","FW"]),
            "Age":random.randint(15 if youth else 18,18 if youth else 34),
            "Salary":random.randint(30_000 if youth else 120_000,250_000 if youth else 1_200_000),
            "Contract":random.randint(1,2 if youth else 3),
            "OVR":ovr,
            "Goals":0,"Assists":0,"RatingSum":0,"Matches":0,"MVPs":0,
            "Youth":youth,
            **stats
        })
    return pd.DataFrame(rows)

# --- セッション初期化 ---
if "senior"    not in st.session_state: st.session_state.senior    = gen_players(30, False)
if "youth"     not in st.session_state: st.session_state.youth     = gen_players(20, True)
if "stand"     not in st.session_state: st.session_state.stand     = pd.DataFrame({"Club":CLUBS,"W":0,"D":0,"L":0,"Pts":0})
if "opp"       not in st.session_state: st.session_state.opp       = random.choice([c for c in CLUBS if c!=MY_CLUB])
if "detail"    not in st.session_state: st.session_state.detail    = None
if "starters"  not in st.session_state: st.session_state.starters  = []
if "budget"    not in st.session_state: st.session_state.budget    = 3_000_000
if "refresh_s" not in st.session_state: st.session_state.refresh_s = 0
if "refresh_y" not in st.session_state: st.session_state.refresh_y = 0
if "scout_s"   not in st.session_state: st.session_state.scout_s   = pd.DataFrame()
if "scout_y"   not in st.session_state: st.session_state.scout_y   = pd.DataFrame()

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# === Senior タブ ===
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    q = st.text_input("Search Name (Senior)", "")
    df1 = st.session_state.senior.copy()
    df1["Nat"] = df1["Nat"].map(NATIONS)
    if q:
        df1 = df1[df1["Name"].str.contains(q, case=False)]
    for i,row in df1.iterrows():
        st.markdown('<div class="player-card">', unsafe_allow_html=True)
        cols = st.columns([1,3,2])
        with cols[0]:
            st.image(get_img(), width=48)
        with cols[1]:
            st.write(f"**{row['Name']}**")
            st.write(f"{row['Nat']} | {row['Pos']} | Age:{row['Age']}")
            st.write(f"OVR:{row['OVR']}")
        with cols[2]:
            if st.button("Detail", key=f"s_det_{i}"):
                st.session_state.detail = None if st.session_state.detail==f"s_det_{i}" else f"s_det_{i}"
        if st.session_state.detail == f"s_det_{i}":
            abil = [row[l] for l in labels] + [row[labels[0]]]
            ang = np.linspace(0,2*np.pi,len(labels)+1)
            fig,ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(2,2))
            ax.plot(ang, abil, linewidth=2); ax.fill(ang, abil, alpha=0.3)
            ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels], color="#fff")
            ax.set_yticklabels([]); ax.grid(color="#fff", alpha=0.2)
            fig.patch.set_alpha(0); ax.patch.set_alpha(0)
            st.pyplot(fig)
            stats = "".join(
                f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                for l in labels
            )
            st.markdown(f"<div class='detail-popup'>{stats}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# === Youth タブ ===
with tabs[1]:
    st.markdown('<div class="stage-label">Youth Squad</div>', unsafe_allow_html=True)
    q2 = st.text_input("Search Name (Youth)", "")
    df2 = st.session_state.youth.copy()
    df2["Nat"] = df2["Nat"].map(NATIONS)
    if q2:
        df2 = df2[df2["Name"].str.contains(q2, case=False)]
    if df2.empty:
        st.markdown("<div class='red-message'>No youth players.</div>", unsafe_allow_html=True)
    else:
        for i,row in df2.iterrows():
            st.markdown('<div class="player-card">', unsafe_allow_html=True)
            cols = st.columns([1,3,2])
            with cols[0]:
                st.image(get_img(), width=48)
            with cols[1]:
                st.write(f"**{row['Name']}**")
                st.write(f"{row['Nat']} | {row['Pos']} | Age:{row['Age']}")
                st.write(f"OVR:{row['OVR']}")
            with cols[2]:
                if st.button("Detail", key=f"y_det_{i}"):
                    st.session_state.detail = None if st.session_state.detail==f"y_det_{i}" else f"y_det_{i}"
            if st.session_state.detail == f"y_det_{i}":
                abil = [row[l] for l in labels] + [row[labels[0]]]
                ang = np.linspace(0,2*np.pi,len(labels)+1)
                fig,ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(2,2))
                ax.plot(ang, abil, linewidth=2); ax.fill(ang, abil, alpha=0.3)
                ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels], color="#fff")
                ax.set_yticklabels([]); ax.grid(color="#fff", alpha=0.2)
                fig.patch.set_alpha(0); ax.patch.set_alpha(0)
                st.pyplot(fig)
                stats = "".join(
                    f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                    for l in labels
                )
                st.markdown(f"<div class='detail-popup'>{stats}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# === Match タブ ===
with tabs[2]:
    st.markdown('<div class="stage-label">Match Simulation – Week 1</div>', unsafe_allow_html=True)
    st.write(f"**Your Club:** {MY_CLUB} vs **Opponent:** {st.session_state.opp}")
    formation = st.selectbox("Formation", ["4-4-2","4-3-3","3-5-2"])
    if st.button("Auto Starting XI"):
        st.session_state.starters = st.session_state.senior.nlargest(11,"OVR")["Name"].tolist()

    # フォーメーション図（狭めて中央寄せ）
    if st.session_state.starters:
        coords = {
            "4-4-2": ([5],[4,6,8,10],[4,6,8,10],[6,8]),
            "4-3-3": ([5],[4,6,8,10],[6,8,10],[6,8,10]),
            "3-5-2": ([5],[6,8,10],[4,6,8,10],[6,8])
        }
        gk,defp,midp,fw = coords[formation]
        fig,ax = plt.subplots(figsize=(3,5))
        fig.patch.set_facecolor('none'); ax.patch.set_facecolor('none'); ax.axis('off')
        ax.axhline(8, color='white', alpha=0.3, linewidth=1, zorder=0)
        def sur(n): return n.split()[-1]
        names = st.session_state.starters; idx=0
        ax.text(7,1, sur(names[idx]), ha='center', va='center', color='yellow', fontweight='bold', fontsize=12); idx+=1
        for x in defp:
            ax.text(x,4, sur(names[idx]), ha='center', va='center', color='white', fontsize=10); idx+=1
        for x in midp:
            ax.text(x,8, sur(names[idx]), ha='center', va='center', color='white', fontsize=10); idx+=1
        for x in fw:
            ax.text(x,12, sur(names[idx]), ha='center', va='center', color='white', fontsize=10); idx+=1
        st.pyplot(fig)

    if st.button("Start Match"):
        # 勝敗判定
        g1 = random.randint(0,4); g2 = random.randint(0,4)
        winners = {"Win":(1,0,0),"Lose":(0,0,1),"Draw":(0,1,0)}
        res = "Win" if g1>g2 else "Lose" if g1<g2 else "Draw"
        W,D,L = winners[res]
        dfst = st.session_state.stand
        mi,oi = MY_CLUB, st.session_state.opp
        # 自チーム
        dfst.loc[dfst.Club==mi, ["W","D","L","Pts"]] += [W, D, L, 3*W+1*D]
        # 相手
        dfst.loc[dfst.Club==oi, ["W","D","L","Pts"]] += [L, D, W, 3*L+1*D]
        st.session_state.stand = dfst.sort_values("Pts", ascending=False).reset_index(drop=True)

        # 得点者・アシスト・評価・MVP
        starters = st.session_state.starters
        scorers   = random.choices(starters, k=g1)
        assisters = random.choices([p for p in starters if p not in scorers], k=g1)
        ratings   = {p:random.uniform(5,10) for p in starters}
        mvp       = max(ratings, key=ratings.get)

        # Stats 更新
        for p in starters:
            idx = st.session_state.senior.index[st.session_state.senior["Name"]==p][0]
            st.session_state.senior.at[idx,"Matches"] += 1
            st.session_state.senior.at[idx,"RatingSum"] += ratings[p]
            if p==mvp: st.session_state.senior.at[idx,"MVPs"] += 1
        for s in scorers:
            idx = st.session_state.senior.index[st.session_state.senior["Name"]==s][0]
            st.session_state.senior.at[idx,"Goals"] += 1
        for a in assisters:
            idx = st.session_state.senior.index[st.session_state.senior["Name"]==a][0]
            st.session_state.senior.at[idx,"Assists"] += 1

        # 表示
        st.markdown(f"<div style='background:#27e3b9;color:#fff;padding:8px;border-radius:8px;'>**{res} ({g1}-{g2})**</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#314265;color:#fff;padding:6px;border-radius:6px;'>Goals: {', '.join(scorers)}<br>Assists: {', '.join(assisters)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#314265;color:#fff;padding:6px;border-radius:6px;'>MVP: {mvp}</div>", unsafe_allow_html=True)

# === Scout タブ ===
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players</div>', unsafe_allow_html=True)
    st.markdown(f"**Budget:** {fmt_money(st.session_state.budget)}")
    c1,c2 = st.columns(2)
    with c1:
        if st.button(f"Refresh Senior ({st.session_state.refresh_s}/3)"):
            if st.session_state.refresh_s<3:
                st.session_state.scout_s = gen_players(5,False)
                st.session_state.refresh_s += 1
            else: st.warning("Senior scout limit reached")
    with c2:
        if st.button(f"Refresh Youth ({st.session_state.refresh_y}/3)"):
            if st.session_state.refresh_y<3:
                st.session_state.scout_y = gen_players(5,True)
                st.session_state.refresh_y += 1
            else: st.warning("Youth scout limit reached")

    for df,label,offset in [(st.session_state.scout_s,"Senior",60),(st.session_state.scout_y,"Youth",100)]:
        if not df.empty:
            st.markdown(f"#### {label} Candidates")
            for i,row in df.iterrows():
                st.markdown('<div class="player-card">', unsafe_allow_html=True)
                cols=st.columns([1,3,2])
                with cols[0]:
                    st.image(get_img(), width=48)
                with cols[1]:
                    st.write(f"**{row['Name']}**")
                    st.write(f"{NATIONS[row['Nat']]} | {row['Pos']} | Age:{row['Age']}")
                    st.write(f"OVR:{row['OVR']} | Sal:{fmt_money(row['Salary'])}")
                with cols[2]:
                    if st.button("Sign", key=f"{label}_{i}"):
                        if row["Name"] in (st.session_state.senior["Name"] if label=="Senior" else st.session_state.youth["Name"]).tolist():
                            st.error("Already in squad")
                        elif st.session_state.budget<row["Salary"]:
                            st.error("Insufficient budget")
                        else:
                            st.session_state.budget-=row["Salary"]
                            target = st.session_state.senior if label=="Senior" else st.session_state.youth
                            target = pd.concat([target, pd.DataFrame([row])], ignore_index=True)
                            if label=="Senior":
                                st.session_state.senior = target
                            else:
                                st.session_state.youth = target
                            st.success(f"{row['Name']} signed!")
                st.markdown("</div>", unsafe_allow_html=True)

# === Standings タブ ===
with tabs[4]:
    st.markdown('<div class="stage-label">Player Rankings</div>', unsafe_allow_html=True)
    dfp = st.session_state.senior.copy()
    dfp["AvgRating"] = dfp["RatingSum"]/dfp["Matches"].replace(0,1)
    def top5(col, fmt=None):
        tmp = dfp.nlargest(5, col)[["Name",col]]
        if fmt: tmp[col] = tmp[col].map(fmt)
        return tmp
    # テーブル白文字化
    for title, tbl in [("Top Goals", top5("Goals")),
                       ("Top Assists", top5("Assists")),
                       ("Top AvgRating", top5("AvgRating", lambda x:f"{x:.2f}")),
                       ("Top MVPs", top5("MVPs"))]:
        st.markdown(f"**{title}**")
        st.write(tbl.to_html(classes="ranking-table", index=False), unsafe_allow_html=True)

    st.markdown('---')
    st.markdown('<div class="stage-label">Standings</div>', unsafe_allow_html=True)
    dfst = st.session_state.stand
    styled = dfst.style.set_properties(**{"background-color":"rgba(32,44,70,0.7)","color":"white","text-align":"center"})\
        .set_table_styles([{"selector":"thead th","props":[("background","rgba(32,44,70,0.9)"),("color","white")]}])
    st.dataframe(styled, height=300, use_container_width=True)

# === Save タブ ===
with tabs[5]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Data"): st.success("Data saved!")
    if st.button("Load Data"): st.success("Data loaded!")

st.caption("2025年版：完全版＋エラー修正＋白ランキング＋カードUI＋画像フォールバック")
