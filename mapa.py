import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from analysis.metrics import filtrar_por_item


def render(df_atual, cands_sel, partidos_sel, mun_sel, share_min, mapa_cores, coords_dict, normalizar_texto):
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
        votos_m['nm_municipio_busca'] = (votos_m['nm_municipio']
                                         .str.normalize('NFKD')
                                         .str.encode('ascii', errors='ignore')
                                         .str.decode('utf-8')
                                         .str.upper())
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
                    radius=max(5, min((linha['qt_votos'] ** 0.5) * 0.8, 30)),
                    color=mapa_cores.get(linha['nm_votavel'], "#318ce7"),
                    fill=True, fill_opacity=0.6,
                    popup=f"<b>{linha['nm_votavel']}</b><br>{linha['nm_municipio']}<br>Votos: {int(linha['qt_votos'])}<br>Share: {linha['share']:.2f}%"
                ).add_to(m)

    st_folium(m, width=1200, height=500)
