# =========================
# Part 1 / 13  --- Imports / Config / CSS / 定数・共通関数(1)
# =========================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime
import math

# --- ページ設定 ---
st.set_page_config(page_title="Club Strive", layout="wide")
random.seed(42)
np.random.seed(42)

# --- Matplotlib 全体白文字＆透明背景 ---
plt.rcParams.update({
    'text.color':'#fff',
    'axes.labelcolor':'#fff',
    'xtick.color':'#fff',
    'ytick.color':'#fff',
    'axes.edgecolor':'#fff',
    'figure.facecolor':'none',
    'axes.facecolor':'none',
    'legend.edgecolor':'#fff'
})

# --- CSS/UIカスタム ---
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }
h1,h2,h3,h4,h5,h6 { color:#fff!important; margin:0 0 8px 0; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }
.stButton>button{
  background:#27e3b9!important; color:#202b41!important; font-weight:bold!important;
  border-radius:10px!important; margin:6px 0; border:0!important; padding:6px 18px!important;
}
.stButton>button:active { background:#ffee99!important; }
div[data-testid="stFormSubmitButton"] button{
  background:#27e3b9!important; color:#202b41!important; font-weight:bold!important;
  border-radius:10px!important; border:0!important; padding:6px 18px!important;
}
.player-card { background:#fff; color:#132346; border-radius:12px; padding:10px; margin:8px; min-width:140px; max-width:160px; box-shadow:0 0 8px #0003; }
.detail-popup { position:absolute; top:100%; left:50%; transform:translateX(-50%); background:rgba(36,54,84,0.9); color:#fff; padding:12px; border-radius:10px; width:220px; box-shadow:0 0 10px #000a; backdrop-filter:blur(8px); z-index:10; }
.mobile-table, .mobile-scroll { overflow-x:auto; white-space:nowrap; }
.mobile-table th, .mobile-table td { padding:4px 10px; font-size:15px; border-bottom:1px solid #243255; }
.mobile-scroll .player-card { display:inline-block; vertical-align:top; }
.stage-label { background:#222b3c88; color:#fff; padding:6px 12px; border-radius:8px; display:inline-block; margin-bottom:8px; }
.red-message { color:#f55!important; }

.section-box{
  background:rgba(255,255,255,0.08);
  border:1px solid rgba(255,255,255,0.15);
  border-radius:14px;
  padding:18px 20px;
  margin:18px 0;
}
.scout-card{
  background:rgba(255,255,255,0.08);
  border:1px solid rgba(255,255,255,0.12);
  border-radius:10px;
  padding:12px 16px;
  margin:12px 0;
  line-height:1.6;
}

/* DataFrame 全般 */
[data-testid="stDataFrame"] div{ color:#fff!important; }
[data-testid="stDataFrame"] table{ background:rgba(255,255,255,0.05)!important; }
[data-testid="stDataFrame"] thead tr{ background:rgba(255,255,255,0.10)!important; }

/* 全体黒文字→白（必要に応じ調整） */
.stMarkdown, .stText, label, p, span, div{ color:#fff!important; }
</style>
""", unsafe_allow_html=True)

st.title("Club Strive")

# ---------- 定数 ----------
SEASON_WEEKS = 14

ABILITY_KEYS = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
ABILITY_FULL = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense',
                'Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

# 国コード（要求された20ヶ国）
NATIONS = ["ENG","GER","FRA","ESP","ITA","NED","BRA","POR","BEL","TUR",
           "ARG","URU","COL","USA","MEX","SAU","NGA","MAR","KOR","AUS"]

POS_ORDER = ["GK","DF","MF","FW"]

# ---------- ユーティリティ ----------
def fmt_money(v:int)->str:
    if v>=1_000_000: return f"{v//1_000_000}m€"
    if v>=1_000:     return f"{v//1_000}k€"
    return f"{v}€"

def normalize_value(v:int)->int:
    if v<1000:
        return int((v//5)*5)
    return int(v//1000*1000)

def sort_by_pos(df:pd.DataFrame, reverse=False)->pd.DataFrame:
    order = {p:i for i,p in enumerate(POS_ORDER)}
    df2 = df.copy()
    df2['__p'] = df2['Pos'].map(order)
    if reverse:
        df2 = df2.sort_values('__p', ascending=False)
    else:
        df2 = df2.sort_values('__p', ascending=True)
    return df2.drop(columns='__p')

def sort_table(df):
    if {'Pts','GF','GA'}.issubset(df.columns):
        df = df.copy()
        df['GD']=df['GF']-df['GA']
        return df.sort_values(['Pts','GD','GF'], ascending=False).reset_index(drop=True)
    return df

def make_highlighter(col_name, target):
    def _hl(row):
        return ['background-color:rgba(247,223,112,0.35); color:#202b41; font-weight:bold;' if row[col_name]==target else '' for _ in row]
    return _hl

def make_transparent(ax):
    ax.patch.set_alpha(0)
    if ax.figure: ax.figure.patch.set_alpha(0)

def radar_chart(values, labels):
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    values = values + values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(3.2,3.2))
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color="#fff", fontsize=9)
    ax.set_yticklabels([])
    ax.grid(color="#fff", alpha=0.2)
    make_transparent(ax)
    return fig

def df_white(df:pd.DataFrame):
    return df.style.set_properties(**{"background-color":"rgba(255,255,255,0.05)","color":"#fff"})

# =========================
# Part 2 / 13  --- 名前プール / プレースタイル・成長タイプ
# =========================

# 各国30パターンずつ（名/姓）、共通予備30
NAME_POOLS = {
    "UNIV": {
        "first": ["Alex","Chris","Jordan","Taylor","Sam","Jamie","Casey","Morgan","Avery","Riley",
                  "Cameron","Quinn","Dakota","Emerson","Skyler","Parker","Rowan","Reese","Hayden","Elliot",
                  "Devin","Finley","Harley","Jules","Kendall","Leslie","Marley","Nico","Phoenix","Robin"],
        "last":  ["Gray","Hunter","Lane","Blake","Reed","Wells","Cross","Frost","Hale","Kerr",
                  "Lynn","Pope","Shaw","Stone","West","York","Vale","Page","Price","Sloan",
                  "Rhodes","Parks","Knox","Hicks","Gates","Flynn","Beck","Boone","Pruitt","Mercer"]
    },
    "ENG": {
        "first":["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
                 "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin",
                 "Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"],
        "last":["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
                "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris",
                "Baker","Moore","Wright","Hill","Cooper","Ward","King","Parker","Campbell","Morris"]
    },
    "GER": {
        "first":["Lukas","Leon","Finn","Jonas","Luis","Paul","Maximilian","Felix","Elias","Noah",
                 "Moritz","Jan","Nico","Tim","Fabian","David","Tom","Philipp","Jannik","Daniel",
                 "Tobias","Florian","Johannes","Simon","Matthias","Benjamin","Sebastian","Erik","Kilian","Milan"],
        "last":["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Hoffmann","Koch",
                "Bauer","Richter","Klein","Wolf","Schröder","Neumann","Schwarz","Zimmermann","Braun","Krüger",
                "Hofmann","Hartmann","Lange","Werner","Schmitt","Krause","Meier","Lehmann","König","Walter"]
    },
    "FRA": {
        "first":["Lucas","Hugo","Louis","Gabriel","Arthur","Jules","Adam","Ethan","Raphaël","Paul",
                 "Thomas","Nathan","Maxime","Baptiste","Noah","Oscar","Matéo","Clément","Sacha","Enzo",
                 "Timéo","Antoine","Alexandre","Valentin","Romain","Julien","Quentin","Victor","Léo","Théo"],
        "last":["Martin","Bernard","Thomas","Petit","Robert","Richard","Durand","Dubois","Moreau","Laurent",
                "Simon","Michel","Lefebvre","Leroy","Roux","David","Bertrand","Morel","Fournier","Girard",
                "Bonnet","Dupont","Lambert","Fontaine","Rousseau","Vincent","Muller","Lefevre","Faure","Mercier"]
    },
    "ESP": {
        "first":["Alejandro","Daniel","Pablo","Álvaro","Javier","Sergio","Carlos","Diego","Hugo","Manuel",
                 "Antonio","Adrián","Jorge","David","Mario","Miguel","Raúl","Fernando","Rafael","Rubén",
                 "Iván","Ángel","Juan","Gonzalo","Luis","Ismael","Óscar","Alfonso","Marco","Lucas"],
        "last":["García","Fernández","González","Rodríguez","López","Martínez","Sánchez","Pérez","Gómez","Martín",
                "Jiménez","Hernández","Ruiz","Díaz","Moreno","Muñoz","Álvarez","Romero","Alonso","Gutiérrez",
                "Navarro","Torres","Domínguez","Vázquez","Ramos","Gil","Ramírez","Serrano","Blanco","Molina"]
    },
    "ITA": {
        "first":["Lorenzo","Francesco","Alessandro","Andrea","Mattia","Gabriele","Riccardo","Tommaso","Leonardo","Giuseppe",
                 "Antonio","Marco","Davide","Federico","Simone","Edoardo","Pietro","Niccolò","Diego","Giovanni",
                 "Cristian","Emanuele","Salvatore","Stefano","Luca","Daniele","Matteo","Raffaele","Filippo","Enrico"],
        "last":["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco",
                "Bruno","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Moretti",
                "Barbieri","Fontana","Santoro","Mariani","Rinaldi","Caruso","Ferraro","Galli","Martini","Leone"]
    },
    "NED": {
        "first":["Daan","Sem","Luuk","Finn","Milan","Bram","Thijs","Jesse","Lars","Ruben",
                 "Thomas","Luca","Niels","Jens","Timo","Joep","Mees","Sven","Tygo","Noah",
                 "Teun","Guus","Kai","Julian","Dex","Boaz","Floris","Gijs","Mats","Wout"],
        "last":["de Jong","Jansen","de Vries","van den Berg","Bakker","van Dijk","Visser","Smit","Meijer","de Boer",
                "Mulder","de Groot","Bos","Vos","Peters","Hendriks","van Leeuwen","Dekker","Brouwer","van der Meer",
                "Dijkstra","van der Linden","Kok","Smits","Schouten","Verhoeven","van der Heijden","Kuiper","Post","Vink"]
    },
    "BRA": {
        "first":["João","Pedro","Gabriel","Lucas","Matheus","Guilherme","Rafael","Felipe","Gustavo","Bruno",
                 "Daniel","Thiago","Diego","Caio","Vitor","Eduardo","André","Rodrigo","Leonardo","Fernando",
                 "Renan","Igor","Luiz","Marcelo","Sergio","Alex","Ruan","Henrique","Luan","Willian"],
        "last":["Silva","Santos","Oliveira","Souza","Pereira","Lima","Carvalho","Gomes","Ribeiro","Almeida",
                "Martins","Rocha","Dias","Barbosa","Correia","Fernandes","Araujo","Costa","Moreira","Cardoso",
                "Teixeira","Freitas","Melo","Castro","Moura","Campos","Jesus","Nunes","da Cruz","Rezende"]
    },
    "POR": {
        "first":["João","Diogo","Rodrigo","Tiago","Miguel","André","Gonçalo","Pedro","Martim","Francisco",
                 "Rafael","Bruno","Henrique","Alexandre","Vasco","Ricardo","Eduardo","Luís","Carlos","Manuel",
                 "Rúben","Hugo","David","Nuno","Filipe","Paulo","Sérgio","Marco","António","Duarte"],
        "last":["Silva","Santos","Ferreira","Pereira","Oliveira","Costa","Rodrigues","Martins","Jesus","Sousa",
                "Fernandes","Gonçalves","Gomes","Lopes","Marques","Alves","Almeida","Ribeiro","Pinto","Carvalho",
                "Teixeira","Moreira","Correia","Moura","Cardoso","Rocha","Dias","Nogueira","Paiva","Azevedo"]
    },
    "BEL": {
        "first":["Noah","Lucas","Louis","Liam","Arthur","Jules","Adam","Victor","Thomas","Ethan",
                 "Gabriel","Nathan","Alex","Benjamin","Enzo","Matteo","Maxime","Hugo","Samuel","Oscar",
                 "Tim","Milan","Baptiste","Quentin","Simon","Mathis","Théo","Elio","Julien","Yanis"],
        "last":["Peeters","Janssens","Maes","Jacobs","Mertens","Willems","Claes","Goossens","Wouters","De Smet",
                "Dubois","Lemaire","Dupont","Lefevre","Lambert","Declercq","De Clercq","Vermeulen","De Vos","Desmet",
                "Pauwels","Aerts","Verhoeven","Hermans","Van Damme","Smet","Segers","Wauters","Roelants","Martens"]
    },
    "TUR": {
        "first":["Mehmet","Mustafa","Ahmet","Ali","Hüseyin","Hasan","İbrahim","Osman","Yusuf","Murat",
                 "Ömer","Ramazan","Fatih","Kadir","Emre","Serkan","Burak","Gökhan","Onur","Halil",
                 "Cem","Kenan","Ercan","Uğur","Ferhat","Volkan","Can","Selim","Barış","Eren"],
        "last":["Yılmaz","Kaya","Demir","Şahin","Çelik","Yıldız","Yıldırım","Öztürk","Aydın","Özdemir",
                "Arslan","Doğan","Kılıç","Aslan","Çetin","Kara","Koç","Kurt","Özkan","Şimşek",
                "Polat","Korkmaz","Eren","Ateş","Aktaş","Güneş","Bal","Avcı","Uçar","Köse"]
    },
    "ARG": {
        "first":["Juan","Santiago","Matías","Nicolás","Agustín","Lucas","Joaquín","Martín","Facundo","Federico",
                 "Franco","Tomás","Gonzalo","Diego","Bruno","Emiliano","Sebastián","Pablo","Ezequiel","Nahuel",
                 "Ramiro","Lautaro","Alejandro","Cristian","Hernán","Leandro","Maximiliano","Iván","Leonel","Gabriel"],
        "last":["González","Rodríguez","Gómez","Fernández","López","Martínez","Díaz","Pérez","Sánchez","Romero",
                "Alvarez","Torres","Ruiz","Ramírez","Flores","Acosta","Benítez","Medina","Suárez","Castro",
                "Ortiz","Vázquez","Molina","Ibarra","Sosa","Moreno","Rivas","Godoy","Cabrera","Ferreyra"]
    },
    "URU": {
        "first":["Juan","Diego","Nicolás","Santiago","Agustín","Matías","Bruno","Federico","Gonzalo","Pablo",
                 "Lucas","Martín","Emiliano","Rodrigo","Franco","Sebastián","Facundo","Maximiliano","Cristian","Jonathan",
                 "Leandro","Kevin","Nahuel","Lautaro","Felipe","Alejandro","Gastón","Hernán","Mauricio","Tomás"],
        "last":["Pérez","González","Rodríguez","Fernández","López","Martínez","Sánchez","Díaz","Silva","Morales",
                "Suárez","Ramos","Castro","Vega","Méndez","Romero","Cabrera","Acosta","Núñez","Ortiz",
                "Rojas","Farias","Torres","Cardozo","Perdomo","Borges","Cruz","Machado","Molina","Reyes"]
    },
    "COL": {
        "first":["Juan","Carlos","Andrés","Luis","Jorge","Alejandro","Diego","Sergio","Camilo","Felipe",
                 "Daniel","Miguel","Cristian","Oscar","Wilson","Ricardo","Fernando","David","Pedro","Rafael",
                 "Hernán","Edwin","Jaime","Victor","Mauricio","Gustavo","Esteban","Mateo","Sebastián","Iván"],
        "last":["García","Rodríguez","Martínez","López","González","Hernández","Pérez","Sánchez","Ramírez","Torres",
                "Flores","Gómez","Ruiz","Moreno","Vargas","Castro","Jiménez","Rojas","Navarro","Mendoza",
                "Romero","Acosta","Ortega","Cortés","Guerrero","Cárdenas","Salazar","Velásquez","Mejía","Pineda"]
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
        "first":["José","Juan","Luis","Carlos","Jorge","Miguel","Jesús","Francisco","Fernando","Alejandro",
                 "Ricardo","Eduardo","Sergio","Rafael","Manuel","David","Pedro","Arturo","Hugo","Ruben",
                 "Diego","Ramon","Rodolfo","Cristian","Mauricio","Hector","Alfredo","Antonio","Ernesto","Pablo"],
        "last":["Hernández","García","Martínez","López","González","Pérez","Rodríguez","Sánchez","Ramírez","Cruz",
                "Flores","Gómez","Ruiz","Díaz","Reyes","Torres","Morales","Ortiz","Gutierrez","Chávez",
                "Ramos","Vargas","Castillo","Juárez","Mendoza","Navarro","Álvarez","Delgado","Romero","Herrera"]
    },
    "SAU": {
        "first":["Mohammed","Ahmed","Ali","Omar","Abdullah","Hassan","Khalid","Fahad","Saud","Sultan",
                 "Nasser","Yousef","Ibrahim","Abdulaziz","Majed","Turki","Saleh","Faisal","Talal","Rayan",
                 "Marwan","Waleed","Anas","Hamad","Mansour","Bader","Rashed","Saeed","Ziyad","Khalaf"],
        "last":["Al-Saud","Al-Harbi","Al-Qahtani","Al-Shahrani","Al-Ghamdi","Al-Mutairi","Al-Otaibi","Al-Zahrani","Al-Dosari","Al-Subaie",
                "Al-Johani","Al-Rashid","Al-Marri","Al-Ajmi","Al-Harthy","Al-Amri","Al-Shehri","Al-Tamimi","Al-Najjar","Al-Bishi",
                "Al-Jabri","Al-Salim","Al-Balawi","Al-Anazi","Al-Faraj","Al-Salim","Al-Hassan","Al-Yami","Al-Suwailem","Al-Fadhli"]
    },
    "NGA": {
        "first":["Emeka","Chinedu","Ifeanyi","Oluwaseun","Ayodele","Tunde","Segun","Chukwuemeka","Kunle","Babatunde",
                 "Femi","Sola","Nonso","Ibrahim","Abdul","Collins","Samuel","Joseph","Peter","Chisom",
                 "Uche","Henry","Ebuka","Kingsley","Sunday","Bright","Victor","Kelvin","Godwin","Stephen"],
        "last":["Okafor","Okeke","Okoro","Adegoke","Adebayo","Balogun","Ogunyemi","Eze","Ojo","Abdullahi",
                "Ibrahim","Mohammed","Olawale","Olowo","Adesanya","Nwankwo","Ogbu","Nwachukwu","Owolabi","Onyeka",
                "Opara","Okon","Ofori","Bello","Ogunleye","Ogunlade","Damilola","Olawale","Obinna","Ogunyinka"]
    },
    "MAR": {
        "first":["Youssef","Mohamed","Ayoub","Hamza","Anass","Mehdi","Yassine","Reda","Othmane","Soufiane",
                 "Ismail","Amine","Karim","Hassan","Khalid","Abdelaziz","Ilyas","Achraf","Nabil","Rachid",
                 "Walid","Adil","Fouad","Said","Tarik","Ibrahim","Hicham","Aziz","Bilal","Imad"],
        "last":["El Amrani","Benali","Bennani","El Idrissi","El Ghazali","El Fassi","Bouazza","Bouzid","El Bahri","El Arbi",
                "El Haddad","Benkirane","Berrada","El Mansouri","El Khattabi","Bennouna","El Morabet","El Farissi","El Azizi","Bouras",
                "Choukri","El Khatib","Bouziane","El Hachmi","Benchekroun","El Hamdi","El Omari","Moujahid","Benhaddou","Bouhaddou"]
    },
    "KOR": {
        "first":["Min-jun","Seo-jun","Do-hyun","Ji-ho","Ha-joon","Joon-woo","Ji-hoon","Ye-jun","Hyun-woo","Jae-won",
                 "Seung-min","Tae-hyun","Jin-woo","Sung-min","Hyeon-seo","Dong-hyun","Woo-jin","Seung-ho","Ji-hu","Yun-seo",
                 "Chan-woo","Jun-seo","Hyun-seok","Gun-woo","Min-seok","Sang-ho","Young-ho","Jin-seok","Sung-hoon","Dong-woo"],
        "last":["Kim","Lee","Park","Choi","Jung","Kang","Cho","Yoon","Jang","Lim",
                "Han","Shin","Seo","Kwon","Hwang","Ahn","Song","Yu","Hong","Jeon",
                "Go","Moon","Bae","Baek","Yang","Nam","Oh","Joo","Ryu","Ha"]
    },
    "AUS": {
        "first":["Oliver","William","Jack","Noah","Henry","Charlie","Thomas","James","Lucas","Leo",
                 "Alexander","Harrison","Mason","Ethan","Liam","Oscar","Logan","Hunter","Connor","Isaac",
                 "Sebastian","Cooper","Benjamin","Archer","Levi","Harvey","Nate","Hudson","Flynn","Jasper"],
        "last":["Smith","Jones","Williams","Brown","Taylor","Johnson","White","Martin","Anderson","Thompson",
                "Nguyen","Harris","Lewis","Walker","Hall","Young","King","Wright","Turner","Scott",
                "Cooper","Ward","Morris","Hill","Clark","Baker","Adams","Mitchell","Campbell","Roberts"]
    }
}

# プレースタイル（複数所持可・国特色は生成時に重み付けする想定）
PLAY_STYLES = [
    "チーム至上主義","職人","頭脳派","感情型","爆発型","ムードメーカー","師弟型",
    "セカンドストライカー","クロスハンター","インナーラップSB","タックルマスター",
    "フリーキック職人","チャンスメイカー","シャドーストライカー","司令塔","ドリブラー",
    "空中戦の鬼","ジョーカー","起点型GK","起点CB","スイーパーリーダー","影の支配者",
    "ディストラクター","スーパーリーダー","パワーヘッダー","ロングスロワー","ポーチャー","ボールウィナー","レジスタ","ラインブレーカー"
]

# 成長タイプ（非表示要求なので内部のみ）
GROWTH_TYPES = ["超晩成","晩成","普通","遅咲き","停滞","下降"]

# =========================
# Part 3 / 13  --- 生成系・オファー系・補強判定など 共通関数(2)
# =========================

def pick_name(nation:str, used:set)->str:
    pool = NAME_POOLS.get(nation, NAME_POOLS["UNIV"])
    first = random.choice(pool["first"])
    last  = random.choice(pool["last"])
    name = f"{first} {last}"
    if name in used:
        # 予備プールで重複回避
        for _ in range(10):
            first = random.choice(pool["first"])
            last  = random.choice(pool["last"])
            name  = f"{first} {last}"
            if name not in used: break
        else:
            # ユニバーサルから
            first = random.choice(NAME_POOLS["UNIV"]["first"])
            last  = random.choice(NAME_POOLS["UNIV"]["last"])
            name  = f"{first} {last}"
    used.add(name)
    return name

def choose_playstyles(nation:str, k:int=2)->str:
    # 国ごと特色: 例として簡易重み（必要に応じ調整）
    nat_bias = {
        "BRA":["ドリブラー","チャンスメイカー","ムードメーカー","ジョーカー"],
        "ENG":["タックルマスター","フリーキック職人","ポーチャー","ラインブレーカー"],
        "GER":["頭脳派","司令塔","レジスタ","スーパーリーダー"],
        "ESP":["シャドーストライカー","セカンドストライカー","チャンスメイカー","レジスタ"],
        "ITA":["ディストラクター","インナーラップSB","影の支配者","レジスタ"],
        "NED":["チーム至上主義","レジスタ","チャンスメイカー","ラインブレーカー"],
        "ARG":["ムードメーカー","ジョーカー","パワーヘッダー","ポーチャー"],
        "URU":["ムードメーカー","ポーチャー","タックルマスター"],
        "COL":["ドリブラー","クロスハンター","チャンスメイカー"],
        "USA":["パワーヘッダー","職人","爆発型"],
        "MEX":["クロスハンター","ドリブラー","ジョーカー"],
        "SAU":["空中戦の鬼","影の支配者","職人"],
        "NGA":["爆発型","空中戦の鬼","ジョーカー"],
        "MAR":["ドリブラー","タックルマスター","職人"],
        "KOR":["チーム至上主義","頭脳派","司令塔"],
        "AUS":["パワーヘッダー","チーム至上主義","職人"],
        "POR":["フリーキック職人","チャンスメイカー","セカンドストライカー"],
        "BEL":["司令塔","チーム至上主義","チャンスメイカー"],
        "TUR":["爆発型","感情型","タックルマスター"],
        "FRA":["シャドーストライカー","チャンスメイカー","ムードメーカー"]
    }
    bias = nat_bias.get(nation, [])
    candidates = PLAY_STYLES.copy()
    random.shuffle(candidates)
    styles = set()
    # まずバイアスから
    for s in bias:
        if len(styles)>=k: break
        if random.random()<0.6:
            styles.add(s)
    # 足りなければランダム補充
    for s in candidates:
        if len(styles)>=k: break
        styles.add(s)
    return " / ".join(list(styles))

def choose_growth()->str:
    return random.choices(GROWTH_TYPES, weights=[5,10,35,20,20,10], k=1)[0]

def gen_player(nation:str, youth:bool, club:str="Free")->dict:
    used = gen_player.used_names.setdefault(nation, set())
    name = pick_name(nation, used)
    stats = {k: random.randint(52 if youth else 60, 82 if youth else 90) for k in ABILITY_KEYS}
    ovr   = int(np.mean(list(stats.values())))
    val   = normalize_value(ovr*ovr*50 + random.randint(-2000,2000))
    ps    = choose_playstyles(nation, k=random.randint(1,2))
    gt    = choose_growth()
    return {
        "Name":name, "Nat":nation, "Pos":random.choice(POS_ORDER),
        "Age": random.randint(15 if youth else 19, 18 if youth else 34),
        **stats, "OVR":ovr,
        "Matches_Played":0, "Goals":0, "Assists":0, "IntlApps":0,
        "Fatigue":0, "Injured":False, "Status":"通常",
        "Salary": normalize_value(random.randint(30_000 if youth else 120_000, 250_000 if youth else 1_200_000)),
        "Contract": random.randint(1,2 if youth else 3),
        "Value": val,
        "PlayStyle": ps,
        "Growth": gt,
        "Club": club,
        "RentalFrom":None,"RentalUntil":None,"OptionFee":None
    }
gen_player.used_names = {}

def gen_players(n:int, youth:bool, nation_list=None, club:str="Free")->pd.DataFrame:
    if nation_list is None: nation_list = NATIONS
    lst = [gen_player(random.choice(nation_list), youth, club) for _ in range(n)]
    return pd.DataFrame(lst)

def gen_scout_candidates(n:int, youth:bool)->pd.DataFrame:
    # AI選手群から抜粋＋新規生成を混ぜる
    pool = []
    # まずAIから
    if not ses.ai_players.empty:
        cand = ses.ai_players[ses.ai_players['Age']<=18] if youth else ses.ai_players[ses.ai_players['Age']>=19]
        cand = cand.sample(min(len(cand), n//2)) if len(cand)>0 else pd.DataFrame()
        pool.append(cand)
    # 新規生成
    remain = n - (0 if not pool else len(pool[0]))
    if remain>0:
        pool.append(gen_players(remain, youth))
    df = pd.concat(pool) if pool else gen_players(n, youth)
    # 評価額調整
    df['Value'] = df['Value'].apply(normalize_value)
    df.reset_index(drop=True, inplace=True)
    return df

def suggest_positions(df:pd.DataFrame)->list:
    ideal = {"GK":3,"DF":8,"MF":8,"FW":5}
    cnt = df['Pos'].value_counts().to_dict()
    need=[]
    for p, num in ideal.items():
        if cnt.get(p,0) < num:
            need.append(p)
    return need

# ------ オファー判定 ------
def offer_result(row, wage_offer, years, fee_offer, budget, policy="balanced"):
    want_wage = int(row['OVR']*180 + random.randint(-5000,5000))
    want_fee  = int(row['Value']*0.9)
    ok = (wage_offer>=want_wage) and (fee_offer>=want_fee) and (budget>=fee_offer)
    return ok, want_wage, want_fee

def rental_result(row, weeks, fee_offer, budget, policy="balanced"):
    demand = int(row['Value']*0.12 + weeks*500)  # 簡易
    ok = (fee_offer>=demand) and (budget>=fee_offer)
    return ok, demand

# ------ レンタル期限処理 ------
def handle_rental_expirations():
    wk = ses.week
    for dfname in ['senior','youth']:
        df = getattr(ses, dfname)
        mask = df['RentalUntil'].notna() & (df['RentalUntil']<=wk)
        if mask.any():
            back = df[mask].copy()
            for _, r in back.iterrows():
                # 買取選択？
                if r['OptionFee'] and r['OptionFee']>0 and ses.budget>=r['OptionFee']:
                    # ここでは自動買取しない。SNS報告のみ。
                    ses.sns_posts.append(f"買取オプション満了：{r['Name']} の去就を決める必要があります。")
                    ses.sns_times.append(datetime.now())
                # 元クラブへ返却
                if r['RentalFrom']:
                    r2 = r.copy()
                    r2['Club'] = r['RentalFrom']
                    r2['Status']="通常"
                    r2[['RentalFrom','RentalUntil','OptionFee']] = [None,None,None]
                    ses.ai_players = pd.concat([ses.ai_players, pd.DataFrame([r2])], ignore_index=True)
            setattr(ses, dfname, df[~mask])
    housekeeping()

# ------ 決算ログ追加 ------
def add_finance(week:int, ticket:int, goods:int, salary:int):
    ses.finance_log.append({
        "week":week,
        "revenue_ticket":ticket,
        "revenue_goods":goods,
        "expense_salary":salary
    })

# ------ マッチログ追加 ------
def add_match_log(week:int, club_a:str, club_b:str, g1:int, g2:int, shooters:list, assisters:list):
    ses.match_log.append({
        "week":week,
        "home":club_a,
        "away":club_b,
        "g1":g1,"g2":g2,
        "shooters":shooters,
        "assisters":assisters
    })

# ------ その他メンテ ------
def housekeeping():
    # スカウト推奨更新（簡易）
    ses.need_positions = suggest_positions(ses.senior)

# =========================
# Part 4 / 13  --- リーグ生成 / スタンディング生成 / セッション初期化
# =========================
from types import SimpleNamespace

ADJ = ["Sterling","Golden","Shadow","Crimson","Ivory","Apex","Royal","Urban",
       "Mighty","Unity","Rapid","Valiant","Storm","Eagle","Phoenix","Velvet",
       "Copper","Silver","Emerald","Obsidian","Scarlet","Azure","Ivory","Iron"]
NOUN = ["Hearts","Dynamos","Rovers","Wolves","Falcons","Knights","Stars","Rangers",
        "United","Town","City","Giants","Queens","Kings","Storm","Comets","Titans",
        "Voyagers","Pilots","Bulls","Suns","Wizards","Sharks","Jets","Dragons"]

def gen_club_names(n, used):
    names=[]
    while len(names)<n:
        nm = f"{random.choice(ADJ)} {random.choice(NOUN)}"
        if nm not in used:
            used.add(nm); names.append(nm)
    return names

def build_leagues(my_club:str):
    leagues = {}
    used=set([my_club])
    for nat in NATIONS:
        if nat=="ITA":
            leagues[nat]={"D1":gen_club_names(10,used),"D2":gen_club_names(10,used)}
        else:
            leagues[nat]={"D1":gen_club_names(10,used)}
    # ENG D1 先頭に自クラブ
    if my_club not in leagues["ENG"]["D1"]:
        leagues["ENG"]["D1"][0] = my_club
    else:
        # 既に入っていたときは先頭へ
        lst = leagues["ENG"]["D1"]
        lst.insert(0, lst.pop(lst.index(my_club)))
        leagues["ENG"]["D1"] = lst
    return leagues

def build_standings(leagues:dict)->pd.DataFrame:
    rows=[]
    for nat, divs in leagues.items():
        for div, clubs in divs.items():
            for c in clubs:
                rows.append({"Nation":nat,"Division":div,"Club":c,
                             "W":0,"D":0,"L":0,"GF":0,"GA":0,"Pts":0})
    return pd.DataFrame(rows)

def build_club_map(df:pd.DataFrame):
    return {r.Club:(r.Nation,r.Division) for r in df.itertuples()}

def init_session():
    ses = SimpleNamespace()
    ses.my_club = "Signature Team"  # デフォルト名
    ses.leagues   = build_leagues(ses.my_club)
    ses.standings = build_standings(ses.leagues)
    ses.club_map  = build_club_map(ses.standings)

    # 自クラブ選手
    ses.senior = gen_players(30, youth=False, nation_list=NATIONS, club=ses.my_club)
    ses.youth  = gen_players(20, youth=True,  nation_list=NATIONS, club=ses.my_club)

    # AIクラブ全体の選手
    ai_list=[]
    for club,(nat,div) in ses.club_map.items():
        if club==ses.my_club: continue
        ai_list.append(gen_players(26, youth=False, nation_list=[nat], club=club))
    ses.ai_players = pd.concat(ai_list, ignore_index=True) if ai_list else pd.DataFrame()

    ses.week = 1
    ses.budget = 5_000_000
    ses.need_positions = suggest_positions(ses.senior)
    ses.scout_candidates = pd.DataFrame()
    ses.scout_type = "Senior"
    ses.rental_pending = []
    ses.player_history = {}
    ses.finance_log = []
    ses.match_log = []
    ses.sns_posts = []
    ses.sns_times = []
    ses.intl_tournament = {}   # {'clubs':[],'results':[],'finished':bool}
    ses.intl_player_stats = {} # name:{G: ,A: ,Club:,Pos:}
    ses.auto_selected = False
    ses.starters = []
    return ses

# st.session_state に格納
if "ses" not in st.session_state:
    st.session_state.ses = init_session()
ses = st.session_state.ses

# =========================
# Part 5 / 13  --- 成長/履歴・順位更新・国際大会・シーズンリセット
# =========================

def apply_growth(df:pd.DataFrame, week:int)->pd.DataFrame:
    df = df.copy()
    for i,r in df.iterrows():
        g = r.get("Growth","普通")
        delta = 0
        if g=="超晩成" and week>SEASON_WEEKS//2 and random.random()<0.35: delta=random.randint(2,4)
        elif g=="晩成"  and week>SEASON_WEEKS//2 and random.random()<0.25: delta=random.randint(1,3)
        elif g=="遅咲き" and week>SEASON_WEEKS//3 and random.random()<0.2:  delta=random.randint(1,2)
        elif g=="停滞":  delta=random.choice([0,0,1,-1])
        elif g=="下降":  delta=random.choice([-2,-1,0])
        else:             delta=random.choice([0,0,1])

        if delta!=0:
            for k in ABILITY_KEYS:
                df.at[i,k] = int(np.clip(df.at[i,k]+delta//2, 1, 99))
            df.at[i,'OVR'] = int(np.clip(df.at[i,'OVR']+delta, 1, 99))
    return df

def update_player_history(name, row, week):
    ses.player_history.setdefault(name, []).append(
        {"week":week,"OVR":row["OVR"], **{k:row[k] for k in ABILITY_KEYS}}
    )

def update_standings(home, away, gh, ga):
    df = ses.standings
    if gh>ga:
        df.loc[df.Club==home,["W","Pts"]]+= [1,3]
        df.loc[df.Club==away,"L"]+=1
    elif gh<ga:
        df.loc[df.Club==away,["W","Pts"]]+= [1,3]
        df.loc[df.Club==home,"L"]+=1
    else:
        df.loc[df.Club.isin([home,away]),"D"]+=1
        df.loc[df.Club.isin([home,away]),"Pts"]+=1
    df.loc[df.Club==home,["GF","GA"]]+= [gh,ga]
    df.loc[df.Club==away,["GF","GA"]]+= [ga,gh]
    ses.standings = sort_table(df)

def auto_intl_round():
    # 初回セット
    if not ses.intl_tournament:
        # 各国D1上位2クラブ
        clubs=[]
        for nat,divs in ses.leagues.items():
            if "D1" in divs:
                tmp = ses.standings[(ses.standings.Nation==nat)&(ses.standings.Division=="D1")]
                top2 = tmp.sort_values(["Pts","GF"], ascending=False).head(2)["Club"].tolist()
                clubs.extend(top2)
        random.shuffle(clubs)
        ses.intl_tournament={"clubs":clubs,"results":[],"finished":False}
        return

    if ses.intl_tournament.get("finished"): return
    clubs = ses.intl_tournament["clubs"]
    if len(clubs)<=1:
        ses.intl_tournament["finished"]=True
        return

    winners=[]
    for i in range(0,len(clubs)-1,2):
        c1,c2 = clubs[i], clubs[i+1]
        g1,g2 = random.randint(0,4), random.randint(0,4)
        pk_txt=""
        if g1==g2:
            p1,p2 = random.randint(3,6), random.randint(3,6)
            while p1==p2:
                p1,p2 = random.randint(3,6), random.randint(3,6)
            pk_txt=f"PK {p1}-{p2}"
            win = c1 if p1>p2 else c2
        else:
            win = c1 if g1>g2 else c2

        ses.intl_tournament["results"].append((c1,g1,c2,g2,pk_txt,win))

        # SNS
        ses.sns_posts.append(f"[国際大会] {c1} {g1}-{g2} {c2} {pk_txt} → 勝者:{win}")
        ses.sns_times.append(datetime.now())

        # 個人成績簡易付与
        pool_all = pd.concat([ses.senior, ses.youth, ses.ai_players], ignore_index=True)
        XI1 = pool_all[pool_all["Club"]==c1].nlargest(11,"OVR")
        XI2 = pool_all[pool_all["Club"]==c2].nlargest(11,"OVR")
        for club, goals in [(c1,g1),(c2,g2)]:
            XI = XI1 if club==c1 else XI2
            for _ in range(goals):
                if XI.empty: break
                sid = XI.sample(1).iloc[0]
                aid = XI.sample(1).iloc[0]
                ses.intl_player_stats.setdefault(sid["Name"],{"G":0,"A":0,"Club":club,"Pos":sid["Pos"]})
                ses.intl_player_stats.setdefault(aid["Name"],{"G":0,"A":0,"Club":club,"Pos":aid["Pos"]})
                ses.intl_player_stats[sid["Name"]]["G"] += 1
                ses.intl_player_stats[aid["Name"]]["A"] += 1

        winners.append(win)
    if len(clubs)%2==1:
        winners.append(clubs[-1])
    ses.intl_tournament["clubs"]=winners
    if len(winners)==1:
        ses.intl_tournament["finished"]=True
        ses.sns_posts.append(f"[国際大会] 優勝: {winners[0]}")
        ses.sns_times.append(datetime.now())

def reset_season():
    # 順位表リセット
    ses.standings = build_standings(ses.leagues)
    # 成績初期化
    for dfname in ["senior","youth","ai_players"]:
        df = getattr(ses, dfname)
        for col in ["Matches_Played","Goals","Assists","IntlApps","Fatigue"]:
            if col in df.columns: df[col]=0
        df["Status"]="通常"
        df[["RentalFrom","RentalUntil","OptionFee"]] = [None,None,None]
        setattr(ses, dfname, df)
    ses.week = 1
    ses.finance_log.clear()
    ses.match_log.clear()
    ses.player_history.clear()
    ses.intl_tournament.clear()
    ses.intl_player_stats.clear()
    ses.sns_posts.clear(); ses.sns_times.clear()
    ses.rental_pending.clear()
    ses.auto_selected=False
    ses.starters=[]
    housekeeping()

# =========================
# Part 6 / 13  --- タブ定義 / シニア / ユース / 選手詳細
# =========================

tabs = st.tabs([
    "シニア","ユース","選手詳細","試合","順位表",
    "スカウト/移籍","レンタル管理","SNS","財務レポート",
    "年間表彰","国際大会","クラブ設定"
])

# ---------- 0) シニア ----------
with tabs[0]:
    st.markdown('<div class="section-box"><h3>シニア選手一覧</h3></div>', unsafe_allow_html=True)
    handle_rental_expirations()

    order_mode = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="order_senior")
    reverse_flag = (order_mode == "FW→MF→DF→GK")

    df_s = ses.senior[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Goals','Assists','Status']]
    df_s = sort_by_pos(df_s, reverse=reverse_flag)
    st.dataframe(
        df_white(df_s).apply(make_highlighter('Status', "レンタル中"), axis=1),
        use_container_width=True
    )

# ---------- 1) ユース ----------
with tabs[1]:
    st.markdown('<div class="section-box"><h3>ユース選手一覧</h3></div>', unsafe_allow_html=True)

    order_mode_y = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="order_youth")
    reverse_flag_y = (order_mode_y == "FW→MF→DF→GK")

    df_y = ses.youth[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Goals','Assists','Status']]
    df_y = sort_by_pos(df_y, reverse=reverse_flag_y)
    st.dataframe(
        df_white(df_y).apply(make_highlighter('Status', "レンタル中"), axis=1),
        use_container_width=True
    )

# ---------- 2) 選手詳細 ----------
with tabs[2]:
    st.markdown('<div class="section-box"><h3>選手詳細</h3></div>', unsafe_allow_html=True)
    pool = pd.concat([ses.senior, ses.youth], ignore_index=True)
    if pool.empty:
        st.markdown("<div class='tab-info'>表示できる選手がいません。</div>", unsafe_allow_html=True)
    else:
        sel_name = st.selectbox("選手選択", pool['Name'].tolist())
        row = pool[pool['Name']==sel_name].iloc[0]

        st.write(f"ポジション: {row['Pos']} / OVR:{row['OVR']} / 年齢:{row['Age']}")
        st.write(f"国籍: {row['Nat']} / 国際大会出場: {row.get('IntlApps',0)}回")
        st.write(f"所属: {row['Club']} / 状態: {row.get('Status','')}")
        st.write(f"プレースタイル: {row['PlayStyle']}")

        vals = [row[k] for k in ABILITY_KEYS]
        fig_r = radar_chart(vals, ABILITY_KEYS)
        st.pyplot(fig_r)

        hist_df = pd.DataFrame(ses.player_history.get(
            sel_name, [{'week':0,'OVR':row['OVR'], **{k:row[k] for k in ABILITY_KEYS}}]
        ))
        if len(hist_df)>1:
            fig1, ax1 = plt.subplots()
            for k in ABILITY_KEYS:
                ax1.plot(hist_df['week'], hist_df[k], marker='o', label=k)
            ax1.set_xlabel("節"); ax1.set_ylabel("能力")
            ax1.legend(frameon=False, bbox_to_anchor=(1,1))
            make_transparent(ax1)
            st.pyplot(fig1)

            fig2, ax2 = plt.subplots()
            ax2.plot(hist_df['week'], hist_df['OVR'], marker='o')
            ax2.set_xlabel("節"); ax2.set_ylabel("総合値")
            make_transparent(ax2)
            st.pyplot(fig2)
        else:
            st.markdown("<div class='tab-info'>成長データはまだありません。</div>", unsafe_allow_html=True)

# =========================
# Part 7 / 13  --- 試合 / 順位表（各国ランキング統合）
# =========================

# ---------- 3) 試合 ----------
with tabs[3]:
    st.markdown(f'<div class="section-box"><h3>第 {ses.week} 節　試合シミュレーション</h3></div>', unsafe_allow_html=True)

    formation = st.selectbox("フォーメーション", ["4-4-2","4-3-3","3-5-2"], key="formation_sel")

    if st.button("オート先発選考", key="auto_xi"):
        req = {
            "4-4-2":("FW",2,"MF",4,"DF",4,"GK",1),
            "4-3-3":("FW",3,"MF",3,"DF",4,"GK",1),
            "3-5-2":("FW",2,"MF",5,"DF",3,"GK",1)
        }[formation]
        starters=[]
        for i in range(0,len(req),2):
            p,cnt=req[i],req[i+1]
            starters += ses.senior[ses.senior["Pos"]==p].nlargest(cnt,"OVR")["Name"].tolist()
        ses.starters = starters
        ses.auto_selected = True

    if ses.starters:
        st.markdown('<div class="section-box"><h4>先発メンバー</h4></div>', unsafe_allow_html=True)
        s_df = ses.senior[ses.senior["Name"].isin(ses.starters)][['Name','Pos','OVR','Goals','Assists','PlayStyle']]
        s_df = sort_by_pos(s_df)
        st.dataframe(df_white(s_df), use_container_width=True)
    else:
        st.warning("『オート先発選考』を行わないと試合開始できません。")

    # 対戦相手選択（同リーグ内から）
    my_nat, my_div = ses.club_map[ses.my_club]
    same_league = ses.standings[(ses.standings.Nation==my_nat)&(ses.standings.Division==my_div)]
    opp_candidates = [c for c in same_league.Club if c!=ses.my_club]
    opponent = random.choice(opp_candidates) if opp_candidates else ses.my_club

    kickoff = st.button("キックオフ", disabled=(not ses.auto_selected or ses.week>SEASON_WEEKS))

    if kickoff:
        # 自クラブ攻撃力
        atk = ses.senior[ses.senior["Name"].isin(ses.starters)]["OVR"].mean() if ses.starters else 70
        # 相手攻撃力（簡易）
        opp_pool = ses.ai_players[ses.ai_players["Club"]==opponent]
        oppatk   = opp_pool["OVR"].mean() if not opp_pool.empty else random.uniform(60,90)

        gf = max(0, int(np.random.normal((atk-60)/8, 1)))
        ga = max(0, int(np.random.normal((oppatk-60)/8, 1)))

        shots = random.randint(6,15)
        on_t  = random.randint(max(0,shots-7), shots)
        poss  = random.randint(40,60)

        # ゴール&アシスト記録
        scorers=[]; assisters=[]
        if gf>0 and ses.starters:
            for _ in range(gf):
                s = random.choice(ses.starters)
                cand = [x for x in ses.starters if x!=s]
                a = random.choice(cand) if cand else s
                scorers.append(s); assisters.append(a)
                ses.senior.loc[ses.senior["Name"]==s,"Goals"] += 1
                ses.senior.loc[ses.senior["Name"]==a,"Assists"] += 1

        update_standings(ses.my_club, opponent, gf, ga)

        # その他クラブ試合
        done_pairs={(ses.my_club,opponent)}
        for nat, divs in ses.leagues.items():
            for div, clubs in divs.items():
                c_list = clubs[:]
                random.shuffle(c_list)
                for i in range(0,len(c_list),2):
                    if i+1>=len(c_list): break
                    h,a = c_list[i], c_list[i+1]
                    if (h,a) in done_pairs or (a,h) in done_pairs: continue
                    g1,g2 = random.randint(0,3), random.randint(0,3)
                    update_standings(h,a,g1,g2)
                    done_pairs.add((h,a))

        # ログ・SNS・財務
        add_match_log(ses.week, ses.my_club, opponent, gf, ga, scorers, assisters)
        ses.sns_posts.append(f"{ses.my_club} {gf}-{ga} {opponent}｜得点:{', '.join(scorers) if scorers else 'なし'} / アシスト:{', '.join(assisters) if assisters else 'なし'}")
        ses.sns_times.append(datetime.now())

        add_finance(ses.week,
                    ticket = gf*15000 + random.randint(5000,10000),
                    goods  = ga*8000  + random.randint(2000,6000),
                    salary = int(ses.senior["OVR"].mean()*1000))

        # 成長
        ses.senior = apply_growth(ses.senior, ses.week)
        for _,rw in ses.senior.iterrows():
            update_player_history(rw["Name"], rw, ses.week)

        # 表示
        st.success(f"結果：{gf}-{ga}")
        if scorers:   st.write("得点者: " + " / ".join(scorers))
        if assisters: st.write("アシスト: " + " / ".join(assisters))
        st.write(f"シュート: {shots}（枠内:{on_t}） / ポゼッション:{poss}%")

        ses.week += 1
        ses.auto_selected = False

        # 国際大会進行
        auto_intl_round()

        if ses.week > SEASON_WEEKS:
            st.success("シーズン終了！自動で新シーズンを開始します。")
            reset_season()
            st.experimental_rerun()

    elif ses.week > SEASON_WEEKS:
        st.info("シーズン終了済みです。自動で次シーズンが開始されています。")


# ---------- 4) 順位表（単体 + 各国ランキング統合） ----------
with tabs[4]:
    st.markdown('<div class="section-box"><h3>順位表（単一表示）</h3></div>', unsafe_allow_html=True)

    nat_sel = st.selectbox("国を選択", list(ses.leagues.keys()), key="nat_sel_table")
    div_sel = st.selectbox("ディビジョンを選択", list(ses.leagues[nat_sel].keys()), key="div_sel_table")
    df_cur = ses.standings[(ses.standings.Nation==nat_sel)&(ses.standings.Division==div_sel)]
    df_cur = sort_table(df_cur)
    st.dataframe(df_white(df_cur).apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)

    st.markdown('<div class="section-box"><h3>各国リーグランキング（順位表・得点王・アシスト王・ベスト11）</h3></div>', unsafe_allow_html=True)

    # 全選手（AI含む）
    df_all = pd.concat([ses.senior, ses.youth, ses.ai_players], ignore_index=True)
    for col in ['Goals','Assists']:
        if col not in df_all: df_all[col]=0
    df_all['Nation']   = df_all['Club'].map(lambda c: ses.club_map.get(c,("",""))[0] if c in ses.club_map else "")
    df_all['Division'] = df_all['Club'].map(lambda c: ses.club_map.get(c,("",""))[1] if c in ses.club_map else "")

    for nat, divs in ses.leagues.items():
        st.markdown(f"### {nat}")
        for d in divs.keys():
            st.markdown(f"#### {d} 順位表")
            df_st = ses.standings[(ses.standings.Nation==nat)&(ses.standings.Division==d)]
            df_st = sort_table(df_st)
            st.dataframe(df_white(df_st).apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)

            sub = df_all[(df_all['Nation']==nat)&(df_all['Division']==d)]
            if sub.empty:
                st.markdown("<div class='tab-info'>選手データなし</div>", unsafe_allow_html=True)
                st.markdown("---")
                continue

            top_g = sub.nlargest(5,'Goals')[['Name','Pos','Goals','Club']]
            top_a = sub.nlargest(5,'Assists')[['Name','Pos','Assists','Club']]

            st.markdown("**🏅 得点王 TOP5**")
            st.dataframe(df_white(top_g).apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)

            st.markdown("**🎯 アシスト王 TOP5**")
            st.dataframe(df_white(top_a).apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)

            best11=[]
            for p,need in [('GK',1),('DF',4),('MF',4),('FW',2)]:
                cand = sub[sub['Pos']==p].nlargest(need,'OVR')[['Name','Pos','OVR','Club']]
                best11.append(cand)
            best11 = pd.concat(best11)
            st.markdown("**⚽️ ベストイレブン**")
            st.dataframe(df_white(best11).apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)
            st.markdown("---")

# =========================
# Part 8 / 13  --- スカウト / 移籍
# =========================
with tabs[5]:
    st.markdown('<div class="section-box"><h3>スカウト / 移籍 / 補強</h3></div>', unsafe_allow_html=True)

    cat = st.radio("対象カテゴリー", ["シニア候補","ユース候補"], horizontal=True, key="scout_cat")
    youth_flag = (cat=="ユース候補")

    # 補強推奨
    base_df = ses.youth if youth_flag else ses.senior
    ses.need_positions = suggest_positions(base_df)
    st.markdown(f"**補強推奨ポジション:** {', '.join(ses.need_positions) if ses.need_positions else 'バランスOK'}")

    c1,c2 = st.columns(2)
    with c1:
        if st.button("候補リスト更新", key="refresh_scout"):
            ses.scout_candidates = gen_scout_candidates(10, youth_flag)
    with c2:
        st.write(f"予算：{fmt_money(ses.budget)}")

    if ses.scout_candidates.empty:
        st.markdown("<div class='tab-info'>候補がありません。『候補リスト更新』を押してください。</div>", unsafe_allow_html=True)
    else:
        for i,row in ses.scout_candidates.iterrows():
            st.markdown('<div class="scout-card">', unsafe_allow_html=True)
            st.markdown(
                f"**{row['Name']}**｜{row['Nat']}｜{row['Age']}歳｜{row['Pos']}｜OVR:{row['OVR']}<br>"
                f"PlayStyle: {row['PlayStyle']}<br>"
                f"所属: {row['Club']}｜評価額: {fmt_money(row['Value'])}",
                unsafe_allow_html=True
            )

            if row['Club']=="Free":
                if st.button("契約", key=f"free_sign_{i}"):
                    dst = 'youth' if youth_flag else 'senior'
                    setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row])], ignore_index=True))
                    ses.scout_candidates = ses.scout_candidates.drop(i).reset_index(drop=True)
                    housekeeping()
                    st.success("獲得しました！")
            else:
                mode = st.selectbox(f"オファー種別（{row['Name']}）", ["完全移籍","レンタル(買取OP付)"], key=f"offer_mode_{i}")

                with st.form(f"offer_form_{i}"):
                    if mode=="完全移籍":
                        wage  = st.number_input("提示年俸(€)", min_value=0, value=int(row['OVR']*180), key=f"wage_{i}")
                        years = st.slider("契約年数",1,5,3,key=f"years_{i}")
                        fee   = st.number_input("移籍金(€)", min_value=0, value=int(row['Value']), key=f"fee_{i}")
                        sent  = st.form_submit_button("送信")
                        if sent:
                            ok, want_wage, want_fee = offer_result(row,wage,years,fee,ses.budget)
                            if ok:
                                ses.budget -= fee
                                r2 = row.copy()
                                r2['Club']=ses.my_club
                                dst = 'youth' if youth_flag else 'senior'
                                setattr(ses,dst, pd.concat([getattr(ses,dst), pd.DataFrame([r2])], ignore_index=True))
                                ses.ai_players = ses.ai_players[ses.ai_players['Name']!=row['Name']]
                                ses.scout_candidates = ses.scout_candidates.drop(i).reset_index(drop=True)
                                housekeeping()
                                st.success("移籍成立！")
                            else:
                                st.error(f"拒否：要求目安 年俸{fmt_money(want_wage)} / 移籍金{fmt_money(want_fee)}")
                    else:
                        weeks = st.slider("レンタル期間（節）",1,8,4,key=f"rent_weeks_{i}")
                        fee_r = st.number_input("レンタル料(€)",min_value=0,value=int(row['Value']*0.12),key=f"rent_fee_{i}")
                        opt   = st.number_input("買取オプション額(€)",min_value=0,value=int(row['Value']*1.2),key=f"opt_fee_{i}")
                        sent2 = st.form_submit_button("送信")
                        if sent2:
                            ok,demand = rental_result(row,weeks,fee_r,ses.budget)
                            if ok:
                                ses.budget -= fee_r
                                r2 = row.copy()
                                r2['Club']=ses.my_club
                                r2['RentalFrom']=row['Club']
                                r2['RentalUntil']=ses.week+weeks
                                r2['OptionFee']=opt
                                r2['Status']=f"レンタル中({weeks}節)"
                                dst = 'youth' if youth_flag else 'senior'
                                setattr(ses,dst, pd.concat([getattr(ses,dst), pd.DataFrame([r2])], ignore_index=True))
                                ses.ai_players = ses.ai_players[ses.ai_players['Name']!=row['Name']]
                                ses.scout_candidates = ses.scout_candidates.drop(i).reset_index(drop=True)
                                housekeeping()
                                st.success("レンタル成立！")
                            else:
                                st.error(f"拒否：要求額目安 {fmt_money(demand)}")

            st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Part 9 / 13  --- レンタル管理 / SNS
# =========================

# ---------- 6) レンタル管理 ----------
with tabs[6]:
    st.markdown('<div class="section-box"><h3>レンタル管理</h3></div>', unsafe_allow_html=True)

    # 期限切れチェック
    handle_rental_expirations()

    df_r = pd.concat([ses.senior, ses.youth], ignore_index=True)
    df_r = df_r[df_r['Status'].str.startswith("レンタル中", na=False)][
        ['Name','Pos','OVR','RentalFrom','RentalUntil','OptionFee','Status']
    ]

    if df_r.empty:
        st.markdown("<div class='tab-info'>レンタル中の選手はいません。</div>", unsafe_allow_html=True)
    else:
        st.dataframe(df_white(df_r), use_container_width=True)
        st.markdown("※ レンタル満了時に自動返却します。買取したい場合は下から実行してください。")

        for _, r in df_r.iterrows():
            nm = r['Name']
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"買取（{nm}）", key=f"buy_{nm}"):
                    opt = int(r['OptionFee'] or 0)
                    if ses.budget >= opt:
                        # senior/youth から該当選手を更新
                        for dfname in ['senior','youth']:
                            df = getattr(ses, dfname)
                            idx = df.index[df['Name']==nm]
                            if len(idx)>0:
                                df.loc[idx, ['RentalFrom','RentalUntil','OptionFee','Status']] = [None,None,None,"通常"]
                                setattr(ses, dfname, df)
                        ses.budget -= opt
                        st.success("買取成立！")
                    else:
                        st.error("予算不足です。")
            with c2:
                if st.button(f"即時返却（{nm}）", key=f"ret_{nm}"):
                    # 元クラブへ返却
                    origin = r['RentalFrom']
                    for dfname in ['senior','youth']:
                        df = getattr(ses, dfname)
                        idx = df.index[df['Name']==nm]
                        if len(idx)>0:
                            bak = df.loc[idx[0]].copy()
                            df = df.drop(idx)
                            setattr(ses, dfname, df)
                            break
                    bak['Club']=origin
                    bak[['RentalFrom','RentalUntil','OptionFee','Status']] = [None,None,None,"通常"]
                    ses.ai_players = pd.concat([ses.ai_players, pd.DataFrame([bak])], ignore_index=True)
                    st.info("返却しました。")

# ---------- 7) SNS ----------
with tabs[7]:
    st.markdown('<div class="section-box"><h3>SNS / ファンフィード</h3></div>', unsafe_allow_html=True)
    if ses.sns_posts:
        for t, msg in zip(reversed(ses.sns_times), reversed(ses.sns_posts)):
            st.write(f"{t.strftime('%m/%d %H:%M')} - {msg}")
    else:
        st.markdown("<div class='tab-info'>投稿はまだありません。</div>", unsafe_allow_html=True)

# =========================
# Part 10 / 13  --- 財務レポート
# =========================
with tabs[8]:
    st.markdown('<div class="section-box"><h3>財務レポート</h3></div>', unsafe_allow_html=True)

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
        ax.legend(frameon=False, bbox_to_anchor=(1,1))
        make_transparent(ax)
        st.pyplot(fig)

        st.dataframe(df_white(df_fin_j), use_container_width=True)

# =========================
# Part 12 / 13  --- 国際大会
# =========================
with tabs[10]:
    st.markdown('<div class="section-box"><h3>国際大会</h3></div>', unsafe_allow_html=True)

    if not ses.intl_tournament or len(ses.intl_tournament.get('results',[]))==0:
        st.markdown("<div class='tab-info'>国際大会は未開催です。試合を進めると自動で進行します。</div>", unsafe_allow_html=True)
    else:
        res = ses.intl_tournament['results']

        # ラウンド分割表示
        st.markdown("### 📊 トーナメント結果")
        # 単純に結果件数で段階的に割る（例：16→8→4→2→1）
        size = len(res)
        rounds = []
        # 推測で1R=総試合数の1/4などは難しいので、結果を4試合ずつなどで区切る
        step = 4
        for i in range(0, size, step):
            rounds.append(res[i:i+step])

        for idx, rd in enumerate(rounds, 1):
            st.markdown(f"#### Round {idx}")
            show = []
            for (c1,g1,c2,g2,pk,win) in rd:
                show.append({"Home":c1,"G1":g1,"Away":c2,"G2":g2,"PK":pk,"勝者":win})
            df_r = pd.DataFrame(show)
            st.dataframe(df_white(df_r).apply(make_highlighter('勝者', ses.my_club), axis=1), use_container_width=True)

        if ses.intl_tournament.get('finished') and len(ses.intl_tournament.get('clubs',[]))==1:
            champ = ses.intl_tournament['clubs'][0]
            if champ == ses.my_club:
                st.markdown(f"<span style='background:#f7df70;color:#202b41;font-weight:bold'>優勝: {champ}</span>", unsafe_allow_html=True)
            else:
                st.success(f"優勝: {champ}")

    st.markdown("---")
    st.markdown("### 🏆 個人成績ランキング（国際大会）")
    if not ses.intl_player_stats:
        st.markdown("<div class='tab-info'>個人成績データがまだありません。</div>", unsafe_allow_html=True)
    else:
        df_int = pd.DataFrame.from_dict(ses.intl_player_stats, orient='index')
        df_int['Name'] = df_int.index
        for c in ['G','A','Club','Pos']:
            if c not in df_int: df_int[c]=0

        top_g = df_int.sort_values('G', ascending=False).head(10)[['Name','Pos','G','A','Club']]
        st.markdown("**得点ランキング TOP10**")
        st.dataframe(df_white(top_g).apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)

        top_a = df_int.sort_values('A', ascending=False).head(10)[['Name','Pos','A','G','Club']]
        st.markdown("**アシストランキング TOP10**")
        st.dataframe(df_white(top_a).apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)

        # ベスト11（国際大会）
        best11=[]
        for p,need in [('GK',1),('DF',4),('MF',4),('FW',2)]:
            cand = df_int[df_int['Pos']==p].copy()
            cand['Score'] = cand['G']*2 + cand['A']
            best11.append(cand.sort_values('Score', ascending=False).head(need)[['Name','Pos','G','A','Club']])
        best11 = pd.concat(best11) if best11 else pd.DataFrame()
        st.markdown("**⚽️ 国際大会ベストイレブン**")
        st.dataframe(df_white(best11).apply(make_highlighter('Club', ses.my_club), axis=1), use_container_width=True)

# =========================
# Part 13 / 13  --- クラブ設定 / 終端
# =========================
with tabs[11]:
    st.markdown('<div class="section-box"><h3>クラブ設定</h3></div>', unsafe_allow_html=True)

    st.write(f"現在のクラブ名：**{ses.my_club}**　／　予算：{fmt_money(ses.budget)}")

    # --- クラブ名変更 ---
    new_name = st.text_input("自クラブ名を変更", value=ses.my_club, max_chars=40, key="rename_box")
    def rename_club(old, new):
        if old==new: return
        # standings
        ses.standings.loc[ses.standings.Club==old, 'Club'] = new
        # leagues
        nat, div = ses.club_map[old]
        lst = ses.leagues[nat][div]
        if old in lst:
            lst[lst.index(old)] = new
        # players
        for dfname in ['senior','youth']:
            df = getattr(ses, dfname)
            df.loc[df['Club']==old, 'Club'] = new
            setattr(ses, dfname, df)
        # map更新
        ses.club_map = build_club_map(ses.standings)
        ses.my_club  = new
        housekeeping()

    if st.button("クラブ名変更", key="btn_rename"):
        if new_name.strip():
            rename_club(ses.my_club, new_name.strip())
            st.success("クラブ名を変更しました。")
            st.experimental_rerun()
        else:
            st.error("名前が空です。")

    st.markdown("---")

    # --- シーズンリセット（手動フル） ---
    st.markdown('<div class="section-box"><h4>シーズン管理</h4></div>', unsafe_allow_html=True)
    st.write("※ シーズン終了時は自動で次シーズンが始まります。手動リセットしたい場合のみ使用してください。")
    if st.button("シーズンを手動でリセット"):
        reset_season()
        st.success("新シーズン開始！")
        st.experimental_rerun()

    # --- 完全初期化（デバッグ用） ---
    with st.expander("完全初期化（全データ再生成・注意）"):
        if st.button("初期化を実行する"):
            st.session_state.ses = init_session()
            st.success("初期化しました。")
            st.experimental_rerun()

st.caption("✅ 全パート読み込み完了。エラーが出た場合は、最初のエラーメッセージ行を教えてください。")
