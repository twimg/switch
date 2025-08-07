import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import pickle
from datetime import datetime
from collections import defaultdict

# --- ページ設定 ---
st.set_page_config(page_title="Club Strive", layout="wide")
random.seed(42)
np.random.seed(42)

# --- CSS/UIカスタム ---
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }
h1,h2,h3,h4,h5,h6 { color:#fff!important; }
.section-box { background:rgba(20,30,50,0.8); padding:8px 12px; border-radius:8px; margin-bottom:8px; }
.stButton>button, .save-button>button { background:#27e3b9!important; color:#202b41!important; font-weight:bold; border-radius:8px; padding:6px 12px; }
.stButton>button:active, .save-button>button:active { background:#ffee99!important; }
.stDataFrame td, .stDataFrame th { background:rgba(20,30,50,0.7)!important; color:#fff!important; }
</style>
""", unsafe_allow_html=True)

st.title("🌟 Club Strive 🌟")

# --- 定数 ---
SEASON_WEEKS = 14
ABILITY_KEYS = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
ABILITY_JP = {'Spd':'走力','Pas':'パス','Phy':'フィジカル','Sta':'スタミナ','Def':'守備','Tec':'テクニック','Men':'メンタル','Sht':'シュート','Pow':'パワー'}
TACTICS = {"4-4-2":("FW",2,"MF",4,"DF",4,"GK",1), "4-3-3":("FW",3,"MF",3,"DF",4,"GK",1),"3-5-2":("FW",2,"MF",5,"DF",3,"GK",1)}

# --- 名前プール ---
GIVEN = {
    'ENG': ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
            "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin"],
    'FRA': ["Hugo","Lucas","Adam","Gabriel","Léo","Louis","Raphaël","Arthur","Paul","Maël",
            "Victor","Nathan","Enzo","Clément","Mathis","Julien","Maxime","Tom","Romain","Antoine"],
    # ... 他国も30ずつ用意 ...
}
SURNAME = {
    'ENG': ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
            "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris"],
    'FRA': ["Martin","Bernard","Thomas","Petit","Robert","Richard","Durand","Dubois","Moreau","Laurent",
            "Simon","Michel","Lefebvre","Leroy","Roux","David","Bertrand","Morel","Fournier","Girard"],
    # ... 他国も30ずつ用意 ...
}

def make_name(nat, used):
    while True:
        name = f"{random.choice(GIVEN[nat])} {random.choice(SURNAME[nat])}"
        if name not in used:
            used.add(name)
            return name

def fmt_money(v):
    if v>=1_000_000: return f"{v//1_000_000}m€"
    if v>=1_000:     return f"{v//1_000}k€"
    return f"{v}€"

def gen_players(n, youth=False):
    used = set()
    rows = []
    for _ in range(n):
        nat = random.choice(list(GIVEN.keys()))
        name = make_name(nat, used)
        stats = {k:random.randint(52 if youth else 60,82 if youth else 90) for k in ABILITY_KEYS}
        ovr = int(np.mean(list(stats.values())))
        rows.append({
            "Name": name,
            "Nat": nat,
            "Pos": random.choice(["GK","DF","MF","FW"]),
            "Age": random.randint(15 if youth else 18,18 if youth else 34),
            **stats,
            "OVR": ovr,
            "Salary": random.randint(30_000 if youth else 120_000,250_000 if youth else 1_200_000),
            "Club": None,
            "PlayStyle": random.sample(["職人","チーム至上主義","爆発型","頭脳派","感情型","インナートライアンフ"], k=2),
            "intl_caps": 0,
            "status":"通常"
        })
    return pd.DataFrame(rows)

# --- セッション初期化 ---
if "ses" not in st.session_state:
    st.session_state.ses = st.session_state  # alias
ses = st.session_state.ses

for attr in ["senior","youth","scout","leagues","club_map","standings","finance_log","week","starters","intl_tournament","world_cup","sns_times","sns_posts","save_slots"]:
    if attr not in ses:
        setattr(ses, attr, pd.DataFrame() if attr in ["senior","youth","scout","standings"] else ([] if attr in ["finance_log","starters","sns_times","sns_posts"] else {} if attr in ["leagues","club_map","save_slots"] else 1 if attr=="week" else None))

ses.my_club = "Signature Team"

# =========================
# 第3部：リーグ生成 & クラブマップ作成
# =========================
def setup_leagues():
    nations = list(GIVEN.keys()) + ["BEL","TUR","ARG","URU","COL","USA","MEX","SAU","NGA","MAR","KOR","AUS"]
    clubs_per_div = 16
    for nat in nations:
        ses.leagues[nat] = {}
        for div in ['D1','D2']:
            club_list = [f"{nat}_Club{i+1:02d}" for i in range(clubs_per_div)]
            for c in club_list:
                ses.club_map[c] = (nat,div)
            ses.leagues[nat][div] = club_list

if not ses.leagues:
    setup_leagues()

# =========================
# 第3部：順位表 & 財務ログ初期化
# =========================
def init_standings():
    rows=[]
    for nat, divs in ses.leagues.items():
        for div, clubs in divs.items():
            for club in clubs:
                rows.append({"Nation":nat,"Division":div,"Club":club,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0})
    ses.standings = pd.DataFrame(rows)

def init_finance_log():
    ses.finance_log = [{"week":w,"revenue_ticket":0,"revenue_goods":0,"expenses_salaries":0,"expenses_stadium":0} for w in range(1,SEASON_WEEKS+1)]

init_standings()
init_finance_log()

# =========================
# 第3部：シニア & ユース 選手生成
# =========================
if ses.senior.empty:
    df = gen_players(30, youth=False)
    df['Club'] = ses.my_club
    ses.senior = df

if ses.youth.empty:
    df = gen_players(20, youth=True)
    df['Club'] = ses.my_club
    ses.youth = df

# =========================
# 第3部：国際大会 & 代表戦 初期化
# =========================
ContinentalTournament = lambda **kw: SimpleNamespace(**kw)
WorldCup = lambda **kw: SimpleNamespace(**kw)

def init_intl_tournament():
    eng_d1 = ses.leagues['ENG']['D1'][:4]
    ger_d1 = ses.leagues['GER']['D1'][:4]
    fra_d1 = ses.leagues['FRA']['D1'][:4]
    esp_d1 = ses.leagues['ESP']['D1'][:4]
    ita_d1 = ses.leagues['ITA']['D1'][:4]
    ned_d1 = ses.leagues['NED']['D1'][:4]
    clubs_all = eng_d1+ger_d1+fra_d1+esp_d1+ita_d1+ned_d1
    random.shuffle(clubs_all)
    groups = [clubs_all[i:i+4] for i in range(0,len(clubs_all),4)]
    ses.intl_tournament = ContinentalTournament(
        name="Euro Champions Cup", clubs=clubs_all, groups=groups, results=[], finished=False
    )
    nats = list(ses.leagues.keys())
    random.shuffle(nats)
    wc_groups = [nats[i:i+4] for i in range(0,16,4)]
    ses.world_cup = WorldCup(name="World Cup", nations=nats, groups=wc_groups, results=[], finished=False)

init_intl_tournament()

# SNSフィード初期化
ses.sns_times = []
ses.sns_posts = []

# =========================
# 第4部：ユーティリティ & タブ UI 実装
# =========================

def sort_by_pos(df, reverse=False):
    order = ["GK","DF","MF","FW"]
    df = df.copy()
    df['pos_order'] = df['Pos'].map({p:i for i,p in enumerate(order[::-1] if reverse else order)})
    return df.sort_values(['pos_order','OVR'], ascending=[True,False]).drop(columns='pos_order')

def style_table(df):
    return df.style.set_table_styles([{"selector":"th","props":[("background","rgba(20,30,50,0.8)"),("color","#fff")]}])

def radar_chart(vals, labels):
    ang = np.linspace(0,2*np.pi,len(vals),endpoint=False).tolist()
    vals = vals + [vals[0]]
    ang = np.concatenate((ang,[ang[0]]))
    fig,ax = plt.subplots(subplot_kw=dict(polar=True),figsize=(3,3))
    ax.plot(ang,vals,linewidth=2, color="cyan"); ax.fill(ang,vals,alpha=0.25, color="cyan")
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels, color="#eaf6ff")
    ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    return fig

def auto_select(formation):
    req = TACTICS[formation]
    sel=[]
    for i in range(0,len(req),2):
        pos=count=req[i+1]
        pool = ses.senior[ses.senior["Pos"]==req[i]]
        sel += pool.nlargest(count,"OVR")["Name"].tolist()
    return sel

def play_match(our, opp):
    ga,gb = random.randint(0,3), random.randint(0,3)
    scorers = random.sample(our, ga) if ga>0 else []
    assisters = random.sample(our, min(len(our),gb)) if gb>0 else []
    stats = {"shots":random.randint(5,15),"on_target":random.randint(1,ga+2),"possession":random.randint(40,60)}
    return ({"score":f"{ga}-{gb}","scorers":scorers,"assisters":assisters}, stats)

def sort_table(df):
    return df.sort_values(["Nation","Division","Pts"], ascending=[True,True,False]).reset_index(drop=True)

def show_leaderboard(df):
    topG = df.nlargest(10,"GF")[["Club","GF"]].rename(columns={"GF":"G"})
    topA = df.nlargest(10,"GA")[["Club","GA"]].rename(columns={"GA":"A"})
    st.write("**得点王 TOP10**"); st.table(topG)
    st.write("**アシスト王 TOP10**"); st.table(topA)
    # ベスト11 は省略

def gen_scout(cat):
    pool = ses.youth if cat=="ユース候補" else ses.senior
    return pool.sample(5)

def round_value(v):
    if v<1_000: return int(round(v/5)*5)
    return v - (v%1_000)

def contract_player(p):
    ses.senior = pd.concat([ses.senior, pd.DataFrame([p])], ignore_index=True)
    st.success(f"{p['Name']} を獲得しました。")

def manage_rentals():
    st.write("レンタル機能: 実装中")

def show_awards():
    st.write("年間表彰: MVP, 得点王など")

def render_continental():
    st.write("🏆 Euro Champions Cup グループステージ")
    # 省略

def render_worldcup():
    st.write("🌍 World Cup グループステージ")
    # 省略

def simulate_international():
    st.write("代表戦: 対戦シミュレーション中")
    # 省略

# --- タブ 定義 ---
tabs = st.tabs([
    "シニア","ユース","選手詳細","試合","順位表",
    "スカウト/移籍","レンタル管理","SNS","財務レポート",
    "年間表彰","国際大会","ワールドカップ","代表戦","設定"
])

# 1) シニア選手タブ
with tabs[0]:
    st.markdown('<div class="section-box"><h3>シニア選手一覧</h3></div>', unsafe_allow_html=True)
    st.dataframe(style_table(sort_by_pos(ses.senior)[["Name","Nat","Pos","Age","OVR","Club"]]))

# 2) ユース選手タブ
with tabs[1]:
    st.markdown('<div class="section-box"><h3>ユース選手一覧</h3></div>', unsafe_allow_html=True)
    st.dataframe(style_table(sort_by_pos(ses.youth)[["Name","Nat","Pos","Age","OVR","Club"]]))

# 3) 選手詳細タブ
with tabs[2]:
    st.markdown('<div class="section-box"><h3>選手詳細</h3></div>', unsafe_allow_html=True)
    allp = pd.concat([ses.senior, ses.youth], ignore_index=True)
    sel = st.selectbox("選手選択", allp["Name"].tolist())
    p = allp[allp["Name"]==sel].iloc[0]
    st.write(f"ポジション: {p.Pos} / OVR: {p.OVR} / 年齢: {p.Age}")
    st.write(f"国籍: {p.Nat} / 国際大会出場: {p.intl_caps}回")
    st.write(f"所属: {p.Club} / 状態: {p.status}")
    st.write(f"プレースタイル: {', '.join(p.PlayStyle)}")
    fig = radar_chart([p[k] for k in ABILITY_KEYS], [ABILITY_JP[k] for k in ABILITY_KEYS])
    st.pyplot(fig)

# 4) 試合タブ
with tabs[3]:
    st.markdown(f'<div class="section-box"><h3>試合 ‒ 第{ses.week}節</h3></div>', unsafe_allow_html=True)
    opp = random.choice([c for c in ses.club_map if ses.club_map[c][0]==ses.club_map[ses.my_club][0] and c!=ses.my_club])
    st.write(f"⚽ {ses.my_club} vs {opp}")
    formation = st.selectbox("フォーメーション", list(TACTICS.keys()))
    if st.button("オート先発選考"):
        ses.starters = auto_select(formation)
    if ses.starters:
        st.write("[先発メンバー]")
        st.dataframe(style_table(pd.DataFrame({'Name':ses.starters})))
    if st.button("キックオフ!", disabled=not ses.starters):
        res, stats = play_match(ses.starters, opp)
        st.success(f"結果: {res['score']} | 得点者: {','.join(res['scorers'])} | アシスト: {','.join(res['assisters'])}")
        st.write(f"シュート: {stats['shots']} 枠内: {stats['on_target']} ポゼッション: {stats['possession']}%")

# 5) 順位表タブ
with tabs[4]:
    st.markdown('<div class="section-box"><h3>順位表 & ランキング</h3></div>', unsafe_allow_html=True)
    st.dataframe(style_table(sort_table(ses.standings)))
    show_leaderboard(ses.standings)

# 6) スカウトタブ
with tabs[5]:
    st.markdown('<div class="section-box"><h3>スカウト / 移籍</h3></div>', unsafe_allow_html=True)
    sel = st.radio("対象カテゴリー", ["シニア候補","ユース候補"])
    if st.button("候補リスト更新"):
        ses.scout = gen_scout(sel)
    if ses.scout.empty:
        st.info("候補がいません。リスト更新を押してください。")
    else:
        dfsc = sort_by_pos(ses.scout.copy())
        dfsc["評価額"] = dfsc["Salary"].map(round_value)
        st.dataframe(style_table(dfsc[["Name","Nat","Pos","Age","OVR","評価額"]]))
        idx = st.number_input("選択行番号",0,len(dfsc)-1)
        if st.button("契約する"):
            contract_player(dfsc.iloc[int(idx)])

# 7) レンタル管理タブ
with tabs[6]:
    st.markdown('<div class="section-box"><h3>レンタル管理</h3></div>', unsafe_allow_html=True)
    manage_rentals()

# 8) SNSタブ
with tabs[7]:
    st.markdown('<div class="section-box"><h3>SNS フィード</h3></div>', unsafe_allow_html=True)
    for t,p in zip(ses.sns_times, ses.sns_posts):
        st.write(f"{t}: {p}")

# 9) 財務レポートタブ
with tabs[8]:
    st.markdown('<div class="section-box"><h3>財務レポート</h3></div>', unsafe_allow_html=True)
    df_fin = pd.DataFrame(ses.finance_log)
    c1,c2 = st.columns([2,1])
    with c1:
        st.line_chart(df_fin.set_index('week')[['revenue_ticket','revenue_goods','expenses_salaries']])
    with c2:
        st.dataframe(style_table(df_fin))

# 10) 年間表彰タブ
with tabs[9]:
    st.markdown('<div class="section-box"><h3>年間表彰</h3></div>', unsafe_allow_html=True)
    show_awards()

# 11) 国際大会タブ
with tabs[10]:
    st.markdown('<div class="section-box"><h3>Euro Champions Cup</h3></div>', unsafe_allow_html=True)
    render_continental()

# 12) ワールドカップタブ
with tabs[11]:
    st.markdown('<div class="section-box"><h3>World Cup</h3></div>', unsafe_allow_html=True)
    render_worldcup()

# 13) 代表戦タブ
with tabs[12]:
    st.markdown('<div class="section-box"><h3>代表戦</h3></div>', unsafe_allow_html=True)
    simulate_international()

# 14) 設定タブ
with tabs[13]:
    st.markdown('<div class="section-box"><h3>クラブ設定／セーブ & ロード</h3></div>', unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1:
        slot = st.text_input("セーブ名を入力")
        if st.button("セーブ"): 
            ses.save_slots[slot] = pickle.dumps(ses)
            st.success(f"ゲームを '{slot}' に保存しました。")
    with col2:
        slot_load = st.text_input("ロード名を入力")
        if st.button("ロード"):
            if slot_load in ses.save_slots:
                st.session_state.ses = pickle.loads(ses.save_slots[slot_load])
                st.experimental_rerun()
            else:
                st.error("その名前のセーブデータはありません。")
