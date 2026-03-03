import unicodedata
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from analysis.metrics import filtrar_por_item


def normalizar(texto):
    if not texto:
        return ""
    return "".join(c for c in unicodedata.normalize('NFKD', str(texto))
                   if unicodedata.category(c) != 'Mn').upper().strip()


@st.cache_data(show_spinner="Baixando mapa dos municípios...")
def carregar_geojson():
    """
    Tenta baixar o GeoJSON dos municípios de SC de múltiplas fontes.
    Retorna (geojson, nome_field) ou (None, None) em caso de falha.
    """
    fontes = [
        {
            "url": "https://servicodados.ibge.gov.br/api/v3/malhas/estados/42?intrarregiao=municipio&formato=application/vnd.geo+json",
            "campos": ["NM_MUN", "name", "NOME", "nm_mun", "municipio"]
        },
        {
            # Repositório público com GeoJSON dos municípios brasileiros por estado
            "url": "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-42-mun.json",
            "campos": ["name", "NM_MUN", "NOME"]
        },
    ]

    for fonte in fontes:
        try:
            resp = requests.get(fonte["url"], timeout=30)
            resp.raise_for_status()
            data = resp.json()
            features = data.get('features', [])
            if not features:
                continue

            # Detectar qual campo contém o nome do município
            sample_props = features[0].get('properties', {})
            nome_field = None
            for campo in fonte["campos"]:
                if campo in sample_props and sample_props[campo]:
                    nome_field = campo
                    break

            if not nome_field:
                # Tentar qualquer campo de string com conteúdo útil
                for k, v in sample_props.items():
                    if isinstance(v, str) and len(v) > 3 and not v.isdigit():
                        nome_field = k
                        break

            if not nome_field:
                continue

            # Normalizar e injetar 'id' em cada feature para o join com plotly
            for feature in features:
                props = feature.get('properties', {})
                nome_orig = props.get(nome_field, '')
                nome_norm = normalizar(nome_orig)
                feature['id'] = nome_norm
                feature['properties']['_nome_norm'] = nome_norm
                feature['properties']['_nome_orig'] = nome_orig

            # Verificar se normalizou corretamente (pelo menos alguns nomes não vazios)
            nomes = [f['properties']['_nome_norm'] for f in features if f['properties']['_nome_norm']]
            if len(nomes) < 10:
                continue

            return data, nome_field

        except Exception:
            continue

    return None, None


def render(df_atual, cands_sel, partidos_sel, selecionados_todos, mun_sel, mapa_cores):
    st.subheader("🌈 Mapa Coroplético — Intensidade por Município")
    st.caption("Quanto mais escura a cor, maior o share do candidato/partido naquele município.")

    if not selecionados_todos:
        st.info("Selecione candidatos ou partidos na barra lateral.")
        return

    if mun_sel != "TODOS":
        st.info("O mapa coroplético exibe todo o estado. Remova o filtro de cidade para visualizá-lo.")
        return

    geojson, nome_field = carregar_geojson()

    if geojson is None:
        st.error("❌ Não foi possível baixar o mapa. Verifique sua conexão com a internet.")
        return

    item_sel = st.selectbox(
        "Selecione o candidato/partido para visualizar no mapa:",
        selecionados_todos,
        key="coropletico_item"
    )

    # Calcular share por município
    filtrado    = filtrar_por_item(df_atual, item_sel)
    votos_cand  = filtrado.groupby('nm_municipio')['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'votos_cand'})
    votos_total = df_atual.groupby('nm_municipio')['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'votos_total'})

    df_mapa = pd.merge(votos_cand, votos_total, on='nm_municipio')
    df_mapa['Share (%)'] = (df_mapa['votos_cand'] / df_mapa['votos_total'] * 100).round(2)
    df_mapa['nm_norm']   = df_mapa['nm_municipio'].apply(normalizar)

    # Verificar match
    nomes_geojson = {f['properties'].get('_nome_norm', '') for f in geojson.get('features', [])}
    matches = df_mapa['nm_norm'].isin(nomes_geojson).sum()
    total   = len(df_mapa)

    if matches == 0:
        st.warning("⚠️ Nenhum município foi identificado no mapa.")
        with st.expander("🔍 Diagnóstico"):
            st.write("**Nomes nos dados eleitorais (primeiros 5):**")
            st.code(df_mapa['nm_norm'].head(5).tolist())
            st.write("**Nomes no GeoJSON (primeiros 5):**")
            st.code(sorted(nomes_geojson)[:5])
            st.write(f"**Campo de nome detectado:** `{nome_field}`")
            st.write("**Propriedades da 1ª feature:**")
            st.json(geojson['features'][0].get('properties', {}))
        return

    pct = matches / total * 100
    if pct < 80:
        st.warning(f"⚠️ {matches} de {total} municípios identificados ({pct:.0f}%). Alguns ficarão sem cor.")
    else:
        st.caption(f"✅ {matches} de {total} municípios identificados no mapa.")

    cor_hex = mapa_cores.get(item_sel, "#318ce7")

    fig = px.choropleth(
        df_mapa,
        geojson=geojson,
        locations='nm_norm',
        color='Share (%)',
        color_continuous_scale=[[0, "#f0f4ff"], [1, cor_hex]],
        hover_name='nm_municipio',
        hover_data={
            'votos_cand':  ':,.0f',
            'votos_total': ':,.0f',
            'Share (%)':   ':.2f',
            'nm_norm':     False
        },
        labels={'votos_cand': 'Votos', 'votos_total': 'Total de Votos'},
        title=f"Share de {item_sel} por Município — SC"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="Share (%)")
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela complementar
    st.markdown("#### 📋 Dados por Município")
    st.dataframe(
        df_mapa[['nm_municipio', 'votos_cand', 'votos_total', 'Share (%)' ]]
            .sort_values('Share (%)', ascending=False)
            .rename(columns={
                'nm_municipio': 'Município',
                'votos_cand':   'Votos Candidato',
                'votos_total':  'Total Votos'
            }),
        use_container_width=True, hide_index=True,
        column_config={
            'Votos Candidato': st.column_config.NumberColumn(format="%d"),
            'Total Votos':     st.column_config.NumberColumn(format="%d"),
            'Share (%)':       st.column_config.ProgressColumn(format="%.2f%%", min_value=0, max_value=100)
        }
    )
