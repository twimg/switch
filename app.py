import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="サッカー運営ゲーム", layout="wide")

# データ読み込み
df = pd.read_csv("players.csv")

st.title("クラブ運営シミュレーション v6")

# セレクション
position = st.selectbox("ポジションを選択", ["全て"] + sorted(df["ポジション"].unique().tolist()))
if position != "全て":
    filtered_df = df[df["ポジション"] == position]
else:
    filtered_df = df

# 表示
st.dataframe(filtered_df.reset_index(drop=True))

# 選手能力レーダーチャート
st.subheader("選手能力チャート")
selected_player = st.selectbox("選手を選択", df["名前"])
player_row = df[df["名前"] == selected_player].iloc[0]

labels = ['スピード', 'パス', 'フィジカル', 'スタミナ', 'ディフェンス', 'テクニック', 'メンタル', 'シュート', 'パワー']
stats = [player_row[label] for label in labels]

angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
stats += stats[:1]
angles += angles[:1]

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
