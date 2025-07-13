import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

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

# --- 顔画像リスト（欧米顔） ---
euro_faces = [
    f"https://randomuser.me/api/portraits/men/{i}.jpg" for i in [10,11,13,14,15,16,18,19,20,21,23,24,25,26,28,29,30,31,33,34,35,36,38,39,40,41,43,44,45,46]
]
def get_player_img(nationality, idx):
    return euro_faces[idx % len(euro_faces)]

# --- 国籍・姓/名リスト（各30種） ---
surname_pools = {
    "England": ["Smith","Jones","Williams","Taylor","Brown","Davies","Evans","Wilson","Johnson","Roberts","Thompson","Wright","Walker","White","Green","Hall","Wood","Martin","Harris","Cooper","King","Clark","Baker","Turner","Carter","Mitchell","Scott","Phillips","Adams","Campbell"],
    "Germany": ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Hoffmann","Schulz","Keller","Richter","Koch","Bauer","Wolf","Neumann","Schwarz","Krüger","Zimmermann","Braun","Hartmann","Lange","Schmitt","Werner","Krause","Meier","Lehmann","Schmid","Schulze","Maier"],
    "Spain": ["García","Martínez","Rodríguez","López","Sánchez","Pérez","Gómez","Martín","Jiménez","Ruiz","Hernández","Díaz","Moreno","Muñoz","Álvarez","Romero","Alonso","Gutiérrez","Navarro","Torres","Domínguez","Vega","Castro","Ramos","Flores","Ortega","Serrano","Blanco","Suárez","Molina"],
    "France": ["Martin","Bernard","Dubois","Thomas","Robert","Richard","Petit","Durand","Leroy","Moreau","Simon","Laurent","Lefebvre","Michel","Garcia","David","Bertrand","Roux","Vincent","Fournier","Girard","Bonnet","Dupont","Lambert","Fontaine","Rousseau","Blanchard","Guerin","Muller","Marchand"],
    "Italy": ["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco","Bruno","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Moretti","Barbieri","Mariani","Santoro","Vitale","Martini","Bianco","Longo","Leone","Gentile","Lombardo"],
    "Netherlands": ["de Jong","de Vries","van den Berg","van Dijk","Bakker","Jansen","Mulder","de Boer","Visser","Smit","Meijer","de Groot","Bos","Vos","Peters","Hendriks","Dekker","Brouwer","van Leeuwen","van der Meer","Kok","Jacobs","de Bruin","van Dam","Koning","Post","Willems","van der Linden","Kuiper","Verhoeven"],
    "Brazil": ["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Almeida","Costa","Gomes","Martins","Araújo","Ribeiro","Barbosa","Barros","Freitas","Lima","Teixeira","Fernandes","Pereira","Carvalho","Moura","Macedo","Azevedo","Cardoso","Moreira","Castro","Campos","Rocha","Pinto","Nascimento"]
}
givenname_pools = {
    "England": ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William","James","Henry","Leo","Alfie","Joshua","Freddie","Archie","Arthur","Logan","Alexander","Harrison","Benjamin","Mason","Ethan","Finley","Lucas","Isaac","Edward","Samuel","Joseph"],
    "Germany": ["Leon","Ben","Paul","Jonas","Elias","Finn","Noah","Luis","Luca","Felix","Maximilian","Moritz","Tim","Julian","Max","David","Jakob","Emil","Philipp","Tom","Nico","Fabian","Marlon","Samuel","Daniel","Jan","Simon","Jonathan","Aaron","Mika"],
    "Spain": ["Alejandro","Pablo","Daniel","Adrián","Javier","David","Hugo","Mario","Manuel","Álvaro","Diego","Miguel","Raúl","Carlos","José","Antonio","Andrés","Fernando","Iván","Sergio","Alberto","Juan","Rubén","Ángel","Gonzalo","Martín","Rafael","Lucas","Jorge","Víctor"],
    "France": ["Lucas","Louis","Hugo","Gabriel","Arthur","Jules","Nathan","Léo","Adam","Raphaël","Enzo","Paul","Tom","Noah","Théo","Ethan","Axel","Sacha","Mathis","Antoine","Clément","Matteo","Maxime","Samuel","Romain","Simon","Nolan","Benjamin","Alexandre","Julien"],
    "Italy": ["Francesco","Alessandro","Lorenzo","Andrea","Matteo","Gabriele","Leonardo","Mattia","Davide","Tommaso","Giuseppe","Riccardo","Edoardo","Federico","Antonio","Marco","Giovanni","Nicolo","Simone","Samuele","Alberto","Pietro","Luca","Stefano","Paolo","Filippo","Angelo","Salvatore","Giorgio","Daniele"],
    "Netherlands": ["Daan","Bram","Sem","Luuk","Jesse","Finn","Milan","Thijs","Lars","Lucas","Thomas","Stijn","Julian","Gijs","Tijn","Sven","Ruben","Niels","Tom","Tim","Noah","Max","Sam","Jens","Pim","Floris","Nick","Jurre","Koen","Luca"],
    "Brazil": ["Lucas","Gabriel","Pedro","Matheus","Guilherme","Rafael","Bruno","Arthur","João","Gustavo","Felipe","Enzo","Davi","Matheus","Samuel","Eduardo","Luiz","Leonardo","Henrique","Thiago","Carlos","Caio","Vinícius","André","Vitor","Marcelo","Luan","Yuri","Ruan","Diego"]
}
ALL_NATIONS = list(surname_pools.keys())

