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

# --- CSS/UIカスタム ---
st.markdown("""
<style>
body, .stApp { font-family:'IPAexGothic','Meiryo',sans-serif; }
.stApp { background:linear-gradient(120deg,#202c46 0%,#314265 100%)!important; color:#eaf6ff; }
.stTabs button { color:#fff!important; background:transparent!important; }
.stTabs [aria-selected="true"] { border-bottom:2.5px solid #f7df70!important; }
.stButton>button { background:#27e3b9!important; color:#202b41!important; font-weight:bold; border-radius:10px; margin:6px 0; }
.stButton>button:active { background:#ffee99!important; }
</style>
""", unsafe_allow_html=True)

st.title("Club Strive")

SEASON_WEEKS = 14

LEAGUES = {
    'イングランド': {'1部': ["Riverdale FC","Midtown United","Eastport Rovers","Kingsbridge Athletic","Westhaven City","Southvale Town","Northgate FC","Oakwood Albion"],
                 '2部': ["Lakemont FC","Greenfield United","Highview Rangers","Stonebridge Town","Redwood City","Bayview Athletic","Hillcrest FC","Harborport United"]},
    'スペイン':   {'1部': ["Costa Mar FC","Solaria United","Nueva Vista Rovers","Valencia Hills","Sevilla Coast Athletic","Barcelona Verde","Madrid Oeste City","Catalonia Albion"],
                 '2部': ["Andalusia Stars","Granada Echo FC","Cadiz Mariners","Ibiza Sun United","Mallorca Winds","Murcia Valley Athletic","Castilla Rovers","Toledo Town"]},
    'フランス':   {'1部': ["Paris Saintoise","Lyonnais Athletic","Marseille Bleu","Monaco Royal","Lille Nord FC","Rennes Rouge","Nice Côte Town","Nantes Loire United"],
                 '2部': ["Bordeaux Vine FC","Montpellier Horizon","Toulouse Aero Athletic","Reims Champagne","Strasbourg Forest","Brest Bretagne","Angers Loire","Metz Lorraine"]},
    'ドイツ':     {'1部': ["Bavaria Deutschland","Borussia Rhein","Leipzig Redbulls","Leverkusen Chemie","Schalke Ruhr","Wolfsburg VW United","Eintracht Hessen","Freiburg Blackforest"],
                 '2部': ["St Pauli Harbor","Hamburg Hanseatic","Karlsruhe Baden","Heidelberg Lions","Nuremberg Franconia","Darmstadt Lilies","Dusseldorf Fortuna","Stuttgart Swabia"]},
    'オランダ':   {'1部': ["Amsterdam Canal FC","Rotterdam Harbor","Eindhoven Philips United","Utrecht Dom Rovers","Groningen North Sea","PSV Eindhoven","AZ Alkmaar","Feyenoord Rijnstad"],
                 '2部': ["Sparta Rotterdam","NEC Nijmegen","Volendam Fishermen","Cambuur Leeeuw FC","Excelsior Maas United","Twente Tukkers","Willem II Tilburg","Roda Sunshine"]}
}
regions = list(LEAGUES.keys())
labels = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']

NAME_POOLS = { ... }   # ここは直前のコードそのまま（ENG, GER, ITA, ESP, FRA, BRA, NED）

PLAY_STYLE_POOL = [
    "チャンスメーカー","シャドーストライカー","タックルマスター","インナーラップSB","スイーパーリーダー",
    "セカンドストライカー","ディストラクター","バランサー","トリックスター","クロスハンター",
    "カウンターランナー","クラッチプレイヤー","ジョーカー","フリーキックスペシャリスト","メンタルリーダー",
    "空中戦の鬼","起点型GK","配給型CB","王様タイプ","スペ体質","ムードメーカー","影の支配者",
    "勝負師","頭脳派","職人","チーム至上主義","師弟型","感情型","爆発型","メディア映え型","俊足ドリブラー"
]
GROWTH_TYPES_POOL = [
    "超早熟型","早熟型","標準型","晩成型","超晩成型","スペ体質","安定型","一発屋型","伸び悩み型","終盤爆発型"
]

NATION_STYLE_MAP = { ... }  # 直前のコード同様
NATION_GROWTH_MAP = { ... } # 直前のコード同様

