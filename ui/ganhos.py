import io
import streamlit as st
import pandas as pd
from analysis.metrics import filtrar_por_item


def render(df_18, df_22, selecionados_todos, mun_sel):
    st.subheader("🌡️ Comparativo 2018 vs 2022")
    eixo = 'nm_municipio' if mun_sel == "TODOS" else 'nm_local_votacao'

    for item in selecionados_todos:
        st.write(f"#### {item}")
        c18 = filtrar_por_item(df_18, item)
        c22 = filtrar_por_item(df_22, item)

        if mun_sel != "TODOS":
            c18 = c18[c18['nm_municipio'] == mun_sel]
            c22 = c22[c22['nm_municipio'] == mun_sel]

        v18 = c18.groupby(eixo)['qt_votos'].sum().reset_index()
        v22 = c22.groupby(eixo)['qt_votos'].sum().reset_index()

        comp = v18.merge(v22, on=eixo, how='outer', suffixes=('_18', '_22')).fillna(0)
        comp['Saldo'] = comp['qt_votos_22'] - comp['qt_votos_18']
        comp = comp.sort_values('Saldo', ascending=False)
        comp = comp.rename(columns={
            eixo: "Localidade" if eixo == 'nm_municipio' else "Local de Votação",
            "qt_votos_18": "Votos 2018",
            "qt_votos_22": "Votos 2022"
        })

        st.dataframe(
            comp.style
                .format({"Votos 2018": "{:.0f}", "Votos 2022": "{:.0f}", "Saldo": "{:.0f}"})
                .map(lambda x: 'color: #28a745; font-weight: bold' if x > 0 else 'color: #dc3545', subset=['Saldo']),
            use_container_width=True, hide_index=True
        )

        # Botão de exportação
        buffer = io.BytesIO()
        comp.to_excel(buffer, index=False, engine='openpyxl')
        st.download_button(
            label=f"💾 Baixar Excel — {item}",
            data=buffer.getvalue(),
            file_name=f"ganhos_perdas_{item.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_ganhos_{item}"
        )
