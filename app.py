import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# ======= 名前リスト・顔画像関数 =======
NATIONS = ["日本", "イングランド", "ドイツ", "スペイン", "フランス", "イタリア", "ブラジル"]
surname_pools = {
    "日本": ["佐藤","鈴木","高橋","田中","伊藤","渡辺","山本","中村","小林","加藤",
           "吉田","山田","佐々木","山口","松本","井上","木村","林","斎藤","清水",
           "山崎","森","池田","橋本","阿部","石川","石井","村上","藤田","坂本"],
    "イングランド": ["Smith","Jones","Taylor","Brown","Wilson","Johnson","King","White","Evans","Walker",
           "Wright","Martin","Clark","Lee","Scott","Green","Adams","Hall","Baker","Turner",
           "Hill","Phillips","Mitchell","Campbell","Carter","Roberts","Robinson","Harris","Lewis","Morris"],
    "ドイツ": ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Wolf","Keller",
         "Richter","Koch","Bauer","Neumann","Schwarz","Zimmermann","Braun","Hartmann","Lange","Werner",
         "Schmitt","Krause","Meier","Lehmann","Schulze","Maier","Jung","Herrmann","König","Kraus"],
    "スペイン": ["García","Martínez","Rodríguez","López","Sánchez","Pérez","Gómez","Jiménez","Ruiz","Moreno",
            "Muñoz","Álvarez","Romero","Alonso","Navarro","Torres","Domínguez","Vega","Castro","Ramos",
            "Flores","Ortega","Serrano","Blanco","Suárez","Molina","Cruz","Delgado","Guerrero","Ortega"],
    "フランス": ["Martin","Bernard","Dubois","Thomas","Robert","Petit","Leroy","Moreau","Simon","Laurent",
             "Lefebvre","Michel","Garcia","David","Bertrand","Roux","Vincent","Fournier","Girard","Dupont",
             "Lambert","Fontaine","Blanchard","Guerin","Muller","Marchand","Aubert","Giraud","Masson","Andre"],
    "イタリア": ["Rossi","Russo","Ferrari","Bianchi","Romano","Ricci","Marino","Greco","Bruno","Gallo",
             "Costa","Giordano","Rizzo","Lombardi","Moretti","Barbieri","Mariani","Santoro","Vitale","Martini",
             "Bianco","Longo","Leone","Gentile","Lombardo","Conti","De Luca","Mancini","Bruni","Colombo"],
    "ブラジル": ["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Almeida","Costa","Gomes","Martins",
             "Araújo","Ribeiro","Barbosa","Barros","Freitas","Lima","Teixeira","Fernandes","Pereira","Carvalho",
             "Moura","Macedo","Azevedo","Cardoso","Moreira","Castro","Campos","Rocha","Pinto","Nascimento"]
}
givenname_pools = {
    "日本": ["翔","大輔","陸","颯太","陽平","悠真","隼人","翼","優","蓮",
           "大輝","駿","光希","悠人","慎吾","洸太","楓","龍也","亮介","航太",
           "一輝","健太","達也","幸太","悠馬","瑛太","渉","和真","勇太","直樹"],
    "イングランド": ["Oliver","Jack","Harry","George","Noah","Jacob","Oscar","William","James","Henry",
           "Charlie","Thomas","Alfie","Joshua","Freddie","Archie","Arthur","Logan","Alexander","Harrison",
           "Benjamin","Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph","Dylan"],
    "ドイツ": ["Leon","Ben","Paul","Jonas","Elias","Finn","Noah","Luis","Luca","Felix",
         "Maximilian","Moritz","Tim","Julian","Max","David","Jakob","Emil","Philipp","Tom",
         "Nico","Fabian","Marlon","Samuel","Daniel","Jan","Simon","Jonathan","Aaron","Mika"],
    "スペイン": ["Alejandro","Pablo","Daniel","Adrián","Javier","David","Mario","Manuel","Álvaro","Diego",
            "Miguel","Raúl","Carlos","José","Antonio","Andrés","Fernando","Iván","Sergio","Alberto",
            "Juan","Rubén","Ángel","Gonzalo","Martín","Rafael","Lucas","Jorge","Víctor","Mateo"],
    "フランス": ["Lucas","Louis","Hugo","Gabriel","Arthur","Jules","Nathan","Léo","Adam","Raphaël",
             "Enzo","Paul","Tom","Noah","Théo","Ethan","Axel","Sacha","Mathis","Antoine",
             "Clément","Matteo","Maxime","Samuel","Romain","Simon","Nolan","Benjamin","Alexandre","Julien"],
    "イタリア": ["Francesco","Alessandro","Lorenzo","Andrea","Matteo","Gabriele","Leonardo","Mattia","Davide","Tommaso",
             "Giuseppe","Riccardo","Edoardo","Federico","Antonio","Marco","Giovanni","Nicolo","Simone","Samuele",
             "Alberto","Pietro","Luca","Stefano","Paolo","Filippo","Angelo","Salvatore","Giorgio","Daniele"],
    "ブラジル": ["Lucas","Gabriel","Pedro","Matheus","Rafael","Bruno","Arthur","João","Gustavo","Felipe",
             "Enzo","Davi","Samuel","Eduardo","Luiz","Leonardo","Henrique","Thiago","Carlos","Caio",
             "Vinícius","André","Vitor","Marcelo","Luan","Yuri","Ruan","Diego","Fernando","Roberto"]
}

