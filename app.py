import streamlit as st
import pandas as pd
import numpy as np
import random

# ====== 1. 国籍ごとの名前リスト ======
name_pools = {
    "日本": [
        "佐藤 翔","木村 隼人","西村 陸","大谷 陽平","本田 悠真","松岡 悠人","飯田 啓太","吉田 海斗","白石 翼","黒田 隆成",
        "長谷川 海斗","松本 凛","森本 優","斉藤 颯太","安藤 匠","高橋 拓真","山本 大輝","小林 蓮","田中 光","加藤 大和"
    ],
    "ブラジル": [
        "マテウス","パブロ","ルーカス","リカルド","アンドレ","ジョアン","エリック","ペドロ","マルコス","ジオバニ",
        "ブルーノ","レアンドロ","ファビオ","ダニーロ","グスタボ","ガブリエル","レナン","ヴィトル","ラファエル","ジョルジ"
    ],
    "スペイン": [
        "サンチェス","ロペス","マルティン","ミゲル","フェルナンド","フアン","カルロス","ダビド","ルイス","ペレス",
        "パブロ","ロドリゴ","アルバロ","セルヒオ","イバン","マリオ","マヌエル","ラウル","ヘスス","ゴンサロ"
    ],
    "フランス": [
        "ピエール","ジャン","トマ","アントワン","レオン","アンリ","ルカ","ダニエル","パスカル","マルク",
        "ミカエル","ジュリアン","カミーユ","バスティアン","ロマン","アドリアン","ロイック","ガエル","ジョルダン","バンジャマン"
    ],
    "イタリア": [
        "ファビオ","マルコ","アレッサンドロ","ロッシ","サルヴァトーレ","ダニエレ","トーマス","ロレンツォ","ミケーレ","エミリオ",
        "ルイジ","アントニオ","シモーネ","ジジ","パオロ","フランチェスコ","クラウディオ","ステファノ","クリスティアン","ニコラ"
    ],
    "ドイツ": [
        "クラウス","ティモ","ミヒャエル","ルーカス","マティアス","セバスティアン","ニコ","ラファエル","カミーロ","ダニエル",
        "トビアス","フローリアン","クリストフ","ユリアン","モリッツ","フィリップ","アレクサンダー","シモン","フランク","オリバー"
    ],
    "イングランド": [
        "トーマス","ジェームズ","ウィリアム","ハリー","ジョージ","ジャック","チャールズ","ダニエル","オリバー","ルーカス",
        "ヘンリー","エドワード","ベンジャミン","ジョシュア","サミュエル","メイソン","ジョセフ","マシュー","リアム","アーチー"
    ]
}

def get_unique_name_by_nationality(nationality, used_names):
    pool = name_pools.get(nationality, [])
    for name in pool:
        if name not in used_names:
            return name
    # 他国からでもOKにする（尽きたら）
    for other_pool in name_pools.values():
        for name in other_pool:
            if name not in used_names:
                return name
    return f"名無し{len(used_names)+1}"

# ====== 2. ゲーム状態初期化 ======
TEAM_NUM = 8
PLAYER_TEAM = "ストライバーFC"
AI_TEAMS = [f"CPUクラブ{i+1}" for i in range(TEAM_NUM-1)]
labels = ['スピード','パス','フィジカル','スタミナ','ディフェンス','テクニック','メンタル','シュート','パワー']

if "current_round" not in st.session_state:
    st.session_state.current_round = 1
if "scout_list" not in st.session_state:
    st.session_state.scout_list = []
if "scout_button_disabled" not in st.session_state:
    st.session_state.scout_button_disabled = [False]*5
if "ai_players" not in st.session_state:
    ai_players = []
    used_names = set()
    for t in AI_TEAMS:
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
                "所属クラブ": t
            })
    st.session_state.ai_players = pd.DataFrame(ai_players)

# ====== 3. プレイヤークラブの読込 ======
df = pd.read_csv("players.csv")
df["所属クラブ"] = PLAYER_TEAM

