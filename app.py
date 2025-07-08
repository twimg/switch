import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# --- ページ全体の背景色設定（紺色） ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0f1a2b;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- 初期セッション設定 ---
if "current_round" not in st.session_state:
    st.session_state.current_round = 1
if "scout_list" not in st.session_state:
    st.session_state.scout_list = []
if "budget" not in st.session_state:
    st.session_state.budget = 50000
if "team_points" not in st.session_state:
    st.session_state.team_points = {"ストライバーFC": 0}

# --- データ読み込み ---
df = pd.read_csv("players.csv")
df_senior = df[df["年齢"] >= 19].reset_index(drop=True)
df_youth = df[df["年齢"] < 19].reset_index(drop=True)

# --- タイトル表示 ---
st.title("\u30b5\u30c3\u30ab\u30fc\u904b\u55b6\u30b7\u30df\u30e5\u30ec\u30fc\u30b7\u30e7\u30f3 v8")

# --- 節数と予算表示 ---
st.markdown(f"### \ud604\uc7ac {st.session_state.current_round} \uc808  |  \ubc30\uc7a5\uc608\uc815\u91d1: {st.session_state.budget:,}万円")

# --- 表示切替 ---
menu = st.radio("表示切替", ("\u30b7\u30cb\u30a2", "\u30e6\u30fc\u30b9"), horizontal=True)
df_view = df_senior if menu == "\u30b7\u30cb\u30a2" else df_youth

# --- 選手一覧（簡易表示） ---
st.subheader("\u9078\u624b\u4e00\u89a7")
for idx, row in df_view.iterrows():
    with st.expander(f"{row['名前']}（{row['ポジション']} / {row['年齢']}歳 / {row['国籍']}）"):
        st.write(row.to_frame().T.drop(columns=["名前", "ポジション", "年齢", "国籍"]))

# --- 試合シミュレーション ---
st.subheader("\u8a66\u5408")
tactics = st.selectbox("\u30c1\u30fc\u30e0\u6226\u8853", ["攻撃的", "バランス", "守備的"])
if st.button("\u8a66\u5408\u958b\u59cb！"):
    my_strength = df_senior[["スピード", "パス", "フィジカル", "スタミナ", "ディフェンス", "テクニック", "メンタル", "シュート", "パワー"]].mean().mean()
    if tactics == "攻撃的": my_strength *= 1.1
    elif tactics == "守備的": my_strength *= 0.9
    
    enemy_strength = random.uniform(65, 80)
    my_goals = max(0, int(random.gauss((my_strength-60)/8, 1.2)))
    op_goals = max(0, int(random.gauss((enemy_strength-60)/8, 1.2)))

    # 結果と勝ち点
    if my_goals > op_goals:
        result = "勝利"
        st.session_state.team_points["ストライバーFC"] += 3
    elif my_goals < op_goals:
        result = "敗北"
    else:
        result = "引き分け"
        st.session_state.team_points["ストライバーFC"] += 1

    st.success(f"【{result}】 {my_goals} - {op_goals}")
    st.session_state.current_round += 1

# --- 順位表（仮） ---
st.subheader("順位表（自クラブのみ表示）")
st.table(pd.DataFrame.from_dict(st.session_state.team_points, orient='index', columns=['勝ち点']).sort_values("勝ち点", ascending=False))

# --- スカウト ---
st.subheader("スカウト")
st.markdown(f"現在の予算：**{st.session_state.budget:,}万円**")

# --- スカウト候補更新 ---
if st.button("スカウトリストを更新"):
    name_pool = ["マルコ", "アンドレ", "ロベルト", "リカルド", "トマス", "ルーカス", "ファビオ", "サンチェス", "ニコ", "アントン"]
    used_names = set(df["名前"].tolist())
    st.session_state.scout_list = []
    while len(st.session_state.scout_list) < 5:
        name = random.choice(name_pool) + random.choice(["・ガルシア", "・ロドリゲス", "・ペレス", "・カブレラ"])
        if name not in used_names:
            used_names.add(name)
            st.session_state.scout_list.append({
                "名前": name,
                "ポジション": random.choice(["GK", "DF", "MF", "FW"]),
                "年齢": random.randint(18, 22),
                "国籍": random.choice(["ブラジル", "スペイン", "フランス", "イタリア", "ドイツ"]),
                "スピード": random.randint(60, 80),
                "パス": random.randint(60, 80),
                "フィジカル": random.randint(60, 80),
                "スタミナ": random.randint(60, 80),
                "ディフェンス": random.randint(60, 80),
                "テクニック": random.randint(60, 80),
                "メンタル": random.randint(60, 80),
                "シュート": random.randint(60, 80),
                "パワー": random.randint(60, 80)
            })

# --- スカウト候補表示 ---
for idx, player in enumerate(st.session_state.scout_list):
    with st.expander(f"{player['名前']}（{player['ポジション']}／{player['国籍']}）"):
        st.write(player)
        key = f"scout_{idx}_clicked"
        if key not in st.session_state:
            st.session_state[key] = False
        if not st.session_state[key]:
            if st.button(f"この選手を獲得 ({player['名前']})", key=f"scout_{idx}"):
                df = pd.concat([df, pd.DataFrame([player])], ignore_index=True)
                df.to_csv("players.csv", index=False)
                st.session_state.budget -= 3000
                st.session_state[key] = True
                st.success(f"{player['名前']} をクラブに追加しました！")
