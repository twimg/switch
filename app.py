import streamlit as st
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

# ====== 名前リスト（枯渇時は自動生成） ======
name_pools = {
    "日本": ["佐藤 翔","木村 隼人","西村 陸","大谷 陽平","本田 悠真","松岡 悠人","飯田 啓太","吉田 海斗","白石 翼","黒田 隆成","長谷川 海斗","松本 凛","森本 優","斉藤 颯太","安藤 匠","高橋 拓真","山本 大輝","小林 蓮","田中 光","加藤 大和"],
    "ブラジル": ["マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ","ブルーノ","レアンドロ","ファビオ","ダニーロ","グスタボ","ガブリエル","レナン","ヴィトル","ラファエル","ジョルジ"],
    "スペイン": ["サンチェス","ロペス","マルティン","ミゲル","フェルナンド","フアン","カルロス","ダビド","ルイス","ペレス","パブロ","ロドリゴ","アルバロ","セルヒオ","イバン","マリオ","マヌエル","ラウル","ヘスス","ゴンサロ"],
    "フランス": ["ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク","ミカエル","ジュリアン","カミーユ","バスティアン","ロマン","アドリアン","ロイック","ガエル","ジョルダン","バンジャマン"],
    "イタリア": ["ファビオ","マルコ","アレッサンドロ","ロッシ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ","ルイジ","アントニオ","シモーネ","ジジ","パオロ","フランチェスコ","クラウディオ","ステファノ","クリスティアン","ニコラ"],
    "ドイツ": ["クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル","トビアス","フローリアン","クリストフ","ユリアン","モリッツ","フィリップ","アレクサンダー","シモン","フランク","オリバー"],
    "イングランド": ["トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ルーカス","ヘンリー","エドワード","ベンジャミン","ジョシュア","サミュエル","メイソン","ジョセフ","マシュー","リアム","アーチー"]
}

def get_unique_name_by_nationality(nationality, used_names):
    pool = name_pools.get(nationality, [])
    for name in pool:
        if name not in used_names:
            return name
    # 枯渇時は「カタカナ名＋数字」
    return f"{nationality}ネーム{len(used_names)%1000}"

PLAYER_TEAM = "ストライバーFC"
AI_CLUB_NAMES = ["ブルーウルブズ", "ファルコンズ", "レッドスターズ", "ヴォルティス", "ユナイテッドFC", "オーシャンズ", "タイガース", "スカイバード", "イーグルス", "キングス"]
TEAM_NUM = 8
random.seed(42)
random.shuffle(AI_CLUB_NAMES)
AI_TEAMS = AI_CLUB_NAMES[:TEAM_NUM-1]
ALL_TEAMS = [PLAYER_TEAM] + AI_TEAMS
labels = ['スピード','パス','フィジカル','スタミナ','ディフェンス','テクニック','メンタル','シュート','パワー']

# --- 名前リスト ---
name_pools = {
    "日本": ["佐藤 翔","木村 隼人","西村 陸","大谷 陽平","本田 悠真","松岡 悠人","飯田 啓太","吉田 海斗","白石 翼","黒田 隆成","長谷川 海斗","松本 凛","森本 優","斉藤 颯太","安藤 匠","高橋 拓真","山本 大輝","小林 蓮","田中 光","加藤 大和"],
    "ブラジル": ["マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ","ブルーノ","レアンドロ","ファビオ","ダニーロ","グスタボ","ガブリエル","レナン","ヴィトル","ラファエル","ジョルジ"],
    "スペイン": ["サンチェス","ロペス","マルティン","ミゲル","フェルナンド","フアン","カルロス","ダビド","ルイス","ペレス","パブロ","ロドリゴ","アルバロ","セルヒオ","イバン","マリオ","マヌエル","ラウル","ヘスス","ゴンサロ"],
    "フランス": ["ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク","ミカエル","ジュリアン","カミーユ","バスティアン","ロマン","アドリアン","ロイック","ガエル","ジョルダン","バンジャマン"],
    "イタリア": ["ファビオ","マルコ","アレッサンドロ","ロッシ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ","ルイジ","アントニオ","シモーネ","ジジ","パオロ","フランチェスコ","クラウディオ","ステファノ","クリスティアン","ニコラ"],
    "ドイツ": ["クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル","トビアス","フローリアン","クリストフ","ユリアン","モリッツ","フィリップ","アレクサンダー","シモン","フランク","オリバー"],
    "イングランド": ["トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ルーカス","ヘンリー","エドワード","ベンジャミン","ジョシュア","サミュエル","メイソン","ジョセフ","マシュー","リアム","アーチー"]
}
def get_unique_name_by_nationality(nationality, used_names):
    pool = name_pools.get(nationality, [])
    for name in pool:
        if name not in used_names:
            return name
    # 枯渇時は苗字＋・＋名前のランダム生成
    fams = family_names_dict.get(nationality, ["名無し"])
    firsts = first_names_dict.get(nationality, ["太郎"])
    while True:
        name = f"{random.choice(fams)}・{random.choice(firsts)}"
        if name not in used_names:
            return name
    return f"{nationality}ネーム{len(used_names)%1000}"

