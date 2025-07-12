import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# ========== ① UIデザイン/CSS ==========
TEAM_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/6/67/Soccer_ball_animated.svg"
st.markdown("""
    <style>
    html, body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
    .stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff; }
    .player-card {
        background: #fff; color: #133469; border-radius: 15px;
        padding: 12px 10px 8px 10px; margin: 10px 2vw 15px 2vw;
        box-shadow: 0 0 13px #20b6ff33;
        display: flex; flex-direction: column; align-items: center;
        min-width: 140px; max-width: 170px; font-size:0.99em;
        transition: 0.15s; border: 2px solid #25b5ff20; position: relative;
    }
    .player-card img {border-radius:50%;margin-bottom:10px;border:2px solid #3398d7;background:#fff;}
    .player-card.selected {border: 2.7px solid #f5e353; box-shadow: 0 0 16px #f5e35399;}
    .player-card:hover {
        background: #f8fcff; color: #1b54a4; transform: scale(1.03);
        box-shadow: 0 0 13px #1cefff55; border:2px solid #42d8ff;
    }
    .mobile-table {overflow-x:auto; white-space:nowrap;}
    .mobile-table th, .mobile-table td {
        padding: 4px 9px; font-size: 14px; border-bottom: 1.3px solid #1c2437;
    }
    .table-highlight th, .table-highlight td {
        background: #182649 !important; color: #ffe45a !important; border-bottom: 1.4px solid #24335d !important;
    }
    /* タブ文字色・背景補正 */
    .stTabs [data-baseweb="tab"] {
      color: #fff !important;
      background: linear-gradient(90deg,#183860 40%,#3650a0 100%) !important;
      border-radius: 13px 13px 0 0 !important;
      margin-right: 2px !important;
    }
    .stTabs [aria-selected="true"] {
      color: #ffe45a !important; background: #243c78 !important;
      border-bottom: 4px solid #ffe45a !important;
    }
    /* 予算欄カラー */
    .custom-budget {background:#fff7d7; color:#1c2c44 !important; padding:7px 15px;border-radius:14px;margin-bottom:14px;font-weight:bold;display:inline-block;}
    .position-text {color:#fff !important; font-weight:bold;}
    </style>
""", unsafe_allow_html=True)

st.image(TEAM_LOGO_URL, width=48)
st.title("Soccer Club Management Sim")

labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
labels_full = {
    'Spd':'Speed','Pas':'Pass','Phy':'Physical','Sta':'Stamina','Def':'Defense',
    'Tec':'Technique','Men':'Mental','Sht':'Shoot','Pow':'Power'
}

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