def pick_from_weighted_pool(nat, pool_map, all_pool):
    base = pool_map.get(nat, pool_map['OTHER']).copy()
    if len(base) < len(all_pool):
        base.extend([s for s in all_pool if s not in base])
    random.shuffle(base)
    return base

def gen_players(n, youth=False):
    lst = []
    for _ in range(n):
        nat = random.choice(list(NAME_POOLS.keys()))
        style_pool = pick_from_weighted_pool(nat, NATION_STYLE_MAP, PLAY_STYLE_POOL)
        growth_pool = pick_from_weighted_pool(nat, NATION_GROWTH_MAP, GROWTH_TYPES_POOL)
        play_styles = random.sample(style_pool, 2)
        growth_type = growth_pool.pop()
        first = random.choice(NAME_POOLS[nat]['given'])
        last = random.choice(NAME_POOLS[nat]['surname'])
        name = f"{first} {last}"
        stats = {l: random.randint(60 if not youth else 50, 90) for l in labels}
        ovr = int(np.mean(list(stats.values())))
        lst.append({
            'Name': name, 'Nat': nat, 'Pos': random.choice(['GK','DF','MF','FW']),
            **stats, 'OVR': ovr, 'PlayStyle': play_styles, 'GrowthType': growth_type,
            'Matches': 0, 'Goals': 0, 'Assists': 0, 'Age': random.randint(18,33) if not youth else random.randint(14,17)
        })
    return pd.DataFrame(lst)

# --- セッション初期化 ---
ses = st.session_state
if 'week' not in ses: ses.week = 1
if 'senior' not in ses: ses.senior = gen_players(30)
if 'youth' not in ses: ses.youth = gen_players(20, True)
if 'starters' not in ses: ses.starters = []
if 'standings' not in ses:
    ses.standings = {r:{d:pd.DataFrame({'Club':LEAGUES[r][d],'W':0,'D':0,'L':0,'GF':0,'GA':0,'Pts':0}) for d in LEAGUES[r]} for r in regions}
if 'player_history' not in ses: ses.player_history = {}
for key in ['match_log','sns_posts','sns_times','finance_log','season_summary','injury_info','suspension_info','intl_tournament']:
    if key not in ses: ses[key] = [] if key in ['match_log','sns_posts','sns_times','finance_log','season_summary'] else {}

# タブ定義（続く）
# --- タブ定義 ---
tabs = st.tabs([
    'シニア', 'ユース', '選手詳細', '試合', '順位表',
    'SNS', '国際大会', '財務レポート', '年間表彰', 'リーダーボード'
])

# 0) シニア
with tabs[0]:
    st.markdown('<div style="color:#fff; font-size:20px;">シニア選手一覧</div>', unsafe_allow_html=True)
    df0 = ses.senior[['Name','Nat','Pos','Age','OVR','PlayStyle','GrowthType']]
    st.dataframe(
        df0.style.set_properties(**{
            "background-color":"rgba(20,30,50,0.7)",
            "color":"white"
        }),
        use_container_width=True
    )

# 1) ユース
with tabs[1]:
    st.markdown('<div style="color:#fff; font-size:20px;">ユース選手一覧</div>', unsafe_allow_html=True)
    df1 = ses.youth[['Name','Nat','Pos','Age','OVR','PlayStyle','GrowthType']]
    st.dataframe(
        df1.style.set_properties(**{
            "background-color":"rgba(20,30,50,0.7)",
            "color":"white"
        }),
        use_container_width=True
    )

# 2) 選手詳細
with tabs[2]:
    sel = st.selectbox('選手選択', ses.senior['Name'].tolist())
    hist = pd.DataFrame(ses.player_history.get(sel, [{'week':0,'OVR': ses.senior[ses.senior.Name==sel]['OVR'].iloc[0]}]))
    fig, ax = plt.subplots()
    for l in labels:
        if l in hist.columns:
            ax.plot(hist['week'], hist[l], marker='o', label=l)
    ax.set_xlabel('節'); ax.set_ylabel('能力値'); ax.legend(bbox_to_anchor=(1,1))
    st.pyplot(fig)
    p = ses.senior[ses.senior.Name==sel].iloc[0]
    fig2, ax2 = plt.subplots()
    style_map = {'超早熟型':'-.','早熟型':'--','晩成型':':','超晩成型':'-.'}
    ax2.plot(hist['week'], hist['OVR'], marker='o', linestyle=style_map.get(p['GrowthType'],'-'))
    ax2.set_xlabel('節'); ax2.set_ylabel('総合値'); st.pyplot(fig2)
    st.write(f"スタイル: {p['PlayStyle']} | 成長: {p['GrowthType']}")

