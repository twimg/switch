import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# --- UI/ロゴ・デザイン・スマホ最適化 ---
TEAM_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/6/67/Soccer_ball_animated.svg"
PLAYER_ICON_URL = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
st.markdown("""
    <style>
    html, body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
    .stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff; }
    .stRadio [role='radiogroup'] label {
        background: linear-gradient(90deg,#eee969 30%,#3f98e3 100%);
        color: #173060 !important;
        font-weight: bold !important;
        border-radius: 17px !important;
        margin: 5px 9px 5px 0;
        padding: 7px 16px !important;
        font-size: 1.08em !important;
        box-shadow: 0 0 8px #23aaff22;
        border: 2px solid #23345a33;
        display: inline-block;
        transition: 0.18s;
    }
    .stRadio [role='radiogroup'] label[data-selected="true"] {
        background: linear-gradient(90deg,#3f98e3 35%,#f7ec95 100%);
        color: #1c233d !important;
        border: 2.2px solid #fff16c !important;
        box-shadow: 0 0 12px #fff16c33;
        font-size: 1.13em !important;
    }
    .player-card {
        background: #fff;
        color: #133469;
        border-radius: 15px;
        padding: 12px 10px 8px 10px;
        margin: 10px 2vw 15px 2vw;
        box-shadow: 0 0 13px #20b6ff33;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 140px; max-width: 170px;
        font-size:0.99em;
        transition: 0.15s;
        border: 2px solid #25b5ff20;
        position: relative;
    }
    .player-card img {border-radius:50%;margin-bottom:10px;border:2px solid #3398d7;background:#fff;}
    .player-card.selected {border: 2.7px solid #f5e353; box-shadow: 0 0 16px #f5e35399;}
    .player-card:hover {
        background: #f8fcff;
        color: #1b54a4;
        transform: scale(1.03);
        box-shadow: 0 0 13px #1cefff55;
        border:2px solid #42d8ff;
    }
    .player-card .detail-popup {
        position: absolute;
        top: 6px;
        left: 101%;
        z-index:10;
        min-width: 180px; max-width:270px;
        background: #202c49;
        color: #ffe;
        border-radius: 11px;
        padding: 13px 12px;
        box-shadow: 0 0 14px #131f31b2;
        font-size: 1.02em;
        border: 2px solid #1698d488;
    }
    .clickable-name {color: #2bc5ff; font-weight:700; text-decoration: underline; cursor:pointer;}
    .clickable-name:hover {color: #ffe45a; background: #1c1f29;}
    .mobile-table {overflow-x:auto; white-space:nowrap;}
    .mobile-table th, .mobile-table td {
        padding: 4px 9px;
        font-size: 14px;
        border-bottom: 1.3px solid #1c2437;
    }
    .stDataFrame {border-radius:12px !important;}
    .table-highlight th, .table-highlight td {
        background: #182649 !important;
        color: #ffe45a !important;
        border-bottom: 1.4px solid #24335d !important;
    }
    </style>
""", unsafe_allow_html=True)
st.image(TEAM_LOGO_URL, width=48)
st.title("Soccer Club Management Sim")

# --- 略称/カラー補助 ---
labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {
    'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense',
    'Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'
}
def ability_col(v):
    if v >= 90: return f"<span style='color:#20e660;font-weight:bold'>{v}</span>"
    if v >= 75: return f"<span style='color:#ffe600;font-weight:bold'>{v}</span>"
    return f"<span style='color:#1aacef'>{v}</span>"

