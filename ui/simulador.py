import streamlit as st
import pandas as pd
import plotly.express as px
from analysis.metrics import filtrar_por_item, calcular_saldo


def render(df_18, df_22, selecionados_todos, mun_sel):
    st.subheader("🗳️ Simulador de Coligação — Projeção 2026")
    st.caption(
        "Estima quantos votos o candidato precisaria para ser eleito em 2026, "
        "com base no crescimento histórico e no quociente eleitoral."
    )

    cands_individuais = [x for x in selecionados_todos if not x.startswith("PARTIDO ")]
    if not cands_individuais:
        st.info("Selecione pelo menos um **candidato individual** na barra lateral.")
        return

    st.markdown("#### ⚙️ Parâmetros da Simulação")
    col1, col2, col3 = st.columns(3)
    with col1:
        vagas = st.number_input("Vagas em disputa:", min_value=1, max_value=70, value=16,
                                help="Federal: 16 vagas para SC. Estadual: 40 vagas.")
    with col2:
        crescimento_eleitorado = st.slider("Crescimento do eleitorado 2022→2026 (%):",
                                           0.0, 15.0, 5.0, step=0.5)
    with col3:
        participacao = st.slider("Estimativa de comparecimento (%):",
                                 60.0, 95.0, 80.0, step=1.0)

    st.divider()

    for item in cands_individuais:
        st.markdown(f"#### 📍 {item}")

        saldo = calcular_saldo(df_18, df_22, item, mun_sel)
        v18, v22, dif, perc = saldo["v_18"], saldo["v_22"], saldo["dif"], saldo["perc"]

        if v18 == 0 and v22 == 0:
            st.warning("Sem dados suficientes para simulação.")
            continue

        # Total de votos válidos em 2022
        df_base = df_22.copy()
        if mun_sel != "TODOS":
            df_base = df_base[df_base['nm_municipio'] == mun_sel]
        total_validos_22 = int(df_base['qt_votos'].sum())

        # Estimativa de votos válidos em 2026
        total_estimado_26 = int(total_validos_22 * (1 + crescimento_eleitorado / 100) * (participacao / 100) /
                                (df_22['qt_votos'].sum() / df_22['qt_votos'].sum()))  # proporção mantida
        total_estimado_26 = int(total_validos_22 * (1 + crescimento_eleitorado / 100))

        # Quociente eleitoral estimado
        qe_estimado = total_estimado_26 / vagas

        # Tendência do candidato
        taxa_crescimento = perc / 100 if v18 > 0 else 0.05
        v26_tendencia = int(v22 * (1 + taxa_crescimento))

        # Simulador de cenários
        st.markdown("##### 📊 Projeção de Votos em 2026")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Votos em 2018", f"{int(v18):,}")
        col_b.metric("Votos em 2022", f"{int(v22):,}", delta=f"{int(dif):+,} ({perc:.1f}%)")
        col_c.metric("Quociente Eleitoral Estimado 2026", f"{int(qe_estimado):,}")

        st.markdown("##### 🎯 Cenários para 2026")
        cenarios = []
        for nome, mult in [("Pessimista (-20%)", 0.80), ("Neutro (tendência)", 1.0),
                           ("Otimista (+20%)", 1.20), ("Muito otimista (+50%)", 1.50)]:
            v_cen = int(v22 * (1 + taxa_crescimento) * mult)
            eleito = v_cen >= qe_estimado
            cenarios.append({
                "Cenário": nome,
                "Votos Projetados": v_cen,
                "Quociente Necessário": int(qe_estimado),
                "Saldo para Eleição": v_cen - int(qe_estimado),
                "Eleito?": "✅ Sim" if eleito else "❌ Não"
            })

        df_cen = pd.DataFrame(cenarios)
        st.dataframe(df_cen, use_container_width=True, hide_index=True,
                     column_config={
                         "Votos Projetados": st.column_config.NumberColumn(format="%d"),
                         "Quociente Necessário": st.column_config.NumberColumn(format="%d"),
                         "Saldo para Eleição": st.column_config.NumberColumn(format="%+d"),
                     })

        # Gráfico de barras com linha do quociente
        import plotly.graph_objects as go
        fig = go.Figure()
        cores_cen = ["#e74c3c", "#f1c40f", "#2ecc71", "#27ae60"]
        for idx, row in df_cen.iterrows():
            fig.add_bar(x=[row["Cenário"]], y=[row["Votos Projetados"]],
                        marker_color=cores_cen[idx],
                        name=row["Cenário"], text=f"{row['Votos Projetados']:,}",
                        textposition='outside')
        fig.add_hline(y=qe_estimado, line_dash="dash", line_color="red",
                      annotation_text=f"Quociente: {int(qe_estimado):,}", annotation_position="top right")
        fig.update_layout(showlegend=False, yaxis_title="Votos", title=f"Projeção 2026 — {item}")
        st.plotly_chart(fig, use_container_width=True)

        # Quantos votos faltam no pior cenário
        pior = df_cen.iloc[0]
        if pior["Saldo para Eleição"] < 0:
            faltam = abs(pior["Saldo para Eleição"])
            st.warning(
                f"⚠️ No cenário pessimista, **{item}** precisaria de mais **{faltam:,} votos** "
                f"para atingir o quociente eleitoral estimado."
            )
        else:
            st.success(f"✅ Mesmo no cenário pessimista, **{item}** ultrapassaria o quociente eleitoral estimado.")

        st.divider()
