import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# --- UI/デザイン ---
st.set_page_config(page_title="Soccer Club Management Sim", layout="wide")

st.markdown("""
<style>
html, body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
.stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff; }
.stTabs [role="tab"] { color: #fff !important; font-size:1.14em !important; }
.stTabs [aria-selected="true"] { color:#fff !important; font-weight:bold; border-bottom:4px solid #ffe066 !important; }
.stButton > button {
    background: linear-gradient(90deg,#ffe066 40%,#29a6f5 100%);
    color: #222 !important; font-weight: bold; font-size:1.08em;
    border-radius: 1.8em !important;
    box-shadow: 0 0 8px #ffe06633;
    border: 2px solid #ffe066bb;
    margin: 6px 0 10px 0; transition: 0.14s;
}
.stButton > button:hover {
    background: linear-gradient(90deg,#29a6f5 0%,#ffe066 100%);
    color: #1555a5 !important;
    border:2.2px solid #29a6f5 !important;
}
.budget-box {
    background: #fff5cc;
    color: #2c2c2c;
    font-weight: bold;
    padding: 0.7em 2em 0.7em 1.4em;
    border-radius: 1em;
    font-size: 1.13em;
    display: inline-block;
    margin-bottom:1em;
}
.pos-label {
    background: #113377;
    color: #fff !important;
    font-weight: bold;
    border-radius: 12px;
    padding: 2px 17px;
    display:inline-block;
    margin:5px 0 7px 0;
    font-size:1.15em;
    letter-spacing:1.5px;
}
.player-cards-row { display: flex; overflow-x: auto; gap: 19px; padding: 6px 3px 14px 0; }
.player-card {
    background: #fff; color: #133469; border-radius: 15px;
    min-width: 210px; max-width: 210px; padding: 13px 11px 13px 11px;
    box-shadow: 0 0 14px #20b6ff22; display: flex; flex-direction: column; align-items: center;
    font-size:1.02em; border: 2px solid #25b5ff30; position: relative;
}
.player-card.selected {border: 2.7px solid #f5e353; box-shadow: 0 0 16px #f5e35399;}
.player-card:hover { background: #f8fcff; color: #1b54a4; box-shadow: 0 0 13px #1cefff55; border:2px solid #42d8ff; }
.player-card img {border-radius:50%;margin-bottom:10px;border:2px solid #3398d7;background:#fff;width:76px;height:76px;object-fit:cover;}
.detail-btn { background: #ffe066; color:#23325a;font-weight:bold;border-radius:1.5em;padding:7px 25px;font-size:1.03em;border:none;cursor:pointer; }
.detail-btn:hover { background:#29a6f5;color:#fff; }
.add-btn { background:#ffe066;color:#23325a;font-weight:bold;border-radius:1.5em;padding:7px 27px;font-size:1.08em;border:none;margin-top:11px;}
.add-btn:hover { background:#29a6f5;color:#fff;}
.mobile-table {overflow-x:auto; white-space:nowrap;}
.mobile-table th, .mobile-table td {padding: 4px 9px; font-size: 14px; border-bottom: 1.3px solid #1c2437;}
.table-highlight th, .table-highlight td {background: #182649 !important; color: #ffe45a !important; border-bottom: 1.4px solid #24335d !important;}
</style>
""", unsafe_allow_html=True)

st.title("Soccer Club Management Sim")
st.markdown("<span style='color:#b5eaff;'>AIリアル調サッカー選手写真・国籍反映・横スクロール・ユース外国人・全機能統合最新版</span>", unsafe_allow_html=True)

# ---- 基本パラメータ ----
labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense','Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'}