# --- 苗字・名前 ---
surname_pools = {
    "日本": ["佐藤","田中","鈴木","高橋","山本","中村","小林","加藤","吉田","渡辺","山田","松本","斎藤","木村","林","清水","山口","池田","森","石川","橋本","阿部","山崎","井上","岡田","村上","石井","三浦","上田","原田","大野","福田","星野","竹内","大西"],
    "ブラジル": ["シウバ","サントス","コスタ","オリヴェイラ","ソウザ","フェレイラ","ロドリゲス","ペレイラ","アウベス","リマ","ゴンサウベス","ゴメス","マルチンス","マシャド","ロペス","メンドンサ","アラウージョ","ピント","カルドーゾ","カストロ","モラエス","フレイタス","パイヴァ","ドスサントス","バルボーザ","メロ","テイシェイラ","ドミンゲス","メンドンサ","カブラル","カンポス","ラモス","ペレイラ","コエーリョ","サラザール"],
    "スペイン": ["ガルシア","ロペス","マルティネス","ゴンザレス","ロドリゲス","フェルナンデス","サンチェス","ペレス","ゴメス","マルティン","ヒメネス","ルイス","ディアス","アルバレス","モレノ","ムニョス","アロンソ","グティエレス","ロメロ","トーレス","ナバロ","ドミンゲス","ベガ","ソト","サラサル","カストロ","セラーノ","イダルゴ","ラモス","イバニェス","ロサーノ","モントーヤ","プラド","パチェコ","マンサナレス"],
    "フランス": ["マルタン","ベルナール","デュラン","プティ","ロベール","リシャール","フォール","ガルシア","ルイ","ルフェーブル","モロー","ルルー","アンドレ","ルジェ","コロンブ","ヴィダル","ジョリー","ガイヤール","フィリップ","ピカール","ピエール","ボワイエ","ブラン","バルビエ","ジラール","アダン","パスカル","フローラン","バティスト","シャルパンティエ","フレール","グラン","デマル","アベール","ラフォント"],
    "イタリア": ["ロッシ","ルッソ","フェラーリ","エスポジト","ビアンキ","ロマーノ","コロンボ","リッチ","マリーニ","グレコ","ブルーノ","ガッリ","コンティ","マンチーニ","モレッティ","バルディーニ","ジェンティーレ","ロンバルディ","マルティーニ","マルケージ","ヴィオリ","ジアーニ","フィオリ","パルマ","デサンティス","ヴェントゥーラ","カッシーニ","ベルティ","ヴィタリ","カッパーニ","カプート","バルバ","ピッチーニ","サルトリ","ガルガーノ"],
    "ドイツ": ["ミュラー","シュミット","シュナイダー","フィッシャー","ヴェーバー","マイヤー","ヴァーグナー","ベッカー","ホフマン","シュルツ","ケラー","リヒター","クレーマー","カール","バウアー","シュトルツ","ヴォルフ","ピンター","ブランク","リース","ローゼ","ハルトマン","ヴァイス","ランゲ","ボッシュ","ゲルハルト","フランク","ザイデル","ヴィンター","メッツガー","エルンスト","ミヒャエル","キルヒ","ドレッサー","カッツ"],
    "イングランド": ["スミス","ジョンソン","ウィリアムズ","ブラウン","ジョーンズ","ミラー","デイビス","テイラー","クラーク","ホワイト","ハリス","マーチン","トンプソン","ロビンソン","ライト","ウォーカー","ヒル","グリーン","キング","リチャーズ","アレン","モリス","クーパー","ベイリー","ジェームズ","ウッド","スコット","モーガン","ベネット","アダムズ","ロジャース","フレッチャー","ディクソン","パーカー","フォスター"]
}
givenname_pools = {
    "日本": ["翔","隼人","陸","陽平","悠真","悠人","啓太","海斗","翼","隆成","凛","優","颯太","匠","拓真","蓮","大輝","光","大和","光希","慎吾","陸斗","悠馬","洸太","楓","洋平","航","駿","晴斗","航太","亮介","竜也","渉","一輝","瑞希"],
    "ブラジル": ["マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ","ブルーノ","レアンドロ","ファビオ","ダニーロ","グスタボ","ガブリエル","レナン","ヴィトル","ラファエル","ジョルジ","チアゴ","エンリケ","レナト","カイオ","ジエゴ","ジウベルト","カルロス","イゴール","ラファ","ジュニオル","エヴェルトン","マルセロ","イアゴ","ホドリゴ","カウアン"],
    "スペイン": ["アレハンドロ","パブロ","ダニエル","ミゲル","アドリアン","ハビエル","イバン","ルイス","マヌエル","ディエゴ","アルバロ","ダビド","セルヒオ","ラウル","カルロス","マリオ","ホセ","ロドリゴ","フアン","アルトゥーロ","サンティアゴ","ビクトル","ガブリエル","フェリペ","アルベルト","イニゴ","ハイメ","エリック","ルベン","イサーク","マルク","サウル","サミュエル","ジェラルド","マルティ"],
    "フランス": ["ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク","ミカエル","ジュリアン","カミーユ","バスティアン","ロマン","アドリアン","ロイック","ガエル","ジョルダン","バンジャマン","エリオット","エミール","テオ","エンゾ","ナタン","ウーゴ","トリスタン","アレクシス","ガブリエル","ルイ","クレマン","マティス","ポール","マルタン","ジュール"],
    "イタリア": ["ファビオ","マルコ","アレッサンドロ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ","ルイジ","アントニオ","シモーネ","ジジ","パオロ","フランチェスコ","クラウディオ","ステファノ","クリスティアン","ニコラ","ドメニコ","マッテオ","エンリコ","カルロ","アンドレア","サミュエレ","アウグスト","ルチアーノ","ジーノ","ロベルト","エドアルド","ダヴィデ","ヴィットリオ","マルチェロ","ルカ","レオナルド"],
    "ドイツ": ["クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル","トビアス","フローリアン","クリストフ","ユリアン","モリッツ","フィリップ","アレクサンダー","シモン","フランク","オリバー","エミル","ノア","パスカル","レナード","レオナルド","カール","フェリックス","マルクス","イェンス","ベネディクト","ヨナス","レンツ","サミー","ベン","ユスティン"],
    "イングランド": ["トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ルーカス","ヘンリー","エドワード","ベンジャミン","ジョシュア","サミュエル","メイソン","ジョセフ","マシュー","リアム","アーチー","イーサン","ルイ","ジェイコブ","ディラン","アルフィー","マックス","レオ","アレクサンダー","タイラー","ハーヴィー","ジェイデン","ローガン","オスカー","セバスチャン","ザック"]
}
def get_unique_name_by_nationality(nationality, used_names):
    sur_pool = surname_pools.get(nationality, ["NoSurname"])
    given_pool = givenname_pools.get(nationality, ["NoGiven"])
    for _ in range(100):
        surname = random.choice(sur_pool)
        given = random.choice(given_pool)
        if nationality == "日本":
            name = f"{surname} {given}"
        else:
            name = f"{given} {surname}"
        if name not in used_names:
            return name
    return f"{nationality}Player{random.randint(100,999)}"

