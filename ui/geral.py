import streamlit as st


def render(df_atual, cands_sel, partidos_sel, mun_sel, loc_title):
    st.subheader(f"🏆 Ranking Geral: {loc_title}")

    df_local = df_atual.copy()
    if mun_sel != "TODOS":
        df_local = df_local[df_local['nm_municipio'] == mun_sel]

    total_votos_local = df_local['qt_votos'].sum()
    col_rank1, col_rank2 = st.columns(2)

    with col_rank1:
        st.markdown("#### 👤 Deputados Mais Votados")
        ranking_cands = (df_local.groupby('nm_votavel')['qt_votos'].sum()
                         .reset_index()
                         .sort_values('qt_votos', ascending=False)
                         .reset_index(drop=True))
        ranking_cands.index += 1
        ranking_cands['Share %'] = (ranking_cands['qt_votos'] / total_votos_local) * 100

        def highlight_sel(row):
            return ['background-color: #fff3cd' if row['nm_votavel'] in cands_sel else '' for _ in row]

        st.dataframe(
            ranking_cands.head(20).style
                .format({'qt_votos': '{:,.0f}', 'Share %': '{:.2f}%'})
                .apply(highlight_sel, axis=1),
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
                except IndexError:
                    st.write(f"- **{c}**: Não obteve votos neste local.")

    with col_rank2:
        st.markdown("#### 🚩 Partidos Mais Votados")
        ranking_partidos = (df_local.groupby('nr_partido')['qt_votos'].sum()
                            .reset_index()
                            .sort_values('qt_votos', ascending=False)
                            .reset_index(drop=True))
        ranking_partidos.index += 1
        ranking_partidos['Share %'] = (ranking_partidos['qt_votos'] / total_votos_local) * 100

        def highlight_part(row):
            return ['background-color: #d1ecf1' if row['nr_partido'] in partidos_sel else '' for _ in row]

        st.dataframe(
            ranking_partidos.style
                .format({'qt_votos': '{:,.0f}', 'Share %': '{:.2f}%'})
                .apply(highlight_part, axis=1),
            column_config={"nr_partido": "Partido", "qt_votos": "Votos Totais"},
            use_container_width=True
        )