# --- 各国ファミリーネーム／ファーストネーム（30件×7カ国例）---
names_data = {
    "日本": (
        ["佐藤","鈴木","高橋","田中","伊藤","山本","中村","小林","加藤","吉田","山田","佐々木","山口","斎藤","松本","井上","木村","林","清水","山崎","池田","橋本","阿部","石川","森","藤田","村上","石井","三浦","上田"],
        ["翔","隼人","大輝","海斗","陽平","蓮","拓真","悠人","陸","翼","光希","優斗","颯太","匠","光","隆成","凛","悠真","陽太","駿","洸太","楓","洋平","慎吾","陸斗","洸介","亮介","渉","瑞希","一輝"]
    ),
    "ブラジル": (
        ["シウバ","サントス","コスタ","ロドリゲス","ペレイラ","リマ","マルチンス","ロペス","メンドンサ","バルボーザ","テイシェイラ","アウベス","ドスサントス","メロ","サラザール","モラエス","ゴンサウベス","パイヴァ","ソウザ","ゴメス","アラウージョ","フェレイラ","オリヴェイラ","ドミンゲス","フレイタス","カルドーゾ","カンポス","カブラル","ペレイラ","サントス"],
        ["マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","ペドロ","ブルーノ","レアンドロ","ファビオ","ダニーロ","ガブリエル","ジョルジ","エリック","カイオ","マルコス","ジオバニ","ラファエル","ジエゴ","イゴール","マルセロ","チアゴ","ジョゼ","ヴィトル","イアゴ","エンリケ","ホドリゴ","エヴェルトン","レナン","カウアン"]
    ),
    "スペイン": (
        ["ガルシア","ロペス","マルティネス","ゴンザレス","ロドリゲス","フェルナンデス","サンチェス","ペレス","ゴメス","マルティン","ヒメネス","ルイス","ディアス","アルバレス","モレノ","ムニョス","アロンソ","グティエレス","ロメロ","トーレス","ナバロ","ベガ","ドミンゲス","ソト","イダルゴ","カストロ","セラーノ","プラド","イバニェス","ラモス"],
        ["アレハンドロ","パブロ","ダニエル","ミゲル","アドリアン","ハビエル","イバン","ルイス","マヌエル","アルバロ","ダビド","セルヒオ","ラウル","カルロス","マリオ","ホセ","フアン","サンティアゴ","ビクトル","フェリペ","アルベルト","イニゴ","ハイメ","エリック","ルベン","イサーク","サウル","ジェラルド","マルク","サミュエル"]
    ),
    "フランス": (
        ["マルタン","ベルナール","デュラン","プティ","ロベール","リシャール","フォール","ルイ","ルフェーブル","モロー","アンドレ","ヴィダル","ジョリー","ガイヤール","フィリップ","ピカール","ピエール","グラン","フローラン","バティスト","バルビエ","ジラール","パスカル","バンジャマン","パルド","ビダル","ボワイエ","ドゥビュッソン","メイヤー","ミラン"],
        ["ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク","ミカエル","ジュリアン","カミーユ","バスティアン","ロマン","アドリアン","ロイック","ガエル","ジョルダン","エリオット","エミール","テオ","エンゾ","ナタン","ウーゴ","アレクシス","ガブリエル","ルイ","クレマン","マティス"]
    ),
    "イタリア": (
        ["ロッシ","ルッソ","フェラーリ","エスポジト","ビアンキ","ロマーノ","コロンボ","リッチ","マリーニ","グレコ","ブルーノ","ガッリ","コンティ","マンチーニ","モレッティ","バルディーニ","ロンバルディ","マルティーニ","マルケージ","ヴィオリ","フィオリ","パルマ","ジアーニ","カッシーニ","ヴィタリ","ベルティ","サルトリ","ピッチーニ","カッパーニ","バルバ"],
        ["ファビオ","マルコ","アレッサンドロ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ","ルイジ","アントニオ","シモーネ","パオロ","フランチェスコ","クラウディオ","ステファノ","クリスティアン","ニコラ","ドメニコ","マッテオ","ルカ","エドアルド","レオナルド","ダヴィデ","ジーノ","ヴィットリオ","マルチェロ","カルロ","アンドレア","ジジ"]
    ),
    "ドイツ": (
        ["ミュラー","シュミット","シュナイダー","フィッシャー","ヴェーバー","マイヤー","ヴァーグナー","ベッカー","ホフマン","シュルツ","ケラー","リヒター","カール","バウアー","シュトルツ","ヴォルフ","ローゼ","ハルトマン","ヴァイス","ランゲ","ゲルハルト","フランク","ザイデル","ヴィンター","ミヒャエル","ドレッサー","エルンスト","カッツ","クレーマー","ブランク"],
        ["クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル","トビアス","フローリアン","クリストフ","ユリアン","モリッツ","フィリップ","アレクサンダー","シモン","フランク","オリバー","エミル","ノア","パスカル","レナード","ヨナス","レンツ","ベン","ユスティン","サミー","ベネディクト"]
    ),
    "イングランド": (
        ["スミス","ジョンソン","ウィリアムズ","ブラウン","ジョーンズ","ミラー","デイビス","テイラー","クラーク","ホワイト","ハリス","マーチン","トンプソン","ロビンソン","ライト","ウォーカー","ヒル","グリーン","キング","リチャーズ","アレン","モリス","クーパー","ジェームズ","ウッド","スコット","モーガン","ベイリー","ベネット","アダムズ"],
        ["トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ヘンリー","エドワード","ベンジャミン","ジョシュア","サミュエル","メイソン","ジョセフ","マシュー","リアム","アーチー","イーサン","ルイ","ジェイコブ","ディラン","アルフィー","マックス","レオ","タイラー","ハーヴィー","ジェイデン","ローガン"]
    )
}

