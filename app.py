import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# --- UI/ロゴ・デザイン ---
TEAM_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/6/67/Soccer_ball_animated.svg"
PLAYER_ICON_URL = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
st.markdown("""
    <style>
    .stApp { background: linear-gradient(120deg, #182a45 0%, #27345b 100%) !important; color: #eaf6ff; }
    .stDataFrame th, .stDataFrame td {
        color: #f6f7fa !important;
        background: #223152 !important;
        font-size: 15px !important;
        border-bottom: 1px solid #27345b !important;
    }
    .stDataFrame tbody tr:nth-child(even) td {
        background: #2d4066 !important;
    }
    .stDataFrame thead tr th {
        background: #14203a !important;
        color: #fff03d !important;
        font-size: 16px !important;
        letter-spacing:0.04em;
        text-shadow: 0 2px 8px #28335099;
    }
    .player-card {
        background: #fff;
        color: #133469;
        border-radius: 15px;
        padding: 16px 13px 8px 13px;
        margin: 10px 4px 16px 4px;
        box-shadow: 0 0 14px #27e2ff33;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 170px; max-width: 220px;
        font-size:1.01em;
        transition: 0.14s;
        border: 2.5px solid #25b5ff22;
        position: relative;
    }
    .player-card img {border-radius:50%;margin-bottom:12px;border:2.5px solid #2d7cf7;background:#fff;}
    .player-card.selected {border: 2.5px solid #fff03d; box-shadow: 0 0 18px #fff03d55;}
    .player-card:hover {
        background: #f5fbff;
        color: #1b54a4;
        transform: scale(1.025);
        box-shadow: 0 0 18px #2fefff99;
        border:2.5px solid #29d4ff;
    }
    .player-card .detail-popup {
        position: absolute;
        top: 8px;
        left: 108%;
        z-index:10;
        min-width: 260px;
        background: #202c49;
        color: #ffe;
        border-radius: 11px;
        padding: 13px 16px;
        box-shadow: 0 0 20px #131f31a8;
        font-size: 1.02em;
        border: 2px solid #1d7fec99;
    }
    .clickable-name {color: #2bc5ff; font-weight:700; text-decoration: underline; cursor:pointer;}
    .clickable-name:hover {color: #fff03d; background: #1c1f29;}
    </style>
""", unsafe_allow_html=True)
st.image(TEAM_LOGO_URL, width=56)
st.title("Soccer Club Management Sim（全部入り 完成版）")