# 3) 試合
with tabs[3]:
    st.markdown(f"<div style='color:#fff; font-size:20px;'>第{ses.week}節 試合シミュレーション</div>", unsafe_allow_html=True)
    formation = st.selectbox("フォーメーション", ["4-4-2","4-3-3","3-5-2"])
    if st.button("オート先発選考"):
        df = ses.senior
        req = {"4-4-2":("FW",2,"MF",4,"DF",4,"GK",1),"4-3-3":("FW",3,"MF",3,"DF",4,"GK",1),"3-5-2":("FW",2,"MF",5,"DF",3,"GK",1)}[formation]
        starters = []
        for i in range(0,len(req),2):
            pos,count = req[i],req[i+1]
            starters += df[df['Pos']==pos].nlargest(count,'OVR')['Name'].tolist()
        ses.starters = starters
    if ses.starters:
        st.markdown('<span style="color:white; font-weight:bold;">【先発メンバー】</span>', unsafe_allow_html=True)
        starters_df = ses.senior[ses.senior['Name'].isin(ses.starters)][['Name','Pos','OVR','PlayStyle']]
        st.dataframe(
            starters_df.style.set_properties(**{
                "background-color":"rgba(20,30,50,0.7)",
                "color":"white"
            }),
            use_container_width=True
        )

    division = list(LEAGUES[regions[0]].keys())[0]
    opp = random.choice([c for c in LEAGUES[regions[0]][division] if c != LEAGUES[regions[0]][division][0]])
    if ses.week <= SEASON_WEEKS:
        if st.button('キックオフ'):
            events = []
            g1, g2 = random.randint(0,3), random.randint(0,3)
            for player in random.sample(ses.senior['Name'].tolist(),2):
                if random.random()<0.1:
                    events.append({'minute':random.randint(1,90),'text':f"{player} 🟡"})
            if random.random()<0.05:
                pl = random.choice(ses.senior['Name'].tolist()); wks = random.randint(1,3)
                ses.injury_info[pl] = {'start': ses.week, 'return': ses.week+wks}
                events.append({'minute': random.randint(1,90), 'text': f"{pl} 負傷離脱"})
            st.success(f"結果 {g1}-{g2}")
            st.markdown('---')
            for ev in events: st.write(f"{ev['minute']}’ {ev['text']}")
            post = f"{regions[0]} {g1}-{g2} {opp}"
            ses.sns_posts.append(post); ses.sns_times.append(datetime.now())
            ses.finance_log.append({'week':ses.week,'revenue_ticket':g1*10000,'revenue_goods':g2*5000,'expense_salary':int(ses.senior['OVR'].mean()*1000)})
            ses.week += 1
            if ses.week > SEASON_WEEKS:
                champion = ses.standings[regions[0]][division].nlargest(1,'Pts')['Club'].iloc[0]
                top_scorer = ses.senior.nlargest(1,'Goals')['Name'].iloc[0]
                ses.season_summary.append({'Champion':champion,'TopScorer':top_scorer})
                st.success("シーズン終了！")
    else:
        st.info("シーズンは終了しました。次シーズンを開始してください。")
        if st.button("次シーズン開始"):
            ses.week = 1
            ses.senior = gen_players(30)
            ses.youth = gen_players(20, True)
            ses.standings = {r:{d:pd.DataFrame({'Club':LEAGUES[r][d],'W':0,'D':0,'L':0,'GF':0,'GA':0,'Pts':0}) for d in LEAGUES[r]} for r in regions}
            ses.sns_posts.clear(); ses.sns_times.clear(); ses.finance_log.clear(); ses.intl_tournament.clear()
            st.success("新シーズンを開始しました！")

