import io
import streamlit as st
import pandas as pd


def render(df_atual, cands_sel, partidos_sel, selecionados_todos, mun_sel):
    tipo_perf = "Cidades" if mun_sel == "TODOS" else "Locais de Votação"
    st.subheader(f"📊 Market Share por {tipo_perf}")

    df_perf = df_atual.copy()
    grupo_cols = ['nm_municipio'] if mun_sel == "TODOS" else ['nm_municipio', 'nm_local_votacao']

    if mun_sel != "TODOS":
        df_perf = df_perf[df_perf['nm_municipio'] == mun_sel]

    totais_local = (df_perf.groupby(grupo_cols)['qt_votos'].sum()
                    .reset_index().rename(columns={'qt_votos': 'total_votos'}))

    df_sel_c = df_perf[df_perf['nm_votavel'].isin(cands_sel)]
    df_sel_p = df_perf[df_perf['nr_partido'].isin(partidos_sel)].copy()
    if not df_sel_p.empty:
        df_sel_p['nm_votavel'] = "PARTIDO " + df_sel_p['nr_partido']

    df_final_sel = pd.concat([df_sel_c, df_sel_p])

    if not df_final_sel.empty:
        pivot_perf = df_final_sel.pivot_table(
            index=grupo_cols, columns='nm_votavel',
            values='qt_votos', aggfunc='sum', fill_value=0
        ).reset_index()
        df_res_perf = pd.merge(pivot_perf, totais_local, on=grupo_cols)

        config_cols = {
            "nm_municipio": "Cidade",
            "nm_local_votacao": "Local de Votação",
            "total_votos": "Votos Totais"
        }
        for item in selecionados_todos:
            if item in df_res_perf.columns:
                col_pct = f"% {item}"
                df_res_perf[col_pct] = (df_res_perf[item] / df_res_perf['total_votos']) * 100
                config_cols[col_pct] = st.column_config.ProgressColumn(col_pct, format="%.2f%%", min_value=0, max_value=100)
                config_cols[item] = st.column_config.NumberColumn(f"Votos {item}", format="%d")

        sort_col = selecionados_todos[0] if selecionados_todos else grupo_cols[0]
        st.dataframe(
            df_res_perf.sort_values(sort_col, ascending=False),
            use_container_width=True, hide_index=True, column_config=config_cols
        )

        # Botão de exportação
        buffer = io.BytesIO()
        df_res_perf.to_excel(buffer, index=False, engine='openpyxl')
        st.download_button(
            label="💾 Baixar Excel — Performance Detalhada",
            data=buffer.getvalue(),
            file_name="performance_detalhada.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_performance"
        )
    else:
        st.info("Selecione candidatos ou partidos na barra lateral para ver a performance detalhada.")
