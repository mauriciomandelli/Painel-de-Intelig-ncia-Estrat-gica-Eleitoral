import streamlit as st
import pandas as pd
from analysis.metrics import filtrar_por_item


def render(df_atual, selecionados_todos, mun_sel):
    titulo_rank = "🏙️ Top 10 Cidades" if mun_sel == "TODOS" else f"🏫 Top 10 Escolas em {mun_sel}"
    st.subheader(titulo_rank)

    if not selecionados_todos:
        st.info("Selecione candidatos ou partidos na barra lateral.")
        return

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

            cand_df = filtrar_por_item(df_base_rank, item).groupby(col_agrupamento)['qt_votos'].sum().reset_index()
            total_df = df_base_rank.groupby(col_agrupamento)['qt_votos'].sum().reset_index()

            top_10 = pd.merge(cand_df, total_df, on=col_agrupamento, suffixes=('_c', '_t'))
            top_10['Share %'] = (top_10['qt_votos_c'] / top_10['qt_votos_t']) * 100
            top_10 = top_10.sort_values(
                'qt_votos_c' if criterio == "Votos Brutos" else 'Share %', ascending=False
            ).head(10)

            top_10_view = top_10[[col_agrupamento, 'qt_votos_c', 'Share %']].rename(
                columns={col_agrupamento: col_label, 'qt_votos_c': 'Votos'}
            )
            st.dataframe(top_10_view, hide_index=True, column_config={
                "Votos": st.column_config.NumberColumn(format="%d"),
                "Share %": st.column_config.NumberColumn(format="%.2f%%")
            })
