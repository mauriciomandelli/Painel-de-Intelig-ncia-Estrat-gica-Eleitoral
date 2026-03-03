import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis.metrics import filtrar_por_item


def render(df_atual, selecionados_todos, mun_sel):
    st.subheader("📊 Comparação Direta entre Candidatos")
    st.caption("Cada ponto é um município. Pontos acima da diagonal = candidato B domina. Abaixo = candidato A domina.")

    if len(selecionados_todos) < 2:
        st.info("Selecione pelo menos **2 candidatos ou partidos** na barra lateral para comparar.")
        return

    col1, col2 = st.columns(2)
    with col1:
        item_a = st.selectbox("Candidato A (eixo X):", selecionados_todos, index=0, key="comp_a")
    with col2:
        opcoes_b = [x for x in selecionados_todos if x != item_a]
        item_b = st.selectbox("Candidato B (eixo Y):", opcoes_b, index=0, key="comp_b")

    eixo = 'nm_municipio' if mun_sel == "TODOS" else 'nm_local_votacao'
    label_eixo = "Município" if mun_sel == "TODOS" else "Local de Votação"

    df_base = df_atual.copy()
    if mun_sel != "TODOS":
        df_base = df_base[df_base['nm_municipio'] == mun_sel]

    votos_a = filtrar_por_item(df_base, item_a).groupby(eixo)['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'votos_a'})
    votos_b = filtrar_por_item(df_base, item_b).groupby(eixo)['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'votos_b'})
    total   = df_base.groupby(eixo)['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'total'})

    df_comp = votos_a.merge(votos_b, on=eixo, how='outer').fillna(0)
    df_comp = df_comp.merge(total, on=eixo, how='left')
    df_comp['share_a'] = (df_comp['votos_a'] / df_comp['total'] * 100).round(2)
    df_comp['share_b'] = (df_comp['votos_b'] / df_comp['total'] * 100).round(2)
    df_comp['domina'] = df_comp.apply(
        lambda r: item_a if r['votos_a'] > r['votos_b'] else (item_b if r['votos_b'] > r['votos_a'] else 'Empate'),
        axis=1
    )
    df_comp = df_comp.rename(columns={eixo: label_eixo})

    cor_map = {item_a: "#318ce7", item_b: "#e74c3c", "Empate": "#aaaaaa"}

    modo = st.radio("Visualizar por:", ["Votos Brutos", "Share (%)"], horizontal=True, key="comp_modo")

    if modo == "Votos Brutos":
        x_col, y_col = 'votos_a', 'votos_b'
        x_label, y_label = f"Votos — {item_a}", f"Votos — {item_b}"
    else:
        x_col, y_col = 'share_a', 'share_b'
        x_label, y_label = f"Share (%) — {item_a}", f"Share (%) — {item_b}"

    fig = px.scatter(
        df_comp, x=x_col, y=y_col,
        color='domina', color_discrete_map=cor_map,
        hover_name=label_eixo,
        hover_data={
            'votos_a': ':,.0f', 'votos_b': ':,.0f',
            'share_a': ':.2f', 'share_b': ':.2f',
            'domina': False, x_col: False, y_col: False
        },
        labels={x_col: x_label, y_col: y_label, 'domina': 'Quem domina'},
        title=f"{item_a} vs {item_b} por {label_eixo}"
    )

    # Linha diagonal de equilíbrio
    max_val = max(df_comp[x_col].max(), df_comp[y_col].max()) * 1.05
    fig.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode='lines',
        line=dict(color='gray', dash='dash', width=1),
        name='Linha de equilíbrio',
        hoverinfo='skip'
    ))

    fig.update_layout(legend_title="Quem domina")
    st.plotly_chart(fig, use_container_width=True)

    # Resumo
    domina_a = (df_comp['domina'] == item_a).sum()
    domina_b = (df_comp['domina'] == item_b).sum()
    total_loc = len(df_comp)
    c1, c2, c3 = st.columns(3)
    c1.metric(f"🔵 {item_a} domina", f"{domina_a} de {total_loc} {label_eixo}s")
    c2.metric(f"🔴 {item_b} domina", f"{domina_b} de {total_loc} {label_eixo}s")
    c3.metric("⚖️ Empate", f"{total_loc - domina_a - domina_b} {label_eixo}s")

    # Tabela
    st.markdown("#### 📋 Dados Completos")
    st.dataframe(
        df_comp[[label_eixo, 'votos_a', 'share_a', 'votos_b', 'share_b', 'domina']]
            .sort_values('votos_a', ascending=False)
            .rename(columns={
                'votos_a': f'Votos {item_a}', 'share_a': f'Share% {item_a}',
                'votos_b': f'Votos {item_b}', 'share_b': f'Share% {item_b}',
                'domina': 'Quem domina'
            }),
        use_container_width=True, hide_index=True
    )

    buffer = io.BytesIO()
    df_comp.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button(
        label="💾 Baixar Excel — Comparação Direta",
        data=buffer.getvalue(),
        file_name="comparacao_direta.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_comparacao"
    )