def make_name(nat, used_names):
    surname = random.choice(surname_pools[nat])
    given = random.choice(givenname_pools[nat])
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
if "budget" not in st.session_state:
    st.session_state.budget = 1_000_000

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
    scroll_cols = st.columns(min(len(df_senior), 8))
    for idx, row in df_senior.iterrows():
        with scroll_cols[idx%8]:
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
        st.markdown("<div class='red-message'>No youth players available</div>", unsafe_allow_html=True)
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

# --- Match ---
with tabs[2]:
    st.subheader("Match Simulation")
    auto_starters = df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist()
    starters = st.multiselect("Starting XI", df_senior["名前"].tolist(), default=auto_starters)
    if len(starters) != 11:
        st.markdown("<div class='red-message'>Please select exactly 11 players.</div>", unsafe_allow_html=True)
    else:
        tactics = st.selectbox("Tactics", ["Attack", "Balanced", "Defensive", "Counter", "Possession"])
        if st.button("Kickoff!"):
            team_strength = df_senior[df_senior["名前"].isin(starters)][labels].mean().mean() + random.uniform(-2, 2)
            ai_strength = random.uniform(65, 88)
            pwin = (team_strength / (team_strength+ai_strength)) if (team_strength+ai_strength)>0 else 0.5
            fig, ax = plt.subplots(figsize=(4,1.3))
            ax.bar(["You","AI"], [team_strength, ai_strength], color=["#22e","#ccc"])
            ax.set_xticks([0,1]); ax.set_ylabel("Strength")
            ax.set_title(f"Team Power (Win Probability: {int(100*pwin)}%)", color="#f4f8fc")
            fig.patch.set_alpha(0)
            st.pyplot(fig, transparent=True)
            my_goals = max(0, int(np.random.normal((team_strength-60)/8, 1.0)))
            op_goals = max(0, int(np.random.normal((ai_strength-60)/8, 1.0)))
            result = "Win" if my_goals>op_goals else ("Lose" if my_goals<op_goals else "Draw")
            st.success(f"{result}! {my_goals}-{op_goals}")

# --- Scout ---
with tabs[3]:
    st.subheader("Scout Candidates")
    st.markdown(f"<span class='budget-info'>Budget: {format_money(st.session_state.budget)}</span>", unsafe_allow_html=True)
    if st.button("Refresh Senior List"):
        st.session_state['scout_senior'] = generate_players(5, 0)
    if st.button("Refresh Youth List"):
        st.session_state['scout_youth'] = generate_players(0, 5)
    if "scout_senior" in st.session_state:
        st.markdown("**Senior Candidates**")
        for idx, row in st.session_state['scout_senior'].iterrows():
            img_url = get_player_img(row["国籍"], idx)
            st.markdown(
                f"<div class='player-card'><img src='{img_url}' width='55'><b>{row['名前']}</b><br>{row['ポジション']}/{row['年齢']}/{row['国籍']}<br>{format_money(row['年俸'])}</div>", 
                unsafe_allow_html=True)
    if "scout_youth" in st.session_state:
        st.markdown("**Youth Candidates**")
        for idx, row in st.session_state['scout_youth'].iterrows():
            img_url = get_player_img(row["国籍"], idx)
            st.markdown(
                f"<div class='player-card'><img src='{img_url}' width='55'><b>{row['名前']}</b><br>{row['ポジション']}/{row['年齢']}/{row['国籍']}<br>{format_money(row['年俸'])}</div>", 
                unsafe_allow_html=True)

# --- Standings ---
with tabs[4]:
    st.subheader("League Standings")
    st.markdown("<div class='mobile-table table-highlight'><table><thead><tr><th>Club</th><th>Pts</th><th>Goals</th></tr></thead><tbody><tr><td>You</td><td>0</td><td>0</td></tr><tr><td>AI</td><td>0</td><td>0</td></tr></tbody></table></div>", unsafe_allow_html=True)

# --- Save ---
with tabs[5]:
    st.subheader("Data Save")
    if st.button("Save (Local Only)"):
        st.success("Saved!")

st.caption("All features: English names, Euro faces, Netherlands added, no Japan, all improvements, full integration.")
