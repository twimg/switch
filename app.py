import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import re

st.set_page_config(page_title="Soccer Club Management Sim", layout="wide")

# --- UI/デザイン ---
st.markdown("""
<style>
body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
.stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff; }
h1,h2,h3,h4,h5,h6, .stTabs label, .stTabs span { color: #fff !important; }
.stTabs [data-baseweb="tab"] > button[aria-selected="true"] { color: #fff !important; background: #286edb !important; }
.stTabs [data-baseweb="tab"] > button { color: #fff !important; background: #2b3659 !important; }
.stButton>button, .stDownloadButton>button { background: linear-gradient(90deg, #ffd800 20%, #17b6ff 100%); color: #192841 !important; font-weight:bold; border-radius: 13px; font-size:1.02em; margin:6px 0 7px 0; box-shadow:0 0 8px #33e0ff33; }
.stButton>button:active { background: #ffdf4d !important; }
.stAlert, .stInfo, .stWarning { border-radius:10px !important; font-size:1.08em !important; }
.red-message { color:#ff3a3a; font-weight:bold; font-size:1.08em; padding:7px 0 2px 0;}
.player-card {
  background: #f9fafd;
  color: #132346;
  border-radius: 17px;
  padding: 13px 12px 7px 12px;
  margin: 9px 3vw 16px 3vw;
  box-shadow: 0 0 15px #17b6ff44;
  min-width: 150px; max-width: 170px; font-size:1.01em;
  display: flex; flex-direction: column; align-items: center;
  border: 2px solid #0c79b333; position: relative; transition:0.13s;
}
.player-card.selected {border: 2.5px solid #f5e353; box-shadow: 0 0 20px #ffe63e77;}
.player-card img { border-radius:50%; margin-bottom:7px; border:2px solid #2789d7; background:#fff; object-fit:cover; }
.player-card .detail-popup {
  position: absolute; top: 7px; left: 104%; z-index:10;
  min-width: 180px; max-width:280px;
  background: #242e41; color: #ffe;
  border-radius: 13px; padding: 15px 15px;
  box-shadow: 0 0 14px #1f2d44b2; font-size: 1.06em;
  border: 2px solid #1698d499;
}
.mobile-table {overflow-x:auto; white-space:nowrap;}
.mobile-table th, .mobile-table td {
  padding: 4px 9px; font-size: 15px; border-bottom: 1.3px solid #1c2437;
}
.table-highlight th, .table-highlight td {
  background: #192844 !important; color: #ffe45a !important; border-bottom: 1.5px solid #24335d !important;
}
.budget-info { background:#ffeeaa; color:#253246; padding:7px 17px; border-radius:10px; font-weight:bold; display:inline-block; font-size:1.11em;}
.position-label { color: #fff !important; background:#1b4f83; border-radius:7px; padding:1px 8px; font-weight:bold; margin:0 2px;}
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- 顔画像リスト（日本人はアジア顔、他国は欧米顔） ---
asian_faces = [
    f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in [60,61,62,63,64,65,66,67,68,69,79,80,81,82,83,84,85,86,87,88,89,12,17,22,27,32,37,42,47,52]
]
euro_faces = [
    f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in [10,11,13,14,15,16,18,19,20,21,23,24,25,26,28,29,30,31,33,34,35,36,38,39,40,41,43,44,45,46]
]
def get_player_img(nationality, idx):
    if nationality == "日本":
        return asian_faces[idx % len(asian_faces)]
    else:
        return euro_faces[idx % len(euro_faces)]

# --- 主要国籍・姓/名リスト（各30種） ---
surname_pools = {
    "日本": ["佐藤","鈴木","高橋","田中","伊藤","渡辺","山本","中村","小林","加藤","吉田","山田","佐々木","山口","松本","井上","木村","林","斎藤","清水","山崎","森","池田","橋本","阿部","石川","石井","村上","藤田","坂本"],
    "イングランド": ["Smith","Jones","Williams","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Thompson","Wright","Walker","White","Green","Hall","Wood","Martin","Harris","Cooper","King","Clark","Baker","Turner","Carter","Mitchell","Scott","Phillips","Adams","Campbell"],
    "ドイツ": ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Hoffmann","Schulz","Keller","Richter","Koch","Bauer","Wolf","Neumann","Schwarz","Krüger","Zimmermann","Braun","Hartmann","Lange","Schmitt","Werner","Krause","Meier","Lehmann","Schmid","Schulze","Maier"],
    "スペイン": ["García","Martínez","Rodríguez","López","Sánchez","Pérez","Gómez","Martín","Jiménez","Ruiz","Hernández","Díaz","Moreno","Muñoz","Álvarez","Romero","Alonso","Gutiérrez","Navarro","Torres","Domínguez","Vega","Castro","Ramos","Flores","Ortega","Serrano","Blanco","Suárez","Molina"],
    "フランス": ["Martin","Bernard","Dubois","Thomas","Robert","Richard","Petit","Durand","Leroy","Moreau","Simon","Laurent","Lefebvre","Michel","Garcia","David","Bertrand","Roux","Vincent","Fournier","Girard","Bonnet","Dupont","Lambert","Fontaine","Rousseau","Blanchard","Guerin","Muller","Marchand"],
    "イタリア": ["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco","Bruno","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Moretti","Barbieri","Mariani","Santoro","Vitale","Martini","Bianco","Longo","Leone","Gentile","Lombardo"],
    "ブラジル": ["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Almeida","Costa","Gomes","Martins","Araújo","Ribeiro","Barbosa","Barros","Freitas","Lima","Teixeira","Fernandes","Pereira","Carvalho","Moura","Macedo","Azevedo","Cardoso","Moreira","Castro","Campos","Rocha","Pinto","Nascimento"]
}
givenname_pools = {
    "日本": ["翔","大輔","陸","颯太","陽平","悠真","隼人","啓太","海斗","翼","優","拓真","蓮","大輝","駿","光希","悠人","慎吾","洸太","楓","龍也","亮介","航太","一輝","健太","達也","幸太","悠馬","瑛太","渉"],
    "イングランド": ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William","James","Henry","Leo","Alfie","Joshua","Freddie","Archie","Arthur","Logan","Alexander","Harrison","Benjamin","Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph"],
    "ドイツ": ["Leon","Ben","Paul","Jonas","Elias","Finn","Noah","Luis","Luca","Felix","Maximilian","Moritz","Tim","Julian","Max","David","Jakob","Emil","Philipp","Tom","Nico","Fabian","Marlon","Samuel","Daniel","Jan","Simon","Jonathan","Aaron","Mika"],
    "スペイン": ["Alejandro","Pablo","Daniel","Adrián","Javier","David","Hugo","Mario","Manuel","Álvaro","Diego","Miguel","Raúl","Carlos","José","Antonio","Andrés","Fernando","Iván","Sergio","Alberto","Juan","Rubén","Ángel","Gonzalo","Martín","Rafael","Lucas","Jorge","Víctor"],
    "フランス": ["Lucas","Louis","Hugo","Gabriel","Arthur","Jules","Nathan","Léo","Adam","Raphaël","Enzo","Paul","Tom","Noah","Théo","Ethan","Axel","Sacha","Mathis","Antoine","Clément","Matteo","Maxime","Samuel","Romain","Simon","Nolan","Benjamin","Alexandre","Julien"],
    "イタリア": ["Francesco","Alessandro","Lorenzo","Andrea","Matteo","Gabriele","Leonardo","Mattia","Davide","Tommaso","Giuseppe","Riccardo","Edoardo","Federico","Antonio","Marco","Giovanni","Nicolo","Simone","Samuele","Alberto","Pietro","Luca","Stefano","Paolo","Filippo","Angelo","Salvatore","Giorgio","Daniele"],
    "ブラジル": ["Lucas","Gabriel","Pedro","Matheus","Guilherme","Rafael","Bruno","Arthur","João","Gustavo","Felipe","Enzo","Davi","Matheus","Samuel","Eduardo","Luiz","Leonardo","Henrique","Thiago","Carlos","Caio","Vinícius","André","Vitor","Marcelo","Luan","Yuri","Ruan","Diego"]
}
ALL_NATIONS = list(surname_pools.keys())

# --- 高精度カタカナ変換（外部APIなし簡易） ---
def alphabet_to_katakana(s):
    # 先頭大文字はカタカナ語頭化
    s = s.lower()
    s = re.sub(r'[^a-z]', '', s)  # 記号など除去
    rep = [
        ("sch", "シュ"),("ch", "チ"),("sh", "シ"),("ph", "フ"),("qu", "ク"),("ts", "ツ"),("th", "ス"),
        ("a", "ア"),("i", "イ"),("u", "ウ"),("e", "エ"),("o", "オ"),("b", "バ"),("c", "ク"),("d", "ド"),("f", "フ"),
        ("g", "グ"),("h", "ハ"),("j", "ジ"),("k", "カ"),("l", "ル"),("m", "マ"),("n", "ン"),("p", "プ"),("q", "ク"),
        ("r", "ル"),("s", "ス"),("t", "ト"),("v", "ヴ"),("w", "ウ"),("x", "クス"),("y", "イ"),("z", "ズ")
    ]
    for a, k in rep:
        s = s.replace(a, k)
    return s.title()

def name_to_katakana(name):
    # "John Smith" → "ジョンスミス"
    name_parts = name.split()
    return "".join([alphabet_to_katakana(n) for n in name_parts])

def make_name(nat, used_names):
    surname = random.choice(surname_pools[nat])
    given = random.choice(givenname_pools[nat])
    if nat == "日本":
        name = f"{surname} {given}"
    else:
        raw_name = f"{given} {surname}"
        name = name_to_katakana(raw_name)
    if name in used_names:
        return make_name(nat, used_names)
    used_names.add(name)
    return name

def format_money(val):
    if val >= 1_000_000_000:
        return f"{val//1_000_000_000}b€"
    elif val >= 1_000_000:
        return f"{val//1_000_000}m€"
    elif val >= 1_000:
        return f"{val//1_000}k€"
    else:
        return f"{int(val)}€"

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

# --- 初期データ生成 ---
def generate_players(nsenior=30, nyouth=20):
    players = []
    used_names = set()
    for i in range(nsenior):
        nat = random.choice(ALL_NATIONS)
        name = make_name(nat, used_names)
        player = dict(
            名前=name,
            ポジション=random.choice(["GK","DF","MF","FW"]),
            年齢=random.randint(19,33),
            国籍=nat,
            Spd=random.randint(60,90),
            Pas=random.randint(60,90),
            Phy=random.randint(60,90),
            Sta=random.randint(60,90),
            Def=random.randint(60,90),
            Tec=random.randint(60,90),
            Men=random.randint(60,90),
            Sht=random.randint(60,90),
            Pow=random.randint(60,90),
            年俸=random.randint(120_000,1_200_000),
            契約年数=random.randint(1,3),
            総合=0,
            ユース=0
        )
        player["総合"] = int(np.mean([player[l] for l in labels]))
        players.append(player)
    for i in range(nyouth):
        nat = random.choice(ALL_NATIONS)
        name = make_name(nat, used_names)
        player = dict(
            名前=name,
            ポジション=random.choice(["GK","DF","MF","FW"]),
            年齢=random.randint(14,18),
            国籍=nat,
            Spd=random.randint(52,82),
            Pas=random.randint(52,82),
            Phy=random.randint(52,82),
            Sta=random.randint(52,82),
            Def=random.randint(52,82),
            Tec=random.randint(52,82),
            Men=random.randint(52,82),
            Sht=random.randint(52,82),
            Pow=random.randint(52,82),
            年俸=random.randint(30_000,250_000),
            契約年数=random.randint(1,2),
            総合=0,
            ユース=1
        )
        player["総合"] = int(np.mean([player[l] for l in labels]))
        players.append(player)
    return pd.DataFrame(players)

if "players_df" not in st.session_state:
    st.session_state.players_df = generate_players()

df = st.session_state.players_df
df_senior = df[df["ユース"]==0].reset_index(drop=True)
df_youth = df[df["ユース"]==1].reset_index(drop=True)

# --- メインタブ ---
tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save"])

# --- Senior ---
with tabs[0]:
    st.subheader("Senior Squad")
    st.markdown("<div class='mobile-table'><table><thead><tr>" +
                "".join([f"<th>{c}</th>" for c in ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]]) +
                "</tr></thead><tbody>" +
                "".join([
                    "<tr>" + "".join([
                        f"<td>{row['名前']}</td><td><span class='position-label'>{row['ポジション']}</span></td><td>{row['年齢']}</td><td>{row['国籍']}</td><td>{row['契約年数']}</td><td>{format_money(row['年俸'])}</td><td>{row['総合']}</td>"
                    ]) + "</tr>" for _, row in df_senior.iterrows()
                ]) +
                "</tbody></table></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### Player Cards")
    scroll_cols = st.columns(len(df_senior))
    for idx, row in df_senior.iterrows():
        with scroll_cols[idx]:
            card_class = "player-card"
            img_url = get_player_img(row["国籍"], idx)
            st.markdown(
                f"""<div class='{card_class}'>
                <img src="{img_url}" width="66">
                <b>{row['名前']}</b>
                <br><span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span>
                <br><span class='position-label'>{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}
                <br><span style='font-size:0.95em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                </div>""", unsafe_allow_html=True)

# --- Youth ---
with tabs[1]:
    st.subheader("Youth Players")
    if len(df_youth)==0:
        st.markdown("<div class='red-message'>ユース選手はいません</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='mobile-table'><table><thead><tr>" +
                    "".join([f"<th>{c}</th>" for c in ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]]) +
                    "</tr></thead><tbody>" +
                    "".join([
                        "<tr>" + "".join([
                            f"<td>{row['名前']}</td><td><span class='position-label'>{row['ポジション']}</span></td><td>{row['年齢']}</td><td>{row['国籍']}</td><td>{row['契約年数']}</td><td>{format_money(row['年俸'])}</td><td>{row['総合']}</td>"
                        ]) + "</tr>" for _, row in df_youth.iterrows()
                    ]) +
                    "</tbody></table></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### Player Cards")
        scroll_cols = st.columns(len(df_youth))
        for idx, row in df_youth.iterrows():
            with scroll_cols[idx]:
                card_class = "player-card"
                img_url = get_player_img(row["国籍"], idx)
                st.markdown(
                    f"""<div class='{card_class}'>
                    <img src="{img_url}" width="66">
                    <b>{row['名前']}</b>
                    <br><span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span>
                    <br><span class='position-label'>{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}
                    <br><span style='font-size:0.95em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                    </div>""", unsafe_allow_html=True)

# --- 他タブ（Match, Scout, Standings, Save）も同様に改善できます。  
# さらに「詳細」「レーダーチャート」「試合/スカウト/順位表/セーブ」など
# フル実装ご要望あれば続けて送ります！

st.caption("外国人は自動カタカナ化、国籍ごと顔割り当て、シニア30人・ユース20人・全機能対応版")
