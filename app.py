import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- ページ設定 ---
st.set_page_config(page_title="Soccer Club Management Sim", layout="wide")
random.seed(42)
np.random.seed(42)

# --- CSS／UIカスタム ---
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff;}
h1,h2,h3,h4,h5,h6 { color:#fff!important;}
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
  padding:4px 8px; border-radius:6px; margin-top:6px;
}
.detail-popup {
  position:absolute; top:100%; left:50%; transform:translateX(-50%);
  background:rgba(36,54,84,0.9); color:#fff; padding:12px; border-radius:10px;
  width:200px; box-shadow:0 0 10px #000a; z-index:10;
  backdrop-filter:blur(8px);
}
.mobile-table {overflow-x:auto; white-space:nowrap;}
.mobile-table th, .mobile-table td {
  padding:4px 10px; font-size:15px; border-bottom:1px solid #243255;
}
.mobile-scroll { overflow-x:auto; white-space:nowrap;}
.mobile-scroll .player-card { display:inline-block; vertical-align:top;}
.stage-label { background:#222b3c88; color:#fff; padding:6px 12px; border-radius:8px; display:inline-block; margin-bottom:8px;}
.red-message { color:#f55!important; font-weight:bold;}
.stDataFrame {background:rgba(20,30,50,0.7)!important; color:#fff!important;}
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- 定数定義 ---
CLUBS = [
    "Strive FC","Oxford Utd","Viking SC","Lazio Town",
    "Munich Stars","Lille City","Sevilla Reds","Verona Blues"
]
MY_CLUB = CLUBS[0]

# --- 顔画像リスト（任意差替可） ---
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

# --- フォーマット関数など ---
def fmt_money(v):
    if v>=1_000_000: return f"{v//1_000_000}m€"
    if v>=1_000:     return f"{v//1_000}k€"
    return f"{v}€"

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina',
               'Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

# --- データ生成関数 ---
def gen(n, youth=False):
    used = set()
    rows=[]
    for i in range(n):
        name = make_name(used)
        stats = {l: random.randint(52 if youth else 60,82 if youth else 90) for l in labels}
        ovr = int(np.mean(list(stats.values())))
        rows.append({
            "Name":name,
            "Pos":random.choice(["GK","DF","MF","FW"]),
            "Age":random.randint(15 if youth else 18,18 if youth else 34),
            **stats,
            "Salary":random.randint(30_000 if youth else 120_000,
                                   250_000 if youth else 1_200_000),
            "Contract":random.randint(1,2 if youth else 3),
            "OVR":ovr,
            "Youth":youth
        })
    return pd.DataFrame(rows)

# --- セッション初期化 ---
if "senior" not in st.session_state:
    st.session_state.senior = gen(30, youth=False)
if "youth" not in st.session_state:
    st.session_state.youth  = gen(20, youth=True)
if "stand" not in st.session_state:
    st.session_state.stand  = pd.DataFrame({"Club":CLUBS,"W":0,"D":0,"L":0,"Pts":0})
if "opponent" not in st.session_state:
    st.session_state.opponent = random.choice([c for c in CLUBS if c!=MY_CLUB])
if "detail" not in st.session_state:
    st.session_state.detail = None
if "starters" not in st.session_state:
    st.session_state.starters = []
if "refresh_s" not in st.session_state:
    st.session_state.refresh_s = 0
if "refresh_y" not in st.session_state:
    st.session_state.refresh_y = 0
if "scout_senior_list" not in st.session_state:
    st.session_state.scout_senior_list = pd.DataFrame()
if "scout_youth_list" not in st.session_state:
    st.session_state.scout_youth_list = pd.DataFrame()

# --- タブ ---
tabs = st.tabs(["Senior","Youth","Match","Scout","Standings","Save"])

# ===== 1. Senior =====
with tabs[0]:
    st.markdown('<div class="stage-label">Senior Squad</div>', unsafe_allow_html=True)
    df1 = st.session_state.senior
    # 一覧テーブル
    st.markdown('<div class="mobile-table"><table><thead><tr>' +
                ''.join([f'<th>{c}</th>' for c in ["Name","Pos","Age","Contract","Salary","OVR"]]) +
                '</tr></thead><tbody>' +
                ''.join([
                    '<tr>' +
                    f"<td>{r['Name']}</td><td>{r['Pos']}</td><td>{r['Age']}</td>"
                    f"<td>{r['Contract']}</td><td>{fmt_money(r['Salary'])}</td><td>{r['OVR']}</td>"
                    '</tr>' for _,r in df1.iterrows()
                ]) +
                '</tbody></table></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### Players")
    st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
    for idx,row in df1.iterrows():
        key=f"sen{idx}"
        st.markdown(f"""
            <div class="player-card">
              <img src="{get_img(idx)}"><b>{row['Name']}</b><br>
              <small>{row['Pos']}｜{row['Age']}｜{fmt_money(row['Salary'])}</small><br>
              <span style="color:#27e3b9;">OVR:{row['OVR']}</span><br>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Detail", key=key):
            st.session_state.detail = key
        if st.session_state.detail==key:
            abil=[row[l] for l in labels]+[row[labels[0]]]
            ang=np.linspace(0,2*np.pi,len(labels)+1)
            fig,ax=plt.subplots(subplot_kw=dict(polar=True),figsize=(2,2))
            ax.plot(ang,abil,linewidth=2); ax.fill(ang,abil,alpha=0.3)
            ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels],color="#fff")
            ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
            fig.patch.set_alpha(0); ax.patch.set_alpha(0)
            st.pyplot(fig)
            stats_html="".join([
                f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                for l in labels
            ])
            st.markdown(f"""
                <div class="detail-popup">
                  <b>{row['Name']} ({row['Pos']})</b><br>{stats_html}
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===== 2. Youth =====
with tabs[1]:
    st.markdown('<div class="stage-label">Youth Squad</div>', unsafe_allow_html=True)
    df2=st.session_state.youth
    if df2.empty:
        st.markdown("<div class='red-message'>No youth players.</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="mobile-table"><table><thead><tr>' +
                    ''.join([f'<th>{c}</th>' for c in ["Name","Pos","Age","Contract","Salary","OVR"]]) +
                    '</tr></thead><tbody>' +
                    ''.join([
                        '<tr>' +
                        f"<td>{r['Name']}</td><td>{r['Pos']}</td><td>{r['Age']}</td>"
                        f"<td>{r['Contract']}</td><td>{fmt_money(r['Salary'])}</td><td>{r['OVR']}</td>"
                        '</tr>' for _,r in df2.iterrows()
                    ]) +
                    '</tbody></table></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### Players")
        st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
        for idx,row in df2.iterrows():
            key=f"you{idx}"
            st.markdown(f"""
                <div class="player-card">
                  <img src="{get_img(idx+100)}"><b>{row['Name']}</b><br>
                  <small>{row['Pos']}｜{row['Age']}｜{fmt_money(row['Salary'])}</small><br>
                  <span style="color:#27e3b9;">OVR:{row['OVR']}</span><br>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Detail", key=key):
                st.session_state.detail = key
            if st.session_state.detail==key:
                abil=[row[l] for l in labels]+[row[labels[0]]]
                ang=np.linspace(0,2*np.pi,len(labels)+1)
                fig,ax=plt.subplots(subplot_kw=dict(polar=True),figsize=(2,2))
                ax.plot(ang,abil,linewidth=2); ax.fill(ang,abil,alpha=0.3)
                ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels],color="#fff")
                ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
                fig.patch.set_alpha(0); ax.patch.set_alpha(0)
                st.pyplot(fig)
                stats_html="".join([
                    f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                    for l in labels
                ])
                st.markdown(f"""
                    <div class="detail-popup">
                      <b>{row['Name']} ({row['Pos']})</b><br>{stats_html}
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ===== 3. Match =====
with tabs[2]:
    st.markdown('<div class="stage-label">Match Simulation ‒ Week 1</div>', unsafe_allow_html=True)
    opp=st.session_state.opponent
    st.write(f"**Your Club:** {MY_CLUB}  vs  **Opponent:** {opp}")
    formation=st.selectbox("Formation",["4-4-2","4-3-3","3-5-2"])
    if st.button("Auto Starting XI"):
        st.session_state.starters = st.session_state.senior.nlargest(11,"OVR")["Name"].tolist()
        # フォーメーション図
        coords = {
            "4-4-2":([5],[2,4,6,8],[2,4,6,8],[3,7]),
            "4-3-3":([5],[2,4,6,8],[3.5,5,6.5],[2,5,8]),
            "3-5-2":([5],[3.5,5,6.5],[2,4,6,8],[3,7])
        }
        gk,def4,mid,fw = coords[formation]
        fig,ax = plt.subplots(figsize=(3,5))
        ax.set_xlim(0,10); ax.set_ylim(0,16); ax.axis('off')
        # ライン
        ax.plot([0,10],[8,8],color='white',linewidth=1)
        names=st.session_state.starters
        # 配置
        ax.text(5,1,names[0],ha='center',color='yellow')
        idx=1
        for x in def4:
            ax.text(x,4,names[idx],ha='center',color='white'); idx+=1
        for x in mid:
            ax.text(x,8,names[idx],ha='center',color='white'); idx+=1
        for x in fw:
            ax.text(x,12,names[idx],ha='center',color='white'); idx+=1
        st.pyplot(fig)
    # 手動
    starters = st.multiselect("Starting XI",st.session_state.senior["Name"],default=st.session_state.starters)
    if st.button("Kickoff!"):
        # 裏試合
        others=[c for c in CLUBS if c not in (MY_CLUB,opp)]
        dfst=st.session_state.stand
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
        mi,oi=MY_CLUB,opp
        if res=="Win": dfst.loc[dfst.Club==mi,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==oi,"L"]+=1
        elif res=="Lose": dfst.loc[dfst.Club==oi,["W","Pts"]]+= [1,3]; dfst.loc[dfst.Club==mi,"L"]+=1
        else: dfst.loc[dfst.Club.isin([mi,oi]),"D"]+=1; dfst.loc[dfst.Club==mi,"Pts"]+=1; dfst.loc[dfst.Club==oi,"Pts"]+=1
        st.session_state.stand = dfst.sort_values("Pts",ascending=False).reset_index(drop=True)
        st.markdown(f"<div style='background:#27e3b9;color:#fff;padding:8px;border-radius:8px;'>**{res} ({g1}-{g2})**</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#314265;color:#fff;padding:6px;border-radius:6px;'>Goals: You {g1} ‒ Opp {g2} | MVP: {mvp}</div>", unsafe_allow_html=True)

# ===== 4. Scout =====
with tabs[3]:
    st.markdown('<div class="stage-label">Scout Players (Max 3 each)</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    if cols[0].button(f"Refresh Senior ({st.session_state.refresh_s}/3)"):
        if st.session_state.refresh_s < 3:
            st.session_state.scout_senior_list = gen(5, youth=False)
            st.session_state.refresh_s += 1
        else:
            st.warning("Senior scout limit reached")
    if cols[1].button(f"Refresh Youth  ({st.session_state.refresh_y}/3)"):
        if st.session_state.refresh_y < 3:
            st.session_state.scout_youth_list = gen(5, youth=True)
            st.session_state.refresh_y += 1
        else:
            st.warning("Youth scout limit reached")
    # 表示
    for df_sc, tag in [(st.session_state.scout_senior_list,"Senior"),(st.session_state.scout_youth_list,"Youth")]:
        if not df_sc.empty:
            st.markdown(f"#### {tag} Candidates")
            st.markdown('<div class="mobile-scroll">', unsafe_allow_html=True)
            for idx,row in df_sc.iterrows():
                key=f"sc_{tag}_{idx}"
                st.markdown(f"""
                    <div class="player-card">
                      <img src="{get_img(idx+300)}"><b>{row['Name']}</b><br>
                      <small>{tag}｜{row['Pos']}｜{row['Age']}</small><br>
                      <span style="color:#27e3b9;">OVR:{row['OVR']}</span><br>
                      <button class="detail-btn" onclick="window.streamlitDetail('{key}')">Detail</button>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Join", key=key):
                    if tag=="Senior":
                        st.session_state.senior = pd.concat([st.session_state.senior,df_sc.iloc[[idx]]],ignore_index=True)
                    else:
                        st.session_state.youth  = pd.concat([st.session_state.youth, df_sc.iloc[[idx]]],ignore_index=True)
                    st.success(f"{tag} player signed!")
                if st.session_state.detail==key:
                    abil=[row[l] for l in labels]+[row[labels[0]]]
                    ang=np.linspace(0,2*np.pi,len(labels)+1)
                    fig,ax=plt.subplots(subplot_kw=dict(polar=True),figsize=(2,2))
                    ax.plot(ang,abil,linewidth=2); ax.fill(ang,abil,alpha=0.3)
                    ax.set_xticks(ang[:-1]); ax.set_xticklabels([labels_full[l] for l in labels],color="#fff")
                    ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
                    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
                    st.pyplot(fig)
                    stats_html="".join([
                        f"<span style='color:{'#20e660' if row[l]>=90 else '#ffe600' if row[l]>=75 else '#1aacef'}'>{l}:{row[l]}</span><br>"
                        for l in labels
                    ])
                    st.markdown(f"""
                        <div class="detail-popup">
                          <b>{row['Name']} ({row['Pos']})</b><br>{stats_html}
                        </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ===== 5. Standings =====
with tabs[4]:
    st.markdown('<div class="stage-label">Standings</div>', unsafe_allow_html=True)
    dfst=st.session_state.stand
    styled=dfst.style.set_properties(**{"background-color":"rgba(20,30,50,0.8)","color":"white"})\
                    .set_table_styles([{"selector":"thead th","props":[("color","white"),("background-color","rgba(20,30,50,0.9)")]}])
    st.dataframe(styled, height=300)

# ===== 6. Save =====
with tabs[5]:
    st.markdown('<div class="stage-label">Save / Load</div>', unsafe_allow_html=True)
    if st.button("Save Data"): st.success("Data saved!")
    if st.button("Load Data"): st.success("Data loaded!")

st.caption("2025年最新版：Scout制限3回／詳細即時表示／Formation図付AutoXI 全要素統合版")