# --- セッション初期化 ---
if "current_round" not in st.session_state:
    st.session_state.current_round = 1
if "league_table" not in st.session_state:
    st.session_state.league_table = {t: {"勝ち点":0,"勝":0,"分":0,"敗":0,"得点":0,"失点":0} for t in ALL_TEAMS}
if "season_history" not in st.session_state:
    st.session_state.season_history = []
if "scout_list" not in st.session_state:
    st.session_state.scout_list = []
if "scout_button_disabled" not in st.session_state:
    st.session_state.scout_button_disabled = [False]*5
if "match_log" not in st.session_state:
    st.session_state.match_log = []
if "money" not in st.session_state:
    st.session_state.money = 30000
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
                "名前": name,
                "ポジション": random.choice(["GK","DF","MF","FW"]),
                "年齢": random.randint(19,32),
                "国籍": nationality,
                "スピード": random.randint(55,85),
                "パス": random.randint(55,85),
                "フィジカル": random.randint(55,85),
                "スタミナ": random.randint(55,85),
                "ディフェンス": random.randint(55,85),
                "テクニック": random.randint(55,85),
                "メンタル": random.randint(55,85),
                "シュート": random.randint(55,85),
                "パワー": random.randint(55,85),
                "所属クラブ": t,
                "AIタイプ": ai_type,
                "出場数": 0,
                "得点": 0
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

# --- プレイヤーチーム読込 ---
df = pd.read_csv("players.csv")
df["所属クラブ"] = PLAYER_TEAM
if "出場数" not in df.columns: df["出場数"] = 0
if "得点" not in df.columns: df["得点"] = 0

# --- タブ構成 ---
tab1, tab2, tab3 = st.tabs(["自クラブ選手", "AIクラブ情報", "スカウト/補強"])

# --- 1.自クラブ選手（ユース/トップ切替＆詳細・レーダー）---
with tab1:
    player_subtab = st.radio("表示切替", ["シニアメンバー", "ユースメンバー"], horizontal=True)
    youth_df = df[df["年齢"] < 19]
    senior_df = df[df["年齢"] >= 19]
    display_df = senior_df if player_subtab == "シニアメンバー" else youth_df
    st.dataframe(display_df[["名前","ポジション","年齢","国籍","出場数","得点"]], use_container_width=True)
    selected_player = st.selectbox("選手名", display_df["名前"])
    player_row = display_df[display_df["名前"]==selected_player].iloc[0]
    st.write(player_row)
    stats = [float(player_row[l]) for l in labels]
    stats += stats[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels) + 1)
    fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, linewidth=2)
    ax.fill(angles, stats, alpha=0.3)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    st.pyplot(fig)

# --- 2.AIクラブ情報 ---
with tab2:
    ai_club = st.selectbox("AIクラブを選択", AI_TEAMS)
    club_players = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==ai_club]
    st.dataframe(club_players[["名前","ポジション","年齢","国籍","出場数","得点"]], use_container_width=True)
    ai_selected = st.selectbox("AI選手名", club_players["名前"])
    ai_row = club_players[club_players["名前"]==ai_selected].iloc[0]
    st.write(ai_row)
    stats = [float(ai_row[l]) for l in labels]
    stats += stats[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels) + 1)
    fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, linewidth=2)
    ax.fill(angles, stats, alpha=0.3)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    st.pyplot(fig)

# --- 3.スカウト/補強（資金表示・かぶり無し・1度だけ） ---
with tab3:
    st.info(f"クラブ資金：{st.session_state.money}万円")
    if st.button("スカウトリストを更新"):
        existing_names = set(df["名前"].tolist())
        existing_names.update(st.session_state.ai_players["名前"].tolist())
        st.session_state.scout_list = []
        st.session_state.scout_button_disabled = []
        for _ in range(5):
            nationality = random.choice(list(name_pools.keys()))
            name = get_unique_name_by_nationality(nationality, existing_names)
            existing_names.add(name)
            player = {
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(18, 22),
                "国籍": nationality,
                "スピード": random.randint(55, 80),
                "パス": random.randint(55, 80),
                "フィジカル": random.randint(55, 80),
                "スタミナ": random.randint(55, 80),
                "ディフェンス": random.randint(55, 80),
                "テクニック": random.randint(55, 80),
                "メンタル": random.randint(55, 80),
                "シュート": random.randint(55, 80),
                "パワー": random.randint(55, 80),
                "所属クラブ": PLAYER_TEAM,
                "出場数": 0,
                "得点": 0
            }
            st.session_state.scout_list.append(player)
            st.session_state.scout_button_disabled.append(False)
    for idx, player in enumerate(st.session_state.scout_list):
        with st.expander(f"{player['名前']}（{player['ポジション']}／{player['国籍']}）"):
            st.write(player)
            if st.session_state.scout_button_disabled[idx]:
                st.button(f"この選手を獲得", key=f"scout_{idx}", disabled=True)
            else:
                if st.button(f"この選手を獲得", key=f"scout_{idx}"):
                    df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                    df.to_csv("players.csv", index=False)
                    st.session_state.money -= 2000
                    st.session_state.scout_button_disabled[idx] = True
                    st.success(f"{player['名前']}をクラブに追加しました！（-2000万円）")

