import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import pickle
from types import SimpleNamespace
from datetime import datetime

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

# --- 名前プール（各国30パターンずつ）---
NAME_POOL = {
    'ENG': {
        'first': ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
                  "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin",
                  "Samuel","Ethan","Daniel","Jasper","Matthew","Lewis","David","Michael","Jonathan","Edward"],
        'last':  ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
                  "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris",
                  "Young","King","Wright","Hill","Moore","Allen","Cook","Long","Ward","Morris"]
    },
    'GER': {
        'first': ["Leon","Finn","Elias","Lukas","Jonas","Luis","Noah","Paul","Felix","Maximilian",
                  "Emil","Anton","Jakob","Luca","Moritz","Alexander","Ben","David","Henry","Julian",
                  "Jan","Oskar","Lennard","Theo","Samuel","Jonathan","Mattis","Tim","Philipp","Marvin"],
        'last':  ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Schulz","Hoffmann",
                  "Schäfer","Koch","Bauer","Richter","Klein","Wolf","Schröder","Neumann","Schwarz","Zimmermann",
                  "Braun","Krüger","Hofmann","Hartmann","Lange","Schmitt","Werner","Schmitz","Krause","Meier"]
    },
    'FRA': {
        'first': ["Hugo","Lucas","Adam","Gabriel","Léo","Louis","Raphaël","Arthur","Paul","Maël",
                  "Victor","Nathan","Enzo","Clément","Mathis","Julien","Maxime","Tom","Romain","Antoine",
                  "Benjamin","Ethan","Thomas","Eliott","Arthur","Lilian","Malo","Sacha","Yanis","Aaron"],
        'last':  ["Martin","Bernard","Thomas","Petit","Robert","Richard","Durand","Dubois","Moreau","Laurent",
                  "Simon","Michel","Lefebvre","Leroy","Roux","David","Bertrand","Morel","Fournier","Girard",
                  "Bonnet","Dupont","Lambert","François","Mercier","Dupuis","Blanc","Garnier","Chevalier","Faure"]
    },
    'ESP': {
        'first': ["Hugo","Pablo","Alvaro","Diego","Alejandro","Adrián","Daniel","Martín","José","David",
                  "Javier","Miguel","Iker","Sergio","Juan","Jorge","Luis","Carlos","Raúl","Fran",
                  "Álex","Víctor","Sergi","Rubén","Álvaro","Óscar","Enrique","Iván","Eduardo","Samuel"],
        'last':  ["García","Rodríguez","González","Fernández","López","Martínez","Sánchez","Pérez","Gómez","Martín",
                  "Jiménez","Ruiz","Hernández","Díaz","Moreno","Muñoz","Álvarez","Romero","Alonso","Gutiérrez",
                  "Navarro","Torres","Domínguez","Vázquez","Suárez","Ramírez","Ortega","Ramos","Gil","Delgado"]
    },
    'ITA': {
        'first': ["Luca","Francesco","Alessandro","Leonardo","Mattia","Gabriele","Andrea","Tommaso","Niccolò","Federico",
                  "Riccardo","Matteo","Giuseppe","Antonio","Marco","Simone","Davide","Lorenzo","Stefano","Emanuele",
                  "Daniele","Christian","Alberto","Valerio","Salvatore","Vincenzo","Filippo","Danilo","Pietro","Massimo"],
        'last':  ["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco",
                  "Bruno","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Moretti",
                  "Barbieri","Fontana","Santos","Mariani","Rinaldi","Longo","Martini","Leone","Gentile","Martinelli"]
    },
    'NED': {
        'first': ["Daan","Luca","Mees","Finn","Sem","Levi","Lucas","Luuk","Tijn","Jens",
                  "Thijs","Mats","Sven","Noah","Max","Bram","Julian","Thomas","Sam","Jelle",
                  "Dylano","Ruben","Noud","Milan","Jozua","Gijs","Koen","Stijn","Timo","Jop"],
        'last':  ["de Jong","Jansen","de Vries","van den Berg","Van Dijk","Bakker","Janssen","Visser","Smit","de Boer",
                  "Mulder","Vos","Peters","de Groot","Bos","Vos","Meijer","Veenstra","van der Linden","van Leeuwen",
                  "Kramer","de Wit","de Graaf","van der Meer","Dekker","Brouwer","Schouten","Hoekstra","van Dongen","Fischer"]
    },
    # 以下、その他各国（BEL/TUR/ARG/URU/COL/USA/MEX/SAU/NGA/MAR/KOR/AUS/BRA/POR）も同様に30ずつ用意…
}