# ====== 4. 順位表 ======
st.title("サッカー運営シミュレーション 統合版")
st.subheader("順位表（平均戦力順）")
all_teams = [PLAYER_TEAM] + AI_TEAMS
team_stats = []
for t in all_teams:
    if t == PLAYER_TEAM:
        players = df
    else:
        players = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==t]
    strength = players[labels].mean().mean()
    team_stats.append({"クラブ":t,"平均戦力":int(strength)})
ranked = pd.DataFrame(team_stats).sort_values("平均戦力", ascending=False).reset_index(drop=True)
ranked.index += 1
st.dataframe(ranked)

# ====== 5. 現在節表示 ======
st.header(f"現在 {st.session_state.current_round} 節")

# ====== 6. 選手一覧・ポジション直接編集 ======
st.subheader("選手一覧（ポジション直接編集可）")
edit_df = df.copy()
edit_pos = []
for i, row in edit_df.iterrows():
    pos = st.selectbox(
        f"{row['名前']}のポジション",
        ["GK", "DF", "MF", "FW"],
        index=["GK", "DF", "MF", "FW"].index(row["ポジション"]),
        key=f"pos_{i}"
    )
    edit_pos.append(pos)
edit_df["ポジション"] = edit_pos

if st.button("ポジション編成を保存する"):
    df["ポジション"] = edit_df["ポジション"]
    df.to_csv("players.csv", index=False)
    st.success("新しいポジション配置で保存しました！")

st.dataframe(edit_df)

# ====== 7. レーダーチャート ======
st.subheader("選手能力レーダーチャート")
player_chart = st.selectbox("レーダーチャートを表示する選手", df["名前"], key="radar_select")
player_row = df[df["名前"] == player_chart].iloc[0]
stats = [float(player_row[label]) for label in labels]
stats += stats[:1]
angles = np.linspace(0, 2 * np.pi, len(labels) + 1)
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
ax.plot(angles, stats, linewidth=2)
ax.fill(angles, stats, alpha=0.3)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)
st.pyplot(fig)

# ====== 8. 試合シミュレーション ======
st.subheader("試合")
tactics = st.selectbox("チーム戦術", ["攻撃的", "バランス", "守備的"])
if st.button("試合開始！"):
    team_strength = df[labels].mean().mean()
    if tactics == "攻撃的":
        team_strength *= 1.1
    elif tactics == "守備的":
        team_strength *= 0.9
    # 対戦クラブ決定
    next_ai = AI_TEAMS[(st.session_state.current_round-1)%len(AI_TEAMS)]
    opp_df = st.session_state.ai_players[st.session_state.ai_players["所属クラブ"]==next_ai]
    opponent_strength = opp_df[labels].mean().mean()
    my_goals = max(0, int(random.gauss((team_strength-60)/8, 0.8)))
    op_goals = max(0, int(random.gauss((opponent_strength-60)/8, 0.8)))
    if my_goals > op_goals:
        result = "勝利！"
    elif my_goals < op_goals:
        result = "敗北"
    else:
        result = "引き分け"
    st.session_state.current_round += 1
    st.success(f"第{st.session_state.current_round-1}節 {PLAYER_TEAM} vs {next_ai}\n【{result}】 {my_goals} - {op_goals}")

# ====== 9. スカウト画面（連打防止・かぶりゼロ） ======
st.subheader("スカウト候補")
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
            "パワー": random.randint(55, 80)
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
                st.session_state.scout_button_disabled[idx] = True
                st.success(f"{player['名前']}をクラブに追加しました！")

# ====== 10. AIクラブ移籍イベント（かぶり無し） ======
st.subheader("移籍マーケット")
if st.button("AIクラブから選手獲得イベント（体験版）"):
    available = st.session_state.ai_players[~st.session_state.ai_players["名前"].isin(df["名前"])]
    if not available.empty:
        ai_row = available.sample(1).iloc[0]
        st.write(f"AIクラブ「{ai_row['所属クラブ']}」から{ai_row['名前']}({ai_row['ポジション']}, {ai_row['国籍']})の獲得オファー！")
        if st.button(f"{ai_row['名前']}を獲得する"):
            df = pd.concat([df, pd.DataFrame([ai_row])], ignore_index=True)
            df.to_csv("players.csv", index=False)
            st.success(f"{ai_row['名前']}をクラブに移籍獲得しました！")
    else:
        st.info("移籍可能なAI選手が残っていません。")
    