# --- 順位表 ---
def show_league_table():
    table = []
    for t in ALL_TEAMS:
        d = st.session_state.league_table[t]
        得失点 = d["得点"] - d["失点"]
        table.append([t, d["勝ち点"], d["勝"], d["分"], d["敗"], d["得点"], d["失点"], 得失点])
    df_league = pd.DataFrame(table, columns=["クラブ","勝ち点","勝","分","敗","得点","失点","得失点"])
    df_league = df_league.sort_values(["勝ち点","得失点","得点"], ascending=False).reset_index(drop=True)
    st.dataframe(df_league)
st.subheader("順位表（勝ち点制）")
show_league_table()

# --- スタメン選択 ---
st.subheader("スタメン11人選択")
selected_starters = st.multiselect("スタメンにしたい選手（11人まで）", df["名前"].tolist(), default=df["名前"].tolist()[:11])
if len(selected_starters) > 11:
    st.error("スタメンは11人までです！")
starters_df = df[df["名前"].isin(selected_starters)].copy()

# --- 試合シミュレーション ---
st.header(f"現在 {st.session_state.current_round} 節")
tactics = st.selectbox("チーム戦術", ["攻撃的", "バランス", "守備的"])
if st.button("試合開始！"):
    next_ai = AI_TEAMS[(st.session_state.current_round-1)%len(AI_TEAMS)]
    opp_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==next_ai]
    opp_type = opp_df["AIタイプ"].mode().iat[0] if not opp_df.empty else "バランス型"
    team_strength = starters_df[labels].mean().mean()
    if tactics == "攻撃的":
        team_strength *= 1.1
    elif tactics == "守備的":
        team_strength *= 0.9
    opponent_strength = opp_df[labels].mean().mean()
    if opp_type == "攻撃型":
        opponent_strength *= 1.08
    elif opp_type == "守備型":
        opponent_strength *= 0.95
    my_goals = max(0, int(random.gauss((team_strength-60)/8, 0.8)))
    op_goals = max(0, int(random.gauss((opponent_strength-60)/8, 0.8)))
    # 得点者
    my_scorers = random.choices(starters_df["名前"].tolist(), k=my_goals) if my_goals > 0 else []
    op_scorers = random.choices(opp_df["名前"].tolist(), k=op_goals) if op_goals > 0 else []
    # 個人成績
    for n in my_scorers:
        df.loc[df["名前"]==n, "得点"] += 1
    for n in starters_df["名前"]:
        df.loc[df["名前"]==n, "出場数"] += 1
    df.to_csv("players.csv", index=False)
    # 勝ち点等を順位表に反映
    tab = st.session_state.league_table
    tab[PLAYER_TEAM]["得点"] += my_goals
    tab[PLAYER_TEAM]["失点"] += op_goals
    tab[next_ai]["得点"] += op_goals
    tab[next_ai]["失点"] += my_goals
    if my_goals > op_goals:
        tab[PLAYER_TEAM]["勝ち点"] += 3
        tab[PLAYER_TEAM]["勝"] += 1
        tab[next_ai]["敗"] += 1
    elif my_goals < op_goals:
        tab[next_ai]["勝ち点"] += 3
        tab[next_ai]["勝"] += 1
        tab[PLAYER_TEAM]["敗"] += 1
    else:
        tab[PLAYER_TEAM]["勝ち点"] += 1
        tab[next_ai]["勝ち点"] += 1
        tab[PLAYER_TEAM]["分"] += 1
        tab[next_ai]["分"] += 1
    logtext = f"{st.session_state.current_round}節 {PLAYER_TEAM} vs {next_ai}: {my_goals}-{op_goals} 得点者:{','.join(my_scorers) if my_scorers else 'なし'}"
    st.session_state.match_log.append(logtext)
    st.success(logtext)
    st.session_state.current_round += 1

# --- 試合ログ ---
if st.session_state.match_log:
    st.markdown("#### 試合ログ")
    for l in st.session_state.match_log[-10:]:
        st.text(l)

# --- シーズン終了・表彰 ---
def show_season_awards(df, league_table):
    tab = pd.DataFrame(league_table).T
    tab["得失点"] = tab["得点"] - tab["失点"]
    champion = tab.sort_values(["勝ち点","得失点","得点"], ascending=False).index[0]
    top_scorer_row = df.sort_values("得点", ascending=False).iloc[0]
    st.success(f"🏆 優勝: {champion}")
    st.info(f"⚽ 得点王: {top_scorer_row['名前']}（{int(top_scorer_row['得点'])}点）")
if st.button("シーズン終了／表彰"):
    show_season_awards(df, st.session_state.league_table)
    st.session_state.season_history.append(pd.DataFrame(st.session_state.league_table).T)
if st.session_state.season_history:
    st.markdown("#### 過去成績（年度推移）")
    for year, hist in enumerate(st.session_state.season_history, 1):
        st.write(f"{year}年")
        st.dataframe(hist)
    
