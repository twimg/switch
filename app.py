# =========================
# Part 1 / 8
# =========================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# ---------- ページ設定 ----------
st.set_page_config(page_title="Club Strive Manager", layout="wide")
random.seed(42)
np.random.seed(42)

# ---------- CSS ----------
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }
h1,h2,h3,h4,h5,h6, .stMarkdown, .css-1offfwp, .css-10trblm { color:#ffffff!important; }
[data-testid="stMarkdownContainer"] * { color:#ffffff!important; }
strong { color:#eaf6ff!important; }
label, .stRadio > label, .stSelectbox label { color:#bfeaff!important; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }
.stButton>button { background:#27e3b9!important; color:#202b41!important; font-weight:bold; border-radius:10px; margin:6px 0; }
.stButton>button:disabled { background:#555!important; color:#999!important; }
.player-card { background:#fff; color:#132346; border-radius:12px; padding:10px; margin:8px; min-width:140px; max-width:160px; box-shadow:0 0 8px #0003; }
.detail-popup { position:absolute; top:100%; left:50%; transform:translateX(-50%); background:rgba(36,54,84,0.9); color:#fff; padding:12px; border-radius:10px; width:220px; box-shadow:0 0 10px #000a; backdrop-filter:blur(8px); z-index:10; }
.mobile-table, .mobile-scroll { overflow-x:auto; white-space:nowrap; }
.mobile-table th, .mobile-table td { padding:4px 10px; font-size:15px; border-bottom:1px solid #243255; }
.mobile-scroll .player-card { display:inline-block; vertical-align:top; }
.stage-label { background:#222b3c88; color:#fff; padding:6px 12px; border-radius:8px; display:inline-block; margin-bottom:8px; }
.red-message { color:#f55!important; }
.stDataFrame { background:rgba(20,30,50,0.7)!important; color:#fff!important; }
.dataframe td, .dataframe th { color:#fff!important; }
.agent-card { background:#192841; color:#eaf6ff; padding:8px; border-radius:8px; margin:4px; display:inline-block; width:160px; vertical-align:top; }
</style>
""", unsafe_allow_html=True)

st.title("Club Strive")

# ---------- 定数 ----------
SEASON_WEEKS = 14
MY_CLUB_DEFAULT = "Signature Team"  # 自クラブ名
ABILITY_KEYS = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']

# ポジションソート用
def sort_by_pos(df, reverse=False):
    order = ['GK','DF','MF','FW']
    if reverse: order = order[::-1]
    mapper = {p:i for i,p in enumerate(order)}
    return df.sort_values(by='Pos', key=lambda s: s.map(mapper)).reset_index(drop=True)

# DataFrameで自クラブ行を薄ハイライト
def make_highlighter(col, myclub):
    def _hl(row):
        return ['background-color:#f7df7033' if row[col]==myclub else '' for _ in row]
    return _hl

# PlayStyleの色付け（白文字固定）
def style_playstyle(series):
    return ['color:#eaf6ff;background-color:rgba(0,0,0,0)' for _ in series]

# グラフ透過
def make_transparent(ax):
    ax.set_facecolor("none")
    if ax.figure: ax.figure.patch.set_alpha(0)

# レーダーチャート
def radar_chart(values, labels):
    ang = np.linspace(0, 2*np.pi, len(labels)+1)
    vals = values + values[:1]
    fig, ax = plt.subplots(figsize=(3.2,3.2), subplot_kw=dict(polar=True))
    ax.plot(ang, vals, linewidth=2)
    ax.fill(ang, vals, alpha=0.25)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(labels, color="#eaf6ff", fontsize=9)
    ax.set_yticklabels([])
    ax.grid(color="#eaf6ff55")
    make_transparent(ax)
    return fig

# =========================
# Part 2 / 8
# =========================

# ---------- 名前プール（各国：名30・姓30／予備GEN30） ----------
NAME_POOLS = {
    'ENG': {
        'given': ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
                  "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin",
                  "Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"],
        'surname': ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
                    "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark",
                    "Harris","Baker","Moore","Wright","Hill","Cooper","Ward","King","Parker","Campbell"]
    },
    'GER': {
        'given': ["Lukas","Leon","Paul","Jonas","Felix","Maximilian","Moritz","Niklas","Noah","Elias",
                  "Tim","Finn","Jan","Lennard","Fabian","Philipp","Tobias","David","Simon","Benedikt",
                  "Julius","Erik","Ben","Matthias","Robin","Kevin","Marco","Stefan","Dominik","Daniel"],
        'surname': ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Schulz","Hoffmann",
                    "Koch","Richter","Klein","Wolf","Schröder","Neumann","Schwarz","Zimmermann","Braun","Hofmann",
                    "Krüger","Hartmann","Lange","Werner","Schmitt","Friedrich","Keller","Günther","Kaiser","Vogel"]
    },
    'FRA': {
        'given': ["Lucas","Hugo","Louis","Gabriel","Arthur","Jules","Thomas","Raphaël","Nathan","Léo",
                  "Maxime","Alexandre","Quentin","Antoine","Paul","Nicolas","Baptiste","Mathis","Clément","Romain",
                  "Florian","Julien","Théo","Enzo","Damien","Kevin","Yann","Adrien","Guillaume","Victor"],
        'surname': ["Martin","Bernard","Dubois","Thomas","Robert","Richard","Petit","Durand","Leroy","Moreau",
                    "Simon","Laurent","Lefebvre","Michel","Garcia","David","Bertrand","Roux","Vincent","Fournier",
                    "Morel","Girard","Andre","Lefevre","Mercier","Dupont","Lambert","Bonnet","Francois","Martinez"]
    },
    'ESP': {
        'given': ["Alejandro","Hugo","Daniel","Pablo","Adrián","David","Javier","Álvaro","Diego","Mario",
                  "Sergio","Carlos","Juan","Miguel","Rafael","Rubén","Luis","Ignacio","Antonio","Fernando",
                  "Iván","Raúl","Jorge","Marcos","Óscar","Ruben","Gonzalo","Víctor","Iker","Andrés"],
        'surname': ["García","Martínez","López","Sánchez","Pérez","Gómez","Fernández","Díaz","Hernández","Alvarez",
                    "Jiménez","Moreno","Muñoz","Alonso","Gutiérrez","Romero","Navarro","Torres","Domínguez","Vázquez",
                    "Ramos","Gil","Ramírez","Serrano","Blanco","Molina","Suárez","Ortega","Delgado","Castro"]
    },
    'ITA': {
        'given': ["Lorenzo","Alessandro","Leonardo","Matteo","Francesco","Andrea","Gabriele","Riccardo","Tommaso","Edoardo",
                  "Federico","Giuseppe","Antonio","Marco","Nicola","Davide","Simone","Daniele","Stefano","Salvatore",
                  "Michele","Roberto","Alberto","Paolo","Carlo","Giorgio","Filippo","Vincenzo","Pietro","Raffaele"],
        'surname': ["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco",
                    "Bruno","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Barbieri",
                    "Moretti","Fontana","Santoro","Mariani","Rinaldi","Caruso","Ferrara","Fabbri","Bianco","Martini"]
    },
    'NED': {
        'given': ["Daan","Sem","Lucas","Levi","Finn","Luuk","Milan","Jesse","Noah","Thijs",
                  "Lars","Tom","Sam","Ruben","Julian","Sven","Timo","Benjamin","Bram","Mees",
                  "Niels","Jasper","Tim","Max","Gijs","Joep","Wouter","Pim","Koen","Floris"],
        'surname': ["de Jong","Jansen","de Vries","van den Berg","van Dijk","Bakker","Janssen","Visser","Smit","Meijer",
                    "de Boer","Mulder","Bos","Vos","Peters","Hendriks","van der Meer","van Beek","van Leeuwen","Dekker",
                    "Brouwer","de Wit","Schouten","Kramer","Post","van Dam","Hoekstra","Maas","Vermeulen","Kok"]
    },
    'BRA': {
        'given': ["Gabriel","Lucas","Matheus","Pedro","Guilherme","Rafael","João","Bruno","Felipe","Gustavo",
                  "Diego","Thiago","André","Rodrigo","Daniel","Vitor","Caio","Eduardo","Henrique","Fernando",
                  "Leonardo","Igor","Marcelo","Luiz","Alex","Rogério","Ronan","Samuel","Wesley","Miguel"],
        'surname': ["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Alves","Pereira","Lima","Gomes",
                    "Costa","Ribeiro","Carvalho","Almeida","Lopes","Soares","Fernandes","Vieira","Barbosa","Rocha",
                    "Dias","Nunes","Cardoso","Teixeira","Moreira","Correia","Cruz","Batista","Campos","Araújo"]
    },
    'POR': {
        'given': ["João","Miguel","Tiago","Diogo","Rui","André","Pedro","Gonçalo","Bruno","Francisco",
                  "Henrique","Ricardo","Hugo","Luís","Filipe","Marco","Sérgio","Nuno","Paulo","Vítor",
                  "Daniel","Alexandre","Eduardo","Carlos","António","Mário","Jorge","Fernando","Cristiano","Rafael"],
        'surname': ["Silva","Santos","Ferreira","Pereira","Oliveira","Costa","Rodrigues","Martins","Jesus","Sousa",
                    "Fernandes","Gonçalves","Almeida","Ribeiro","Pinto","Carvalho","Teixeira","Moreira","Correia","Mendes",
                    "Nunes","Vieira","Lopes","Cardoso","Castro","Araújo","Dias","Matos","Barros","Fonseca"]
    },
    'BEL': {
        'given': ["Liam","Noah","Lucas","Arthur","Louis","Milan","Jules","Nathan","Thomas","Maxime",
                  "Ethan","Adam","Hugo","Victor","Matteo","Mohamed","Benjamin","Julien","Théo","Antoine",
                  "Rayan","Alexis","Enzo","Baptiste","Quentin","Gabriel","Samuel","Mathis","Amine","Olivier"],
        'surname': ["Peeters","Janssens","Maes","Jacobs","Mertens","Willems","Claes","Goossens","Wouters","De Smet",
                    "Dubois","Lambert","Dupont","Declercq","De Clercq","Martens","Michiels","Smets","Aerts","Vermeulen",
                    "Lemmens","Leclercq","Simons","Gielen","Theunissen","Hubert","Henry","Lefevre","Renard","Desmet"]
    },
    'TUR': {
        'given': ["Mehmet","Ahmet","Mustafa","Ali","Hüseyin","İbrahim","İsmail","Osman","Yusuf","Murat",
                  "Ömer","Halil","Mahmut","Fatih","Ramazan","Emre","Serkan","Hasan","Cem","Onur",
                  "Eren","Burak","Uğur","Can","Barış","Kerem","Gökhan","Yasin","Kaan","Furkan"],
        'surname': ["Yılmaz","Kaya","Demir","Şahin","Çelik","Yıldız","Yıldırım","Öztürk","Aydın","Özdemir",
                    "Arslan","Doğan","Kılıç","Aslan","Çetin","Kara","Koç","Kurt","Özkan","Polat",
                    "Güneş","Bozkurt","Aksoy","Erdoğan","Tekin","Özer","Işık","Uçar","Bulut","Sezer"]
    },
    'ARG': {
        'given': ["Santiago","Mateo","Thiago","Juan","Lucas","Benjamín","Tomás","Joaquín","Martín","Agustín",
                  "Francisco","Alejandro","Nicolás","Diego","Matías","Facundo","Bruno","Emiliano","Gabriel","Ramiro",
                  "Gonzalo","Lautaro","Hernán","Carlos","Pablo","Ezequiel","Maximiliano","Iván","Rodrigo","Leandro"],
        'surname': ["González","Rodríguez","Gómez","Fernández","López","Martínez","Díaz","Pérez","Sánchez","Romero",
                    "Sosa","Álvarez","Torres","Ruiz","Ramírez","Flores","Acosta","Benítez","Medina","Herrera",
                    "Aguirre","Ponce","Castro","Rojas","Molina","Ortiz","Silva","Suárez","Morales","Peralta"]
    },
    'URU': {
        'given': ["Matías","Bruno","Santiago","Nicolás","Juan","Martín","Agustín","Federico","Thiago","Ignacio",
                  "Emiliano","Lucas","Rodrigo","Pablo","Gonzalo","Facundo","Gabriel","Diego","Maximiliano","Sebastián",
                  "Franco","Valentín","Lautaro","Ramiro","Leandro","Carlos","Joaquín","Hernán","Cristian","Ezequiel"],
        'surname': ["Pérez","González","Rodríguez","Fernández","López","Martínez","Sánchez","Silva","Álvarez","Romero",
                    "Ruiz","Vázquez","Acosta","Medina","Castro","Ortiz","Méndez","Arias","Pereira","Perdomo",
                    "Cabrera","Suárez","Núñez","Herrera","Cardozo","Ramos","Figueira","Bentancur","Godín","Forlán"]
    },
    'COL': {
        'given': ["Juan","Andrés","Carlos","Santiago","Sebastián","Felipe","David","Daniel","Mateo","Julián",
                  "Camilo","Miguel","Nicolás","Jorge","Diego","Esteban","Luis","Gabriel","Tomás","Ricardo",
                  "Fernando","Oscar","Iván","Hernán","Víctor","Rafael","Mauricio","Jaime","César","Eduardo"],
        'surname': ["García","Rodríguez","Martínez","Gómez","López","Hernández","Díaz","Pérez","Sánchez","Ramírez",
                    "Romero","Vargas","Moreno","Jiménez","Rojas","Gutiérrez","Castro","Ortiz","Guerrero","Suárez",
                    "Torres","Navarro","Reyes","Cortés","Mejía","Salazar","Patiño","Mendoza","Valencia","Hoyos"]
    },
    'USA': {
        'given': ["James","John","Robert","Michael","William","David","Richard","Joseph","Thomas","Charles",
                  "Christopher","Daniel","Matthew","Anthony","Mark","Donald","Steven","Paul","Andrew","Joshua",
                  "Kenneth","Kevin","Brian","George","Timothy","Ronald","Edward","Jason","Jeffrey","Ryan"],
        'surname': ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
                    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
                    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson"]
    },
    'MEX': {
        'given': ["José","Juan","Luis","Carlos","Jorge","Miguel","Jesús","Francisco","David","Antonio",
                  "Alejandro","Ricardo","Roberto","Fernando","Manuel","Rafael","Eduardo","Sergio","Andrés","Héctor",
                  "Arturo","Adrián","Víctor","César","Omar","Diego","Iván","Raúl","Hugo","Marco"],
        'surname': ["Hernández","García","Martínez","López","González","Pérez","Rodríguez","Sánchez","Ramírez","Cruz",
                    "Flores","Gómez","Vargas","Reyes","Morales","Jiménez","Díaz","Torres","Ruiz","Mendoza",
                    "Ortega","Aguilar","Castillo","Chávez","Ramos","Guerrero","Muñoz","Velázquez","Domínguez","Navarro"]
    },
    'SAU': {
        'given': ["Abdullah","Mohammed","Ahmed","Ali","Omar","Hassan","Fahad","Khaled","Ibrahim","Yousef",
                  "Saad","Majed","Nasser","Sultan","Turki","Saleh","Bandar","Hamad","Mansour","Talal",
                  "Rashed","Abdulaziz","Faisal","Mazid","Abdulrahman","Saeed","Yasir","Anas","Ziyad","Bader"],
        'surname': ["Al-Saud","Al-Qahtani","Al-Zahrani","Al-Ghamdi","Al-Harbi","Al-Anazi","Al-Shammari","Al-Otaibi","Al-Mutairi","Al-Dosari",
                    "Al-Johani","Al-Shehri","Al-Malki","Al-Subaie","Al-Enezi","Al-Faraj","Al-Nasser","Al-Rashid","Al-Salem","Al-Hazza",
                    "Al-Qahtan","Al-Harthy","Al-Fahad","Al-Turki","Al-Sayf","Al-Naimi","Al-Farhan","Al-Khalifa","Al-Hassan","Al-Amri"]
    },
    'NGA': {
        'given': ["Emeka","Chinedu","Ifeanyi","Kelechi","Olumide","Tunde","Segun","Ibrahim","Ahmed","Abdul",
                  "Gbenga","Oluwaseun","Samuel","Daniel","Michael","Victor","Peter","Joseph","Paul","Henry",
                  "Kelvin","Collins","Francis","Simeon","Uche","Onyekachi","Chukwuemeka","Ayodele","Kingsley","Sunday"],
        'surname': ["Okafor","Ogunleye","Adewale","Okeke","Eze","Ibrahim","Abubakar","Ojo","Ogedegbe","Nwosu",
                    "Balogun","Yakubu","Osei","Oparaji","Adeyemi","Lawal","Afolayan","Uzoho","Oshodi","Ogbu",
                    "Awolowo","Omoregie","Odiaka","Okorie","Ezenwa","Okonkwo","Oladipo","Olowo","Effiong","Udom"]
    },
    'MAR': {
        'given': ["Youssef","Mohamed","Achraf","Hassan","Oussama","Mehdi","Ayoub","Nabil","Amine","Anass",
                  "Soufiane","Rachid","Hamza","Tarik","Karim","Zakaria","Yassine","Abdelaziz","Badr","Ismail",
                  "Said","Ilias","Walid","Omar","Aziz","Ibrahim","Reda","Khalid","Imad","Driss"],
        'surname': ["El Fassi","Bennani","El Amrani","Bouzid","El Idrissi","Chakiri","Benali","Azzouzi","El Ouahabi","Ait Lahcen",
                    "Laaroussi","Azoulay","Bouziane","Othmani","Ouakrim","Haddadi","Tazi","Benchekroun","Bouazza","Hassani",
                    "Kabbaj","Saidi","Cherkaoui","El Hajj","Belkadi","El Mansouri","El Hajji","Tahar","El Khatib","Fassi"]
    },
    'KOR': {
        'given': ["Minjun","Jisoo","Seojun","Jihoon","Yuna","Jimin","Hyeon","Seungmin","Jiwon","Yoonsu",
                  "Taeyang","Hyunjin","Donghyun","Sungmin","Jaemin","Jaeho","Minseok","Yongjun","Dohyun","Suho",
                  "Jongin","Hoseok","Jisung","Chanwoo","Minho","Yongho","Junseo","Juwon","Joon","Hyunwoo"],
        'surname': ["Kim","Lee","Park","Choi","Jung","Kang","Cho","Yoon","Jang","Im",
                    "Han","Oh","Seo","Shin","Kwon","Hwang","Ahn","Song","Jeon","Hong",
                    "Yang","Ko","Moon","Son","Baek","Yoo","Nam","Sim","Ha","No"]
    },
    'AUS': {
        'given': ["Jack","Oliver","William","Noah","James","Lucas","Thomas","Liam","Alexander","Henry",
                  "Ethan","Charlie","Samuel","Harrison","Levi","Oscar","Mason","Hunter","Leo","Archie",
                  "Logan","Cooper","Isaac","Daniel","Lachlan","Jackson","Samuel","Riley","Max","Harry"],
        'surname': ["Smith","Jones","Williams","Brown","Wilson","Taylor","Johnson","White","Martin","Anderson",
                    "Thompson","Nguyen","Harris","Moore","Jackson","Lee","Clark","Walker","Hall","Allen",
                    "Young","King","Wright","Scott","Green","Baker","Adams","Nelson","Mitchell","Roberts"]
    },
    'GEN': {  # どの国でも使える予備
        'given': ["Alex","Chris","Pat","Sam","Taylor","Jordan","Casey","Jamie","Robin","Drew",
                  "Cameron","Morgan","Lee","Riley","Skyler","Avery","Reese","Kai","Quinn","Rowan",
                  "River","Max","Jules","Emerson","Shannon","Logan","Peyton","Harley","Eli","Ash"],
        'surname': ["Gray","Reed","West","Stone","Brooks","Price","Lane","Cole","Fox","Grant",
                    "Blair","Page","Ford","Ray","Dale","Snow","Wells","Parks","Lake","North",
                    "Cross","Fields","Moss","Banks","Shaw","Wade","Dean","Miles","Pope","Frost"]
    }
}

# ---------- プレースタイル & 成長タイプ ----------
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

# ---------- 国別特徴（能力バイアス・出やすいスタイル/成長タイプ） ----------
NATION_TRAITS_DEFAULT = {'bias':{}, 'styles':PLAY_STYLE_POOL, 'growth':GROWTH_TYPES_POOL}

NATION_TRAITS = {
    'ENG': {'bias':{'Phy':2,'Men':2}, 'styles':["空中戦の鬼","メンタルリーダー","職人","チーム至上主義","勝負師"], 'growth':["標準型","安定型","晩成型","終盤爆発型"]},
    'GER': {'bias':{'Phy':3,'Sta':2,'Men':1}, 'styles':["配給型CB","タックルマスター","メンタルリーダー","頭脳派","職人"], 'growth':["標準型","晩成型","超晩成型","安定型"]},
    'FRA': {'bias':{'Tec':2,'Spd':2}, 'styles':["トリックスター","メディア映え型","チャンスメーカー","ジョーカー","俊足ドリブラー"], 'growth':["超早熟型","早熟型","標準型","一発屋型"]},
    'ESP': {'bias':{'Tec':3,'Pas':3}, 'styles':["チャンスメーカー","王様タイプ","トリックスター","フリーキックスペシャリスト","頭脳派"], 'growth':["早熟型","標準型","晩成型","終盤爆発型"]},
    'ITA': {'bias':{'Def':3,'Men':2}, 'styles':["スイーパーリーダー","タックルマスター","影の支配者","王様タイプ","職人"], 'growth':["標準型","晩成型","超晩成型","安定型"]},
    'NED': {'bias':{'Pas':2,'Tec':2}, 'styles':["バランサー","配給型CB","チャンスメーカー","クラッチプレイヤー","トリックスター"], 'growth':["標準型","早熟型","終盤爆発型","一発屋型"]},
    'BRA': {'bias':{'Tec':4,'Sht':2,'Spd':2}, 'styles':["トリックスター","チャンスメーカー","ジョーカー","俊足ドリブラー","メディア映え型"], 'growth':["超早熟型","早熟型","標準型","スペ体質"]},
    'POR': {'bias':{'Tec':3,'Pas':2}, 'styles':["チャンスメーカー","フリーキックスペシャリスト","職人","頭脳派","王様タイプ"], 'growth':["標準型","晩成型","安定型","終盤爆発型"]},
    'BEL': {'bias':{'Pas':2,'Men':1}, 'styles':["バランサー","メンタルリーダー","配給型CB","クラッチプレイヤー","職人"], 'growth':["標準型","安定型","早熟型","晩成型"]},
    'TUR': {'bias':{'Pow':3,'Men':2}, 'styles':["感情型","爆発型","タックルマスター","勝負師","影の支配者"], 'growth':["一発屋型","スペ体質","標準型","晩成型"]},
    'ARG': {'bias':{'Tec':3,'Men':2}, 'styles':["王様タイプ","トリックスター","勝負師","メディア映え型","クラッチプレイヤー"], 'growth':["早熟型","標準型","晩成型","終盤爆発型"]},
    'URU': {'bias':{'Men':3,'Pow':2}, 'styles':["勝負師","空中戦の鬼","タックルマスター","影の支配者","チーム至上主義"], 'growth':["晩成型","超晩成型","安定型","標準型"]},
    'COL': {'bias':{'Spd':2,'Tec':2}, 'styles':["俊足ドリブラー","トリックスター","ジョーカー","チャンスメーカー","爆発型"], 'growth':["一発屋型","標準型","早熟型","終盤爆発型"]},
    'USA': {'bias':{'Phy':2,'Sta':2}, 'styles':["バランサー","配給型CB","メンタルリーダー","クラッチプレイヤー","職人"], 'growth':["標準型","安定型","早熟型","晩成型"]},
    'MEX': {'bias':{'Tec':2,'Sht':2}, 'styles':["フリーキックスペシャリスト","チャンスメーカー","ジョーカー","感情型","爆発型"], 'growth':["早熟型","標準型","一発屋型","終盤爆発型"]},
    'SAU': {'bias':{'Men':2,'Sta':1}, 'styles':["メンタルリーダー","影の支配者","王様タイプ","職人","バランサー"], 'growth':["標準型","晩成型","安定型","スペ体質"]},
    'NGA': {'bias':{'Spd':3,'Phy':3}, 'styles':["俊足ドリブラー","空中戦の鬼","爆発型","感情型","タックルマスター"], 'growth':["一発屋型","標準型","終盤爆発型","スペ体質"]},
    'MAR': {'bias':{'Tec':2,'Men':2}, 'styles':["トリックスター","フリーキックスペシャリスト","影の支配者","チャンスメーカー","王様タイプ"], 'growth':["早熟型","標準型","晩成型","安定型"]},
    'KOR': {'bias':{'Sta':3,'Men':2}, 'styles':["チーム至上主義","メンタルリーダー","バランサー","配給型CB","勝負師"], 'growth':["標準型","晩成型","安定型","終盤爆発型"]},
    'AUS': {'bias':{'Phy':2,'Pow':2}, 'styles':["空中戦の鬼","配給型CB","バランサー","クラッチプレイヤー","職人"], 'growth':["標準型","安定型","早熟型","晩成型"]}
}

# ---------- 各種ユーティリティ ----------
def pick_style_pool(nat):
    t = NATION_TRAITS.get(nat, NATION_TRAITS_DEFAULT)
    base = t['styles'][:]
    if len(base) < 6:
        base += [x for x in PLAY_STYLE_POOL if x not in base]
    random.shuffle(base)
    return base

def pick_growth_pool(nat):
    t = NATION_TRAITS.get(nat, NATION_TRAITS_DEFAULT)
    base = t['growth'][:]
    if len(base) < 4:
        base += [x for x in GROWTH_TYPES_POOL if x not in base]
    random.shuffle(base)
    return base

def apply_bias(stats:dict, nat:str):
    bias = NATION_TRAITS.get(nat, NATION_TRAITS_DEFAULT)['bias']
    for k,v in bias.items():
        if k in stats:
            stats[k] = int(max(30, min(99, stats[k] + random.randint(v//2, v))))
    return stats

def normalize_value(v:int)->int:
    if v >= 1000:
        return (v // 1000) * 1000
    else:
        return v - (v % 5)

def suggest_positions(df):
    target = {'GK':2,'DF':8,'MF':8,'FW':4}
    cnt = df['Pos'].value_counts()
    need = []
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
    elif gtype == "一発屋型":
        base = 2.0 if random.random()<0.08 else -0.5
    elif gtype == "スペ体質":
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

def gen_unique_name(nat, used:set):
    pool = NAME_POOLS.get(nat, NAME_POOLS['GEN'])
    while True:
        first = random.choice(pool['given'])
        last  = random.choice(pool['surname'])
        name  = f"{first} {last}"
        if name not in used:
            used.add(name)
            return name

# =========================
# Part 3 / 8
# =========================

# ---------- フォーマット ----------
def fmt_money(v:int)->str:
    if v >= 1_000_000: return f"{v//1_000_000}m€"
    if v >= 1_000:     return f"{v//1_000}k€"
    return f"{v}€"

# ---------- リーグ構成（地域＝国単位 / 2ディビジョン想定） ----------
def build_leagues(my_club:str):
    leagues = {
        "England": {
            "1部": ["Oxford Rovers","Kingsbridge City","Bristol Forge","Camden Borough",
                    "Lancaster Gate","Strive FC","Chelsea Heath","Manchester Vale","Liverpool Docks","Leeds Forge"],
            "2部": ["Brighton Seasiders","Derby Miners","Norwich Meadow","Reading Royals","Hull Mariners",
                    "Swansea River","Plymouth Harbors","Coventry Motors","Sheffield Steel","Portsmouth Sailors"]
        },
        "Spain": {
            "1部": ["Sevilla Reds","Madrid Norte","Catalunya Blau","Valencia Citrus","Bilbao Iron",
                    "Mallorca Waves","Granada Alhambra","Zaragoza Ebro","La Coruna Breeze","Toledo Town"],
            "2部": ["Tenerife Sun","Oviedo Peaks","Cadiz Harbor","Murcia Huerta","Almeria Desert",
                    "Lugo Forest","Huelva Coast","Girona Pyrenees","Burgos Castle","Leon Cathedral"]
        },
        "France": {
            "1部": ["Lille City","Lyon Lumière","Marseille Port","Bordeaux Vignes","Toulouse Violet",
                    "Nantes Atlantique","Rennes Armor","Nice Azure","Reims Champagne","Strasbourg Rhine"],
            "2部": ["Dijon Moutarde","Angers Loire","Metz Lorraine","Brest Océan","Le Havre Dockers",
                    "Caen Normand","Grenoble Alpes","Sochaux Lions","Tours Loire","Amiens Picardie"]
        },
        "Germany": {
            "1部": ["Munich Stars","Berlin Spree","Hamburg Hafen","Dortmund Coal","Leipzig Trade",
                    "Frankfurt Main","Stuttgart Motor","Bremen Weser","Hannover Messe","Köln Dom"],
            "2部": ["Bochum Ruhr","Freiburg Schwarzwald","Augsburg Fugger","Kiel Fjord","Nürnberg Burg",
                    "Dresden Elbe","Heidenheim Brenz","Regensburg Donau","Rostock Hanse","Paderborn Senne"]
        },
        "Netherlands": {
            "1部": ["Amsterdam Canal","Rotterdam Harbor","Utrecht Dom","Eindhoven Light","Alkmaar Cheese",
                    "Arnhem Bridge","Groningen North","Nijmegen Waalkade","Zwolle IJssel","Heerenveen Frisia"],
            "2部": ["Maastricht Meuse","Tilburg Textile","Breda Nassau","Leeuwarden Crown","Venlo Maas",
                    "Dordrecht Delta","Deventer Trade","Emmen Drenthe","Sittard Fortuna","Helmond Brabants"]
        }
    }

    # 自クラブを確実にどこかに置く（England 1部の1チームと差し替え）
    if my_club not in sum([sum(leagues[r].values(),[]) for r in leagues], []):
        eng1 = leagues["England"]["1部"]
        eng1[0] = my_club
        leagues["England"]["1部"] = eng1
    return leagues

# ---------- AIクラブ方針 ----------
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

# ---------- 選手生成 ----------
PID_COUNTER = 0
def new_pid():
    global PID_COUNTER
    PID_COUNTER += 1
    return PID_COUNTER

def gen_players(n:int, youth:bool=False, club:str="Free", used:set=None):
    if used is None: used=set()
    rows=[]
    for _ in range(n):
        nat = random.choice(list(NAME_POOLS.keys()-{'GEN'}))
        name = gen_unique_name(nat, used)
        stats = {k: random.randint(52 if youth else 60, 82 if youth else 90) for k in ABILITY_KEYS}
        stats = apply_bias(stats, nat)
        ovr = int(np.mean(list(stats.values())))
        plays = random.sample(pick_style_pool(nat), random.randint(1,3))
        growth = random.choice(pick_growth_pool(nat))
        val = normalize_value(int(ovr*ovr*12 + random.randint(-5000,5000)))
        age = random.randint(15 if youth else 19, 18 if youth else 34)
        rows.append({
            "PID": new_pid(),
            "Name": name,
            "Nat": nat,
            "Pos": random.choice(["GK","DF","MF","FW"]),
            "Age": age,
            **stats,
            "OVR": ovr,
            "Goals":0,
            "Assists":0,
            "IntlApps":0,
            "PlayStyle": plays,
            "GrowthType": growth,
            "Value": val,
            "Club": club,
            "Status":"通常",
            "RentalFrom":None,
            "RentalUntil":None,
            "OptionFee":None
        })
    return pd.DataFrame(rows)

# ---------- オファー判定 ----------
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

# ---------- 試合結果適用 ----------
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

# ---------- レンタル期限チェック ----------
def tick_rentals(df, week, pending_list):
    for i, r in df.iterrows():
        if r['RentalUntil'] is not None and week > r['RentalUntil'] and r['Status'].startswith("レンタル中"):
            pending_list.append(r['PID'])
            df.at[i,'Status'] = "レンタル満了"
    return df, pending_list

# ---------- 国際大会自動進行 ----------
def auto_intl_round():
    ses = st.session_state
    if not ses.intl_tournament:
        participants=[]
        for reg in ses.leagues:
            if '1部' in ses.standings[reg]:
                participants.extend(ses.standings[reg]['1部'].nlargest(2,'Pts')['Club'].tolist())
        random.shuffle(participants)
        ses.intl_tournament = {'clubs':participants,'results':[]}

    clubs = ses.intl_tournament['clubs']
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

        ses.intl_tournament['results'].append((c1,g1,c2,g2,pk_txt,w))
        ses.sns_posts.append(f"[国際大会] {c1} {g1}-{g2} {c2} {pk_txt} → 勝者:{w}")
        ses.sns_times.append(datetime.now())

        if 'intl_player_stats' not in ses:
            ses.intl_player_stats = {}

        pool_all = pd.concat([ses.senior, ses.youth, ses.all_players_pool], ignore_index=True)
        for club, goals in [(c1,g1),(c2,g2)]:
            team_df = pool_all[pool_all['Club']==club]
            if team_df.empty: 
                continue
            XI = team_df.nlargest(11,'OVR')
            # ゴール
            for _ in range(goals):
                pid = random.choice(XI['PID'].tolist())
                ses.intl_player_stats.setdefault(pid, {'G':0,'A':0,'Club':club,
                                                       'Name':team_df[team_df['PID']==pid]['Name'].iloc[0],
                                                       'Pos':team_df[team_df['PID']==pid]['Pos'].iloc[0]})
                ses.intl_player_stats[pid]['G'] += 1
            # アシスト
            for _ in range(goals):
                pid = random.choice(XI['PID'].tolist())
                ses.intl_player_stats.setdefault(pid, {'G':0,'A':0,'Club':club,
                                                       'Name':team_df[team_df['PID']==pid]['Name'].iloc[0],
                                                       'Pos':team_df[team_df['PID']==pid]['Pos'].iloc[0]})
                ses.intl_player_stats[pid]['A'] += 1

        # 自クラブの国際大会出場数
        if c1==ses.my_club or c2==ses.my_club:
            starters_names = ses.starters if ses.starters else ses.senior.nlargest(11,'OVR')['Name'].tolist()
            for nm in starters_names:
                for df in [ses.senior, ses.youth]:
                    idx = df.index[df['Name']==nm]
                    if len(idx)>0:
                        df.at[idx[0],'IntlApps'] = df.at[idx[0],'IntlApps'] + 1

        winners.append(w)

    if len(clubs)%2==1:
        winners.append(clubs[-1])
    ses.intl_tournament['clubs'] = winners

# =========================
# Part 4 / 8
# =========================

# -------- セッション初期化 --------
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

# 自クラブ選手
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

# クラブ→地域/Div マップ
if 'club_region_div' not in ses:
    mapping={}
    for reg in ses.leagues:
        for div in ses.leagues[reg]:
            for c in ses.leagues[reg][div]:
                mapping[c]=(reg,div)
    ses.club_region_div = mapping

# AIクラブ方針
if 'club_intent' not in ses:
    ses.club_intent = build_club_intents(ses.leagues, ses.my_club)

# 各種ログ／状態
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
    'starters':[],
    'intl_player_stats':{}
}
for k,v in defaults.items():
    if k not in ses: ses[k]=v

# レンタル満了チェック
ses.senior, ses.rental_pending = tick_rentals(ses.senior, ses.week, ses.rental_pending)
ses.youth , ses.rental_pending = tick_rentals(ses.youth , ses.week, ses.rental_pending)

# -------- レンタル満了処理UI --------
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
        st.write(f"**{r['Name']}** | Pos:{r['Pos']} | OVR:{r['OVR']} | 元:{r['RentalFrom']} | 買取OP:{fmt_money(r['OptionFee'])}")
        c1,c2 = st.columns(2)
        with c1:
            if st.button(f"買取する（{fmt_money(r['OptionFee'])}）", key=f"buy_{pid}"):
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

# -------- スカウト候補生成 --------
def gen_scout_candidates(pool_df, myclub, n=8, youth=False):
    # 年齢フィルタ
    if youth:
        pool_df = pool_df[pool_df['Age'] <= 18]
        free_df  = gen_players(max(1, n//2), youth=True , club="Free", used=ses.used_names)
    else:
        pool_df = pool_df[pool_df['Age'] >= 19]
        free_df  = gen_players(max(1, n//2), youth=False, club="Free", used=ses.used_names)

    others = pool_df[(pool_df['Club']!="Free") & (pool_df['Club']!=myclub)]
    take = n - len(free_df)
    pick_df = others.sample(min(take, len(others))) if len(others)>0 else pd.DataFrame()
    cands = pd.concat([free_df, pick_df], ignore_index=True)
    cands['PlayStyle'] = cands['PlayStyle'].apply(lambda x: " / ".join(x))
    return cands.sample(frac=1).reset_index(drop=True)

def get_rental_candidates(pool_df, myclub):
    return pool_df[(pool_df['Club']!=myclub) & (pool_df['RentalFrom'].isna()) & (pool_df['RentalUntil'].isna())]

# -------- タブ定義 --------
tabs = st.tabs([
    'シニア','ユース','選手詳細','試合','順位表',
    'スカウト/移籍','レンタル管理','SNS','財務レポート',
    '年間表彰','ランキング/国際大会','クラブ設定'
])

# =========================
# Part 5 / 8
# =========================

# ========= 0) シニア =========
with tabs[0]:
    st.markdown('<div style="color:#fff;font-size:20px;">シニア選手一覧</div>', unsafe_allow_html=True)
    handle_rental_expirations()

    order_mode = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="o_senior")
    reverse_flag = (order_mode=="FW→MF→DF→GK")

    df0 = ses.senior[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Club','Status','Goals','Assists']]
    df0['PlayStyle'] = df0['PlayStyle'].apply(lambda x:" / ".join(x))
    df0 = sort_by_pos(df0, reverse=reverse_flag)

    st.dataframe(
        df0.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                 .apply(style_playstyle, subset=['PlayStyle'])
                 .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# ========= 1) ユース =========
with tabs[1]:
    st.markdown('<div style="color:#fff;font-size:20px;">ユース選手一覧</div>', unsafe_allow_html=True)

    order_mode_y = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="o_youth")
    reverse_flag_y = (order_mode_y=="FW→MF→DF→GK")

    df1 = ses.youth[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Club','Status','Goals','Assists']]
    df1['PlayStyle'] = df1['PlayStyle'].apply(lambda x:" / ".join(x))
    df1 = sort_by_pos(df1, reverse=reverse_flag_y)

    st.dataframe(
        df1.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                 .apply(style_playstyle, subset=['PlayStyle'])
                 .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# ========= 2) 選手詳細 =========
with tabs[2]:
    pool_detail = pd.concat([ses.senior, ses.youth], ignore_index=True)
    sel_name = st.selectbox('選手選択', pool_detail['Name'].tolist())
    prow = pool_detail.loc[pool_detail['Name']==sel_name].iloc[0]

    st.write(f"ポジション: {prow['Pos']} / OVR:{prow['OVR']} / 年齢:{prow['Age']}")
    st.write(f"国籍: {prow['Nat']} / 国際大会出場: {prow['IntlApps']}回")
    st.write(f"プレースタイル: {', '.join(prow['PlayStyle'])}")
    st.write(f"所属: {prow['Club']} / 状態: {prow['Status']}")

    # レーダーチャート
    vals = [prow[k] for k in ABILITY_KEYS]
    fig_r = radar_chart(vals, ABILITY_KEYS)
    st.pyplot(fig_r)

    # 成長推移
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
        st.info("成長データはまだありません。")

# =========================
# Part 6 / 8
# =========================

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
        s_df = ses.senior[ses.senior['Name'].isin(ses.starters)][['Name','Pos','OVR','Goals','Assists','PlayStyle','Club']]
        s_df['PlayStyle']=s_df['PlayStyle'].apply(lambda x:" / ".join(x))
        s_df = sort_by_pos(s_df)
        st.dataframe(
            s_df.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                      .apply(style_playstyle, subset=['PlayStyle'])
                      .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )
    else:
        st.warning("まず『オート先発選考』を行ってください。")

    # 地域・ディビジョンから対戦相手を選択
    my_reg, my_div = ses.club_region_div[ses.my_club]
    opp = random.choice([c for c in ses.leagues[my_reg][my_div] if c != ses.my_club])

    kick_btn = st.button("キックオフ", disabled=(len(ses.starters)==0 or ses.week>SEASON_WEEKS))
    if kick_btn:
        atk = ses.senior[ses.senior['Name'].isin(ses.starters)]['OVR'].mean() if ses.starters else 70
        oppatk = random.uniform(60,90)
        gh = max(0,int(np.random.normal((atk-60)/8,1)))
        ga = max(0,int(np.random.normal((oppatk-60)/8,1)))
        shots = random.randint(5,15); on_t = random.randint(0,shots)

        scorers=[]; assisters=[]
        if gh>0 and ses.starters:
            for _ in range(gh):
                s = random.choice(ses.starters)
                a_candidates = [x for x in ses.starters if x!=s]
                a = random.choice(a_candidates) if a_candidates else s
                scorers.append(s); assisters.append(a)
                ses.senior.loc[ses.senior['Name']==s,'Goals']   += 1
                ses.senior.loc[ses.senior['Name']==a,'Assists'] += 1

        ses.match_log.append({'week':ses.week,'opp':opp,'gf':gh,'ga':ga})
        ses.sns_posts.append(f"{ses.my_club} {gh}-{ga} {opp}")
        ses.sns_times.append(datetime.now())

        ses.finance_log.append({
            'week': ses.week,
            'revenue_ticket': gh*15000 + random.randint(5000,10000),
            'revenue_goods' : ga*8000  + random.randint(1000,5000),
            'expense_salary': int(ses.senior['OVR'].mean()*1000)
        })

        ses.standings[my_reg][my_div] = apply_result(ses.standings[my_reg][my_div], ses.my_club, opp, gh, ga)

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

        # 成長処理・履歴保存
        ses.senior = apply_growth(ses.senior, ses.week)
        for _,rw in ses.senior.iterrows():
            update_player_history(rw['Name'], rw, ses.week)

        st.success(f"結果 {gh}-{ga}")
        if scorers:   st.write("得点者: " + " / ".join(scorers))
        if assisters: st.write("アシスト: " + " / ".join(assisters))
        st.write(f"シュート:{shots} 枠内:{on_t} ポゼッション:{random.randint(40,60)}%")

        ses.week += 1
        auto_intl_round()

        if ses.week > SEASON_WEEKS:
            champ = ses.standings[my_reg][my_div].nlargest(1,'Pts')['Club'].iloc[0]
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
            ses.intl_player_stats.clear()
            st.success("新シーズン開始！")

# ========= 4) 順位表 =========
with tabs[4]:
    region = st.selectbox('地域', list(ses.leagues.keys()))
    division = st.selectbox('部', list(ses.leagues[region].keys()))
    df_st = ses.standings[region][division]
    st.dataframe(
        df_st.style.apply(make_highlighter('Club', ses.my_club), axis=1)
            .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# =========================
# Part 7 / 8
# =========================

# ========= 5) スカウト/移籍 =========
with tabs[5]:
    st.markdown("<div style='color:#fff;font-size:20px;'>スカウト / 移籍 / レンタル</div>", unsafe_allow_html=True)

    cat = st.radio("対象カテゴリー", ["シニア候補","ユース候補"], horizontal=True)
    youth_flag = (cat=="ユース候補")

    need_txt = suggest_positions(ses.senior if not youth_flag else ses.youth)
    st.markdown(f"**補強推奨ポジション:** {need_txt}")

    c1,c2 = st.columns(2)
    with c1:
        if st.button("候補リスト更新"):
            pool_all = pd.concat([ses.all_players_pool, ses.senior, ses.youth], ignore_index=True)
            ses.scout_list = gen_scout_candidates(pool_all, ses.my_club, n=8, youth=youth_flag)
    with c2:
        st.write(f"予算: {fmt_money(ses.budget)}")

    if ses.scout_list is None or ses.scout_list.empty:
        st.info("候補がいません。『候補リスト更新』を押してください。")
    else:
        for i,row in ses.scout_list.iterrows():
            st.markdown(
                "<div style='background:rgba(255,255,255,0.10);padding:10px 14px;margin:14px 0;border-radius:10px;'>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"**{row['Name']}** | {row['Nat']} | {row['Age']}歳 | {row['Pos']} | OVR:{row['OVR']}<br>"
                f"PlayStyle: {row['PlayStyle']}<br>"
                f"所属:{row['Club']} / 価値:{fmt_money(row['Value'])}",
                unsafe_allow_html=True
            )

            if row['Club']=="Free":
                if st.button("契約", key=f"sign_free_{i}"):
                    dst = 'youth' if youth_flag else 'senior'
                    setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row])], ignore_index=True))
                    ses.scout_list = ses.scout_list.drop(i).reset_index(drop=True)
                    st.success("獲得しました！")
            else:
                mode = st.selectbox(f"オファー種別（{row['Name']}）", ["完全移籍","レンタル(買取OP付)"], key=f"mode_{i}")
                policy = ses.club_intent.get(row['Club'],{}).get('policy','balanced')

                with st.form(f"offer_{i}"):
                    if mode=="完全移籍":
                        wage = st.number_input("提示年俸(€)", min_value=0, value=row['OVR']*150, key=f"wage_{i}")
                        years= st.slider("契約年数",1,5,3, key=f"years_{i}")
                        fee  = st.number_input("移籍金(€)", min_value=0, value=int(row['Value']), key=f"fee_{i}")
                        sub  = st.form_submit_button("送信")
                        if sub:
                            ok, want_wage, want_fee = offer_result(row, wage, years, fee, ses.budget, policy)
                            if ok:
                                ses.budget -= fee
                                row2 = row.copy(); row2['Club']=ses.my_club
                                dst = 'youth' if youth_flag else 'senior'
                                setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row2])], ignore_index=True))
                                ses.scout_list = ses.scout_list.drop(i).reset_index(drop=True)
                                st.success("移籍成立！")
                            else:
                                st.error(f"拒否【要求目安:年俸{want_wage}€, 移籍金{want_fee}€】")

                    else:  # レンタル
                        weeks = st.slider("レンタル期間（節）",1,8,4, key=f"weeks_{i}")
                        fee_r = st.number_input("レンタル料(€)", min_value=0, value=int(row['Value']*0.15), key=f"feer_{i}")
                        opt   = st.number_input("買取オプション額(€)", min_value=0, value=int(row['Value']*1.2), key=f"opt_{i}")
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
                                dst = 'youth' if youth_flag else 'senior'
                                setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row2])], ignore_index=True))
                                ses.all_players_pool = ses.all_players_pool[ses.all_players_pool['PID']!=row['PID']]
                                ses.scout_list = ses.scout_list.drop(i).reset_index(drop=True)
                                st.success("レンタル成立！")
                            else:
                                st.error(f"拒否【要求額目安:{fmt_money(demand)}】")
            st.markdown("</div>", unsafe_allow_html=True)

# ========= 6) レンタル管理 =========
with tabs[6]:
    st.markdown("<div style='color:#fff;font-size:20px;'>レンタル管理</div>", unsafe_allow_html=True)
    handle_rental_expirations()

    df_r = pd.concat([ses.senior, ses.youth], ignore_index=True)
    df_r = df_r[df_r['Status'].str.startswith("レンタル中", na=False)][
        ['Name','Pos','OVR','RentalFrom','RentalUntil','OptionFee','Status']
    ]
    if df_r.empty:
        st.info("レンタル中の選手はいません。")
    else:
        st.dataframe(
            df_r.set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

# ========= 7) SNS =========
with tabs[7]:
    st.markdown("<div style='color:#fff;font-size:20px;'>SNS / ファン投稿</div>", unsafe_allow_html=True)
    if ses.sns_posts:
        for t, p in zip(reversed(ses.sns_times), reversed(ses.sns_posts)):
            st.write(f"{t.strftime('%m/%d %H:%M')} - {p}")
    else:
        st.info("投稿なし")

# ========= 8) 財務レポート =========
with tabs[8]:
    st.markdown("<div style='color:#fff;font-size:20px;'>財務レポート</div>", unsafe_allow_html=True)
    df_fin = pd.DataFrame(ses.finance_log)
    if df_fin.empty:
        st.info("財務データなし")
    else:
        fig, ax = plt.subplots()
        ax.plot(df_fin['week'], df_fin['revenue_ticket']+df_fin['revenue_goods'], label='収入')
        ax.plot(df_fin['week'], df_fin['expense_salary'], label='支出')
        ax.set_xlabel("節"); ax.set_ylabel("金額(€)"); ax.set_title("収支推移")
        ax.legend()
        make_transparent(ax)
        st.pyplot(fig)

        st.dataframe(
            df_fin.rename(columns={
                'week':'節','revenue_ticket':'チケット収入','revenue_goods':'グッズ収入','expense_salary':'人件費'
            }).style.set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