# ========== ② 名前リスト（30種×7ヶ国） ==========
names_by_country = {
    "日本": [("佐藤", "翔"),("田中", "隼人"),("鈴木", "陸"),("高橋", "陽平"),("山本", "悠真"),
             ("中村", "悠人"),("小林", "啓太"),("加藤", "海斗"),("吉田", "翼"),("渡辺", "隆成"),
             ("山田", "凛"),("松本", "優"),("斎藤", "颯太"),("木村", "匠"),("林", "拓真"),
             ("清水", "蓮"),("山口", "大輝"),("池田", "光"),("森", "大和"),("石川", "光希"),
             ("橋本", "慎吾"),("阿部", "陸斗"),("山崎", "悠馬"),("井上", "洸太"),("岡田", "楓"),
             ("村上", "洋平"),("石井", "航"),("三浦", "駿"),("上田", "晴斗"),("原田", "航太")],
    "ブラジル": [("シウバ","マテウス"),("サントス","パブロ"),("コスタ","ルーカス"),("オリヴェイラ","リカルド"),
        ("ソウザ","アンドレ"),("フェレイラ","ジョアン"),("ロドリゲス","エリック"),("ペレイラ","ペドロ"),
        ("アウベス","マルコス"),("リマ","ジオバニ"),("ゴンサウベス","ブルーノ"),("ゴメス","レアンドロ"),
        ("マルチンス","ファビオ"),("マシャド","ダニーロ"),("ロペス","グスタボ"),("メンドンサ","ガブリエル"),
        ("アラウージョ","レナン"),("ピント","ヴィトル"),("カルドーゾ","ラファエル"),("カストロ","ジョルジ"),
        ("モラエス","チアゴ"),("フレイタス","エンリケ"),("パイヴァ","レナト"),("ドスサントス","カイオ"),
        ("バルボーザ","ジエゴ"),("メロ","ジウベルト"),("テイシェイラ","カルロス"),("ドミンゲス","イゴール"),
        ("メンドンサ","ラファ"),("カブラル","ジュニオル")],
    "スペイン": [("ガルシア","アレハンドロ"),("ロペス","パブロ"),("マルティネス","ダニエル"),
        ("ゴンザレス","ミゲル"),("ロドリゲス","アドリアン"),("フェルナンデス","ハビエル"),
        ("サンチェス","イバン"),("ペレス","ルイス"),("ゴメス","マヌエル"),("マルティン","ディエゴ"),
        ("ヒメネス","アルバロ"),("ルイス","ダビド"),("ディアス","セルヒオ"),("アルバレス","ラウル"),
        ("モレノ","カルロス"),("ムニョス","マリオ"),("アロンソ","ホセ"),("グティエレス","ロドリゴ"),
        ("ロメロ","フアン"),("トーレス","アルトゥーロ"),("ナバロ","サンティアゴ"),("ドミンゲス","ビクトル"),
        ("ベガ","ガブリエル"),("ソト","フェリペ"),("サラサル","アルベルト"),("カストロ","イニゴ"),
        ("セラーノ","ハイメ"),("イダルゴ","エリック"),("ラモス","ルベン"),("イバニェス","イサーク")],
    "フランス": [("マルタン","ピエール"),("ベルナール","ジャン"),("デュラン","トマ"),("プティ","アントワン"),
        ("ロベール","レオン"),("リシャール","アンリ"),("フォール","ルカ"),("ガルシア","ダニエル"),
        ("ルイ","パスカル"),("ルフェーブル","マルク"),("モロー","ミカエル"),("ルルー","ジュリアン"),
        ("アンドレ","カミーユ"),("ルジェ","バスティアン"),("コロンブ","ロマン"),("ヴィダル","アドリアン"),
        ("ジョリー","ロイック"),("ガイヤール","ガエル"),("フィリップ","ジョルダン"),("ピカール","バンジャマン"),
        ("ピエール","エリオット"),("ボワイエ","エミール"),("ブラン","テオ"),("バルビエ","エンゾ"),
        ("ジラール","ナタン"),("アダン","ウーゴ"),("パスカル","トリスタン"),("フローラン","アレクシス"),
        ("バティスト","ガブリエル"),("シャルパンティエ","ルイ")],
    "イタリア": [("ロッシ","ファビオ"),("ルッソ","マルコ"),("フェラーリ","アレッサンドロ"),("エスポジト","サルヴァトーレ"),
        ("ビアンキ","ダニエレ"),("ロマーノ","トーマス"),("コロンボ","ロレンツォ"),("リッチ","ミケーレ"),
        ("マリーニ","エミリオ"),("グレコ","ルイジ"),("ブルーノ","アントニオ"),("ガッリ","シモーネ"),
        ("コンティ","ジジ"),("マンチーニ","パオロ"),("モレッティ","フランチェスコ"),("バルディーニ","クラウディオ"),
        ("ジェンティーレ","ステファノ"),("ロンバルディ","クリスティアン"),("マルティーニ","ニコラ"),("マルケージ","ドメニコ"),
        ("ヴィオリ","マッテオ"),("ジアーニ","エンリコ"),("フィオリ","カルロ"),("パルマ","アンドレア"),
        ("デサンティス","サミュエレ"),("ヴェントゥーラ","アウグスト"),("カッシーニ","ルチアーノ"),("ベルティ","ジーノ"),
        ("ヴィタリ","ロベルト"),("カッパーニ","エドアルド")],
    "ドイツ": [("ミュラー","クラウス"),("シュミット","ティモ"),("シュナイダー","ミヒャエル"),("フィッシャー","ルーカス"),
        ("ヴェーバー","マティアス"),("マイヤー","セバスティアン"),("ヴァーグナー","ニコ"),("ベッカー","ラファエル"),
        ("ホフマン","カミーロ"),("シュルツ","ダニエル"),("ケラー","トビアス"),("リヒター","フローリアン"),
        ("クレーマー","クリストフ"),("カール","ユリアン"),("バウアー","モリッツ"),("シュトルツ","フィリップ"),
        ("ヴォルフ","アレクサンダー"),("ピンター","シモン"),("ブランク","フランク"),("リース","オリバー"),
        ("ローゼ","エミル"),("ハルトマン","ノア"),("ヴァイス","パスカル"),("ランゲ","レナード"),
        ("ボッシュ","レオナルド"),("ゲルハルト","カール"),("フランク","フェリックス"),("ザイデル","マルクス"),
        ("ヴィンター","イェンス"),("メッツガー","ベネディクト")],
    "イングランド": [("スミス","トーマス"),("ジョンソン","ジェームズ"),("ウィリアムズ","ウィリアム"),("ブラウン","ハリー"),
        ("ジョーンズ","ジョージ"),("ミラー","ジャック"),("デイビス","チャールズ"),("テイラー","ダニエル"),
        ("クラーク","オリバー"),("ホワイト","ルーカス"),("ハリス","ヘンリー"),("マーチン","エドワード"),
        ("トンプソン","ベンジャミン"),("ロビンソン","ジョシュア"),("ライト","サミュエル"),("ウォーカー","メイソン"),
        ("ヒル","ジョセフ"),("グリーン","マシュー"),("キング","リアム"),("リチャーズ","アーチー"),
        ("アレン","イーサン"),("モリス","ルイ"),("クーパー","ジェイコブ"),("ベイリー","ディラン"),
        ("ジェームズ","アルフィー"),("ウッド","マックス"),("スコット","レオ"),("モーガン","アレクサンダー"),
        ("ベネット","タイラー"),("アダムズ","ハーヴィー")]
}

