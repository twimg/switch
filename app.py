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
