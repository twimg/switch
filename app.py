# =========================
# Part 1 / 10  --- 基本設定・共通関数
# =========================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# ---- ページ設定 ----
st.set_page_config(page_title="Club Strive - Ultimate Soccer Manager", layout="wide")

# 乱数固定
random.seed(42)
np.random.seed(42)

# Matplotlib 日本語 & 透明背景
plt.rcParams['font.family'] = 'IPAexGothic'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['figure.facecolor'] = 'none'

# ---- CSS（全体UI調整）----
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }
h1,h2,h3,h4,h5,h6 { color:#fff!important; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }

/* 通常&送信ボタン */
.stButton>button, div[data-testid="stFormSubmitButton"] button {
  background:#27e3b9!important; color:#202b41!important; font-weight:bold;
  border-radius:10px; margin:6px 0; border:2px solid #27e3b9!important;
}
.stButton>button:active, div[data-testid="stFormSubmitButton"] button:active {
  background:#ffee99!important;
}

/* DataFrame */
.dataframe tbody tr, .dataframe thead tr, .stDataFrame, .stDataFrame div {
  background:rgba(32,44,70,0.85)!important; color:#fff!important;
}
.dataframe td, .dataframe th { color:#fff!important; }

/* スカウトカード */
.scout-card{
  background:rgba(255,255,255,0.10); padding:12px 16px; margin:16px 0;
  border-radius:12px; box-shadow:0 0 6px #0006;
}

/* 情報ボックス（空白防止） */
.tab-info{
  color:#fff; background:rgba(255,255,255,0.08); padding:12px 16px;
  border-radius:8px; margin:12px 0;
}

/* プレースタイルのタグ風表示用（必要に応じて使う） */
span.playstyle-chip {
  display:inline-block; padding:3px 8px; margin:2px; border-radius:12px;
  background:#f7df70; color:#202b41; font-size:12px; font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.title("Club Strive")

# ---- 定数 ----
SEASON_WEEKS = 14
POS_ORDER = {"GK":0, "DF":1, "MF":2, "FW":3}
ABILITY_KEYS = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
ABILITY_LABELS = {
    'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina',
    'Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'
}

# ---- 便利関数 ----
def fmt_money(v:int)->str:
    if v >= 1_000_000: return f"{v//1_000_000}m€"
    if v >= 1_000:     return f"{v//1_000}k€"
    return f"{v}€"

def make_transparent(ax):
    ax.tick_params(colors="#fff")
    for spine in ax.spines.values():
        spine.set_color("#fff")
    ax.title.set_color("#fff")
    ax.xaxis.label.set_color("#fff")
    ax.yaxis.label.set_color("#fff")
    leg = ax.get_legend()
    if leg:
        for text in leg.get_texts():
            text.set_color("#fff")

def radar_chart(vals, labels):
    L = len(labels)
    angles = np.linspace(0, 2*np.pi, L, endpoint=False)
    vals = np.r_[vals, vals[0]]
    angles = np.r_[angles, angles[0]]
    fig = plt.figure(figsize=(3,3))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, vals, linewidth=2)
    ax.fill(angles, vals, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color="#fff", fontsize=8)
    ax.set_yticklabels([])
    ax.grid(color="#fff", alpha=0.2)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    return fig

def sort_by_pos(df, reverse=False):
    df = df.copy()
    df['__p__'] = df['Pos'].map(POS_ORDER)
    df = df.sort_values(['__p__','OVR'], ascending=[not reverse, False]).drop(columns='__p__')
    return df

def make_highlighter(col_name, target):
    def _hl(row):
        return ['background-color: rgba(247,223,112,0.25); color:#fff']*len(row) if row[col_name]==target else ['']*len(row)
    return _hl

def style_playstyle(series: pd.Series):
    # DataFrame.style で使うダミー（今回は色変え済みなので空）
    return ['']*len(series)

def normalize_value(v:int)->int:
    if v < 1000:
        v = (v//5)*5
    else:
        v = (v//1000)*1000
    return max(v, 0)

def suggest_positions(df):
    need = {'GK':2,'DF':8,'MF':8,'FW':5}
    cnt = df['Pos'].value_counts().to_dict()
    msg=[]
    for p in ['GK','DF','MF','FW']:
        lack = need[p] - cnt.get(p,0)
        if lack>0: msg.append(f"{p}×{lack}")
    return "なし" if not msg else ", ".join(msg)

# =========================
# Part 2 / 10  --- 名前/スタイル/成長/バイアス
# =========================

# ---- 20か国 + 汎用 の名前プール（first30/last30）----
# 追加・修正したい場合はこの辞書を編集
NAME_POOLS = {
    "ENG": {
        "first": ["Oliver","George","Harry","Jack","Noah","Charlie","Jacob","Thomas","Oscar","William",
                  "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Harrison","Benjamin",
                  "Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan","Toby"],
        "last":  ["Smith","Jones","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Walker",
                  "White","Hall","Green","Wood","Martin","Lewis","Turner","Scott","Clark","Harris",
                  "Baker","Moore","Wright","Hill","Cooper","Edwards","Ward","King","Parker","Campbell"]
    },
    "GER": {
        "first": ["Lukas","Leon","Finn","Jonas","Paul","Noah","Elias","Ben","Felix","Maximilian",
                  "Luis","Moritz","Tim","Fabian","David","Daniel","Simon","Julian","Niklas","Philipp",
                  "Tobias","Sebastian","Matthias","Erik","Valentin","Jannik","Mats","Marco","Marvin","Joshua"],
        "last":  ["Muller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Hoffmann","Schäfer",
                  "Koch","Richter","Klein","Wolf","Schroder","Neumann","Schwarz","Zimmermann","Braun","Kruger",
                  "Hofmann","Hartmann","Lange","Schmitt","Werner","Schmitz","Krause","Meier","Lehmann","Hermann"]
    },
    "FRA": {
        "first": ["Lucas","Hugo","Louis","Adam","Gabriel","Arthur","Raphael","Jules","Ethan","Paul",
                  "Théo","Tom","Enzo","Nathan","Alexandre","Maxime","Baptiste","Evan","Noah","Nolan",
                  "Liam","Matteo","Antoine","Clément","Quentin","Victor","Simon","Mathis","Benjamin","Daniel"],
        "last":  ["Martin","Bernard","Dubois","Thomas","Robert","Richard","Petit","Durand","Leroy","Moreau",
                  "Simon","Laurent","Lefebvre","Michel","Garcia","David","Bertrand","Roux","Vincent","Fournier",
                  "Morel","Girard","Andre","Lefevre","Mercier","Dupont","Lambert","Bonnet","Francois","Martinez"]
    },
    "ESP": {
        "first": ["Alejandro","Daniel","Pablo","Alvaro","Adrian","David","Javier","Diego","Mario","Sergio",
                  "Hugo","Miguel","Juan","Carlos","Ruben","Jorge","Andres","Francisco","Raul","Marco",
                  "Gabriel","Oscar","Ignacio","Iker","Lucas","Gonzalo","Victor","Jaime","Ismael","Rafael"],
        "last":  ["Garcia","Martinez","Lopez","Sanchez","Gonzalez","Perez","Rodriguez","Fernandez","Gomez","Martin",
                  "Jimenez","Ruiz","Diaz","Hernandez","Alvarez","Moreno","Muñoz","Alonso","Gutierrez","Navarro",
                  "Torres","Dominguez","Vazquez","Ramos","Gil","Ramirez","Serrano","Blanco","Molina","Suarez"]
    },
    "ITA": {
        "first": ["Lorenzo","Alessandro","Leonardo","Francesco","Mattia","Andrea","Matteo","Gabriele","Riccardo","Tommaso",
                  "Edoardo","Giuseppe","Antonio","Diego","Filippo","Nicolo","Federico","Samuel","Michele","Marco",
                  "Daniele","Raffaele","Christian","Simone","Roberto","Pietro","Enrico","Salvatore","Emanuele","Stefano"],
        "last":  ["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco",
                  "Bruno","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Moretti",
                  "Barbieri","Fontana","Santoro","Mariani","Rinaldi","Caruso","Ferrara","Ferri","Bianco","Grasso"]
    },
    "NED": {
        "first": ["Daan","Sem","Lucas","Levi","Finn","Milan","Liam","Noah","Luuk","Thijs",
                  "Jesse","Bram","Mees","Timo","Ties","Julian","Max","Jens","Niels","Sven",
                  "Bas","Ruben","Koen","Floris","Thomas","Gijs","Nick","Pepijn","Sam","Rens"],
        "last":  ["de Jong","de Vries","van den Berg","van Dijk","Bakker","Jansen","Visser","Smit","Meijer","Mulder",
                  "Bos","Vos","Peters","Hendriks","Dekker","Brouwer","van Leeuwen","Koster","van der Meer","Kuiper",
                  "Kok","Schouten","Vermeulen","Post","van Dam","Willems","Hermans","van der Linden","Hoekstra","Sanders"]
    },
    "BRA": {
        "first": ["Joao","Gabriel","Pedro","Lucas","Matheus","Gustavo","Felipe","Rafael","Bruno","Thiago",
                  "Diego","Daniel","Eduardo","Vitor","Leonardo","Vinicius","Anderson","Alex","Paulo","Rodrigo",
                  "Marcos","Renan","Caio","Igor","Fernando","Hugo","Samuel","Antonio","Nathan","Luiz"],
        "last":  ["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Almeida","Costa","Carvalho","Gomes",
                  "Martins","Araujo","Barbosa","Ribeiro","Alves","Pereira","Lima","Nascimento","Moreira","Teixeira",
                  "Correia","Melo","Cardoso","Rocha","Dias","Campos","Fonseca","Monteiro","Batista","Freitas"]
    },
    "POR": {
        "first": ["Tiago","Goncalo","Diogo","Miguel","Joao","Rodrigo","Andre","Rafael","Bruno","Hugo",
                  "Pedro","Luis","Carlos","Ricardo","Paulo","Nuno","Fernando","Manuel","Eduardo","Vitor",
                  "Filipe","Alexandre","Sergio","Fabio","Rui","Marco","Samuel","Henrique","Antonio","Gil"],
        "last":  ["Silva","Santos","Ferreira","Pereira","Oliveira","Costa","Rodrigues","Martins","Jesus","Sousa",
                  "Fernandes","Goncalves","Lopes","Marques","Alves","Ribeiro","Carvalho","Cardoso","Pinto","Teixeira",
                  "Moreira","Correia","Rocha","Nunes","Vieira","Monteiro","Mendes","Azevedo","Figueiredo","Machado"]
    },
    "BEL": {
        "first": ["Liam","Noah","Jules","Arthur","Lucas","Louis","Victor","Adam","Gabriel","Oscar",
                  "Mathis","Eden","Nathan","Thomas","Benjamin","Alexis","Hugo","Maxime","Simon","Theo",
                  "Baptiste","Ruben","Stan","Milan","Thibault","Matteo","Dries","Yoran","Lars","Quinten"],
        "last":  ["Peeters","Janssens","Maes","Jacobs","Mertens","Willems","Claes","Goossens","Wouters","De Smet",
                  "Dubois","Aerts","Dumont","Hermans","Martens","Vermeulen","Lemmens","Pauwels","Smets","Hubert",
                  "Gielen","Vos","Michiels","Engelen","Luyten","Smeets","Leclercq","Lambrecht","Cornelis","Vanderlinden"]
    },
    "TUR": {
        "first": ["Mehmet","Mustafa","Ahmet","Ali","Huseyin","Ibrahim","Hasan","Osman","Yusuf","Fatih",
                  "Emre","Murat","Omer","Burak","Serkan","Ismail","Kadir","Halil","Erdem","Furkan",
                  "Cem","Onur","Can","Volkan","Gokhan","Tugrul","Alper","Sinan","Recep","Yasin"],
        "last":  ["Yilmaz","Kaya","Demir","Sahin","Celik","Yildiz","Aydin","Ozdemir","Arslan","Kilic",
                  "Ozkan","Simsek","Polat","Avci","Dogan","Korkmaz","Aslan","Tekin","Gunes","Keskin",
                  "Erdogan","Kurt","Aksoy","Cetin","Aktaş","Işık","Bulut","Turan","Ucar","Bozkurt"]
    },
    "ARG": {
        "first": ["Juan","Matias","Nicolas","Federico","Santiago","Agustin","Joaquin","Lucas","Martin","Gonzalo",
                  "Diego","Ezequiel","Facundo","Leandro","Maximiliano","Pablo","Bruno","Alejandro","Cristian","Sebastian",
                  "Emiliano","Damian","Hernan","Rodrigo","Esteban","Franco","Ivan","Mariano","Nahuel","Mauricio"],
        "last":  ["Gonzalez","Rodriguez","Fernandez","Lopez","Martinez","Garcia","Perez","Sanchez","Romero","Alvarez",
                  "Torres","Ruiz","Diaz","Suarez","Castro","Gutierrez","Gimenez","Acosta","Benitez","Silva",
                  "Molina","Ortega","Delgado","Vega","Sosa","Herrera","Aguirre","Ponce","Ramos","Mendez"]
    },
    "URU": {
        "first": ["Carlos","Diego","Pablo","Gaston","Sergio","Jorge","Maxi","Matias","Sebastian","Martin",
                  "Nicolas","Cristian","Federico","Agustin","Rodrigo","Bruno","Emiliano","Facundo","Gabriel","Jonathan",
                  "Hernan","Leandro","Lucas","Nahuel","Santiago","Victor","Marcos","Franco","Ruben","Ignacio"],
        "last":  ["Gonzalez","Rodriguez","Fernandez","Perez","Martinez","Garcia","Lopez","Sanchez","Suarez","Castro",
                  "Gomez","Silva","Diaz","Acosta","Torres","Ramos","Vazquez","Mendez","Cabrera","Pereyra",
                  "Mora","Aguilar","Pereira","Arias","Benitez","Medina","Mendoza","Herrera","Viera","Sosa"]
    },
    "COL": {
        "first": ["Juan","Andres","Carlos","Jorge","Diego","Santiago","Luis","Felipe","Daniel","Camilo",
                  "Sebastian","Miguel","Oscar","Julian","Fabian","Jonathan","Victor","Cristian","Esteban","Ivan",
                  "Fernando","Armando","Wilson","Mauricio","Alejandro","Ricardo","Nicolas","Hernan","Edwin","Pedro"],
        "last":  ["Gomez","Rodriguez","Martinez","Garcia","Perez","Gonzalez","Sanchez","Ramirez","Diaz","Torres",
                  "Castro","Moreno","Suarez","Reyes","Gutierrez","Vargas","Rojas","Ortiz","Rubio","Pineda",
                  "Mendoza","Guerrero","Salazar","Quintero","Herrera","Cortes","Arias","Velasquez","Sandoval","Peña"]
    },
    "USA": {
        "first": ["James","John","Robert","Michael","William","David","Richard","Joseph","Thomas","Charles",
                  "Christopher","Daniel","Matthew","Anthony","Mark","Donald","Steven","Paul","Andrew","Joshua",
                  "Kevin","Brian","Edward","George","Timothy","Jason","Jeffrey","Ryan","Jacob","Gary"],
        "last":  ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
                  "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
                  "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson"]
    },
    "MEX": {
        "first": ["Juan","Jose","Luis","Carlos","Jorge","Miguel","Antonio","Pedro","Jesus","Francisco",
                  "Rafael","Ricardo","Alejandro","Manuel","Fernando","Hector","Eduardo","Javier","Arturo","Sergio",
                  "Daniel","Adrian","Raul","Victor","Mario","Emilio","Ernesto","Gustavo","Armando","Osvaldo"],
        "last":  ["Hernandez","Garcia","Martinez","Lopez","Gonzalez","Perez","Rodriguez","Sanchez","Ramirez","Cruz",
                  "Flores","Gomez","Morales","Vargas","Reyes","Diaz","Torres","Gutierrez","Ruiz","Chavez",
                  "Ramos","Mendoza","Ortega","Castillo","Silva","Delgado","Campos","Ayala","Pineda","Munoz"]
    },
    "SAU": {  # Saudi Arabia
        "first": ["Abdullah","Mohammed","Ahmed","Ali","Hassan","Omar","Yousef","Fahad","Majed","Turki",
                  "Khalid","Saud","Nasser","Ibrahim","Saif","Mansour","Talal","Sultan","Abdulrahman","Faisal",
                  "Saeed","Rayan","Adel","Badr","Saleh","Waleed","Sami","Bandar","Ziad","Khaled"],
        "last":  ["Al-Saud","Al-Harbi","Al-Qahtani","Al-Shahrani","Al-Ghamdi","Al-Otaibi","Al-Mutairi","Al-Dossari","Al-Subaie","Al-Johani",
                  "Al-Zahrani","Al-Anazi","Al-Rashid","Al-Shehri","Al-Hazmi","Al-Amri","Al-Malki","Al-Ahmad","Al-Fahad","Al-Bishi",
                  "Al-Dhafeeri","Al-Harthi","Al-Balawi","Al-Sayed","Al-Zayed","Al-Najjar","Al-Bassam","Al-Jaber","Al-Nasser","Al-Faraj"]
    },
    "NGA": {  # Nigeria
        "first": ["Emeka","Chinedu","Ifeanyi","Segun","Ibrahim","Sule","Sunday","Kingsley","Emmanuel","Joseph",
                  "Samuel","Peter","Abdul","Uche","Tunde","Collins","Bright","Godwin","Sani","Moses",
                  "Charles","Ikenna","Nonso","Kelechi","Chukwuemeka","Chigozie","Olamide","Ayodele","Oluwatobi","Kunle"],
        "last":  ["Okafor","Okeke","Ogunleye","Adeyemi","Balogun","Okoye","Ojo","Eze","Abiola","Afolayan",
                  "Adewale","Olawale","Ogunbiyi","Ibrahim","Mohammed","Danladi","Yakubu","Nwosu","Chukwu","Odinaka",
                  "Onyekachi","Opara","Olatunji","Oladipo","Ogunbanjo","Ezekiel","Ogunjobi","Akintola","Abubakar","Oladimeji"]
    },
    "MAR": {  # Morocco
        "first": ["Youssef","Mohamed","Achraf","Hassan","Said","Omar","Mehdi","Ismail","Amine","Rachid",
                  "Ayoub","Anass","Karim","Hamza","Zakaria","Yassine","Imad","Reda","Walid","Khalid",
                  "Nabil","Idriss","Soufiane","Aziz","Tarik","Abdelaziz","Abdelkader","Mounir","Abdelhak","Samir"],
        "last":  ["El Fassi","El Idrissi","El Amrani","Benali","Benyoussef","El Haddad","El Ghazali","El Mansouri","Bennani","El Hachimi",
                  "El Moussaoui","Bourquia","Chakiri","Sebbar","Ait Taleb","El Abidi","El Yousfi","El Jouni","Azouzi","Ait Lahcen",
                  "Hassani","Ramdani","El Amiri","Harrak","El Azzouzi","Bouazza","El Hamdi","Khattabi","Bakkali","Bouhaddi"]
    },
    "KOR": {
        "first": ["Min-jae","Joon-ho","Ji-hoon","Sung-min","Dong-hyun","Hyun-woo","Seung-hyun","Jae-won","Young-ho","Min-seok",
                  "Tae-hyun","Jin-woo","Sang-hoon","Byung-ho","Woo-jin","Hyeon-su","Kang-min","Do-hyun","Seok-jin","Jun-seo",
                  "Yoon-seo","Dae-hyun","Sang-min","Jong-hyun","Hyun-jin","Ji-ho","Seung-woo","Chul-soo","Min-ho","Yong-ho"],
        "last":  ["Kim","Lee","Park","Choi","Jung","Kang","Cho","Yoon","Jang","Lim",
                  "Han","Shin","Yoo","Ahn","Seo","Kwon","Hwang","Oh","Song","Hong",
                  "Yang","Moon","Son","Bae","Baek","Nam","Heo","No","Gu","Ryu"]
    },
    "AUS": {
        "first": ["Jack","Noah","William","James","Lucas","Hunter","Jackson","Lachlan","Ethan","Cooper",
                  "Oliver","Leo","Harrison","Max","Isaac","Benjamin","Mason","Henry","Samuel","Thomas",
                  "Alexander","Archie","Elijah","Hudson","Levi","Logan","Sebastian","Oscar","Joseph","Charlie"],
        "last":  ["Smith","Jones","Williams","Brown","Wilson","Taylor","Johnson","White","Martin","Anderson",
                  "Thompson","Nguyen","Walker","Harris","Kelly","King","Wright","Scott","Young","Allen",
                  "Clarke","Mitchell","Morris","Hall","Adams","Roberts","Campbell","Phillips","Evans","Turner"]
    },
    "GEN": {  # どこでも使える汎用名
        "first": ["Alex","Chris","Sam","Jamie","Jordan","Taylor","Casey","Morgan","Robin","Cameron",
                  "Riley","Avery","Quinn","Hayden","Skyler","Kendall","Reese","Rowan","Peyton","Dakota",
                  "Elliot","Finley","Harper","Jules","Kai","Lee","Micah","Noel","Parker","Shay"],
        "last":  ["Gray","Hill","West","Stone","Lane","Reed","Ford","Woods","Grant","Cole",
                  "Mason","Shaw","Dunn","Watts","Cross","Kerr","Black","Snow","Frost","Day",
                  "Fox","Lake","Pope","Glass","Miles","Page","Rice","Sharp","Watt","Ball"]
    }
}

# ---- プレースタイル候補（重複なく） ----
PLAYSTYLE_BASE = [
    "チーム至上主義","スーパーリーダー","職人","司令塔","タックルマスター","ゲームメーカー","チャンスメーカー",
    "ムードメーカー","影の支配者","爆発型","クロスハンター","フリーキック職人","ジョーカー","空中戦の覇者",
    "インナーラップSB","セカンドストライカー","起点型GK","守護神","スナイパー","ドリブラー","シャドーストライカー",
    "カットイン職人","フィニッシャー","ワークホース","ボールハンター","レジスタ","プレッサー","ハードマーカー",
    "ポストプレイヤー","ラインブレーカー"
]

# 国別に強調するスタイル（加算用）
NATION_STYLE_EXTRA = {
    "ENG": ["フィジカルモンスター","空中戦の覇者","ロングスロー"],
    "GER": ["規律派","インテリジェンス","精密機械"],
    "FRA": ["アーティスト","テクニシャン","シャドーストライカー"],
    "ESP": ["ティキタカ使い","レジスタ","パサー"],
    "ITA": ["カテナチオ守備者","ディフェンスリーダー","戦術家"],
    "NED": ["トータルフットボール","偽9番","多才型"],
    "BRA": ["サンバドリブラー","ファンタジスタ","フリーキック職人"],
    "POR": ["カットイン職人","エレガント","トリックスター"],
    "BEL": ["ユーティリティ","ポリバレント","ボックスtoボックス"],
    "TUR": ["闘魂タイプ","情熱家","ショットガン"],
    "ARG": ["メンタルモンスター","ラテンの殺し屋","ゲームメーカー"],
    "URU": ["闘犬","ハードワーカー","魂のストライカー"],
    "COL": ["快速ウインガー","カウンターエース","爆発型"],
    "USA": ["フィジカルモンスター","運動量おばけ","メンタルリーダー"],
    "MEX": ["技巧派","チャンスメイカー","スピードスター"],
    "SAU": ["砂漠の戦士","対人勝負師","メンタル強者"],
    "NGA": ["爆発型","身体能力特化","空中戦の覇者"],
    "MAR": ["技巧派","俊敏ドリブラー","ボールウィナー"],
    "KOR": ["走力モンスター","規律派","ハードワーカー"],
    "AUS": ["タフガイ","万能型","戦術理解度高"],
    "GEN": []
}

# ---- 成長タイプ（プレースタイルからは除外） ----
GROWTH_TYPES = ["超晩成型","晩成型","通常型","やや早熟型","超早熟型"]

# 国別ビアスで使う係数（上げたい能力:倍率）
NATION_ABILITY_BIAS = {
    "ENG": {"Phy":1.1,"Pow":1.05,"Def":1.05},
    "GER": {"Men":1.1,"Def":1.05,"Pas":1.05},
    "FRA": {"Tec":1.08,"Sht":1.05,"Spd":1.05},
    "ESP": {"Pas":1.1,"Tec":1.08,"Men":1.02},
    "ITA": {"Def":1.1,"Men":1.05,"Pas":1.02},
    "NED": {"Pas":1.06,"Tec":1.06,"Spd":1.02},
    "BRA": {"Tec":1.1,"Sht":1.06,"Spd":1.04},
    "POR": {"Tec":1.08,"Pas":1.05,"Sht":1.03},
    "BEL": {"MF":1.0},  # unused but kept
    "TUR": {"Pow":1.06,"Men":1.05,"Phy":1.04},
    "ARG": {"Men":1.06,"Sht":1.06,"Tec":1.04},
    "URU": {"Men":1.08,"Def":1.05,"Pow":1.03},
    "COL": {"Spd":1.07,"Sht":1.05,"Tec":1.03},
    "USA": {"Phy":1.08,"Sta":1.05,"Pow":1.03},
    "MEX": {"Tec":1.06,"Pas":1.05,"Spd":1.03},
    "SAU": {"Men":1.05,"Sta":1.04,"Tec":1.02},
    "NGA": {"Phy":1.1,"Spd":1.07,"Pow":1.05},
    "MAR": {"Tec":1.06,"Spd":1.04,"Men":1.03},
    "KOR": {"Sta":1.08,"Men":1.06,"Spd":1.03},
    "AUS": {"Phy":1.05,"Sta":1.05,"Men":1.03},
    "GEN": {}
}

# ---- 名前生成 ----
def gen_unique_name(nat:str, used:set):
    pool = NAME_POOLS.get(nat, NAME_POOLS["GEN"])
    for _ in range(200):  # ループ保険
        n = f"{random.choice(pool['first'])} {random.choice(pool['last'])}"
        if n not in used:
            used.add(n)
            return n
    # 予備
    n = f"{random.choice(NAME_POOLS['GEN']['first'])} {random.choice(NAME_POOLS['GEN']['last'])}"
    used.add(n)
    return n

# ---- スタイル/成長プール取得 ----
def pick_style_pool(nat:str):
    base = PLAYSTYLE_BASE.copy()
    extra = NATION_STYLE_EXTRA.get(nat, [])
    return list(dict.fromkeys(base + extra))  # 重複除去

def pick_growth_pool(nat:str):
    return GROWTH_TYPES  # 今回は共通

# ---- 能力バイアス適用 ----
def apply_bias(stats:dict, nat:str):
    bias = NATION_ABILITY_BIAS.get(nat, {})
    for k,v in bias.items():
        if k in stats:
            stats[k] = int(stats[k]*v)
    return stats

# =========================
# Part 3 / 10  --- リーグ/選手生成/初期化（Italyのみ2部構成）
# =========================

# ----- 国コード一覧（20か国） -----
NATIONS = ["ENG","GER","FRA","ESP","ITA","NED","BRA","POR","BEL","TUR",
           "ARG","URU","COL","USA","MEX","SAU","NGA","MAR","KOR","AUS"]

# ----- リーグ構成（各国1部。既存5か国＋Italyは2部） -----
def build_leagues(my_club:str):
    leagues = {
        "England": {
            "1部": ["Strive FC","Oxford Rovers","Kingsbridge City","Bristol Forge","Camden Borough",
                    "Lancaster Gate","Chelsea Heath","Manchester Vale","Liverpool Docks","Leeds Forge"],
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
                    "Frankfurt Main","Stuttgart Motor","Bremen Weser","Hannover Messe","Koln Dom"],
            "2部": ["Bochum Ruhr","Freiburg Blackforest","Augsburg Fugger","Kiel Fjord","Nurnberg Burg",
                    "Dresden Elbe","Heidenheim Brenz","Regensburg Donau","Rostock Hanse","Paderborn Senne"]
        },
        "Netherlands": {
            "1部": ["Amsterdam Canal","Rotterdam Harbor","Utrecht Dom","Eindhoven Light","Alkmaar Cheese",
                    "Arnhem Bridge","Groningen North","Nijmegen Waalkade","Zwolle IJssel","Heerenveen Frisia"],
            "2部": ["Maastricht Meuse","Tilburg Textile","Breda Nassau","Leeuwarden Crown","Venlo Maas",
                    "Dordrecht Delta","Deventer Trade","Emmen Drenthe","Sittard Fortuna","Helmond Brabants"]
        },

        # ★ Italy を 2部構成に変更 ★
        "Italy": {
            "1部": ["Turin Bull","Milan Navigli","Rome Colosseum","Naples Vesuvio","Florence Arno",
                    "Genoa Harbor","Bologna Portico","Verona Arena","Palermo Citrus","Cagliari Sardinia"],
            "2部": ["Parma Duchy","Spezia Gulf","Bari Adriatic","Udine Friuli","Reggio Tricolor",
                    "Perugia Griffin","Catania Etna","Brescia Leonessa","Pisa Tower","Lecce Salento"]
        },

        # 以下 1部のみ
        "Brazil": {"1部": ["Rio Aurora","Sao Paulo Atlas","Bahia Mariners","Porto Alegre Gauchos","Recife Coral",
                            "Curitiba Pines","Fortaleza Sun","Brasilia Federal","Manaus Jungle","Belo Horizonte Iron"]},
        "Portugal": {"1部": ["Lisbon Tramway","Porto Douro","Braga Minho","Coimbra Mondego","Faro Algarve",
                              "Funchal Madeira","Aveiro Lagoon","Setubal Sado","Guimaraes Castle","Evora Roman"]},
        "Belgium": {"1部": ["Brussels Atom","Antwerp Diamond","Bruges Canal","Ghent Graven","Liege Steel",
                            "Charleroi Coal","Leuven Beer","Mechelen Clock","Genk Mine","Kortrijk Textile"]},
        "Turkey": {"1部": ["Istanbul Bosphorus","Ankara Anatolia","Izmir Aegean","Bursa Silk","Antalya Riviera",
                           "Konya Plateau","Trabzon BlackSea","Kayseri Erciyes","Adana Citrus","Gaziantep Pistachio"]},
        "Argentina": {"1部": ["Buenos Aires Tango","Cordoba Sierras","Rosario River","Mendoza Andes","La Plata Students",
                               "Mar del Plata Surf","San Juan Sun","Tucuman Sugar","Salta Valley","Bahia Blanca Wind"]},
        "Uruguay": {"1部": ["Montevideo Anchor","Colonia River","Rivera Border","Maldonado Coast","Salto Thermal",
                             "Paysandu Mills","Tacuarembo Gaucho","Durazno Orange","Florida Meadow","Rocha Ocean"]},
        "Colombia": {"1部": ["Bogota Andes","Medellin Coffee","Cali Sugarcane","Barranquilla Carnival","Cartagena Wall",
                              "Bucaramanga Gold","Pereira Otun","Manizales Snow","Santa Marta Pearl","Cucuta Border"]},
        "USA": {"1部": ["NY Empire","LA Coast","Chicago Wind","Houston Space","Miami Wave",
                         "Seattle Rain","Boston Harbor","Dallas LoneStar","SF Bay","Philly Liberty"]},
        "Mexico": {"1部": ["Mexico City Aztec","Guadalajara Pearl","Monterrey Steel","Puebla Volcano","Tijuana Border",
                           "Leon Emerald","Toluca Nevado","Veracruz Gulf","Merida Maya","Cancun Coral"]},
        "Saudi Arabia": {"1部": ["Riyadh Falcons","Jeddah RedSea","Dammam Oilers","Taif Roses","Medina Dates",
                                 "Abha Asir","Tabuk Desert","Al Khobar Coast","Hail Caravan","Yanbu Harbor"]},
        "Nigeria": {"1部": ["Lagos Lagoon","Abuja Unity","Kano Emir","Port Harcourt Oil","Ibadan Brown",
                             "Enugu Coal","Kaduna Croc","Benin Bronze","Jos Plateau","Maiduguri Sahel"]},
        "Morocco": {"1部": ["Casablanca Atlas","Rabat Oudaya","Marrakech Red","Fes Medina","Tangier Strait",
                            "Agadir Ocean","Oujda Oriental","Meknes Imperial","Tetouan Rif","Safi Ceramic"]},
        "South Korea": {"1部": ["Seoul Han","Busan Harbor","Incheon Sky","Daegu Apple","Daejeon Expo",
                                "Gwangju Light","Ulsan Steel","Suwon Fortress","Jeonju Bibim","Jeju Islanders"]},
        "Australia": {"1部": ["Sydney Harbour","Melbourne Laneway","Brisbane River","Perth Sand","Adelaide Wine",
                               "Canberra Capital","Hobart Derwent","Darwin TopEnd","Gold Coast Surf","Newcastle Steel"]}
    }

    # 自クラブ名を1部のどこかと差し替え
    flat = sum([sum(v.values(), []) for v in leagues.values()], [])
    if my_club not in flat:
        leagues["England"]["1部"][0] = my_club
    return leagues

# ----- スタンドings DataFrame 生成 -----
def build_standings(leagues:dict)->pd.DataFrame:
    rows=[]
    for nation, divs in leagues.items():
        for div, clubs in divs.items():
            for c in clubs:
                rows.append({"Club":c,"Nation":nation,"Division":div,
                             "W":0,"D":0,"L":0,"GF":0,"GA":0,"Pts":0})
    return pd.DataFrame(rows)

# ----- 選手生成 -----
def gen_players(n:int, youth:bool, club:str, nation_code:str)->pd.DataFrame:
    used = st.session_state.name_used
    lst=[]
    for _ in range(n):
        nat = nation_code if random.random()<0.5 else random.choice(NATIONS)
        name = gen_unique_name(nat, used)
        pos = random.choices(["GK","DF","MF","FW"], weights=[1,4,5,3])[0]
        base_min, base_max = (52,82) if youth else (60,90)
        stats = {k: random.randint(base_min, base_max) for k in ABILITY_KEYS}
        stats = apply_bias(stats, nat)
        ovr = int(np.mean(list(stats.values())))
        styles = random.sample(pick_style_pool(nat), k=random.randint(1,3))
        growth = random.choice(pick_growth_pool(nat))
        lst.append({
            "Name":name,"Nat":nat,"Pos":pos,"Age":random.randint(15,18) if youth else random.randint(19,34),
            **stats,"OVR":ovr,"Matches_Played":0,"Goals":0,"Assists":0,"IntCaps":0,
            "Fatigue":0,"Injured":False,"Salary":random.randint(30_000,120_000) if youth else random.randint(120_000,1_200_000),
            "Contract":random.randint(1,2) if youth else random.randint(2,4),
            "Youth":youth,"Club":club,"PlayStyle":styles,"GrowthType":growth,"Value":normalize_value(ovr*random.randint(3500,5500)//100),
            "Status":"通常"
        })
    return pd.DataFrame(lst)

# ----- セッション初期化 -----
def init_session():
    ses = st.session_state
    if 'initialized' in ses: return
    ses.initialized = True
    ses.name_used = set()

    ses.my_club = "Signature Team"
    ses.leagues = build_leagues(ses.my_club)
    ses.standings = build_standings(ses.leagues)

    ses.senior = gen_players(30, False, ses.my_club, "ENG")
    ses.youth  = gen_players(20, True,  ses.my_club, "ENG")

    others = [c for c in ses.standings.Club if c!=ses.my_club]
    pool_list=[]
    for club in others:
        nat_code = random.choice(NATIONS)
        df = gen_players(15, False, club, nat_code)
        pool_list.append(df)
    ses.ai_players = pd.concat(pool_list, ignore_index=True)

    ses.week = 1
    ses.finance_log = []
    ses.budget = 5_000_000
    ses.player_history = {}
    ses.auto_selected = False
    ses.starters = []
    ses.match_log = []
    ses.scout_pool = pd.DataFrame()
    ses.intl_tournament = {}
    ses.rank_cache = {}
    ses.need_positions = suggest_positions(ses.senior)

init_session()

# =========================
# Part 4 / 10  --- 各種ユーティリティ関数群
# =========================

# ----- 整合性補正（IntCaps→IntlApps 等）-----
def _fix_columns():
    for dfname in ['senior','youth','ai_players']:
        df = getattr(st.session_state, dfname)
        if 'IntCaps' in df.columns and 'IntlApps' not in df.columns:
            df.rename(columns={'IntCaps':'IntlApps'}, inplace=True)
        if 'IntlApps' not in df.columns:
            df['IntlApps'] = 0
        setattr(st.session_state, dfname, df)

_fix_columns()

# ----- クラブ→(Nation,Division)辞書 -----
def build_club_map(standings_df:pd.DataFrame)->dict:
    mp={}
    for _,r in standings_df.iterrows():
        mp[r['Club']] = (r['Nation'], r['Division'])
    return mp

st.session_state.club_map = build_club_map(st.session_state.standings)

# ----- 試合結果適用 -----
def apply_result(st_df:pd.DataFrame, home, away, gh, ga):
    # 勝敗・Pts
    if gh>ga:
        st_df.loc[st_df.Club==home, ['W','Pts']] += [1,3]
        st_df.loc[st_df.Club==away, 'L'] += 1
    elif gh<ga:
        st_df.loc[st_df.Club==away, ['W','Pts']] += [1,3]
        st_df.loc[st_df.Club==home, 'L'] += 1
    else:
        st_df.loc[st_df.Club.isin([home,away]), 'D'] += 1
        st_df.loc[st_df.Club.isin([home,away]), 'Pts'] += 1
    # 得失点
    st_df.loc[st_df.Club==home, ['GF','GA']] += [gh, ga]
    st_df.loc[st_df.Club==away, ['GF','GA']] += [ga, gh]
    return st_df

# ----- オファー判定 -----
def offer_result(row, wage, years, fee, my_budget, policy):
    want_wage = row['OVR']*120 + random.randint(-3000,3000)
    want_fee  = row['Value']
    coef = 0.8 if policy=='seller' else (1.2 if policy=='hold' else 1.0)
    wage_ok = wage >= want_wage
    fee_ok  = fee  >= want_fee*coef
    club_ok = random.random() < (0.7 if policy=='seller' else (0.4 if policy=='hold' else 0.55))
    money_ok= my_budget >= fee
    return (wage_ok and fee_ok and club_ok and money_ok), want_wage, int(want_fee*coef)

def rental_result(row, weeks, fee, my_budget, policy):
    demand = int(row['Value']*0.15 + weeks*800)
    ok_fee = fee >= demand
    ok_club= random.random() < (0.65 if policy!='hold' else 0.4)
    return (ok_fee and ok_club and my_budget>=fee), demand

# ----- レンタル期限チェック -----
def tick_rentals(df, week, pending_list):
    for i,r in df.iterrows():
        if r.get('RentalUntil') is not None and week > r['RentalUntil'] and str(r.get('Status','')).startswith("レンタル中"):
            pending_list.append(r['Name'])
            df.at[i,'Status'] = "レンタル満了"
    return df, pending_list

# ----- レンタル満了処理UI -----
def handle_rental_expirations():
    ses = st.session_state
    if not ses.get('rental_pending'):
        return
    st.markdown("### レンタル満了選手の処理")
    all_df = pd.concat([ses.senior, ses.youth], ignore_index=True)
    for nm in ses.rental_pending[:]:
        row = all_df[all_df['Name']==nm]
        if row.empty:
            ses.rental_pending.remove(nm)
            continue
        r = row.iloc[0]
        st.write(f"**{r['Name']}** | Pos:{r['Pos']} | OVR:{r['OVR']} | 元:{r.get('RentalFrom')} | 買取OP:{fmt_money(r.get('OptionFee',0))}")
        c1,c2 = st.columns(2)
        with c1:
            if st.button(f"買取する（{fmt_money(r.get('OptionFee',0))}）", key=f"buy_{nm}"):
                if ses.budget >= r.get('OptionFee',0):
                    ses.budget -= r.get('OptionFee',0)
                    for df in ['senior','youth']:
                        idx = getattr(ses,df).index[getattr(ses,df)['Name']==nm]
                        if len(idx)>0:
                            getattr(ses,df).loc[idx, ['Club','RentalFrom','RentalUntil','OptionFee','Status']] = \
                                [ses.my_club, None, None, None, "通常"]
                            break
                    st.success("買取成立！")
                    ses.rental_pending.remove(nm)
                else:
                    st.error("予算不足です。")
        with c2:
            if st.button("返却する", key=f"return_{nm}"):
                origin = r.get('RentalFrom')
                # 自クラブDFから削除
                for df in ['senior','youth']:
                    idx = getattr(ses,df).index[getattr(ses,df)['Name']==nm]
                    if len(idx)>0:
                        bak = getattr(ses,df).loc[idx[0]].copy()
                        getattr(ses,df).drop(idx, inplace=True)
                        break
                # 元クラブへ戻す -> ai_playersへ
                bak['Club']=origin
                bak[['RentalFrom','RentalUntil','OptionFee','Status']] = [None,None,None,"通常"]
                ses.ai_players = pd.concat([ses.ai_players, pd.DataFrame([bak])], ignore_index=True)
                st.info("返却完了")
                ses.rental_pending.remove(nm)

# ----- スカウト候補生成 -----
def gen_scout_candidates(n=8, youth=False):
    ses = st.session_state
    pool = pd.concat([ses.ai_players, ses.senior, ses.youth], ignore_index=True)
    if youth:
        pool = pool[pool['Age']<=18]
    else:
        pool = pool[pool['Age']>=19]

    # Free生成
    free_df = gen_players(max(1,n//2), youth=youth, club="Free", nation_code=random.choice(NATIONS))
    # 他クラブ
    others = pool[(pool['Club']!="Free") & (pool['Club']!=ses.my_club)]
    take = n - len(free_df)
    pick_df = others.sample(min(take, len(others))) if len(others)>0 else pd.DataFrame()
    cands = pd.concat([free_df, pick_df], ignore_index=True)

    # 表示用加工
    cands['PlayStyle'] = cands['PlayStyle'].apply(lambda x: " / ".join(x))
    cands['Value'] = cands['Value'].apply(normalize_value)
    return cands.sample(frac=1).reset_index(drop=True)

def get_rental_candidates():
    ses = st.session_state
    pool = ses.ai_players
    return pool[(pool['Club']!=ses.my_club) & (pool.get('RentalFrom').isna() if 'RentalFrom'in pool else True)]

# ----- 国際大会自動進行 -----
def auto_intl_round():
    ses = st.session_state
    if 'intl_tournament' not in ses or not ses.intl_tournament:
        # 各国1部上位2クラブ
        clubs=[]
        for nation, divs in ses.leagues.items():
            if "1部" in divs:
                table = ses.standings[(ses.standings.Nation==nation) & (ses.standings.Division=="1部")]
                top2 = table.sort_values('Pts', ascending=False).head(2)['Club'].tolist()
                clubs.extend(top2)
        random.shuffle(clubs)
        ses.intl_tournament = {"clubs":clubs, "results":[], "finished":False}
        return

    if ses.intl_tournament.get("finished"):  # 終了
        return
    clubs = ses.intl_tournament['clubs']
    if len(clubs)<=1:
        ses.intl_tournament["finished"]=True
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

        # 個人成績（簡易：勝者側の上位11人にランダム配点）
        pool_all = pd.concat([ses.senior, ses.youth, ses.ai_players], ignore_index=True)
        XI1 = pool_all[pool_all['Club']==c1].nlargest(11,'OVR')
        XI2 = pool_all[pool_all['Club']==c2].nlargest(11,'OVR')

        if 'intl_player_stats' not in ses:
            ses.intl_player_stats={}
        # ゴール・アシスト割り振り
        for club, goals in [(c1,g1),(c2,g2)]:
            XI = XI1 if club==c1 else XI2
            if XI.empty: 
                continue
            for _ in range(goals):
                pid = XI.sample(1).index[0]
                name = XI.loc[pid,'Name']
                pos  = XI.loc[pid,'Pos']
                ses.intl_player_stats.setdefault(name, {'G':0,'A':0,'Club':club,'Pos':pos})
                ses.intl_player_stats[name]['G'] += 1
                # assist
                pid2 = XI.sample(1).index[0]
                name2 = XI.loc[pid2,'Name']
                pos2  = XI.loc[pid2,'Pos']
                ses.intl_player_stats.setdefault(name2, {'G':0,'A':0,'Club':club,'Pos':pos2})
                ses.intl_player_stats[name2]['A'] += 1

        # 自クラブ選手の国際試合数増やす
        if c1==ses.my_club or c2==ses.my_club:
            starters_names = ses.starters if ses.starters else ses.senior.nlargest(11,'OVR')['Name'].tolist()
            for nm in starters_names:
                for dfn in ['senior','youth']:
                    idx = getattr(ses,dfn).index[getattr(ses,dfn)['Name']==nm]
                    if len(idx)>0:
                        getattr(ses,dfn).at[idx[0],'IntlApps'] = getattr(ses,dfn).at[idx[0],'IntlApps'] + 1

        winners.append(win)
    if len(clubs)%2==1:
        winners.append(clubs[-1])
    ses.intl_tournament['clubs']=winners
    if len(winners)==1:
        ses.intl_tournament['finished']=True
        ses.sns_posts.append(f"[国際大会] 優勝: {winners[0]}")
        ses.sns_times.append(datetime.now())

# =========================
# Part 5 / 10  --- タブ定義 / シニア / ユース / 選手詳細
# =========================

ses = st.session_state
if 'rental_pending' not in ses: ses.rental_pending = []

# ---------- タブ定義 ----------
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

    if df_s.empty:
        st.markdown("<div class='tab-info'>選手データがありません。</div>", unsafe_allow_html=True)
    else:
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

    if df_y.empty:
        st.markdown("<div class='tab-info'>ユース選手がいません。</div>", unsafe_allow_html=True)
    else:
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

        # レーダーチャート
        vals = [prow[k] for k in ABILITY_KEYS]
        fig_r = radar_chart(vals, ABILITY_KEYS)
        st.pyplot(fig_r)

        # 成長履歴
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
# Part 6 / 10  --- 試合 / 順位表
# =========================

def update_standings_global(home, away, gh, ga):
    df = ses.standings
    # 勝敗
    if gh > ga:
        df.loc[df.Club==home, ['W','Pts']] += [1,3]
        df.loc[df.Club==away, 'L'] += 1
    elif gh < ga:
        df.loc[df.Club==away, ['W','Pts']] += [1,3]
        df.loc[df.Club==home, 'L'] += 1
    else:
        df.loc[df.Club.isin([home,away]), 'D'] += 1
        df.loc[df.Club.isin([home,away]), 'Pts'] += 1
    # 得失点
    df.loc[df.Club==home, ['GF','GA']] += [gh, ga]
    df.loc[df.Club==away, ['GF','GA']] += [ga, gh]
    ses.standings = df

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
        st.warning("『オート先発選考』を行ってください。")

    # 自クラブの所属リーグからランダムな相手選出
    my_nat, my_div = ses.club_map[ses.my_club]
    same_league = ses.standings[(ses.standings.Nation==my_nat)&(ses.standings.Division==my_div)]
    opp_choices = [c for c in same_league.Club if c!=ses.my_club]
    opp = random.choice(opp_choices) if opp_choices else ses.my_club

    kickoff = st.button("キックオフ", disabled=(not ses.auto_selected or ses.week>SEASON_WEEKS))
    if kickoff:
        # 自チーム攻撃力
        atk = ses.senior[ses.senior['Name'].isin(ses.starters)]['OVR'].mean() if ses.starters else 70
        oppatk = random.uniform(60,90)

        gh = max(0,int(np.random.normal((atk-60)/8,1)))
        ga = max(0,int(np.random.normal((oppatk-60)/8,1)))

        shots = random.randint(5,15)
        on_t  = random.randint(0,shots)
        poss  = random.randint(40,60)

        # ゴール/アシスト記録
        scorers=[]; assisters=[]
        if gh>0 and ses.starters:
            for _ in range(gh):
                s = random.choice(ses.starters)
                a_candidates = [x for x in ses.starters if x!=s]
                a = random.choice(a_candidates) if a_candidates else s
                scorers.append(s); assisters.append(a)
                ses.senior.loc[ses.senior['Name']==s,'Goals']   += 1
                ses.senior.loc[ses.senior['Name']==a,'Assists'] += 1

        # スタンディング更新
        update_standings_global(ses.my_club, opp, gh, ga)

        # 他試合
        all_pairs_done={(ses.my_club,opp)}
        for nation, divs in ses.leagues.items():
            for div, clubs in divs.items():
                cl = clubs.copy()
                random.shuffle(cl)
                for i in range(0,len(cl),2):
                    if i+1>=len(cl): break
                    h,a = cl[i], cl[i+1]
                    if (h,a) in all_pairs_done or (a,h) in all_pairs_done: continue
                    g1,g2 = random.randint(0,3), random.randint(0,3)
                    update_standings_global(h,a,g1,g2)
                    all_pairs_done.add((h,a))

        # ログ・SNS・財務
        ses.match_log.append({'week':ses.week,'opp':opp,'gf':gh,'ga':ga,'scorers':scorers,'assisters':assisters})
        ses.sns_posts.append(f"{ses.my_club} {gh}-{ga} {opp} | 得点: {', '.join(scorers) if scorers else 'なし'}")
        ses.sns_times.append(datetime.now())
        ses.finance_log.append({
            'week': ses.week,
            'revenue_ticket': gh*15000 + random.randint(5000,10000),
            'revenue_goods' : ga*8000  + random.randint(1000,5000),
            'expense_salary': int(ses.senior['OVR'].mean()*1000)
        })

        # 成長
        ses.senior = apply_growth(ses.senior, ses.week)
        for _,rw in ses.senior.iterrows():
            update_player_history(rw['Name'], rw, ses.week)

        st.success(f"結果 {gh}-{ga}")
        if scorers:   st.write("得点者: " + " / ".join(scorers))
        if assisters: st.write("アシスト: " + " / ".join(assisters))
        st.write(f"シュート:{shots}（枠内:{on_t}） / ポゼッション:{poss}%")

        ses.week += 1
        ses.auto_selected = False  # 次節も選考必須
        auto_intl_round()

        if ses.week > SEASON_WEEKS:
            st.success("シーズン終了！『年間表彰』タブ等をご確認ください。")

    elif ses.week > SEASON_WEEKS:
        st.info("シーズン終了済です。『クラブ設定』で新シーズン開始など調整してください。")

# ---------- 4) 順位表 ----------
with tabs[4]:
    st.markdown('<div style="color:#fff;font-size:20px;">順位表</div>', unsafe_allow_html=True)
    nations = list(ses.leagues.keys())
    sel_nat = st.selectbox("国を選択", nations)
    sel_div = st.selectbox("ディビジョンを選択", list(ses.leagues[sel_nat].keys()))
    df_st = ses.standings[(ses.standings.Nation==sel_nat)&(ses.standings.Division==sel_div)].copy()
    df_st = df_st.sort_values(['Pts','GF-GA','GF'], ascending=[False,False,False]).reset_index(drop=True)
    st.dataframe(
        df_st.style.apply(make_highlighter('Club', ses.my_club), axis=1)
            .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )
# =========================
# Part 8 / 10  --- 年間表彰 / ランキング&国際大会 / クラブ設定
# =========================

# -------- 9) 年間表彰 --------
with tabs[9]:
    st.markdown('<div style="color:white;font-size:20px;">年間表彰</div>', unsafe_allow_html=True)

    df_all_my = pd.concat([ses.senior, ses.youth], ignore_index=True)
    for col in ['Goals','Assists']:
        if col not in df_all_my: df_all_my[col]=0

    top5g = df_all_my.nlargest(5,'Goals')[['Name','Pos','Goals','Club']]
    top5a = df_all_my.nlargest(5,'Assists')[['Name','Pos','Assists','Club']]

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

    # --- 国際大会試合ログ ---
    st.markdown("### 🌍 国際大会 試合ログ")
    if not ses.intl_tournament or len(ses.intl_tournament.get('results',[]))==0:
        st.markdown("<div class='tab-info'>国際大会は未開催です。試合を進めると自動で進行します。</div>", unsafe_allow_html=True)
    else:
        for idx,m in enumerate(ses.intl_tournament['results']):
            # m = (c1,g1,c2,g2,pk_txt,win)
            line = f"【R{idx+1}】 {m[0]} {m[1]}-{m[3]} {m[2]} {m[4]} → 勝者:{m[5]}"
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

    # --- 国際大会 個人成績 ---
    st.markdown("### 🏆 国際大会 個人成績ランキング")
    if not ses.get('intl_player_stats'):
        st.markdown("<div class='tab-info'>国際大会の個人成績データがまだありません。</div>", unsafe_allow_html=True)
    else:
        df_intp = pd.DataFrame.from_dict(ses.intl_player_stats, orient='index')
        # ensure columns
        for c in ['G','A','Club','Pos','Name']:
            if c not in df_intp.columns:
                df_intp[c]=0
        df_intp['Name'] = df_intp.index

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
        st.markdown("**⚽️ 国際大会ベストイレブン（ポジション別成績上位）**")
        st.dataframe(
            best11.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                        .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

    st.markdown("---")

    # --- 各国リーグランキングまとめ ---
    st.markdown("### 🇪🇺 各国リーグランキング（順位表・得点王・アシスト王・ベスト11）")
    df_all = pd.concat([ses.senior, ses.youth, ses.ai_players], ignore_index=True)
    for col in ['Goals','Assists']:
        if col not in df_all: df_all[col]=0
    df_all['Nation'] = df_all['Club'].map(lambda c: ses.club_map.get(c,("",""))[0] if c in ses.club_map else "")
    df_all['Division'] = df_all['Club'].map(lambda c: ses.club_map.get(c,("",""))[1] if c in ses.club_map else "")

    for nation, divs in ses.leagues.items():
        st.markdown(f"## {nation}")
        for div in divs.keys():
            st.markdown(f"#### {div} 順位表")
            df_st = ses.standings[(ses.standings.Nation==nation)&(ses.standings.Division==div)].copy()
            # GD列
            df_st['GD'] = df_st['GF']-df_st['GA']
            df_st = df_st.sort_values(['Pts','GD','GF'], ascending=[False,False,False]).reset_index(drop=True)
            st.dataframe(
                df_st.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                    .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
                use_container_width=True
            )

            sub = df_all[(df_all['Nation']==nation) & (df_all['Division']==div)].copy()
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
            for p in ['GK','DF','MF','FW']:
                need = 1 if p=='GK' else (4 if p in ['DF','MF'] else 2)
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

# -------- 11) クラブ設定 --------
with tabs[11]:
    st.markdown('<div style="color:white;font-size:20px;">クラブ設定</div>', unsafe_allow_html=True)
    new_name = st.text_input("自クラブ名", value=ses.my_club, max_chars=40)
    if st.button("クラブ名変更"):
        if new_name and new_name != ses.my_club:
            old = ses.my_club
            ses.my_club = new_name

            # standings / leagues 更新処理
            ses.leagues = build_leagues(ses.my_club)
            ses.standings = build_standings(ses.leagues)
            ses.club_map = build_club_map(ses.standings)

            # 所属変更
            for dfname in ['senior','youth']:
                df = getattr(ses, dfname)
                df.loc[df['Club']==old,'Club']=ses.my_club
                setattr(ses, dfname, df)

            st.success("クラブ名を変更しました。アプリを再実行してください。")

    st.markdown("---")
    st.markdown("### シーズン管理")
    if st.button("新シーズン開始"):
        ses.week = 1
        # standingsを初期化
        ses.standings = build_standings(ses.leagues)
        # 選手の成長履歴クリア
        ses.player_history = {}
        ses.finance_log.clear()
        ses.match_log.clear()
        ses.intl_tournament.clear()
        ses.intl_player_stats={}
        ses.sns_posts.clear(); ses.sns_times.clear()
        ses.rental_pending=[]
        st.success("新シーズン開始！")

# =========================
# Part 9 / 10  --- ハウスキーピング / 整合性補正
# =========================

def housekeeping():
    ses = st.session_state

    # 未定義ガード
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

    # スタンドング再ソート
    ses.standings = ses.standings.sort_values(['Nation','Division','Pts','GF'], ascending=[True,True,False,False]).reset_index(drop=True)

    # クラブマップ更新
    ses.club_map = build_club_map(ses.standings)

    # 補強推奨再計算
    ses.need_positions = suggest_positions(ses.senior)

housekeeping()

# =========================
# Part 10 / 10  --- 終端処理
# =========================

st.caption("✅ 全コード読み込み完了。問題があればエラーメッセージ先頭をお知らせください。")