# ========== ③ 顔写真URLジェネレーター（国籍・人種・顔被り防止） ==========
def get_player_photo_url(name, nationality):
    # 1. StableDiffusion等を使った本格APIなら本当はここに組み込む
    # 2. ただし安定性重視＆無料APIであればDiceBear notionistsかthumbs（国籍っぽさは控えめ・被り防止はseed指定）
    # 3. 完全に被りを避けるには「名前＋国名」をseed化
    # 4. サッカー選手感&男性: notionists/identicon/avataaars系だと一番安定
    url = f"https://api.dicebear.com/7.x/notionists/png?seed={name}-{nationality}&backgroundColor=fffafa,e7e9ef&radius=50"
    return url

# ========== ④ 初期設定・データ管理 ==========
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
    random.seed(42)
    for t in AI_TEAMS:
        used_name_idx = set()
        for i in range(20):
            nat = random.choice(list(names_by_country.keys()))
            idx = random.randint(0, 29)
            while (nat, idx) in used_name_idx:
                idx = random.randint(0, 29)
            used_name_idx.add((nat, idx))
            surname, given = names_by_country[nat][idx]
            if nat == "日本":
                name = f"{surname} {given}"
            else:
                name = f"{given} {surname}"
            ai_players.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(19,32), "国籍": nat,
                "Spd": random.randint(60,85), "Pas": random.randint(60,85),
                "Phy": random.randint(60,85), "Sta": random.randint(60,85),
                "Def": random.randint(60,85), "Tec": random.randint(60,85),
                "Men": random.randint(60,85), "Sht": random.randint(60,85),
                "Pow": random.randint(60,85), "所属クラブ": t, "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

# ========== ⑤ CSV読込＆自クラブ選手生成 ==========
try:
    df = pd.read_csv("players.csv")
except Exception:
    # 無い場合は初期サンプル生成
    df = pd.DataFrame([
        {
            "名前": f"{given} {surname}" if nat!="日本" else f"{surname} {given}",
            "ポジション": random.choice(["GK","DF","MF","FW"]),
            "年齢": random.randint(19,28),
            "国籍": nat,
            "Spd": random.randint(60,85),"Pas": random.randint(60,85),
            "Phy": random.randint(60,85),"Sta": random.randint(60,85),
            "Def": random.randint(60,85),"Tec": random.randint(60,85),
            "Men": random.randint(60,85),"Sht": random.randint(60,85),
            "Pow": random.randint(60,85),
            "契約年数":2,"年俸":120_000,"所属クラブ":PLAYER_TEAM,"得点":0,"出場数":0
        }
        for nat in names_by_country for surname,given in names_by_country[nat][:4]
    ])
col_map = {'スピード':'Spd','パス':'Pas','フィジカル':'Phy','スタミナ':'Sta',
    'ディフェンス':'Def','テクニック':'Tec','メンタル':'Men','シュート':'Sht','パワー':'Pow'}
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

# ========== ⑥ タブ生成 ==========
tabs = st.tabs(["Senior", "Youth", "Match", "Scout", "Standings", "Save", "SNS"])

# ======== Seniorタブ =========
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
    st.markdown("#### Player Cards")
    cols = st.columns(2 if st.session_state.get("mobile",False) else 4)
    for idx, row in df_senior.iterrows():
        with cols[idx%len(cols)]:
            card_class = "player-card"
            avatar_url = get_player_photo_url(row["名前"], row["国籍"])
            st.markdown(
                f"""<div class='{card_class}'>
                <img src="{avatar_url}" width="64">
                <b>{row['名前']}</b>
                <br><span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span>
                <br><span class="position-text">{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}
                <br><span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                </div>""", unsafe_allow_html=True)