# --- 苗字・名前データ（各国30+件ずつ） ---
surname_pools = {
    "日本": [
        "佐藤","田中","鈴木","高橋","山本","中村","小林","加藤","吉田","渡辺",
        "山田","松本","斎藤","木村","林","清水","山口","池田","森","石川",
        "橋本","阿部","山崎","井上","岡田","村上","石井","三浦","上田","原田",
        "大野","福田","星野","竹内","大西"
    ],
    "ブラジル": [
        "シウバ","サントス","コスタ","オリヴェイラ","ソウザ","フェレイラ","ロドリゲス","ペレイラ","アウベス","リマ",
        "ゴンサウベス","ゴメス","マルチンス","マシャド","ロペス","メンドンサ","アラウージョ","ピント","カルドーゾ","カストロ",
        "モラエス","フレイタス","パイヴァ","ドスサントス","バルボーザ","メロ","テイシェイラ","ドミンゲス","メンドンサ","カブラル",
        "カンポス","ラモス","ペレイラ","コエーリョ","サラザール"
    ],
    "スペイン": [
        "ガルシア","ロペス","マルティネス","ゴンザレス","ロドリゲス","フェルナンデス","サンチェス","ペレス","ゴメス","マルティン",
        "ヒメネス","ルイス","ディアス","アルバレス","モレノ","ムニョス","アロンソ","グティエレス","ロメロ","トーレス",
        "ナバロ","ドミンゲス","ベガ","ソト","サラサル","カストロ","セラーノ","イダルゴ","ラモス","イバニェス",
        "ロサーノ","モントーヤ","プラド","パチェコ","マンサナレス"
    ],
    "フランス": [
        "マルタン","ベルナール","デュラン","プティ","ロベール","リシャール","フォール","ガルシア","ルイ","ルフェーブル",
        "モロー","ルルー","アンドレ","ルジェ","コロンブ","ヴィダル","ジョリー","ガイヤール","フィリップ","ピカール",
        "ピエール","ボワイエ","ブラン","バルビエ","ジラール","アダン","パスカル","フローラン","バティスト","シャルパンティエ",
        "フレール","グラン","デマル","アベール","ラフォント"
    ],
    "イタリア": [
        "ロッシ","ルッソ","フェラーリ","エスポジト","ビアンキ","ロマーノ","コロンボ","リッチ","マリーニ","グレコ",
        "ブルーノ","ガッリ","コンティ","マンチーニ","モレッティ","バルディーニ","ジェンティーレ","ロンバルディ","マルティーニ","マルケージ",
        "ヴィオリ","ジアーニ","フィオリ","パルマ","デサンティス","ヴェントゥーラ","カッシーニ","ベルティ","ヴィタリ","カッパーニ",
        "カプート","バルバ","ピッチーニ","サルトリ","ガルガーノ"
    ],
    "ドイツ": [
        "ミュラー","シュミット","シュナイダー","フィッシャー","ヴェーバー","マイヤー","ヴァーグナー","ベッカー","ホフマン","シュルツ",
        "ケラー","リヒター","クレーマー","カール","バウアー","シュトルツ","ヴォルフ","ピンター","ブランク","リース",
        "ローゼ","ハルトマン","ヴァイス","ランゲ","ボッシュ","ゲルハルト","フランク","ザイデル","ヴィンター","メッツガー",
        "エルンスト","ミヒャエル","キルヒ","ドレッサー","カッツ"
    ],
    "イングランド": [
        "スミス","ジョンソン","ウィリアムズ","ブラウン","ジョーンズ","ミラー","デイビス","テイラー","クラーク","ホワイト",
        "ハリス","マーチン","トンプソン","ロビンソン","ライト","ウォーカー","ヒル","グリーン","キング","リチャーズ",
        "アレン","モリス","クーパー","ベイリー","ジェームズ","ウッド","スコット","モーガン","ベネット","アダムズ",
        "ロジャース","フレッチャー","ディクソン","パーカー","フォスター"
    ],
}
givenname_pools = {
    "日本": [
        "翔","隼人","陸","陽平","悠真","悠人","啓太","海斗","翼","隆成",
        "凛","優","颯太","匠","拓真","蓮","大輝","光","大和","光希",
        "慎吾","陸斗","悠馬","洸太","楓","洋平","航","駿","晴斗","航太",
        "亮介","竜也","渉","一輝","瑞希"
    ],
    "ブラジル": [
        "マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ",
        "ブルーノ","レアンドロ","ファビオ","ダニーロ","グスタボ","ガブリエル","レナン","ヴィトル","ラファエル","ジョルジ",
        "チアゴ","エンリケ","レナト","カイオ","ジエゴ","ジウベルト","カルロス","イゴール","ラファ","ジュニオル",
        "エヴェルトン","マルセロ","イアゴ","ホドリゴ","カウアン"
    ],
    "スペイン": [
        "アレハンドロ","パブロ","ダニエル","ミゲル","アドリアン","ハビエル","イバン","ルイス","マヌエル","ディエゴ",
        "アルバロ","ダビド","セルヒオ","ラウル","カルロス","マリオ","ホセ","ロドリゴ","フアン","アルトゥーロ",
        "サンティアゴ","ビクトル","ガブリエル","フェリペ","アルベルト","イニゴ","ハイメ","エリック","ルベン","イサーク",
        "マルク","サウル","サミュエル","ジェラルド","マルティ"
    ],
    "フランス": [
        "ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク",
        "ミカエル","ジュリアン","カミーユ","バスティアン","ロマン","アドリアン","ロイック","ガエル","ジョルダン","バンジャマン",
        "エリオット","エミール","テオ","エンゾ","ナタン","ウーゴ","トリスタン","アレクシス","ガブリエル","ルイ",
        "クレマン","マティス","ポール","マルタン","ジュール"
    ],
    "イタリア": [
        "ファビオ","マルコ","アレッサンドロ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ","ルイジ",
        "アントニオ","シモーネ","ジジ","パオロ","フランチェスコ","クラウディオ","ステファノ","クリスティアン","ニコラ","ドメニコ",
        "マッテオ","エンリコ","カルロ","アンドレア","サミュエレ","アウグスト","ルチアーノ","ジーノ","ロベルト","エドアルド",
        "ダヴィデ","ヴィットリオ","マルチェロ","ルカ","レオナルド"
    ],
    "ドイツ": [
        "クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル",
        "トビアス","フローリアン","クリストフ","ユリアン","モリッツ","フィリップ","アレクサンダー","シモン","フランク","オリバー",
        "エミル","ノア","パスカル","レナード","レオナルド","カール","フェリックス","マルクス","イェンス","ベネディクト",
        "ヨナス","レンツ","サミー","ベン","ユスティン"
    ],
    "イングランド": [
        "トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ルーカス",
        "ヘンリー","エドワード","ベンジャミン","ジョシュア","サミュエル","メイソン","ジョセフ","マシュー","リアム","アーチー",
        "イーサン","ルイ","ジェイコブ","ディラン","アルフィー","マックス","レオ","アレクサンダー","タイラー","ハーヴィー",
        "ジェイデン","ローガン","オスカー","セバスチャン","ザック"
    ],
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

# --- クラブ・AIクラブ情報 ---
PLAYER_TEAM = "ストライバーFC"
AI_CLUB_NAMES = ["ブルーウルブズ", "ファルコンズ", "レッドスターズ", "ヴォルティス", "ユナイテッドFC", "オーシャンズ", "タイガース", "スカイバード"]
TEAM_NUM = 8
random.seed(42)
AI_TEAMS = AI_CLUB_NAMES[:TEAM_NUM-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_TEAMS
labels = ['Speed','Pass','Physical','Stamina','Defense','Technique','Mental','Shoot','Power']
currency_unit = "€"

def format_money(euro):
    if euro >= 1_000_000_000:
        return f"{euro/1_000_000_000:.2f}b{currency_unit}"
    elif euro >= 1_000_000:
        return f"{euro/1_000_000:.2f}m{currency_unit}"
    elif euro >= 1_000:
        return f"{euro/1_000:.1f}k{currency_unit}"
    return f"{int(euro)}{currency_unit}"

# --- 選手タイプ/成長限界生成 ---
def assign_hidden_type_and_growth(df):
    types = ["万能型","守備型","攻撃型","早熟型","晩成型","王様型"]
    growth = np.random.randint(70, 99, len(df))
    df["_タイプ"] = np.random.choice(types, len(df))
    df["_成長限界"] = growth
    return df

# --- セッション初期化 ---
if "current_round" not in st.session_state: st.session_state.current_round = 1
if "scout_list" not in st.session_state: st.session_state.scout_list = []
if "budget" not in st.session_state: st.session_state.budget = 1_000_000
if "予算履歴" not in st.session_state: st.session_state["予算履歴"] = [st.session_state.budget]
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
                "Speed": random.randint(60,85), "Pass": random.randint(60,85),
                "Physical": random.randint(60,85), "Stamina": random.randint(60,85),
                "Defense": random.randint(60,85), "Technique": random.randint(60,85),
                "Mental": random.randint(60,85), "Shoot": random.randint(60,85),
                "Power": random.randint(60,85), "所属クラブ": t, "AIタイプ": ai_type,
                "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

# --- データ読込 ---
df = pd.read_csv("players.csv")
column_rename = {'スピード': 'Speed', 'パス': 'Pass', 'フィジカル': 'Physical', 'スタミナ': 'Stamina',
    'ディフェンス': 'Defense', 'テクニック': 'Technique', 'メンタル': 'Mental',
    'シュート': 'Shoot', 'パワー': 'Power'}
df = df.rename(columns=column_rename)
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000
df["総合"] = df[labels].mean(axis=1).astype(int)
df = assign_hidden_type_and_growth(df)  # 隠し属性付与
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)
if "selected_player" not in st.session_state: st.session_state.selected_player = None

# --- タブ ---
tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save", "Event"])

# 1. Senior
with tabs[0]:
    st.subheader("Senior Squad")
    show_df = df_senior[["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]+labels].copy()
    show_df["年俸"] = show_df["年俸"].apply(format_money)
    st.dataframe(show_df, height=440, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.markdown("#### Player Cards")
    cols = st.columns(4)
    detail_idx = st.session_state.selected_player["row"] if isinstance(st.session_state.selected_player, dict) and "row" in st.session_state.selected_player else -1
    for idx, row in df_senior.iterrows():
        with cols[idx%4]:
            selected = detail_idx == idx
            card_class = "player-card selected" if selected else "player-card"
            st.markdown(
                f"""<div class='{card_class}'>
                <img src="{PLAYER_ICON_URL}" width="56">
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
                fig, ax = plt.subplots(figsize=(2.3,2.3), subplot_kw=dict(polar=True))
                ax.plot(angles, stats, color="#1c53d6", linewidth=2)
                ax.fill(angles, stats, color="#87d4ff", alpha=0.20)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels, fontsize=9, color='#fff03d')
                ax.set_yticklabels([])
                fig.patch.set_alpha(0.0)
                st.pyplot(fig, transparent=True)
                st.markdown(
                    f"ポジション: {row['ポジション']}<br>年齢: {row['年齢']}<br>国籍: {row['国籍']}<br>"
                    f"契約年数: {row['契約年数']}年<br>年俸: {format_money(row['年俸'])}<br>"
                    f"所属クラブ: {row.get('所属クラブ','-')}",
                    unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# 2. Youth
with tabs[1]:
    st.subheader("Youth Players")
    show_df = df_youth[["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]+labels].copy()
    show_df["年俸"] = show_df["年俸"].apply(format_money)
    st.dataframe(show_df, height=350, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.markdown("#### Player Cards")
    cols = st.columns(4)
    for idx, row in df_youth.iterrows():
        with cols[idx%4]:
            st.markdown(
                f"""<div class='player-card'>
                <img src="{PLAYER_ICON_URL}" width="56">
                <b>{row['名前']}</b>
                <br><span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span>
                <br>{row['ポジション']} / {row['年齢']} / {row['国籍']}
                <br><span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                </div>""", unsafe_allow_html=True)

# 3. Match
with tabs[2]:
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
            # 毎回乱数シードを変えて演算
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
            fig, ax = plt.subplots(figsize=(4,1.4))
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

# 4. Scout
with tabs[3]:
    st.subheader("Scout Candidates")
    st.info(f"Budget: {format_money(st.session_state.budget)}")
    if st.button("Refresh List"):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_list = []
        for _ in range(5):
            nationality = random.choice(list(surname_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            used_names.add(name)
            st.session_state.scout_list.append({
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(19, 29),
                "国籍": nationality,
                "Speed": random.randint(60, 80),
                "Pass": random.randint(60, 80),
                "Physical": random.randint(60, 80),
                "Stamina": random.randint(60, 80),
                "Defense": random.randint(60, 80),
                "Technique": random.randint(60, 80),
                "Mental": random.randint(60, 80),
                "Shoot": random.randint(60, 80),
                "Power": random.randint(60, 80),
                "契約年数": 2,
                "年俸": random.randint(100_000,180_000),
                "得点": 0,
                "出場数": 0,
                "所属クラブ": PLAYER_TEAM
            })
    cols = st.columns(5)
    for idx, player in enumerate(st.session_state.scout_list):
        with cols[idx%5]:
            ovr = int(np.mean([player[l] for l in labels]))
            st.markdown(
                f"<div class='player-card'><b>{player['名前']}</b> <span style='color:#2cabe8;'>(OVR:{ovr})</span><br>"
                f"{player['ポジション']} / {player['年齢']} / {player['国籍']}<br>"
                f"契約:{player['契約年数']}年｜年俸:{format_money(player['年俸'])}</div>", 
                unsafe_allow_html=True)
            if st.button("加入", key=f"scout_{idx}"):
                df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                df.to_csv("players.csv", index=False)
                st.session_state.budget -= player['年俸']
                st.success(f"{player['名前']} signed!")

# 5. Standings
with tabs[4]:
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
    st.dataframe(dft[["Rank","Club","Pts","Goals"]], hide_index=True, use_container_width=True)
    if st.session_state.match_log:
        st.markdown("**Recent Matches**")
        for l in st.session_state.match_log[-5:][::-1]:
            st.text(l)

# 6. Save
with tabs[5]:
    st.subheader("Data Save")
    if st.button("Save (players.csv)"):
        df.to_csv("players.csv", index=False)
        st.success("Saved! (players.csv)")
    if st.button("Save AI Players List"):
        st.session_state.ai_players.to_csv("ai_players.csv", index=False)
        st.success("AI Players list saved.")

# 7. Event/SNS風
with tabs[6]:
    st.subheader("SNS/News & Events")
    st.markdown("**直近の移籍・試合・イベントログ**")
    logs = (st.session_state["移籍履歴"] + st.session_state.match_log)[-10:][::-1]
    for l in logs:
        st.write("📢", l)

st.caption("全機能・全国対応・苗字名前分離・タッチ式選手詳細・連打修正・フル完成版。ご要望は随時どうぞ！")
