# =========================
# Part 1 / 12  --- Imports / 定数 / 基本ユーティリティ
# =========================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime
from types import SimpleNamespace

# ---- ページ設定 & 乱数固定 ----
st.set_page_config(page_title="Club Strive", layout="wide")
random.seed(42)
np.random.seed(42)

# ---- ゲーム基本設定 ----
SEASON_WEEKS = 14                      # 1シーズン14節
MY_DEFAULT_CLUB = "Signature Team"     # 自クラブ名
ABILITY_KEYS = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
ABILITY_JP   = {'Spd':'スピード','Pas':'パス','Phy':'フィジカル','Sta':'スタミナ',
                'Def':'守備','Tec':'テクニック','Men':'メンタル','Sht':'シュート','Pow':'パワー'}

POS_ORDER = ['GK','DF','MF','FW']      # 正順
POS_ORDER_REV = list(reversed(POS_ORDER))

# ---- 表示用ユーティリティ ----
def fmt_money(v:int)->str:
    if v>=1_000_000: return f"{v//1_000_000}m€"
    if v>=1_000:     return f"{v//1_000}k€"
    return f"{v}€"

def round_value(v:int)->int:
    """評価額の丸め：1000以上は切り捨て、999以下は5刻み"""
    if v>=1000:
        return (v//1000)*1000
    else:
        return int(round(v/5)*5)

def sort_by_pos(df:pd.DataFrame, reverse=False):
    order = POS_ORDER_REV if reverse else POS_ORDER
    cat = pd.Categorical(df['Pos'], categories=order, ordered=True)
    return df.assign(_poscat=cat).sort_values(['_poscat','OVR'], ascending=[True,False]).drop(columns='_poscat')

def sort_table(df):
    return df.sort_values(['Pts','W','GD','GF'], ascending=[False,False,False,False]).reset_index(drop=True)

def make_transparent(ax):
    ax.set_facecolor('none')
    ax.figure.patch.set_alpha(0)
    ax.grid(color="#fff", alpha=0.15)

# ---- レーダーチャート ----
def radar_chart(values, labels):
    ang = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    vals = np.array(values)
    fig = plt.figure(figsize=(3.2,3.2))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(np.concatenate([ang,[ang[0]]]), np.concatenate([vals,[vals[0]]]), linewidth=2)
    ax.fill(np.concatenate([ang,[ang[0]]]), np.concatenate([vals,[vals[0]]]), alpha=0.25)
    ax.set_xticks(ang); ax.set_xticklabels(labels, color="#eaf6ff", fontsize=9)
    ax.set_yticklabels([])
    make_transparent(ax)
    return fig

# =========================
# Part 2 / 12  --- CSS / テーブル描画ユーティリティ
# =========================
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }

.section-box h3{ font-size:1.45rem!important; margin-bottom:0.4rem; }
.section-box h4{ font-size:1.15rem!important; margin:0.6rem 0 0.2rem 0; }

.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }

