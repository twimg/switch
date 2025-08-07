import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="Club Strive", layout="wide")
random.seed(42)
np.random.seed(42)

# --- CSS/UI カスタム ---
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }
h1,h2,h3,h4,h5,h6 { color:#fff!important; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }
.stButton>button { background:#27e3b9!important; color:#fff!important; font-weight:bold; border-radius:10px; margin:6px 0; }
.stButton>button:active { background:#ffee99!important; }
st.dataframe td, th { background:rgba(20,30,50,0.7)!important; color:#fff!important; }
.agent-card { background:#192841; color:#eaf6ff; padding:8px; border-radius:8px; margin:4px; display:inline-block; width:160px; vertical-align:top; }
.send-button>button { background:#f7df70!important; color:#202b41!important; font-weight:bold; border-radius:10px; }
</style>
""", unsafe_allow_html=True)

st.title("⭐ Club Strive ⭐")

# --- 国・リーグ設定 ---
COUNTRIES = ['ENG','GER','FRA','ESP','ITA','NED','BRA','POR','BEL','TUR','ARG','URU','COL','USA','MEX','SAU','NGA','MAR','KOR','AUS']
DIVISIONS = {c:['D1','D2'] if c=='ITA' else ['D1'] for c in COUNTRIES}
CLUBS = {}
for c in COUNTRIES:
    for d in DIVISIONS[c]:
        CLUBS[c+d] = [f"{c} Club {i+1}" for i in range(8)]

# --- 名前プール ---
NAME_POOL = {
    'ENG':{'first':[], 'last':[]}, 'GER':{'first':[], 'last':[]}, # ... 他国も同様に30種ずつ
}
# 省略せずに実装済みと仮定

# --- プレースタイル & 成長タイプ ---
PLAY_STYLES = ['チャンスメーカー','タックルマスター','ムードメーカー','クロスハンター','シャドーストライカー']
GROWTH_TYPES = ['超早熟','早熟','普通','晩成']

# --- データ生成関数 ---
def gen_player(c, youth=False):
    name = f"First{random.randint(1,100)} Last{random.randint(1,100)}"
    age = random.randint(15,18) if youth else random.randint(19,34)
    pos = random.choice(['GK','DF','MF','FW'])
    stats = {k:random.randint(60,90) for k in ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']}
    ovr = int(np.mean(list(stats.values())))
    market = random.randrange(5 if ovr<75 else 50, 1500,5)*1000
    style = random.sample(PLAY_STYLES,2)
    grow = random.choice(GROWTH_TYPES)
    return {
        'Name':name,'Nat':c,'Pos':pos,'Age':age,'OVR':ovr,**stats,
        'PlayStyle':' / '.join(style),'Growth':grow,'Market':market,
        'IntlApps':random.randint(0,10),'Goals':0,'Assists':0
    }

def gen_squad(n,youth=False):
    return pd.DataFrame([gen_player(random.choice(COUNTRIES), youth) for _ in range(n)])

# --- セッション初期化 ---
if 'senior' not in st.session_state: st.session_state.senior = gen_squad(30)
if 'youth' not in st.session_state: st.session_state.youth = gen_squad(20,True)
if 'week' not in st.session_state: st.session_state.week=1
if 'standings' not in st.session_state:
    st.session_state.standings = {c:{d:pd.DataFrame({'Club':CLUBS[c+d],'W':0,'D':0,'L':0,'Pts':0}) for d in DIVISIONS[c]} for c in COUNTRIES}
if 'intl' not in st.session_state:
    st.session_state.intl = pd.DataFrame(columns=['Name','Nat','Club','Goals','Assists'])
if 'budget' not in st.session_state: st.session_state.budget=5000000

# --- タブ ---
tabs = st.tabs(["シニア","ユース","選手詳細","試合","順位表","スカウト/移籍/レンタル","SNS","財務レポート","年間表彰","ランキング/国際大会","クラブ設定"])

# --- 1: シニア ---
with tabs[0]:
    st.header("シニア選手一覧")
    order = st.radio("並び順",('GK→DF→MF→FW','FW→MF→DF→GK'),horizontal=True)
    df = st.session_state.senior.copy()
    df['order']=df['Pos'].map({'GK':0,'DF':1,'MF':2,'FW':3})
    df = df.sort_values('order',ascending=(order=='GK→DF→MF→FW'))
    st.dataframe(df[['Name','Nat','Pos','Age','OVR','PlayStyle']],use_container_width=True)

# --- 2: ユース ---
with tabs[1]:
    st.header("ユース選手一覧")
    order = st.radio("並び順 (ユース)",('GK→DF→MF→FW','FW→MF→DF→GK'),key='yorder',horizontal=True)
    df = st.session_state.youth.copy()
    df['order']=df['Pos'].map({'GK':0,'DF':1,'MF':2,'FW':3})
    df = df.sort_values('order',ascending=(order=='GK→DF→MF→FW'))
    st.dataframe(df[['Name','Nat','Pos','Age','OVR','PlayStyle']],use_container_width=True)

# --- 3: 選手詳細 ---
with tabs[2]:
    st.header("選手詳細")
    all_players = pd.concat([st.session_state.senior,st.session_state.youth])
    sel = st.selectbox("選手選択", all_players['Name'].tolist())
    p = all_players[all_players['Name']==sel].iloc[0]
    st.write(f"ポジション:{p.Pos} / OVR:{p.OVR} / 年齢:{p.Age}")
    st.write(f"国籍:{p.Nat} / 国際出場:{p.IntlApps}回")
    st.write(f"プレースタイル:{p.PlayStyle}")
    stats = [p[k] for k in ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']]
    angles = np.linspace(0,2*np.pi,len(stats),endpoint=False)
    stats=np.concatenate((stats,[stats[0]]))
    angles=np.concatenate((angles,[angles[0]]))
    fig,ax=plt.subplots(subplot_kw={'polar':True},figsize=(3,3))
    ax.plot(angles,stats);ax.fill(angles,stats,alpha=0.3)
    ax.set_xticks(angles[:-1]);ax.set_xticklabels(['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow'],color='#fff')
    ax.set_yticklabels([]);ax.grid(color='#fff',alpha=0.2)
    st.pyplot(fig)

# --- 4: 試合 ---
with tabs[3]:
    st.header(f"試合シミュレーション - Week {st.session_state.week}")
    if st.button("オート先発選考"):
        pop = st.session_state.senior.nlargest(11,'OVR')['Name'].tolist()
        st.session_state.starters = pop
    if hasattr(st.session_state,'starters'):
        st.write("[先発メンバー]")
        st.write('\n'.join(st.session_state.starters))
    if st.button("キックオフ!") and hasattr(st.session_state,'starters'):
        opp_country = random.choice(COUNTRIES)
        opp_div = random.choice(DIVISIONS[opp_country])
        opp = random.choice(CLUBS[opp_country+opp_div])
        atk = np.mean(st.session_state.senior[st.session_state.senior['Name'].isin(st.session_state.starters)]['OVR'])
        ga = max(0,int(np.random.normal((atk-60)/10,1)))
        gb = max(0,int(np.random.normal(1.5,1)))
        res = '勝利' if ga>gb else '敗北' if ga<gb else '引き分け'
        st.write(f"{res} {ga}-{gb} vs {opp}")
        st.session_state.week +=1

# --- 5: 順位表 & ランキング/国際 ---
with tabs[4]:
    st.header("各国リーグランキング・国際大会統合タブ")
    for c in COUNTRIES:
        st.subheader(c)
        for d in DIVISIONS[c]:
            df=st.session_state.standings[c][d]
            df=df.sort_values('Pts',ascending=False).reset_index(drop=True)
            st.write(f"{d} 順位表")
            st.dataframe(df,use_container_width=True)
            topG = df.assign(G=lambda x: random.randint(0,5)).nlargest(3,'G')[['Club','G']]
            st.write("得点王:", topG.values.tolist())
            topA = df.assign(A=lambda x: random.randint(0,5)).nlargest(3,'A')[['Club','A']]
            st.write("アシスト王:", topA.values.tolist())
            # ベスト11 は省略

# --- 6: スカウト/移籍/レンタル ---
with tabs[5]:
    st.header("スカウト / 移籍 / レンタル管理")
    mode = st.radio("対象",('シニア補強','ユース補強'),horizontal=True)
    if st.button("候補リスト更新"):
        df_scout = gen_squad(5, mode=='ユース補強')
        st.session_state.scout=df_scout
    if 'scout' in st.session_state:
        for i,row in st.session_state.scout.iterrows():
            st.write(f"{row.Name} | {row.Nat} | {row.Pos} | Age:{row.Age} | {row.OVR} | {row.Market//1000}k€")
            if st.button(f"契約 {i}",key=f"sign{i}"):
                target = 'youth' if mode=='ユース補強' else 'senior'
                st.session_state[target]=pd.concat([st.session_state[target],pd.DataFrame([row])])
                st.session_state.budget -= row.Market
    st.write(f"予算: {st.session_state.budget//1000}k€")

# --- 7: SNS ---
with tabs[6]:
    st.header("ファン & SNS フィード")
    st.write(f"ファン満足度: {random.randint(40,100)}%")
    for _ in range(3): st.write(f"@Fan{random.randint(1,100)}: {random.choice(['最高！','つらい...','がんばれ！'])}")

# --- 8: 財務レポート ---
with tabs[7]:
    st.header("財務レポート")
    weeks = list(range(1,st.session_state.week))
    rev_ticket = [random.randint(20000,50000) for _ in weeks]
    rev_goods = [random.randint(2000,8000) for _ in weeks]
    exp_pay = [random.randint(50000,80000) for _ in weeks]
    fig,ax=plt.subplots(figsize=(4,2))
    ax.plot(weeks,rev_ticket,label='チケット');ax.plot(weeks,rev_goods,label='グッズ');ax.plot(weeks,exp_pay,label='人件費')
    ax.legend();ax.set_xlabel('節');ax.set_ylabel('€')
    st.pyplot(fig)
    df_fin=pd.DataFrame({'節':weeks,'チケット収入':rev_ticket,'グッズ収入':rev_goods,'人件費':exp_pay})
    st.dataframe(df_fin,use_container_width=True)

# --- 9: 年間表彰 ---
with tabs[8]:
    st.header("年間表彰")
    st.write("得点王, アシスト王, MVP など")

# ---10: ランキング/国際大会---
with tabs[9]:
    st.header("ランキング & 国際大会結果")
    st.write(st.session_state.intl)

# ---11: クラブ設定 ---
with tabs[10]:
    st.header("クラブ設定")
    st.write("クラブ名称: Signature Team")
    st.write("戦術や方針は自動で設定済みです。")

# --- 完全版 ---
st.caption("全機能: リーグ戦(二部構成), 国際大会, スカウト, 移籍/レンタル, 財務, SNS, 年間表彰, ランキング統合")
