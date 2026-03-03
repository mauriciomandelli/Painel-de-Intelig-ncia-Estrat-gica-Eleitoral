import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis.metrics import filtrar_por_item


def calcular_hhi(votos_por_local: pd.Series) -> float:
    """Calcula o Índice de Herfindahl-Hirschman (0 = pulverizado, 1 = concentrado)."""
    total = votos_por_local.sum()
    if total == 0:
        return 0.0
    shares = votos_por_local / total
    return float((shares ** 2).sum())


def render(df_atual, selecionados_todos, mun_sel):
    st.subheader("🎯 Índice de Concentração de Votos")
    st.caption(
        "O índice HHI mede se os votos estão concentrados em poucos municípios (candidato de cidade) "
        "ou pulverizados por todo o estado (candidato de interior). "
        "**Próximo de 1** = muito concentrado. **Próximo de 0** = muito pulverizado."
    )

    if not selecionados_todos:
        st.info("Selecione candidatos ou partidos na barra lateral.")
        return

    eixo = 'nm_municipio' if mun_sel == "TODOS" else 'nm_local_votacao'
    label_eixo = "município" if mun_sel == "TODOS" else "local de votação"

    resultados = []
    detalhes = {}

    for item in selecionados_todos:
        df_base = filtrar_por_item(df_atual, item)
        if mun_sel != "TODOS":
            df_base = df_base[df_base['nm_municipio'] == mun_sel]

        votos = df_base.groupby(eixo)['qt_votos'].sum()
        hhi = calcular_hhi(votos)
        total_votos = int(votos.sum())
        n_locais = int((votos > 0).sum())

        if hhi < 0.15:
            perfil = "🌿 Muito pulverizado"
        elif hhi < 0.30:
            perfil = "🔵 Pulverizado"
        elif hhi < 0.50:
            perfil = "🟡 Moderadamente concentrado"
        elif hhi < 0.70:
            perfil = "🟠 Concentrado"
        else:
            perfil = "🔴 Muito concentrado"

        resultados.append({
            'Candidato/Partido': item,
            'HHI': round(hhi, 4),
            'Perfil': perfil,
            'Total de Votos': total_votos,
            f'Nº de {label_eixo}s com votos': n_locais
        })

        detalhes[item] = votos.reset_index().rename(columns={eixo: label_eixo.title(), 'qt_votos': 'Votos'})

    df_res = pd.DataFrame(resultados).sort_values('HHI', ascending=False)

    # --- Gráfico de barras comparativo ---
    fig = go.Figure()
    for _, row in df_res.iterrows():
        fig.add_bar(
            x=[row['Candidato/Partido']],
            y=[row['HHI']],
            name=row['Candidato/Partido'],
            text=[f"{row['HHI']:.4f}"],
            textposition='outside'
        )

    fig.add_hline(y=0.15, line_dash="dot", line_color="green",
                  annotation_text="Limite pulverizado (0.15)", annotation_position="top right")
    fig.add_hline(y=0.50, line_dash="dot", line_color="orange",
                  annotation_text="Limite concentrado (0.50)", annotation_position="top right")
    fig.update_layout(
        yaxis=dict(title="HHI", range=[0, 1]),
        xaxis_title="",
        showlegend=False,
        title="Índice HHI por Candidato/Partido"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Tabela resumo ---
    st.markdown("#### 📋 Resumo")
    st.dataframe(df_res, use_container_width=True, hide_index=True,
                 column_config={'HHI': st.column_config.NumberColumn(format="%.4f"),
                                'Total de Votos': st.column_config.NumberColumn(format="%d")})

    # --- Detalhamento por candidato ---
    st.markdown("#### 🔍 Distribuição de Votos por Localidade")
    for item in selecionados_todos:
        with st.expander(f"Ver distribuição — {item}"):
            df_det = detalhes[item].sort_values('Votos', ascending=False).reset_index(drop=True)
            df_det.index += 1
            total = df_det['Votos'].sum()
            df_det['Share (%)'] = (df_det['Votos'] / total * 100).round(2)
            df_det['Acumulado (%)'] = df_det['Share (%)'].cumsum().round(2)

            fig_dist = px.bar(
                df_det.head(20), x=label_eixo.title(), y='Votos',
                title=f"Top 20 {label_eixo}s — {item}",
                color='Share (%)',
                color_continuous_scale=["#d0e8ff", "#318ce7"]
            )
            fig_dist.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_dist, use_container_width=True)

            st.dataframe(df_det, use_container_width=True,
                         column_config={'Votos': st.column_config.NumberColumn(format="%d"),
                                        'Share (%)': st.column_config.NumberColumn(format="%.2f%%"),
                                        'Acumulado (%)': st.column_config.NumberColumn(format="%.2f%%")})

    buffer = io.BytesIO()
    df_res.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button(
        label="💾 Baixar Excel — Índice de Concentração",
        data=buffer.getvalue(),
        file_name="indice_concentracao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_concentracao"
    )
