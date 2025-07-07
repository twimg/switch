import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("テストレーダーチャート")

# 仮データ例（本番はdf = pd.read_csv("players.csv")でOK）
data = {
    '名前': ['木村 隼人'],
    'スピード': [70],
    'パス': [65],
    'フィジカル': [75],
    'スタミナ': [68],
    'ディフェンス': [67],
    'テクニック': [73],
    'メンタル': [64],
    'シュート': [60],
    'パワー': [72]
}
df = pd.DataFrame(data)

labels = ['スピード', 'パス', 'フィジカル', 'スタミナ', 'ディフェンス', 'テクニック', 'メンタル', 'シュート', 'パワー']
selected_player = st.selectbox("選手を選択", df["名前"])
player_row = df[df["名前"] == selected_player].iloc[0]

stats = [float(player_row[label]) for label in labels]
stats += stats[:1]  # 先頭値を最後に追加

angles = np.linspace(0, 2 * np.pi, len(labels) + 1)

fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
ax.plot(angles, stats, linewidth=2)
ax.fill(angles, stats, alpha=0.3)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)
st.pyplot(fig)

# --- 試合シミュレーション ---
st.subheader("試合シミュレーション")
tactics = st.selectbox("チーム戦術を選択", ["攻撃的", "バランス", "守備的"])
if st.button("試合開始！"):
    # 総合能力の平均でチーム戦力を計算
    team_strength = df[labels].mean().mean()
    if tactics == "攻撃的":
        team_strength *= 1.1
    elif tactics == "守備的":
        team_strength *= 0.9

    opponent_strength = random.uniform(65, 80)

    if team_strength > opponent_strength:
        result = "勝利！"
    elif team_strength < opponent_strength:
        result = "敗北"
    else:
        result = "引き分け"

    st.subheader(f"試合結果：{result}")
    st.text(f"自チーム戦力：{int(team_strength)}")
    st.text(f"相手チーム戦力：{int(opponent_strength)}")

import streamlit as st
import pandas as pd
import random

# --- 初期設定 ---
if "current_round" not in st.session_state:
    st.session_state.current_round = 1
if "scout_list" not in st.session_state:
    # 仮スカウト候補
    st.session_state.scout_list = [
        {"名前":"ルーカス・マルティン", "ポジション":"FW", "年齢":20, "国籍":"ブラジル", "スピード":77, "パス":66, "フィジカル":73, "スタミナ":72, "ディフェンス":51, "テクニック":71, "メンタル":70, "シュート":75, "パワー":79},
        {"名前":"ファビオ・ロッシ", "ポジション":"MF", "年齢":22, "国籍":"イタリア", "スピード":69, "パス":79, "フィジカル":68, "スタミナ":74, "ディフェンス":59, "テクニック":78, "メンタル":71, "シュート":64, "パワー":69},
        {"名前":"ジャン・ピエール", "ポジション":"DF", "年齢":19, "国籍":"フランス", "スピード":66, "パス":64, "フィジカル":75, "スタミナ":70, "ディフェンス":79, "テクニック":65, "メンタル":70, "シュート":54, "パワー":76},
    ]

df = pd.read_csv("players.csv")
st.title("サッカー運営シミュレーション v7")

# --- 現在節表示 ---
st.header(f"現在 {st.session_state.current_round} 節")

# --- ポジション変更 ---
st.subheader("選手ポジション変更")
selected_player = st.selectbox("選手を選ぶ", df["名前"])
current_pos = df.loc[df["名前"]==selected_player, "ポジション"].values[0]
new_pos = st.selectbox("新しいポジション", ["GK", "DF", "MF", "FW"], index=["GK", "DF", "MF", "FW"].index(current_pos))
if st.button("ポジション変更"):
    df.loc[df["名前"]==selected_player, "ポジション"] = new_pos
    st.success(f"{selected_player} のポジションを {new_pos} に変更しました！")
    df.to_csv("players.csv", index=False)

# --- 選手一覧 ---
st.subheader("選手一覧")
st.dataframe(df)

# --- 試合シミュレーション（スコア付き） ---
st.subheader("試合")
tactics = st.selectbox("チーム戦術", ["攻撃的", "バランス", "守備的"])
if st.button("試合開始！"):
    team_strength = df[['スピード','パス','フィジカル','スタミナ','ディフェンス','テクニック','メンタル','シュート','パワー']].mean().mean()
    if tactics == "攻撃的":
        team_strength *= 1.1
    elif tactics == "守備的":
        team_strength *= 0.9
    opponent_strength = random.uniform(65, 80)

    # スコア生成
    my_goals = max(0, int(random.gauss((team_strength-60)/8, 0.8)))
    op_goals = max(0, int(random.gauss((opponent_strength-60)/8, 0.8)))

    # 勝敗
    if my_goals > op_goals:
        result = "勝利！"
    elif my_goals < op_goals:
        result = "敗北"
    else:
        result = "引き分け"

    st.session_state.current_round += 1
    st.success(f"【{result}】 {my_goals} - {op_goals}")

# --- スカウト画面 ---
st.subheader("スカウト候補")
if st.button("スカウトリストを更新"):
    # 仮のランダム生成
    names = ["マテウス", "ペドロ", "サンチェス", "リカルド", "アンリ", "ピエール", "トーマス", "ニコ", "ダニエル", "レオン"]
    st.session_state.scout_list = [
        {
            "名前": random.choice(names),
            "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
            "年齢": random.randint(18, 22),
            "国籍": random.choice(["ブラジル","スペイン","フランス","イタリア","ドイツ"]),
            "スピード": random.randint(55, 80),
            "パス": random.randint(55, 80),
            "フィジカル": random.randint(55, 80),
            "スタミナ": random.randint(55, 80),
            "ディフェンス": random.randint(55, 80),
            "テクニック": random.randint(55, 80),
            "メンタル": random.randint(55, 80),
            "シュート": random.randint(55, 80),
            "パワー": random.randint(55, 80)
        } for _ in range(5)
    ]

# 表示と獲得
for idx, player in enumerate(st.session_state.scout_list):
    with st.expander(f"{player['名前']}（{player['ポジション']}／{player['国籍']}）"):
        st.write(player)
        if st.button(f"この選手を獲得", key=f"scout_{idx}"):
            # players.csvに追加
            df = df.append(player, ignore_index=True)
            df.to_csv("players.csv", index=False)
            st.success(f"{player['名前']}をクラブに追加しました！")
