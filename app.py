import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import unicodedata

# Configuração da página
st.set_page_config(page_title="Radar Eleitoral SC - Inteligência", layout="wide")

# Função auxiliar para remover acentos
def normalizar_texto(texto):
    if not texto:
        return ""
    return "".join(c for c in unicodedata.normalize('NFKD', str(texto))
                   if unicodedata.category(c) != 'Mn').upper().strip()

# --- DICIONÁRIO DE COORDENADAS ---
def get_coords_map():
    return {
        'ADRIANOPOLIS': [-24.6644, -48.9928], 'AGROLANDIA': [-27.4014, -49.821], 'AGRONOMICA': [-27.2656, -49.711],
        'AGUA DOCE': [-26.9975, -51.5549], 'AGUAS DE CHAPECO': [-27.0706, -52.9875], 'AGUAS FRIAS': [-26.8814, -52.859],
        'AGUAS MORNAS': [-27.7025, -48.8258], 'ALFREDO WAGNER': [-27.7003, -49.3339], 'ALTO BELA VISTA': [-27.3875, -51.9056],
        'ANCHIETA': [-26.5375, -53.3325], 'ANGELINA': [-27.5683, -48.9856], 'ANITA GARIBALDI': [-27.6881, -51.1303],
        'ANITAPOLIS': [-27.9017, -49.1297], 'ANTONIO CARLOS': [-27.5172, -48.7725], 'APIUNA': [-27.0369, -49.3908],
        'ARABUTA': [-27.1589, -52.1292], 'ARAQUARI': [-26.3742, -48.7214], 'ARARANGUA': [-28.9344, -49.4853],
        'ARMAZEM': [-28.2619, -49.0203], 'ARROIO TRINTA': [-26.9286, -51.2131], 'ARVOREDO': [-27.0744, -52.4542],
        'ASCURRA': [-26.9553, -49.3756], 'ATALANTA': [-27.4253, -49.7719], 'AURORA': [-27.3017, -49.635],
        'BALNEARIO ARROIO DO SILVA': [-28.9847, -49.4136], 'BALNEARIO CAMBORIU': [-26.9925, -48.6341],
        'BALNEARIO GAIVOTA': [-29.1558, -49.5769], 'BALNEARIO PICARRAS': [-26.7644, -48.6719],
        'BALNEARIO RINCAO': [-28.8314, -49.235], 'BALNEARIO BARRA DO SUL': [-26.4556, -48.6119],
        'BANDEIRANTE': [-26.7697, -53.6378], 'BARRA BONITA': [-26.6547, -53.44], 'BARRA VELHA': [-26.6322, -48.6847],
        'BELA VISTA DO TOLDO': [-26.2731, -50.4653], 'BELMONTE': [-26.8422, -53.5764], 'BENEDITO NOVO': [-26.7817, -49.3639],
        'BIGUACU': [-27.4925, -48.6603], 'BLUMENAU': [-26.9193, -49.0661], 'BOM JARDIM DA SERRA': [-28.3372, -49.6272],
        'BOM RETIRO': [-27.7972, -49.4897], 'BOM JESUS': [-26.7328, -52.395], 'BOM JESUS DO OESTE': [-26.7917, -53.0039],
        'BOMBINHAS': [-27.1372, -48.4947], 'BOTUVERA': [-27.2003, -49.1125], 'BRACO DO NORTE': [-28.2728, -49.1747],
        'BRACO DO TROMBUDO': [-27.3606, -49.8839], 'BRUNOPOLIS': [-27.3117, -50.8872], 'BRUSQUE': [-27.0978, -48.911],
        'CACADOR': [-26.7753, -51.0153], 'CAIBI': [-27.0722, -53.2472], 'CALMON': [-26.5986, -51.0967],
        'CAMBORIU': [-27.0247, -48.6533], 'CAMPO ALEGRE': [-26.1933, -49.2639], 'CAMPO ERE': [-26.3944, -53.0872],
        'CAMPO BELO DO SUL': [-27.8986, -50.7583], 'CAMPOS NOVOS': [-27.4019, -51.2264], 'CANELINHA': [-27.2656, -48.7619],
        'CANOINHAS': [-26.1772, -50.4436], 'CAPAO ALTO': [-27.9356, -50.5103], 'CAPINZAL': [-27.3453, -51.6119],
        'CAPIVARI DE BAIXO': [-28.4456, -48.7958], 'CATANDUVAS': [-27.0706, -51.6619], 'CAXAMBU DO SUL': [-27.1625, -52.8806],
        'CELSO RAMOS': [-27.6353, -51.3361], 'CERRO NEGRO': [-27.7925, -50.8775], 'CHAPECO': [-27.1006, -52.6153],
        'COCAL DO SUL': [-28.6019, -49.3258], 'CONCORDIA': [-27.2342, -52.0314], 'CORDILHEIRA ALTA': [-27.0678, -52.7139],
        'CORONEL FREITAS': [-26.9083, -52.7025], 'CORONEL MARTINS': [-26.6433, -52.8122], 'CORREIA PINTO': [-27.5856, -50.3603],
        'CORUPA': [-26.4253, -49.2431], 'CRICIUMA': [-28.6775, -49.3703], 'CUNHA PORA': [-26.8931, -53.1672],
        'CUNHATAI': [-26.9461, -53.0475], 'CURITIBANOS': [-27.2828, -50.5847], 'DESCANSO': [-26.8256, -53.4986],
        'DIONISIO CERQUEIRA': [-26.2547, -53.5042], 'DONA EMMA': [-27.0519, -49.7214], 'DOUTOR PEDRINHO': [-26.7117, -49.4847],
        'ENTRE RIOS': [-26.7217, -52.5572], 'ERVAL VELHO': [-27.2731, -51.4403], 'FAXINAL DOS GUEDES': [-26.8539, -52.2614],
        'FLORIANOPOLIS': [-27.5969, -48.5495], 'FORQUILHINHA': [-28.7461, -49.4719], 'FRAIBURGO': [-27.0256, -50.9169],
        'GASPAR': [-26.9317, -48.9592], 'GOVERNADOR CELSO RAMOS': [-27.3153, -48.5586], 'GRAO PARA': [-28.1839, -49.215],
        'GRAVATAL': [-28.3264, -49.0381], 'GUABIRUBA': [-27.0853, -48.9056], 'GUARACIABA': [-26.5986, -53.5208],
        'GUARAMIRIM': [-26.4742, -49.0033], 'GUARUJA DO SUL': [-26.3908, -53.5222], 'GUATAMBU': [-27.1311, -52.7853],
        'HERVAL D\'OESTE': [-27.1856, -51.4969], 'IBIAM': [-27.1839, -51.2361], 'IBICARE': [-27.0911, -51.3614],
        'IBIRAMA': [-27.0564, -49.5161], 'ICARA': [-28.7125, -49.3003], 'ILHOTA': [-26.8997, -48.8258],
        'IMBITUBA': [-28.24, -48.6703], 'INDAIAL': [-26.89, -49.2317], 'IOMERE': [-27.0019, -51.2431],
        'IPIRA': [-27.3389, -51.7619], 'IPORA DO OESTE': [-26.9883, -53.535], 'IPUACU': [-26.63, -52.4542],
        'IPUMIRIM': [-27.0806, -52.1339], 'IRACEMINHA': [-26.8203, -53.2842], 'IRANI': [-27.0253, -51.905],
        'IRATI': [-26.6547, -52.8469], 'IRINEOPOLIS': [-26.2361, -50.8122], 'ITA': [-27.2883, -52.3214],
        'ITABERABA': [-26.9389, -52.4633], 'ITAIOPOLIS': [-26.3353, -49.9114], 'ITAJAI': [-26.9078, -48.6619],
        'ITAPEMA': [-27.0911, -48.6119], 'ITAPIRANGA': [-27.1689, -53.7119], 'ITAPOA': [-26.1169, -48.6144],
        'ITUPORANGA': [-27.4019, -49.6019], 'JABORA': [-27.1722, -51.7339], 'JACINTO MACHADO': [-28.9972, -49.7644],
        'JAGUARUNA': [-28.6144, -49.0269], 'JARAGUA DO SUL': [-26.4842, -49.0692], 'JOACABA': [-27.1739, -51.5064],
        'JOINVILLE': [-26.3044, -48.8456], 'JOSE BOITEUX': [-26.9583, -49.6283], 'LACERDOPOLIS': [-27.1658, -51.5564],
        'LAGES': [-27.816, -50.3261], 'LAGUNA': [-28.4811, -48.7819], 'LAURO MULLER': [-28.3928, -49.3958],
        'LEBON REGIS': [-26.9286, -50.6947], 'LEOBERTO LEAL': [-27.4475, -49.2881], 'LONTRAS': [-27.1633, -49.5447],
        'LUIZ ALVES': [-26.7214, -48.9319], 'LUZERNA': [-27.135, -51.46], 'MAFRA': [-26.1153, -49.805],
        'MARAVILHA': [-26.7589, -53.1731], 'MAREMA': [-26.8044, -52.6322], 'MASSARANDUBA': [-26.6114, -49.0086],
        'MATOS COSTA': [-26.4719, -51.1503], 'MELEIRO': [-28.8286, -49.6353], 'MIRIM DOCE': [-27.1956, -50.0764],
        'MODELO': [-26.78, -53.0561], 'MONDAI': [-27.1089, -53.4019], 'MONTE CARLO': [-27.2217, -50.9856],
        'MONTE CASTELO': [-26.4631, -50.2319], 'MORRO DA FUMACA': [-28.6514, -49.2131], 'MORRO GRANDE': [-28.8353, -49.7153],
        'NAVEGANTES': [-26.8897, -48.6519], 'NOVA ERECHIM': [-26.9039, -52.91], 'NOVA ITABERABA': [-26.9406, -52.8122],
        'NOVA TRENTO': [-27.2842, -48.9319], 'NOVA VENEZA': [-28.6361, -49.4986], 'ORLEANS': [-28.3589, -49.2886],
        'OTACILIO COSTA': [-27.4831, -50.115], 'OURO': [-27.34, -51.6186], 'PAIAL': [-27.2536, -52.4947],
        'PAINEL': [-27.9239, -50.1036], 'PALHOCA': [-27.6478, -48.6701], 'PALMA SOLA': [-26.3486, -53.2783],
        'PALMEIRA': [-27.5831, -50.1611], 'PALMITOS': [-27.0675, -53.1619], 'PAPANDUVA': [-26.3686, -50.145],
        'PASSO DE TORRES': [-29.3117, -49.7214], 'PASSOS MAIA': [-26.7781, -52.0583], 'PAULO LOPES': [-27.9622, -48.6833],
        'PEDRAS GRANDES': [-28.4383, -49.19], 'PENHA': [-26.7694, -48.6458], 'PERITIBA': [-27.2403, -51.9056],
        'PESCARIA BRAVA': [-28.3975, -48.8167], 'PETROLANDIA': [-27.5339, -49.7], 'PINHALZINHO': [-26.8483, -52.9922],
        'PINHEIRO PRETO': [-27.0519, -51.2294], 'PIRATUBA': [-27.4122, -51.7761], 'PLANALTO ALEGRE': [-27.0683, -52.8122],
        'POMERODE': [-26.74, -49.1764], 'PONTE ALTA': [-27.4842, -50.3756], 'PONTE ALTA DO NORTE': [-27.1581, -50.5878],
        'PONTE SERRADA': [-26.8719, -52.0153], 'PORTO BELO': [-27.1578, -48.5447], 'PORTO UNIAO': [-26.2378, -51.0872],
        'POUSO REDONDO': [-27.2561, -49.9772], 'PRAIA GRANDE': [-29.1953, -49.9447], 'PRESIDENTE CASTELLO BRANCO': [-27.2217, -51.8083],
        'PRESIDENTE GETULIO': [-27.0506, -49.6247], 'PRESIDENTE NEREU': [-27.2786, -49.3853], 'PRINCESA': [-26.435, -53.6033],
        'QUILOMBO': [-26.7264, -52.7219], 'RANCHO QUEIMADO': [-27.6742, -49.0208], 'RIO DAS ANTAS': [-26.8994, -51.0733],
        'RIO DO CAMPO': [-26.9458, -50.1383], 'RIO DO OESTE': [-27.1919, -49.7947], 'RIO DO SUL': [-27.2156, -49.6436],
        'RIO DOS CEDROS': [-26.7369, -49.2736], 'RIO FORTUNA': [-28.1325, -49.1122], 'RIO NEGRINHO': [-26.2525, -49.4169],
        'RIO RUFINO': [-27.86, -49.78], 'RIQUEZA': [-27.0658, -53.32], 'RODEIO': [-26.9214, -49.3664],
        'ROMELANDIA': [-26.6753, -53.3156], 'SALETE': [-26.9833, -49.9667], 'SALTINHO': [-26.6083, -53.0531],
        'SALTO VELOSO': [-26.905, -51.4069], 'SANGAO': [-28.6328, -49.1297], 'SANTA CECILIA': [-26.7583, -50.4264],
        'SANTA HELENA': [-26.9364, -53.62], 'SANTA ROSA DE LIMA': [-28.0389, -49.1283], 'SANTA ROSA DO SUL': [-29.1417, -49.7119],
        'SANTA TEREZINHA': [-26.78, -50.005], 'SANTA TEREZINHA DO PROGRESSO': [-26.6183, -53.2039], 'SANTIAGO DO SUL': [-26.7483, -52.7306],
        'SANTO AMARO DA IMPERATRIZ': [-27.6881, -48.7783], 'SAO BENTO DO SUL': [-26.25, -49.3794], 'SAO BERNARDINO': [-26.5167, -52.9667],
        'SAO BONIFACIO': [-27.9017, -48.9286], 'SAO CARLOS': [-27.0789, -53.0039], 'SAO CRISTOVAO DO SUL': [-27.2658, -50.4447],
        'SAO DOMINGOS': [-26.5583, -52.53], 'SAO FRANCISCO DO SUL': [-26.2433, -48.6381], 'SAO JOAO BATISTA': [-27.2756, -48.8492],
        'SAO JOAO DO ITAPERIU': [-26.6192, -48.7508], 'SAO JOAO DO OESTE': [-27.0983, -53.5939], 'SAO JOAO DO SUL': [-29.1219, -49.8089],
        'SAO JOAQUIM': [-28.2939, -49.9319], 'SAO JOSE': [-27.6146, -48.6353], 'SAO JOSE DO CEDRO': [-26.4839, -53.4969],
        'SAO JOSE DO CERRITO': [-27.6631, -50.5803], 'SAO LORENCO DO OESTE': [-26.3589, -52.85], 'SAO LUDGERO': [-28.23, -48.8683],
        'SAO MARTINHO': [-28.165, -48.9786], 'SAO MIGUEL DA BOA VISTA': [-26.8767, -53.2439], 'SAO MIGUEL DO OESTE': [-26.7264, -53.5183],
        'SAO PEDRO DE ALCANTARA': [-27.5642, -48.8058], 'SAUDAVEL': [-26.9406, -53.0019], 'SAUDADES': [-26.9242, -53.0039],
        'SCHROEDER': [-26.4114, -49.0733], 'SEARA': [-27.1489, -52.31], 'SERRA ALTA': [-26.7247, -53.0294],
        'SIDEROPOLIS': [-28.5969, -49.4264], 'SOMBRIO': [-29.1139, -49.6169], 'SUL BRASIL': [-26.7369, -52.9547],
        'TAIO': [-27.1158, -49.9983], 'TANGARA': [-27.1061, -51.1897], 'TIGRINHOS': [-26.6872, -53.325],
        'TIJUCAS': [-27.2433, -48.6331], 'TIMBE DO SUL': [-28.83, -49.8469], 'TIMBO': [-26.8242, -49.2711],
        'TROMBUDO CENTRAL': [-27.2989, -49.7914], 'TUBARAO': [-28.4789, -48.9917], 'TUNAPOLIS': [-26.97, -53.64],
        'TURVO': [-28.9261, -49.6786], 'URUBICI': [-28.015, -49.5917], 'URUPEMA': [-27.9575, -49.8658],
        'URUSSANGA': [-28.5186, -49.3217], 'VARGEAO': [-26.8778, -52.1811], 'VARGEM': [-27.4883, -50.9764],
        'VARGEM BONITA': [-27.005, -51.7417], 'VIDAL RAMOS': [-27.3919, -49.355], 'VIDEIRA': [-27.0083, -51.1506],
        'VITOR MEIRELES': [-26.8953, -49.845], 'WITMARSUM': [-26.9272, -49.795], 'XANXERE': [-26.8772, -52.4039],
        'XAVANTINA': [-27.0675, -52.3431], 'XAXIM': [-26.9589, -52.5342], 'ZORTEA': [-27.4519, -51.5511]
    }