# 4) 順位表
with tabs[4]:
    region = st.selectbox('地域', regions)
    div = st.selectbox('部', list(LEAGUES[region].keys()))
    st.dataframe(
        ses.standings[region][div].style.set_properties(
            **{"background-color":"rgba(20,30,50,0.7)","color":"white"}
        ),
        use_container_width=True
    )

# 5) SNS
with tabs[5]:
    if ses.sns_posts:
        for t,p in zip(reversed(ses.sns_times), reversed(ses.sns_posts)):
            st.write(f"{t.strftime('%m/%d %H:%M')} - {p}")
    else:
        st.info('投稿なし')

# 6) 国際大会
with tabs[6]:
    if not ses.intl_tournament:
        parts = []
        for reg in regions:
            parts.extend(ses.standings[reg]['1部'].nlargest(2,'Pts')['Club'].tolist())
        random.shuffle(parts)
        ses.intl_tournament = {'clubs':parts,'results':[]}
    if st.button('次ラウンド進行'):
        clubs = ses.intl_tournament['clubs']; winners=[]
        for i in range(0,len(clubs),2):
            c1,c2=clubs[i],clubs[i+1]
            g1,g2=random.randint(0,4),random.randint(0,4)
            w = c1 if g1>g2 else c2
            ses.intl_tournament['results'].append((c1,g1,c2,g2,w)); winners.append(w)
        ses.intl_tournament['clubs'] = winners
    for idx,m in enumerate(ses.intl_tournament['results']):
        st.write(f"【R{idx+1}】 {m[0]} {m[1]}-{m[3]} {m[2]} → {m[4]}")
    if len(ses.intl_tournament['clubs'])==1:
        st.success(f"優勝: {ses.intl_tournament['clubs'][0]}")

# 7) 財務レポート
with tabs[7]:
    df_fin = pd.DataFrame(ses.finance_log)
    if not df_fin.empty:
        fig,ax=plt.subplots()
        ax.plot(df_fin['week'], df_fin['revenue_ticket']+df_fin['revenue_goods'], label='収入')
        ax.plot(df_fin['week'], df_fin['expense_salary'], label='支出')
        ax.legend(); st.pyplot(fig)
    else:
        st.info('財務データなし')

# 8) 年間表彰
with tabs[8]:
    st.markdown('<div style="color:white; font-size:20px;">年間表彰</div>', unsafe_allow_html=True)
    df_all = pd.concat([ses.senior, ses.youth], ignore_index=True)
    top5 = df_all.nlargest(5,'Goals')
    st.markdown('<span style="color:white; font-weight:bold;">🏅 得点王 TOP5</span>', unsafe_allow_html=True)
    st.table(top5[['Name','Goals']].rename(columns={'Name':'選手','Goals':'ゴール'}))
    best11 = df_all.nlargest(11,'OVR')
    st.markdown('<span style="color:white; font-weight:bold;">⚽️ ベストイレブン</span>', unsafe_allow_html=True)
    st.write(best11['Name'].tolist())

# 9) リーダーボード
with tabs[9]:
    st.markdown('<div style="color:white; font-size:20px;">リーダーボード</div>', unsafe_allow_html=True)
    df_all['AgeGroup'] = pd.cut(df_all['Age'] if 'Age' in df_all.columns else pd.Series([0]),
                                bins=[0,21,23,100], labels=['U21','U23','25+'])
    typ = st.selectbox('表示タイプ',['国籍別得点','国籍別平均OVR','世代別ゴール'])
    if typ=='国籍別得点':
        df_nat = df_all.groupby('Nat')['Goals'].sum().reset_index().sort_values('Goals',ascending=False)
        st.table(df_nat.rename(columns={'Nat':'国籍','Goals':'総ゴール'}))
    elif typ=='国籍別平均OVR':
        df_nat = df_all.groupby('Nat')['OVR'].mean().reset_index().sort_values('OVR',ascending=False)
        fig,ax=plt.subplots(); ax.bar(df_nat['Nat'],df_nat['OVR']); st.pyplot(fig)
    else:
        df_age = df_all.groupby('AgeGroup')['Goals'].sum().reset_index()
        fig,ax=plt.subplots(); ax.bar(df_age['AgeGroup'],df_age['Goals']); st.pyplot(fig)
