import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

st.set_page_config(page_title="Inteligência Eleitoral Pro", layout="wide")

# CSS para customização visual
st.markdown("""
    <style>
    span[data-baseweb="tag"] { background-color: #555555 !important; color: white !important; }
    .metric-azul { color: #1f77b4; font-weight: bold; font-size: 1.2rem; }
    .metric-vermelha { color: #d62728; font-weight: bold; font-size: 1.2rem; }
    .metric-verde { color: #2ca02c; font-weight: bold; font-size: 1.2rem; }
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #f0f2f6; color: #31333f; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('votacao_local_votacao-uf_2022_sc_presidente.csv', sep=';', encoding='latin-1', low_memory=False)
    df['nm_votavel'] = df['nm_votavel'].astype(str).str.upper().str.strip()
    df['nm_municipio'] = df['nm_municipio'].astype(str).str.upper().str.strip()
    df['nm_municipio_busca'] = df['nm_municipio'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()
    return df

@st.cache_data
def load_coords():
    url = "https://raw.githubusercontent.com/kelvins/Municipios-Brasileiros/main/csv/municipios.csv"
    municipios = pd.read_csv(url)
    sc = municipios[municipios['codigo_uf'] == 42].copy()
    sc['nome_busca'] = sc['nome'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()
    return sc

try:
    df = load_data()
    coords_df = load_coords()

    st.title("🚀 Painel de Inteligência Estratégica Eleitoral")
    
    # --- BARRA LATERAL ---
    st.sidebar.header("🎯 Filtros")
    lista_candidatos = sorted(df['nm_votavel'].unique())
    selecionados = st.sidebar.multiselect("Selecione até 3 candidatos:", lista_candidatos, default=[lista_candidatos[0]], max_selections=3)
    
    cores_hex = ["#1f77b4", "#d62728", "#2ca02c"]
    lista_cidades = sorted(df['nm_municipio'].unique())
    cidade_foco = st.sidebar.selectbox("Focar Município:", ["TODAS"] + lista_cidades)

    if not selecionados:
        st.warning("Selecione os candidatos na barra lateral.")
    else:
        df_contexto = df if cidade_foco == "TODAS" else df[df['nm_municipio'] == cidade_foco]

        # --- MÉTRICAS ---
        cols_met = st.columns(len(selecionados))
        classes_css = ["metric-azul", "metric-vermelha", "metric-verde"]
        for idx, cand in enumerate(selecionados):
            v_loc = df_contexto[df_contexto['nm_votavel'] == cand]['qt_votos'].sum()
            cols_met[idx].markdown(f"<p class='{classes_css[idx]}'>{cand}</p>", unsafe_allow_html=True)
            cols_met[idx].metric(f"Total de Votos", f"{int(v_loc):,}".replace(',', '.'))

        # --- ABAS ---
        tab_mapa, tab_detalhe = st.tabs(["🗺️ Mapa e Rankings", "📊 Detalhamento por Escola"])

        with tab_mapa:
            col_esq, col_dir = st.columns([7, 3])

            with col_esq:
                # Lógica do Mapa
                votos_mapa = df_contexto[df_contexto['nm_votavel'].isin(selecionados)].groupby(['nm_municipio', 'nm_votavel'])['qt_votos'].sum().unstack(fill_value=0).reset_index()
                votos_mapa['nm_municipio_busca'] = votos_mapa['nm_municipio'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()
                df_mapa = pd.merge(votos_mapa, coords_df, left_on='nm_municipio_busca', right_on='nome_busca')

                lat_ini, lon_ini, zoom_ini = -27.2423, -50.2189, 7
                if cidade_foco != "TODAS":
                    c_limpa = pd.Series([cidade_foco]).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()[0]
                    foco = coords_df[coords_df['nome_busca'] == c_limpa]
                    if not foco.empty:
                        lat_ini, lon_ini, zoom_ini = foco.iloc[0]['latitude'], foco.iloc[0]['longitude'], 12

                m = folium.Map(location=[lat_ini, lon_ini], zoom_start=zoom_ini, tiles="cartodbpositron")
                
                # Se for cidade específica, vamos plotar os pontos das escolas se houver coordenadas (opcional)
                # Por enquanto, mantemos a lógica de círculos por município para estabilidade
                for _, row in df_mapa.iterrows():
                    v_dict = {c: row[c] for c in selecionados if c in row}
                    if v_dict:
                        lider = max(v_dict, key=v_dict.get)
                        total_votos_local = sum(v_dict.values())
                        raio = max(min(math.sqrt(total_votos_local) * 0.15, 40), 3)
                        folium.CircleMarker(
                            location=[row['latitude'], row['longitude']],
                            radius=raio, color=cores_hex[selecionados.index(lider)], fill=True, fill_opacity=0.65, weight=1,
                            popup=f"<b>{row['nome']}</b><br>Votos: {int(total_votos_local)}"
                        ).add_to(m)
                st_folium(m, width=800, height=600, key=f"mapa_final_{cidade_foco}")

            with col_dir:
                if cidade_foco == "TODAS":
                    st.markdown("### 🏆 Top 10 Municípios")
                    for idx, cand in enumerate(selecionados):
                        st.markdown(f"<p class='{classes_css[idx]}'>{cand}</p>", unsafe_allow_html=True)
                        top_res = df[df['nm_votavel'] == cand].groupby('nm_municipio')['qt_votos'].sum().nlargest(10).reset_index()
                        top_res.columns = ['Município', 'Votos']
                        top_res['Votos'] = top_res['Votos'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
                        top_res.index = [""] * len(top_res)
                        st.table(top_res)
                else:
                    st.markdown(f"### 🏫 Top 10 Escolas\n**({cidade_foco})**")
                    for idx, cand in enumerate(selecionados):
                        st.markdown(f"<p class='{classes_css[idx]}'>{cand}</p>", unsafe_allow_html=True)
                        top_esc = df_contexto[df_contexto['nm_votavel'] == cand].groupby('nm_local_votacao')['qt_votos'].sum().nlargest(10).reset_index()
                        top_esc.columns = ['Escola/Local', 'Votos']
                        top_esc['Votos'] = top_esc['Votos'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
                        top_esc.index = [""] * len(top_esc)
                        st.table(top_esc)

        with tab_detalhe:
            st.subheader(f"📍 Votos Detalhados por Localidade")
            df_resumo = df_contexto[df_contexto['nm_votavel'].isin(selecionados)].groupby(['nm_municipio', 'nm_local_votacao', 'nm_votavel'])['qt_votos'].sum().reset_index()
            tabela_escolas = df_resumo.pivot_table(index=['nm_municipio', 'nm_local_votacao'], columns='nm_votavel', values='qt_votos', fill_value=0).reset_index()
            
            venc_idx = df_contexto.groupby(['nm_municipio', 'nm_local_votacao'])['qt_votos'].idxmax()
            venc_df = df_contexto.loc[venc_idx, ['nm_municipio', 'nm_local_votacao', 'nm_votavel', 'qt_votos']].rename(
                columns={'nm_votavel': 'Vencedor Local', 'qt_votos': 'Votos do Vencedor'}
            )

            resultado = pd.merge(tabela_escolas, venc_df, on=['nm_municipio', 'nm_local_votacao'], how='left')
            resultado = resultado.rename(columns={'nm_municipio': 'Município', 'nm_local_votacao': 'Local de Votação'})

            for col in selecionados:
                resultado[col] = resultado[col].astype(int)
            resultado['Votos do Vencedor'] = resultado['Votos do Vencedor'].astype(int)
            resultado = resultado.sort_values(by=selecionados[0], ascending=False)

            if not resultado.empty:
                st.write(f"📊 Exibindo **{len(resultado)}** locais de votação:")
                resultado_visual = resultado.head(100).copy()
                resultado_visual.index = [""] * len(resultado_visual)
                st.table(resultado_visual)
                
                csv = resultado.to_csv(index=False, sep=';', encoding='latin-1')
                st.download_button("📥 Baixar Planilha Completa", csv, f"detalhe_{cidade_foco}.csv", "text/csv")

except Exception as e:
    st.error(f"Erro no sistema: {e}")