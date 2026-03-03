import io
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from analysis.metrics import filtrar_por_item


def render(df_atual, selecionados_todos, mun_sel):
    st.subheader("🔗 Análise de Coligação")
    st.caption(
        "Mostra a correlação entre os votos do candidato e os votos do seu partido por município. "
        "**Correlação alta** = candidato e partido andam juntos. "
        "**Correlação baixa** = candidato tem base própria, independente do partido."
    )

    # Filtrar apenas candidatos individuais (não partidos)
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

        # Descobrir o partido do candidato
        partido_cand = df_base[df_base['nm_votavel'] == item]['nr_partido'].mode()
        if partido_cand.empty:
            st.warning(f"Não foi possível identificar o partido de {item}.")
            continue
        partido_num = partido_cand.iloc[0]

        # Votos do candidato por local
        votos_cand = (df_base[df_base['nm_votavel'] == item]
                      .groupby(eixo)['qt_votos'].sum()
                      .reset_index().rename(columns={'qt_votos': 'votos_cand'}))

        # Votos do partido (excluindo o próprio candidato) por local
        votos_partido = (df_base[(df_base['nr_partido'] == partido_num) & (df_base['nm_votavel'] != item)]
                         .groupby(eixo)['qt_votos'].sum()
                         .reset_index().rename(columns={'qt_votos': 'votos_partido'}))

        df_col = votos_cand.merge(votos_partido, on=eixo, how='inner').merge(total_por_local, on=eixo)
        df_col['share_cand (%)']   = (df_col['votos_cand']   / df_col['total'] * 100).round(2)
        df_col['share_partido (%)'] = (df_col['votos_partido'] / df_col['total'] * 100).round(2)
        df_col = df_col.rename(columns={eixo: label_eixo})

        if len(df_col) < 3:
            st.warning("Dados insuficientes para análise de correlação.")
            continue

        corr = df_col['votos_cand'].corr(df_col['votos_partido'])

        if corr >= 0.75:
            interp = f"🟢 **Correlação forte ({corr:.2f})** — O candidato e o partido crescem juntos. Os votos do partido impulsionam o candidato."
        elif corr >= 0.40:
            interp = f"🟡 **Correlação moderada ({corr:.2f})** — Há alguma relação, mas o candidato tem uma base parcialmente independente."
        else:
            interp = f"🔴 **Correlação fraca ({corr:.2f})** — O candidato tem base própria, distinta da do partido."

        st.info(f"Partido identificado: **{partido_num}** | {interp}")

        fig = px.scatter(
            df_col,
            x='votos_partido', y='votos_cand',
            hover_name=label_eixo,
            hover_data={'share_cand (%)': ':.2f', 'share_partido (%)': ':.2f', 'votos_cand': ':,.0f', 'votos_partido': ':,.0f'},
            labels={
                'votos_partido': f'Votos do Partido {partido_num} (sem o candidato)',
                'votos_cand': f'Votos de {item}'
            },
            trendline='ols',
            trendline_color_override='red',
            title=f"{item} vs Partido {partido_num} — Correlação: {corr:.2f}"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Municípios onde o candidato supera a média do partido
        media_share_partido = df_col['share_partido (%)'].mean()
        media_share_cand = df_col['share_cand (%)'].mean()
        df_col['acima_media_partido'] = df_col['share_cand (%)'] > df_col['share_partido (%)']

        c1, c2, c3 = st.columns(3)
        c1.metric("Share médio do candidato", f"{media_share_cand:.2f}%")
        c2.metric(f"Share médio do partido {partido_num}", f"{media_share_partido:.2f}%")
        superou = df_col['acima_media_partido'].sum()
        c3.metric("Municípios onde supera o partido", f"{superou} de {len(df_col)}")

        with st.expander("Ver tabela completa"):
            st.dataframe(
                df_col[[label_eixo, 'votos_cand', 'share_cand (%)', 'votos_partido', 'share_partido (%)', 'acima_media_partido']]
                    .sort_values('votos_cand', ascending=False),
                use_container_width=True, hide_index=True
            )

        buffer = io.BytesIO()
        df_col.to_excel(buffer, index=False, engine='openpyxl')
        st.download_button(
            label=f"💾 Baixar Excel — Coligação {item}",
            data=buffer.getvalue(),
            file_name=f"coligacao_{item.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_coligacao_{item}"
        )
