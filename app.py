import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import matplotlib

# --- matplotlib日本語フォント指定（環境に合わせて！） ---
matplotlib.rc('font', family='IPAexGothic')

# --- UIデザイン（濃紺+強コントラスト/白） ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(120deg, #122042 0%, #202f52 100%); color: #f6f7fa; }
    .stDataFrame th, .stDataFrame td { color: #2fefff !important; background: #141e32 !important; }
    .stButton>button, .stRadio>div>label { color: #fff !important; }
    .player-card {
        background: #162245;
        color: #f6f7fa;
        border-radius: 15px;
        padding: 16px 14px 7px 14px;
        margin: 6px 3px;
        box-shadow: 0 0 8px #12204244;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 160px; max-width: 192px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 名前リストを大幅増強 ---
name_pools = {
    "日本": ["佐藤 翔","木村 隼人","西村 陸","大谷 陽平","本田 悠真","松岡 悠人","飯田 啓太","吉田 海斗","白石 翼","黒田 隆成",
        "長谷川 海斗","松本 凛","森本 優","斉藤 颯太","安藤 匠","高橋 拓真","小林 蓮","山本 大輝","田中 光","加藤 大和",
        "福島 光希","中村 慎吾","山崎 陸斗","藤井 悠馬","三浦 洸太","伊藤 楓","近藤 洋平","山口 航","岡田 駿","清水 晴斗"],
    "ブラジル": ["マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ",
        "ブルーノ","レアンドロ","ファビオ","ダニーロ","グスタボ","ガブリエル","レナン","ヴィトル","ラファエル","ジョルジ",
        "チアゴ","エンリケ","レナト","カイオ","ジエゴ","ジウベルト","カルロス","イゴール","ラファ","ジュニオル"],
    "スペイン": ["サンチェス","ロペス","マルティン","ミゲル","フェルナンド","フアン","カルロス","ダビド","ルイス","ペレス",
        "パブロ","ロドリゴ","アルバロ","セルヒオ","イバン","マリオ","マヌエル","ラウル","ヘスス","ゴンサロ",
        "マルコス","ディエゴ","サエス","サモラ","アドリアン","エステバン","アルベルト","イサーク","ジェラルド"],
    "フランス": ["ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク",
        "ミカエル","ジュリアン","カミーユ","バスティアン","ロマン","アドリアン","ロイック","ガエル","ジョルダン","バンジャマン",
        "マチュー","セバスチャン","ティエリ","ジャン＝ルイ","ギョーム","ユーゴ","ロラン","パトリス","ステファン"],
    "イタリア": ["ファビオ","マルコ","アレッサンドロ","ロッシ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ",
        "ルイジ","アントニオ","シモーネ","ジジ","パオロ","フランチェスコ","クラウディオ","ステファノ","クリスティアン","ニコラ",
        "ジャンルカ","マウリツィオ","ロベルト","アンドレア","サンドロ","アメデオ","ドメニコ","ダビデ","ピエトロ"],
    "ドイツ": ["クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル",
        "トビアス","フローリアン","クリストフ","ユリアン","モリッツ","フィリップ","アレクサンダー","シモン","フランク","オリバー",
        "ヤン","マルセル","ヨナス","ベネディクト","カイ","パスカル","マークス","マルティン","パトリック"],
    "イングランド": ["トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ルーカス",
        "ヘンリー","エドワード","ベンジャミン","ジョシュア","サミュエル","メイソン","ジョセフ","マシュー","リアム","アーチー",
        "ジェイデン","イーサン","ディラン","ローガン","ハーヴィー","アルフィー","ルイス","ザック","エリオット"],
}

def get_unique_name_by_nationality(nationality, used_names):
    pool = name_pools.get(nationality, [])
    for name in pool:
        if name not in used_names:
            return name
    return f"{nationality}ネーム{random.randint(100,999)}"

# --- 定数 ---
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

# --- セッション初期化 ---
if "current_round" not in st.session_state: st.session_state.current_round = 1
if "scout_list" not in st.session_state: st.session_state.scout_list = []
if "youth_scout_list" not in st.session_state: st.session_state.youth_scout_list = []
if "budget" not in st.session_state: st.session_state.budget = 1_000_000
if "team_points" not in st.session_state: st.session_state.team_points = {t: 0 for t in ALL_TEAMS}
if "match_log" not in st.session_state: st.session_state.match_log = []
if "ai_players" not in st.session_state:
    ai_players = []
    used_names = set()
    AI_TYPES = ["攻撃型", "守備型", "バランス型"]
    for t in AI_TEAMS:
        ai_type = random.choice(AI_TYPES)
        for i in range(20):
            nationality = random.choice(list(name_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            used_names.add(name)
            ai_players.append({
                "名前": name, "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(19,32), "国籍": nationality,
                "スピード": random.randint(60,85), "パス": random.randint(60,85),
                "フィジカル": random.randint(60,85), "スタミナ": random.randint(60,85),
                "ディフェンス": random.randint(60,85), "テクニック": random.randint(60,85),
                "メンタル": random.randint(60,85), "シュート": random.randint(60,85),
                "パワー": random.randint(60,85), "所属クラブ": t, "AIタイプ": ai_type,
                "出場数": 0, "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

# --- データ読込＆初期分割 ---
df = pd.read_csv("players.csv")
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0
if "契約年数" not in df.columns: df["契約年数"] = 2
if "年俸" not in df.columns: df["年俸"] = 120_000
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)

# === タイトル・UI ===
st.title("サッカー運営シミュレーション v9（新UI/自動試合/名前増量）")
st.markdown(f"**現在 {st.session_state.current_round} 節｜予算**: {format_money(st.session_state.budget)}")
main_tab = st.radio("表示", ("シニア", "ユース", "試合", "スカウト", "順位表", "セーブ"), horizontal=True)

# === シニア選手リスト：タイル型横並びグリッド表示 ===
if main_tab == "シニア":
    st.subheader("【シニア選手一覧】")
    cols = st.columns(4)
    for idx, row in df_senior.iterrows():
        with cols[idx%4]:
            st.markdown(f"<div class='player-card'>"
                        f"<b>{row['名前']}</b><br>"
                        f"{row['ポジション']} / {row['年齢']}歳 / {row['国籍']}<br>"
                        f"契約:{row['契約年数']}年｜年俸:{format_money(row['年俸'])}", unsafe_allow_html=True)
            stats = [float(row[l]) for l in labels]
            stats += stats[:1]
            angles = np.linspace(0, 2 * np.pi, len(labels)+1)
            fig, ax = plt.subplots(figsize=(2,2), subplot_kw=dict(polar=True))
            ax.plot(angles, stats, color="#1cefff", linewidth=2)
            ax.fill(angles, stats, color="#1cefff", alpha=0.13)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=8, color='#f4f8fc')
            ax.set_yticklabels([])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, transparent=True)
            st.markdown("</div>", unsafe_allow_html=True)

# === ユースもタイル式・スカウトにレーダーチャート ===
if main_tab == "ユース":
    st.subheader("【ユース選手一覧】")
    cols = st.columns(4)
    for idx, row in df_youth.iterrows():
        with cols[idx%4]:
            st.markdown(f"<div class='player-card'>"
                        f"<b>{row['名前']}</b><br>"
                        f"{row['ポジション']} / {row['年齢']}歳 / {row['国籍']}<br>"
                        f"契約:{row['契約年数']}年｜年俸:{format_money(row['年俸'])}", unsafe_allow_html=True)
            stats = [float(row[l]) for l in labels]
            stats += stats[:1]
            angles = np.linspace(0, 2 * np.pi, len(labels)+1)
            fig, ax = plt.subplots(figsize=(2,2), subplot_kw=dict(polar=True))
            ax.plot(angles, stats, color="#ffef41", linewidth=2)
            ax.fill(angles, stats, color="#ffef41", alpha=0.13)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=8, color='#f4f8fc')
            ax.set_yticklabels([])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, transparent=True)
            st.markdown("</div>", unsafe_allow_html=True)

# === 試合（自動AIマッチング） ===
if main_tab == "試合":
    st.subheader("【今節の対戦】")
    round_idx = (st.session_state.current_round-1)%len(AI_TEAMS)
    enemy = AI_TEAMS[round_idx]
    st.write(f"今節: {PLAYER_TEAM} vs {enemy}")
    # スタメン自動（能力順上位11名/未選択なら）
    auto_starters = df_senior.sort_values(labels, ascending=False).head(11)["名前"].tolist()
    starters = st.multiselect("出場メンバー（11人）", df_senior["名前"].tolist(), default=auto_starters)
    if len(starters) != 11:
        st.warning("11人ちょうど選んでください")
    else:
        tactics = st.selectbox("チーム戦術", ["攻撃的", "バランス", "守備的", "カウンター", "ポゼッション"])
        # チーム力比較グラフ
        team_strength = df_senior[df_senior["名前"].isin(starters)][labels].mean().mean()
        ai_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==enemy]
        ai_strength = ai_df[labels].mean().mean()
        if tactics=="攻撃的": team_strength *= 1.08
        elif tactics=="守備的": team_strength *= 0.93
        elif tactics=="カウンター": team_strength *= 1.04
        elif tactics=="ポゼッション": team_strength *= 1.03
        # 勝率計算
        pwin = (team_strength / (team_strength+ai_strength)) if (team_strength+ai_strength)>0 else 0.5
        fig, ax = plt.subplots(figsize=(4,1.4))
        ax.bar(["自クラブ","AI"], [team_strength, ai_strength], color=["#22e","#ccc"])
        ax.set_xticks([0,1]); ax.set_ylabel("平均能力")
        ax.set_title(f"チーム力比較（推定勝率: {int(100*pwin)}%）", color="#f4f8fc")
        fig.patch.set_alpha(0)
        st.pyplot(fig, transparent=True)
        if st.button("試合開始！"):
            my_goals = max(0, int(random.gauss((team_strength-60)/8, 1.0)))
            op_goals = max(0, int(random.gauss((ai_strength-60)/8, 1.0)))
            # 勝ち点
            if my_goals > op_goals:
                result = "勝利"
                st.session_state.team_points[PLAYER_TEAM] += 3
            elif my_goals < op_goals:
                result = "敗北"
                st.session_state.team_points[enemy] += 3
            else:
                result = "引き分け"
                st.session_state.team_points[PLAYER_TEAM] += 1
                st.session_state.team_points[enemy] += 1
            st.success(f"{result}！ {my_goals}-{op_goals}")
            st.session_state.current_round += 1
            st.session_state.match_log.append(f"{st.session_state.current_round-1}節 {PLAYER_TEAM} vs {enemy}: {my_goals}-{op_goals}")

# === スカウト（タイル＋レーダーチャートつき） ===
if main_tab == "スカウト":
    st.subheader("【スカウト候補】")
    st.info(f"予算: {format_money(st.session_state.budget)}")
    if st.button("スカウトリストを更新"):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_list = []
        for _ in range(5):
            nationality = random.choice(list(name_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names)
            used_names.add(name)
            st.session_state.scout_list.append({
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(19, 29),
                "国籍": nationality,
                "スピード": random.randint(60, 80),
                "パス": random.randint(60, 80),
                "フィジカル": random.randint(60, 80),
                "スタミナ": random.randint(60, 80),
                "ディフェンス": random.randint(60, 80),
                "テクニック": random.randint(60, 80),
                "メンタル": random.randint(60, 80),
                "シュート": random.randint(60, 80),
                "パワー": random.randint(60, 80),
                "契約年数": 2,
                "年俸": random.randint(100_000,180_000),
                "得点": 0,
                "出場数": 0,
                "所属クラブ": PLAYER_TEAM
            })
    cols = st.columns(5)
    for idx, player in enumerate(st.session_state.scout_list):
        with cols[idx%5]:
            st.markdown(f"<div class='player-card'>"
                        f"<b>{player['名前']}</b><br>"
                        f"{player['ポジション']} / {player['年齢']}歳 / {player['国籍']}<br>"
                        f"契約:{player['契約年数']}年｜年俸:{format_money(player['年俸'])}", unsafe_allow_html=True)
            stats = [float(player[l]) for l in labels]
            stats += stats[:1]
            angles = np.linspace(0, 2 * np.pi, len(labels)+1)
            fig, ax = plt.subplots(figsize=(1.6,1.6), subplot_kw=dict(polar=True))
            ax.plot(angles, stats, color="#ff8e41", linewidth=2)
            ax.fill(angles, stats, color="#ff8e41", alpha=0.13)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=7, color='#f4f8fc')
            ax.set_yticklabels([])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, transparent=True)
            btn_key = f"scout_{idx}"
            if st.button("加入", key=btn_key):
                df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                df.to_csv("players.csv", index=False)
                st.session_state.budget -= player['年俸']
                st.success(f"{player['名前']}が加入！")
            st.markdown("</div>", unsafe_allow_html=True)

# === 順位表/リーグ管理 ===
if main_tab == "順位表":
    st.subheader("【リーグ順位表】")
    tbl = []
    for t in ALL_TEAMS:
        tbl.append([t, st.session_state.team_points.get(t,0)])
    dft = pd.DataFrame(tbl, columns=["クラブ","勝ち点"])
    st.dataframe(dft.sort_values("勝ち点", ascending=False), use_container_width=True)
    if st.session_state.match_log:
        st.markdown("**直近試合ログ**")
        for l in st.session_state.match_log[-5:][::-1]:
            st.text(l)

# === セーブ機能 ===
if main_tab == "セーブ":
    st.subheader("【セーブ】")
    if st.button("データ保存（players.csv）"):
        df.to_csv("players.csv", index=False)
        st.success("セーブ完了！（players.csv）")
    if st.button("AIクラブ選手リスト保存"):
        st.session_state.ai_players.to_csv("ai_players.csv", index=False)
        st.success("AIクラブ選手リストも保存しました")