def make_name(nat, used):
    while True:
        fn = random.choice(NAME_POOL[nat]['first'])
        ln = random.choice(NAME_POOL[nat]['last'])
        name = f"{fn} {ln}"
        if name not in used:
            used.add(name)
            return name

# --- セッション初期化 ---
if "ses" not in st.session_state:
    st.session_state.ses = st.session_state
ses = st.session_state.ses

# 各種ストレージを初期化
for attr, default in [
    ("senior", None), ("youth", None), ("scout", None),
    ("leagues", {}), ("club_map", {}), ("standings", None),
    ("finance_log", None), ("week", 1), ("starters", []),
    ("intl_tournament", None), ("world_cup", None),
    ("sns_times", []), ("sns_posts", []), ("save_slots", {})
]:
    if not hasattr(ses, attr):
        setattr(ses, attr, default)

ses.my_club = "Signature Team"

# --- ユーティリティ関数 ---
def fmt_money(v):
    if v>=1_000_000: return f"{v//1_000_000}m€"
    if v>=1_000:     return f"{v//1_000}k€"
    return f"{v}€"

def gen_players(n, youth=False):
    used = set()
    rows = []
    for _ in range(n):
        nat = random.choice(list(NAME_POOL.keys()))
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
            "Club": ses.my_club,
            "PlayStyle": random.sample(
                ["職人","チーム至上主義","爆発型","頭脳派","感情型","クロスハンター","チャンスメイカー"], k=2),
            "intl_caps": 0,
            "status":"通常"
        })
    return pd.DataFrame(rows)

# --- リーグ＆クラブマップ生成 ---
def setup_leagues():
    NATIONS = [
        'ENG','GER','FRA','ESP','ITA','NED','BEL','TUR',
        'ARG','URU','COL','USA','MEX','SAU','NGA','MAR',
        'KOR','AUS','BRA','POR'
    ]
    for nat in NATIONS:
        ses.leagues[nat] = {}
        for div in ['D1','D2']:
            clubs = [f"{nat}_Club{i+1:02d}" for i in range(16)]
            ses.leagues[nat][div] = clubs
            for c in clubs:
                ses.club_map[c] = (nat, div)

if not ses.leagues:
    setup_leagues()

