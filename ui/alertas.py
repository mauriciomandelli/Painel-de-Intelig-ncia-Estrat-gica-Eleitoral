import io
import streamlit as st
import pandas as pd
from analysis.metrics import filtrar_por_item


def render(df_18, df_22, selecionados_todos, mun_sel):
    st.subheader("🔍 Alertas de Oportunidade")
    st.caption("Municípios onde o candidato cresceu muito em votos, mas o market share ainda é baixo — indicando potencial inexplorado.")

    if not selecionados_todos:
        st.info("Selecione candidatos ou partidos na barra lateral.")
        return

    col1, col2 = st.columns(2)
    with col1:
        crescimento_min = st.slider("Crescimento mínimo de votos (%):", 10, 200, 30, step=10, key="alerta_cresc")
    with col2:
        share_max = st.slider("Share máximo no município (%):", 1.0, 30.0, 15.0, step=0.5, key="alerta_share")

    eixo = 'nm_municipio' if mun_sel == "TODOS" else 'nm_local_votacao'
    label_eixo = "Cidade" if mun_sel == "TODOS" else "Local de Votação"

    for item in selecionados_todos:
        st.markdown(f"---\n#### 📍 {item}")

        c18 = filtrar_por_item(df_18, item)
        c22 = filtrar_por_item(df_22, item)

        if mun_sel != "TODOS":
            c18 = c18[c18['nm_municipio'] == mun_sel]
            c22 = c22[c22['nm_municipio'] == mun_sel]

        v18 = c18.groupby(eixo)['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'votos_18'})
        v22 = c22.groupby(eixo)['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'votos_22'})

        comp = v18.merge(v22, on=eixo, how='outer').fillna(0)
        comp['Crescimento (%)'] = comp.apply(
            lambda r: ((r['votos_22'] - r['votos_18']) / r['votos_18'] * 100) if r['votos_18'] > 0 else 0, axis=1
        )

        # Calcular share de 2022
        if mun_sel == "TODOS":
            total_22 = df_22.groupby('nm_municipio')['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'total_mun', 'nm_municipio': eixo})
        else:
            total_22 = df_22[df_22['nm_municipio'] == mun_sel].groupby(eixo)['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'total_mun'})

        comp = comp.merge(total_22, on=eixo, how='left')
        comp['Share 2022 (%)'] = (comp['votos_22'] / comp['total_mun'] * 100).fillna(0)

        # Filtrar alertas
        alertas = comp[
            (comp['Crescimento (%)'] >= crescimento_min) &
            (comp['Share 2022 (%)'] <= share_max) &
            (comp['votos_22'] > 0)
        ].sort_values('Crescimento (%)', ascending=False)

        alertas = alertas.rename(columns={
            eixo: label_eixo,
            'votos_18': 'Votos 2018',
            'votos_22': 'Votos 2022'
        })

        if alertas.empty:
            st.info(f"Nenhum município encontrado com os critérios selecionados para **{item}**.")
        else:
            st.success(f"✅ {len(alertas)} municípios encontrados!")
            st.dataframe(
                alertas[[label_eixo, 'Votos 2018', 'Votos 2022', 'Crescimento (%)', 'Share 2022 (%)']].style
                    .format({
                        'Votos 2018': '{:.0f}', 'Votos 2022': '{:.0f}',
                        'Crescimento (%)': '{:.1f}%', 'Share 2022 (%)': '{:.2f}%'
                    })
                    .map(lambda x: 'color: #28a745; font-weight: bold' if isinstance(x, float) and x >= crescimento_min else '', subset=['Crescimento (%)']),
                use_container_width=True, hide_index=True
            )

            buffer = io.BytesIO()
            alertas.to_excel(buffer, index=False, engine='openpyxl')
            st.download_button(
                label=f"💾 Baixar Excel — Alertas {item}",
                data=buffer.getvalue(),
                file_name=f"alertas_{item.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_alertas_{item}"
            )