def get_unique_name_by_nationality(nationality, used_names):
    fams, givens = names_data.get(nationality, (["Player"],["X"]))
    for _ in range(100):
        surname = random.choice(fams)
        given = random.choice(givens)
        if nationality == "日本":
            name = f"{surname} {given}"
        else:
            name = f"{given} {surname}"
        if name not in used_names:
            return name
    return f"{nationality}Player{random.randint(100,999)}"

# --- 顔写真自動割当（real顔。国籍ごとに変化） ---
def get_player_photo(nationality, seed_str):
    # 国籍に応じた人種/髪色/目色パターン
    nat2nat = {
        "日本":"asian", "中国":"asian", "韓国":"asian",
        "ブラジル":"latino", "スペイン":"latino", "イタリア":"mediterranean", "フランス":"mediterranean",
        "ドイツ":"white", "イングランド":"white"
    }
    nat = nat2nat.get(nationality,"white")
    # randomuser.me API (サッカー選手風・男性)
    # 男性だけ。顔seedとして名前をSHA1化
    import hashlib
    hexseed = hashlib.sha1(seed_str.encode()).hexdigest()
    idx = int(hexseed,16)%100  # 0〜99で大きくバラけ
    # APIのパターンを人種で調整
    if nat=="asian":
        gender = "male"
        return f"https://randomuser.me/api/portraits/men/{(idx%40)+60}.jpg"
    elif nat=="latino" or nat=="mediterranean":
        return f"https://randomuser.me/api/portraits/men/{(idx%30)+30}.jpg"
    else: # white, black etc.
        return f"https://randomuser.me/api/portraits/men/{(idx%60)}.jpg"

def ability_col(v):
    if v >= 90: return f"<span style='color:#20e660;font-weight:bold'>{v}</span>"
    if v >= 75: return f"<span style='color:#ffe600;font-weight:bold'>{v}</span>"
    return f"<span style='color:#1aacef'>{v}</span>"

def format_money(euro):
    if euro >= 1_000_000_000:
        return f"{euro/1_000_000_000:.2f}b€"
    elif euro >= 1_000_000:
        return f"{euro/1_000_000:.2f}m€"
    elif euro >= 1_000:
        return f"{euro/1_000:.1f}k€"
    return f"{int(euro)}€"

