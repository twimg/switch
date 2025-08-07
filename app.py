import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import json
import os
from datetime import datetime
from dataclasses import dataclass
from types import SimpleNamespace
from typing import List

# =========================
# Streamlit ページ設定 & シード固定
# =========================
st.set_page_config(page_title="Club Strive", layout="wide")
random.seed(42)
np.random.seed(42)

# =========================
# テーマ切替 & アクセシビリティ
# =========================

# テーマ切替
theme = st.sidebar.radio("テーマ", ["Dark","Light"], index=0)
if theme=="Light":
    st.markdown("""
    <style>
    .stApp { background: #f0f0f0 !important; color: #202020 !important; }
    div[data-testid="stDataFrame"] table { background: #ffffff !important; color: #202020 !important; }
    </style>
    """, unsafe_allow_html=True)

# フォントサイズ調整
font_size = st.sidebar.slider("フォントサイズ", 12, 24, 14)
st.markdown(
    f"<style>body, .stApp, div, table, th, td {{ font-size: {font_size}px !important; }}</style>",
    unsafe_allow_html=True
)

# 色覚モード
cb_mode = st.sidebar.selectbox("色覚モード", ["標準","プロタノピア","デュタノピア","トリタノピア"], index=0)
if cb_mode=="プロタノピア":
    st.markdown("<style>html { filter: hue-rotate(90deg); }</style>", unsafe_allow_html=True)
elif cb_mode=="デュタノピア":
    st.markdown("<style>html { filter: hue-rotate(180deg); }</style>", unsafe_allow_html=True)
elif cb_mode=="トリタノピア":
    st.markdown("<style>html { filter: hue-rotate(270deg); }</style>", unsafe_allow_html=True)

# =========================
# 定数定義
# =========================
SEASON_WEEKS = 14
MY_DEFAULT_CLUB = "Signature Team"
ABILITY_KEYS = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']
ABILITY_JP = {
    'Spd':'スピード','Pas':'パス','Phy':'フィジカル','Sta':'スタミナ',
    'Def':'守備','Tec':'テクニック','Men':'メンタル','Sht':'シュート','Pow':'パワー'
}
POS_ORDER = ['GK','DF','MF','FW']
POS_ORDER_REV = list(reversed(POS_ORDER))

# =========================
# データモデル定義
# =========================
@dataclass
class Staff:
    name: str
    role: str
    salary: int
    morale: int

@dataclass
class Stadium:
    capacity: int
    level: int
    base_price: int

@dataclass
class Sponsor:
    name: str
    base_fee: int
    bonus_per_goal: int
    duration: int

@dataclass
class Debt:
    amount: int
    interest_rate: float
    term: int

@dataclass
class ContinentalTournament:
    name: str
    clubs: List[str]
    group_size: int
    groups: List[List[str]]
    results: List
    finished: bool

@dataclass
class WorldCup:
    name: str
    nations: List[str]
    groups: List[List[str]]
    results: List
    finished: bool

# =========================
# ユーティリティ関数
# =========================
def fmt_money(v:int) -> str:
    if v >= 1_000_000: return f"{v//1_000_000}m€"
    if v >=   1_000: return f"{v//1_000}k€"
    return f"{v}€"