def get_unique_name(nat, used):
    sur = random.choice(surname_pools[nat])
    given = random.choice(givenname_pools[nat])
    if nat == "日本":
        name = f"{sur} {given}"
    else:
        name = f"{given} {sur}"
    if name in used: return get_unique_name(nat, used)
    used.add(name)
    return name

def get_real_face_url(nat, idx):
    # サッカー選手風・国籍ごと
    if nat == "日本":
        return f"https://randomuser.me/api/portraits/men/{(idx%20)+40}.jpg"
    elif nat == "イングランド":
        return f"https://randomuser.me/api/portraits/men/{(idx%20)+10}.jpg"
    elif nat == "ドイツ":
        return f"https://randomuser.me/api/portraits/men/{(idx%20)+30}.jpg"
    elif nat == "スペイン":
        return f"https://randomuser.me/api/portraits/men/{(idx%20)+18}.jpg"
    elif nat == "フランス":
        return f"https://randomuser.me/api/portraits/men/{(idx%20)+5}.jpg"
    elif nat == "イタリア":
        return f"https://randomuser.me/api/portraits/men/{(idx%20)+48}.jpg"
    elif nat == "ブラジル":
        return f"https://randomuser.me/api/portraits/men/{(idx%20)+58}.jpg"
    return f"https://randomuser.me/api/portraits/men/{(idx%99)}.jpg"

def format_money(val):
    if val >= 1_000_000_000: return f"{val//1_000_000_000}b€"
    elif val >= 1_000_000: return f"{val//1_000_000}m€"
    elif val >= 1_000: return f"{val//1_000}k€"
    else: return f"{int(val)}€"

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {
    'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense',
    'Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'
}

def ability_col(v):
    if v >= 90: return f"<span style='color:#20e660;font-weight:bold'>{v}</span>"
    if v >= 75: return f"<span style='color:#ffe600;font-weight:bold'>{v}</span>"
    return f"<span style='color:#1aacef'>{v}</span>"

# ====== データ初期化 ======
random.seed(42)
if "senior_players" not in st.session_state or "youth_players" not in st.session_state:
    used = set()
    senior = []
    youth = []
    # シニア30
    for i in range(30):
        nat = random.choice(NATIONS)
        name = get_unique_name(nat, used)
        data = {
            "名前": name,
            "ポジション": random.choice(["GK","DF","MF","FW"]),
            "年齢": random.randint(19,34),
            "国籍": nat,
            "Spd": random.randint(55,99), "Pas": random.randint(55,99), "Phy": random.randint(55,99),
            "Sta": random.randint(55,99), "Def": random.randint(55,99), "Tec": random.randint(55,99),
            "Men": random.randint(55,99), "Sht": random.randint(55,99), "Pow": random.randint(55,99),
            "契約年数": random.randint(1,5),
            "年俸": random.randint(100_000,2_000_000),
            "画像": get_real_face_url(nat, i)
        }
        data["総合"] = int(np.mean([data[k] for k in labels]))
        senior.append(data)
    # ユース20
    for i in range(20):
        nat = random.choice(NATIONS)
        name = get_unique_name(nat, used)
        data = {
            "名前": name,
            "ポジション": random.choice(["GK","DF","MF","FW"]),
            "年齢": random.randint(15,18),
            "国籍": nat,
            "Spd": random.randint(50,88), "Pas": random.randint(50,88), "Phy": random.randint(50,88),
            "Sta": random.randint(50,88), "Def": random.randint(50,88), "Tec": random.randint(50,88),
            "Men": random.randint(50,88), "Sht": random.randint(50,88), "Pow": random.randint(50,88),
            "契約年数": random.randint(1,4),
            "年俸": random.randint(50_000,300_000),
            "画像": get_real_face_url(nat, i+100)
        }
        data["総合"] = int(np.mean([data[k] for k in labels]))
        youth.append(data)
    st.session_state.senior_players = senior
    st.session_state.youth_players = youth
    st.session_state.selected_player = None
    st.session_state.selected_youth = None