PLAYER_TEAM = "ストライバーFC"
AI_CLUB_NAMES = ["ブルーウルブズ", "ファルコンズ", "レッドスターズ", "ヴォルティス", "ユナイテッドFC", "オーシャンズ", "タイガース", "スカイバード"]
TEAM_NUM = 8
random.seed(42)
AI_TEAMS = AI_CLUB_NAMES[:TEAM_NUM-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_TEAMS
currency_unit = "€"

def format_money(euro):
    if euro >= 1_000_000_000:
        return f"{euro/1_000_000_000:.2f}b{currency_unit}"
    elif euro >= 1_000_000:
        return f"{euro/1_000_000:.2f}m{currency_unit}"
    elif euro >= 1_000:
        return f"{euro/1_000:.1f}k{currency_unit}"
    return f"{int(euro)}{currency_unit}"

def assign_hidden_type_and_growth(df):
    types = ["万能型","守備型","攻撃型","早熟型","晩成型","王様型"]
    growth = np.random.randint(70, 99, len(df))
    df["_タイプ"] = np.random.choice(types, len(df))
    df["_成長限界"] = growth
    return df

if "current_round" not in st.session_state: st.session_state.current_round = 1
if "scout_list" not in st.session_state: st.session_state.scout_list = []
if "budget" not in st.session_state: st.session_state.budget = 1_000_000
if "team_points" not in st.session_state: st.session_state.team_points = {t: 0 for t in ALL_TEAMS}
if "match_log" not in st.session_state: st.session_state.match_log = []
if "移籍履歴" not in st.session_state: st.session_state["移籍履歴"] = []
if "sns_news" not in st.session_state: st.session_state["sns_news"] = []
if "ai_players" not in st.session_state:
    ai_players = []
    used_names = set()
    AI_TYPES = ["攻撃型", "守備型", "バランス型"]
    for t in AI_TEAMS:
        ai_type = random.choice(AI_TYPES)
        for i in range(20):
            nationality = random.choice(list(surname_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            used_names.add(name)
            ai_players.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(19,32), "国籍": nationality,
                "Spd": random.randint(60,85), "Pas": random.randint(60,85),
                "Phy": random.randint(60,85), "Sta": random.randint(60,85),
                "Def": random.randint(60,85), "Tec": random.randint(60,85),
                "Men": random.randint(60,85), "Sht": random.randint(60,85),
                "Pow": random.randint(60,85), "所属クラブ": t, "AIタイプ": ai_type,
                "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

# --- データ読込 ---
df = pd.read_csv("players.csv")
col_map = {'スピード':'Spd','パス':'Pas','フィジカル':'Phy','スタミナ':'Sta',
    'ディフェンス':'Def','テクニック':'Tec','メンタル':'Men','シュート':'Sht','パワー':'Pow'}
df = df.rename(columns=col_map)
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000
df["総合"] = df[labels].mean(axis=1).astype(int)
df = assign_hidden_type_and_growth(df)
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)
if "selected_player" not in st.session_state: st.session_state.selected_player = None

main_tab = st.radio("メニュー", ("Senior", "Youth", "Match", "Scout", "Standings", "Save", "SNS"), horizontal=True)

# --- Senior ---
if main_tab == "Senior":
    st.subheader("Senior Squad")
    main_cols = ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]
    st.markdown(
        "<div class='mobile-table'><table><thead><tr>" +
        "".join([f"<th>{col}</th>" for col in main_cols]) +
        "</tr></thead><tbody>" +
        "".join([
            "<tr>" + "".join([f"<td>{row[col]}</td>" for col in main_cols]) + "</tr>"
            for _, row in df_senior.iterrows()
        ]) +
        "</tbody></table></div>", unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("#### Player Cards")
    cols = st.columns(2 if st.session_state.get("mobile",False) else 4)
    detail_idx = st.session_state.selected_player["row"] if isinstance(st.session_state.selected_player, dict) and "row" in st.session_state.selected_player else -1
    for idx, row in df_senior.iterrows():
        with cols[idx%len(cols)]:
            selected = detail_idx == idx
            card_class = "player-card selected" if selected else "player-card"
            st.markdown(
                f"""<div class='{card_class}'>
                <img src="{PLAYER_ICON_URL}" width="48">
                <b>{row['名前']}</b>
                <br><span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span>
                <br>{row['ポジション']} / {row['年齢']} / {row['国籍']}
                <br><span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                {"<div class='detail-popup'>" if selected else ""}
                {"<b>能力チャート</b><br>" if selected else ""}
                """, unsafe_allow_html=True)
            if st.button("詳細", key=f"senior_{idx}"):
                st.session_state.selected_player = {"row": idx, **row.to_dict()}
            if selected:
                stats = [float(row[l]) for l in labels] + [float(row[labels[0]])]
                angles = np.linspace(0, 2 * np.pi, len(labels)+1)
                fig, ax = plt.subplots(figsize=(2,2), subplot_kw=dict(polar=True))
                ax.plot(angles, stats, color="#1c53d6", linewidth=2)
                ax.fill(angles, stats, color="#87d4ff", alpha=0.21)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels, fontsize=9, color='#ffe45a')
                ax.set_yticklabels([])
                fig.patch.set_alpha(0.0)
                st.pyplot(fig, transparent=True)
                ab_table = "<table>"
                for l in labels:
                    v = int(row[l])
                    ab_table += f"<tr><td style='color:#b7e2ff;font-weight:bold'>{l}</td><td>{ability_col(v)}</td><td style='color:#bbb;font-size:0.92em'>{labels_full[l]}</td></tr>"
                ab_table += "</table>"
                st.markdown(ab_table, unsafe_allow_html=True)
                st.markdown(
                    f"ポジション: {row['ポジション']}<br>年齢: {row['年齢']}<br>国籍: {row['国籍']}<br>"
                    f"契約年数: {row['契約年数']}年<br>年俸: {format_money(row['年俸'])}<br>"
                    f"所属クラブ: {row.get('所属クラブ','-')}",
                    unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# --- Youth ---
if main_tab == "Youth":
    st.subheader("Youth Players")
    if len(df_youth) == 0:
        st.info("ユース選手はいません")
    else:
        st.markdown(
            "<div class='mobile-table'><table><thead><tr>" +
            "".join([f"<th>{col}</th>" for col in main_cols]) +
            "</tr></thead><tbody>" +
            "".join([
                "<tr>" + "".join([f"<td>{row[col]}</td>" for col in main_cols]) + "</tr>"
                for _, row in df_youth.iterrows()
            ]) +
            "</tbody></table></div>", unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown("#### Player Cards")
        cols = st.columns(2 if st.session_state.get("mobile",False) else 4)
        detail_idx = st.session_state.selected_player["row"] if isinstance(st.session_state.selected_player, dict) and "row" in st.session_state.selected_player else -1
        for idx, row in df_youth.iterrows():
            with cols[idx%len(cols)]:
                selected = detail_idx == idx
                card_class = "player-card selected" if selected else "player-card"
                st.markdown(
                    f"""<div class='{card_class}'>
                    <img src="{PLAYER_ICON_URL}" width="48">
                    <b>{row['名前']}</b>
                    <br><span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span>
                    <br>{row['ポジション']} / {row['年齢']} / {row['国籍']}
                    <br><span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                    {"<div class='detail-popup'>" if selected else ""}
                    {"<b>能力チャート</b><br>" if selected else ""}
                    """, unsafe_allow_html=True)
                if st.button("詳細", key=f"youth_{idx}"):
                    st.session_state.selected_player = {"row": idx, **row.to_dict()}
                if selected:
                    stats = [float(row[l]) for l in labels] + [float(row[labels[0]])]
                    angles = np.linspace(0, 2 * np.pi, len(labels)+1)
                    fig, ax = plt.subplots(figsize=(2,2), subplot_kw=dict(polar=True))
                    ax.plot(angles, stats, color="#1c53d6", linewidth=2)
                    ax.fill(angles, stats, color="#87d4ff", alpha=0.21)
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(labels, fontsize=9, color='#ffe45a')
                    ax.set_yticklabels([])
                    fig.patch.set_alpha(0.0)
                    st.pyplot(fig, transparent=True)
                    ab_table = "<table>"
                    for l in labels:
                        v = int(row[l])
                        ab_table += f"<tr><td style='color:#b7e2ff;font-weight:bold'>{l}</td><td>{ability_col(v)}</td><td style='color:#bbb;font-size:0.92em'>{labels_full[l]}</td></tr>"
                    ab_table += "</table>"
                    st.markdown(ab_table, unsafe_allow_html=True)
                    st.markdown(
                        f"ポジション: {row['ポジション']}<br>年齢: {row['年齢']}<br>国籍: {row['国籍']}<br>"
                        f"契約年数: {row['契約年数']}年<br>年俸: {format_money(row['年俸'])}<br>"
                        f"所属クラブ: {row.get('所属クラブ','-')}",
                        unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

# --- Match ---
if main_tab == "Match":
    st.subheader("Match Simulation")
    round_idx = (st.session_state.current_round-1)%len(AI_TEAMS)
    enemy = AI_TEAMS[round_idx]
    st.write(f"今節: {PLAYER_TEAM} vs {enemy}")
    auto_starters = df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist()
    starters = st.multiselect("Starting XI", df_senior["名前"].tolist(), default=auto_starters)
    if len(starters) != 11:
        st.warning("11人ちょうど選んでください")
    else:
        tactics = st.selectbox("Tactics", ["Attack", "Balanced", "Defensive", "Counter", "Possession"])
        if st.button("Kickoff!", key=f"kick_{datetime.now().isoformat()}_{random.random()}"):
            seed_val = random.randint(1,1_000_000)
            np.random.seed(seed_val)
            random.seed(seed_val)
            team_strength = df_senior[df_senior["名前"].isin(starters)][labels].mean().mean() + random.uniform(-2, 2)
            ai_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==enemy]
            ai_strength = ai_df[labels].mean().mean() + random.uniform(-2, 2)
            if tactics=="Attack": team_strength *= 1.08
            elif tactics=="Defensive": team_strength *= 0.93
            elif tactics=="Counter": team_strength *= 1.04
            elif tactics=="Possession": team_strength *= 1.03
            pwin = (team_strength / (team_strength+ai_strength)) if (team_strength+ai_strength)>0 else 0.5
            fig, ax = plt.subplots(figsize=(4,1.3))
            ax.bar(["You","AI"], [team_strength, ai_strength], color=["#22e","#ccc"])
            ax.set_xticks([0,1]); ax.set_ylabel("平均能力")
            ax.set_title(f"チーム力比較（推定勝率: {int(100*pwin)}%）", color="#f4f8fc")
            fig.patch.set_alpha(0)
            st.pyplot(fig, transparent=True)
            my_goals = max(0, int(np.random.normal((team_strength-60)/8, 1.0)))
            op_goals = max(0, int(np.random.normal((ai_strength-60)/8, 1.0)))
            if my_goals > op_goals:
                result = "Win"
                st.session_state.team_points[PLAYER_TEAM] += 3
            elif my_goals < op_goals:
                result = "Lose"
                st.session_state.team_points[enemy] += 3
            else:
                result = "Draw"
                st.session_state.team_points[PLAYER_TEAM] += 1
                st.session_state.team_points[enemy] += 1
            scorer = random.choice(starters) if my_goals > 0 else "なし"
            ai_scorer = random.choice(ai_df["名前"].tolist()) if op_goals > 0 else "なし"
            st.success(f"{result}! {my_goals}-{op_goals}")
            st.info(f"得点者: {scorer} / 相手: {ai_scorer}")
            st.session_state.current_round += 1
            st.session_state.match_log.append(f"Round {st.session_state.current_round-1}: {PLAYER_TEAM} vs {enemy}: {my_goals}-{op_goals}, 得点: {scorer}")

    st.markdown("#### 最近の試合ログ")
    for l in st.session_state.match_log[-5:][::-1]:
        st.write(l)

# --- Scout ---
if main_tab == "Scout":
    st.subheader("Scout Candidates")
    st.info(f"Budget: {format_money(st.session_state.budget)}")
    if st.button("Refresh List"):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_list = []
        for _ in range(5):
            nationality = random.choice(list(surname_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names | set(p["名前"] for p in st.session_state.scout_list))
            used_names.add(name)
            st.session_state.scout_list.append({
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(19, 29),
                "国籍": nationality,
                "Spd": random.randint(60, 80),
                "Pas": random.randint(60, 80),
                "Phy": random.randint(60, 80),
                "Sta": random.randint(60, 80),
                "Def": random.randint(60, 80),
                "Tec": random.randint(60, 80),
                "Men": random.randint(60, 80),
                "Sht": random.randint(60, 80),
                "Pow": random.randint(60, 80),
                "契約年数": 2,
                "年俸": random.randint(100_000,180_000),
                "得点": 0,
                "出場数": 0,
                "所属クラブ": PLAYER_TEAM
            })
    cols = st.columns(1 if st.session_state.get("mobile",False) else 3)
    already = set(df["名前"].tolist())
    for idx, player in enumerate(st.session_state.scout_list):
        with cols[idx%len(cols)]:
            ovr = int(np.mean([player[l] for l in labels]))
            st.markdown(
                f"<div class='player-card'><b>{player['名前']}</b> <span style='color:#2cabe8;'>(OVR:{ovr})</span><br>"
                f"{player['ポジション']} / {player['年齢']} / {player['国籍']}<br>"
                f"契約:{player['契約年数']}年｜年俸:{format_money(player['年俸'])}</div>", 
                unsafe_allow_html=True)
            if player["名前"] not in already:
                if st.button("加入", key=f"scout_{idx}"):
                    df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                    df.to_csv("players.csv", index=False)
                    st.session_state.budget -= player['年俸']
                    st.success(f"{player['名前']} signed!")
                    st.session_state["移籍履歴"].append(f"{player['名前']}（{player['国籍']}）をスカウトで獲得！")
            else:
                st.markdown("🟦<span style='color:#888'>既に在籍</span>", unsafe_allow_html=True)

# --- Standings ---
if main_tab == "Standings":
    st.subheader("League Standings")
    tbl = []
    for t in ALL_TEAMS:
        total_goals = 0
        if t == PLAYER_TEAM:
            total_goals = df_senior["得点"].sum()
        else:
            ai_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==t]
            total_goals = ai_df["得点"].sum() if "得点" in ai_df.columns else 0
        tbl.append([t, st.session_state.team_points.get(t,0), total_goals])
    dft = pd.DataFrame(tbl, columns=["Club","Pts","Goals"])
    dft = dft.sort_values(["Pts","Goals"], ascending=[False,False]).reset_index(drop=True)
    dft["Rank"] = dft.index + 1
    st.markdown(
        "<div class='mobile-table table-highlight'><table><thead><tr>" +
        "".join([f"<th>{col}</th>" for col in ["Rank","Club","Pts","Goals"]]) +
        "</tr></thead><tbody>" +
        "".join([
            "<tr>" + "".join([f"<td>{row[col]}</td>" for col in ["Rank","Club","Pts","Goals"]]) + "</tr>"
            for _, row in dft.iterrows()
        ]) +
        "</tbody></table></div>", unsafe_allow_html=True
    )
    if st.session_state.match_log:
        st.markdown("**Recent Matches**")
        for l in st.session_state.match_log[-5:][::-1]:
            st.text(l)

# --- Save ---
if main_tab == "Save":
    st.subheader("Data Save")
    if st.button("Save (players.csv)"):
        df.to_csv("players.csv", index=False)
        st.success("Saved! (players.csv)")
    if st.button("Save AI Players List"):
        st.session_state.ai_players.to_csv("ai_players.csv", index=False)
        st.success("AI Players list saved.")

# --- SNS ---
if main_tab == "SNS":
    st.subheader("SNS / Event Feed")
    if st.session_state["移籍履歴"]:
        st.write("### Recent Transfers")
        for news in st.session_state["移籍履歴"][-5:][::-1]:
            st.info(news)
    if st.session_state.match_log:
        st.write("### Recent Matches")
        for l in st.session_state.match_log[-5:][::-1]:
            st.write(l)

st.caption("デザイン/UI/機能・全修正版（スマホ対応・能力色分け・エラー防止済）")