def round_value(v:int) -> int:
    """スカウト評価額を切り捨て or 5の倍数に丸める"""
    if v >= 1000:
        return (v // 1000) * 1000
    return int(round(v / 5) * 5)

def sort_by_pos(df: pd.DataFrame, reverse: bool=False) -> pd.DataFrame:
    """Pos 列を GK→DF→MF→FW、または逆でソート。OVR 降順も併用。"""
    order = POS_ORDER_REV if reverse else POS_ORDER
    cat = pd.Categorical(df['Pos'], categories=order, ordered=True)
    return df.assign(_poscat=cat).sort_values(['_poscat','OVR'], ascending=[True,False]).drop(columns='_poscat')

def make_transparent(ax):
    ax.set_facecolor('none')
    ax.figure.patch.set_alpha(0)
    ax.grid(color="#fff", alpha=0.15)

def radar_chart(vals, labels):
    """レーダーチャート描画"""
    ang = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    fig = plt.figure(figsize=(3,3))
    ax  = fig.add_subplot(111, polar=True)
    ax.plot(np.concatenate([ang, [ang[0]]]), np.concatenate([vals, [vals[0]]]), linewidth=2)
    ax.fill(np.concatenate([ang, [ang[0]]]), np.concatenate([vals, [vals[0]]]), alpha=0.25)
    ax.set_xticks(ang)
    ax.set_xticklabels(labels, color="#eaf6ff", fontsize=9)
    ax.set_yticklabels([])
    make_transparent(ax)
    return fig

# =========================
# CSS & テーブルスタイル
# =========================
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }
.section-box h3{ font-size:1.45rem!important; }
.section-box h4{ font-size:1.15rem!important; }
.stTabs button{ color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"]{ border-bottom:2.5px solid #f7df70!important; }
.stButton>button{ background:#27e3b9!important; color:#202b41!important; border-radius:10px; }
button[kind="formSubmit"]{ background:#27e3b9!important; color:#202b41!important; border:2px solid #f7df70!important; }
div[data-testid="stDataFrame"] table{ background:rgba(32,44,70,0.78)!important; color:#eaf6ff!important; }
</style>
""", unsafe_allow_html=True)

# =========================
# セッション初期化
# =========================
def init_session():
    ses = SimpleNamespace()
    ses.week          = 1
    ses.my_club       = MY_DEFAULT_CLUB
    ses.budget        = 5_000_000
    ses.staff         = [Staff("マルコ・リッパ","Manager",800000,70),
                         Staff("佐藤コーチ","Coach",500000,65),
                         Staff("李スカウト","Scout",400000,60)]
    ses.stadium       = Stadium(10000,1,20)
    ses.sponsors      = []
    ses.debts         = []
    ses.finance_log   = []
    ses.sns_posts     = []
    ses.sns_times     = []
    ses.senior        = pd.DataFrame()
    ses.youth         = pd.DataFrame()
    ses.leagues       = {}
    ses.standings     = pd.DataFrame()
    ses.club_map      = {}
    ses.intl_tournament = {}
    ses.world_cup     = None
    ses.save_slots    = {}
    return ses

if "ses" not in st.session_state:
    st.session_state.ses = init_session()
ses = st.session_state.ses

# =========================
# 名前プール & 生成関数
# =========================
NAME_POOL = {
    'ENG': {'given': ["Oliver","Jack","Harry","George","Noah"], 'surname': ["Smith","Jones","Taylor","Brown","Davies"]},
    'GER': {'given': ["Lukas","Max","Leon","Paul","Jonas"],    'surname': ["Müller","Schmidt","Schneider","Fischer","Weber"]},
    # ... 他国 (FRA, ESP, ITA(2部), NED, BRA, POR, BEL, TUR, ARG, URU, COL, USA, MEX, SAU, NGA, MAR, KOR, AUS) を同様に定義 ...
}

used_names = set()

def make_name(nat):
    pool = NAME_POOL.get(nat, NAME_POOL['ENG'])
    while True:
        name = f"{random.choice(pool['given'])} {random.choice(pool['surname'])}"
        if name not in used_names:
            used_names.add(name)
            return name

def gen_players(n, youth=False):
    """選手データを n 人分生成（youth=True で若手）"""
    lst = []
    for _ in range(n):
        nat   = random.choice(list(NAME_POOL.keys()))
        name  = make_name(nat)
        stats = {k: random.randint(52 if youth else 60, 82 if youth else 90) for k in ABILITY_KEYS}
        ovr   = int(np.mean(list(stats.values())))
        age   = random.randint(15 if youth else 18, 18 if youth else 34)
        sal   = random.randint(30_000 if youth else 120_000, 250_000 if youth else 1_200_000)
        lst.append({
            "Name":        name,
            "Nat":         nat,
            "Pos":         random.choice(POS_ORDER),
            "Age":         age,
            **stats,
            "OVR":         ovr,
            "Salary":      sal,
            "Contract":    random.randint(1, 2 if youth else 3),
            "Matches":     0,
            "Fatigue":     0,
            "Injured":     False,
            "Youth":       youth,
            "Club":        None,
            "PlayStyle":   random.sample(["職人","タックルマスター","ムードメーカー","影の支配者"], 2),
            "GrowthType":  random.choice(["早熟","晩成","爆発"])
        })
    return pd.DataFrame(lst)