# ====== UIデザイン ======
st.markdown("""
<style>
.stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff; }
.stTabs [data-baseweb="tab-list"] {background:transparent !important;}
.stTabs [role="tab"] {color:#fff !important;font-weight:bold;}
.stTabs [aria-selected="true"] {color:#fff !important;border-bottom:3px solid #ffe600 !important;background:#26376a !important;}
.stButton>button, .css-19rxjzo {background:linear-gradient(90deg,#ffe200 40%,#2873e3 100%);color:#20211b !important;
    border-radius:16px;font-weight:bold;box-shadow:0 0 5px #ffe60088;margin:4px 0 8px 0;}
.player-scroll {display:flex;overflow-x:auto;gap:1.5vw;}
.player-card {background:#fff;color:#133469;border-radius:13px;padding:11px 10px;margin:7px 2vw 15px 0;box-shadow:0 0 11px #20b6ff22;min-width:160px;max-width:180px;flex-shrink:0;position:relative;}
.player-card img {border-radius:50%;margin-bottom:9px;border:2px solid #3398d7;background:#fff;}
.player-card.selected {border:2.5px solid #f5e353;box-shadow:0 0 13px #f5e35355;}
.player-detail-popup {position:absolute;top:60px;left:0;z-index:10;min-width:210px;max-width:280px;background:#202c49;color:#ffe;border-radius:10px;padding:13px 12px;box-shadow:0 0 12px #131f31b2;font-size:1.01em;border:2px solid #1698d488;}
.red-msg {color:#ff5151;font-weight:bold;}
.budget-box {background:linear-gradient(90deg,#ffe200 60%,#2873e3 100%);color:#222;border-radius:11px;padding:7px 20px;display:inline-block;font-size:1.08em;font-weight:bold;}
.position-label {display:inline-block;background:#163b8c;color:#fff;border-radius:10px;padding:1px 9px 1.5px 9px;margin:2px 2px 2px 0;font-size:1.04em;}
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")
tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save", "SNS"])

# === Senior ===
with tabs[0]:
    st.subheader("Senior Squad")
    # 一覧
    df_senior = pd.DataFrame(st.session_state.senior_players)
    st.markdown("<div class='mobile-table'><table><thead><tr>"+\
        "".join([f"<th>{col}</th>" for col in ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]])+"</tr></thead><tbody>"+\
        "".join(["<tr>"+\
                 "".join([f"<td>{row[col]}</td>" if col!="年俸" else f"<td>{format_money(row['年俸'])}</td>" for col in ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]])+"</tr>"
                 for _,row in df_senior.iterrows()])+"</tbody></table></div>",unsafe_allow_html=True)
    st.markdown("#### Player Cards")
    st.markdown("<div class='player-scroll'>", unsafe_allow_html=True)
    for idx,row in df_senior.iterrows():
        selected = st.session_state.selected_player==idx
        st.markdown(f"""<div class='player-card{' selected' if selected else ''}'>""",unsafe_allow_html=True)
        st.image(row["画像"], width=70)
        st.markdown(f"<b>{row['名前']}</b>", unsafe_allow_html=True)
        st.markdown(f"<span class='position-label'>{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}<br><span style='font-size:0.94em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>", unsafe_allow_html=True)
        if st.button("詳細", key=f"sen_detail_{idx}"):
            st.session_state.selected_player = idx
        if selected:
            # 詳細ポップ
            stats = [row[l] for l in labels]+[row[labels[0]]]
            angles = np.linspace(0,2*np.pi,len(labels)+1)
            fig,ax = plt.subplots(figsize=(2.3,2.3),subplot_kw=dict(polar=True))
            ax.plot(angles,stats,color="#1c53d6",linewidth=2)
            ax.fill(angles,stats,color="#87d4ff",alpha=0.21)
            ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels,fontsize=10,color='#ffe45a')
            ax.set_yticklabels([])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig,transparent=True)
            ab_table = "<table>"
            for l in labels:
                v = int(row[l])
                ab_table += f"<tr><td style='color:#b7e2ff;font-weight:bold'>{l}</td><td>{ability_col(v)}</td><td style='color:#bbb;font-size:0.92em'>{labels_full[l]}</td></tr>"
            ab_table += "</table>"
            st.markdown(ab_table, unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

# === Youth ===
with tabs[1]:
    st.subheader("Youth Players")
    df_youth続きから**全文（ユース～SNSまで）フルで仕上げます。**  
（改善点・デザイン維持、エラー系赤文字、ユースも外国人、ボタン色・選手顔・横スクロール対応）

---

```python
# === Youth ===
with tabs[1]:
    st.subheader("Youth Players")
    df_youth = pd.DataFrame(st.session_state.youth_players)
    if len(df_youth) == 0:
        st.markdown("<span class='red-msg'>ユース選手はいません</span>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='mobile-table'><table><thead><tr>"+\
            "".join([f"<th>{col}</th>" for col in ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]])+"</tr></thead><tbody>"+\
            "".join(["<tr>"+\
                     "".join([f"<td>{row[col]}</td>" if col!="年俸" else f"<td>{format_money(row['年俸'])}</td>" for col in ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]])+"</tr>"
                     for _,row in df_youth.iterrows()])+"</tbody></table></div>",unsafe_allow_html=True)
        st.markdown("#### Player Cards")
        st.markdown("<div class='player-scroll'>", unsafe_allow_html=True)
        for idx,row in df_youth.iterrows():
            selected = st.session_state.selected_youth==idx
            st.markdown(f"""<div class='player-card{' selected' if selected else ''}'>""",unsafe_allow_html=True)
            st.image(row["画像"], width=70)
            st.markdown(f"<b>{row['名前']}</b>", unsafe_allow_html=True)
            st.markdown(f"<span class='position-label'>{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}<br><span style='font-size:0.94em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>", unsafe_allow_html=True)
            if st.button("詳細", key=f"youth_detail_{idx}"):
                st.session_state.selected_youth = idx
            if selected:
                stats = [row[l] for l in labels]+[row[labels[0]]]
                angles = np.linspace(0,2*np.pi,len(labels)+1)
                fig,ax = plt.subplots(figsize=(2.3,2.3),subplot_kw=dict(polar=True))
                ax.plot(angles,stats,color="#1c53d6",linewidth=2)
                ax.fill(angles,stats,color="#87d4ff",alpha=0.21)
                ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels,fontsize=10,color='#ffe45a')
                ax.set_yticklabels([])
                fig.patch.set_alpha(0.0)
                st.pyplot(fig,transparent=True)
                ab_table = "<table>"
                for l in labels:
                    v = int(row[l])
                    ab_table += f"<tr><td style='color:#b7e2ff;font-weight:bold'>{l}</td><td>{ability_col(v)}</td><td style='color:#bbb;font-size:0.92em'>{labels_full[l]}</td></tr>"
                ab_table += "</table>"
                st.markdown(ab_table, unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

# === Match ===
with tabs[2]:
    st.subheader("Match Simulation")
    # オススメ編成一発ボタン
    if st.button("オススメ編成", key="auto_sel"):
        best_idxs = df_senior[labels].sum(axis=1).nlargest(11).index
        st.session_state["starters"] = list(best_idxs)
    # 手動選択もOK
    st.markdown("ポジションごとに11人選択してください。")
    starter_names = df_senior["名前"].tolist()
    if "starters" not in st.session_state:
        st.session_state["starters"] = list(range(11))
    starter_idxs = st.multiselect("Starting XI", options=list(range(len(starter_names))),
                                  format_func=lambda x: f"{starter_names[x]}", default=st.session_state["starters"])
    if len(starter_idxs)!=11:
        st.markdown("<span class='red-msg'>11人ちょうど選んでください</span>", unsafe_allow_html=True)
    else:
        df_start = df_senior.iloc[starter_idxs]
        # ポジション分布
        pos_counts = df_start["ポジション"].value_counts().to_dict()
        pos_disp = "".join([f"<span class='position-label'>{p}:{pos_counts.get(p,0)}</span>" for p in ["GK","DF","MF","FW"]])
        st.markdown(pos_disp, unsafe_allow_html=True)
        # 勝率予想
        team_strength = df_start[labels].mean().mean()
        ai_strength = random.uniform(62,81)
        win_rate = int(100*team_strength/(team_strength+ai_strength))
        st.markdown(f"<b>推定チーム力:</b> {team_strength:.1f}　<b>対戦AI:</b> {ai_strength:.1f}<br><b style='color:#ffe600'>勝率予想: {win_rate}%</b>",unsafe_allow_html=True)
        # KICKOFF
        if st.button("Kickoff", key="kickoff", help="試合開始!", use_container_width=True):
            g_mine = max(0, int(np.random.normal((team_strength-58)/8, 1.0)))
            g_ai = max(0, int(np.random.normal((ai_strength-58)/8, 1.0)))
            result = "Win" if g_mine>g_ai else ("Lose" if g_mine<g_ai else "Draw")
            st.success(f"{result}! {g_mine}-{g_ai}")
            st.info(f"得点者: {random.choice(df_start['名前'].tolist()) if g_mine>0 else 'なし'}")
        else:
            st.caption("KICKOFFボタンで試合を実行！")

# === Scout ===
with tabs[3]:
    st.subheader("Scout Candidates")
    st.markdown("<div class='budget-box'>予算: 1,000,000€</div>", unsafe_allow_html=True)
    # Senior/Youthスカウト切替
    scout_type = st.radio("スカウトタイプ", ["シニアスカウト", "ユーススカウト"], horizontal=True)
    if st.button("Refresh List", key="refresh_scout"):
        st.session_state.scout_list = []
        used = set([x["名前"] for x in (st.session_state.senior_players+st.session_state.youth_players)])
        for i in range(5):
            nat = random.choice(NATIONS)
            name = get_unique_name(nat, used)
            is_youth = (scout_type=="ユーススカウト")
            age = random.randint(15,18) if is_youth else random.randint(19,34)
            imgidx = random.randint(0,60)
            row = {
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": age, "国籍": nat,
                "Spd": random.randint(50,99), "Pas": random.randint(50,99), "Phy": random.randint(50,99),
                "Sta": random.randint(50,99), "Def": random.randint(50,99), "Tec": random.randint(50,99),
                "Men": random.randint(50,99), "Sht": random.randint(50,99), "Pow": random.randint(50,99),
                "契約年数": random.randint(1,4), "年俸": random.randint(80_000,600_000),
                "画像": get_real_face_url(nat, imgidx)
            }
            row["総合"] = int(np.mean([row[k] for k in labels]))
            st.session_state.scout_list.append(row)
    if "scout_list" not in st.session_state:
        st.session_state.scout_list = []
    if len(st.session_state.scout_list)==0:
        st.markdown("<span class='red-msg'>スカウト候補はいません。Refreshしてください。</span>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='player-scroll'>", unsafe_allow_html=True)
        for idx,row in enumerate(st.session_state.scout_list):
            st.markdown("<div class='player-card'>",unsafe_allow_html=True)
            st.image(row["画像"], width=68)
            st.markdown(f"<b>{row['名前']}</b>", unsafe_allow_html=True)
            st.markdown(f"<span class='position-label'>{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}<br><span style='font-size:0.94em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>", unsafe_allow_html=True)
            if st.button("加入", key=f"scout_add_{idx}"):
                # 追加
                if scout_type=="ユーススカウト":
                    st.session_state.youth_players.append(row)
                else:
                    st.session_state.senior_players.append(row)
                st.success(f"{row['名前']}を獲得しました！")
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

# === Standings ===
with tabs[4]:
    st.subheader("League Standings")
    tbl = []
    df_senior = pd.DataFrame(st.session_state.senior_players)
    tbl.append(["あなたのクラブ", "--", df_senior["総合"].mean().round(1)])
    # ダミー順位表
    for n in ["Blue Wolves","Falcons","RedStars","Vortis","United FC"]:
        tbl.append([n,"--",random.randint(63,85)])
    df_rank = pd.DataFrame(tbl, columns=["クラブ","Pts","Ave能力"])
    st.markdown("<div class='mobile-table table-highlight'><table><thead><tr>"+\
        "".join([f"<th>{col}</th>" for col in df_rank.columns])+"</tr></thead><tbody>"+\
        "".join(["<tr>"+\
                 "".join([f"<td>{row[col]}</td>" for col in df_rank.columns])+"</tr>"
                 for _,row in df_rank.iterrows()])+"</tbody></table></div>",unsafe_allow_html=True)

# === Save ===
with tabs[5]:
    st.subheader("Data Save")
    if st.button("Save All Data"):
        st.success("（ダミー）セーブしました！")

# === SNS ===
with tabs[6]:
    st.subheader("SNS / Event Feed")
    st.info("SNSイベントフィード（ここに今後移籍・試合ログ等）")

st.caption("完全統合：シニア30/ユース20, 国籍顔, 横スクロール, 各種ボタン色, エラー赤, オススメ編成, 勝率, ポジ白文字, ユースも外国人, UI強化版")
