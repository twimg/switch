import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime
import pandas.api.types as ptypes

# ---------------- 基本設定 ----------------
MY_CLUB_DEFAULT = "Signature Team"
SEASON_WEEKS = 14
ABILITY_KEYS = ['Spd','Pas','Phy','Sta','Def','Tec','Men','Sht','Pow']

random.seed(42)
np.random.seed(42)

# Matplotlib 文字化け対策
plt.rcParams['font.family'] = ['IPAexGothic','Meiryo','Noto Sans CJK JP','DejaVu Sans']

# ページ設定 & CSS
st.set_page_config(page_title="Club Strive", layout="wide")
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

# ---------------- 表示用ユーティリティ ----------------
def sort_by_pos(df, reverse=False):
    order = ['GK','DF','MF','FW']
    if reverse:
        order = list(reversed(order))
    cat = ptypes.CategoricalDtype(order, ordered=True)
    return df.assign(_p=df['Pos'].astype(cat))\
             .sort_values(['_p','OVR'], ascending=[True,False])\
             .drop(columns='_p')

def make_highlighter(column, value):
    def _func(row):
        return ['background-color:#f7df70;color:#202b41;font-weight:bold' if row[column]==value else '' for _ in row]
    return _func

def style_playstyle(col):
    return ['background-color:#f7df70;color:#202b41;font-weight:bold' for _ in col]

# ---------------- リーグ構築（既存5地域＋追加12地域） ----------------
def build_leagues(my_club_name):
    base = {
        'イングランド': {
            '1部': [my_club_name,"Midtown United","Eastport Rovers","Kingsbridge Athletic",
                    "Westhaven City","Southvale Town","Northgate FC","Oakwood Albion"],
            '2部': ["Lakemont FC","Greenfield United","Highview Rangers","Stonebridge Town",
                    "Redwood City","Bayview Athletic","Hillcrest FC","Harborport United"]
        },
        'スペイン': {
            '1部': ["Costa Mar FC","Solaria United","Nueva Vista Rovers","Valencia Hills",
                    "Sevilla Coast Athletic","Barcelona Verde","Madrid Oeste City","Catalonia Albion"],
            '2部': ["Andalusia Stars","Granada Echo FC","Cadiz Mariners","Ibiza Sun United",
                    "Mallorca Winds","Murcia Valley Athletic","Castilla Rovers","Toledo Town"]
        },
        'フランス': {
            '1部': ["Paris Saintoise","Lyonnais Athletic","Marseille Bleu","Monaco Royal",
                    "Lille Nord FC","Rennes Rouge","Nice Côte Town","Nantes Loire United"],
            '2部': ["Bordeaux Vine FC","Montpellier Horizon","Toulouse Aero Athletic","Reims Champagne",
                    "Strasbourg Forest","Brest Bretagne","Angers Loire","Metz Lorraine"]
        },
        'ドイツ': {
            '1部': ["Bavaria Deutschland","Borussia Rhein","Leipzig Redbulls","Leverkusen Chemie",
                    "Schalke Ruhr","Wolfsburg VW United","Eintracht Hessen","Freiburg Blackforest"],
            '2部': ["St Pauli Harbor","Hamburg Hanseatic","Karlsruhe Baden","Heidelberg Lions",
                    "Nuremberg Franconia","Darmstadt Lilies","Dusseldorf Fortuna","Stuttgart Swabia"]
        },
        'オランダ': {
            '1部': ["Amsterdam Canal FC","Rotterdam Harbor","Eindhoven Philips United","Utrecht Dom Rovers",
                    "Groningen North Sea","PSV Eindhoven","AZ Alkmaar","Feyenoord Rijnstad"],
            '2部': ["Sparta Rotterdam","NEC Nijmegen","Volendam Fishermen","Cambuur Leeeuw FC",
                    "Excelsior Maas United","Twente Tukkers","Willem II Tilburg","Roda Sunshine"]
        }
    }

    extra = {
        'ポルトガル': {
            '1部': ["Lisboa Azul","Porto Ribeira","Braga Minho","Sportiva Aveiro",
                    "Coimbra Scholars","Faro Atlantico","Setubal Sado","Guimarães Castle"],
            '2部': ["Leiria Lions","Funchal Madeira","Viseu Douro","Evora Roman",
                    "Aveiro Coast","Barreiro Steel","Sintra Palace","Algarve Sun"]
        },
        'ベルギー': {
            '1部': ["Brussels Royale","Antwerp Diamonds","Brugge Canal","Gent Buffalos",
                    "Liege Ardennes","Charleroi Zebras","Genk Limburg","Mechelen Yellow"],
            '2部': ["Leuven Scholars","Kortrijk Courtrai","Mons Dragons","Oostende Coast",
                    "Westerlo Campine","Seraing Steel","Namur Citadel","Hasselt Jenever"]
        },
        'トルコ': {
            '1部': ["Istanbul Bosphorus","Ankara Anatolia","Izmir Ege","Trabzon BlackSea",
                    "Bursa Green","Adana Toros","Antalya Sun","Samsun Waves"],
            '2部': ["Gaziantep Pistachio","Eskisehir Rail","Konya Seljuk","Kayseri Mount",
                    "Mersin Citrus","Sivas Snow","Malatya Apricot","Rize Tea"]
        },
        'アルゼンチン': {
            '1部': ["Buenos Aires River","Boca La Boca","Rosario Centralis","Cordoba Talleres",
                    "La Plata Students","Mendoza Andes","Santa Fe Colon","San Juan Valle"],
            '2部': ["Tucuman Norte","Salta Gaucho","Mar del Plata Coast","Bahia Blanca Wind",
                    "Neuquen Patagonia","Parana Litoral","Chaco Forest","Corrientes Mate"]
        },
        'ウルグアイ': {
            '1部': ["Montevideo Nacionales","Peñarol Carboneros","Rivera Norte","Salto Naranjas",
                    "Paysandu Litoral","Maldonado Playa","Tacuarembo Gauchos","Colonia Real"],
            '2部': ["Las Piedras Cerro","Minas Lavalleja","Durazno Centro","Florida Prado",
                    "Rocha Oceano","Artigas Frontera","Treinta y Tres Este","Canelones Sur"]
        },
        'コロンビア': {
            '1部': ["Bogotá Andes","Medellín Paisa","Cali Azucareros","Barranquilla Caribe",
                    "Bucaramanga Oro","Pereira Matecaña","Manizales Nevado","Santa Marta Tayrona"],
            '2部': ["Cartagena Piratas","Cúcuta Frontera","Ibagué Musical","Neiva Huila",
                    "Tunja Boyaca","Villavicencio Llanos","Popayán Blanca","Sincelejo Sabanas"]
        },
        'アメリカ': {
            '1部': ["New York Empire","Los Angeles Stars","Chicago Wind","Houston Space",
                    "Miami Ocean","Seattle Sound","Boston Harbor","Dallas Longhorns"],
            '2部': ["San Diego Surf","Portland Forest","Atlanta Phoenix","Philadelphia Liberty",
                    "Denver Altitude","Orlando Sunshine","Charlotte Crown","Austin Tech"]
        },
        'メキシコ': {
            '1部': ["Ciudad de Mexico Azteca","Guadalajara Tapatios","Monterrey Regios","Puebla Angeles",
                    "Tijuana Frontera","León Esmeralda","Toluca Diablos","Santos Laguna"],
            '2部': ["Queretaro Gallo","Aguascalientes Hidro","Culiacan Dorados","Chihuahua Norte",
                    "Merida Yucatan","Durango Scorpions","Tampico Madero","Veracruz Tiburon"]
        },
        'サウジアラビア': {
            '1部': ["Riyadh Falcons","Jeddah RedSea","Dammam Oasis","Mecca Desert","Medina Dates",
                     "Taif Highland","Tabuk North","Abha Asir"],
            '2部': ["Hail Camel","Najran Green","Jizan Coast","Al Qassim Palm",
                    "Al Baha Valley","Yanbu Port","Arar Border","Sakakah Oasis"]
        },
        'ナイジェリア': {
            '1部': ["Lagos Eko","Abuja Capital","Port Harcourt Oilers","Kano Pillars",
                    "Enugu Coal","Kaduna Crocs","Benin City Bronze","Ibadan Oluyole"],
            '2部': ["Jos Plateau","Aba Elephants","Calabar Carnival","Maiduguri Saharan",
                    "Owerri Heartland","Warri Delta","Ilorin Harmony","Uyo Heritage"]
        },
        'モロッコ': {
            '1部': ["Casablanca Atlas","Rabat Royal","Marrakesh RedCity","Fes Medina",
                    "Tangier Strait","Agadir Souss","Oujda East","Tetouan Rif"],
            '2部': ["Meknes Zerhoun","Kenitra Gharb","Beni Mellal Atlas","Nador Rif",
                    "El Jadida Ocean","Safi Ceramic","Taza Middle","Ouarzazate Sahara"]
        },
        '韓国': {
            '1部': ["Seoul Capital","Busan Harbor","Incheon Waves","Daegu Apple",
                    "Ulsan Tigers","Gwangju Phoenix","Jeonju Motors","Suwon Fortress"],
            '2部': ["Daejeon Science","Pohang Steelers","Jeju Island","Gimcheon Army",
                    "Anyang Violets","Chungnam Dragons","Goyang City","Cheonan Blue"]
        },
        'オーストラリア': {
            '1部': ["Sydney Harbour","Melbourne Victory","Brisbane Roarers","Perth Glorywest",
                    "Adelaide Reds","Newcastle Hunter","Wellington Tasman","Gold Coast Suns"],
            '2部': ["Canberra Capital","Hobart Southern","Darwin TopEnd","Geelong Bay",
                    "Cairns Tropics","Townsville Coral","Sunshine Coast Wave","Launceston North"]
        }
    }

    base.update(extra)
    base['イングランド']['1部'][0] = my_club_name
    return base

