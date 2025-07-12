import matplotlib
matplotlib.rc('font', family='IPAexGothic')
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# --- UI/ロゴ・デザイン・スマホ最適化 ---
TEAM_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/6/67/Soccer_ball_animated.svg"
st.markdown("""
    <style>
    html, body, .stApp { font-family: 'IPAexGothic','Meiryo',sans-serif; }
    .stApp { background: linear-gradient(120deg, #192841 0%, #24345b 100%) !important; color: #eaf6ff; }
    .stTabs [data-baseweb="tab"] { color: #fff !important; font-weight: bold !important; }
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
    .budget-box {
        background: linear-gradient(90deg, #b1f6ff 30%, #61b0ff 100%);
        color: #18191c !important; border-radius: 14px;
        font-size: 1.16em; font-weight: bold;
        padding: 8px 15px; margin: 9px 0 17px 0; display: inline-block;
        border:2px solid #46d7ff66; box-shadow: 0 0 7px #93eaff44;
    }
    /* ポジションセレクト用 - 強制白色文字 */
    .stSelectbox label, .stSelectbox div { color: #fff !important; }
    .stSelectbox span { color: #222 !important; }
    </style>
""", unsafe_allow_html=True)
st.image(TEAM_LOGO_URL, width=48)
st.title("Soccer Club Management Sim")

# --- サッカー“男性顔” DiceBearスタイル切り替え ---
def get_avatar_url(name, nationality):
    # 1. notionists-neutral/avataaars/micah/initials fallback
    seed = f"{nationality}_{name}"
    try:
        # notionists-neutral（男性多め・比較的リアル寄り）
        return f"https://api.dicebear.com/7.x/notionists-neutral/png?seed={seed}&radius=50"
    except:
        # 2. avataaars fallback
        return f"https://api.dicebear.com/7.x/avataaars/png?seed={seed}&radius=50&top=shortHairShortFlat"
    # 3. initials fallback
    return f"https://api.dicebear.com/7.x/initials/png?seed={seed}"

# --- 国籍別名前プールなどは省略 ---

# ---- 省略部分に前回の長い国名・ファーストネーム辞書・選手生成/AIクラブ/能力関連/df生成など一式そのまま入れて下さい ----
# ※ 前回のコードから「顔画像URLだけ上記get_avatar_url関数で生成」になるように修正

# ↓↓↓ ここから「Scoutタブ」だけの変更例
# --- Scout ---
with tabs[3]:
    st.subheader("Scout Candidates")
    st.markdown(f"<span class='budget-box'>予算: {format_money(st.session_state.budget)}</span>", unsafe_allow_html=True)
    if st.button("Refresh List"):
        used_names = set(df["名前"].tolist())
        st.session_state.scout_list = []
        for _ in range(5):
            nationality = random.choice(list(surname_pools.keys()))
            name = get_unique_name_by_nationality(nationality, used_names | set(p["名前"] for p in st.session_state.scout_list))
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
    cols = st.columns(1 if st.session_state.get("mobile",False) else 3)
    already = set(df["名前"].tolist())
    for idx, player in enumerate(st.session_state.scout_list):
        with cols[idx%len(cols)]:
            ovr = int(np.mean([player[l] for l in labels]))
            avatar_url = get_avatar_url(player["名前"], player["国籍"])
            st.markdown(
                f"<div class='player-card'><img src='{avatar_url}' width='48'><b>{player['名前']}</b> <span style='color:#2cabe8;'>(OVR:{ovr})</span><br>"
                f"{player['ポジション']} / {player['年齢']} / {player['国籍']}<br>"
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

# ---- 「Matchタブ」のポジション欄も
# 　st.selectbox(..., label_visibility="visible") を使い
# 　セレクトボックス用のlabel, div, spanなどの色指定CSSも上に記載済みです

# --- 以下、他タブ・詳細・ポジション割り当て等は前回最新版と同じでOK ---

# 最後のキャプション
st.caption("UI/全機能統合（顔はDiceBear notionists-neutral、予算・ポジション見やすさ強化、写真“？”激減版）")