@st.cache_data
def load_data(arquivo_nome):
    try:
        df = pd.read_parquet(arquivo_nome)
        df['nm_votavel'] = df['nm_votavel'].astype(str).str.upper().str.strip()
        df['nm_municipio'] = df['nm_municipio'].astype(str).str.upper().str.strip()
        df['nr_votavel'] = df['nr_votavel'].astype(str)
        df['nr_partido'] = df['nr_votavel'].str[:2]
        df['nm_municipio_busca'] = df['nm_municipio'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {arquivo_nome}: {e}")
        return pd.DataFrame()

# --- SIDEBAR ---
st.sidebar.header("🗳️ Configurações")
ano_sel = st.sidebar.radio("Ano em exibição:", ["2018", "2022"])
cargo_sel = st.sidebar.radio("Cargo:", ["Federal", "Estadual"])

tipo_slug = "federal" if cargo_sel == "Federal" else "estadual"
df_atual = load_data(f"dep{tipo_slug}sc{ano_sel}.parquet")
df_18 = load_data(f"dep{tipo_slug}sc2018.parquet")
df_22 = load_data(f"dep{tipo_slug}sc2022.parquet")

st.sidebar.divider()

if not df_atual.empty:
    todos_cands = sorted(df_atual['nm_votavel'].unique())
    cands_sel = st.sidebar.multiselect("👤 Selecionar Candidatos:", todos_cands)
    
    todos_partidos = sorted(df_atual['nr_partido'].unique())
    partidos_sel = st.sidebar.multiselect("🚩 Selecionar Partidos:", todos_partidos)
    
    mun_sel = st.sidebar.selectbox("📍 Filtro de Cidade:", ["TODOS"] + sorted(df_atual['nm_municipio'].unique()))
    share_min = st.sidebar.slider("Exibir no mapa share acima de (%):", 0.0, 100.0, 0.0, step=0.1)

    selecionados_todos = cands_sel + [f"PARTIDO {p}" for p in partidos_sel]
    # Paleta de cores fixa para consistência entre cards e mapa
    CORES_HEX = ["#318ce7", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22"]
    mapa_cores = {item: CORES_HEX[i % len(CORES_HEX)] for i, item in enumerate(selecionados_todos)}

    loc_title = f"em {mun_sel}" if mun_sel != "TODOS" else "no Estado"
    st.title(f"📊 Inteligência: {cargo_sel}")
    st.subheader(f"🏁 Performance Geral {loc_title}")
    
    # --- MÉTRICAS DE TOPO ---
    if selecionados_todos:
        cols_geral = st.columns(len(selecionados_todos))
        for i, item in enumerate(selecionados_todos):
            if item.startswith("PARTIDO "):
                p_num = item.replace("PARTIDO ", "")
                c18_base, c22_base = df_18[df_18['nr_partido'] == p_num], df_22[df_22['nr_partido'] == p_num]
            else:
                c18_base, c22_base = df_18[df_18['nm_votavel'] == item], df_22[df_22['nm_votavel'] == item]
            
            v_18 = c18_base[c18_base['nm_municipio'] == mun_sel]['qt_votos'].sum() if mun_sel != "TODOS" else c18_base['qt_votos'].sum()
            v_22 = c22_base[c22_base['nm_municipio'] == mun_sel]['qt_votos'].sum() if mun_sel != "TODOS" else c22_base['qt_votos'].sum()
            
            dif = v_22 - v_18
            perc = (dif / v_18 * 100) if v_18 > 0 else (100.0 if v_22 > 0 else 0.0)
            
            with cols_geral[i]:
                color_trend = "#28a745" if dif > 0 else ("#dc3545" if dif < 0 else "#6c757d")
                # Cor do nome agora é a mesma do mapa
                st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-top: 5px solid {mapa_cores[item]}; border: 1px solid #ddd;'>
                        <h4 style='margin:0; font-size:14px; color:{mapa_cores[item]};'>{item}</h4>
                        <p style='margin:0; font-size:22px;'><b>{int(v_22):.0f}</b> <small style='font-size:12px; color:gray;'>votos</small></p>
                        <p style='margin:0; color:{color_trend}; font-size:15px; font-weight:bold;'>
                            {'▲' if dif > 0 else ('▼' if dif < 0 else '●')} {abs(int(dif)):.0f} ({perc:.1f}%)
                        </p>
                    </div>
                """, unsafe_allow_html=True)

    st.divider()
    tab_mapa, tab_ganhos, tab_perf, tab_rankings, tab_geral = st.tabs(["🗺️ Mapa de Redutos", "🌡️ Ganhos e Perdas", "🏫 Performance Detalhada", "🏙️ Rankings por Selecionado", "🏆 Ranking Geral"])

    # --- ABA: MAPA ---
    with tab_mapa:
        coords_dict = get_coords_map()
        map_center = [-27.2423, -50.2189]
        zoom = 7
        
        if mun_sel != "TODOS":
            mun_busca = normalizar_texto(mun_sel)
            if mun_busca in coords_dict:
                map_center = coords_dict[mun_busca]
                zoom = 12
        
        m = folium.Map(location=map_center, zoom_start=zoom, tiles="cartodbpositron")
        
        df_m_cands = df_atual[df_atual['nm_votavel'].isin(cands_sel)]
        df_m_partidos = df_atual[df_atual['nr_partido'].isin(partidos_sel)].copy()
        if not df_m_partidos.empty:
            df_m_partidos['nm_votavel'] = "PARTIDO " + df_m_partidos['nr_partido']
        
        df_m = pd.concat([df_m_cands, df_m_partidos])
        
        if mun_sel != "TODOS":
            df_m = df_m[df_m['nm_municipio'] == mun_sel]
            votos_m = df_m.groupby(['nm_municipio', 'nm_local_votacao', 'nm_votavel'])['qt_votos'].sum().reset_index()
            votos_m['nm_municipio_busca'] = votos_m['nm_municipio'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()
        else:
            votos_m = df_m.groupby(['nm_municipio', 'nm_municipio_busca', 'nm_votavel'])['qt_votos'].sum().reset_index()

        if not votos_m.empty:
            total_ref = df_atual.groupby('nm_municipio')['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'total_mun'})
            votos_m = pd.merge(votos_m, total_ref, on='nm_municipio')
            votos_m['share'] = (votos_m['qt_votos'] / votos_m['total_mun']) * 100
            votos_m = votos_m[votos_m['share'] >= share_min]

            for _, linha in votos_m.iterrows():
                if linha['nm_municipio_busca'] in coords_dict:
                    lat, lon = coords_dict[linha['nm_municipio_busca']]
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=max(5, min((linha['qt_votos']**0.5)*0.8, 30)),
                        color=mapa_cores.get(linha['nm_votavel'], "#318ce7"),
                        fill=True, fill_opacity=0.6,
                        popup=f"<b>{linha['nm_votavel']}</b><br>{linha['nm_municipio']}<br>Votos: {int(linha['qt_votos'])}<br>Share: {linha['share']:.2f}%"
                    ).add_to(m)
        st_folium(m, width=1200, height=500)

    # --- ABA: GANHOS E PERDAS ---
    with tab_ganhos:
        st.subheader(f"🌡️ Comparativo 2018 vs 2022")
        eixo = 'nm_municipio' if mun_sel == "TODOS" else 'nm_local_votacao'
        for item in selecionados_todos:
            st.write(f"#### {item}")
            if item.startswith("PARTIDO "):
                p_num = item.replace("PARTIDO ", "")
                c18, c22 = df_18[df_18['nr_partido'] == p_num], df_22[df_22['nr_partido'] == p_num]
            else:
                c18, c22 = df_18[df_18['nm_votavel'] == item], df_22[df_22['nm_votavel'] == item]

            if mun_sel != "TODOS":
                c18, c22 = c18[c18['nm_municipio'] == mun_sel], c22[c22['nm_municipio'] == mun_sel]
            
            v18 = c18.groupby(eixo)['qt_votos'].sum().reset_index()
            v22 = c22.groupby(eixo)['qt_votos'].sum().reset_index()
            comp = pd.merge(v18, v22, on=eixo, how='outer', suffixes=('_18', '_22')).fillna(0)
            comp['Saldo'] = comp['qt_votos_22'] - comp['qt_votos_18']
            comp = comp.sort_values('Saldo', ascending=False)
            
            comp = comp.rename(columns={eixo: "Localidade" if eixo=='nm_municipio' else "Local de Votação", 
                                        "qt_votos_18": "Votos 2018", "qt_votos_22": "Votos 2022"})
            
            st.dataframe(comp.style.format({"Votos 2018": "{:.0f}", "Votos 2022": "{:.0f}", "Saldo": "{:.0f}"})
                         .applymap(lambda x: 'color: #28a745; font-weight: bold' if x > 0 else 'color: #dc3545', subset=['Saldo']), 
                         use_container_width=True, hide_index=True)

    # --- ABA: PERFORMANCE DETALHADA (DINÂMICA) ---
    with tab_perf:
        tipo_perf = "Cidades" if mun_sel == "TODOS" else "Locais de Votação"
        st.subheader(f"📊 Market Share por {tipo_perf}")
        
        df_perf = df_atual.copy()
        # Define o nível de agrupamento
        grupo_cols = ['nm_municipio'] if mun_sel == "TODOS" else ['nm_municipio', 'nm_local_votacao']
        
        if mun_sel != "TODOS": 
            df_perf = df_perf[df_perf['nm_municipio'] == mun_sel]
        
        totais_local = df_perf.groupby(grupo_cols)['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'total_votos'})
        
        df_sel_c = df_perf[df_perf['nm_votavel'].isin(cands_sel)]
        df_sel_p = df_perf[df_perf['nr_partido'].isin(partidos_sel)].copy()
        if not df_sel_p.empty: df_sel_p['nm_votavel'] = "PARTIDO " + df_sel_p['nr_partido']
        
        df_final_sel = pd.concat([df_sel_c, df_sel_p])

        if not df_final_sel.empty:
            pivot_perf = df_final_sel.pivot_table(index=grupo_cols, columns='nm_votavel', values='qt_votos', aggfunc='sum', fill_value=0).reset_index()
            df_res_perf = pd.merge(pivot_perf, totais_local, on=grupo_cols)
            
            config_cols = {"nm_municipio": "Cidade", "nm_local_votacao": "Local de Votação", "total_votos": "Votos Totais"}
            for item in selecionados_todos:
                if item in df_res_perf.columns:
                    col_pct = f"% {item}"
                    df_res_perf[col_pct] = (df_res_perf[item] / df_res_perf['total_votos']) * 100
                    config_cols[col_pct] = st.column_config.ProgressColumn(col_pct, format="%.2f%%", min_value=0, max_value=100)
                    config_cols[item] = st.column_config.NumberColumn(f"Votos {item}", format="%d")
            
            # Ordenar pelo primeiro selecionado
            sort_col = selecionados_todos[0] if selecionados_todos else grupo_cols[0]
            st.dataframe(df_res_perf.sort_values(sort_col, ascending=False), 
                         use_container_width=True, hide_index=True, column_config=config_cols)
        else:
            st.info("Selecione candidatos ou partidos na barra lateral para ver a performance detalhada.")

    # --- ABA: RANKINGS POR SELECIONADO ---
    with tab_rankings:
        titulo_rank = f"🏙️ Top 10 Cidades" if mun_sel == "TODOS" else f"🏫 Top 10 Escolas em {mun_sel}"
        st.subheader(titulo_rank)
        
        if selecionados_todos:
            criterio = st.radio("Ordenar por:", ["Votos Brutos", "Market Share (%)"], horizontal=True, key="rank_sel_new")
            c_cols = st.columns(len(selecionados_todos))
            
            for i, item in enumerate(selecionados_todos):
                with c_cols[i]:
                    st.markdown(f"**📍 {item}**")
                    df_base_rank = df_atual.copy()
                    col_agrupamento = 'nm_municipio'
                    col_label = "Cidade"
                    
                    if mun_sel != "TODOS":
                        df_base_rank = df_base_rank[df_base_rank['nm_municipio'] == mun_sel]
                        col_agrupamento = 'nm_local_votacao'
                        col_label = "Local de Votação"
                    
                    if item.startswith("PARTIDO "):
                        p_num = item.replace("PARTIDO ", "")
                        cand_df = df_base_rank[df_base_rank['nr_partido'] == p_num].groupby(col_agrupamento)['qt_votos'].sum().reset_index()
                    else:
                        cand_df = df_base_rank[df_base_rank['nm_votavel'] == item].groupby(col_agrupamento)['qt_votos'].sum().reset_index()
                    
                    total_df = df_base_rank.groupby(col_agrupamento)['qt_votos'].sum().reset_index()
                    top_10 = pd.merge(cand_df, total_df, on=col_agrupamento, suffixes=('_c', '_t'))
                    top_10['Share %'] = (top_10['qt_votos_c'] / top_10['qt_votos_t']) * 100
                    top_10 = top_10.sort_values('qt_votos_c' if criterio == "Votos Brutos" else 'Share %', ascending=False).head(10)
                    
                    top_10_view = top_10[[col_agrupamento, 'qt_votos_c', 'Share %']].rename(columns={col_agrupamento: col_label, 'qt_votos_c': 'Votos'})
                    st.dataframe(top_10_view, hide_index=True, column_config={
                        "Votos": st.column_config.NumberColumn(format="%d"),
                        "Share %": st.column_config.NumberColumn(format="%.2f%%")
                    })

    # --- ABA: RANKING GERAL DO LOCAL ---
    with tab_geral:
        st.subheader(f"🏆 Ranking Geral: {loc_title}")
        df_local = df_atual.copy()
        if mun_sel != "TODOS":
            df_local = df_local[df_local['nm_municipio'] == mun_sel]
        
        total_votos_local = df_local['qt_votos'].sum()
        col_rank1, col_rank2 = st.columns(2)
        
        with col_rank1:
            st.markdown("#### 👤 Deputados Mais Votados")
            ranking_cands = df_local.groupby('nm_votavel')['qt_votos'].sum().reset_index()
            ranking_cands = ranking_cands.sort_values('qt_votos', ascending=False).reset_index(drop=True)
            ranking_cands.index += 1
            ranking_cands['Share %'] = (ranking_cands['qt_votos'] / total_votos_local) * 100
            
            def highlight_sel(row):
                return ['background-color: #fff3cd' if row['nm_votavel'] in cands_sel else '' for _ in row]
            
            st.dataframe(
                ranking_cands.head(20).style.format({'qt_votos': '{:,.0f}', 'Share %': '{:.2f}%'}).apply(highlight_sel, axis=1),
                column_config={"nm_votavel": "Candidato", "qt_votos": "Votos"},
                use_container_width=True
            )
            
            if cands_sel:
                st.markdown("##### 📍 Posição dos seus Selecionados:")
                for c in cands_sel:
                    try:
                        pos = ranking_cands[ranking_cands['nm_votavel'] == c].index[0]
                        vts = ranking_cands.loc[pos, 'qt_votos']
                        st.write(f"- **{c}**: {pos}º lugar ({int(vts)} votos)")
                    except:
                        st.write(f"- **{c}**: Não obteve votos neste local.")

        with col_rank2:
            st.markdown("#### 🚩 Partidos Mais Votados")
            ranking_partidos = df_local.groupby('nr_partido')['qt_votos'].sum().reset_index()
            ranking_partidos = ranking_partidos.sort_values('qt_votos', ascending=False).reset_index(drop=True)
            ranking_partidos.index += 1
            ranking_partidos['Share %'] = (ranking_partidos['qt_votos'] / total_votos_local) * 100
            
            def highlight_part(row):
                return ['background-color: #d1ecf1' if row['nr_partido'] in partidos_sel else '' for _ in row]

            st.dataframe(
                ranking_partidos.style.format({'qt_votos': '{:,.0f}', 'Share %': '{:.2f}%'}).apply(highlight_part, axis=1),
                column_config={"nr_partido": "Partido", "qt_votos": "Votos Totais"},
                use_container_width=True
            )