# ---------------- 名前プール（各国 30名×30姓程度） ----------------
NAME_POOLS = {
    'ENG': {'given': ["Oliver","Jack","Harry","George","Noah","Charlie","Jacob","Thomas","Oscar","William",
                      "James","Henry","Leo","Joshua","Freddie","Archie","Logan","Alexander","Ethan","Mason",
                      "Finley","Lucas","Samuel","Joseph","Dylan","Matthew","Daniel","Benjamin","Max","Harvey"],
            'surname': ["Smith","Jones","Taylor","Brown","Wilson","Evans","Thomas","Roberts","Johnson","Lewis",
                        "Walker","White","Harris","Martin","Thompson","Robinson","Clark","Young","Allen","King",
                        "Wright","Scott","Adams","Baker","Hill","Green","Nelson","Mitchell","Perez","Campbell"]},
    'GER': {'given': ["Lukas","Maximilian","Finn","Leon","Felix","Elias","Paul","Jonas","Luis","Tim",
                      "Noah","Ben","Jan","Anton","Henry","David","Moritz","Nico","Samuel","Philipp",
                      "Emil","Jonathan","Mats","Lennard","Theo","Jannik","Fabian","Johannes","Tobias","Florian"],
            'surname': ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Bauer","Koch",
                        "Richter","Klein","Wolf","Neumann","Schwarz","Zimmermann","Schmitt","Krüger","Hofmann","Hartmann",
                        "Lange","Werner","Schubert","Krause","Meier","Lehmann","Köhler","Frank","Mayer","Brandt"]},
    'ITA': {'given': ["Lorenzo","Alessandro","Francesco","Mattia","Leonardo","Riccardo","Gabriele","Niccolò","Tommaso","Andrea",
                      "Marco","Matteo","Fabio","Emanuele","Valerio","Daniele","Federico","Simone","Alberto","Vincenzo",
                      "Stefano","Davide","Giovanni","Fabiano","Luca","Antonio","Paolo","Maurizio","Raffaele","Jonathan"],
            'surname': ["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino","Greco",
                        "Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi","Moretti","Barbieri",
                        "Fontana","Santoro","Mariani","Riva","Bianco","Ferrara","Bernardi","Caputo","Monti","Serra"]},
    'ESP': {'given': ["Hugo","Martín","Lucas","Mateo","Iker","Diego","Álvaro","Pablo","Adrián","Sergio",
                      "Joaquín","Ángel","David","Rubén","Martí","Óscar","Víctor","Miguel","Enzo","Álex",
                      "Bruno","Mario","Oliver","Juan","José","Raúl","Pedro","Nacho","Saúl","Isco"],
            'surname': ["García","Martínez","López","Sánchez","Pérez","González","Rodríguez","Fernández","Torres","Ramírez",
                        "Flores","Gómez","Ruiz","Hernández","Díaz","Morales","Muñoz","Alonso","Gutiérrez","Castro",
                        "Ortiz","Rubio","Marín","Serrano","Gil","Blanco","Molina","Romero","Navarro","Medina"]},
    'FRA': {'given': ["Lucas","Gabriel","Léo","Raphaël","Arthur","Louis","Hugo","Jules","Adam","Nathan",
                      "Ethan","Thomas","Clément","Théo","Mathis","Noah","Maxime","Paul","Alexis","Victor",
                      "Martin","Gabin","Quentin","Guillaume","Baptiste","Maxence","Romain","Antoine","Mathieu","Robin"],
            'surname': ["Martin","Bernard","Thomas","Petit","Robert","Richard","Durand","Dubois","Moreau","Laurent",
                        "Simon","Michel","Leroy","Rousseau","David","Bertrand","Morel","Girard","Bonnet","Dupont",
                        "Lambert","Fontaine","Roux","Vincent","Morin","Nicolas","Lefebvre","Mercier","Dupuis","Blanc"]},
    'BRA': {'given': ["Pedro","Lucas","Guilherme","Mateus","Gabriel","Rafael","Bruno","Thiago","Felipe","Diego",
                      "Vinícius","João","Carlos","Ricardo","Eduardo","Fernando","Rodrigo","Paulo","Leandro","André",
                      "Vitor","Marcelo","Roberto","Caio","Renato","Igor","Luan","Fábio","Jonas","Samuel"],
            'surname': ["Silva","Santos","Oliveira","Souza","Rodrigues","Ferreira","Alves","Pereira","Lima","Gomes",
                        "Martins","Araújo","Ribeiro","Cardoso","Rocha","Dias","Carvalho","Barbosa","Pinto","Fernandes",
                        "Costa","Moreira","Mendes","Camargo","Rezende","Moura","Medeiros","Freitas","Castro","Campos"]},
    'NED': {'given': ["Daan","Lars","Sem","Finn","Thijs","Mees","Senna","Luuk","Milan","Jens",
                      "Rick","Rens","Sven","Tijs","Joost","Noud","Stijn","Tygo","Mats","Niels",
                      "Jelle","Bram","Wout","Teun","Guus","Floris","Koen","Derk","Gerrit","Max"],
            'surname': ["de Jong","Janssen","de Vries","van Dijk","Bakker","Visser","Smit","Meijer","de Boer","Mulder",
                        "de Graaf","Brouwer","van der Meer","Kuiper","Bos","Vos","Peters","Hendriks","Jakobs","van Leeuwen",
                        "de Groot","van den Berg","Kramer","van Dam","Molenaar","Corsten","Bergman","Verhoeven","Dekker","Veldman"]},

    # ---- 追加国籍 ----
    'POR': {'given': ["João","Miguel","Tiago","Diogo","Pedro","Gonçalo","Rui","André","Bruno","Hugo",
                      "Ricardo","Fábio","Paulo","Luís","Nuno","Carlos","Rafael","Francisco","Eduardo","Daniel",
                      "Vítor","Marco","Sérgio","Alexandre","Manuel","Henrique","Duarte","Artur","Matias","Cristiano"],
            'surname': ["Silva","Santos","Ferreira","Pereira","Oliveira","Costa","Rodrigues","Martins","Jesus","Sousa",
                        "Fernandes","Gonçalves","Lopes","Marques","Almeida","Ribeiro","Carvalho","Teixeira","Moreira","Correia",
                        "Mendes","Nunes","Soares","Vieira","Monteiro","Cardoso","Figueiredo","Batista","Moraes","Castro"]},
    'BEL': {'given': ["Lucas","Noah","Arthur","Louis","Liam","Jules","Nathan","Thomas","Elias","Victor",
                      "Hugo","Mathis","Gabriel","Adam","Baptiste","Ethan","Axel","Tim","Benjamin","Noé",
                      "Dylan","Enzo","Maxime","Samuel","Simon","Matthias","Kilian","Antoine","Rayan","Ilyas"],
            'surname': ["Peeters","Janssens","Maes","Jacobs","Mertens","Dupont","Leroy","Declercq","Vermeulen","Willems",
                        "Claes","Goossens","De Smet","De Clercq","Lambert","Dubois","Dumont","Devos","Simon","De Backer",
                        "Collins","Masson","Michiels","De Wilde","Hubert","Coppens","De Cock","Bekaert","Vander Velde","De Vos"]},
    'TUR': {'given': ["Ahmet","Mehmet","Mustafa","Ali","Hüseyin","İbrahim","Osman","Yusuf","Emre","Burak",
                      "Mert","Can","Kerem","Oğuzhan","Umut","Serkan","Onur","Furkan","Kaan","Eren",
                      "Berk","Tolga","Batuhan","Salih","Barış","Volkan","Cenk","Recep","Cem","Halil"],
            'surname': ["Yılmaz","Kaya","Demir","Şahin","Çelik","Yıldız","Yıldırım","Öztürk","Aydın","Özdemir",
                        "Arslan","Doğan","Kılıç","Aslan","Çetin","Kara","Koç","Kurt","Şimşek","Polat",
                        "Önder","Güler","Sarı","Taş","Bozkurt","Bulut","Keskin","Akın","Bakır","Uçar"]},
    'ARG': {'given': ["Juan","Carlos","Luis","Jorge","Miguel","Alejandro","Sergio","Diego","Hernán","Pablo",
                      "Matías","Facundo","Nicolás","Agustín","Lucas","Franco","Gonzalo","Maximiliano","Ezequiel","Leandro",
                      "Bruno","Martín","Emiliano","Ramiro","Cristian","Rodrigo","Tomás","Federico","Ariel","Enzo"],
            'surname': ["González","Rodríguez","Gómez","Fernández","López","Martínez","Pérez","Sánchez","Romero","Díaz",
                        "Álvarez","Torres","Ruiz","Ramírez","Flores","Acosta","Benítez","Herrera","Molina","Castro",
                        "Ortiz","Suárez","Rojas","Silva","Méndez","Ferreyra","Domínguez","Morales","Peralta","Ibarra"]},
    'URU': {'given': ["Diego","Luis","Sebastián","Matías","Nicolás","Gonzalo","Maxi","Federico","Rodrigo","Santiago",
                      "Bruno","Agustín","Facundo","Gastón","Álvaro","Jonathan","Emiliano","Pablo","Jorge","Cristian",
                      "Franco","Kevin","Leandro","Ramiro","Enzo","Marcelo","Emanuel","Mauricio","Carlos","Ignacio"],
            'surname': ["Pereira","Fernández","González","Rodríguez","Silva","Martínez","López","Sosa","Díaz","Suárez",
                        "Torres","Álvarez","Castro","Núñez","Ramos","Vázquez","Méndez","Cabrera","Romero","Medina",
                        "Ortiz","Cruz","Acosta","Herrera","Arias","Perdomo","Bentancur","Forlán","Lugano","Arambarri"]},
    'COL': {'given': ["Juan","Carlos","Luis","Jhon","Andrés","Miguel","Santiago","Diego","Felipe","Camilo",
                      "David","Sebastián","Nicolás","Julián","Cristian","Kevin","Mateo","Anderson","Mauricio","Esteban",
                      "Brayan","Yeferson","Harold","Jhony","Fabio","Wilson","Rafael","Jeison","Daniel","Germán"],
            'surname': ["García","Martínez","Rodríguez","González","Hernández","López","Díaz","Pérez","Sánchez","Ramírez",
                        "Torres","Suárez","Gómez","Castro","Vargas","Moreno","Jiménez","Rojas","Reyes","Guerrero",
                        "Muñoz","Ortega","Rivera","Cortés","Valencia","Mendoza","Cárdenas","Cardona","Barrios","Salazar"]},
    'USA': {'given': ["Liam","Noah","William","James","Benjamin","Lucas","Henry","Alexander","Michael","Ethan",
                      "Daniel","Jacob","Logan","Jackson","Levi","Sebastian","Mateo","Jack","Owen","Theodore",
                      "Aiden","Samuel","Joseph","John","David","Wyatt","Matthew","Luke","Asher","Carter"],
            'surname': ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
                        "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
                        "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson"]},
    'MEX': {'given': ["José","Juan","Luis","Carlos","Jesús","Miguel","Francisco","Jorge","Antonio","Alejandro",
                      "Fernando","Ricardo","Eduardo","Roberto","Manuel","Enrique","Raúl","Andrés","Héctor","Pedro",
                      "Arturo","Víctor","Mario","Rafael","Alberto","Adrián","Sergio","Hugo","Diego","Mauricio"],
            'surname': ["Hernández","García","Martínez","López","González","Pérez","Rodríguez","Sánchez","Ramírez","Cruz",
                        "Flores","Gómez","Reyes","Morales","Jiménez","Torres","Díaz","Vázquez","Ruiz","Mendoza",
                        "Aguilar","Ortiz","Castillo","Chávez","Ramos","Herrera","Medina","Vargas","Juárez","Silva"]},
    'SAU': {'given': ["Abdullah","Mohammed","Fahad","Saud","Nasser","Faisal","Sultan","Omar","Turki","Yasser",
                      "Abdulaziz","Khalid","Majed","Youssef","Salman","Mansour","Hassan","Ibrahim","Talal","Riyadh",
                      "Bader","Osama","Jassim","Hamad","Saeed","Mahmoud","Khalifa","Ziyad","Muteb","Anas"],
            'surname': ["Al-Saud","Al-Harbi","Al-Qahtani","Al-Mutairi","Al-Otaibi","Al-Shammari","Al-Dosari","Al-Shehri","Al-Zahrani","Al-Ghamdi",
                        "Al-Harthy","Al-Subaie","Al-Anazi","Al-Rashid","Al-Juhani","Al-Bishi","Al-Shahrani","Al-Faraj","Al-Hazmi","Al-Mansour",
                        "Al-Salem","Al-Qaed","Al-Nasser","Al-Ahmad","Al-Suwailem","Al-Marri","Al-Ajmi","Al-Saif","Al-Saadi","Al-Omari"]},
    'NGA': {'given': ["Emeka","Chinedu","Ifeanyi","Oluwaseun","Tunde","Chukwuemeka","Ayodele","Obinna","Segun","Babatunde",
                      "Ahmed","Ibrahim","Mohammed","John","Samuel","Peter","Daniel","Kingsley","Patrick","Collins",
                      "Kelechi","Henry","Godwin","Paul","Sunday","Victor","Bright","Promise","Emmanuel","Junior"],
            'surname': ["Okafor","Ogunleye","Adewale","Okeke","Okonkwo","Olawale","Balogun","Eze","Ojo","Chukwu",
                        "Adegoke","Ogunbiyi","Nwankwo","Nwosu","Ibrahim","Abubakar","Usman","Musa","Yusuf","Aliyu",
                        "Lawal","Sadiq","Ogbu","Egwu","Oparah","Ekwueme","Onyeka","Akinola","Akintola","Odinaka"]},
    'MAR': {'given': ["Youssef","Achraf","Hakim","Oussama","Ayoub","Yassine","Anas","Walid","Reda","Soufiane",
                      "Ismail","Abderrahim","Hamza","Amine","Mehdi","Adil","Karim","Nabil","Said","Hicham",
                      "Driss","Zakaria","Ilyas","Tarik","Othmane","Khalid","Mounir","Anouar","Fouad","Noureddine"],
            'surname': ["El Idrissi","El Amrani","El Fassi","Bennani","El Bakkali","Ouahbi","Chakir","El Haddad","El Mansouri","El Khattabi",
                        "Brahim","Tazi","Lamrani","El Khatib","El Malki","Bouhaddi","Alaoui","Haddadi","Fassi","El Yousfi",
                        "Zerouali","Mouh","Ziani","Amrabat","Belkacem","Haddou","Ben Ali","El Ghrib","El Azzouzi","Bouazza"]},
    'KOR': {'given': ["Minjun","Seojun","Ha Jun","Ye Joon","Jiwon","Hyunwoo","Jisoo","Taeyang","Sungmin","Donghyun",
                      "Joonho","Jinhyuk","Yunho","Jongin","Kyungmin","Taemin","Jaehyun","Seungmin","Woojin","Chanwoo",
                      "Jaeho","Minseok","Hoseok","Hyunjin","Youngho","Inho","Sangmin","Jaejun","Hajoon","Seungwoo"],
            'surname': ["Kim","Lee","Park","Choi","Jung","Kang","Cho","Yoon","Jang","Lim",
                        "Han","Shin","Yoo","Ahn","Kwon","Hwang","Oh","Song","Jeon","Hong",
                        "Yang","Ko","Moon","Son","Bae","Baek","Nam","Sim","Ha","No"]},
    'AUS': {'given': ["Oliver","William","Jack","Noah","Thomas","James","Liam","Lucas","Henry","Ethan",
                      "Harrison","Alexander","Levi","Charlie","Mason","Samuel","Hunter","Archie","Archer","Isaac",
                      "Logan","Joshua","Hudson","Cooper","Xavier","Elijah","Austin","Kai","Sebastian","Nicholas"],
            'surname': ["Smith","Jones","Williams","Brown","Taylor","Wilson","Johnson","White","Martin","Anderson",
                        "Thompson","Nguyen","Harris","Lewis","Walker","Robinson","Young","King","Wright","Kelly",
                        "Scott","Hall","Green","Adams","Baker","Mitchell","Campbell","Roberts","Turner","Parker"]}
}

