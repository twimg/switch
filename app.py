import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime
import pandas.api.types as ptypes

# ---------------- 基本設定 ----------------
MY_CLUB_DEFAULT = "Signature Team"
SEASON_WEEKS = 14
ABILITY_KEYS = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']

random.seed(42)
np.random.seed(42)

# 文字化け対策（matplotlib）
plt.rcParams['font.family'] = ['IPAexGothic','Meiryo','Noto Sans CJK JP','DejaVu Sans']

# ページ設定 & CSS
st.set_page_config(page_title="Club Strive", layout="wide")
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }
.stButton>button { background:#27e3b9!important; color:#202b41!important; font-weight:bold; border-radius:10px; margin:6px 0; }
.stButton>button:active { background:#ffee99!important; }
</style>
""", unsafe_allow_html=True)

st.title("Club Strive")

# ポジション並び順
def sort_by_pos(df, reverse=False):
    order = ['GK','DF','MF','FW']
    if reverse:
        order = list(reversed(order))
    cat = ptypes.CategoricalDtype(order, ordered=True)
    return df.assign(_p=df['Pos'].astype(cat))\
             .sort_values(['_p','OVR'], ascending=[True,False])\
             .drop(columns='_p')

def make_highlighter(column, value):
    def _func(row):
        return ['background-color:#f7df70;color:#202b41;font-weight:bold' if row[column]==value else '' for _ in row]
    return _func

def style_playstyle(col):
    return ['background-color:#f7df70;color:#202b41;font-weight:bold' for _ in col]

# リーグ構築
def build_leagues(my_club_name):
    return {
        'イングランド': {
            '1部': [my_club_name,"Midtown United","Eastport Rovers","Kingsbridge Athletic",
                    "Westhaven City","Southvale Town","Northgate FC","Oakwood Albion"],
            '2部': ["Lakemont FC","Greenfield United","Highview Rangers","Stonebridge Town",
                    "Redwood City","Bayview Athletic","Hillcrest FC","Harborport United"]
        },
        'スペイン': {
            '1部': ["Costa Mar FC","Solaria United","Nueva Vista Rovers","Valencia Hills",
                    "Sevilla Coast Athletic","Barcelona Verde","Madrid Oeste City","Catalonia Albion"],
            '2部': ["Andalusia Stars","Granada Echo FC","Cadiz Mariners","Ibiza Sun United",
                    "Mallorca Winds","Murcia Valley Athletic","Castilla Rovers","Toledo Town"]
        },
        'フランス': {
            '1部': ["Paris Saintoise","Lyonnais Athletic","Marseille Bleu","Monaco Royal",
                    "Lille Nord FC","Rennes Rouge","Nice Côte Town","Nantes Loire United"],
            '2部': ["Bordeaux Vine FC","Montpellier Horizon","Toulouse Aero Athletic","Reims Champagne",
                    "Strasbourg Forest","Brest Bretagne","Angers Loire","Metz Lorraine"]
        },
        'ドイツ': {
            '1部': ["Bavaria Deutschland","Borussia Rhein","Leipzig Redbulls","Leverkusen Chemie",
                    "Schalke Ruhr","Wolfsburg VW United","Eintracht Hessen","Freiburg Blackforest"],
            '2部': ["St Pauli Harbor","Hamburg Hanseatic","Karlsruhe Baden","Heidelberg Lions",
                    "Nuremberg Franconia","Darmstadt Lilies","Dusseldorf Fortuna","Stuttgart Swabia"]
        },
        'オランダ': {
            '1部': ["Amsterdam Canal FC","Rotterdam Harbor","Eindhoven Philips United","Utrecht Dom Rovers",
                    "Groningen North Sea","PSV Eindhoven","AZ Alkmaar","Feyenoord Rijnstad"],
            '2部': ["Sparta Rotterdam","NEC Nijmegen","Volendam Fishermen","Cambuur Leeeuw FC",
                    "Excelsior Maas United","Twente Tukkers","Willem II Tilburg","Roda Sunshine"]
        }
    }

# 名前プール（各国30×30）
NAME_POOLS = {
    'ENG': {'given': ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William","James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Ethan","Mason","Finley","Lucas","Samuel","Joseph","Dylan","Matthew","Daniel","Benjamin","Max"],
            'surname': ["Smith","Jones","Taylor","Brown","Wilson","Evans","Thomas","Roberts","Johnson","Lewis","Walker","White","Harris","Martin","Thompson","Robinson","Clark","Young","Allen","King","Wright","Scott","Adams","Baker","Hill","Green","Nelson","Mitchell","Perez","Campbell"]},
    'GER': {'given': ["Lukas","Maximilian","Finn","Leon","Felix","Elias","Paul","Jonas","Luis","Tim","Noah","Ben","Jan","Anton","Henry","David","Moritz","Nico","Samuel","Philipp","Emil","Jonathan","Mats","Lennard","Theo","Jannik","Fabian","Johannes","Lucas","Elias"],
            'surname': ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Bauer","Koch","Richter","Klein","Wolf","Neumann","Schwarz","Zimmermann","Schmitt","Krüger","Hofmann","Hartmann","Lange","Schmid","Werner","Schubert","Krause","Meier","Lehmann","Köhler","Frank","Mayer"]},
    'ITA': {'given': ["Lorenzo","Alessandro","Francesco","Mattia","Leonardo","Riccardo","Gabriele","Niccolò","Tommaso","Andrea","Marco","Matteo","Fabio","Emanuele","Valerio","Daniele","Federico","Simone","Alberto","Vincenzo","Stefano","Davide","Giovanni","Fabiano","Luca","Antonio","Paolo","Maurizio","Raffaele","Jonathan"],
            'surname': ["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Moretti","Barbieri","Fontana","Santoro","Mariani","Riva","Bianco","Ferrara","Bernardi","Caputo","Monti"]},
    'ESP': {'given': ["Hugo","Martín","Lucas","Mateo","Iker","Diego","Álvaro","Pablo","Adrián","Sergio","Joaquín","Ángel","David","Rubén","Martí","Óscar","Víctor","Miguel","Enzo","Álex","Bruno","Mario","Oliver","Juan","José","Raúl","Isco","Pedro","Nacho","Saúl"],
            'surname': ["García","Martínez","López","Sánchez","Pérez","González","Rodríguez","Fernández","Torres","Ramírez","Flores","Gómez","Ruiz","Hernández","Díaz","Morales","Muñoz","Alonso","Gutiérrez","Castro","Ortiz","Rubio","Marín","Serrano","Gil","Blanco","Molina","Romero","Navarro","Medina"]},
    'FRA': {'given': ["Lucas","Gabriel","Léo","Raphaël","Arthur","Louis","Hugo","Jules","Adam","Nathan","Ethan","Thomas","Clément","Théo","Mathis","Noah","Maxime","Paul","Alexis","Victor","Martin","Gabin","Quentin","Guillaume","Baptiste","Maxence","Romain","Antoine","Mathieu","Robin"],
            'surname': ["Martin","Bernard","Thomas","Petit","Robert","Richard","Durand","Dubois","Moreau","Laurent","Simon","Michel","Leroy","Rousseau","David","Bertrand","Morel","Girard","Bonnet","Dupont","Lambert","Fontaine","Roux","Vincent","Morin","Nicolas","Lefebvre","Mercier","Dupuis","Blanc"]},
    'BRA': {'given': ["Pedro","Lucas","Guilherme","Mateus","Gabriel","Rafael","Bruno","Thiago","Felipe","Diego","Vinícius","João","Carlos","Ricardo","Eduardo","Fernando","Rodrigo","Paulo","Leandro","André","Vitor","Marcelo","Roberto","Caio","Renato","Igor","Luan","Fábio","Jonas","Samuel"],
            'surname': ["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Alves","Pereira","Lima","Gomes","Martins","Araújo","Ribeiro","Cardoso","Rocha","Dias","Carvalho","Barbosa","Pinto","Fernandes","Costa","Moreira","Mendes","Camargo","Rezende","Moura","Medeiros","Freitas","Castro","Campos"]},
    'NED': {'given': ["Daan","Lars","Sem","Finn","Thijs","Mees","Senna","Luuk","Milan","Jens","Rick","Rens","Sven","Tijs","Joost","Noud","Stijn","Tygo","Mats","Niels","Jelle","Bram","Wout","Teun","Guus","Floris","Koen","Derk","Gerrit","Max"],
            'surname': ["de Jong","Janssen","de Vries","van Dijk","Bakker","Visser","Smit","Meijer","de Boer","Mulder","de Graaf","Brouwer","van der Meer","Kuiper","Bos","Vos","Peters","Hendriks","Jakobs","van Leeuwen","de Groot","van den Berg","Kramer","van Dam","Molenaar","Corsten","Bergman","Verhoeven","Dekker","Veldman"]}
}

# プレースタイル／成長タイプ
PLAY_STYLE_POOL = [
    "チャンスメーカー","シャドーストライカー","タックルマスター","インナーラップSB","スイーパーリーダー",
    "セカンドストライカー","ディストラクター","バランサー","トリックスター","クロスハンター",
    "カウンターランナー","クラッチプレイヤー","ジョーカー","フリーキックスペシャリスト","メンタルリーダー",
    "空中戦の鬼","起点型GK","配給型CB","王様タイプ","スペ体質","ムードメーカー","影の支配者",
    "勝負師","頭脳派","職人","チーム至上主義","師弟型","感情型","爆発型","メディア映え型","俊足ドリブラー"
]
GROWTH_TYPES_POOL = [
    "超早熟型","早熟型","標準型","晩成型","超晩成型","スペ体質","安定型","一発屋型","伸び悩み型","終盤爆発型"
]
NATION_STYLE_MAP = {
    'BRA': PLAY_STYLE_POOL[:7],
    'GER': PLAY_STYLE_POOL[7:13],
    'NED': PLAY_STYLE_POOL[13:19],
    'FRA': PLAY_STYLE_POOL[19:25],
    'ENG': PLAY_STYLE_POOL[25:31],
    'ESP': PLAY_STYLE_POOL[31:37],
    'OTHER': PLAY_STYLE_POOL
}
NATION_GROWTH_MAP = {
    'BRA': GROWTH_TYPES_POOL[:4],
    'GER': GROWTH_TYPES_POOL[4:8],
    'NED': GROWTH_TYPES_POOL[8:],
    'FRA': GROWTH_TYPES_POOL[:3],
    'ENG': GROWTH_TYPES_POOL[3:6],
    'ESP': GROWTH_TYPES_POOL[6:9],
    'OTHER': GROWTH_TYPES_POOL
}

# ---------------- ユーティリティ ----------------
def pick_from_weighted_pool(nat, pool_map, all_pool):
    base = pool_map.get(nat, pool_map['OTHER']).copy()
    if len(base) < len(all_pool):
        base += [x for x in all_pool if x not in base]
    random.shuffle(base)
    return base

def gen_unique_name(nat, used):
    while True:
        first = random.choice(NAME_POOLS[nat]['given'])
        last  = random.choice(NAME_POOLS[nat]['surname'])
        name  = f"{first} {last}"
        if name not in used:
            used.add(name)
            return name

def normalize_value(v:int)->int:
    if v >= 1000:
        return (v // 1000) * 1000
    else:
        return v - (v % 5)

def suggest_positions(df):
    need = []
    target = {'GK':2,'DF':8,'MF':8,'FW':4}
    cnt = df['Pos'].value_counts()
    for p, req in target.items():
        lack = req - cnt.get(p,0)
        if lack > 0:
            need.append(f"{p} x{lack}")
    return "・".join(need) if need else "十分揃っています"

def growth_delta(gtype, age, youth=False):
    base = 0
    if gtype in ["超早熟型","早熟型"]:
        base = 1.2 if youth else (0.5 if age<23 else -0.3)
    elif gtype in ["晩成型","超晩成型","終盤爆発型"]:
        base = (0.2 if age<23 else 1.0) if gtype!="終盤爆発型" else (0 if age<25 else 1.5)
    elif gtype in ["一発屋型"]:
        base = 2.0 if random.random()<0.08 else -0.5
    elif gtype in ["スペ体質"]:
        base = 0.8 if random.random()<0.3 else -0.4
    else:
        base = 0.3
    return base + random.uniform(-0.5,0.5)

def apply_growth(df, week):
    for idx, r in df.iterrows():
        delta = growth_delta(r['GrowthType'], r['Age'], youth=False)
        for k in ABILITY_KEYS:
            newv = int(max(30, min(99, r[k] + (1 if delta>0 and random.random()<0.6 else (-1 if random.random()<0.4 else 0)))))
            df.at[idx, k] = newv
        df.at[idx, 'OVR'] = int(np.mean([df.at[idx, k] for k in ABILITY_KEYS]))
    return df

def update_player_history(name, df_row, week):
    snap = {'week':week,'OVR':df_row['OVR']}
    for k in ABILITY_KEYS:
        snap[k] = int(df_row[k])
    st.session_state.player_history.setdefault(name, []).append(snap)

def gen_players(n, youth=False, club=None, used=None):
    if used is None:
        used = set()
    rows = []
    for _ in range(n):
        nat = random.choice(list(NAME_POOLS.keys()))
        name = gen_unique_name(nat, used)
        style_pool  = pick_from_weighted_pool(nat, NATION_STYLE_MAP, PLAY_STYLE_POOL)
        growth_pool = pick_from_weighted_pool(nat, NATION_GROWTH_MAP, GROWTH_TYPES_POOL)
        play_styles = random.sample(style_pool, 2)
        growth_type = random.choice(growth_pool)
        stats = {k: random.randint(50 if youth else 60, 80 if youth else 90) for k in ABILITY_KEYS}
        ovr = int(np.mean(list(stats.values())))
        age = random.randint(15,19) if youth else random.randint(18,34)
        pid = random.randint(10**7,10**8-1)
        rows.append({
            'PID': pid,
            'Name': name,
            'Nat': nat,
            'Pos': random.choice(['GK','DF','MF','FW']),
            **stats,
            'OVR': ovr,
            'PlayStyle': play_styles,
            'GrowthType': growth_type,
            'Age': age,
            'Club': club if club else "Free",
            'Matches': 0,
            'Goals': 0,
            'Assists': 0,
            'Shots': 0,
            'OnTarget': 0,
            'IntlApps': 0,
            'RentalFrom': None,
            'RentalUntil': None,
            'OptionFee': None,
            'Status': "通常",
            'Value': normalize_value(ovr*5000 + random.randint(-5000, 12000))
        })
    return pd.DataFrame(rows)

# ---------------- AIクラブ方針 ----------------
AI_POLICIES = ["seller","hold","young","star","balanced"]

def build_club_intents(leagues, my_club):
    intent = {}
    for reg in leagues:
        for div in leagues[reg]:
            for c in leagues[reg][div]:
                if c == my_club: 
                    continue
                intent[c] = {
                    'policy': random.choice(AI_POLICIES),
                    'budget': random.randint(2_000_000, 15_000_000),
                    'sell_core': random.random()<0.2,
                    'develop_youth': random.random()<0.5
                }
    return intent

def offer_result(row, wage, years, fee, my_budget, club_policy):
    want_wage = row['OVR']*120 + random.randint(-3000,3000)
    want_fee  = row['Value']
    coef = 0.8 if club_policy=='seller' else (1.2 if club_policy=='hold' else 1.0)
    wage_ok = wage >= want_wage
    fee_ok  = fee  >= want_fee*coef
    club_ok = random.random() < (0.7 if club_policy=='seller' else (0.4 if club_policy=='hold' else 0.55))
    money_ok= my_budget >= fee
    return (wage_ok and fee_ok and club_ok and money_ok), want_wage, int(want_fee*coef)

def rental_result(row, weeks, fee, my_budget, club_policy):
    demand = int(row['Value']*0.15 + weeks*800)
    ok_fee = fee >= demand
    ok_club= random.random() < (0.65 if club_policy!='hold' else 0.4)
    return (ok_fee and ok_club and my_budget>=fee), demand

# ---------------- スタンディング更新 ----------------
def apply_result(df, home, away, gh, ga):
    if gh>ga:
        df.loc[df.Club==home, ['W','Pts']] += [1,3]
        df.loc[df.Club==away, 'L'] += 1
    elif gh<ga:
        df.loc[df.Club==away, ['W','Pts']] += [1,3]
        df.loc[df.Club==home, 'L'] += 1
    else:
        df.loc[df.Club.isin([home,away]), 'D'] += 1
        df.loc[df.Club.isin([home,away]), 'Pts'] += 1
    df.loc[df.Club==home, ['GF','GA']] += [gh, ga]
    df.loc[df.Club==away, ['GF','GA']] += [ga, gh]
    return df

# ---------------- レンタル処理 ----------------
def tick_rentals(df, week, pending_list):
    for i, r in df.iterrows():
        if r['RentalUntil'] is not None and week > r['RentalUntil'] and r['Status'].startswith("レンタル中"):
            pending_list.append(r['PID'])
            df.at[i,'Status'] = "レンタル満了"
    return df, pending_list

# ---------------- 国際大会自動進行 ----------------
def auto_intl_round():
    if not st.session_state.intl_tournament:
        parts=[]
        for reg in st.session_state.leagues:
            if '1部' in st.session_state.standings[reg]:
                parts.extend(st.session_state.standings[reg]['1部'].nlargest(2,'Pts')['Club'].tolist())
        random.shuffle(parts)
        st.session_state.intl_tournament = {'clubs':parts,'results':[]}

    clubs = st.session_state.intl_tournament['clubs']
    if len(clubs) < 2:
        return

    winners=[]
    for i in range(0,len(clubs)-1,2):
        c1,c2 = clubs[i], clubs[i+1]
        g1,g2 = random.randint(0,4), random.randint(0,4)
        pk_txt=""
        if g1==g2:
            pk1,pk2 = random.randint(3,5), random.randint(3,5)
            while pk1==pk2:
                pk1,pk2 = random.randint(3,5), random.randint(3,5)
            pk_txt=f"PK {pk1}-{pk2}"
            w = c1 if pk1>pk2 else c2
        else:
            w = c1 if g1>g2 else c2
        st.session_state.intl_tournament['results'].append((c1,g1,c2,g2,pk_txt,w))
        st.session_state.sns_posts.append(f"[国際大会] {c1} {g1}-{g2} {c2} {pk_txt} → 勝者:{w}")
        st.session_state.sns_times.append(datetime.now())

        if c1==st.session_state.my_club or c2==st.session_state.my_club:
            starters_names = st.session_state.starters if st.session_state.starters else st.session_state.senior.nlargest(11,'OVR')['Name'].tolist()
            for nm in starters_names:
                for df in [st.session_state.senior, st.session_state.youth]:
                    idx = df.index[df['Name']==nm]
                    if len(idx)>0:
                        df.at[idx[0],'IntlApps'] = df.at[idx[0],'IntlApps'] + 1
        winners.append(w)

    if len(clubs)%2==1:
        winners.append(clubs[-1])
    st.session_state.intl_tournament['clubs'] = winners

# ---------------- セッション初期化 ----------------
ses = st.session_state

if 'my_club' not in ses:
    ses.my_club = MY_CLUB_DEFAULT
if 'leagues' not in ses:
    ses.leagues = build_leagues(ses.my_club)
if 'week' not in ses:
    ses.week = 1
if 'budget' not in ses:
    ses.budget = 5_000_000
if 'used_names' not in ses:
    ses.used_names = set()

# 自クラブ
if 'senior' not in ses:
    ses.senior = gen_players(30, youth=False, club=ses.my_club, used=ses.used_names)
if 'youth' not in ses:
    ses.youth  = gen_players(20, youth=True , club=ses.my_club, used=ses.used_names)

# 他クラブ全体プール
if 'all_players_pool' not in ses:
    pool = []
    for reg in ses.leagues:
        for div in ses.leagues[reg]:
            for c in ses.leagues[reg][div]:
                if c == ses.my_club: 
                    continue
                pool.append(gen_players(random.randint(18,26), youth=False, club=c, used=ses.used_names))
    ses.all_players_pool = pd.concat(pool, ignore_index=True)

# スタンディング
if 'standings' not in ses:
    ses.standings = {
        r:{ d:pd.DataFrame({'Club':ses.leagues[r][d],
                            'W':0,'D':0,'L':0,'GF':0,'GA':0,'Pts':0})
            for d in ses.leagues[r]}
        for r in ses.leagues
    }

# AIクラブ方針
if 'club_intent' not in ses:
    ses.club_intent = build_club_intents(ses.leagues, ses.my_club)

# 各種ログ類
defaults = {
    'player_history':{},
    'match_log':[],
    'sns_posts':[],
    'sns_times':[],
    'finance_log':[],
    'season_summary':[],
    'injury_info':{},
    'suspension_info':{},
    'intl_tournament':{},
    'scout_list':pd.DataFrame(),
    'rental_pending':[],
    'starters':[]
}
for k,v in defaults.items():
    if k not in ses: ses[k]=v

# レンタル満了チェック
ses.senior, ses.rental_pending = tick_rentals(ses.senior, ses.week, ses.rental_pending)
ses.youth , ses.rental_pending = tick_rentals(ses.youth , ses.week, ses.rental_pending)

# ---------------- レンタル満了処理UI ----------------
def handle_rental_expirations():
    if not ses.rental_pending:
        return
    st.markdown("### レンタル満了選手の処理")
    df_all = pd.concat([ses.senior, ses.youth], ignore_index=True)
    for pid in ses.rental_pending[:]:
        row = df_all[df_all['PID']==pid]
        if row.empty:
            ses.rental_pending.remove(pid)
            continue
        r = row.iloc[0]
        st.write(f"**{r['Name']}** | Pos:{r['Pos']} | OVR:{r['OVR']} | 元:{r['RentalFrom']} | 買取OP:{r['OptionFee']}€")
        c1,c2 = st.columns(2)
        with c1:
            if st.button(f"買取する（{r['OptionFee']}€）", key=f"buy_{pid}"):
                if ses.budget >= r['OptionFee']:
                    ses.budget -= r['OptionFee']
                    for df in [ses.senior, ses.youth]:
                        idx = df.index[df['PID']==pid]
                        if len(idx)>0:
                            df.at[idx[0],'Club'] = ses.my_club
                            df.at[idx[0],'RentalFrom'] = None
                            df.at[idx[0],'RentalUntil']= None
                            df.at[idx[0],'OptionFee']  = None
                            df.at[idx[0],'Status']     = "通常"
                            break
                    st.success("買取成立！")
                    ses.rental_pending.remove(pid)
                else:
                    st.error("予算不足です。")
        with c2:
            if st.button("返却する", key=f"return_{pid}"):
                origin = r['RentalFrom']
                removed=False
                for df in [ses.senior, ses.youth]:
                    idx = df.index[df['PID']==pid]
                    if len(idx)>0:
                        row_back = df.loc[idx[0]].copy()
                        df.drop(idx, inplace=True)
                        removed=True
                        break
                if removed:
                    row_back['Club']=origin
                    row_back['RentalFrom']=None
                    row_back['RentalUntil']=None
                    row_back['OptionFee']=None
                    row_back['Status']="通常"
                    ses.all_players_pool = pd.concat([ses.all_players_pool, pd.DataFrame([row_back])], ignore_index=True)
                st.info("返却完了")
                ses.rental_pending.remove(pid)

# ---------------- スカウト候補生成 ----------------
def gen_scout_candidates(pool_df, myclub, n=6, youth=False):
    free_cnt = max(1, n//2)
    free_df  = gen_players(free_cnt, youth=youth, club="Free", used=ses.used_names)
    others = pool_df[(pool_df['Club']!="Free") & (pool_df['Club']!=myclub)]
    take = n - free_cnt
    pick_df = others.sample(min(take, len(others))) if len(others)>0 else pd.DataFrame()
    cands = pd.concat([free_df, pick_df], ignore_index=True)
    cands['PlayStyle'] = cands['PlayStyle'].apply(lambda x: " / ".join(x))
    return cands.sample(frac=1).reset_index(drop=True)

def get_rental_candidates(pool_df, myclub):
    return pool_df[(pool_df['Club']!=myclub) & (pool_df['RentalFrom'].isna()) & (pool_df['RentalUntil'].isna())]

# ---------------- タブ定義 ----------------
tabs = st.tabs([
    'シニア','ユース','選手詳細','試合','順位表',
    'スカウト/移籍','レンタル管理','SNS','財務レポート',
    '年間表彰','リーダーボード','国際大会ログ','クラブ設定','クラブ方針'
])

# ========= 0) シニア =========
with tabs[0]:
    st.markdown('<div style="color:#fff;font-size:20px;">シニア選手一覧</div>', unsafe_allow_html=True)
    handle_rental_expirations()
    order_mode = st.radio("並び順", ["GK→FW","FW→GK"], horizontal=True, key="o_senior")
    reverse_flag = (order_mode=="FW→GK")
    df0 = ses.senior[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Club','Status']]
    df0['PlayStyle'] = df0['PlayStyle'].apply(lambda x:" / ".join(x))
    df0 = sort_by_pos(df0, reverse=reverse_flag)
    st.dataframe(
        df0.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                 .apply(style_playstyle, subset=['PlayStyle'])
                 .set_properties(**{"background-color":"rgba(20,30,50,0.7)","color":"white"}),
        use_container_width=True
    )

# ========= 1) ユース =========
with tabs[1]:
    st.markdown('<div style="color:#fff;font-size:20px;">ユース選手一覧</div>', unsafe_allow_html=True)
    order_mode_y = st.radio("並び順", ["GK→FW","FW→GK"], horizontal=True, key="o_youth")
    reverse_flag_y = (order_mode_y=="FW→GK")
    df1 = ses.youth[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Club','Status']]
    df1['PlayStyle'] = df1['PlayStyle'].apply(lambda x:" / ".join(x))
    df1 = sort_by_pos(df1, reverse=reverse_flag_y)
    st.dataframe(
        df1.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                 .apply(style_playstyle, subset=['PlayStyle'])
                 .set_properties(**{"background-color":"rgba(20,30,50,0.7)","color":"white"}),
        use_container_width=True
    )

# ========= 2) 選手詳細 =========
with tabs[2]:
    pool_detail = pd.concat([ses.senior, ses.youth], ignore_index=True)
    sel_name = st.selectbox('選手選択', pool_detail['Name'].tolist())
    prow = pool_detail[pool_detail['Name']==sel_name].iloc[0]
    base_ovr = prow['OVR']
    hist = pd.DataFrame(ses.player_history.get(sel_name, [{'week':0,'OVR':base_ovr}]))
    if len(hist) > 1:
        fig, ax = plt.subplots()
        for k in ABILITY_KEYS:
            if k in hist.columns:
                ax.plot(hist['week'], hist[k], marker='o', label=k)
        ax.set_xlabel('節'); ax.set_ylabel('能力'); ax.legend(bbox_to_anchor=(1,1))
        st.pyplot(fig)
        fig2, ax2 = plt.subplots()
        ax2.plot(hist['week'], hist['OVR'], marker='o')
        ax2.set_xlabel('節'); ax2.set_ylabel('総合値')
        st.pyplot(fig2)
    else:
        st.info("成長データはありません。")
    st.write(f"ポジション: {prow['Pos']} / OVR:{prow['OVR']} / 年齢:{prow['Age']}")
    st.write(f"国籍: {prow['Nat']} / 国際大会出場: {prow['IntlApps']}回")
    st.write(f"プレースタイル: {', '.join(prow['PlayStyle'])}")
    st.write(f"所属: {prow['Club']} / 状態: {prow['Status']}")

# ========= 3) 試合 =========
with tabs[3]:
    st.markdown(f"<div style='color:#fff;font-size:20px;'>第{ses.week}節 試合シミュレーション</div>", unsafe_allow_html=True)
    formation = st.selectbox("フォーメーション", ["4-4-2","4-3-3","3-5-2"])
    if st.button("オート先発選考"):
        req = {
            "4-4-2":("FW",2,"MF",4,"DF",4,"GK",1),
            "4-3-3":("FW",3,"MF",3,"DF",4,"GK",1),
            "3-5-2":("FW",2,"MF",5,"DF",3,"GK",1)
        }[formation]
        starters=[]
        for i in range(0,len(req),2):
            pos,cnt=req[i],req[i+1]
            starters += ses.senior[ses.senior['Pos']==pos].nlargest(cnt,'OVR')['Name'].tolist()
        ses.starters = starters

    if ses.starters:
        st.markdown('<span style="color:white;font-weight:bold;">【先発メンバー】</span>', unsafe_allow_html=True)
        s_df = ses.senior[ses.senior['Name'].isin(ses.starters)][['Name','Pos','OVR','PlayStyle','Club']]
        s_df['PlayStyle']=s_df['PlayStyle'].apply(lambda x:" / ".join(x))
        s_df = sort_by_pos(s_df)
        st.dataframe(
            s_df.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                      .apply(style_playstyle, subset=['PlayStyle'])
                      .set_properties(**{"background-color":"rgba(20,30,50,0.7)","color":"white"}),
            use_container_width=True
        )

    # 相手クラブ（自リーグ1部）
    first_reg = list(ses.leagues.keys())[0]
    first_div = list(ses.leagues[first_reg].keys())[0]
    opp = random.choice([c for c in ses.leagues[first_reg][first_div] if c != ses.my_club])

    if ses.week <= SEASON_WEEKS and st.button("キックオフ"):
        atk = ses.senior[ses.senior['Name'].isin(ses.starters)]['OVR'].mean() if ses.starters else 70
        oppatk = random.uniform(60,90)
        gh = max(0,int(np.random.normal((atk-60)/8,1)))
        ga = max(0,int(np.random.normal((oppatk-60)/8,1)))
        shots = random.randint(5,15); on_t = random.randint(0,shots)

        scorers=[]
        if gh>0 and ses.starters:
            for _ in range(gh):
                nm = random.choice(ses.starters)
                scorers.append(nm)
                ses.senior.loc[ses.senior['Name']==nm,'Goals'] += 1

        ses.match_log.append({'week':ses.week,'opp':opp,'gf':gh,'ga':ga})
        ses.sns_posts.append(f"{ses.my_club} {gh}-{ga} {opp}")
        ses.sns_times.append(datetime.now())

        ses.finance_log.append({
            'week': ses.week,
            'revenue_ticket': gh*15000 + random.randint(5000,10000),
            'revenue_goods' : ga*8000  + random.randint(1000,5000),
            'expense_salary': int(ses.senior['OVR'].mean()*1000)
        })

        ses.standings[first_reg][first_div] = apply_result(ses.standings[first_reg][first_div], ses.my_club, opp, gh, ga)

        # 他試合
        for reg in ses.leagues:
            for div in ses.leagues[reg]:
                clubs = ses.leagues[reg][div]
                for i in range(0,len(clubs),2):
                    if i+1>=len(clubs): break
                    h,a = clubs[i], clubs[i+1]
                    if {h,a}=={ses.my_club,opp}:
                        continue
                    g1,g2 = random.randint(0,3), random.randint(0,3)
                    ses.standings[reg][div] = apply_result(ses.standings[reg][div], h,a,g1,g2)

        ses.senior = apply_growth(ses.senior, ses.week)
        for _,rw in ses.senior.iterrows():
            update_player_history(rw['Name'], rw, ses.week)

        st.success(f"結果 {gh}-{ga}")
        if scorers:
            st.write("得点者: " + " / ".join(scorers))
        st.write(f"シュート:{shots} 枠内:{on_t} ポゼッション:{random.randint(40,60)}%")

        ses.week += 1
        auto_intl_round()  # 国際大会自動進行

        if ses.week > SEASON_WEEKS:
            champ = ses.standings[first_reg][first_div].nlargest(1,'Pts')['Club'].iloc[0]
            top_scorer = ses.senior.nlargest(1,'Goals')['Name'].iloc[0] if 'Goals' in ses.senior else ''
            ses.season_summary.append({'Champion':champ,'TopScorer':top_scorer})
            st.success("シーズン終了！")

    elif ses.week > SEASON_WEEKS:
        st.info("シーズン終了済。次シーズン開始してください。")
        if st.button("次シーズン開始"):
            ses.week = 1
            ses.senior = gen_players(30, youth=False, club=ses.my_club, used=ses.used_names)
            ses.youth  = gen_players(20, youth=True , club=ses.my_club, used=ses.used_names)
            ses.standings = {
                r:{d:pd.DataFrame({'Club':ses.leagues[r][d],'W':0,'D':0,'L':0,'GF':0,'GA':0,'Pts':0})
                   for d in ses.leagues[r]} for r in ses.leagues
            }
            ses.sns_posts.clear(); ses.sns_times.clear()
            ses.finance_log.clear(); ses.intl_tournament.clear()
            ses.match_log.clear(); ses.player_history.clear()
            st.success("新シーズン開始！")

# ========= 4) 順位表 =========
with tabs[4]:
    region = st.selectbox('地域', list(ses.leagues.keys()))
    division = st.selectbox('部', list(ses.leagues[region].keys()))
    df_st = ses.standings[region][division]
    st.dataframe(
        df_st.style.apply(make_highlighter('Club', ses.my_club), axis=1)
            .set_properties(**{"background-color":"rgba(20,30,50,0.7)","color":"white"}),
        use_container_width=True
    )

# ========= 5) スカウト/移籍 =========
with tabs[5]:
    st.markdown("<div style='color:#fff;font-size:20px;'>スカウト / 移籍 / 引き抜き / レンタル</div>", unsafe_allow_html=True)

    cat = st.radio("対象カテゴリー", ["シニア候補","ユース候補"], horizontal=True)
    youth_flag = (cat=="ユース候補")

    need_txt = suggest_positions(ses.senior if not youth_flag else ses.youth)
    st.markdown(f"**補強推奨ポジション:** {need_txt}")

    c1,c2 = st.columns(2)
    with c1:
        if st.button("候補リスト更新"):
            pool_all = pd.concat([ses.all_players_pool, ses.senior, ses.youth], ignore_index=True)
            ses.scout_list = gen_scout_candidates(pool_all, ses.my_club, n=6, youth=youth_flag)
    with c2:
        st.write(f"予算: {ses.budget:,} €")

    if ses.scout_list is None or len(ses.scout_list)==0:
        st.info("候補がいません。『候補リスト更新』を押してください。")
    else:
        for i,row in ses.scout_list.iterrows():
            st.markdown("""
            <div style="background:rgba(255,255,255,0.08);padding:10px 14px;margin:12px 0;border-radius:10px;">
            """, unsafe_allow_html=True)

            st.markdown(
                f"**{row['Name']}**  | {row['Nat']} | {row['Age']}歳 | {row['Pos']} | OVR:{row['OVR']}<br>"
                f"PlayStyle: {row['PlayStyle']}<br>"
                f"所属:{row['Club']}  /  価値:{row['Value']:,}€",
                unsafe_allow_html=True
            )

            if row['Club']=="Free":
                if st.button("契約", key=f"sign_free_{i}"):
                    if youth_flag:
                        ses.youth  = pd.concat([ses.youth , pd.DataFrame([row])], ignore_index=True)
                    else:
                        ses.senior = pd.concat([ses.senior, pd.DataFrame([row])], ignore_index=True)
                    ses.scout_list = ses.scout_list.drop(i).reset_index(drop=True)
                    st.success("獲得しました！")
            else:
                mode = st.selectbox(f"オファー種別（{row['Name']}）", ["完全移籍","レンタル(買取OP付)"], key=f"mode_{i}")
                policy = ses.club_intent.get(row['Club'],{}).get('policy','balanced')
                with st.form(f"offer_{i}"):
                    if mode=="完全移籍":
                        wage = st.number_input("提示年俸(€)", min_value=0, value=row['OVR']*150)
                        years= st.slider("契約年数",1,5,3)
                        fee  = st.number_input("移籍金(€)", min_value=0, value=int(row['Value']))
                        sub  = st.form_submit_button("送信")
                        if sub:
                            ok, want_wage, want_fee = offer_result(row, wage, years, fee, ses.budget, policy)
                            if ok:
                                ses.budget -= fee
                                row2 = row.copy()
                                row2['Club']=ses.my_club
                                if youth_flag:
                                    ses.youth  = pd.concat([ses.youth , pd.DataFrame([row2])], ignore_index=True)
                                else:
                                    ses.senior = pd.concat([ses.senior, pd.DataFrame([row2])], ignore_index=True)
                                ses.scout_list = ses.scout_list.drop(i).reset_index(drop=True)
                                st.success("移籍成立！")
                            else:
                                st.error(f"拒否【要求目安:年俸{want_wage}€, 移籍金{want_fee}€】")
                    else:
                        weeks = st.slider("レンタル期間（節）",1,8,4)
                        fee_r = st.number_input("レンタル料(€)", min_value=0, value=int(row['Value']*0.15))
                        opt   = st.number_input("買取オプション額(€)", min_value=0, value=int(row['Value']*1.2))
                        subr  = st.form_submit_button("送信")
                        if subr:
                            ok, demand = rental_result(row,weeks,fee_r,ses.budget,policy)
                            if ok:
                                ses.budget -= fee_r
                                row2 = row.copy()
                                row2['Club'] = ses.my_club
                                row2['RentalFrom'] = row['Club']
                                row2['RentalUntil']= ses.week + weeks
                                row2['OptionFee']  = opt
                                row2['Status']     = f"レンタル中({weeks}節)"
                                if youth_flag:
                                    ses.youth  = pd.concat([ses.youth , pd.DataFrame([row2])], ignore_index=True)
                                else:
                                    ses.senior = pd.concat([ses.senior, pd.DataFrame([row2])], ignore_index=True)
                                ses.all_players_pool = ses.all_players_pool[ses.all_players_pool['PID']!=row['PID']]
                                ses.scout_list = ses.scout_list.drop(i).reset_index(drop=True)
                                st.success("レンタル成立！")
                            else:
                                st.error(f"拒否【要求額目安:{demand}€】")
            st.markdown("</div>", unsafe_allow_html=True)

# ========= 6) レンタル管理 =========
with tabs[6]:
    st.markdown("<div style='color:#fff;font-size:20px;'>レンタル管理</div>", unsafe_allow_html=True)
    handle_rental_expirations()
    df_r = pd.concat([ses.senior, ses.youth], ignore_index=True)
    df_r = df_r[df_r['Status'].str.startswith("レンタル中", na=False)][['Name','Pos','OVR','RentalFrom','RentalUntil','OptionFee','Status']]
    if df_r.empty:
        st.info("レンタル中の選手はいません。")
    else:
        st.dataframe(df_r, use_container_width=True)

# ========= 7) SNS =========
with tabs[7]:
    if ses.sns_posts:
        for t,p in zip(reversed(ses.sns_times), reversed(ses.sns_posts)):
            st.write(f"{t.strftime('%m/%d %H:%M')} - {p}")
    else:
        st.info("投稿なし")

# ========= 8) 財務レポート =========
with tabs[8]:
    df_fin = pd.DataFrame(ses.finance_log)
    if df_fin.empty:
        st.info("財務データなし")
    else:
        fig, ax = plt.subplots()
        ax.plot(df_fin['week'], df_fin['revenue_ticket']+df_fin['revenue_goods'], label='収入')
        ax.plot(df_fin['week'], df_fin['expense_salary'], label='支出')
        ax.set_xlabel("節"); ax.set_ylabel("金額(€)"); ax.set_title("収支推移")
        ax.legend()
        st.pyplot(fig)
        st.dataframe(df_fin.rename(columns={
            'week':'節','revenue_ticket':'チケット収入','revenue_goods':'グッズ収入','expense_salary':'人件費'
        }), use_container_width=True)

# ========= 9) 年間表彰 =========
with tabs[9]:
    st.markdown('<div style="color:white;font-size:20px;">年間表彰</div>', unsafe_allow_html=True)
    df_all = pd.concat([ses.senior, ses.youth], ignore_index=True)
    if 'Goals' not in df_all: df_all['Goals']=0
    top5 = df_all.nlargest(5,'Goals')[['Name','Goals','Club']]
    st.markdown('<span style="color:white;font-weight:bold;">🏅 得点王 TOP5</span>', unsafe_allow_html=True)
    st.dataframe(top5.style.apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)

    best11 = df_all.nlargest(11,'OVR')[['Name','OVR','Club']]
    st.markdown('<span style="color:white;font-weight:bold;">⚽️ ベストイレブン</span>', unsafe_allow_html=True)
    st.dataframe(best11.style.apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)

# ========= 10) リーダーボード =========
with tabs[10]:
    st.markdown('<div style="color:white;font-size:20px;">リーダーボード</div>', unsafe_allow_html=True)
    df_all = pd.concat([ses.senior, ses.youth], ignore_index=True)
    if 'Age' in df_all:
        df_all['AgeGroup'] = pd.cut(df_all['Age'], bins=[0,21,23,100], labels=['U21','U23','25+'])
    typ = st.selectbox('表示タイプ',['国籍別得点','国籍別平均OVR','世代別ゴール'])
    if 'Goals' not in df_all: df_all['Goals']=0
    if typ=='国籍別得点':
        df_nat = df_all.groupby('Nat')['Goals'].sum().reset_index().sort_values('Goals',ascending=False)
        st.dataframe(df_nat, use_container_width=True)
    elif typ=='国籍別平均OVR':
        df_nat = df_all.groupby('Nat')['OVR'].mean().reset_index().sort_values('OVR',ascending=False)
        fig, ax = plt.subplots(); ax.bar(df_nat['Nat'], df_nat['OVR'])
        ax.set_xlabel("国籍"); ax.set_ylabel("平均OVR")
        st.pyplot(fig)
    else:
        df_age = df_all.groupby('AgeGroup')['Goals'].sum().reset_index()
        fig, ax = plt.subplots(); ax.bar(df_age['AgeGroup'], df_age['Goals'])
        ax.set_xlabel("世代"); ax.set_ylabel("総得点")
        st.pyplot(fig)

# ========= 11) 国際大会ログ（閲覧用） =========
with tabs[11]:
    st.markdown('<div style="color:white;font-size:20px;">国際大会ログ</div>', unsafe_allow_html=True)
    if not ses.intl_tournament:
        st.info("まだ大会が開始されていません。（試合を進めると自動で開始）")
    else:
        for idx,m in enumerate(ses.intl_tournament['results']):
            line = f"【R{idx+1}】 {m[0]} {m[1]}-{m[3]} {m[2]} {m[4]} → 勝者:{m[5]}"
            if ses.my_club in line:
                st.markdown(f"<span style='background:#f7df70;color:#202b41;font-weight:bold'>{line}</span>", unsafe_allow_html=True)
            else:
                st.write(line)
        if len(ses.intl_tournament['clubs'])==1:
            champ = ses.intl_tournament['clubs'][0]
            msg = f"優勝: {champ}"
            if champ==ses.my_club:
                st.markdown(f"<span style='background:#f7df70;color:#202b41;font-weight:bold'>{msg}</span>", unsafe_allow_html=True)
            else:
                st.success(msg)

# ========= 12) クラブ設定 =========
with tabs[12]:
    st.markdown('<div style="color:white;font-size:20px;">クラブ設定</div>', unsafe_allow_html=True)
    new_name = st.text_input("自クラブ名", value=ses.my_club, max_chars=30)
    if st.button("クラブ名変更"):
        if new_name and new_name != ses.my_club:
            old = ses.my_club
            ses.my_club = new_name
            ses.leagues = build_leagues(ses.my_club)
            for df in [ses.senior, ses.youth]:
                df.loc[df['Club']==old, 'Club'] = ses.my_club
            st.success("クラブ名を変更しました。再実行してください。")

# ========= 13) クラブ方針（AI） =========
with tabs[13]:
    st.markdown('<div style="color:white;font-size:20px;">クラブ方針（AIクラブの意思）</div>', unsafe_allow_html=True)
    df_int = pd.DataFrame([{'Club':k, **v} for k,v in ses.club_intent.items()])
    st.dataframe(df_int, use_container_width=True)