PLAYER_TEAM = "ストライバーFC"
AI_CLUB_NAMES = ["ブルーウルブズ", "ファルコンズ", "レッドスターズ", "ヴォルティス", "ユナイテッドFC", "オーシャンズ", "タイガース", "スカイバード"]
TEAM_NUM = 8
AI_TEAMS = AI_CLUB_NAMES[:TEAM_NUM-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_TEAMS

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
    for t in AI_TEAMS:
        for i in range(20):
            nationality = random.choice(list(names_data.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            used_names.add(name)
            ai_players.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(19,32), "国籍": nationality,
                "Spd": random.randint(60,85), "Pas": random.randint(60,85),
                "Phy": random.randint(60,85), "Sta": random.randint(60,85),
                "Def": random.randint(60,85), "Tec": random.randint(60,85),
                "Men": random.randint(60,85), "Sht": random.randint(60,85),
                "Pow": random.randint(60,85), "所属クラブ": t, "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

# --- データ読込・初期 ---
try:
    df = pd.read_csv("players.csv")
except:
    # 初回実行用ダミー
    used_names = set()
    data = []
    for i in range(18):
        nationality = random.choice(list(names_data.keys()))
        name = get_unique_name_by_nationality(nationality, used_names)
        used_names.add(name)
        pos = random.choice(["GK","DF","MF","FW"])
        age = random.randint(19,32)
        vals = {l:random.randint(60,88) for l in labels}
        vals.update({
            "名前":name,"ポジション":pos,"年齢":age,"国籍":nationality,
            "契約年数":random.randint(1,3),"年俸":random.randint(200_000,380_000),
            "得点":0,"出場数":0
        })
        data.append(vals)
    df = pd.DataFrame(data)
col_map = {'スピード':'Spd','パス':'Pas','フィジカル':'Phy','スタミナ':'Sta','ディフェンス':'Def','テクニック':'Tec','メンタル':'Men','シュート':'Sht','パワー':'Pow'}
df = df.rename(columns=col_map)
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000
df["総合"] = df[labels].mean(axis=1).astype(int)
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)
if "selected_player" not in st.session_state: st.session_state.selected_player = None

# --- 横スライド式タブ ---
tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save", "SNS"])

# --- Seniorタブ ---
with tabs[0]:
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
    st.markdown("#### Player Cards（横スクロール）")
    st.markdown('<div class="player-cards-row">', unsafe_allow_html=True)
    for idx, row in df_senior.iterrows():
        photo_url = get_player_photo(row["国籍"], row["名前"])
        st.markdown(
            f"""<div class='player-card'>
            <img src="{photo_url}">
            <b>{row['名前']}</b>
            <div class="pos-label">{row['ポジション']}</div>
            <br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}
            <br><span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
            <form action="#">
                <button class='detail-btn' onclick="return false;">詳細</button>
            </form>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Youthタブ ---
with tabs[1]:
    st.subheader("Youth Players")
    main_cols = ["名前","ポジション","年齢","国籍","契約年数","年俸","総合"]
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
        st.markdown("#### Player Cards（横スクロール）")
        st.markdown('<div class="player-cards-row">', unsafe_allow_html=True)
        for idx, row in df_youth.iterrows():
            photo_url = get_player_photo(row["国籍"], row["名前"])
            st.markdown(
                f"""<div class='player-card'>
                <img src="{photo_url}">
                <b>{row['名前']}</b>
                <div class="pos-label">{row['ポジション']}</div>
                <br>OVR:{row['総合']} / {row['年齢']} / {row['国籍']}
                <br><span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                <form action="#">
                    <button class='detail-btn' onclick="return false;">詳細</button>
                </form>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- Matchタブ ---
with tabs[2]:
    st.subheader("Match Simulation")
    round_idx = (st.session_state.current_round-1)%len(AI_TEAMS)
    enemy = AI_TEAMS[round_idx]
    st.write(f"今節: {PLAYER_TEAM} vs {enemy}")
    auto_starters = df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist()
    # ポジションごとに簡易選択
    pos_map = {"GK":1,"DF":4,"MF":4,"FW":2}
    selected = {}
    for pos, cnt in pos_map.items():
        pool = df_senior[df_senior["ポジション"]==pos]["名前"].tolist()
        selected[pos] = st.multiselect(f"{pos}", pool, default=pool[:cnt], key=f"starter_{pos}")
    starters = [p for l in selected.values() for p in l]
    st.markdown("")
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
            st.markdown(f"<b>推定勝率: <span style='color:#ffe066;font-size:1.13em'>{int(100*pwin)}%</span></b>", unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(4,1.3))
            ax.bar(["You","AI"], [team_strength, ai_strength], color=["#22e","#ccc"])
            ax.set_xticks([0,1]); ax.set_ylabel("平均能力")
            ax.set_title(f"チーム力比較", color="#f4f8fc")
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
with tabs[3]:
    st.subheader("Scout Candidates")
    st.markdown(f'<span class="budget-box">Budget: {format_money(st.session_state.budget)}</span>', unsafe_allow_html=True)
    if st.button("Refresh List"):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_list = []
        for _ in range(5):
            nationality = random.choice(list(names_data.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
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
        # ユーススカウト（14-18才で外国人も）
        for _ in range(3):
            nationality = random.choice(list(names_data.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            used_names.add(name)
            st.session_state.scout_list.append({
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(14, 18),
                "国籍": nationality,
                "Spd": random.randint(55, 75),
                "Pas": random.randint(55, 75),
                "Phy": random.randint(55, 75),
                "Sta": random.randint(55, 75),
                "Def": random.randint(55, 75),
                "Tec": random.randint(55, 75),
                "Men": random.randint(55, 75),
                "Sht": random.randint(55, 75),
                "Pow": random.randint(55, 75),
                "契約年数": 3,
                "年俸": random.randint(50_000,110_000),
                "得点": 0,
                "出場数": 0,
                "所属クラブ": PLAYER_TEAM
            })
    st.markdown('<div class="player-cards-row">', unsafe_allow_html=True)
    already = set(df["名前"].tolist())
    for idx, player in enumerate(st.session_state.scout_list):
        ovr = int(np.mean([player[l] for l in labels]))
        photo_url = get_player_photo(player["国籍"], player["名前"])
        st.markdown(
            f"""<div class='player-card'>
            <img src="{photo_url}">
            <b>{player['名前']}</b>
            <div class="pos-label">{player['ポジション']}</div>
            <br>OVR:{ovr} / {player['年齢']} / {player['国籍']}
            <br><span style='font-size:0.92em'>契約:{player['契約年数']}｜年俸:{format_money(player['年俸'])}</span>
            """, unsafe_allow_html=True)
        if player["名前"] not in already:
            if st.button("加入", key=f"scout_{idx}"):
                df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                df.to_csv("players.csv", index=False)
                st.session_state.budget -= player['年俸']
                st.success(f"{player['名前']} signed!")
                st.session_state["移籍履歴"].append(f"{player['名前']}（{player['国籍']}）をスカウトで獲得！")
        else:
            st.markdown("<span style='color:#999;font-size:0.93em'>既に在籍</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Standings ---
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
        pts = st.session_state.team_points.get(t,0)
        tbl.append([t, pts, total_goals])

    dft = pd.DataFrame(tbl, columns=["Club","Pts","Goals"])
    dft = dft.sort_values(["Pts","Goals"], ascending=[False,False]).reset_index(drop=True)
    dft["Rank"] = dft.index + 1
    dft = dft[["Rank","Club","Pts","Goals"]]
    st.markdown(
        "<div class='mobile-table table-highlight'><table><thead><tr>" +
        "".join([f"<th>{col}</th>" for col in dft.columns]) +
        "</tr></thead><tbody>" +
        "".join([
            "<tr>" + "".join([f"<td>{row[col]}</td>" for col in dft.columns]) + "</tr>"
            for _, row in dft.iterrows()
        ]) +
        "</tbody></table></div>", unsafe_allow_html=True
    )
    if st.session_state.match_log:
        st.markdown("**Recent Matches**")
        for l in st.session_state.match_log[-5:][::-1]:
            st.text(l)

# --- Save ---
with tabs[5]:
    st.subheader("Data Save")
    if st.button("Save (players.csv)"):
        df.to_csv("players.csv", index=False)
        st.success("Saved! (players.csv)")
    if st.button("Save AI Players List"):
        st.session_state.ai_players.to_csv("ai_players.csv", index=False)
        st.success("AI Players list saved.")

# --- SNS ---
with tabs[6]:
    st.subheader("SNS / Event Feed")
    if st.session_state["移籍履歴"]:
        st.write("### Recent Transfers")
        for news in st.session_state["移籍履歴"][-5:][::-1]:
            st.info(news)
    if st.session_state.match_log:
        st.write("### Recent Matches")
        for l in st.session_state.match_log[-5:][::-1]:
            st.write(l)

st.caption("最新版｜顔写真リアル自動／多国籍対応／UI色調整・横スクロール・詳細ボタン付き（2025-07 最新）")
