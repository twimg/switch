import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="Soccer Club Management Sim", layout="wide")

# --- CSS/UI ---
st.markdown("""
<style>
body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
.stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff; }
h1,h2,h3,h4,h5,h6 { color: #fff !important; }
.stTabs [data-baseweb="tab"] > button { color: #fff !important; background: transparent !important; }
.stTabs [data-baseweb="tab"] > button[aria-selected="true"] { color: #fff !important; border-bottom: 2px solid #fff !important; background: transparent !important; }
.stButton>button, .stDownloadButton>button, .stMultiSelect>div>div>div { background: linear-gradient(90deg, #ffd800 20%, #17b6ff 100%); color: #192841 !important; font-weight:bold; border-radius: 13px; font-size:1.02em; margin:6px 0 7px 0; box-shadow:0 0 8px #33e0ff33; }
.stButton>button:active { background: #ffdf4d !important; }
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
.mobile-table {overflow-x:auto; white-space:nowrap;}
.mobile-table th, .mobile-table td {
  padding: 4px 9px; font-size: 15px; border-bottom: 1.3px solid #1c2437;
}
.budget-info { background:#ffeeaa; color:#253246; padding:7px 17px; border-radius:10px; font-weight:bold; display:inline-block; font-size:1.11em;}
.position-label { color: #fff !important; background:#1b4f83; border-radius:7px; padding:1px 8px; font-weight:bold; margin:0 2px;}
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")

# --- 画像 ---
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

# --- ネーム・クラブ ---
surname_pools = {
    "日本": ["佐藤","鈴木","高橋","田中","伊藤","渡辺","山本","中村","小林","加藤","吉田","山田","佐々木","山口","松本","井上","木村","林","斎藤","清水","山崎","森","池田","橋本","阿部","石川","石井","村上","藤田","坂本"],
    "イングランド": ["Smith","Jones","Williams","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Thompson","Wright","Walker","White","Green","Hall","Wood","Martin","Harris","Cooper","King","Clark","Baker","Turner","Carter","Mitchell","Scott","Phillips","Adams","Campbell"],
    "ドイツ": ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Hoffmann","Schulz","Keller","Richter","Koch","Bauer","Wolf","Neumann","Schwarz","Krüger","Zimmermann","Braun","Hartmann","Lange","Schmitt","Werner","Krause","Meier","Lehmann","Schmid","Schulze","Maier"],
}
givenname_pools = {
    "日本": ["翔","大輔","陸","颯太","陽平","悠真","隼人","啓太","海斗","翼","優","拓真","蓮","大輝","駿","光希","悠人","慎吾","洸太","楓","龍也","亮介","航太","一輝","健太","達也","幸太","悠馬","瑛太","渉"],
    "イングランド": ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William","James","Henry","Leo","Alfie","Joshua","Freddie","Archie","Arthur","Logan","Alexander","Harrison","Benjamin","Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph"],
    "ドイツ": ["Leon","Ben","Paul","Jonas","Elias","Finn","Noah","Luis","Luca","Felix","Maximilian","Moritz","Tim","Julian","Max","David","Jakob","Emil","Philipp","Tom","Nico","Fabian","Marlon","Samuel","Daniel","Jan","Simon","Jonathan","Aaron","Mika"],
}
CLUBS = ["Striver FC", "Weston Town", "Blitz United", "Tokyo Eagles", "Dresden SV", "London City", "Red Mountain", "Blue Coast"]

ALL_NATIONS = list(surname_pools.keys())
labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']

def make_name(nat, used_names):
    surname = random.choice(surname_pools[nat])
    given = random.choice(givenname_pools[nat])
    if nat == "日本":
        name = f"{surname} {given}"
    else:
        name = f"{given} {surname}"
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

def generate_players(nsenior=30, nyouth=20, club="Striver FC"):
    players = []
    used_names = set()
    for i in range(nsenior):
        nat = random.choice(ALL_NATIONS)
        name = make_name(nat, used_names)
        player = dict(
            名前=name, ポジション=random.choice(["GK","DF","MF","FW"]), 年齢=random.randint(19,33),
            国籍=nat, クラブ=club,
            Spd=random.randint(60,90), Pas=random.randint(60,90), Phy=random.randint(60,90), Sta=random.randint(60,90),
            Def=random.randint(60,90), Tec=random.randint(60,90), Men=random.randint(60,90), Sht=random.randint(60,90), Pow=random.randint(60,90),
            年俸=random.randint(120_000,1_200_000), 契約年数=random.randint(1,3), 総合=0, ユース=0
        )
        player["総合"] = int(np.mean([player[l] for l in labels]))
        players.append(player)
    for i in range(nyouth):
        nat = random.choice(ALL_NATIONS)
        name = make_name(nat, used_names)
        player = dict(
            名前=name, ポジション=random.choice(["GK","DF","MF","FW"]), 年齢=random.randint(14,18),
            国籍=nat, クラブ=club,
            Spd=random.randint(52,82), Pas=random.randint(52,82), Phy=random.randint(52,82), Sta=random.randint(52,82),
            Def=random.randint(52,82), Tec=random.randint(52,82), Men=random.randint(52,82), Sht=random.randint(52,82), Pow=random.randint(52,82),
            年俸=random.randint(30_000,250_000), 契約年数=random.randint(1,2), 総合=0, ユース=1
        )
        player["総合"] = int(np.mean([player[l] for l in labels]))
        players.append(player)
    return pd.DataFrame(players)

# --- 複数クラブ/セーブ対応 ---
if "club_idx" not in st.session_state:
    st.session_state.club_idx = 0
if "clubs" not in st.session_state:
    st.session_state.clubs = {}
    for c in CLUBS:
        st.session_state.clubs[c] = generate_players(30,20,club=c)
    st.session_state.selected_XI = []

club_names = list(st.session_state.clubs.keys())
club_select = st.sidebar.selectbox("操作クラブ", club_names, index=st.session_state.club_idx)
st.session_state.club_idx = club_names.index(club_select)
df = st.session_state.clubs[club_select]
df_senior = df[df["ユース"]==0].reset_index(drop=True)
df_youth = df[df["ユース"]==1].reset_index(drop=True)

tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save"])

# --- Senior ---
with tabs[0]:
    st.subheader(f"Senior Squad ({club_select})")
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
    scroll_cols = st.columns(min(len(df_senior), 8))
    for idx, row in df_senior.iterrows():
        with scroll_cols[idx%8]:
            img_url = get_player_img(row["国籍"], idx)
            st.markdown(
                f"""<div class='player-card'>
                <img src="{img_url}" width="66">
                <b>{row['名前']}</b>
                <br><span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span>
                <br><span class='position-label'>{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}
                <br><span style='font-size:0.95em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                </div>""", unsafe_allow_html=True)
            if st.button("詳細", key=f"senior_detail_{idx}"):
                st.session_state.detail_idx = ("senior", idx)
            if st.session_state.get("detail_idx") == ("senior", idx):
                vals = [row[l] for l in labels]
                angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
                vals += [vals[0]]
                angles2 = np.concatenate([angles, [angles[0]]])
                fig = plt.figure(figsize=(2.6,2.6))
                ax = fig.add_subplot(111, polar=True)
                ax.plot(angles2, vals, linewidth=2)
                ax.fill(angles2, vals, alpha=0.3)
                ax.set_thetagrids(np.degrees(angles), labels)
                ax.set_ylim(0, 100)
                plt.title(row["名前"], size=12)
                st.pyplot(fig, transparent=True)
                st.write({k: row[k] for k in labels})

# --- Youth ---
with tabs[1]:
    st.subheader(f"Youth Squad ({club_select})")
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
        scroll_cols = st.columns(min(len(df_youth), 8))
        for idx, row in df_youth.iterrows():
            with scroll_cols[idx%8]:
                img_url = get_player_img(row["国籍"], idx)
                st.markdown(
                    f"""<div class='player-card'>
                    <img src="{img_url}" width="66">
                    <b>{row['名前']}</b>
                    <br><span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span>
                    <br><span class='position-label'>{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}
                    <br><span style='font-size:0.95em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                    </div>""", unsafe_allow_html=True)
                if st.button("詳細", key=f"youth_detail_{idx}"):
                    st.session_state.detail_idx = ("youth", idx)
                if st.session_state.get("detail_idx") == ("youth", idx):
                    vals = [row[l] for l in labels]
                    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
                    vals += [vals[0]]
                    angles2 = np.concatenate([angles, [angles[0]]])
                    fig = plt.figure(figsize=(2.6,2.6))
                    ax = fig.add_subplot(111, polar=True)
                    ax.plot(angles2, vals, linewidth=2)
                    ax.fill(angles2, vals, alpha=0.3)
                    ax.set_thetagrids(np.degrees(angles), labels)
                    ax.set_ylim(0, 100)
                    plt.title(row["名前"], size=12)
                    st.pyplot(fig, transparent=True)
                    st.write({k: row[k] for k in labels})

# --- Match ---
with tabs[2]:
    st.subheader("Match Simulation")
    XI = st.session_state.get("selected_XI", [])
    st.write("おすすめ編成（自動選出）")
    if st.button("オートスタメン"):
        selected = []
        for pos in ["GK", "DF", "MF", "FW"]:
            num = 1 if pos=="GK" else (4 if pos=="DF" else (3 if pos=="MF" else 3))
            dfp = df_senior[df_senior["ポジション"]==pos].sort_values("総合", ascending=False).head(num)
            selected += list(dfp.index)
        st.session_state.selected_XI = selected
        XI = selected
    picked = st.multiselect("スタメンを11人選択（順不同可）", df_senior.index, default=XI, format_func=lambda i: df_senior.at[i,"名前"])
    st.session_state.selected_XI = picked
    st.markdown("**スターティングXI**：" + "、".join([df_senior.at[i,"名前"] for i in picked]) if picked else "未選択")
    if len(picked)==11 and st.button("試合開始！"):
        ovr = np.mean([df_senior.at[i,"総合"] for i in picked])
        ai = random.randint(55,85)
        st.success(f"試合結果: {club_select} {int(ovr/10)} - {int(ai/10)} AIクラブ（あなた: {int(ovr)}）")

# --- Scout ---
with tabs[3]:
    st.subheader("Scout Candidates")
    st.markdown("<span class='budget-info'>予算: 2,000,000€</span>", unsafe_allow_html=True)
    candidates = generate_players(6,0)
    st.write("スカウトリスト（タップで獲得）")
    scols = st.columns(3)
    for i, row in candidates.iterrows():
        with scols[i%3]:
            img_url = get_player_img(row["国籍"], i)
            st.markdown(f"""<div class='player-card'>
            <img src="{img_url}" width="66">
            <b>{row['名前']}</b> <span class='position-label'>{row['ポジション']}</span>
            <br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}
            <br>年俸:{format_money(row['年俸'])}
            </div>""", unsafe_allow_html=True)
            if st.button("加入", key=f"scout_add_{i}"):
                df.loc[len(df)] = row
                st.success(f"{row['名前']} を獲得しました！")

# --- Standings ---
with tabs[4]:
    st.subheader("Standings (仮/デモ表示)")
    data = {"クラブ": CLUBS, "勝点": np.random.randint(10, 60, size=len(CLUBS)), "得失点": np.random.randint(-10, 35, size=len(CLUBS))}
    st.dataframe(pd.DataFrame(data).sort_values("勝点", ascending=False))

# --- Save ---
with tabs[5]:
    st.subheader("Save/Load")
    if st.button("保存ダウンロード"):
        st.download_button("Download Current Squad", data=df.to_csv(index=False), file_name=f"{club_select}_squad.csv")
    if st.button("ロードサンプル"):
        st.session_state.clubs[club_select] = generate_players(30,20,club=club_select)
        st.success("サンプルでリロードしました。")

st.caption("全タブ統合・8クラブ選択式・白タブ・顔画像・詳細・スカウト・順位表・セーブ機能付フル版")
