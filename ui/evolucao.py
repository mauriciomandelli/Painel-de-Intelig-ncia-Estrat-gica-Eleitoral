import io
import streamlit as st
import pandas as pd
import plotly.express as px
from analysis.metrics import filtrar_por_item


def render(df_18, df_22, selecionados_todos, mun_sel, mapa_cores):
    st.subheader("📈 Evolução de Votos: 2018 → 2022")

    if not selecionados_todos:
        st.info("Selecione candidatos ou partidos na barra lateral.")
        return

    eixo = 'nm_municipio' if mun_sel == "TODOS" else 'nm_local_votacao'
    label_eixo = "Cidade" if mun_sel == "TODOS" else "Local de Votação"

    registros = []
    for item in selecionados_todos:
        for ano, df in [("2018", df_18), ("2022", df_22)]:
            filtrado = filtrar_por_item(df, item)
            if mun_sel != "TODOS":
                filtrado = filtrado[filtrado['nm_municipio'] == mun_sel]
            agrupado = filtrado.groupby(eixo)['qt_votos'].sum().reset_index()
            agrupado['Candidato/Partido'] = item
            agrupado['Ano'] = ano
            registros.append(agrupado)

    if not registros:
        st.info("Sem dados para exibir.")
        return

    df_evol = pd.concat(registros, ignore_index=True)
    df_evol = df_evol.rename(columns={eixo: label_eixo, 'qt_votos': 'Votos'})

    # --- Gráfico geral: total de votos por ano ---
    st.markdown("#### 🔢 Total de Votos por Ano")
    totais = df_evol.groupby(['Candidato/Partido', 'Ano'])['Votos'].sum().reset_index()
    fig_total = px.line(
        totais, x='Ano', y='Votos', color='Candidato/Partido',
        markers=True, text='Votos',
        color_discrete_map=mapa_cores,
        title="Evolução do Total de Votos"
    )
    fig_total.update_traces(textposition="top center", texttemplate='%{text:,.0f}')
    fig_total.update_layout(yaxis_title="Votos", xaxis_title="Ano", legend_title="")
    st.plotly_chart(fig_total, use_container_width=True)

    # --- Gráfico por localidade: top localidades ---
    st.markdown(f"#### 🏙️ Evolução por {label_eixo} (Top 10)")

    for item in selecionados_todos:
        st.markdown(f"**{item}**")
        df_item = df_evol[df_evol['Candidato/Partido'] == item]

        # Pega top 10 localidades pelo total de votos somando 2018+2022
        top_locais = (df_item.groupby(label_eixo)['Votos'].sum()
                      .nlargest(10).index.tolist())
        df_top = df_item[df_item[label_eixo].isin(top_locais)]

        fig = px.line(
            df_top, x='Ano', y='Votos', color=label_eixo,
            markers=True,
            title=f"Top 10 {label_eixo}s — {item}"
        )
        fig.update_layout(yaxis_title="Votos", xaxis_title="Ano", legend_title=label_eixo)
        st.plotly_chart(fig, use_container_width=True)

    # Botão de exportação
    buffer = io.BytesIO()
    df_evol.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button(
        label="💾 Baixar Excel — Evolução Temporal",
        data=buffer.getvalue(),
        file_name="evolucao_temporal.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_evolucao"
    )
