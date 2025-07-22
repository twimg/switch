# =========================
# Part 1 / 12  --- Imports / Page Config / CSS / Constants
# =========================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

st.set_page_config(page_title="Club Strive", layout="wide")
random.seed(42)
np.random.seed(42)

# ----- 強制白文字＆背景調整（DataFrame含む） -----
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }
h1,h2,h3,h4,h5,h6 { color:#fff!important; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }
.stButton>button { background:#27e3b9!important; color:#202b41!important; font-weight:bold; border-radius:10px; margin:6px 0; }
.stButton>button:active { background:#ffee99!important; }
[data-testid="stDataFrame"] td, 
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] span,
[data-testid="stDataFrame"] div { color:#fff !important; }
[data-testid="stDataFrame"] table { background-color:rgba(32,44,70,0.85) !important; }
.scout-card { background:rgba(32,44,70,0.85); color:#fff; padding:10px 12px; margin:8px 0; border-radius:10px; box-shadow:0 0 8px #0005; }
.tab-info { color:#eaf6ff88; padding:6px 0; }
</style>
""", unsafe_allow_html=True)

st.title("Club Strive")

# ----- 共通定数 -----
SEASON_WEEKS = 14
ABILITY_KEYS = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
POS_ORDER = {'GK':0,'DF':1,'MF':2,'FW':3}

# =========================
# Part 2 / 12  --- Utility / Name Pools / Growth & Style / Charts
# =========================

# ---------- 表示系ユーティリティ ----------
def fmt_money(v:int)->str:
    if v >= 1_000_000:
        return f"{v//1_000_000}m€"
    if v >= 1_000:
        return f"{v//1_000}k€"
    return f"{v}€"

def normalize_value(v:int)->int:
    if v >= 1000:
        return (v // 1000) * 1000
    else:
        return max(5, (v // 5) * 5)

def sort_by_pos(df:pd.DataFrame, reverse:bool=False)->pd.DataFrame:
    order = (-1 if reverse else 1)
    return df.assign(_ord=df['Pos'].map(POS_ORDER)).sort_values(['_ord','OVR'], ascending=[order>0, False]).drop(columns=['_ord'])

def make_highlighter(col:str, target):
    def _hl(row):
        return ['background-color:#27e3b933' if row[col]==target else '' for _ in row]
    return _hl

def make_transparent(ax):
    ax.set_facecolor("none")
    if ax.figure:
        ax.figure.patch.set_alpha(0)
    for spine in ax.spines.values():
        spine.set_color("#fff3")
    ax.tick_params(colors="#fff8")
    ax.title.set_color("#fff")

def radar_chart(values, labels):
    vals = values + values[:1]
    ang  = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    ang += ang[:1]
    fig, ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(3,3))
    ax.plot(ang, vals, linewidth=2)
    ax.fill(ang, vals, alpha=0.25)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(labels, color="#fff")
    ax.set_yticklabels([])
    make_transparent(ax)
    return fig

def update_player_history(name:str, row:pd.Series, week:int):
    ses = st.session_state
    rec = {'week':week, 'OVR':row['OVR'], **{k:row[k] for k in ABILITY_KEYS}}
    ses.player_history.setdefault(name, []).append(rec)

def suggest_positions(df:pd.DataFrame)->list:
    need=[]
    for p, min_cnt in [('GK',2),('DF',8),('MF',8),('FW',6)]:
        have = (df['Pos']==p).sum()
        if have < min_cnt:
            need.append(f"{p}({min_cnt-have})")
    return need if need else ["バランスOK"]

# ---------- 成長タイプ / プレースタイル ----------
GROWTH_TYPES = {
    "ENG":["通常","晩成","持続","波あり"],
    "GER":["通常","晩成","持続"],
    "FRA":["通常","波あり","瞬間伸び"],
    "ESP":["通常","技巧型","瞬間伸び"],
    "ITA":["通常","守備伸び","晩成"],
    "NED":["通常","攻撃伸び","持続"],
    "BRA":["通常","爆発型","技巧型"],
    "POR":["通常","爆発型","波あり"],
    "BEL":["通常","守備伸び","持続"],
    "TUR":["通常","波あり","晩成"],
    "ARG":["通常","爆発型","技巧型"],
    "URU":["通常","守備伸び","晩成"],
    "COL":["通常","波あり","攻撃伸び"],
    "USA":["通常","持続","波あり"],
    "MEX":["通常","爆発型","波あり"],
    "SAU":["通常","持続","晩成"],
    "NGA":["通常","爆発型","身体伸び"],
    "MAR":["通常","守備伸び","波あり"],
    "KOR":["通常","持続","晩成"],
    "AUS":["通常","波あり","持続"]
}

PLAYSTYLE_POOL = {
    "default": ["チーム至上主義","ムードメーカー","司令塔","インサイドハーフ","クロスハンター","タックルマスター",
                "影の支配者","チャンスメーカ―","爆発型CB","起点型GK","スイーパーリーダー","師弟型","感情型",
                "セカンドストライカー","ジョーカー","空中戦の覇者","フリーキック職人","ロングスロー使い"],
    "BRA": ["ドリブラー","ファンタジスタ","リベルタドーレスの闘士"],
    "ARG": ["シャドーストライカー","パンパスの狩人"],
    "ENG": ["ゴールハンター","ロングシュート職人"],
    "GER": ["メンタルリーダー","鉄壁ディフェンダー"],
    "ITA": ["カテナチオスペシャリスト","レジスタ"],
    "ESP": ["ティキタカ使い","ポゼッションマスター"],
    "FRA": ["アーティスト","ボックストゥボックス"],
    "NED": ["トータルフットボール信奉者"],
    "POR": ["インナーフォワード"],
    "BEL": ["万能型ミッドフィールダー"],
    "TUR": ["激情型ファイター"],
    "URU": ["ガリンチャ魂","闘犬"],
    "COL": ["テクニカルウィング"],
    "USA": ["ハードワーカー"],
    "MEX": ["蛇の牙ストライカー"],
    "SAU": ["砂漠のスプリンター"],
    "NGA": ["爆速ランナー"],
    "MAR": ["砂漠のレジスタ"],
    "KOR": ["勤勉ボランチ"],
    "AUS": ["タフガイ"]
}

def pick_style_pool(nat):
    pool = PLAYSTYLE_POOL["default"] + PLAYSTYLE_POOL.get(nat,[])
    return pool

def pick_growth_pool(nat):
    return GROWTH_TYPES.get(nat, ["通常"])

def apply_growth(df:pd.DataFrame, week:int)->pd.DataFrame:
    df = df.copy()
    for i,r in df.iterrows():
        g = r.get('GrowthType','通常')
        delta = 0
        if g=="爆発型" and random.random()<0.3: delta = random.randint(2,4)
        elif g=="瞬間伸び" and random.random()<0.15: delta = random.randint(3,5)
        elif g=="晩成" and week>SEASON_WEEKS//2 and random.random()<0.2: delta = random.randint(2,3)
        elif g=="持続": delta = random.choice([0,1])
        elif g=="波あり": delta = random.choice([-1,0,1,2])
        elif g=="身体伸び": delta = random.choice([0,1]);  # small
        elif g=="守備伸び" and r['Pos'] in ['DF','GK'] and random.random()<0.25: delta = random.randint(1,2)
        elif g=="攻撃伸び" and r['Pos'] in ['FW','MF'] and random.random()<0.25: delta = random.randint(1,2)
        else:
            delta = random.choice([0,0,1])

        if delta!=0:
            for k in ABILITY_KEYS:
                df.at[i,k] = min(99, df.at[i,k] + delta//2)
            df.at[i,'OVR'] = min(99, df.at[i,'OVR'] + delta)
    return df

# ---------- 名前プール ----------
# 各国 first/last 30件 + 共通30件
NAME_POOL = {
    "COMMON": {
        "first": ["Alex","Chris","Jordan","Taylor","Sam","Jamie","Ryan","Casey","Robin","Morgan",
                  "Cameron","Drew","Jesse","Reese","Riley","Avery","Parker","Quinn","Emerson","Hayden",
                  "Rowan","Skyler","Sawyer","Logan","Blake","Corey","Elliot","Finley","Shawn","Kelly"],
        "last" : ["Smith","Johnson","Brown","Taylor","Anderson","Thomas","Jackson","White","Harris","Martin",
                  "Thompson","Garcia","Martinez","Robinson","Clark","Rodriguez","Lewis","Lee","Walker","Hall",
                  "Allen","Young","King","Wright","Scott","Green","Baker","Adams","Nelson","Carter"]
    },
    "ENG": {
        "first": ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
                  "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin",
                  "Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"],
        "last": ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
                 "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris",
                 "Baker","Moore","Wright","Hill","Cooper","Edwards","Ward","King","Parker","Campbell"]
    },
    "GER": {
        "first":["Lukas","Felix","Jonas","Finn","Leon","Paul","Maximilian","Noah","Elias","Moritz",
                 "Niklas","Tim","Lennard","Daniel","David","Jan","Florian","Fabian","Philipp","Timo",
                 "Sebastian","Simon","Julius","Tobias","Eric","Benjamin","Rafael","Oliver","Kilian","Emil"],
        "last":["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Hoffmann","Schäfer",
                "Koch","Bauer","Richter","Klein","Wolf","Schröder","Neumann","Schwarz","Zimmermann","Braun",
                "Krüger","Hofmann","Hartmann","Lange","Schmitt","Werner","Schmitz","Krause","Meier","Lehmann"]
    },
    "FRA": {
        "first":["Louis","Gabriel","Arthur","Jules","Raphaël","Hugo","Léo","Lucas","Adam","Nathan",
                 "Ethan","Paul","Mathis","Noah","Théo","Tom","Enzo","Sacha","Maxime","Yanis",
                 "Baptiste","Antoine","Clément","Valentin","Alexandre","Romain","Nicolas","Simon","Benoît","Quentin"],
        "last":["Martin","Bernard","Thomas","Petit","Robert","Richard","Durand","Dubois","Moreau","Laurent",
                "Simon","Michel","Lefebvre","Leroy","Roux","David","Bertrand","Morel","Fournier","Girard",
                "Bonnet","Dupont","Lambert","Fontaine","Rousseau","Vincent","Muller","Lefevre","Faure","Andre"]
    },
    "ESP": {
        "first":["Hugo","Martin","Lucas","Mateo","Leo","Daniel","Alejandro","Pablo","Álvaro","Adrián",
                 "Mario","Diego","Javier","Enzo","Marcos","Marco","David","Izan","Álex","Bruno",
                 "Thiago","Gabriel","Sergio","Gonzalo","Eric","Jorge","Rubén","Raúl","Iván","Pedro"],
        "last":["García","Martínez","López","Sánchez","Pérez","Gómez","Martín","Jiménez","Ruiz","Hernández",
                "Díaz","Moreno","Muñoz","Álvarez","Romero","Alonso","Gutiérrez","Navarro","Torres","Domínguez",
                "Vázquez","Ramos","Gil","Ramírez","Serrano","Blanco","Suárez","Molina","Morales","Ortega"]
    },
    "ITA": {
        "first":["Leonardo","Francesco","Alessandro","Lorenzo","Mattia","Andrea","Gabriele","Matteo","Riccardo","Tommaso",
                 "Edoardo","Davide","Federico","Giuseppe","Simone","Antonio","Daniele","Nicola","Pietro","Stefano",
                 "Paolo","Salvatore","Marco","Michele","Raffaele","Enrico","Filippo","Luca","Alberto","Giovanni"],
        "last":["Rossi","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco","Bruno",
                "Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Barbieri","Moretti",
                "Fontana","Santoro","Mariani","Rinaldi","Caruso","Ferrara","Fabbri","Bianco","Martini","Pellegrini"]
    },
    "NED": {
        "first":["Daan","Sem","Levi","Finn","Lucas","Liam","Milan","Thijs","Jesse","Noah",
                 "Bram","Niels","Gijs","Timo","Sven","Luuk","Joep","Jasper","Mees","Hugo",
                 "Ruben","Stijn","Sam","Nick","Thomas","Joris","Victor","Bas","Pieter","Koen"],
        "last":["de Jong","Jansen","de Vries","van den Berg","van Dijk","Bakker","Janssen","Visser","Smit","Meijer",
                "de Boer","Mulder","de Groot","Bos","Vos","Peters","Hendriks","Dekker","van Leeuwen","Kok",
                "Jacobs","van der Meer","Willems","van Dam","Post","Koster","van der Heijden","Kuipers","Boer","Veenstra"]
    },
    "BRA": {
        "first":["João","Gabriel","Mateus","Lucas","Pedro","Guilherme","Gustavo","Rafael","Felipe","Bruno",
                 "Enzo","Luiz","Daniel","Thiago","Eduardo","Vitor","Diego","Caio","Henrique","Samuel",
                 "Murilo","Fernando","André","Rodrigo","Marcelo","Antônio","Leonardo","Vinícius","Miguel","Alex"],
        "last":["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Alves","Pereira","Lima","Gomes",
                "Costa","Ribeiro","Carvalho","Nascimento","Araujo","Moreira","Dias","Barbosa","Vieira","Cardoso",
                "Rocha","Neves","Cunha","Monteiro","Machado","Mendes","Freitas","Teixeira","Ramos","Campos"]
    },
    "POR": {
        "first":["João","Martim","Rodrigo","Afonso","Santiago","Tomás","Gonçalo","Martim","Miguel","Francisco",
                 "Diogo","Duarte","Lourenço","Xavier","Tiago","Alexandre","Rúben","Luís","Pedro","Carlos",
                 "Henrique","Rafael","André","Vasco","Daniel","António","Bruno","Hugo","Nuno","Ricardo"],
        "last":["Silva","Santos","Ferreira","Pereira","Oliveira","Costa","Sousa","Rodrigues","Martins","Jesus",
                "Gomes","Marques","Alves","Almeida","Ribeiro","Pinto","Carvalho","Teixeira","Moreira","Correia",
                "Mendes","Nunes","Soares","Vieira","Monteiro","Cardoso","Sousa","Fonseca","Gonçalves","Machado"]
    },
    "BEL": {
        "first":["Noah","Lucas","Arthur","Liam","Louis","Jules","Hugo","Milan","Adam","Gabriel",
                 "Victor","Baptiste","Thomas","Nathan","Enzo","Mathis","Ethan","Raphaël","Sacha","Maxime",
                 "Tim","Simon","Quentin","Benjamin","Daan","Jens","Wout","Robin","Seppe","Lars"],
        "last":["Peeters","Janssens","Maes","Jacobs","Mertens","Willems","Claes","Goossens","Wouters","De Smet",
                "Dubois","Lambert","Dupont","Leroy","Van Damme","Vermeulen","De Clercq","Pauwels","Hendrickx","De Winter",
                "Desmet","Van den Bossche","De Vos","Verhoeven","Martens","Michiels","De Backer","Coppens","Vandenberghe","Smets"]
    },
    "TUR": {
        "first":["Mehmet","Mustafa","Ahmet","Ali","Hüseyin","Hasan","İbrahim","İsmail","Yusuf","Osman",
                 "Murat","Fatih","Serkan","Emre","Ömer","Kemal","Burak","Furkan","Halil","Ramazan",
                 "Eren","Batuhan","Uğur","Can","Kaan","Onur","Gökhan","Selim","Cem","Barış"],
        "last":["Yılmaz","Kaya","Demir","Şahin","Çelik","Yıldız","Yıldırım","Öztürk","Aydın","Arslan",
                "Doğan","Kılıç","Aslan","Çetin","Dere","Güneş","Bozkurt","Koç","Kaplan","Avcı",
                "Polat","Uzun","Aksoy","Duman","Bulut","Özdemir","Taş","Erdem","Türkmen","Özkan"]
    },
    "ARG": {
        "first":["Mateo","Thiago","Benjamín","Valentino","Joaquín","Lorenzo","Santino","Tomás","Lucas","Martín",
                 "Juan","Francisco","Agustín","Ignacio","Facundo","Emiliano","Matías","Nicolás","Bruno","Axel",
                 "Iker","Dylan","Gael","Simón","Iván","Renzo","Ulises","Bautista","Ramiro","Gonzalo"],
        "last":["González","Rodríguez","Gómez","Fernández","López","Díaz","Martínez","Pérez","Sánchez","Romero",
                "Sosa","Álvarez","Torres","Ruiz","Ramírez","Flores","Acosta","Benítez","Medina","Suárez",
                "Herrera","Molina","Castro","Ortiz","Núñez","Rojas","Arias","Vera","Silva","Ríos"]
    },
    "URU": {
        "first":["Santiago","Agustín","Juan","Lucas","Matías","Nicolás","Diego","Bruno","Martín","Facundo",
                 "Emiliano","Franco","Thiago","Benjamín","Joaquín","Tomás","Valentín","Gonzalo","Ramiro","Pablo",
                 "Ignacio","Sebastián","Nahuel","Axel","Kevin","Dylan","Lautaro","Gabriel","Leonardo","Felipe"],
        "last":["González","Rodríguez","Pérez","Fernández","López","Martínez","Silva","García","Sánchez","Díaz",
                "Álvarez","Torres","Ruiz","Suárez","Ramos","Castro","Vega","Méndez","Vázquez","Herrera",
                "Cardozo","Navarro","Cabrera","Rojas","Acuña","Aguiar","Valdez","Peralta","Crespo","Brum"]
    },
    "COL": {
        "first":["Santiago","Juan","Mateo","Nicolás","Samuel","David","Daniel","Sebastián","Andrés","Tomás",
                 "Jerónimo","Emmanuel","Julián","Gabriel","Felipe","Emilio","Cristian","Esteban","Brayan","Kevin",
                 "Johan","Harold","Carlos","Jorge","Michael","Patrick","Diego","Luis","Oscar","Rafael"],
        "last":["García","Rodríguez","Martínez","López","González","Pérez","Sánchez","Ramírez","Torres","Álvarez",
                "Castro","Gómez","Díaz","Ruiz","Moreno","Muñoz","Rojas","Espinosa","Suárez","Herrera",
                "Vargas","Guerrero","Ortiz","Rincón","Reyes","Navarro","Valencia","Cortés","Molina","Mejía"]
    },
    "USA": {
        "first":["Liam","Noah","Oliver","Elijah","James","William","Benjamin","Lucas","Henry","Alexander",
                 "Mason","Michael","Ethan","Daniel","Jacob","Logan","Jackson","Levi","Sebastian","Mateo",
                 "Jack","Owen","Theodore","Aiden","Samuel","Joseph","John","David","Wyatt","Matthew"],
        "last":["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
                "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
                "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson"]
    },
    "MEX": {
        "first":["Santiago","Mateo","Leonardo","Matías","Emiliano","Diego","Sebastián","Daniel","Emilio","Gael",
                 "Gabriel","Alexander","Thiago","Pablo","Carlos","Andrés","Fernando","Eduardo","Jorge","Javier",
                 "Iván","Erick","Héctor","Luis","Marco","Rafael","Adrián","Roberto","Mauricio","Óscar"],
        "last":["Hernández","García","Martínez","López","González","Pérez","Rodríguez","Sánchez","Ramírez","Cruz",
                "Flores","Gómez","Díaz","Reyes","Torres","Gutiérrez","Ruiz","Mendoza","Aguilar","Ortiz",
                "Morales","Delgado","Castillo","Vargas","Jiménez","Chávez","Ramos","Guerrero","Salazar","Silva"]
    },
    "SAU": {
        "first":["Abdullah","Mohammed","Abdulaziz","Fahad","Khalid","Ahmed","Saud","Turki","Sultan","Hassan",
                 "Yousef","Omar","Talal","Rayan","Nawaf","Bandar","Salman","Ibrahim","Mahmoud","Adel",
                 "Anas","Badr","Faisal","Hani","Hamza","Marwan","Rashed","Saeed","Ziyad","Majed"],
        "last":["Al-Saud","Al-Harbi","Al-Qahtani","Al-Mutairi","Al-Shammari","Al-Otaibi","Al-Ghamdi","Al-Zahrani","Al-Dosari","Al-Anazi",
                "Al-Shehri","Al-Subaie","Al-Johani","Al-Farhan","Al-Bishi","Al-Malki","Al-Salem","Al-Balawi","Al-Dhafiri","Al-Hajari",
                "Al-Najjar","Al-Suwaidi","Al-Ajmi","Al-Saadi","Al-Omari","Al-Hassan","Al-Asmari","Al-Fahad","Al-Harithi","Al-Harqan"]
    },
    "NGA": {
        "first":["Emeka","Chukwu","Ifeanyi","Uche","Chinedu","Tunde","Ade","Kelechi","Oluwaseun","Segun",
                 "Seyi","Babatunde","Ayo","Femi","Kunle","Gbenga","Olamide","Sola","Nonso","Uzo",
                 "Chima","Ikenna","Ibrahim","Yakubu","Isaac","Kelvin","Joseph","Michael","Samuel","Peter"],
        "last":["Okafor","Okeke","Okonkwo","Olawale","Ogunleye","Balogun","Adebayo","Adeyemi","Adenuga","Ogunbiyi",
                "Nwankwo","Nwosu","Nnamdi","Chukwu","Eze","Udo","Ojo","Ibrahim","Abdullahi","Yakubu",
                "Onyeka","Oputa","Oparah","Olowo","Odiase","Akinwale","Ogunjimi","Ige","Olonisakin","Aliyu"]
    },
    "MAR": {
        "first":["Youssef","Mohamed","Omar","Ayoub","Hassan","Anas","Mehdi","Ilyas","Khalid","Hamza",
                 "Soufiane","Ismail","Abdelaziz","Rachid","Reda","Yassine","Nabil","Tariq","Said","Imad",
                 "Karim","Abdelkader","Walid","Idriss","Bilal","Amin","Adil","Mounir","Samir","Hicham"],
        "last":["El Fassi","Ben Ali","El Idrissi","Bennani","El Amrani","Bouzid","El Mahdi","El Haddad","El Mansouri","Benjelloun",
                "El Ghazal","Chakiri","Alaoui","El Fakir","El Arbi","Benabdeljalil","Belkacem","Cherkaoui","El Ouahabi","El Khattabi",
                "Bensaid","Mouline","Bouchaib","Amrani","El Ouali","Othmani","Zaidi","Bendahmane","El Bouzidi","Jebbar"]
    },
    "KOR": {
        "first":["Minjun","Seo-Jun","Ha-Jun","Ji-Ho","Do-Yoon","Ji-Hoon","Joon-Woo","Si-Woo","Ye-Jun","Jin-Woo",
                 "Hyun-Woo","Sung-Min","Ji-Min","Dong-Hyun","Young-Ho","Jae-Hyun","Seung-Hyun","Joon-Ho","Tae-Hyun","Seung-Woo",
                 "Sang-Hoon","Jin-Ho","Woo-Jin","Jae-Won","Hyeon-Seo","Chan-Woo","Jun-Young","Min-Su","Tae-Min","Yong-Jun"],
        "last":["Kim","Lee","Park","Choi","Jung","Kang","Cho","Yoon","Jang","Lim",
                "Han","Shin","Seo","Kwon","Hwang","Ahn","Song","Ryu","Jeon","Hong",
                "Oh","Yang","Moon","Son","Bae","Baek","Yoo","Nam","Sim","Heo"]
    },
    "AUS": {
        "first":["Jack","Noah","William","Oliver","Thomas","Lucas","James","Liam","Henry","Charlie",
                 "Leo","Mason","Ethan","Alexander","Harrison","Cooper","Hunter","Xavier","Isaac","Levi",
                 "Archie","Jacob","Benjamin","Samuel","Hudson","Logan","Joshua","Nate","Angus","Flynn"],
        "last":["Smith","Jones","Williams","Brown","Taylor","Wilson","Johnson","White","Martin","Anderson",
                "Thompson","Nguyen","Harris","Walker","Clark","Hall","Young","King","Wright","Scott",
                "Green","Baker","Adams","Nelson","Mitchell","Roberts","Campbell","Moore","Murphy","Carter"]
    }
}

def gen_unique_name(nat:str, used:set)->str:
    pools = NAME_POOL.get(nat, NAME_POOL["COMMON"])
    fn_list = pools["first"] + NAME_POOL["COMMON"]["first"]
    ln_list = pools["last"]  + NAME_POOL["COMMON"]["last"]
    while True:
        n = f"{random.choice(fn_list)} {random.choice(ln_list)}"
        if n not in used:
            used.add(n)
            return n

# ---------- 国籍別バイアス ----------
def apply_bias(stats:dict, nat:str)->dict:
    s = stats.copy()
    if nat in ["ESP","FRA","BRA","ARG","POR","COL","MEX"]:
        s['Tec'] = min(99, s['Tec'] + 3)
    if nat in ["GER","ITA","URU","BEL","MAR","TUR"]:
        s['Def'] = min(99, s['Def'] + 3)
    if nat in ["NGA","USA","AUS","KOR","SAU"]:
        s['Phy'] = min(99, s['Phy'] + 3)
    return s

# =========================
# Part 3 / 12  --- League / Club builders & Standings init
# =========================

# ----- 国一覧（ユーザー指定） -----
NATIONS = ["ENG","GER","FRA","ESP","ITA","NED","BRA","POR","BEL","TUR",
           "ARG","URU","COL","USA","MEX","SAU","NGA","MAR","KOR","AUS"]

# ----- クラブ名自動生成用語彙（被り防止ユニーク生成） -----
ADJ_WORDS  = ["Apex","Crystal","Liberty","Imperial","Emerald","Crimson","Azure","Sterling",
              "Valiant","Solar","Arctic","Urban","Royal","Northern","Eastern","Western","Central",
              "Copper","Golden","Iron","Velvet","Ivory","Obsidian","Shadow","Silver","Bronze","Neon"]
NOUN_WORDS = ["Rovers","Athletic","City","Hearts","Dynamos","Giants","Rangers","Wolves","Phoenix",
              "Pilots","Falcons","Comets","United","Storm","Titans","Voyagers","Hawks","Harbor",
              "Dragons","Foxes","Orbit","Galaxy","Kings","Queens","Sentinels","Nomads","Vikings","Jets"]

def gen_club_name(used:set)->str:
    # 無限ループ回避のため多少ランダムで試す
    for _ in range(2000):
        n = f"{random.choice(ADJ_WORDS)} {random.choice(NOUN_WORDS)}"
        if n not in used:
            used.add(n)
            return n
    # フォールバック
    i=1
    while True:
        n=f"Club{i}"
        if n not in used:
            used.add(n); return n
        i+=1

def build_leagues(my_club:str)->dict:
    """
    return: {nation:{'D1':[clubs], 'D2':[clubs] ...}}
    ITAのみD2も作成。他はD1のみ。
    """
    leagues={}
    used=set([my_club])
    for nat in NATIONS:
        if nat=="ITA":
            leagues[nat]={"D1":[],"D2":[]}
            for _ in range(8):
                leagues[nat]["D1"].append(gen_club_name(used))
            for _ in range(8):
                leagues[nat]["D2"].append(gen_club_name(used))
        else:
            leagues[nat]={"D1":[]}
            for _ in range(8):
                leagues[nat]["D1"].append(gen_club_name(used))
    # ENG のD1に必ず自クラブを入れる（なければ先頭に）
    if "ENG" in leagues and "D1" in leagues["ENG"]:
        if my_club not in leagues["ENG"]["D1"]:
            leagues["ENG"]["D1"][0] = my_club
    return leagues

def build_standings(leagues:dict)->pd.DataFrame:
    rows=[]
    for nat, divs in leagues.items():
        for div, clubs in divs.items():
            for c in clubs:
                rows.append({"Nation":nat,"Division":div,"Club":c,
                             "W":0,"D":0,"L":0,"GF":0,"GA":0,"Pts":0})
    return pd.DataFrame(rows)

def build_club_map(df_stand:pd.DataFrame)->dict:
    # club -> (nation, division)
    return {r['Club']:(r['Nation'],r['Division']) for _,r in df_stand.iterrows()}

def sort_table(df):
    df = df.copy()
    if 'GD' not in df.columns and 'GF' in df.columns and 'GA' in df.columns:
        df['GD'] = df['GF'] - df['GA']
    return df.sort_values(['Pts','GD','GF'], ascending=[False,False,False]).reset_index(drop=True)

# =========================
# Part 4 / 12  --- Players / Offers / Scout / International / Init
# =========================

def gen_players(n:int, youth:bool, club:str, base_nat:str)->pd.DataFrame:
    ses = st.session_state
    used = ses.name_used
    rows=[]
    for _ in range(n):
        nat = base_nat if random.random()<0.5 else random.choice(NATIONS)
        name = gen_unique_name(nat, used)
        pos  = random.choices(["GK","DF","MF","FW"], weights=[1,4,5,3])[0]
        base_min, base_max = (52,82) if youth else (60,90)
        stats = {k: random.randint(base_min, base_max) for k in ABILITY_KEYS}
        stats = apply_bias(stats, nat)
        ovr = int(np.mean(list(stats.values())))

        styles = random.sample(pick_style_pool(nat), k=random.randint(1,3))
        growth = random.choice(pick_growth_pool(nat))

        rows.append({
            "Name":name,"Nat":nat,"Pos":pos,"Age":random.randint(15,18) if youth else random.randint(19,34),
            **stats,"OVR":ovr,"Matches_Played":0,"Goals":0,"Assists":0,"IntlApps":0,
            "Fatigue":0,"Injured":False,"Salary":random.randint(30_000,120_000) if youth else random.randint(120_000,1_200_000),
            "Contract":random.randint(1,2) if youth else random.randint(2,4),
            "Youth":youth,"Club":club,"PlayStyle":styles,"GrowthType":growth,
            "Value":normalize_value(ovr*random.randint(3500,5500)//100),
            "Status":"通常","RentalFrom":None,"RentalUntil":None,"OptionFee":None
        })
    return pd.DataFrame(rows)

# ------ オファー判定 ------
def offer_result(row, wage, years, fee, my_budget, policy="balanced"):
    want_wage = row['OVR']*120 + random.randint(-3000,3000)
    want_fee  = row['Value']
    coef = 0.8 if policy=='seller' else (1.2 if policy=='hold' else 1.0)
    wage_ok = wage >= want_wage
    fee_ok  = fee  >= want_fee*coef
    club_ok = random.random() < (0.7 if policy=='seller' else (0.4 if policy=='hold' else 0.55))
    money_ok= my_budget >= fee
    return (wage_ok and fee_ok and club_ok and money_ok), want_wage, int(want_fee*coef)

# ------ レンタル判定 ------
def rental_result(row, weeks, fee, my_budget, policy="balanced"):
    demand = int(row['Value']*0.15 + weeks*800)
    ok_fee = fee >= demand
    ok_club= random.random() < (0.65 if policy!='hold' else 0.4)
    return (ok_fee and ok_club and my_budget>=fee), demand

# ------ レンタル期限チェック ------
def tick_rentals(df, week, pending_list):
    for i,r in df.iterrows():
        if r.get('RentalUntil'):
            if week > r['RentalUntil'] and str(r.get('Status','')).startswith("レンタル中"):
                pending_list.append(r['Name'])
                df.at[i,'Status'] = "レンタル満了"
    return df, pending_list

# ------ レンタル満了処理UI ------
def handle_rental_expirations():
    ses = st.session_state
    if not ses.get('rental_pending'):
        return
    st.markdown("### レンタル満了選手の処理")
    all_df = pd.concat([ses.senior, ses.youth], ignore_index=True)
    for nm in ses.rental_pending[:]:
        row = all_df[all_df['Name']==nm]
        if row.empty:
            ses.rental_pending.remove(nm); continue
        r = row.iloc[0]
        st.write(f"**{r['Name']}** | Pos:{r['Pos']} | OVR:{r['OVR']} | 元:{r.get('RentalFrom')} | 買取OP:{fmt_money(r.get('OptionFee',0))}")
        c1,c2 = st.columns(2)
        with c1:
            if st.button(f"買取する（{fmt_money(r.get('OptionFee',0))}）", key=f"buy_{nm}"):
                if ses.budget >= (r.get('OptionFee') or 0):
                    ses.budget -= (r.get('OptionFee') or 0)
                    for dfname in ['senior','youth']:
                        df = getattr(ses,dfname)
                        idx = df.index[df['Name']==nm]
                        if len(idx)>0:
                            df.loc[idx, ['Club','RentalFrom','RentalUntil','OptionFee','Status']] = \
                                [ses.my_club, None, None, None, "通常"]
                            setattr(ses,dfname,df)
                            break
                    st.success("買取成立！")
                    ses.rental_pending.remove(nm)
                else:
                    st.error("予算不足です。")
        with c2:
            if st.button("返却する", key=f"return_{nm}"):
                origin = r.get('RentalFrom')
                # 自クラブ側から削除
                for dfname in ['senior','youth']:
                    df = getattr(ses,dfname)
                    idx = df.index[df['Name']==nm]
                    if len(idx)>0:
                        bak = df.loc[idx[0]].copy()
                        df.drop(idx, inplace=True)
                        setattr(ses,dfname,df)
                        break
                # 元クラブ(=AI)へ戻す
                bak['Club']=origin
                bak[['RentalFrom','RentalUntil','OptionFee','Status']] = [None,None,None,"通常"]
                ses.ai_players = pd.concat([ses.ai_players, pd.DataFrame([bak])], ignore_index=True)
                st.info("返却完了")
                ses.rental_pending.remove(nm)

# ------ スカウト候補生成 ------
def gen_scout_candidates(n=8, youth=False):
    ses = st.session_state
    pool = ses.ai_players.copy()
    if youth:
        pool = pool[pool['Age']<=18]
    else:
        pool = pool[pool['Age']>=19]

    free_df = gen_players(max(1,n//2), youth=youth, club="Free", base_nat=random.choice(NATIONS))
    take = n - len(free_df)
    others = pool[pool['Club']!=ses.my_club]
    pick_df = others.sample(min(take, len(others))) if len(others)>0 else pd.DataFrame()

    cands = pd.concat([free_df, pick_df], ignore_index=True)
    cands['PlayStyle'] = cands['PlayStyle'].apply(lambda x: " / ".join(x) if isinstance(x,list) else x)
    cands['Value'] = cands['Value'].apply(normalize_value)
    return cands.sample(frac=1).reset_index(drop=True)

def get_rental_candidates():
    ses = st.session_state
    pool = ses.ai_players
    return pool[(pool['Club']!=ses.my_club) & (pool['RentalFrom'].isna())]

# ------ 国際大会自動進行 ------
def auto_intl_round():
    ses = st.session_state
    if 'intl_tournament' not in ses or not ses.intl_tournament:
        # 各国D1上位2クラブ
        clubs=[]
        for nat, divs in ses.leagues.items():
            if "D1" in divs:
                tmp = ses.standings[(ses.standings.Nation==nat)&(ses.standings.Division=="D1")]
                top2 = tmp.sort_values('Pts', ascending=False).head(2)['Club'].tolist()
                clubs.extend(top2)
        random.shuffle(clubs)
        ses.intl_tournament = {"clubs":clubs, "results":[], "finished":False}
        return

    if ses.intl_tournament.get("finished"):
        return

    clubs = ses.intl_tournament['clubs']
    if len(clubs) <= 1:
        ses.intl_tournament['finished'] = True
        return

    winners=[]
    for i in range(0, len(clubs)-1, 2):
        c1, c2 = clubs[i], clubs[i+1]
        g1, g2 = random.randint(0,4), random.randint(0,4)
        pk_txt=""
        if g1==g2:
            pk1,pk2 = random.randint(3,6), random.randint(3,6)
            while pk1==pk2:
                pk1,pk2 = random.randint(3,6), random.randint(3,6)
            pk_txt=f"PK {pk1}-{pk2}"
            win = c1 if pk1>pk2 else c2
        else:
            win = c1 if g1>g2 else c2

        ses.intl_tournament['results'].append((c1,g1,c2,g2,pk_txt,win))
        ses.sns_posts.append(f"[国際大会] {c1} {g1}-{g2} {c2} {pk_txt} → 勝者:{win}")
        ses.sns_times.append(datetime.now())

        # 個人成績（簡易）
        pool_all = pd.concat([ses.senior, ses.youth, ses.ai_players], ignore_index=True)
        XI1 = pool_all[pool_all['Club']==c1].nlargest(11,'OVR')
        XI2 = pool_all[pool_all['Club']==c2].nlargest(11,'OVR')

        ses.intl_player_stats = ses.intl_player_stats or {}
        for club, goals in [(c1,g1),(c2,g2)]:
            XI = XI1 if club==c1 else XI2
            if XI.empty: continue
            for _ in range(goals):
                pid = XI.sample(1).index[0]
                n1  = XI.loc[pid,'Name']; p1 = XI.loc[pid,'Pos']
                ses.intl_player_stats.setdefault(n1, {'G':0,'A':0,'Club':club,'Pos':p1})
                ses.intl_player_stats[n1]['G'] += 1

                pid2 = XI.sample(1).index[0]
                n2  = XI.loc[pid2,'Name']; p2 = XI.loc[pid2,'Pos']
                ses.intl_player_stats.setdefault(n2, {'G':0,'A':0,'Club':club,'Pos':p2})
                ses.intl_player_stats[n2]['A'] += 1

        # 自クラブ選手の国際出場数
        if c1==ses.my_club or c2==ses.my_club:
            starters_names = ses.starters if ses.starters else ses.senior.nlargest(11,'OVR')['Name'].tolist()
            for nm in starters_names:
                for dfname in ['senior','youth']:
                    df = getattr(ses,dfname)
                    idx = df.index[df['Name']==nm]
                    if len(idx)>0:
                        df.at[idx[0],'IntlApps'] += 1
                        setattr(ses,dfname,df)

        winners.append(win)
    if len(clubs)%2==1:
        winners.append(clubs[-1])

    ses.intl_tournament['clubs']=winners
    if len(winners)==1:
        ses.intl_tournament['finished']=True
        ses.sns_posts.append(f"[国際大会] 優勝: {winners[0]}")
        ses.sns_times.append(datetime.now())

# ------ 初期化 ------
def init_session():
    ses = st.session_state
    if ses.get('initialized'): return
    ses.initialized = True

    ses.name_used = set()
    ses.my_club   = "Signature Team"

    ses.leagues   = build_leagues(ses.my_club)
    ses.standings = build_standings(ses.leagues)
    ses.club_map  = build_club_map(ses.standings)

    ses.senior = gen_players(30, False, ses.my_club, "ENG")
    ses.youth  = gen_players(20, True,  ses.my_club, "ENG")

    # AIクラブ選手
    pool=[]
    for c in ses.standings.Club:
        if c==ses.my_club: continue
        nat = random.choice(NATIONS)
        pool.append(gen_players(15, False, c, nat))
    ses.ai_players = pd.concat(pool, ignore_index=True)

    ses.week = 1
    ses.budget = 5_000_000
    ses.finance_log = []
    ses.player_history = {}
    ses.auto_selected = False
    ses.starters = []
    ses.match_log = []
    ses.scout_pool = pd.DataFrame()
    ses.intl_tournament = {}
    ses.intl_player_stats = {}
    ses.sns_posts = []
    ses.sns_times = []
    ses.rental_pending = []
    ses.need_positions = suggest_positions(ses.senior)

init_session()

# =========================
# Part 5 / 12  --- ハウスキーピング / 共通試合処理
# =========================
ses = st.session_state

def update_standings_global(home, away, gh, ga):
    df = ses.standings
    if gh > ga:
        df.loc[df.Club==home, ['W','Pts']] += [1,3]
        df.loc[df.Club==away, 'L'] += 1
    elif gh < ga:
        df.loc[df.Club==away, ['W','Pts']] += [1,3]
        df.loc[df.Club==home, 'L'] += 1
    else:
        df.loc[df.Club.isin([home,away]), 'D']   += 1
        df.loc[df.Club.isin([home,away]), 'Pts'] += 1
    df.loc[df.Club==home, ['GF','GA']] += [gh, ga]
    df.loc[df.Club==away, ['GF','GA']] += [ga, gh]
    ses.standings = df

def housekeeping():
    # 欠損初期化
    for att, init_val in [
        ('sns_posts', []), ('sns_times', []),
        ('intl_player_stats', {}), ('rental_pending', []),
        ('scout_pool', pd.DataFrame())
    ]:
        if att not in ses: setattr(ses, att, init_val)

    # レンタル期限チェック
    pending=[]
    ses.senior, pending = tick_rentals(ses.senior, ses.week, pending)
    ses.youth,  pending = tick_rentals(ses.youth,  ses.week, pending)
    if pending:
        ses.rental_pending = list(set(ses.rental_pending + pending))

    # 順位表整列 & マップ更新
    ses.standings = sort_table(ses.standings)
    ses.club_map  = build_club_map(ses.standings)

    # 補強推奨更新
    ses.need_positions = suggest_positions(ses.senior)

housekeeping()

# =========================
# Part 6 / 12  --- Tabs / Senior / Youth / Detail
# =========================

tabs = st.tabs([
    "シニア","ユース","選手詳細","試合","順位表",
    "スカウト/移籍","レンタル管理","SNS","財務レポート",
    "年間表彰","ランキング/国際大会","クラブ設定"
])

# ---------- 0) シニア ----------
with tabs[0]:
    st.markdown('<div style="color:#fff;font-size:20px;">シニア選手一覧</div>', unsafe_allow_html=True)
    handle_rental_expirations()

    order_mode = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="order_senior")
    reverse_flag = (order_mode == "FW→MF→DF→GK")

    df_s = ses.senior[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Club','Status','Goals','Assists']]
    df_s['PlayStyle'] = df_s['PlayStyle'].apply(lambda x: " / ".join(x) if isinstance(x,list) else x)
    df_s = sort_by_pos(df_s, reverse=reverse_flag)

    st.dataframe(
        df_s.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                  .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# ---------- 1) ユース ----------
with tabs[1]:
    st.markdown('<div style="color:#fff;font-size:20px;">ユース選手一覧</div>', unsafe_allow_html=True)

    order_mode_y = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="order_youth")
    reverse_flag_y = (order_mode_y == "FW→MF→DF→GK")

    df_y = ses.youth[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Club','Status','Goals','Assists']]
    df_y['PlayStyle'] = df_y['PlayStyle'].apply(lambda x: " / ".join(x) if isinstance(x,list) else x)
    df_y = sort_by_pos(df_y, reverse=reverse_flag_y)

    st.dataframe(
        df_y.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                  .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# ---------- 2) 選手詳細 ----------
with tabs[2]:
    pool_detail = pd.concat([ses.senior, ses.youth], ignore_index=True)
    if pool_detail.empty:
        st.markdown("<div class='tab-info'>表示できる選手がいません。</div>", unsafe_allow_html=True)
    else:
        sel_name = st.selectbox("選手選択", pool_detail['Name'].tolist())
        prow = pool_detail.loc[pool_detail['Name']==sel_name].iloc[0]

        st.write(f"ポジション: {prow['Pos']} / OVR:{prow['OVR']} / 年齢:{prow['Age']}")
        st.write(f"国籍: {prow['Nat']} / 国際大会出場: {prow.get('IntlApps',0)}回")
        st.write(f"所属: {prow['Club']} / 状態: {prow.get('Status','')}")
        st.write("プレースタイル: " + (", ".join(prow['PlayStyle']) if isinstance(prow['PlayStyle'],list) else prow['PlayStyle']))

        vals = [prow[k] for k in ABILITY_KEYS]
        fig_r = radar_chart(vals, ABILITY_KEYS)
        st.pyplot(fig_r)

        hist = pd.DataFrame(ses.player_history.get(
            sel_name, [{'week':0,'OVR':prow['OVR'], **{k:prow[k] for k in ABILITY_KEYS}}]
        ))
        if len(hist) > 1:
            fig_all, ax_all = plt.subplots()
            for k in ABILITY_KEYS:
                ax_all.plot(hist['week'], hist[k], marker='o', label=k)
            ax_all.set_xlabel('節'); ax_all.set_ylabel('能力'); ax_all.legend(bbox_to_anchor=(1,1))
            make_transparent(ax_all)
            st.pyplot(fig_all)

            fig_ovr, ax_ovr = plt.subplots()
            ax_ovr.plot(hist['week'], hist['OVR'], marker='o')
            ax_ovr.set_xlabel('節'); ax_ovr.set_ylabel('総合値')
            make_transparent(ax_ovr)
            st.pyplot(fig_ovr)
        else:
            st.markdown("<div class='tab-info'>成長データはまだありません。</div>", unsafe_allow_html=True)

      # =========================
# Part 7 / 12  --- 試合 / 順位表
# =========================

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
            p,cnt=req[i],req[i+1]
            starters += ses.senior[ses.senior['Pos']==p].nlargest(cnt,'OVR')['Name'].tolist()
        ses.starters = starters
        ses.auto_selected = True

    if ses.starters:
        st.markdown('<span style="color:white;font-weight:bold;">【先発メンバー】</span>', unsafe_allow_html=True)
        s_df = ses.senior[ses.senior['Name'].isin(ses.starters)][['Name','Pos','OVR','Goals','Assists','PlayStyle','Club']]
        s_df['PlayStyle']=s_df['PlayStyle'].apply(lambda x:" / ".join(x) if isinstance(x,list) else x)
        s_df = sort_by_pos(s_df)
        st.dataframe(
            s_df.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                      .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )
    else:
        st.warning("『オート先発選考』を行わないと試合開始できません。")

    # 自クラブの同リーグから対戦相手を自動選択
    my_nat, my_div = ses.club_map[ses.my_club]
    same_league = ses.standings[(ses.standings.Nation==my_nat)&(ses.standings.Division==my_div)]
    opp_choices = [c for c in same_league.Club if c!=ses.my_club]
    opp = random.choice(opp_choices) if opp_choices else ses.my_club

    kickoff = st.button("キックオフ", disabled=(not ses.auto_selected or ses.week>SEASON_WEEKS))
    if kickoff:
        atk = ses.senior[ses.senior['Name'].isin(ses.starters)]['OVR'].mean() if ses.starters else 70
        oppatk = random.uniform(60,90)
        gh = max(0,int(np.random.normal((atk-60)/8,1)))
        ga = max(0,int(np.random.normal((oppatk-60)/8,1)))
        shots = random.randint(5,15)
        on_t  = random.randint(0,shots)
        poss  = random.randint(40,60)

        # ゴール/アシスト
        scorers=[]; assisters=[]
        if gh>0 and ses.starters:
            for _ in range(gh):
                s = random.choice(ses.starters)
                candidates = [x for x in ses.starters if x!=s]
                a = random.choice(candidates) if candidates else s
                scorers.append(s); assisters.append(a)
                ses.senior.loc[ses.senior['Name']==s,'Goals']   += 1
                ses.senior.loc[ses.senior['Name']==a,'Assists'] += 1

        update_standings_global(ses.my_club, opp, gh, ga)

        # 他クラブ試合
        done_pairs={(ses.my_club,opp)}
        for nat, divs in ses.leagues.items():
            for div, clubs in divs.items():
                cl = clubs[:]
                random.shuffle(cl)
                for i in range(0,len(cl),2):
                    if i+1>=len(cl): break
                    h,a = cl[i], cl[i+1]
                    if (h,a) in done_pairs or (a,h) in done_pairs: continue
                    g1,g2 = random.randint(0,3), random.randint(0,3)
                    update_standings_global(h,a,g1,g2)
                    done_pairs.add((h,a))

        # ログ類
        ses.match_log.append({'week':ses.week,'opp':opp,'gf':gh,'ga':ga,'scorers':scorers,'assisters':assisters})
        ses.sns_posts.append(f"{ses.my_club} {gh}-{ga} {opp}｜得点:{', '.join(scorers) if scorers else 'なし'} / アシスト:{', '.join(assisters) if assisters else 'なし'}")
        ses.sns_times.append(datetime.now())
        ses.finance_log.append({
            'week': ses.week,
            'revenue_ticket': gh*15000 + random.randint(5000,10000),
            'revenue_goods' : ga*8000  + random.randint(1000,5000),
            'expense_salary': int(ses.senior['OVR'].mean()*1000)
        })

        # 成長反映
        ses.senior = apply_growth(ses.senior, ses.week)
        for _,rw in ses.senior.iterrows():
            update_player_history(rw['Name'], rw, ses.week)

        st.success(f"結果 {gh}-{ga}")
        if scorers:   st.write("得点者: " + " / ".join(scorers))
        if assisters: st.write("アシスト: " + " / ".join(assisters))
        st.write(f"シュート:{shots}（枠内:{on_t}） / ポゼッション:{poss}%")

        ses.week += 1
        ses.auto_selected = False
        auto_intl_round()

        if ses.week > SEASON_WEEKS:
            st.success("シーズン終了！『年間表彰』タブ等をご確認ください。")

    elif ses.week > SEASON_WEEKS:
        st.info("シーズン終了済です。『クラブ設定』で新シーズン開始できます。")

# ---------- 4) 順位表 ----------
with tabs[4]:
    st.markdown('<div style="color:#fff;font-size:20px;">順位表</div>', unsafe_allow_html=True)
    nations = list(ses.leagues.keys())
    sel_nat = st.selectbox("国を選択", nations)
    sel_div = st.selectbox("ディビジョンを選択", list(ses.leagues[sel_nat].keys()))
    df_st = ses.standings[(ses.standings.Nation==sel_nat)&(ses.standings.Division==sel_div)]
    df_st = sort_table(df_st)
    st.dataframe(
        df_st.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                   .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# =========================
# Part 8 / 12  --- スカウト / 移籍
# =========================

with tabs[5]:
    st.markdown("<div style='color:#fff;font-size:20px;'>スカウト / 移籍 / 補強</div>", unsafe_allow_html=True)

    cat = st.radio("対象カテゴリー", ["シニア候補","ユース候補"], horizontal=True, key="scout_cat")
    youth_flag = (cat == "ユース候補")

    # 補強推奨
    base_df = ses.youth if youth_flag else ses.senior
    ses.need_positions = suggest_positions(base_df)
    st.markdown(f"**補強推奨ポジション:** {', '.join(ses.need_positions)}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("候補リスト更新", key="refresh_scout"):
            ses.scout_pool = gen_scout_candidates(n=8, youth=youth_flag)
    with c2:
        st.write(f"予算：{fmt_money(ses.budget)}")

    if ses.scout_pool is None or ses.scout_pool.empty:
        st.markdown("<div class='tab-info'>候補がいません。『候補リスト更新』を押してください。</div>", unsafe_allow_html=True)
    else:
        for i, row in ses.scout_pool.iterrows():
            st.markdown("<div class='scout-card'>", unsafe_allow_html=True)
            st.markdown(
                f"**{row['Name']}**｜{row['Nat']}｜{row['Age']}歳｜{row['Pos']}｜OVR:{row['OVR']}<br>"
                f"PlayStyle: {row['PlayStyle']}<br>"
                f"所属:{row['Club']}｜評価額:{fmt_money(row['Value'])}",
                unsafe_allow_html=True
            )

            if row['Club'] == "Free":
                if st.button("契約", key=f"sign_free_{i}"):
                    dst = 'youth' if youth_flag else 'senior'
                    setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row])], ignore_index=True))
                    ses.scout_pool = ses.scout_pool.drop(i).reset_index(drop=True)
                    st.success("獲得しました！")
            else:
                mode = st.selectbox(f"オファー種別（{row['Name']}）", ["完全移籍","レンタル(買取OP付)"], key=f"offer_mode_{i}")
                policy = "balanced"

                with st.form(f"offer_form_{i}"):
                    if mode == "完全移籍":
                        wage  = st.number_input("提示年俸(€)", min_value=0, value=row['OVR']*150, key=f"wage_{i}")
                        years = st.slider("契約年数", 1, 5, 3, key=f"years_{i}")
                        fee   = st.number_input("移籍金(€)", min_value=0, value=int(row['Value']), key=f"fee_{i}")
                        submit_full = st.form_submit_button("送信")
                        if submit_full:
                            ok, want_wage, want_fee = offer_result(row, wage, years, fee, ses.budget, policy)
                            if ok:
                                ses.budget -= fee
                                row2 = row.copy()
                                row2['Club'] = ses.my_club
                                dst = 'youth' if youth_flag else 'senior'
                                setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row2])], ignore_index=True))
                                ses.ai_players = ses.ai_players[ses.ai_players['Name']!=row['Name']]
                                ses.scout_pool = ses.scout_pool.drop(i).reset_index(drop=True)
                                st.success("移籍成立！")
                            else:
                                st.error(f"拒否：要求目安 年俸{want_wage}€, 移籍金{want_fee}€")
                    else:
                        weeks = st.slider("レンタル期間（節）", 1, 8, 4, key=f"weeks_{i}")
                        fee_r = st.number_input("レンタル料(€)", min_value=0, value=int(row['Value']*0.15), key=f"rentfee_{i}")
                        opt   = st.number_input("買取オプション額(€)", min_value=0, value=int(row['Value']*1.2), key=f"optfee_{i}")
                        submit_rent = st.form_submit_button("送信")
                        if submit_rent:
                            ok, demand = rental_result(row, weeks, fee_r, ses.budget, policy)
                            if ok:
                                ses.budget -= fee_r
                                row2 = row.copy()
                                row2['Club']        = ses.my_club
                                row2['RentalFrom']  = row['Club']
                                row2['RentalUntil'] = ses.week + weeks
                                row2['OptionFee']   = opt
                                row2['Status']      = f"レンタル中({weeks}節)"
                                dst = 'youth' if youth_flag else 'senior'
                                setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row2])], ignore_index=True))
                                ses.ai_players = ses.ai_players[ses.ai_players['Name']!=row['Name']]
                                ses.scout_pool = ses.scout_pool.drop(i).reset_index(drop=True)
                                st.success("レンタル成立！")
                            else:
                                st.error(f"拒否：要求額目安 {fmt_money(demand)}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")

      # =========================
# Part 9 / 12  --- レンタル管理 / SNS
# =========================

# -------- 6) レンタル管理 --------
with tabs[6]:
    st.markdown("<div style='color:#fff;font-size:20px;'>レンタル管理</div>", unsafe_allow_html=True)
    handle_rental_expirations()

    df_r = pd.concat([ses.senior, ses.youth], ignore_index=True)
    df_r = df_r[df_r['Status'].str.startswith("レンタル中", na=False)][
        ['Name','Pos','OVR','RentalFrom','RentalUntil','OptionFee','Status']
    ]
    if df_r.empty:
        st.markdown("<div class='tab-info'>レンタル中の選手はいません。</div>", unsafe_allow_html=True)
    else:
        st.dataframe(
            df_r.style.set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

# -------- 7) SNS --------
with tabs[7]:
    st.markdown("<div style='color:#fff;font-size:20px;'>SNS / ファン投稿</div>", unsafe_allow_html=True)
    if ses.sns_posts:
        for t, p in zip(reversed(ses.sns_times), reversed(ses.sns_posts)):
            st.write(f"{t.strftime('%m/%d %H:%M')} - {p}")
    else:
        st.markdown("<div class='tab-info'>投稿はまだありません。</div>", unsafe_allow_html=True)

  # =========================
# Part 10 / 12  --- 財務レポート
# =========================

with tabs[8]:
    st.markdown("<div style='color:#fff;font-size:20px;'>財務レポート</div>", unsafe_allow_html=True)

    df_fin = pd.DataFrame(ses.finance_log)
    if df_fin.empty:
        st.markdown("<div class='tab-info'>まだ試合がないため財務データがありません。</div>", unsafe_allow_html=True)
    else:
        df_fin_j = df_fin.rename(columns={
            'week':'節','revenue_ticket':'チケット収入','revenue_goods':'グッズ収入','expense_salary':'人件費'
        })
        df_fin_j['総収入'] = df_fin_j['チケット収入'] + df_fin_j['グッズ収入']
        df_fin_j['収支']   = df_fin_j['総収入'] - df_fin_j['人件費']

        fig, ax = plt.subplots()
        ax.plot(df_fin_j['節'], df_fin_j['総収入'], marker='o', label='総収入')
        ax.plot(df_fin_j['節'], df_fin_j['人件費'], marker='o', label='人件費')
        ax.plot(df_fin_j['節'], df_fin_j['収支'],   marker='o', label='収支')
        ax.set_xlabel("節"); ax.set_ylabel("金額(€)")
        ax.set_title("財務推移")
        ax.legend()
        make_transparent(ax)
        st.pyplot(fig)

        st.dataframe(
            df_fin_j.style.set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

  # =========================
# Part 11 / 12  --- 年間表彰 / ランキング & 国際大会
# =========================

# -------- 9) 年間表彰 --------
with tabs[9]:
    st.markdown('<div style="color:white;font-size:20px;">年間表彰</div>', unsafe_allow_html=True)

    df_my = pd.concat([ses.senior, ses.youth], ignore_index=True)
    for col in ['Goals','Assists']:
        if col not in df_my: df_my[col]=0

    top5g = df_my.nlargest(5,'Goals')[['Name','Pos','Goals','Club']]
    top5a = df_my.nlargest(5,'Assists')[['Name','Pos','Assists','Club']]

    st.markdown('<span style="color:white;font-weight:bold;">🏅 自クラブ 得点王 TOP5</span>', unsafe_allow_html=True)
    if top5g.empty:
        st.markdown("<div class='tab-info'>データがありません。</div>", unsafe_allow_html=True)
    else:
        st.dataframe(
            top5g.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                      .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

    st.markdown('<span style="color:white;font-weight:bold;">🎯 自クラブ アシスト王 TOP5</span>', unsafe_allow_html=True)
    if top5a.empty:
        st.markdown("<div class='tab-info'>データがありません。</div>", unsafe_allow_html=True)
    else:
        st.dataframe(
            top5a.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                      .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

# -------- 10) ランキング / 国際大会 --------
with tabs[10]:
    st.markdown('<div style="color:white;font-size:22px;font-weight:bold;">ランキング / 国際大会まとめ</div>', unsafe_allow_html=True)

    # 国際大会ログ
    st.markdown("### 🌍 国際大会 試合ログ")
    if not ses.intl_tournament or len(ses.intl_tournament.get('results',[]))==0:
        st.markdown("<div class='tab-info'>国際大会は未開催です。試合を進めると自動で進行します。</div>", unsafe_allow_html=True)
    else:
        for i,m in enumerate(ses.intl_tournament['results'],1):
            line = f"【R{i}】 {m[0]} {m[1]}-{m[3]} {m[2]} {m[4]} → 勝者:{m[5]}"
            if ses.my_club in line:
                st.markdown(f"<span style='background:#f7df70;color:#202b41;font-weight:bold'>{line}</span>", unsafe_allow_html=True)
            else:
                st.write(line)
        if ses.intl_tournament.get('finished') and len(ses.intl_tournament.get('clubs',[]))==1:
            champ = ses.intl_tournament['clubs'][0]
            msg = f"優勝: {champ}"
            if champ==ses.my_club:
                st.markdown(f"<span style='background:#f7df70;color:#202b41;font-weight:bold'>{msg}</span>", unsafe_allow_html=True)
            else:
                st.success(msg)

    st.markdown("---")

    # 国際大会個人成績
    st.markdown("### 🏆 国際大会 個人成績ランキング")
    if not ses.get('intl_player_stats'):
        st.markdown("<div class='tab-info'>国際大会の個人成績データがまだありません。</div>", unsafe_allow_html=True)
    else:
        df_intp = pd.DataFrame.from_dict(ses.intl_player_stats, orient='index')
        for c in ['G','A','Club','Pos','Name']:
            if c not in df_intp.columns: df_intp[c]=0
        df_intp['Name']=df_intp.index

        top_g = df_intp.sort_values('G', ascending=False).head(10)[['Name','Pos','G','A','Club']]
        st.markdown("**得点ランキング TOP10**")
        st.dataframe(
            top_g.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                       .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

        top_a = df_intp.sort_values('A', ascending=False).head(10)[['Name','Pos','A','G','Club']]
        st.markdown("**アシストランキング TOP10**")
        st.dataframe(
            top_a.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                       .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

        best11=[]
        for p,need in [('GK',1),('DF',4),('MF',4),('FW',2)]:
            cand = df_intp[df_intp['Pos']==p].copy()
            cand['Score'] = cand['G']*2 + cand['A']
            best11.append(cand.sort_values('Score', ascending=False).head(need)[['Name','Pos','G','A','Club']])
        best11 = pd.concat(best11)
        st.markdown("**⚽️ 国際大会ベストイレブン**")
        st.dataframe(
            best11.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                        .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

    st.markdown("---")

    # 各国リーグまとめ
    st.markdown("### 🇪🇺 各国リーグランキング（順位表・得点王・アシスト王・ベスト11）")
    df_all = pd.concat([ses.senior, ses.youth, ses.ai_players], ignore_index=True)
    for col in ['Goals','Assists']:
        if col not in df_all: df_all[col]=0
    df_all['Nation']   = df_all['Club'].map(lambda c: ses.club_map.get(c,("",""))[0] if c in ses.club_map else "")
    df_all['Division'] = df_all['Club'].map(lambda c: ses.club_map.get(c,("",""))[1] if c in ses.club_map else "")

    for nat, divs in ses.leagues.items():
        st.markdown(f"## {nat}")
        for div in divs.keys():
            st.markdown(f"#### {div} 順位表")
            df_st = ses.standings[(ses.standings.Nation==nat)&(ses.standings.Division==div)].copy()
            df_st = sort_table(df_st)
            st.dataframe(
                df_st.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                           .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
                use_container_width=True
            )

            sub = df_all[(df_all['Nation']==nat)&(df_all['Division']==div)].copy()
            if sub.empty:
                st.markdown("<div class='tab-info'>選手データなし</div>", unsafe_allow_html=True)
                st.markdown("---")
                continue

            top_s = sub.nlargest(5,'Goals')[['Name','Pos','Goals','Club']]
            top_a = sub.nlargest(5,'Assists')[['Name','Pos','Assists','Club']]

            st.markdown('<span style="color:white;font-weight:bold;">🏅 得点王 TOP5</span>', unsafe_allow_html=True)
            st.dataframe(
                top_s.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                           .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
                use_container_width=True
            )

            st.markdown('<span style="color:white;font-weight:bold;">🎯 アシスト王 TOP5</span>', unsafe_allow_html=True)
            st.dataframe(
                top_a.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                           .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
                use_container_width=True
            )

            best11=[]
            for p,need in [('GK',1),('DF',4),('MF',4),('FW',2)]:
                cand = sub[sub['Pos']==p].nlargest(need,'OVR')[['Name','Pos','OVR','Club']]
                best11.append(cand)
            best11 = pd.concat(best11)
            st.markdown('<span style="color:white;font-weight:bold;">⚽️ ベストイレブン</span>', unsafe_allow_html=True)
            st.dataframe(
                best11.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                            .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
                use_container_width=True
            )
            st.markdown("---")

      # =========================
# Part 12 / 12  --- クラブ設定 / リセット / 終端
# =========================

with tabs[11]:
    st.markdown('<div style="color:white;font-size:20px;">クラブ設定</div>', unsafe_allow_html=True)

    new_name = st.text_input("自クラブ名を変更", value=ses.my_club, max_chars=40)
    if st.button("クラブ名変更"):
        if new_name and new_name != ses.my_club:
            old = ses.my_club
            ses.my_club = new_name
            # standings / leagues を再構築（ENG D1 の先頭に置き直す）
            ses.leagues   = build_leagues(ses.my_club)
            ses.standings = build_standings(ses.leagues)
            ses.club_map  = build_club_map(ses.standings)
            # 所属変更
            for dfname in ['senior','youth']:
                df = getattr(ses, dfname)
                df.loc[df['Club']==old,'Club']=ses.my_club
                setattr(ses, dfname, df)
            st.success("クラブ名を変更しました。再実行すると正しく反映されます。")

    st.markdown("---")
    st.markdown("### シーズン管理")

    def reset_season():
        # 順位表だけリセット
        ses.standings = build_standings(ses.leagues)
        # 個人成績リセット（OVR等能力値は維持）
        for dfname in ['senior','youth','ai_players']:
            df = getattr(ses, dfname)
            for col in ['Matches_Played','Goals','Assists','IntlApps','Fatigue']:
                if col in df.columns:
                    df[col]=0
            if 'Status' in df.columns:
                df['Status'] = "通常"
            if 'RentalFrom' in df.columns:
                df[['RentalFrom','RentalUntil','OptionFee']] = [None,None,None]
            setattr(ses, dfname, df)

        ses.week = 1
        ses.finance_log.clear()
        ses.match_log.clear()
        ses.player_history.clear()
        ses.intl_tournament.clear()
        ses.intl_player_stats.clear()
        ses.sns_posts.clear(); ses.sns_times.clear()
        ses.rental_pending.clear()
        ses.auto_selected = False
        ses.starters = []
        housekeeping()

    if st.button("新シーズン開始"):
        reset_season()
        st.success("新シーズン開始！")

    st.caption("保存が必要な場合は、Streamlit のセッションステートを外部に保存する処理を別途実装してください。")

# ---- 終端表示 ----
st.caption("✅ 全パート読み込み完了。エラーが出た場合は、エラーメッセージ冒頭行を教えてください。")