.stButton>button { background:#27e3b9!important; color:#202b41!important; font-weight:bold; border-radius:10px; margin:6px 0; }
.stButton>button:active { background:#ffee99!important; }

/* Form submit(送信)ボタン */
button[kind="formSubmit"]{
    background:#27e3b9!important; color:#202b41!important;
    border:2px solid #f7df70!important; border-radius:10px!important;
}

/* DataFrame */
div[data-testid="stDataFrame"] table{
    background:rgba(32,44,70,0.78)!important;
    color:#eaf6ff!important;
    border-color:#445!important;
    font-size:0.9rem!important;
}
div[data-testid="stDataFrame"] thead tr th{
    background:rgba(32,44,70,0.95)!important;
    color:#ffffff!important;
    font-weight:600!important;
}
div[data-testid="stDataFrame"] tbody tr td{
    background:rgba(32,44,70,0.55)!important;
    color:#eaf6ff!important;
    border-color:#445!important;
}
div[data-testid="stDataFrame"] tbody tr:hover td{
    background:rgba(39,227,185,0.15)!important;
}
div[data-testid="stDataFrame"] div[role="button"]{ color:#eaf6ff!important; }

.scout-card{
    background:rgba(25,40,65,0.85);
    color:#eaf6ff;
    border:1px solid #27e3b9;
    border-radius:10px;
    padding:10px 12px;
    margin:10px 0;
}
.tab-info{
    background:rgba(255,255,255,0.08);
    padding:8px 12px;
    border-radius:8px;
    color:#eaf6ff;
    font-size:0.9rem;
}

/* グラフ背景透過 */
canvas, .js-plotly-plot, svg{ background:transparent!important; }
</style>
""", unsafe_allow_html=True)

def style_table(df: pd.DataFrame, highlight_fn=None):
    sty = df.style.set_properties(**{
        "background-color":"rgba(32,44,70,0.55)",
        "color":"#eaf6ff",
        "border-color":"#445",
        "font-size":"0.9rem"
    }).set_table_styles([
        {'selector':'th','props':[('background-color','rgba(32,44,70,0.95)'),
                                  ('color','#fff'),('font-weight','bold')]}
    ])
    if highlight_fn is not None:
        sty = sty.apply(highlight_fn, axis=1)
    return sty

def make_highlighter(col, value):
    def _hl(row):
        return ['background:rgba(39,227,185,0.25); color:#fff' if row[col]==value else '' for _ in row]
    return _hl

# =========================
# Part 3 / 12  --- 名前プール 1/3
# =========================
NATIONS = ["ENG","GER","FRA","ESP","ITA","NED","BRA","POR","BEL","TUR",
           "ARG","URU","COL","USA","MEX","SAU","NGA","MAR","KOR","AUS"]

NAME_POOL = {
"ENG":{
 "first":["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
          "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin",
          "Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"],
 "last":["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
         "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris",
         "Baker","Moore","Wright","Hill","Cooper","Edwards","Ward","King","Parker","Campbell"]
},
"GER":{
 "first":["Lukas","Finn","Felix","Jonas","Leon","Paul","Noah","Elias","Tim","Jan",
          "Moritz","Tom","Nico","Maximilian","Philipp","Matteo","Fabian","Emil","Erik","Simon",
          "Luis","Jonathan","David","Henry","Karl","Ben","Tobias","Jannik","Milan","Sebastian"],
 "last":["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Hoffmann","Schäfer",
         "Koch","Richter","Klein","Wolf","Schröder","Neumann","Schwarz","Zimmermann","Braun","Krüger",
         "Hofmann","Hartmann","Lange","Schmitt","Werner","Schmitz","Krause","Meier","Lehmann","Köhler"]
},
"FRA":{
 "first":["Louis","Gabriel","Jules","Adam","Arthur","Raphaël","Léo","Lucas","Hugo","Nathan",
          "Ethan","Tom","Paul","Noé","Maxime","Baptiste","Enzo","Theo","Axel","Antoine",
          "Robin","Clément","Julien","Alexandre","Matéo","Martin","Victor","Sacha","Simon","Romain"],
 "last":["Dubois","Durand","Lefebvre","Moreau","Simon","Laurent","Lefevre","Michel","Garcia","David",
         "Bertrand","Roux","Vincent","Fournier","Morel","Girard","Andre","Leroy","Mercier","Dupont",
         "Lambert","Bonnet","Francois","Martinez","Legrand","Garnier","Faure","Rousseau","Blanc","Guerin"]
},
"ESP":{
 "first":["Alejandro","Hugo","Daniel","Pablo","Adrián","Mario","Álvaro","Javier","Diego","Marco",
          "Ángel","Carlos","David","Sergio","Raúl","Rubén","Joel","Iván","Ismael","Gabriel",
          "Martín","Bruno","Nicolás","Gonzalo","Manuel","Arnau","Unai","Iker","Óscar","Miguel"],
 "last":["García","Martínez","López","Sánchez","Pérez","González","Rodríguez","Fernández","Moreno","Jiménez",
         "Álvarez","Romero","Hernández","Muñoz","Gutiérrez","Ruiz","Díaz","Alonso","Torres","Domínguez",
         "Vázquez","Ramos","Gil","Ramírez","Serrano","Navarro","Blanco","Molina","Iglesias","Cruz"]
},
"ITA":{
 "first":["Lorenzo","Alessandro","Gabriele","Matteo","Leonardo","Tommaso","Francesco","Riccardo","Mattia","Edoardo",
          "Andrea","Nicolo","Giovanni","Pietro","Simone","Davide","Filippo","Marco","Diego","Federico",
          "Christian","Daniele","Antonio","Salvatore","Raffaele","Emanuele","Stefano","Samuele","Luigi","Angelo"],
 "last":["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco",
         "Bruno","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Moretti",
         "Barbieri","Fontana","Santoro","Mariani","Rinaldi","Caruso","Ferrara","Galli","Martini","Leone"]
},
"NED":{
 "first":["Daan","Sem","Lucas","Levi","Finn","Liam","Milan","Noah","Thijs","Ruben",
          "Jesse","Bas","Julian","Thomas","Timo","Sven","Luuk","Joep","Niek","Max",
          "Pim","Gijs","Bram","Wout","Nick","Jasper","Stefan","Lars","Boaz","Kyan"],
 "last":["de Jong","Jansen","de Vries","van den Berg","Bakker","van Dijk","Visser","Smeets","Mulder","de Boer",
         "Dekker","van der Meer","Vermeulen","Bos","Maas","Peters","Hendriks","van Leeuwen","Kok","Willems",
         "van Dam","van der Linden","Peeters","Martens","Kuipers","Koster","Post","Smits","Timmermans","Meijer"]
},
"BRA":{
 "first":["Gabriel","João","Pedro","Lucas","Mateus","Guilherme","Felipe","Rafael","Bruno","Thiago",
          "Caio","Enzo","Matheus","Luiz","Henrique","Gustavo","Diego","Vinícius","André","Eduardo",
          "Rodrigo","Samuel","Vitor","Fernando","Danilo","Leonardo","Nathan","Miguel","Igor","Alex"],
 "last":["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Almeida","Costa","Gomes","Martins",
         "Rocha","Ribeiro","Carvalho","Araújo","Pereira","Lima","Barbosa","Barros","Cavalcante","Teixeira",
         "Monteiro","Melo","Cruz","Freitas","Cardoso","Pires","Nogueira","Vieira","Miranda","Dias"]
},
"POR":{
 "first":["Miguel","João","Tiago","Diogo","Gonçalo","Rodrigo","André","Pedro","Afonso","Rafael",
          "Bruno","Henrique","Hugo","Eduardo","Filipe","Martim","Ricardo","Tomás","Carlos","Vasco",
          "Daniel","Luís","Duarte","Samuel","Leandro","Nuno","Gil","Marco","Alexandre","Sérgio"],
 "last":["Silva","Santos","Ferreira","Pereira","Oliveira","Costa","Rodrigues","Martins","Jesus","Sousa",
         "Gonçalves","Fernandes","Alves","Marques","Rocha","Correia","Ribeiro","Carvalho","Pinto","Moreira",
         "Nunes","Soares","Vieira","Lopes","Cardoso","Cruz","Barbosa","Araujo","Castro","Neves"]
},
"BEL":{
 "first":["Lucas","Noah","Arthur","Louis","Gabriel","Milan","Mathis","Jules","Adam","Liam",
          "Victor","Hugo","Ethan","Nathan","Théo","Sacha","Maxime","Simon","Tom","Baptiste",
          "Tim","Robin","Ruben","Lars","Jasper","Daan","Kobe","Seppe","Dries","Stijn"],
 "last":["Peeters","Janssens","Maes","Jacobs","Mertens","Willems","Goossens","Claes","Wouters","de Smet",
         "Dubois","Aerts","Decoster","Pauwels","Smets","Lemmens","Geerts","Hendrickx","Vermeulen","Michiels",
         "Martens","Van Damme","De Clercq","Verhoeven","De Backer","Hermans","Dumont","Bertels","Stevens","Van Dyck"]
},
"TUR":{
 "first":["Mehmet","Mustafa","Ahmet","Ali","Hüseyin","Hasan","İbrahim","Yusuf","Ömer","Burak",
          "Emre","Murat","Fatih","Serkan","Volkan","Onur","Arda","Can","Kerem","Kaan",
          "Furkan","Uğur","Enes","Eren","Gökhan","Berk","Batuhan","Tolga","Sinan","Selim"],
 "last":["Yılmaz","Kaya","Demir","Şahin","Çelik","Yıldız","Yıldırım","Aydın","Öztürk","Aslan",
         "Arslan","Doğan","Kılıç","Özdemir","Kurt","Koç","Uçar","Korkmaz","Polat","Bulut",
         "Güneş","Aksoy","Çetin","Eren","Turan","Türkmen","Ay","Erdoğan","Taş","Sezer"]
}

    # =========================
# Part 4 / 12  --- 名前プール 2/3 & 成長タイプ／プレースタイル定義
# =========================

# --- 残り10カ国 名前プール ---
NAME_POOL.update({
"ARG":{
 "first":["Santiago","Matías","Lucas","Martín","Facundo","Juan","Bruno","Nicolás","Gonzalo","Tomás",
          "Federico","Gustavo","Agustín","Diego","Emiliano","Leandro","Miguel","Iván","Carlos","Jonathan",
          "Maximiliano","Facundo","Manuel","Esteban","Bruno","Sebastián","Marcos","Agustín","Luciano","Alan"],
 "last":["González","Rodríguez","Gómez","Fernández","López","Martínez","Pérez","García","Sánchez","Romero",
         "Torres","Ramírez","Alonso","Ruiz","Flores","Vega","Benítez","Herrera","Castro","Ramos",
         "Silva","Rojo","Vargas","Medina","Molina","Suárez","Ibarra","Domínguez","Acosta","Vega"]
},
"URU":{
 "first":["Mateo","Martín","Matías","Lucas","Santiago","Nicolás","Federico","Facundo","Agustín","Bruno",
          "Sebastián","Diego","Gonzalo","Juan","Emiliano","Rodrigo","Ignacio","Maximiliano","Alan","Leandro",
          "David","Jonathan","Álvaro","Cristian","Manuel","Esteban","José","Francisco","Víctor","Iván"],
 "last":["González","Rodríguez","Gómez","Fernández","López","Pérez","Díaz","Sánchez","Ortiz","Morales",
         "Jiménez","Rojas","Torres","Ramírez","Álvarez","Castro","Suárez","Vega","Rivera","Medina",
         "Núñez","Pereira","Méndez","Vargas","Acosta","Blanco","Quinteros","Herrera","Casanova","Ramos"]
},
"COL":{
 "first":["Juan","Andrés","Santiago","Nicolás","Mateo","David","Camilo","Luis","Felipe","Alejandro",
          "Carlos","Miguel","Daniel","Sebastián","Andrés","José","Diego","Marco","Esteban","Javier",
          "Cristian","William","Jhon","Brayan","Kevin","Óscar","Eduardo","Rodrigo","Anderson","Johan"],
 "last":["González","Rodríguez","Gómez","Martínez","López","Pérez","Sánchez","Ramírez","Torres","Díaz",
         "Castro","Ríos","Vargas","Hernández","Ramírez","Restrepo","Mejía","Rodríguez","Álvarez","Mendoza",
         "Luna","Rodríguez","Cruz","Uribe","Suárez","Patiño","García","Ospina","Jiménez","Soto"]
},
"USA":{
 "first":["Liam","Noah","Oliver","Elijah","William","James","Benjamin","Lucas","Henry","Alexander",
          "Mason","Michael","Ethan","Daniel","Jacob","Logan","Jackson","Levi","Sebastian","Mateo",
          "Jack","Owen","Theodore","Aiden","Samuel","Joseph","John","David","Wyatt","Matthew"],
 "last":["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
         "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
         "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson"]
},
"MEX":{
 "first":["José","Luis","Juan","Miguel","Jorge","Jesús","Carlos","Francisco","Pedro","Manuel",
          "Alejandro","Fernando","Diego","Ricardo","Raúl","Sergio","Antonio","Eduardo","Arturo","Óscar",
          "Héctor","Víctor","Mario","Mario","Emilio","Ángel","Gustavo","Armando","Marcos","Rubén"],
 "last":["García","Martínez","Hernández","López","González","Pérez","Rodríguez","Sánchez","Ramírez","Torres",
         "Flores","Rivera","Gómez","Diaz","Morales","Herrera","Vargas","Castillo","Jiménez","Ortega",
         "Ruiz","Mendoza","Reyes","Cruz","Ortiz","Guerrero","Medina","Castro","Suárez","Núñez"]
},
"SAU":{
 "first":["Mohammed","Abdullah","Fahad","Saud","Turki","Salman","Nasser","Abdulrahman","Yousef","Khalid",
          "Faisal","Riyad","Talal","Abdulaziz","Hassan","Majed","Mansour","Hamad","Mamdouh","Jaber",
          "Abdulaziz","Ahmed","Saleh","Mashari","Abdulmalik","Badr","Sultan","Ayman","Basmah","Rakan"],
 "last":["Al-Shehri","Al-Qahtani","Al-Dossari","Al-Ghamdi","Al-Farhan","Al-Harbi","Al-Zahrani","Al-Mutairi","Al-Shamrani","Al-Rashid",
         "Al-Qaissi","Al-Nasser","Al-Rejaie","Al-Harthi","Al-Subaie","Al-Johani","Al-Gosaibi","Al-Bishi","Al-Qahtani","Al-Qahtani"]
},
"NGA":{
 "first":["Emeka","Chinedu","Ibrahim","Ahmed","David","John","Michael","Joseph","Daniel","Blessing",
          "Chukwuemeka","Oluwaseun","Oluwatobi","Sani","Okechukwu","Kunle","Nnamdi","Ifedayo","Oladipo","Omodayo",
          "Temitope","Chukwu","Obinna","Uche","Emmanuel","Godwin","Segun","Efe","Amara","Benedict"],
 "last":["Okafor","Ibrahim","Ogunleye","Adeniran","Oladipo","Okeke","Chukwu","Eze","Onyekachi","Adebayo",
         "Adekoya","Ojo","Ibe","Iwu","Nwankwo","Eze","Okonkwo","Ikenna","Okoro","Olaoye",
         "Ola","Akintola","Adeyemi","Ogun","Afolabi","Bello","Oladiran","Adewale","Odunze","Obi"]
},
"MAR":{
 "first":["Youssef","Mohamed","Hicham","Omar","Karim","Ayoub","Yassine","Anas","Zakaria","Taha",
          "Soufiane","Noureddine","Rachid","Hassan","Mouad","Adil","Abdel","Salim","Ayoub","Hamza",
          "Nabil","Abdelkader","Ismail","Amine","Youssef","Zinedine","Abdelaziz","Badr","Mehdi","Naji"],
 "last":["El Haddad","El Ghazali","El Youssfi","Benjelloun","El Mansouri","Boukhalfa","Bouhafs","Bensalem","Bouzidi","El Idrissi",
         "El Alami","Bouazza","Bennani","Hafidi","Alaoui","Alami","Ouarzazi","El Fassi","Benarous","Bennani",
         "Boussouf","El Khatib","Azzouzi","El Mokhtar","Mahjoub","Ouladsadok","El Mouden","Benali","El Ouahabi","Benchekroun"]
},
"KOR":{
 "first":["Min-jun","Seo-jun","Ji-hoon","Ji-ho","Ji-hu","Joon","Seung-hyun","Ji-ho","Woo-jin","Hyun-woo",
          "Jae-hyun","Seung-min","Tae-hyun","Dong-hyun","Ji-young","Young-min","Sang-hoon","Dae-hyun","Kang-ho","Sun-woo",
          "Hyeon-woo","Jin-woo","Jun-seo","Yong-hwa","Chan-woo","Min-seok","Hyun-sik","Ji-hoon","Jung-hoon","Seung-woo"],
 "last":["Kim","Lee","Park","Choi","Jung","Kang","Cho","Yoon","Jang","Lim",
         "Han","Oh","Seo","Shin","Yoo","Moon","Jeong","Hwang","Ahn","Song",
         "Ryu","Joo","Baek","Yim","Chung","Ko","Cha","Jeon","Nam","Do"]
},
"AUS":{
 "first":["Oliver","William","Jack","Noah","Thomas","James","Lucas","Ethan","Alexander","Liam",
          "Charlie","Henry","Oscar","Max","Samuel","Mason","Leo","Harrison","Daniel","Benjamin",
          "Jacob","Isaac","Logan","Cooper","Jackson","Ryan","Archie","Carter","Zachary","Hunter"],
 "last":["Smith","Jones","Williams","Brown","Wilson","Taylor","Johnson","White","Martin","Anderson",
         "Thompson","Thomas","Harris","Roberts","Walker","Young","Allen","King","Wright","Scott",
         "Mitchell","Campbell","Evans","Turner","Parker","Collins","Edwards","Stewart","Morris","Murphy"]
}
})

# --- 成長タイプ定義 ---
GROWTH_TYPES = ["早熟型","晩成型","平均型","緩成型","超早熟型"]
# --- プレースタイル例（選手あたり複数持てる） ---
PLAY_STYLES = [
    "チャンスメイカー","タックルマスター","空中戦の王","チーム至上主義","スイーパーリーダー",
    "セカンドストライカー","影の支配者","クロスハンター","ジョーカー","起点型GK",
    "爆発型","職人","師弟型","フリーキッカー","ムードメーカ","インナーラップSB"
]

# --- セッション初期化関数 ---
def init_session():
    ses = SimpleNamespace()
    ses.week = 1
    ses.my_club = MY_DEFAULT_CLUB
    ses.budget = 5_000_000
    ses.senior = pd.DataFrame()
    ses.youth = pd.DataFrame()
    ses.standings = pd.DataFrame()
    ses.leagues = {}
    ses.club_map = {}
    ses.finance_log = []
    ses.intl_tournament = {}
    ses.intl_player_stats = {}
    ses.player_history = {}
    ses.ai_players = pd.DataFrame()
    ses.scout_candidates = pd.DataFrame()
    ses.sns_posts = []
    return ses

# セッション確保
if "ses" not in st.session_state:
    st.session_state.ses = init_session()
ses = st.session_state.ses

# --- ランダムネーム生成 ---
def make_name(nat, used:set):
    while True:
        fn = random.choice(NAME_POOL[nat]["first"])
        ln = random.choice(NAME_POOL[nat]["last"])
        nm = f"{fn} {ln}"
        if nm not in used:
            used.add(nm)
            return nm


# =========================
# Part 5 / 12  (改) --- クラブ・リーグ生成 & 選手配属・シーズン管理関数
#                        【全20ヵ国、すべて2部リーグ化】
# =========================

# ―― クラブ名プール 20ヵ国、すべて2部制（D1/D2） ――
CLUB_NAME_POOL = {
    "ENG":{
        "D1":["Copper City","Sterling Dynamos","Shadow Hearts","Golden Storm","Ivory Queens","Apex Quest","Midnight FC","River Wolves"],
        "D2":["Kingston Kings","Brighton Blazers","Oxford Owls","Yorkshire Yaks","London Lions","Leeds Legends","Nottingham Knights","Sheffield Sharks"]
    },
    "GER":{
        "D1":["Bavaria United","Rhine Rovers","Black Forest","Berlin Eagles","Hamburg Harpoons","Frankfurt Lions","Stuttgart Knights","Cologne Dragons"],
        "D2":["Munich Mavericks","Dortmund Dynamo","Leipzig Lions","Bremen Buccaneers","Düsseldorf Defenders","Hannover Hawks","Darmstadt Dragoons","Köln Kings"]
    },
    "FRA":{
        "D1":["Paris Royals","Lyon Titans","Marseille Mariners","Bordeaux Bulls","Nice Navigators","Lille Stars","Rennes Rangers","Toulouse Trojans"],
        "D2":["Strasbourg Stallions","Nantes Navigators","Monaco Monarchs","Lorient Legends","Brest Buccaneers","Reims Raiders","Montpellier Mavericks","Metz Mariners"]
    },
    "ESP":{
        "D1":["Madrid Monarchs","Barcelona Blazers","Sevilla Spartans","Valencia Vultures","Bilbao Bandits","Granada Guardians","Mallorca Mariners","Zaragoza Zephyrs"],
        "D2":["Valladolid Vixens","Cádiz Chargers","Deportivo Dynamos","Almería Avengers","Sporting Strikers","Leganés Lions","Castilla Knights","Mallorca Mariners II"]
    },
    "ITA":{
        "D1":["Venice Valiants","Rome Reapers","Florence Flyers","Milan Masters","Turin Torches","Naples Navigators","Genoa Gliders","Verona Victors"],
        "D2":["Palermo Pirates","Bari Braves","Siena Sabres","Bologna Beacons","Brescia Breakers","Lecce Legends","Parma Phantoms","Cagliari Cyclones"]
    },
    "NED":{
        "D1":["Amsterdam Admirals","Rotterdam Raiders","Utrecht Unicorns","Eindhoven Eagles","Groningen Giants","Maastricht Monarchs","Tilburg Titans","Hague Hawks"],
        "D2":["Zwolle Zephyrs","Nijmegen Navigators","Enschede Eagles","Apeldoorn Aces","Amersfoort Avengers","Leeuwarden Lions","Roosendaal Rovers","Venlo Vanguards"]
    },
    "BRA":{
        "D1":["Rio Royals","São Paulo Spartans","Brasília Braves","Salvador Strikers","Fortaleza Flyers","Recife Raiders","Curitiba Crushers","Porto Alegre Pioneers"],
        "D2":["Manaus Mariners","Belém Bandits","Florianópolis Falcons","Goiania Gladiators","Campinas Chargers","Natal Navigators","João Pessoa Juggernauts","Cuiabá Crushers"]
    },
    "POR":{
        "D1":["Lisbon Legends","Porto Pioneers","Braga Blazers","Coimbra Kings","Faro Falcons","Aveiro Avengers","Setúbal Stingers","Évora Eagles"],
        "D2":["Guimarães Guardians","Viseu Vanguards","Leiria Lions","Bragança Braves","Vila Real Victors","Castelo Knights","Portalegre Patriots","Bragança Borough"]
    },
    "BEL":{
        "D1":["Brussels Battalion","Antwerp Aces","Ghent Gladiators","Bruges Buccaneers","Liège Lions","Charleroi Chargers","Mons Mavericks","Namur Navigators"],
        "D2":["Mechelen Masters","Leuven Legends","Kortrijk Kings","Ostend Olympians"," Hasselt Hawks","Tournai Titans","La Louvière Lions","Lucebern Lancers"]
    },
    "TUR":{
        "D1":["Istanbul Imperials","Ankara Archers","Izmir Invincibles","Antalya Avengers","Bursa Braves","Konya Kings","Adana Admirals","Trabzon Trojans"],
        "D2":["Eskişehir Eagles","Gaziantep Guardians","Kayseri Knights","Mersin Mariners","Samsun Stallions","Denizli Defenders","Sivas Spartans","Batman Bandits"]
    },
    "ARG":{
        "D1":["Buenos Aires Bandits","Córdoba Crusaders","Rosario Rangers","Mendoza Monarchs","La Plata Lions","Tucumán Titans","Mar del Plata Mariners","Salta Strikers"],
        "D2":["Bahía Blanca Braves","Resistencia Raiders","Posadas Pioneers","San Juan Sentinels","Neuquén Navigators","Formosa Falcons","Corrientes Chargers","Paraná Patriots"]
    },
    "URU":{
        "D1":["Montevideo Mavericks","Salto Spartans","Punta Pioneers","Rivera Royals","Maldonado Mariners","Paysandú Panthers","Tacuarembó Titans","Soriano Stallions"],
        "D2":["Durazno Defenders","Florida Falcons","Canelones Crusaders","San José Strikers","Artigas Avengers","River Plate Rangers","Colonia Chargers","Lavalleja Lions"]
    },
    "COL":{
        "D1":["Bogotá Battalion","Medellín Mariners","Cali Crushers","Barranquilla Blazers","Cartagena Chargers","Pereira Pioneers","Bucaramanga Bulls","Manizales Monarchs"],
        "D2":["Cúcuta Crusaders","Ibagué Invincibles","Pasto Phantoms","Villavicencio Vanguards","Neiva Navigators","Popayán Patriots","Tunja Titans","Valledupar Vipers"]
    },
    "USA":{
        "D1":["New York Knights","Los Angeles Legends","Chicago Chargers","Houston Harbingers","Phoenix Phantoms","Philadelphia Phalanx","San Diego Spartans","Dallas Dynamos"],
        "D2":["Miami Mariners","Seattle Sentinels","Denver Dynamos","Atlanta Archers","Boston Battalion","San Francisco Strikers","Orlando Olympians","Portland Pioneers"]
    },
    "MEX":{
        "D1":["Mexico City Matadors","Guadalajara Griffins","Monterrey Mavericks","Puebla Pioneers","Tijuana Titans","Toluca Torches","León Lions","Querétaro Quetzals"],
        "D2":["Cancún Chargers","Mérida Mariners","Chihuahua Champions","Veracruz Valiants","Durango Defenders","Mazatlán Monarchs","Saltillo Stallions","Aguascalientes Aces"]
    },
    "SAU":{
        "D1":["Riyadh Royals","Jeddah Jaguars","Mecca Mariners","Dammam Dragons","Taif Titans","Medina Monarchs","Jubail Jaguars","Yanbu Yachtsmen"],
        "D2":["Tabuk Titans","Buraidah Braves","Khamis Crusaders","Najran Navigators","Yanbu Warriors","Abha Avengers","Al-Khobar Kings","Al-Hasa Hawks"]
    },
    "NGA":{
        "D1":["Lagos Lions","Abuja Avengers","Kano Knights","Port Harcourt Pirates","Ibadan Invincibles","Benin Braves","Jos Jaguars","Enugu Eagles"],
        "D2":["Kaduna Kings","Zaria Zephyrs","Abeokuta Avengers","Ikeja Invincibles","Onitsha Olympians","Warri Warriors","Uyo Unicorns","Katsina Chargers"]
    },
    "MAR":{
        "D1":["Casablanca Crushers","Rabat Royals","Fes Falcons","Tanger Titans","Agadir Avengers","Marrakech Monarchs","Oujda Olympians","Kenitra Kings"],
        "D2":["Essaouira Eagles","Ouarzazate Ostriches","El Jadida Jaguars","Nador Navigators","Ksar Knights","Khouribga Crusaders","Settat Stallions","Tétouan Titans"]
    },
    "KOR":{
        "D1":["Seoul Spartans","Busan Buccaneers","Incheon Invincibles","Daegu Dragons","Daejeon Dynamos","Gwangju Gladiators","Ulsan United","Suwon Strikers"],
        "D2":["Jeonju Jaguars","Cheonan Chargers","Chuncheon Champions","Andong Avengers","Gangneung Guardians","Pohang Phantoms","Gyeongju Giants","Iksan Invincibles"]
    },
    "AUS":{
        "D1":["Sydney Sentinels","Melbourne Mavericks","Brisbane Blazers","Perth Pioneers","Adelaide Admirals","Canberra Chargers","Gold Coast Gladiators","Hobart Hawks"],
        "D2":["Newcastle Navigators","Wollongong Warriors","Darwin Dynamos","Sunshine Stallions","Townsville Titans","Geelong Guardians","Ballarat Battalion","Bendigo Buccaneers"]
    }
}

def setup_leagues():
    """リーグ・スタンディング初期化＆選手生成"""
    ses.leagues = {}
    for nat, divs in CLUB_NAME_POOL.items():
        ses.leagues[nat] = {div: clubs.copy() for div, clubs in divs.items()}

    rows = []
    for nat, dic in ses.leagues.items():
        for div, clubs in dic.items():
            for c in clubs:
                rows.append({
                    "Nation": nat, "Division": div, "Club": c,
                    "W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0
                })
    ses.standings = pd.DataFrame(rows)
    ses.club_map = build_club_map(ses.standings)

    # 選手生成（シニア30人＋ユース20人）
    sen_list = []; youth_list = []
    for club, (nat, div) in ses.club_map.items():
        # シニア
        df_s = gen_players(30, False)
        df_s["Club"]      = club
        df_s["Growth"]    = random.choices(GROWTH_TYPES, k=len(df_s))
        df_s["PlayStyle"] = ["/".join(random.sample(PLAY_STYLES,2)) for _ in range(len(df_s))]
        sen_list.append(df_s)
        # ユース
        df_y = gen_players(20, True)
        df_y["Club"]      = club
        df_y["Growth"]    = random.choices(GROWTH_TYPES, k=len(df_y))
        df_y["PlayStyle"] = ["/".join(random.sample(PLAY_STYLES,2)) for _ in range(len(df_y))]
        youth_list.append(df_y)

    ses.senior = pd.concat(sen_list, ignore_index=True)
    ses.youth  = pd.concat(youth_list, ignore_index=True)

# =========================
# Part 6 / 12  --- 試合 & 国際大会進行関数
# =========================

def update_standings(home, away, gh, ga):
    """勝敗・得失点・勝ち点をスタンディングに反映"""
    df = ses.standings
    # 勝敗
    if gh > ga:
        df.loc[df.Club==home, ["W","Pts"]] += [1,3]
        df.loc[df.Club==away, "L"]      += 1
    elif gh < ga:
        df.loc[df.Club==away, ["W","Pts"]] += [1,3]
        df.loc[df.Club==home, "L"]      += 1
    else:
        df.loc[df.Club.isin([home,away]), ["D","Pts"]] += [1,1]
    # 得失点
    df.loc[df.Club==home, ["GF","GA"]] += [gh,ga]
    df.loc[df.Club==away, ["GF","GA"]] += [ga,gh]
    # GDとソート更新
    df["GD"] = df["GF"] - df["GA"]
    ses.standings = sort_table(df)

def apply_growth(df, week):
    """節ごとの成長処理"""
    df = df.copy()
    for i, r in df.iterrows():
        gt = r.get("Growth","平均型")
        delta = 0
        if gt=="超早熟型" and week<SEASON_WEEKS//2 and random.random()<0.4:
            delta = random.randint(2,4)
        elif gt=="早熟型" and week<SEASON_WEEKS//2 and random.random()<0.3:
            delta = random.randint(1,3)
        elif gt=="平均型" and random.random()<0.2:
            delta = 1
        elif gt=="晩成型" and week>SEASON_WEEKS//2 and random.random()<0.25:
            delta = random.randint(1,2)
        # 各能力値とOVRに加算
        if delta:
            for k in ABILITY_KEYS:
                df.at[i, k] = int(np.clip(r[k] + delta//2, 1, 99))
            df.at[i, "OVR"] = int(np.clip(r["OVR"] + delta, 1, 99))
    return df

def update_player_history(name, row, week):
    """選手のOVR履歴を記録"""
    hist = ses.player_history.setdefault(name, [])
    hist.append({ "week": week, "OVR": row["OVR"] })

def add_finance(week, ticket, goods, salary):
    """財務ログ追加"""
    ses.finance_log.append({
        "week": week,
        "チケット収入": ticket,
        "グッズ収入": goods,
        "人件費": salary
    })

def add_match_log(week, home, away, gh, ga, scorers, assisters):
    """マッチログ記録"""
    ses.match_log.append({
        "week": week,
        "home": home,
        "away": away,
        "gf": gh,
        "ga": ga,
        "scorers": scorers,
        "assisters": assisters
    })

def auto_intl_round():
    """国際大会を裏で自動進行"""
    # 初回：参加クラブを決定
    if not ses.intl_tournament:
        clubs = []
        for nat, divs in ses.leagues.items():
            if "D1" in divs:
                tbl = ses.standings[(ses.standings.Nation==nat)&(ses.standings.Division=="D1")]
                top2 = tbl.nlargest(2, "Pts")["Club"].tolist()
                clubs += top2
        random.shuffle(clubs)
        ses.intl_tournament = { "clubs": clubs, "results": [], "finished": False }
        return

    # 終了済みなら無視
    if ses.intl_tournament.get("finished"):
        return

    clubs = ses.intl_tournament["clubs"]
    # 残り1なら優勝処理
    if len(clubs) <= 1:
        ses.intl_tournament["finished"] = True
        return

    winners = []
    for i in range(0, len(clubs), 2):
        if i+1 >= len(clubs):
            winners.append(clubs[i])
            break
        c1, c2 = clubs[i], clubs[i+1]
        g1, g2 = random.randint(0,4), random.randint(0,4)
        pk = ""
        if g1 == g2:
            p1, p2 = random.randint(3,6), random.randint(3,6)
            while p1 == p2:
                p1, p2 = random.randint(3,6), random.randint(3,6)
            pk = f"PK {p1}-{p2}"
            win = c1 if p1>p2 else c2
        else:
            win = c1 if g1>g2 else c2
        ses.intl_tournament["results"].append((c1, g1, c2, g2, pk, win))
        # SNSにも投稿
        ses.sns_posts.append(f"[国際大会] {c1} {g1}-{g2} {c2} {pk} → 勝者:{win}")
        ses.sns_times.append(datetime.now())
        # 個人成績反映（簡易）
        pool = pd.concat([ses.senior, ses.youth, ses.ai_players], ignore_index=True)
        XI = pool[pool.Club==win].nlargest(1, "OVR")
        for name in XI["Name"]:
            stats = ses.intl_player_stats.setdefault(name, {"G":0,"A":0,"Club":win,"Pos":XI["Pos"].iloc[0]})
            stats["G"] += 1
        winners.append(win)
    ses.intl_tournament["clubs"] = winners
    if len(winners) == 1:
        ses.intl_tournament["finished"] = True
        ses.sns_posts.append(f"[国際大会] 優勝: {winners[0]}")
        ses.sns_times.append(datetime.now())

# =========================
# Part 7 / 12  --- タブ定ザイン & メインUI実装
# =========================
# タブ定義
tabs = st.tabs([
    "シニア","ユース","選手詳細","試合","順位表",
    "スカウト/移籍","レンタル管理","SNS","財務レポート",
    "年間表彰","国際大会","クラブ設定"
])

# --- 0) シニア選手一覧 ---
with tabs[0]:
    st.markdown('<div class="section-box"><h3>シニア選手一覧</h3></div>', unsafe_allow_html=True)
    handle_rental_expirations()
    mode = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="order_senior")
    df0 = ses.senior[['Name','Nat','Pos','Age','OVR','PlayStyle','Goals','Assists','Status']]
    df0 = sort_by_pos(df0, reverse=(mode.startswith("FW")))
    st.dataframe(style_table(df0, make_highlighter('Status','レンタル中')), use_container_width=True)

# --- 1) ユース選手一覧 ---
with tabs[1]:
    st.markdown('<div class="section-box"><h3>ユース選手一覧</h3></div>', unsafe_allow_html=True)
    mode_y = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="order_youth")
    df1 = ses.youth[['Name','Nat','Pos','Age','OVR','PlayStyle','Goals','Assists','Status']]
    df1 = sort_by_pos(df1, reverse=(mode_y.startswith("FW")))
    st.dataframe(style_table(df1, make_highlighter('Status','レンタル中')), use_container_width=True)

# --- 2) 選手詳細 ---
with tabs[2]:
    st.markdown('<div class="section-box"><h3>選手詳細</h3></div>', unsafe_allow_html=True)
    all_players = pd.concat([ses.senior, ses.youth], ignore_index=True)
    if all_players.empty:
        st.markdown("<div class='tab-info'>表示できる選手がいません。</div>", unsafe_allow_html=True)
    else:
        sel = st.selectbox("選手選択", all_players['Name'].tolist())
        ply = all_players[all_players['Name']==sel].iloc[0]
        st.write(f"ポジション: {ply.Pos}  OVR: {ply.OVR}  年齢: {ply.Age}")
        st.write(f"国籍: {ply.Nat}  シーズン出場: {ply.Matches_Played}  国際大会出場: {ply.IntlApps}")
        st.write(f"状態: {ply.Status}  プレースタイル: {ply.PlayStyle}")
        # レーダーチャート
        fig = radar_chart([ply[k] for k in ABILITY_KEYS], ABILITY_JP.values())
        st.pyplot(fig)
        # 成長履歴グラフ
        hist = ses.player_history.get(sel, [])
        if len(hist)>1:
            dfh = pd.DataFrame(hist)
            fig2, ax2 = plt.subplots()
            ax2.plot(dfh.week, dfh.OVR, marker='o')
            ax2.set_xlabel("節"); ax2.set_ylabel("OVR")
            make_transparent(ax2)
            st.pyplot(fig2)
        else:
            st.markdown("<div class='tab-info'>成長データはまだありません。</div>", unsafe_allow_html=True)

# =========================
# Part 8 / 12  --- 試合 / 順位表 / スカウト・移籍
# =========================

# ── セッション属性の保険 ──
if not hasattr(ses, "starters"):      ses.starters = []
if not hasattr(ses, "auto_selected"): ses.auto_selected = False
if not hasattr(ses, "match_log"):     ses.match_log = []

# --- 3) 試合シミュレーション ---
with tabs[3]:
    st.markdown(f'<div class="section-box"><h3>第 {ses.week} 節 試合シミュレーション</h3></div>', unsafe_allow_html=True)
    formation = st.selectbox("フォーメーション", ["4-4-2","4-3-3","3-5-2"], key="form_sel")

    # オート先発選考
    if st.button("オート先発選考", key="btn_auto"):
        req = {"4-4-2":("FW",2,"MF",4,"DF",4,"GK",1),
               "4-3-3":("FW",3,"MF",3,"DF",4,"GK",1),
               "3-5-2":("FW",2,"MF",5,"DF",3,"GK",1)}[formation]
        sel=[] 
        for i in range(0,len(req),2):
            p,c=req[i],req[i+1]
            sel += ses.senior[ses.senior.Pos==p].nlargest(c,"OVR").Name.tolist()
        ses.starters = sel
        ses.auto_selected = True

    # 先発一覧表示
    if ses.starters:
        st.markdown('<div class="section-box"><h4>先発メンバー</h4></div>', unsafe_allow_html=True)
        dfxi = ses.senior[ses.senior.Name.isin(ses.starters)][['Name','Pos','OVR','Goals','Assists','PlayStyle']]
        st.dataframe(style_table(sort_by_pos(dfxi)), use_container_width=True)
    else:
        st.warning("『オート先発選考』を実行してください。")

    # 対戦相手は同ディビジョン内からランダム
    my_nat,my_div = ses.club_map[ses.my_club]
    opps = ses.standings.query("Nation==@my_nat & Division==@my_div").Club.tolist()
    opps = [c for c in opps if c!=ses.my_club]
    opponent = random.choice(opps) if opps else ses.my_club

    kickoff = st.button("キックオフ", disabled=not ses.auto_selected or ses.week>SEASON_WEEKS)
    if kickoff:
        # 攻撃力
        atk = ses.senior[ses.senior.Name.isin(ses.starters)].OVR.mean() if ses.starters else 70
        opp_pool = ses.ai_players.query("Club==@opponent")
        oppatk = opp_pool.OVR.mean() if not opp_pool.empty else random.uniform(60,90)
        gf = max(0,int(np.random.normal((atk-60)/8,1)))
        ga = max(0,int(np.random.normal((oppatk-60)/8,1)))

        # 得点者・アシスト選出
        scorers=[]; assisters=[]
        for _ in range(gf):
            if not ses.starters: break
            s = random.choice(ses.starters)
            a = random.choice([x for x in ses.starters if x!=s] or [s])
            scorers.append(s); assisters.append(a)
            ses.senior.loc[ses.senior.Name==s,"Goals"] += 1
            ses.senior.loc[ses.senior.Name==a,"Assists"] += 1

        # 勝敗反映
        update_standings(ses.my_club, opponent, gf, ga)
        # 他クラブも同様にシミュ
        done={(ses.my_club,opponent)}
        for nat,divs in ses.leagues.items():
            for div, clubs in divs.items():
                pairs = clubs.copy()
                random.shuffle(pairs)
                for i in range(0,len(pairs),2):
                    if i+1>=len(pairs): break
                    h,a = pairs[i],pairs[i+1]
                    if (h,a) in done or (a,h) in done: continue
                    g1,g2 = random.randint(0,3), random.randint(0,3)
                    update_standings(h,a,g1,g2)
                    done.add((h,a))

        # ログ・SNS・財務
        add_match_log(ses.week, ses.my_club, opponent, gf, ga, scorers, assisters)
        ses.sns_posts.append(f"{ses.my_club} {gf}-{ga} {opponent}｜得点:{','.join(scorers) or 'なし'} / アシスト:{','.join(assisters) or 'なし'}")
        ses.sns_times.append(datetime.now())
        add_finance(ses.week, ticket=gf*15000+random.randint(5000,10000),
                    goods=ga*8000+random.randint(2000,6000),
                    salary=int(ses.senior.OVR.mean()*1000))

        # 成長 & 履歴
        ses.senior = apply_growth(ses.senior, ses.week)
        for _,r in ses.senior.iterrows():
            update_player_history(r.Name, r, ses.week)

        # 国際大会自動進行
        auto_intl_round()

        # 表示
        st.success(f"スコア：{gf}-{ga}")
        st.write(f"得点者：{' / '.join(scorers) or 'なし'}")
        st.write(f"アシスト：{' / '.join(assisters) or 'なし'}")
        ses.week += 1
        ses.auto_selected = False

        # シーズン終了チェック
        if ses.week > SEASON_WEEKS:
            st.success("シーズン終了！ 自動で次シーズンを開始します。")
            reset_season()
            st.experimental_rerun()

# --- 4) 順位表 & 各国ランキング統合 ---
with tabs[4]:
    st.markdown('<div class="section-box"><h3>順位表</h3></div>', unsafe_allow_html=True)
    nat_sel = st.selectbox("国を選択", list(ses.leagues.keys()), key="sel_nat")
    div_sel = st.selectbox("ディビジョンを選択", list(ses.leagues[nat_sel].keys()), key="sel_div")
    df_st = ses.standings.query("Nation==@nat_sel & Division==@div_sel")
    st.dataframe(style_table(sort_table(df_st), make_highlighter('Club',ses.my_club)), use_container_width=True)

    st.markdown('<div class="section-box"><h3>各国リーグランキング</h3></div>', unsafe_allow_html=True)
    df_all = pd.concat([ses.senior, ses.youth, ses.ai_players], ignore_index=True).fillna(0)
    for nat,divs in ses.leagues.items():
        st.markdown(f"### {nat}")
        for d in divs.keys():
            st.markdown(f"#### {d}")
            tbl = ses.standings.query("Nation==@nat & Division==@d")
            st.dataframe(style_table(sort_table(tbl), make_highlighter('Club',ses.my_club)), use_container_width=True)
            sub = df_all.query("Nation==@nat & Division==@d")
            topg=sub.nlargest(5,'Goals')[['Name','Pos','Goals','Club']]
            topa=sub.nlargest(5,'Assists')[['Name','Pos','Assists','Club']]
            st.markdown("🏅 得点王")
            st.dataframe(style_table(topg, make_highlighter('Club',ses.my_club)), use_container_width=True)
            st.markdown("🎯 アシスト王")
            st.dataframe(style_table(topa, make_highlighter('Club',ses.my_club)), use_container_width=True)
            best=[]
            for p,nm in [('GK',1),('DF',4),('MF',4),('FW',2)]:
                best.append(sub[sub.Pos==p].nlargest(nm,'OVR')[['Name','Pos','OVR','Club']])
            be11=pd.concat(best) if best else pd.DataFrame()
            st.markdown("⚽️ ベストイレブン")
            st.dataframe(style_table(be11, make_highlighter('Club',ses.my_club)), use_container_width=True)
            st.markdown("---")

# --- 5) スカウト / 移籍 ---
with tabs[5]:
    st.markdown('<div class="section-box"><h3>スカウト / 移籍</h3></div>', unsafe_allow_html=True)
    cat = st.radio("カテゴリー", ["シニア候補","ユース候補"], horizontal=True, key="scat")
    youth_flag = (cat=="ユース候補")
    st.markdown(f"補強推奨ポジション：{', '.join(suggest_positions(ses.youth if youth_flag else ses.senior)) or 'バランスOK'}")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("候補更新", key="btn_scout"):
            ses.scout_candidates = gen_scout_candidates(10, youth_flag)
    with c2:
        st.write(f"予算：{fmt_money(ses.budget)}")

    if ses.scout_candidates.empty:
        st.markdown("<div class='tab-info'>候補がいません。「候補更新」を押してください。</div>", unsafe_allow_html=True)
    else:
        for i,row in ses.scout_candidates.iterrows():
            st.markdown('<div class="scout-card">', unsafe_allow_html=True)
            st.markdown(f"**{row.Name}**｜{row.Nat}｜{row.Pos}｜OVR:{row.OVR}｜{fmt_money(row.Value)}<br>年齢:{row.Age}歳 / PlayStyle:{row.PlayStyle}", unsafe_allow_html=True)
            if row.Club=="Free":
                if st.button("契約", key=f"sign_{i}"):
                    dst = 'youth' if youth_flag else 'senior'
                    setattr(ses,dst, pd.concat([getattr(ses,dst), pd.DataFrame([row])], ignore_index=True))
                    ses.scout_candidates = ses.scout_candidates.drop(i).reset_index(drop=True)
                    st.success("獲得！")
            else:
                mode = st.selectbox("オファー種別", ["完全移籍","レンタル(OP付)"], key=f"mode_{i}")
                with st.form(f"form_{i}"):
                    if mode=="完全移籍":
                        wage=st.number_input("年俸(€)",0,int(row.OVR*180),key=f"wg_{i}")
                        fee =st.number_input("移籍金(€)",0,int(row.Value),key=f"fee_{i}")
                        ok=st.form_submit_button("送信")
                        if ok:
                            ok2,wd,fd = offer_result(row,wage,1,fee,ses.budget)
                            if ok2:
                                ses.budget -= fee
                                r2=row.copy(); r2.Club=ses.my_club
                                dst='youth' if youth_flag else 'senior'
                                setattr(ses,dst, pd.concat([getattr(ses,dst),pd.DataFrame([r2])],ignore_index=True))
                                ses.scout_candidates=ses.scout_candidates.drop(i).reset_index(drop=True)
                                st.success("移籍！")
                            else:
                                st.error(f"拒否：年俸{fmt_money(wd)}/移籍金{fmt_money(fd)}")
                    else:
                        weeks=st.slider("期間(節)",1,8,4,key=f"wk_{i}")
                        fee_r=st.number_input("レンタル料(€)",0,int(row.Value*0.12),key=f"rf_{i}")
                        opt =st.number_input("買取OP(€)",0,int(row.Value*1.2),key=f"op_{i}")
                        ok2=st.form_submit_button("送信")
                        if ok2:
                            ok3,dmd = rental_result(row,weeks,fee_r,ses.budget)
                            if ok3:
                                ses.budget-=fee_r
                                r2=row.copy()
                                r2.Club=ses.my_club; r2.RentalFrom=row.Club; r2.RentalUntil=ses.week+weeks; r2.OptionFee=opt; r2.Status=f"レンタル中({weeks}節)"
                                dst='youth' if youth_flag else 'senior'
                                setattr(ses,dst,pd.concat([getattr(ses,dst),pd.DataFrame([r2])],ignore_index=True))
                                ses.scout_candidates=ses.scout_candidates.drop(i).reset_index(drop=True)
                                st.success("レンタル！")
                            else:
                                st.error(f"拒否：目安{fmt_money(dmd)}")
            st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Part 9 / 12  --- レンタル管理 / SNS / 財務レポート / 年間表彰
# =========================

# --- 6) レンタル管理 ---
with tabs[6]:
    st.markdown('<div class="section-box"><h3>レンタル管理</h3></div>', unsafe_allow_html=True)
    handle_rental_expirations()
    df_r = pd.concat([ses.senior, ses.youth], ignore_index=True)
    df_r = df_r[df_r.Status.str.contains("レンタル中", na=False)][
        ['Name','Pos','OVR','RentalFrom','RentalUntil','OptionFee','Status']
    ]
    if df_r.empty:
        st.markdown("<div class='tab-info'>レンタル中の選手はいません。</div>", unsafe_allow_html=True)
    else:
        st.dataframe(style_table(df_r), use_container_width=True)
        for _, r in df_r.iterrows():
            nm = r['Name']
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"買取（{nm}）", key=f"buy_{nm}"):
                    opt = int(r['OptionFee'] or 0)
                    if ses.budget >= opt:
                        for dfname in ['senior','youth']:
                            df = getattr(ses, dfname)
                            idx = df.index[df['Name']==nm]
                            if len(idx)>0:
                                df.loc[idx, ['Status','RentalUntil','RentalFrom','OptionFee']] = ["通常", np.nan, None, None]
                                setattr(ses, dfname, df)
                        ses.budget -= opt
                        st.success("買取成立！")
                    else:
                        st.error("予算不足です。")
            with c2:
                if st.button(f"即時返却（{nm}）", key=f"ret_{nm}"):
                    origin = r['RentalFrom']
                    for dfname in ['senior','youth']:
                        df = getattr(ses, dfname)
                        idx = df.index[df['Name']==nm]
                        if len(idx)>0:
                            bak = df.loc[idx[0]].copy()
                            df = df.drop(idx)
                            setattr(ses, dfname, df)
                            break
                    bak['Club'] = origin
                    bak[['Status','RentalUntil','RentalFrom','OptionFee']] = ["通常", np.nan, None, None]
                    ses.ai_players = pd.concat([ses.ai_players, pd.DataFrame([bak])], ignore_index=True)
                    st.info("返却しました。")

# --- 7) SNS ---
with tabs[7]:
    st.markdown('<div class="section-box"><h3>SNS / ファンフィード</h3></div>', unsafe_allow_html=True)
    if ses.sns_posts:
        for t,msg in zip(reversed(ses.sns_times), reversed(ses.sns_posts)):
            st.write(f"{t.strftime('%m/%d %H:%M')} – {msg}")
    else:
        st.markdown("<div class='tab-info'>投稿はまだありません。</div>", unsafe_allow_html=True)

# --- 8) 財務レポート ---
with tabs[8]:
    st.markdown('<div class="section-box"><h3>財務レポート</h3></div>', unsafe_allow_html=True)
    df_fin = pd.DataFrame(ses.finance_log)
    if df_fin.empty:
        st.markdown("<div class='tab-info'>財務データがありません。</div>", unsafe_allow_html=True)
    else:
        df_fin_j = df_fin.rename(columns={'week':'節'})
        df_fin_j['総収入'] = df_fin_j['チケット収入'] + df_fin_j['グッズ収入']
        df_fin_j['収支']   = df_fin_j['総収入'] - df_fin_j['人件費']
        fig, ax = plt.subplots()
        ax.plot(df_fin_j['節'], df_fin_j['総収入'], marker='o', label='総収入')
        ax.plot(df_fin_j['節'], df_fin_j['人件費'], marker='o', label='人件費')
        ax.plot(df_fin_j['節'], df_fin_j['収支'],   marker='o', label='収支')
        ax.set_xlabel("節"); ax.set_ylabel("金額(€)")
        ax.legend(frameon=False, bbox_to_anchor=(1,1))
        make_transparent(ax)
        st.pyplot(fig)
        st.dataframe(style_table(df_fin_j), use_container_width=True)

# --- 9) 年間表彰 ---
with tabs[9]:
    st.markdown('<div class="section-box"><h3>年間表彰</h3></div>', unsafe_allow_html=True)
    df_my = pd.concat([ses.senior, ses.youth], ignore_index=True).fillna(0)
    top_g = df_my.nlargest(5,'Goals')[['Name','Pos','Goals','Assists','OVR']]
    top_a = df_my.nlargest(5,'Assists')[['Name','Pos','Assists','Goals','OVR']]
    st.markdown("**🏅 自クラブ 得点王 TOP5**")
    st.dataframe(style_table(top_g), use_container_width=True)
    st.markdown("**🎯 自クラブ アシスト王 TOP5**")
    st.dataframe(style_table(top_a), use_container_width=True)
    best=[]
    for p,need in [('GK',1),('DF',4),('MF',4),('FW',2)]:
        cand = df_my[df_my['Pos']==p].copy()
        cand['Score'] = cand['Goals']*2 + cand['Assists'] + cand['OVR']/50
        best.append(cand.nlargest(need,'Score')[['Name','Pos','Goals','Assists','OVR']])
    best11 = pd.concat(best) if best else pd.DataFrame()
    st.markdown("**⚽️ 自クラブ ベストイレブン**")
    if best11.empty:
        st.markdown("<div class='tab-info'>データがありません。</div>", unsafe_allow_html=True)
    else:
        st.dataframe(style_table(best11), use_container_width=True)

# =========================
# Part 10 / 12  --- 国際大会タブ
# =========================
with tabs[10]:
    st.markdown('<div class="section-box"><h3>国際大会</h3></div>', unsafe_allow_html=True)

    # 未開催時メッセージ
    if not ses.intl_tournament or not ses.intl_tournament.get("results"):
        st.markdown("<div class='tab-info'>国際大会は未開催です。試合を進めると自動で進行します。</div>", unsafe_allow_html=True)
    else:
        # トーナメント結果表示
        st.markdown("### 📊 トーナメント結果")
        rounds = []
        # 16→8→4→2→1 など、4試合ずつ区切って表示
        res = ses.intl_tournament["results"]
        for i in range(0, len(res), 4):
            rounds.append(res[i:i+4])
        for idx, rd in enumerate(rounds, start=1):
            st.markdown(f"#### Round {idx}")
            df_rd = pd.DataFrame([{
                "Home":c1,"G1":g1,"Away":c2,"G2":g2,"PK":pk,"勝者":win
            } for (c1,g1,c2,g2,pk,win) in rd])
            st.dataframe(style_table(df_rd, make_highlighter("勝者", ses.my_club)), use_container_width=True)

        # 優勝表示
        if ses.intl_tournament.get("finished") and len(ses.intl_tournament.get("clubs",[]))==1:
            champ = ses.intl_tournament["clubs"][0]
            if champ == ses.my_club:
                st.markdown(f"<span style='background:#f7df70;color:#202b41;font-weight:bold'>優勝: {champ}</span>", unsafe_allow_html=True)
            else:
                st.success(f"優勝: {champ}")

        st.markdown("---")
        # 個人成績ランキング
        st.markdown("### 🏆 個人成績ランキング")
        df_int = pd.DataFrame.from_dict(ses.intl_player_stats, orient='index').reset_index().rename(columns={"index":"Name"})
        if df_int.empty:
            st.markdown("<div class='tab-info'>個人成績データがまだありません。</div>", unsafe_allow_html=True)
        else:
            # 得点ランキング
            topg = df_int.nlargest(10, "G")[["Name","Pos","G","A","Club"]]
            st.markdown("**得点ランキング TOP10**")
            st.dataframe(style_table(topg, make_highlighter("Club", ses.my_club)), use_container_width=True)
            # アシストランキング
            topa = df_int.nlargest(10, "A")[["Name","Pos","A","G","Club"]]
            st.markdown("**アシストランキング TOP10**")
            st.dataframe(style_table(topa, make_highlighter("Club", ses.my_club)), use_container_width=True)
            # 国際大会ベストイレブン
            best=[]
            for p,need in [("GK",1),("DF",4),("MF",4),("FW",2)]:
                cand = df_int[df_int["Pos"]==p].copy()
                cand["Score"] = cand["G"]*2 + cand["A"]
                best.append(cand.nlargest(need, "Score")[["Name","Pos","G","A","Club"]])
            bi = pd.concat(best) if best else pd.DataFrame()
            st.markdown("**⚽️ 国際大会ベストイレブン**")
            st.dataframe(style_table(bi, make_highlighter("Club", ses.my_club)), use_container_width=True)

# =========================
# Part 11 / 12  --- クラブ設定 & シーズン管理
# =========================
with tabs[11]:
    st.markdown('<div class="section-box"><h3>クラブ設定</h3></div>', unsafe_allow_html=True)
    st.write(f"現在のクラブ名: **{ses.my_club}**   予算: **{fmt_money(ses.budget)}**")

    # クラブ名変更
    new_name = st.text_input("自クラブ名を変更", value=ses.my_club, key="rename_input")
    if st.button("変更", key="rename_btn"):
        if new_name and new_name != ses.my_club:
            old = ses.my_club
            # standings
            ses.standings.loc[ses.standings.Club==old, "Club"] = new_name
            # leagues
            nat, div = ses.club_map[old]
            lst = ses.leagues[nat][div]
            idx = lst.index(old)
            lst[idx] = new_name
            ses.leagues[nat][div] = lst
            # players
            for dfname in ["senior","youth"]:
                df = getattr(ses, dfname)
                df.loc[df.Club==old, "Club"] = new_name
                setattr(ses, dfname, df)
            ses.my_club = new_name
            ses.club_map = build_club_map(ses.standings)
            st.success("クラブ名を変更しました。")
            st.experimental_rerun()
        else:
            st.error("新しい名前を入力してください。")

    st.markdown("---")
    # 手動シーズンリセット
    if st.button("シーズン手動リセット", key="reset_season_btn"):
        reset_season()
        st.success("シーズンをリセットしました。")
        st.experimental_rerun()

    # 完全初期化（デバッグ用）
    with st.expander("完全初期化 (全データ再生成)"):
        if st.button("再生成実行", key="full_init_btn"):
            st.session_state.ses = init_session()
            st.success("すべて初期化しました。")
            st.experimental_rerun()