# ---------------- プレースタイル & 成長タイプ ----------------
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

ALL_NATIONS = list(NAME_POOLS.keys())

# ---------------- 国別特徴（追加国含む） ----------------
# bias: 能力キーに対する初期補正（±値の目安）
# styles/growth: その国で出やすいプレースタイル／成長タイプ（足りない分は全体プールで補完）
NATION_TRAITS = {
    # 既存（例として少しだけ差別化）
    'ENG': {'bias':{'Phy':2,'Men':2}, 'styles':["空中戦の鬼","メンタルリーダー","職人","チーム至上主義","勝負師"], 'growth':["標準型","安定型","晩成型","終盤爆発型"]},
    'GER': {'bias':{'Phy':3,'Sta':2,'Men':1}, 'styles':["配給型CB","タックルマスター","メンタルリーダー","頭脳派","職人"], 'growth':["標準型","晩成型","超晩成型","安定型"]},
    'FRA': {'bias':{'Tec':2,'Spd':2}, 'styles':["トリックスター","メディア映え型","チャンスメーカー","ジョーカー","俊足ドリブラー"], 'growth':["超早熟型","早熟型","標準型","一発屋型"]},
    'ESP': {'bias':{'Tec':3,'Pas':3}, 'styles':["チャンスメーカー","王様タイプ","トリックスター","フリーキックスペシャリスト","頭脳派"], 'growth':["早熟型","標準型","晩成型","終盤爆発型"]},
    'ITA': {'bias':{'Def':3,'Men':2}, 'styles':["スイーパーリーダー","タックルマスター","影の支配者","王様タイプ","職人"], 'growth':["標準型","晩成型","超晩成型","安定型"]},
    'NED': {'bias':{'Pas':2,'Tec':2}, 'styles':["バランサー","配給型CB","チャンスメーカー","クラッチプレイヤー","トリックスター"], 'growth':["標準型","早熟型","終盤爆発型","一発屋型"]},
    'BRA': {'bias':{'Tec':4,'Sht':2,'Spd':2}, 'styles':["トリックスター","チャンスメーカー","ジョーカー","俊足ドリブラー","メディア映え型"], 'growth':["超早熟型","早熟型","標準型","スペ体質"]},

    # 追加13カ国
    'POR': {'bias':{'Tec':3,'Pas':2}, 'styles':["チャンスメーカー","フリーキックスペシャリスト","職人","頭脳派","王様タイプ"], 'growth':["標準型","晩成型","安定型","終盤爆発型"]},
    'BEL': {'bias':{'Pas':2,'Men':1}, 'styles':["バランサー","メンタルリーダー","配給型CB","クラッチプレイヤー","職人"], 'growth':["標準型","安定型","早熟型","晩成型"]},
    'TUR': {'bias':{'Pow':3,'Men':2}, 'styles':["感情型","爆発型","タックルマスター","勝負師","影の支配者"], 'growth':["一発屋型","スペ体質","標準型","晩成型"]},
    'ARG': {'bias':{'Tec':3,'Men':2}, 'styles':["王様タイプ","トリックスター","勝負師","メディア映え型","クラッチプレイヤー"], 'growth':["早熟型","標準型","晩成型","終盤爆発型"]},
    'URU': {'bias':{'Men':3,'Pow':2}, 'styles':["勝負師","空中戦の鬼","タックルマスター","影の支配者","チーム至上主義"], 'growth':["晩成型","超晩成型","安定型","標準型"]},
    'COL': {'bias':{'Spd':2,'Tec':2}, 'styles':["俊足ドリブラー","トリックスター","ジョーカー","チャンスメーカー","爆発型"], 'growth':["一発屋型","標準型","早熟型","終盤爆発型"]},
    'USA': {'bias':{'Phy':2,'Sta':2}, 'styles':["バランサー","配給型CB","メンタルリーダー","クラッチプレイヤー","職人"], 'growth':["標準型","安定型","早熟型","晩成型"]},
    'MEX': {'bias':{'Tec':2,'Sht':2}, 'styles':["フリーキックスペシャリスト","チャンスメーカー","ジョーカー","感情型","爆発型"], 'growth':["早熟型","標準型","一発屋型","終盤爆発型"]},
    'SAU': {'bias':{'Men':2,'Sta':1}, 'styles':["メンタルリーダー","影の支配者","王様タイプ","職人","バランサー"], 'growth':["標準型","晩成型","安定型","スペ体質"]},
    'NGA': {'bias':{'Spd':3,'Phy':3}, 'styles':["俊足ドリブラー","空中戦の鬼","爆発型","感情型","タックルマスター"], 'growth':["一発屋型","標準型","終盤爆発型","スペ体質"]},
    'MAR': {'bias':{'Tec':2,'Men':2}, 'styles':["トリックスター","フリーキックスペシャリスト","影の支配者","チャンスメーカー","王様タイプ"], 'growth':["早熟型","標準型","晩成型","安定型"]},
    'KOR': {'bias':{'Sta':3,'Men':2}, 'styles':["チーム至上主義","メンタルリーダー","バランサー","配給型CB","勝負師"], 'growth':["標準型","晩成型","安定型","終盤爆発型"]},
    'AUS': {'bias':{'Phy':2,'Pow':2}, 'styles':["空中戦の鬼","配給型CB","バランサー","クラッチプレイヤー","職人"], 'growth':["標準型","安定型","早熟型","晩成型"]}
}

