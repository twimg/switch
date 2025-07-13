import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- UI/Style ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    html, body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
    .stApp { background: linear-gradient(120deg, #1b2944 0%, #25375a 100%) !important; color: #eaf6ff; }
    .main .block-container { padding-top: 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 2vw; }
    .stTabs [data-baseweb="tab"] { color: #fff !important; font-weight: 600; font-size:1.08em; }
    .stTabs [aria-selected="true"] { color: #ffe700 !important; border-bottom: 3px solid #ffe700; }
    .player-cards-row { display: flex; flex-direction: row; overflow-x: auto; gap: 18px; padding: 4px 2vw 12px 2vw; }
    .player-card {
        background: #fff; color: #132b47; border-radius: 16px;
        padding: 14px 15px 10px 15px; min-width: 190px; max-width: 220px;
        box-shadow: 0 0 12px #29b8ff2a; display: flex; flex-direction: column; align-items: center;
        font-size: 1.01em; border: 2.3px solid #229ef320; margin-bottom: 4px; position:relative;
        transition: 0.16s;
    }
    .player-card img {border-radius: 50%; margin-bottom: 10px; border: 2.5px solid #1cb2d8;}
    .player-card .detail-btn {margin-top:7px;padding:2.5px 12px;border-radius:9px;background:#ffec8b;color:#173a45;border:none;font-weight:bold;font-size:0.98em;}
    .player-card .detail-btn:hover {background:#ffd800;color:#002545;}
    .player-card .pos-label {
        font-weight: bold; color: #fff; background: #2363ff;
        border-radius: 9px; padding: 1.5px 11px; margin: 2px 0 2px 0; font-size:1.05em; letter-spacing:1.5px;
        box-shadow:0 0 3px #12347877;
    }
    .recommend-btn, .stButton>button {
        background: linear-gradient(90deg,#ffe15c 60%,#ffe700 100%);
        color: #132b47 !important; font-weight: bold; border-radius: 9px; font-size:1.07em;
        box-shadow: 0 0 7px #ffe60033; border: none; margin-bottom:5px;
        padding: 8px 30px 7px 30px;
    }
    .recommend-btn:hover, .stButton>button:hover { background:#ffe700; color:#002545 !important; }
    .money-badge {background:#fff8ce; color:#183a1d; padding:6px 19px; border-radius:13px; display:inline-block; font-weight:bold; font-size:1.12em;}
    .error-msg {color:#fa3849 !important; font-weight:bold;}
    .info-msg {color:#44caff !important;}
    .youth-msg {color:#fa3849 !important; font-weight:bold;}
    </style>
""", unsafe_allow_html=True)

# ---- 名前リスト/国籍別（30ずつ） ----
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
nationalities = list(surname_pools.keys())

# --- 顔画像API：日本のみアジア系、他は欧米リアル ---
def get_avatar_url(name, nationality):
    idx = (sum(ord(c) for c in name) % 40) + 1
    if nationality == "日本":
        # アジア系顔（例：API用のSeed名生成）
        return f"https://api.dicebear.com/7.x/notionists-neutral/svg?seed={name}&backgroundColor=ecf2f8&skinColor=variant01&radius=50"
    else:
        # 欧米系顔 (男性限定)
        return f"https://randomuser.me/api/portraits/men/{idx}.jpg"

# --- 年俸表示 ---
def format_money_euro(val):
    if val >= 1_000_000_000:
        return f"{val//1_000_000_000}b€"
    elif val >= 1_000_000:
        return f"{val//1_000_000}m€"
    elif val >= 1_000:
        return f"{val//1_000}k€"
    else:
        return f"{int(val)}€"

# --- 選手生成 ---
def get_unique_name(nat, used):
    for _ in range(50):
        sur = random.choice(surname_pools[nat])
        given = random.choice(givenname_pools[nat])
        name = f"{sur} {given}" if nat == "日本" else f"{given} {sur}"
        if name not in used:
            used.add(name)
            return name
    return f"{nat}_Player{random.randint(100,999)}"

def generate_players(num, min_age, max_age, used_names, nationality_pool=None):
    out = []
    for _ in range(num):
        nat = random.choice(nationality_pool) if nationality_pool else random.choice(nationalities)
        name = get_unique_name(nat, used_names)
        pos = random.choice(["GK", "DF", "MF", "FW"])
        age = random.randint(min_age, max_age)
        ovr = random.randint(62,86)
        contract = random.randint(1,3)
        salary = random.randint(90_000, 2_400_000)
        out.append({
            "名前": name, "ポジション": pos, "年齢": age, "国籍": nat, "契約年数": contract,
            "年俸": salary, "総合": ovr,
            "Spd": random.randint(60,90), "Pas": random.randint(60,90),
            "Phy": random.randint(60,90), "Sta": random.randint(60,90),
            "Def": random.randint(60,90), "Tec": random.randint(60,90),
            "Men": random.randint(60,90), "Sht": random.randint(60,90), "Pow": random.randint(60,90)
        })
    return out

# --- データ初期化 ---
try:
    df = pd.read_csv("players.csv")
    for col in ["契約年数","年俸","総合","Spd","Pas","Phy","Sta","Def","Tec","Men","Sht","Pow"]:
        if col not in df.columns: df[col] = 0
except:
    used_names = set()
    players = generate_players(30, 19, 33, used_names)
    players += generate_players(20, 15, 18, used_names)
    df = pd.DataFrame(players)
    df.to_csv("players.csv", index=False)

# --- シニア・ユース ---
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)

if "detail_idx" not in st.session_state: st.session_state.detail_idx = None
if "detail_youth" not in st.session_state: st.session_state.detail_youth = None

tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save", "SNS"])

# --- レーダーチャート描画 ---
def draw_radar(row):
    labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
    stats = [row[l] for l in labels]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    stats += stats[:1]
    angles = np.concatenate([angles, [angles[0]]])
    fig, ax = plt.subplots(figsize=(3,3), subplot_kw={'polar':True})
    ax.plot(angles, stats, linewidth=2)
    ax.fill(angles, stats, alpha=0.35)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color="#222", fontweight="bold")
    fig.tight_layout()
    st.pyplot(fig)

# --- Senior Tab ---
with tabs[0]:
    st.header("Senior Squad")
    # 旧式の表（全ての列）で表示
    st.dataframe(df_senior, use_container_width=True)
    st.markdown("### Players")
    st.markdown('<div class="player-cards-row">', unsafe_allow_html=True)
    for i, row in df_senior.iterrows():
        avatar_url = get_avatar_url(row["名前"], row["国籍"])
        detail_flag = st.session_state.detail_idx == i
        st.markdown(f"""
        <div class="player-card">
            <img src="{avatar_url}" width="64">
            <b>{row['名前']}</b>
            <div class="pos-label">{row['ポジション']}</div>
            <br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}
            <br>契約:{row['契約年数']} | 年俸:{format_money_euro(row['年俸'])}
        </div>
        """, unsafe_allow_html=True)
        # 詳細ボタン設置
        if st.button("詳細", key=f"senior_detail_{i}"):
            st.session_state.detail_idx = i
        # 選択時は詳細&レーダー
        if detail_flag:
            st.markdown("#### 詳細ステータス")
            st.json(row[["総合","Spd","Pas","Phy","Sta","Def","Tec","Men","Sht","Pow"]].to_dict())
            draw_radar(row)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Youth Tab ---
with tabs[1]:
    st.header("Youth Squad")
    if len(df_youth)==0:
        st.markdown('<div class="youth-msg">ユース選手はいません</div>', unsafe_allow_html=True)
    else:
        st.dataframe(df_youth, use_container_width=True)
        st.markdown("### Players")
        st.markdown('<div class="player-cards-row">', unsafe_allow_html=True)
        for i, row in df_youth.iterrows():
            avatar_url = get_avatar_url(row["名前"], row["国籍"])
            detail_flag = st.session_state.detail_youth == i
            st.markdown(f"""
            <div class="player-card">
                <img src="{avatar_url}" width="64">
                <b>{row['名前']}</b>
                <div class="pos-label">{row['ポジション']}</div>
                <br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}
                <br>契約:{row['契約年数']} | 年俸:{format_money_euro(row['年俸'])}
            </div>
            """, unsafe_allow_html=True)
            if st.button("詳細", key=f"youth_detail_{i}"):
                st.session_state.detail_youth = i
            if detail_flag:
                st.markdown("#### 詳細ステータス")
                st.json(row[["総合","Spd","Pas","Phy","Sta","Def","Tec","Men","Sht","Pow"]].to_dict())
                draw_radar(row)
        st.markdown("</div>", unsafe_allow_html=True)

# --- Match Tab ---
with tabs[2]:
    st.header("Match Simulation")
    st.markdown("おすすめ編成で自動選出：")
    if st.button("おすすめ編成", key="auto_lineup", help="自動で11人バランス編成"):
        st.session_state.selected_starters = df_senior.sort_values("総合", ascending=False).head(11)["名前"].tolist()
    starters = st.multiselect("Starting XI", df_senior["名前"].tolist(), default=getattr(st.session_state,"selected_starters",[]))
    st.markdown("ポジション：<b>GK/DF/MF/FW</b>（手動で調整可）",unsafe_allow_html=True)
    if len(starters)!=11:
        st.markdown('<div class="error-msg">11人ちょうど選んでください</div>', unsafe_allow_html=True)
    else:
        if st.button("Kickoff!", key="kick", help="試合開始！（ダミー）"):
            st.success("（ダミー）試合開始！")
        # ここに勝率予想や演出も追加可能

# --- Scout Tab ---
with tabs[3]:
    st.header("Scout Candidates")
    st.markdown('<span class="money-badge">Budget: 1000000€</span>',unsafe_allow_html=True)
    if st.button("Refresh List", key="refresh_scout"):
        st.info("スカウト候補リストをリフレッシュ！（ダミー）")
    # 横スクロール化・顔画像・加入ボタン等ここに追加可
    st.button("ユーススカウト", key="youth_scout")
    st.button("シニアスカウト", key="senior_scout")

# --- Standings Tab ---
with tabs[4]:
    st.header("Standings")
    st.button("順位表リロード", key="standings_reload")
    st.markdown('<span class="info-msg">ダミー順位表（今後実装）</span>',unsafe_allow_html=True)

# --- Save Tab ---
with tabs[5]:
    st.header("Save")
    if st.button("Save players.csv", key="save_btn"):
        df.to_csv("players.csv", index=False)
        st.success("Saved!")
    if st.button("Load players.csv", key="load_btn"):
        st.info("読み込み機能は今後実装")

# --- SNS Tab ---
with tabs[6]:
    st.header("SNS / Event Feed")
    st.button("SNS更新", key="sns_btn")
    st.info("SNS/履歴等は今後実装")

st.caption("2025年最新版：国籍別リアル顔＋横スクロール＋旧式表＋Kickoff＋詳細レーダーチャート＋エラー赤統一＋全機能一体統合版")
