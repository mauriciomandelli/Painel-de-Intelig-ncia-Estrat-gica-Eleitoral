import io
import streamlit as st
import pandas as pd
import plotly.express as px
from analysis.metrics import filtrar_por_item


def render(df_atual, selecionados_todos, mun_sel):
    st.subheader("📍 Benchmark Regional")
    st.caption(
        "Compara o share de cada candidato com a **média por candidato do seu partido** por município. "
        "Verde = candidato performa acima da média dos colegas de partido. Vermelho = abaixo."
    )

    cands_individuais = [x for x in selecionados_todos if not x.startswith("PARTIDO ")]
    if not cands_individuais:
        st.info("Selecione pelo menos um **candidato individual** (não partido) na barra lateral.")
        return

    eixo = 'nm_municipio' if mun_sel == "TODOS" else 'nm_local_votacao'
    label_eixo = "Município" if mun_sel == "TODOS" else "Local de Votação"

    df_base = df_atual.copy()
    if mun_sel != "TODOS":
        df_base = df_base[df_base['nm_municipio'] == mun_sel]

    total_por_local = df_base.groupby(eixo)['qt_votos'].sum().reset_index().rename(columns={'qt_votos': 'total'})

    for item in cands_individuais:
        st.markdown(f"---\n#### 📍 {item}")

        partido_cand = df_base[df_base['nm_votavel'] == item]['nr_partido'].mode()
        if partido_cand.empty:
            st.warning(f"Não foi possível identificar o partido de {item}.")
            continue
        partido_num = partido_cand.iloc[0]

        # Votos do candidato por local
        votos_cand = (filtrar_por_item(df_base, item)
                      .groupby(eixo)['qt_votos'].sum()
                      .reset_index().rename(columns={'qt_votos': 'votos_cand'}))

        # Média de votos por candidato do partido naquele local
        # Divide o total do partido pelo número de candidatos do partido com votos lá
        df_partido = df_base[df_base['nr_partido'] == partido_num]
        n_cands_partido = (df_partido.groupby(eixo)['nm_votavel']
                           .nunique().reset_index().rename(columns={'nm_votavel': 'n_cands'}))
        votos_partido_total = (df_partido.groupby(eixo)['qt_votos'].sum()
                               .reset_index().rename(columns={'qt_votos': 'votos_partido_total'}))
        media_partido = votos_partido_total.merge(n_cands_partido, on=eixo)
        media_partido['votos_media_partido'] = media_partido['votos_partido_total'] / media_partido['n_cands']

        df_bench = (votos_cand
                    .merge(media_partido[[eixo, 'votos_media_partido', 'n_cands']], on=eixo, how='outer')
                    .merge(total_por_local, on=eixo)
                    .fillna(0))

        df_bench['share_cand (%)']          = (df_bench['votos_cand']          / df_bench['total'] * 100).round(2)
        df_bench['share_media_partido (%)'] = (df_bench['votos_media_partido'] / df_bench['total'] * 100).round(2)
        df_bench['diferenca (pp)']          = (df_bench['share_cand (%)'] - df_bench['share_media_partido (%)']).round(2)
        df_bench['share_partido (%)']       = df_bench['share_media_partido (%)']
        df_bench['status'] = df_bench['diferenca (pp)'].apply(
            lambda x: '✅ Acima da média' if x > 0 else ('🔴 Abaixo da média' if x < 0 else '⚖️ Na média')
        )
        df_bench = df_bench.rename(columns={eixo: label_eixo})

        # Métricas gerais
        acima = (df_bench['diferenca (pp)'] > 0).sum()
        abaixo = (df_bench['diferenca (pp)'] < 0).sum()
        media_dif = df_bench['diferenca (pp)'].mean()
        media_n_cands = df_bench['n_cands'].mean()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("✅ Acima da média do partido", acima)
        c2.metric("🔴 Abaixo da média do partido", abaixo)
        c3.metric("📊 Diferença média (pp)", f"{media_dif:+.2f}")
        c4.metric("👥 Média de candidatos do partido por local", f"{media_n_cands:.1f}")

        # Gráfico top/bottom 10
        top10 = df_bench.nlargest(10, 'diferenca (pp)')
        bot10 = df_bench.nsmallest(10, 'diferenca (pp)')
        df_plot = pd.concat([top10, bot10]).drop_duplicates().sort_values('diferenca (pp)', ascending=True)

        fig = px.bar(
            df_plot,
            x='diferenca (pp)', y=label_eixo,
            orientation='h',
            color='diferenca (pp)',
            color_continuous_scale=["#e74c3c", "#f8f9fa", "#2ecc71"],
            color_continuous_midpoint=0,
            hover_data={'share_cand (%)': ':.2f', 'share_partido (%)': ':.2f', 'n_cands': True},
            title=f"Candidato vs Média do Partido {partido_num} (Top/Bottom 10)",
            labels={'diferenca (pp)': 'Diferença (pp)', 'n_cands': 'Nº candidatos do partido'}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Ver tabela completa"):
            st.dataframe(
                df_bench[[label_eixo, 'votos_cand', 'share_cand (%)', 'share_partido (%)', 'n_cands', 'diferenca (pp)', 'status']]
                    .sort_values('diferenca (pp)', ascending=False),
                use_container_width=True, hide_index=True,
                column_config={
                    'votos_cand': st.column_config.NumberColumn('Votos Candidato', format="%d"),
                    'share_cand (%)': st.column_config.NumberColumn('Share Candidato (%)', format="%.2f%%"),
                    'share_partido (%)': st.column_config.NumberColumn('Share Médio Partido (%)', format="%.2f%%"),
                    'n_cands': st.column_config.NumberColumn('Nº cands. partido', format="%d"),
                    'diferenca (pp)': st.column_config.NumberColumn('Diferença (pp)', format="%+.2f")
                }
            )

        buffer = io.BytesIO()
        df_bench.to_excel(buffer, index=False, engine='openpyxl')
        st.download_button(
            label=f"💾 Baixar Excel — Benchmark {item}",
            data=buffer.getvalue(),
            file_name=f"benchmark_{item.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_benchmark_{item}"
        )