# デフォルト
NATION_TRAITS_DEFAULT = {'bias':{}, 'styles':PLAY_STYLE_POOL, 'growth':GROWTH_TYPES_POOL}

# ---------------- ユーティリティ関数群 ----------------
def pick_style_pool(nat):
    t = NATION_TRAITS.get(nat, NATION_TRAITS_DEFAULT)
    base = t['styles'][:]
    # 足りなければ全体から補完
    if len(base) < 6:
        base += [x for x in PLAY_STYLE_POOL if x not in base]
    random.shuffle(base)
    return base

def pick_growth_pool(nat):
    t = NATION_TRAITS.get(nat, NATION_TRAITS_DEFAULT)
    base = t['growth'][:]
    if len(base) < 4:
        base += [x for x in GROWTH_TYPES_POOL if x not in base]
    random.shuffle(base)
    return base

def apply_bias(stats:dict, nat:str):
    bias = NATION_TRAITS.get(nat, NATION_TRAITS_DEFAULT)['bias']
    for k,v in bias.items():
        if k in stats:
            stats[k] = int(max(30, min(99, stats[k] + random.randint(v//2, v))))
    return stats

def normalize_value(v:int)->int:
    if v >= 1000:
        return (v // 1000) * 1000
    else:
        return v - (v % 5)

def suggest_positions(df):
    need = []
    target = {'GK':2,'DF':8,'MF':8,'FW':4}
    cnt = df['Pos'].value_counts()
    for p, req in target.items():
        lack = req - cnt.get(p,0)
        if lack > 0:
            need.append(f"{p} x{lack}")
    return "・".join(need) if need else "十分揃っています"

def growth_delta(gtype, age, youth=False):
    base = 0
    if gtype in ["超早熟型","早熟型"]:
        base = 1.2 if youth else (0.5 if age<23 else -0.3)
    elif gtype in ["晩成型","超晩成型","終盤爆発型"]:
        base = (0.2 if age<23 else 1.0) if gtype!="終盤爆発型" else (0 if age<25 else 1.5)
    elif gtype == "一発屋型":
        base = 2.0 if random.random()<0.08 else -0.5
    elif gtype == "スペ体質":
        base = 0.8 if random.random()<0.3 else -0.4
    else:
        base = 0.3
    return base + random.uniform(-0.5,0.5)

def apply_growth(df, week):
    for idx, r in df.iterrows():
        delta = growth_delta(r['GrowthType'], r['Age'], youth=False)
        for k in ABILITY_KEYS:
            newv = int(max(30, min(99, r[k] + (1 if delta>0 and random.random()<0.6 else (-1 if random.random()<0.4 else 0)))))
            df.at[idx, k] = newv
        df.at[idx, 'OVR'] = int(np.mean([df.at[idx, k] for k in ABILITY_KEYS]))
    return df

def update_player_history(name, df_row, week):
    snap = {'week':week,'OVR':df_row['OVR']}
    for k in ABILITY_KEYS:
        snap[k] = int(df_row[k])
    st.session_state.player_history.setdefault(name, []).append(snap)

def gen_unique_name(nat, used):
    while True:
        first = random.choice(NAME_POOLS[nat]['given'])
        last  = random.choice(NAME_POOLS[nat]['surname'])
        name  = f"{first} {last}"
        if name not in used:
            used.add(name)
            return name

def gen_players(n, youth=False, club=None, used=None):
    if used is None:
        used = set()
    rows = []
    for _ in range(n):
        nat = random.choice(ALL_NATIONS)
        name = gen_unique_name(nat, used)
        # 能力生成
        stats = {k: random.randint(50 if youth else 60, 80 if youth else 90) for k in ABILITY_KEYS}
        stats = apply_bias(stats, nat)

        style_pool  = pick_style_pool(nat)
        growth_pool = pick_growth_pool(nat)
        play_styles = random.sample(style_pool, 2)
        growth_type = random.choice(growth_pool)

        ovr = int(np.mean(list(stats.values())))
        age = random.randint(15,19) if youth else random.randint(18,34)
        pid = random.randint(10**7,10**8-1)

        rows.append({
            'PID': pid,
            'Name': name,
            'Nat': nat,
            'Pos': random.choice(['GK','DF','MF','FW']),
            **stats,
            'OVR': ovr,
            'PlayStyle': play_styles,
            'GrowthType': growth_type,
            'Age': age,
            'Club': club if club else "Free",
            'Matches': 0,
            'Goals': 0,
            'Assists': 0,
            'Shots': 0,
            'OnTarget': 0,
            'IntlApps': 0,
            'RentalFrom': None,
            'RentalUntil': None,
            'OptionFee': None,
            'Status': "通常",
            'Value': normalize_value(ovr*5000 + random.randint(-5000, 12000))
        })
    return pd.DataFrame(rows)

# ---------------- AIクラブ方針などはこの後（4/11以降）に続きます ----------------

# ---------------- AIクラブ方針 ----------------
AI_POLICIES = ["seller","hold","young","star","balanced"]

def build_club_intents(leagues, my_club):
    intent = {}
    for reg in leagues:
        for div in leagues[reg]:
            for c in leagues[reg][div]:
                if c == my_club:
                    continue
                intent[c] = {
                    'policy': random.choice(AI_POLICIES),
                    'budget': random.randint(2_000_000, 15_000_000),
                    'sell_core': random.random()<0.2,
                    'develop_youth': random.random()<0.5
                }
    return intent

# ---------------- 移籍・レンタル判定 ----------------
def offer_result(row, wage, years, fee, my_budget, club_policy):
    want_wage = row['OVR']*120 + random.randint(-3000,3000)
    want_fee  = row['Value']
    coef = 0.8 if club_policy=='seller' else (1.2 if club_policy=='hold' else 1.0)
    wage_ok = wage >= want_wage
    fee_ok  = fee  >= want_fee*coef
    club_ok = random.random() < (0.7 if club_policy=='seller' else (0.4 if club_policy=='hold' else 0.55))
    money_ok= my_budget >= fee
    return (wage_ok and fee_ok and club_ok and money_ok), want_wage, int(want_fee*coef)

def rental_result(row, weeks, fee, my_budget, club_policy):
    demand = int(row['Value']*0.15 + weeks*800)
    ok_fee = fee >= demand
    ok_club= random.random() < (0.65 if club_policy!='hold' else 0.4)
    return (ok_fee and ok_club and my_budget>=fee), demand

# ---------------- スタンディング更新 ----------------
def apply_result(df, home, away, gh, ga):
    if gh>ga:
        df.loc[df.Club==home, ['W','Pts']] += [1,3]
        df.loc[df.Club==away, 'L'] += 1
    elif gh<ga:
        df.loc[df.Club==away, ['W','Pts']] += [1,3]
        df.loc[df.Club==home, 'L'] += 1
    else:
        df.loc[df.Club.isin([home,away]), 'D'] += 1
        df.loc[df.Club.isin([home,away]), 'Pts'] += 1
    df.loc[df.Club==home, ['GF','GA']] += [gh, ga]
    df.loc[df.Club==away, ['GF','GA']] += [ga, gh]
    return df

# ---------------- レンタル期限管理 ----------------
def tick_rentals(df, week, pending_list):
    for i, r in df.iterrows():
        if r['RentalUntil'] is not None and week > r['RentalUntil'] and r['Status'].startswith("レンタル中"):
            pending_list.append(r['PID'])
            df.at[i,'Status'] = "レンタル満了"
    return df, pending_list

# ---------------- 国際大会オート進行（個人成績含む） ----------------
def auto_intl_round():
    ses = st.session_state
    if not ses.intl_tournament:
        parts=[]
        for reg in ses.leagues:
            if '1部' in ses.standings[reg]:
                parts.extend(ses.standings[reg]['1部'].nlargest(2,'Pts')['Club'].tolist())
        random.shuffle(parts)
        ses.intl_tournament = {'clubs':parts,'results':[]}

    clubs = ses.intl_tournament['clubs']
    if len(clubs) < 2:
        return

    winners=[]
    for i in range(0,len(clubs)-1,2):
        c1,c2 = clubs[i], clubs[i+1]
        g1,g2 = random.randint(0,4), random.randint(0,4)
        pk_txt=""
        if g1==g2:
            pk1,pk2 = random.randint(3,5), random.randint(3,5)
            while pk1==pk2:
                pk1,pk2 = random.randint(3,5), random.randint(3,5)
            pk_txt=f"PK {pk1}-{pk2}"
            w = c1 if pk1>pk2 else c2
        else:
            w = c1 if g1>g2 else c2

        ses.intl_tournament['results'].append((c1,g1,c2,g2,pk_txt,w))
        ses.sns_posts.append(f"[国際大会] {c1} {g1}-{g2} {c2} {pk_txt} → 勝者:{w}")
        ses.sns_times.append(datetime.now())

        if 'intl_player_stats' not in ses:
            ses.intl_player_stats = {}

        pool_all = pd.concat([ses.senior, ses.youth, ses.all_players_pool], ignore_index=True)
        for club, goals in [(c1,g1),(c2,g2)]:
            team_df = pool_all[pool_all['Club']==club]
            if team_df.empty: 
                continue
            XI = team_df.nlargest(11,'OVR')
            # ゴール
            for _ in range(goals):
                pid = random.choice(XI['PID'].tolist())
                ses.intl_player_stats.setdefault(pid, {'G':0,'A':0,'Club':club,
                                                       'Name':team_df[team_df['PID']==pid]['Name'].iloc[0],
                                                       'Pos':team_df[team_df['PID']==pid]['Pos'].iloc[0]})
                ses.intl_player_stats[pid]['G'] += 1
            # アシスト
            for _ in range(goals):
                pid = random.choice(XI['PID'].tolist())
                ses.intl_player_stats.setdefault(pid, {'G':0,'A':0,'Club':club,
                                                       'Name':team_df[team_df['PID']==pid]['Name'].iloc[0],
                                                       'Pos':team_df[team_df['PID']==pid]['Pos'].iloc[0]})
                ses.intl_player_stats[pid]['A'] += 1

        # 自クラブ参加者の国際大会出場数カウント
        if c1==ses.my_club or c2==ses.my_club:
            starters_names = ses.starters if ses.starters else ses.senior.nlargest(11,'OVR')['Name'].tolist()
            for nm in starters_names:
                for df in [ses.senior, ses.youth]:
                    idx = df.index[df['Name']==nm]
                    if len(idx)>0:
                        df.at[idx[0],'IntlApps'] = df.at[idx[0],'IntlApps'] + 1

        winners.append(w)

    if len(clubs)%2==1:
        winners.append(clubs[-1])
    ses.intl_tournament['clubs'] = winners

# ---------------- セッション初期化 ----------------
ses = st.session_state

if 'my_club' not in ses:
    ses.my_club = MY_CLUB_DEFAULT
if 'leagues' not in ses:
    ses.leagues = build_leagues(ses.my_club)
if 'week' not in ses:
    ses.week = 1
if 'budget' not in ses:
    ses.budget = 5_000_000
if 'used_names' not in ses:
    ses.used_names = set()

# 自クラブ
if 'senior' not in ses:
    ses.senior = gen_players(30, youth=False, club=ses.my_club, used=ses.used_names)
if 'youth' not in ses:
    ses.youth  = gen_players(20, youth=True , club=ses.my_club, used=ses.used_names)

# 他クラブ全体プール
if 'all_players_pool' not in ses:
    pool = []
    for reg in ses.leagues:
        for div in ses.leagues[reg]:
            for c in ses.leagues[reg][div]:
                if c == ses.my_club:
                    continue
                pool.append(gen_players(random.randint(18,26), youth=False, club=c, used=ses.used_names))
    ses.all_players_pool = pd.concat(pool, ignore_index=True)

# スタンディング
if 'standings' not in ses:
    ses.standings = {
        r:{ d:pd.DataFrame({'Club':ses.leagues[r][d],
                            'W':0,'D':0,'L':0,'GF':0,'GA':0,'Pts':0})
            for d in ses.leagues[r]}
        for r in ses.leagues
    }

# クラブ→地域/Div マップ
if 'club_region_div' not in ses:
    mapping={}
    for reg in ses.leagues:
        for div in ses.leagues[reg]:
            for c in ses.leagues[reg][div]:
                mapping[c]=(reg,div)
    ses.club_region_div = mapping

# AIクラブ方針（自動設定のみ。タブ表示なし）
if 'club_intent' not in ses:
    ses.club_intent = build_club_intents(ses.leagues, ses.my_club)

# 各種ログ・入れ物
defaults = {
    'player_history':{},
    'match_log':[],
    'sns_posts':[],
    'sns_times':[],
    'finance_log':[],
    'season_summary':[],
    'injury_info':{},
    'suspension_info':{},
    'intl_tournament':{},
    'scout_list':pd.DataFrame(),
    'rental_pending':[],
    'starters':[],
    'intl_player_stats':{}
}
for k,v in defaults.items():
    if k not in ses: ses[k]=v

# レンタル満了チェック
ses.senior, ses.rental_pending = tick_rentals(ses.senior, ses.week, ses.rental_pending)
ses.youth , ses.rental_pending = tick_rentals(ses.youth , ses.week, ses.rental_pending)

# ---------------- レンタル満了処理UI ----------------
def handle_rental_expirations():
    if not ses.rental_pending:
        return
    st.markdown("### レンタル満了選手の処理")
    df_all = pd.concat([ses.senior, ses.youth], ignore_index=True)
    for pid in ses.rental_pending[:]:
        row = df_all[df_all['PID']==pid]
        if row.empty:
            ses.rental_pending.remove(pid)
            continue
        r = row.iloc[0]
        st.write(f"**{r['Name']}** | Pos:{r['Pos']} | OVR:{r['OVR']} | 元:{r['RentalFrom']} | 買取OP:{r['OptionFee']}€")
        c1,c2 = st.columns(2)
        with c1:
            if st.button(f"買取する（{r['OptionFee']}€）", key=f"buy_{pid}"):
                if ses.budget >= r['OptionFee']:
                    ses.budget -= r['OptionFee']
                    for df in [ses.senior, ses.youth]:
                        idx = df.index[df['PID']==pid]
                        if len(idx)>0:
                            df.at[idx[0],'Club'] = ses.my_club
                            df.at[idx[0],'RentalFrom'] = None
                            df.at[idx[0],'RentalUntil']= None
                            df.at[idx[0],'OptionFee']  = None
                            df.at[idx[0],'Status']     = "通常"
                            break
                    st.success("買取成立！")
                    ses.rental_pending.remove(pid)
                else:
                    st.error("予算不足です。")
        with c2:
            if st.button("返却する", key=f"return_{pid}"):
                origin = r['RentalFrom']
                removed=False
                for df in [ses.senior, ses.youth]:
                    idx = df.index[df['PID']==pid]
                    if len(idx)>0:
                        row_back = df.loc[idx[0]].copy()
                        df.drop(idx, inplace=True)
                        removed=True
                        break
                if removed:
                    row_back['Club']=origin
                    row_back['RentalFrom']=None
                    row_back['RentalUntil']=None
                    row_back['OptionFee']=None
                    row_back['Status']="通常"
                    ses.all_players_pool = pd.concat([ses.all_players_pool, pd.DataFrame([row_back])], ignore_index=True)
                st.info("返却完了")
                ses.rental_pending.remove(pid)

# ---------------- スカウト候補生成 ----------------
def gen_scout_candidates(pool_df, myclub, n=6, youth=False):
    free_cnt = max(1, n//2)
    free_df  = gen_players(free_cnt, youth=youth, club="Free", used=ses.used_names)
    others = pool_df[(pool_df['Club']!="Free") & (pool_df['Club']!=myclub)]
    take = n - free_cnt
    pick_df = others.sample(min(take, len(others))) if len(others)>0 else pd.DataFrame()
    cands = pd.concat([free_df, pick_df], ignore_index=True)
    cands['PlayStyle'] = cands['PlayStyle'].apply(lambda x: " / ".join(x))
    return cands.sample(frac=1).reset_index(drop=True)

def get_rental_candidates(pool_df, myclub):
    return pool_df[(pool_df['Club']!=myclub) & (pool_df['RentalFrom'].isna()) & (pool_df['RentalUntil'].isna())]

# ---------------- タブ定義 ----------------
tabs = st.tabs([
    'シニア','ユース','選手詳細','試合','順位表',
    'スカウト/移籍','レンタル管理','SNS','財務レポート',
    '年間表彰','ランキング/国際大会','クラブ設定'
])

# ========= 0) シニア =========
with tabs[0]:
    st.markdown('<div style="color:#fff;font-size:20px;">シニア選手一覧</div>', unsafe_allow_html=True)
    handle_rental_expirations()

    order_mode = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="o_senior")
    reverse_flag = (order_mode=="FW→MF→DF→GK")

    df0 = ses.senior[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Club','Status']]
    df0['PlayStyle'] = df0['PlayStyle'].apply(lambda x:" / ".join(x))
    df0 = sort_by_pos(df0, reverse=reverse_flag)

    st.dataframe(
        df0.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                 .apply(style_playstyle, subset=['PlayStyle'])
                 .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# ========= 1) ユース =========
with tabs[1]:
    st.markdown('<div style="color:#fff;font-size:20px;">ユース選手一覧</div>', unsafe_allow_html=True)

    order_mode_y = st.radio("並び順", ["GK→DF→MF→FW","FW→MF→DF→GK"], horizontal=True, key="o_youth")
    reverse_flag_y = (order_mode_y=="FW→MF→DF→GK")

    df1 = ses.youth[['Name','Nat','Pos','Age','OVR','IntlApps','PlayStyle','Club','Status']]
    df1['PlayStyle'] = df1['PlayStyle'].apply(lambda x:" / ".join(x))
    df1 = sort_by_pos(df1, reverse=reverse_flag_y)

    st.dataframe(
        df1.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                 .apply(style_playstyle, subset=['PlayStyle'])
                 .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# ========= 2) 選手詳細 =========
with tabs[2]:
    pool_detail = pd.concat([ses.senior, ses.youth], ignore_index=True)
    sel_name = st.selectbox('選手選択', pool_detail['Name'].tolist())

    prow = pool_detail[pool_detail['Name']==sel_name].iloc[0]
    base_ovr = prow['OVR']
    hist = pd.DataFrame(ses.player_history.get(sel_name, [{'week':0,'OVR':base_ovr, **{k:prow[k] for k in ABILITY_KEYS}}]))

    st.write(f"ポジション: {prow['Pos']} / OVR:{prow['OVR']} / 年齢:{prow['Age']}")
    st.write(f"国籍: {prow['Nat']} / 国際大会出場: {prow['IntlApps']}回")
    st.write(f"プレースタイル: {', '.join(prow['PlayStyle'])}")
    st.write(f"所属: {prow['Club']} / 状態: {prow['Status']}")

    # 能力バーグラフ
    vals = [prow[k] for k in ABILITY_KEYS]
    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(ABILITY_KEYS, vals)
    ax_bar.set_ylim(0, 100); ax_bar.set_title("能力バー表示")
    st.pyplot(fig_bar)

    # 能力推移（折れ線）
    if len(hist) > 1:
        fig_all, ax_all = plt.subplots()
        for k in ABILITY_KEYS:
            ax_all.plot(hist['week'], hist[k], marker='o', label=k)
        ax_all.set_xlabel('節'); ax_all.set_ylabel('能力'); ax_all.legend(bbox_to_anchor=(1,1))
        st.pyplot(fig_all)

        fig_ovr, ax_ovr = plt.subplots()
        ax_ovr.plot(hist['week'], hist['OVR'], marker='o')
        ax_ovr.set_xlabel('節'); ax_ovr.set_ylabel('総合値')
        st.pyplot(fig_ovr)
    else:
        st.info("成長データはまだありません。")

# ========= 3) 試合 =========
with tabs[3]:
    st.markdown(f"<div style='color:#fff;font-size:20px;'>第{ses.week}節 試合シミュレーション</div>", unsafe_allow_html=True)

    formation = st.selectbox("フォーメーション", ["4-4-2","4-3-3","3-5-2"])
    if st.button("オート先発選考"):
        req = {
            "4-4-2":("FW",2,"MF",4,"DF",4,"GK",1),
            "4-3-3":("FW",3,"MF",3,"DF",4,"GK",1),
            "3-5-2":("FW",2,"MF",5,"DF",3,"GK",1)
        }[formation]
        starters=[]
        for i in range(0,len(req),2):
            pos,cnt=req[i],req[i+1]
            starters += ses.senior[ses.senior['Pos']==pos].nlargest(cnt,'OVR')['Name'].tolist()
        ses.starters = starters

    if ses.starters:
        st.markdown('<span style="color:white;font-weight:bold;">【先発メンバー】</span>', unsafe_allow_html=True)
        s_df = ses.senior[ses.senior['Name'].isin(ses.starters)][['Name','Pos','OVR','PlayStyle','Club']]
        s_df['PlayStyle']=s_df['PlayStyle'].apply(lambda x:" / ".join(x))
        s_df = sort_by_pos(s_df)
        st.dataframe(
            s_df.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                      .apply(style_playstyle, subset=['PlayStyle'])
                      .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

    # 自クラブが所属する地域・ディビジョンから対戦相手を選択
    my_reg, my_div = ses.club_region_div[ses.my_club]
    opp = random.choice([c for c in ses.leagues[my_reg][my_div] if c != ses.my_club])

    if ses.week <= SEASON_WEEKS and st.button("キックオフ"):
        atk = ses.senior[ses.senior['Name'].isin(ses.starters)]['OVR'].mean() if ses.starters else 70
        oppatk = random.uniform(60,90)
        gh = max(0,int(np.random.normal((atk-60)/8,1)))
        ga = max(0,int(np.random.normal((oppatk-60)/8,1)))
        shots = random.randint(5,15); on_t = random.randint(0,shots)

        scorers=[]; assisters=[]
        if gh>0 and ses.starters:
            for _ in range(gh):
                s = random.choice(ses.starters)
                a = random.choice([x for x in ses.starters if x!=s]) if len(ses.starters)>1 else s
                scorers.append(s); assisters.append(a)
                ses.senior.loc[ses.senior['Name']==s,'Goals']   += 1
                ses.senior.loc[ses.senior['Name']==a,'Assists'] += 1

        ses.match_log.append({'week':ses.week,'opp':opp,'gf':gh,'ga':ga})
        ses.sns_posts.append(f"{ses.my_club} {gh}-{ga} {opp}")
        ses.sns_times.append(datetime.now())

        ses.finance_log.append({
            'week': ses.week,
            'revenue_ticket': gh*15000 + random.randint(5000,10000),
            'revenue_goods' : ga*8000  + random.randint(1000,5000),
            'expense_salary': int(ses.senior['OVR'].mean()*1000)
        })

        ses.standings[my_reg][my_div] = apply_result(ses.standings[my_reg][my_div], ses.my_club, opp, gh, ga)

        # 他試合を自動処理
        for reg in ses.leagues:
            for div in ses.leagues[reg]:
                clubs = ses.leagues[reg][div]
                for i in range(0,len(clubs),2):
                    if i+1>=len(clubs): break
                    h,a = clubs[i], clubs[i+1]
                    if {h,a}=={ses.my_club,opp}:
                        continue
                    g1,g2 = random.randint(0,3), random.randint(0,3)
                    ses.standings[reg][div] = apply_result(ses.standings[reg][div], h,a,g1,g2)

        # 成長処理＆履歴保存
        ses.senior = apply_growth(ses.senior, ses.week)
        for _,rw in ses.senior.iterrows():
            update_player_history(rw['Name'], rw, ses.week)

        st.success(f"結果 {gh}-{ga}")
        if scorers:   st.write("得点者: " + " / ".join(scorers))
        if assisters: st.write("アシスト: " + " / ".join(assisters))
        st.write(f"シュート:{shots} 枠内:{on_t} ポゼッション:{random.randint(40,60)}%")

        ses.week += 1
        auto_intl_round()

        if ses.week > SEASON_WEEKS:
            champ = ses.standings[my_reg][my_div].nlargest(1,'Pts')['Club'].iloc[0]
            top_scorer = ses.senior.nlargest(1,'Goals')['Name'].iloc[0] if 'Goals' in ses.senior else ''
            ses.season_summary.append({'Champion':champ,'TopScorer':top_scorer})
            st.success("シーズン終了！")

    elif ses.week > SEASON_WEEKS:
        st.info("シーズン終了済。次シーズン開始してください。")
        if st.button("次シーズン開始"):
            ses.week = 1
            ses.senior = gen_players(30, youth=False, club=ses.my_club, used=ses.used_names)
            ses.youth  = gen_players(20, youth=True , club=ses.my_club, used=ses.used_names)
            ses.standings = {
                r:{d:pd.DataFrame({'Club':ses.leagues[r][d],'W':0,'D':0,'L':0,'GF':0,'GA':0,'Pts':0})
                   for d in ses.leagues[r]} for r in ses.leagues
            }
            ses.sns_posts.clear(); ses.sns_times.clear()
            ses.finance_log.clear(); ses.intl_tournament.clear()
            ses.match_log.clear(); ses.player_history.clear()
            ses.intl_player_stats.clear()
            st.success("新シーズン開始！")

# ========= 4) 順位表 =========
with tabs[4]:
    region = st.selectbox('地域', list(ses.leagues.keys()))
    division = st.selectbox('部', list(ses.leagues[region].keys()))
    df_st = ses.standings[region][division]
    st.dataframe(
        df_st.style.apply(make_highlighter('Club', ses.my_club), axis=1)
            .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# ========= 5) スカウト/移籍 =========
with tabs[5]:
    st.markdown("<div style='color:#fff;font-size:20px;'>スカウト / 移籍 / レンタル</div>", unsafe_allow_html=True)

    cat = st.radio("対象カテゴリー", ["シニア候補","ユース候補"], horizontal=True)
    youth_flag = (cat=="ユース候補")

    need_txt = suggest_positions(ses.senior if not youth_flag else ses.youth)
    st.markdown(f"**補強推奨ポジション:** {need_txt}")

    c1,c2 = st.columns(2)
    with c1:
        if st.button("候補リスト更新"):
            pool_all = pd.concat([ses.all_players_pool, ses.senior, ses.youth], ignore_index=True)
            ses.scout_list = gen_scout_candidates(pool_all, ses.my_club, n=8, youth=youth_flag)
    with c2:
        st.write(f"予算: {ses.budget:,} €")

    if ses.scout_list is None or ses.scout_list.empty:
        st.info("候補がいません。『候補リスト更新』を押してください。")
    else:
        for i,row in ses.scout_list.iterrows():
            st.markdown(
                "<div style='background:rgba(255,255,255,0.10);padding:10px 14px;margin:14px 0;border-radius:10px;'>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"**{row['Name']}** | {row['Nat']} | {row['Age']}歳 | {row['Pos']} | OVR:{row['OVR']}<br>"
                f"PlayStyle: {row['PlayStyle']}<br>"
                f"所属:{row['Club']} / 価値:{row['Value']:,}€",
                unsafe_allow_html=True
            )

            if row['Club']=="Free":
                if st.button("契約", key=f"sign_free_{i}"):
                    dst = 'youth' if youth_flag else 'senior'
                    setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row])], ignore_index=True))
                    ses.scout_list = ses.scout_list.drop(i).reset_index(drop=True)
                    st.success("獲得しました！")
            else:
                mode = st.selectbox(f"オファー種別（{row['Name']}）", ["完全移籍","レンタル(買取OP付)"], key=f"mode_{i}")
                policy = ses.club_intent.get(row['Club'],{}).get('policy','balanced')

                with st.form(f"offer_{i}"):
                    if mode=="完全移籍":
                        wage = st.number_input("提示年俸(€)", min_value=0, value=row['OVR']*150, key=f"wage_{i}")
                        years= st.slider("契約年数",1,5,3, key=f"years_{i}")
                        fee  = st.number_input("移籍金(€)", min_value=0, value=int(row['Value']), key=f"fee_{i}")
                        sub  = st.form_submit_button("送信")
                        if sub:
                            ok, want_wage, want_fee = offer_result(row, wage, years, fee, ses.budget, policy)
                            if ok:
                                ses.budget -= fee
                                row2 = row.copy(); row2['Club']=ses.my_club
                                dst = 'youth' if youth_flag else 'senior'
                                setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row2])], ignore_index=True))
                                ses.scout_list = ses.scout_list.drop(i).reset_index(drop=True)
                                st.success("移籍成立！")
                            else:
                                st.error(f"拒否【要求目安:年俸{want_wage}€, 移籍金{want_fee}€】")

                    else:  # レンタル
                        weeks = st.slider("レンタル期間（節）",1,8,4, key=f"weeks_{i}")
                        fee_r = st.number_input("レンタル料(€)", min_value=0, value=int(row['Value']*0.15), key=f"feer_{i}")
                        opt   = st.number_input("買取オプション額(€)", min_value=0, value=int(row['Value']*1.2), key=f"opt_{i}")
                        subr  = st.form_submit_button("送信")
                        if subr:
                            ok, demand = rental_result(row,weeks,fee_r,ses.budget,policy)
                            if ok:
                                ses.budget -= fee_r
                                row2 = row.copy()
                                row2['Club'] = ses.my_club
                                row2['RentalFrom'] = row['Club']
                                row2['RentalUntil']= ses.week + weeks
                                row2['OptionFee']  = opt
                                row2['Status']     = f"レンタル中({weeks}節)"
                                dst = 'youth' if youth_flag else 'senior'
                                setattr(ses, dst, pd.concat([getattr(ses,dst), pd.DataFrame([row2])], ignore_index=True))
                                ses.all_players_pool = ses.all_players_pool[ses.all_players_pool['PID']!=row['PID']]
                                ses.scout_list = ses.scout_list.drop(i).reset_index(drop=True)
                                st.success("レンタル成立！")
                            else:
                                st.error(f"拒否【要求額目安:{demand}€】")
            st.markdown("</div>", unsafe_allow_html=True)