# ======== Youthタブ =========
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
        st.markdown("#### Player Cards")
        cols = st.columns(2 if st.session_state.get("mobile",False) else 4)
        for idx, row in df_youth.iterrows():
            with cols[idx%len(cols)]:
                card_class = "player-card"
                avatar_url = get_player_photo_url(row["名前"], row["国籍"])
                st.markdown(
                    f"""<div class='{card_class}'>
                    <img src="{avatar_url}" width="64">
                    <b>{row['名前']}</b>
                    <br><span style='color:#27b0e7;font-weight:bold'>OVR:{row['総合']}</span>
                    <br><span class="position-text">{row['ポジション']}</span> / {row['年齢']} / {row['国籍']}
                    <br><span style='font-size:0.92em'>契約:{row['契約年数']}｜年俸:{format_money(row['年俸'])}</span>
                    </div>""", unsafe_allow_html=True)

# ======== Matchタブ =========
with tabs[2]:
    st.subheader("Match Simulation")
    round_idx = (st.session_state.current_round-1)%len(AI_TEAMS)
    enemy = AI_TEAMS[round_idx]
    st.write(f"今節: {PLAYER_TEAM} vs {enemy}")
    # 簡易ポジション自動割当・手動変更
    default_pos = ["GK"] + ["DF"]*4 + ["MF"]*3 + ["FW"]*3
    auto_starters = df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist()
    starters = st.multiselect("Starting XI", df_senior["名前"].tolist(), default=auto_starters, key="starters")
    if len(starters) != 11:
        st.warning("11人ちょうど選んでください")
    else:
        pos_assign = st.radio("ポジション割当", options=["自動","カスタム"], horizontal=True)
        if pos_assign=="自動":
            pos_text = " / ".join(default_pos)
        else:
            custom_pos = st.text_input("例: GK,DF,DF,DF,DF,MF,MF,MF,FW,FW,FW", value=",".join(default_pos))
            pos_text = custom_pos
        st.markdown(f"<span style='color:#fff;background:#2b3c69;padding:6px 18px;border-radius:9px;font-size:1.1em'>先発ポジション: {pos_text}</span>", unsafe_allow_html=True)
        tactics = st.selectbox("Tactics", ["Attack", "Balanced", "Defensive", "Counter", "Possession"])
        # 白ベース・黒文字のKickoff
        kickoff_btn = st.button("Kickoff!", key=f"kick_{datetime.now().isoformat()}_{random.random()}", 
                               help="試合を開始")
        if kickoff_btn:
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
            # 勝率予想も組み込み
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

# ======== Scoutタブ =========
with tabs[3]:
    st.subheader("Scout Candidates")
    st.markdown(f'<div class="custom-budget">Budget: {format_money(st.session_state.budget)}</div>', unsafe_allow_html=True)
    if st.button("Refresh List"):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_list = []
        for _ in range(5):
            nat = random.choice(list(names_by_country.keys()))
            idx = random.randint(0,29)
            surname, given = names_by_country[nat][idx]
            if nat == "日本":
                name = f"{surname} {given}"
            else:
                name = f"{given} {surname}"
            st.session_state.scout_list.append({
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(19, 29),
                "国籍": nat,
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
    cols = st.columns(2 if st.session_state.get("mobile",False) else 3)
    already = set(df["名前"].tolist())
    for idx, player in enumerate(st.session_state.scout_list):
        with cols[idx%len(cols)]:
            ovr = int(np.mean([player[l] for l in labels]))
            avatar_url = get_player_photo_url(player["名前"], player["国籍"])
            st.markdown(
                f"<div class='player-card'><img src='{avatar_url}' width='48'><b>{player['名前']}</b> <span style='color:#2cabe8;'>(OVR:{ovr})</span><br>"
                f"<span class='position-text'>{player['ポジション']}</span> / {player['年齢']} / {player['国籍']}<br>"
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

# ======== Standingsタブ =========
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

# ======== Saveタブ =========
with tabs[5]:
    st.subheader("Data Save")
    if st.button("Save (players.csv)"):
        df.to_csv("players.csv", index=False)
        st.success("Saved! (players.csv)")
    if st.button("Save AI Players List"):
        st.session_state.ai_players.to_csv("ai_players.csv", index=False)
        st.success("AI Players list saved.")

# ======== SNSタブ =========
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

st.caption("AIリアル調サッカー選手写真（国籍人種対応・自動割当・エラー防止）全機能統合版")