# --- 順位表 & 財務ログ初期化 ---
def init_standings():
    rows = []
    for nat, divs in ses.leagues.items():
        for div, clubs in divs.items():
            for club in clubs:
                rows.append({**{"Nation":nat,"Division":div,"Club":club}, **{"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0}})
    ses.standings = pd.DataFrame(rows)

def init_finance():
    ses.finance_log = [{"week":w,"revenue_ticket":0,"revenue_goods":0,"expenses_salaries":0} for w in range(1, SEASON_WEEKS+1)]

if ses.standings is None:
    init_standings()
if ses.finance_log is None:
    init_finance()

# --- シニア & ユース選手生成 ---
if ses.senior is None:
    ses.senior = gen_players(30, youth=False)
if ses.youth is None:
    ses.youth = gen_players(20, youth=True)

# --- 国際大会 & ワールドカップ初期化 ---
def init_intl():
    clubs = []
    for nat in ['ENG','GER','FRA','ESP','ITA','NED']:
        clubs += ses.leagues[nat]['D1'][:4]
    random.shuffle(clubs)
    groups = [clubs[i:i+4] for i in range(0, len(clubs), 4)]
    ses.intl_tournament = SimpleNamespace(name="Euro Champions Cup", clubs=clubs, groups=groups, results=[], finished=False)

def init_wc():
    nats = list(ses.leagues.keys())
    random.shuffle(nats)
    groups = [nats[i:i+4] for i in range(0,16,4)]
    ses.world_cup = SimpleNamespace(name="World Cup", nations=nats[:16], groups=groups, results=[], finished=False)

if ses.intl_tournament is None:
    init_intl()
if ses.world_cup is None:
    init_wc()

# --- 表示用ユーティリティ ---
def sort_by_pos(df, reverse=False):
    order = ["GK","DF","MF","FW"]
    df = df.copy()
    df['o'] = df['Pos'].map({p:i for i,p in enumerate(order[::-1] if reverse else order)})
    return df.sort_values(['o','OVR'], ascending=[True,False]).drop(columns='o')

def style_table(df):
    return df.style.set_table_styles([{"selector":"th","props":[("background","rgba(20,30,50,0.8)"),("color","#fff")]}])

def radar_chart(vals, labels):
    angles = np.linspace(0,2*np.pi,len(vals),endpoint=False).tolist()
    vals = vals + [vals[0]]; angles = np.concatenate((angles,[angles[0]]))
    fig,ax = plt.subplots(subplot_kw=dict(polar=True),figsize=(3,3))
    ax.plot(angles,vals,linewidth=2,color="cyan"); ax.fill(angles,vals,alpha=0.25,color="cyan")
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, color="#eaf6ff"); ax.set_yticklabels([]); ax.grid(color="#fff",alpha=0.2)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    return fig

def auto_select(formation):
    req = TACTICS[formation]
    sel=[]
    for i in range(0,len(req),2):
        pos,count = req[i], req[i+1]
        pool = ses.senior[ses.senior.Pos==pos]
        sel += pool.nlargest(count,"OVR").Name.tolist()
    return sel

def play_match(our,opp):
    ga,gb = random.randint(0,3),random.randint(0,3)
    scorers = random.sample(our, ga) if ga>0 else []
    assisters= random.sample(our,min(len(our),gb)) if gb>0 else []
    stats={"shots":random.randint(5,15),"on":random.randint(1,ga+2),"pos":random.randint(40,60)}
    return {"score":f"{ga}-{gb}","scorers":scorers,"assisters":assisters}, stats

# --- タブ定義 ---
tabs = st.tabs([
    "シニア","ユース","選手詳細","試合","順位表",
    "スカウト/移籍","レンタル","SNS","財務","年間表彰",
    "欧州ＣＬ","ワールドＣ","代表戦","設定"
])

# 1) シニア
with tabs[0]:
    st.markdown('<div class="section-box"><h3>シニア選手一覧</h3></div>',unsafe_allow_html=True)
    st.dataframe(style_table(sort_by_pos(ses.senior)[["Name","Nat","Pos","Age","OVR","Club"]]))

# 2) ユース
with tabs[1]:
    st.markdown('<div class="section-box"><h3>ユース選手一覧</h3></div>',unsafe_allow_html=True)
    st.dataframe(style_table(sort_by_pos(ses.youth)[["Name","Nat","Pos","Age","OVR","Club"]]))

# 3) 選手詳細
with tabs[2]:
    st.markdown('<div class="section-box"><h3>選手詳細</h3></div>',unsafe_allow_html=True)
    allp = pd.concat([ses.senior,ses.youth],ignore_index=True)
    sel = st.selectbox("選手選択", allp.Name.tolist())
    p=allp[allp.Name==sel].iloc[0]
    st.write(f"Pos:{p.Pos} / OVR:{p.OVR} / Age:{p.Age}")
    st.write(f"Nat:{p.Nat} / IntlCaps:{p.intl_caps}")
    st.write(f"Club:{p.Club} / 状態:{p.status}")
    st.write(f"PlayStyle:{','.join(p.PlayStyle)}")
    fig=radar_chart([p[k] for k in ABILITY_KEYS],[ABILITY_JP[k] for k in ABILITY_KEYS])
    st.pyplot(fig)

# 4) 試合
with tabs[3]:
    st.markdown(f'<div class="section-box"><h3>試合 第{ses.week}節</h3></div>',unsafe_allow_html=True)
    opp = random.choice([c for c,(n,_) in ses.club_map.items() if n==ses.club_map[ses.my_club][0] and c!=ses.my_club])
    st.write(f"{ses.my_club} vs {opp}")
    form = st.selectbox("フォーメーション", list(TACTICS.keys()))
    if st.button("オート先発選考"):
        ses.starters = auto_select(form)
    if ses.starters:
        st.write("先発")
        st.dataframe(pd.DataFrame({"Name":ses.starters}))
    if st.button("キックオフ",disabled=not ses.starters):
        res,sts = play_match(ses.starters,opp)
        st.success(f"Result:{res['score']} Scorers:{','.join(res['scorers'])} Assists:{','.join(res['assisters'])}")
        st.write(f"Shots:{sts['shots']} OnTarget:{sts['on']} Poss:{sts['pos']}%")

# 5) 順位表
with tabs[4]:
    st.markdown('<div class="section-box"><h3>順位表 & ランキング</h3></div>',unsafe_allow_html=True)
    df=ses.standings.copy().sort_values(["Nation","Division","Pts"],ascending=[True,True,False])
    st.dataframe(style_table(df))
    topG=df.nlargest(10,"GF")[["Club","GF"]].rename(columns={"GF":"G"})
    st.write("得点王"); st.table(topG)
    topA=df.nlargest(10,"GA")[["Club","GA"]].rename(columns={"GA":"A"})
    st.write("アシスト王"); st.table(topA)

# 6) スカウト/移籍
with tabs[5]:
    st.markdown('<div class="section-box"><h3>スカウト / 移籍</h3></div>',unsafe_allow_html=True)
    cat=st.radio("カテゴリー",["シニア候補","ユース候補"])
    if st.button("候補更新"):
        ses.scout = gen_players(5, youth=(cat=="ユース候補"))
    if ses.scout is not None:
        df=sort_by_pos(ses.scout.copy())
        df["評価額"]=df.Salary.map(lambda v: (v if v>=1000 else round(v/5)*5)//1)
        st.dataframe(style_table(df[["Name","Nat","Pos","Age","OVR","評価額"]]))
        idx=st.number_input("行番号",0,len(df)-1)
        if st.button("契約"):
            p=df.iloc[int(idx)].to_dict()
            ses.senior=pd.concat([ses.senior,pd.DataFrame([p])],ignore_index=True)
            st.success(f"{p['Name']} 獲得")

# 7) レンタル
with tabs[6]:
    st.markdown('<div class="section-box"><h3>レンタル管理</h3></div>',unsafe_allow_html=True)
    st.write("レンタル機能: 実装中")

# 8) SNS
with tabs[7]:
    st.markdown('<div class="section-box"><h3>SNS フィード</h3></div>',unsafe_allow_html=True)
    for t,p in zip(ses.sns_times,ses.sns_posts):
        st.write(f"{t}: {p}")

# 9) 財務
with tabs[8]:
    st.markdown('<div class="section-box"><h3>財務レポート</h3></div>',unsafe_allow_html=True)
    df_fin=pd.DataFrame(ses.finance_log)
    c1,c2=st.columns([2,1])
    with c1:
        st.line_chart(df_fin.set_index("week")[["revenue_ticket","revenue_goods","expenses_salaries"]])
    with c2:
        st.dataframe(style_table(df_fin))

# 10) 年間表彰
with tabs[9]:
    st.markdown('<div class="section-box"><h3>年間表彰</h3></div>',unsafe_allow_html=True)
    st.write("MVP, 得点王... 実装中")

# 11) 欧州ＣＬ
with tabs[10]:
    st.markdown('<div class="section-box"><h3>Euro Champions Cup</h3></div>',unsafe_allow_html=True)
    st.write("グループステージ表示... 実装中")

# 12) ワールドＣ
with tabs[11]:
    st.markdown('<div class="section-box"><h3>World Cup</h3></div>',unsafe_allow_html=True)
    st.write("グループステージ表示... 実装中")

# 13) 代表戦
with tabs[12]:
    st.markdown('<div class="section-box"><h3>代表戦</h3></div>',unsafe_allow_html=True)
    st.write("シミュレーション... 実装中")

# 14) 設定
with tabs[13]:
    st.markdown('<div class="section-box"><h3>設定／セーブ&ロード</h3></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        name=st.text_input("セーブ名")
        if st.button("セーブ"):
            ses.save_slots[name]=pickle.dumps(ses)
            st.success(f"保存: {name}")
    with c2:
        name2=st.text_input("ロード名")
        if st.button("ロード"):
            if name2 in ses.save_slots:
                st.session_state.ses=pickle.loads(ses.save_slots[name2])
                st.experimental_rerun()
            else:
                st.error("未登録セーブ名です")