# ========= 6) レンタル管理 =========
with tabs[6]:
    st.markdown("<div style='color:#fff;font-size:20px;'>レンタル管理</div>", unsafe_allow_html=True)
    handle_rental_expirations()

    df_r = pd.concat([ses.senior, ses.youth], ignore_index=True)
    df_r = df_r[df_r['Status'].str.startswith("レンタル中", na=False)][
        ['Name','Pos','OVR','RentalFrom','RentalUntil','OptionFee','Status']
    ]
    if df_r.empty:
        st.info("レンタル中の選手はいません。")
    else:
        st.dataframe(
            df_r.set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

# ========= 7) SNS =========
with tabs[7]:
    st.markdown("<div style='color:#fff;font-size:20px;'>SNS / ファン投稿</div>", unsafe_allow_html=True)
    if ses.sns_posts:
        for t, p in zip(reversed(ses.sns_times), reversed(ses.sns_posts)):
            st.write(f"{t.strftime('%m/%d %H:%M')} - {p}")
    else:
        st.info("投稿なし")

# ========= 8) 財務レポート =========
with tabs[8]:
    st.markdown("<div style='color:#fff;font-size:20px;'>財務レポート</div>", unsafe_allow_html=True)
    df_fin = pd.DataFrame(ses.finance_log)
    if df_fin.empty:
        st.info("財務データなし")
    else:
        fig, ax = plt.subplots()
        ax.plot(df_fin['week'], df_fin['revenue_ticket']+df_fin['revenue_goods'], label='収入')
        ax.plot(df_fin['week'], df_fin['expense_salary'], label='支出')
        ax.set_xlabel("節"); ax.set_ylabel("金額(€)"); ax.set_title("収支推移")
        ax.legend()
        st.pyplot(fig)

        st.dataframe(
            df_fin.rename(columns={
                'week':'節','revenue_ticket':'チケット収入','revenue_goods':'グッズ収入','expense_salary':'人件費'
            }).style.set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

# ========= 9) 年間表彰 =========
with tabs[9]:
    st.markdown('<div style="color:white;font-size:20px;">年間表彰</div>', unsafe_allow_html=True)

    df_all_my = pd.concat([ses.senior, ses.youth], ignore_index=True)
    for stat in ['Goals','Assists']:
        if stat not in df_all_my: df_all_my[stat]=0

    top5g = df_all_my.nlargest(5,'Goals')[['Name','Pos','Goals','Club']]
    top5a = df_all_my.nlargest(5,'Assists')[['Name','Pos','Assists','Club']]

    st.markdown('<span style="color:white;font-weight:bold;">🏅 自クラブ内 得点王 TOP5</span>', unsafe_allow_html=True)
    st.dataframe(
        top5g.style.apply(make_highlighter('Club', ses.my_club), axis=1)
              .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

    st.markdown('<span style="color:white;font-weight:bold;">🎯 自クラブ内 アシスト王 TOP5</span>', unsafe_allow_html=True)
    st.dataframe(
        top5a.style.apply(make_highlighter('Club', ses.my_club), axis=1)
              .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
        use_container_width=True
    )

# ========= 10) ランキング / 国際大会 =========
with tabs[10]:
    st.markdown('<div style="color:white;font-size:22px;font-weight:bold;">ランキング / 国際大会まとめ</div>', unsafe_allow_html=True)

    # 国際大会 試合ログ
    st.markdown("### 🌍 国際大会 試合ログ")
    if not ses.intl_tournament or len(ses.intl_tournament.get('results',[]))==0:
        st.info("国際大会はまだ開始されていません。試合を進めると自動で進行します。")
    else:
        for idx,m in enumerate(ses.intl_tournament['results']):
            line = f"【R{idx+1}】 {m[0]} {m[1]}-{m[3]} {m[2]} {m[4]} → 勝者:{m[5]}"
            if ses.my_club in line:
                st.markdown(f"<span style='background:#f7df70;color:#202b41;font-weight:bold'>{line}</span>", unsafe_allow_html=True)
            else:
                st.write(line)
        if len(ses.intl_tournament['clubs'])==1:
            champ = ses.intl_tournament['clubs'][0]
            msg = f"優勝: {champ}"
            if champ==ses.my_club:
                st.markdown(f"<span style='background:#f7df70;color:#202b41;font-weight:bold'>{msg}</span>", unsafe_allow_html=True)
            else:
                st.success(msg)

    st.markdown("---")

    # 国際大会 個人成績
    st.markdown("### 🏆 国際大会 個人成績ランキング")
    if not ses.intl_player_stats:
        st.info("国際大会の個人成績データがまだありません。")
    else:
        df_intp = pd.DataFrame.from_dict(ses.intl_player_stats, orient='index')
        top_g = df_intp.sort_values('G', ascending=False).head(10)[['Name','Pos','G','A','Club']]
        st.markdown("**得点ランキング TOP10**")
        st.dataframe(
            top_g.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                       .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

        top_a = df_intp.sort_values('A', ascending=False).head(10)[['Name','Pos','A','G','Club']]
        st.markdown("**アシストランキング TOP10**")
        st.dataframe(
            top_a.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                       .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

        best11=[]
        for p,need in [('GK',1),('DF',4),('MF',4),('FW',2)]:
            cand = df_intp[df_intp['Pos']==p].copy()
            cand['Score'] = cand['G']*2 + cand['A']
            best11.append(cand.sort_values('Score', ascending=False).head(need)[['Name','Pos','G','A','Club']])
        best11 = pd.concat(best11)
        st.markdown("**⚽️ 国際大会ベストイレブン**（ポジション別成績上位）")
        st.dataframe(
            best11.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                        .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
            use_container_width=True
        )

    st.markdown("---")

    # 各国リーグランキングまとめ
    st.markdown("### 🇪🇺 各国リーグランキング（順位表・得点王・アシスト王・ベスト11）")
    df_all = pd.concat([ses.senior, ses.youth, ses.all_players_pool], ignore_index=True)
    for col in ['Goals','Assists']:
        if col not in df_all: df_all[col]=0
    df_all['Reg'] = df_all['Club'].map(lambda c: ses.club_region_div.get(c,("",""))[0])
    df_all['Div'] = df_all['Club'].map(lambda c: ses.club_region_div.get(c,("",""))[1])

    for reg in ses.leagues:
        st.markdown(f"## {reg}")
        for div in ses.leagues[reg]:
            st.markdown(f"#### {div} 順位表")
            df_st = ses.standings[reg][div]
            st.dataframe(
                df_st.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                    .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
                use_container_width=True
            )

            sub = df_all[(df_all['Reg']==reg) & (df_all['Div']==div)].copy()
            top_s = sub.nlargest(5,'Goals')[['Name','Pos','Goals','Club']]
            top_a = sub.nlargest(5,'Assists')[['Name','Pos','Assists','Club']]

            st.markdown('<span style="color:white;font-weight:bold;">🏅 得点王 TOP5</span>', unsafe_allow_html=True)
            st.dataframe(
                top_s.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                           .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
                use_container_width=True
            )

            st.markdown('<span style="color:white;font-weight:bold;">🎯 アシスト王 TOP5</span>', unsafe_allow_html=True)
            st.dataframe(
                top_a.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                           .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
                use_container_width=True
            )

            best11=[]
            for p in ['GK','DF','MF','FW']:
                need = 1 if p=='GK' else (4 if p in ['DF','MF'] else 2)
                cand = sub[sub['Pos']==p].nlargest(need,'OVR')[['Name','Pos','OVR','Club']]
                best11.append(cand)
            best11 = pd.concat(best11)
            st.markdown('<span style="color:white;font-weight:bold;">⚽️ ベストイレブン</span>', unsafe_allow_html=True)
            st.dataframe(
                best11.style.apply(make_highlighter('Club', ses.my_club), axis=1)
                            .set_properties(**{"background-color":"rgba(32,44,70,0.85)","color":"#fff"}),
                use_container_width=True
            )
            st.markdown("---")

# ========= 11) クラブ設定 =========
with tabs[11]:
    st.markdown('<div style="color:white;font-size:20px;">クラブ設定</div>', unsafe_allow_html=True)
    new_name = st.text_input("自クラブ名", value=ses.my_club, max_chars=30)
    if st.button("クラブ名変更"):
        if new_name and new_name != ses.my_club:
            old = ses.my_club
            ses.my_club = new_name

            # リーグ再構築（自クラブ差し替え）
            ses.leagues = build_leagues(ses.my_club)

            # 自クラブ所属のプレイヤーも名称更新
            for df in [ses.senior, ses.youth]:
                df.loc[df['Club']==old, 'Club'] = ses.my_club

            # club_region_div を再生成
            mapping={}
            for reg in ses.leagues:
                for div in ses.leagues[reg]:
                    for c in ses.leagues[reg][div]:
                        mapping[c]=(reg,div)
            ses.club_region_div = mapping

            st.success("クラブ名を変更しました。再実行してください。")
