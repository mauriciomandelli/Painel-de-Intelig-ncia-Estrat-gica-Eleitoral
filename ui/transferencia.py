import streamlit as st
import pandas as pd
import plotly.express as px


def render(df_18, df_22, mun_sel):
    st.subheader("🔄 Análise de Transferência de Votos")
    st.caption(
        "Identifica candidatos que votaram em 2018 mas não em 2022 (ou vice-versa) "
        "e estima para onde esses votos foram, comparando a variação por município."
    )

    df_b18 = df_18.copy()
    df_b22 = df_22.copy()
    if mun_sel != "TODOS":
        df_b18 = df_b18[df_b18['nm_municipio'] == mun_sel]
        df_b22 = df_b22[df_b22['nm_municipio'] == mun_sel]

    # Candidatos que existem em 2018 mas não em 2022 (saíram)
    cands_18 = set(df_b18['nm_votavel'].unique())
    cands_22 = set(df_b22['nm_votavel'].unique())
    saíram   = sorted(cands_18 - cands_22)
    entraram = sorted(cands_22 - cands_18)

    tab_saiu, tab_entrou = st.tabs(["📤 Candidatos que saíram (2018→2022)", "📥 Candidatos que entraram (2022)"])

    with tab_saiu:
        if not saíram:
            st.info("Nenhum candidato presente em 2018 deixou de disputar em 2022.")
            return

        cand_sel = st.selectbox("Selecione o candidato que saiu:", saíram, key="transf_saiu")

        votos_cand_18 = df_b18[df_b18['nm_votavel'] == cand_sel].groupby('nm_municipio')['qt_votos'].sum().reset_index()
        votos_cand_18.columns = ['nm_municipio', 'votos_perdidos']

        # Crescimento dos outros candidatos por município nessas localidades
        muns_relevantes = votos_cand_18['nm_municipio'].tolist()
        df_22_muns = df_b22[df_b22['nm_municipio'].isin(muns_relevantes)]
        df_18_muns = df_b18[df_b18['nm_municipio'].isin(muns_relevantes) & (df_b18['nm_votavel'] != cand_sel)]

        crescimento = (
            df_22_muns.groupby('nm_votavel')['qt_votos'].sum() -
            df_18_muns.groupby('nm_votavel')['qt_votos'].sum()
        ).reset_index()
        crescimento.columns = ['Candidato', 'Crescimento de Votos']
        crescimento = crescimento[crescimento['Crescimento de Votos'] > 0].sort_values('Crescimento de Votos', ascending=False)

        total_perdidos = int(votos_cand_18['votos_perdidos'].sum())
        st.metric(f"Votos de {cand_sel} em 2018", f"{total_perdidos:,}")

        st.markdown("#### 📈 Candidatos que mais cresceram nos mesmos municípios")
        st.caption("Estes são os prováveis receptores dos votos liberados.")

        if not crescimento.empty:
            fig = px.bar(
                crescimento.head(15),
                x='Crescimento de Votos', y='Candidato',
                orientation='h',
                color='Crescimento de Votos',
                color_continuous_scale=["#d0e8ff", "#318ce7"],
                title=f"Quem cresceu nos municípios onde {cand_sel} tinha votos?"
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                crescimento.head(20),
                use_container_width=True, hide_index=True,
                column_config={"Crescimento de Votos": st.column_config.NumberColumn(format="%d")}
            )
        else:
            st.info("Não foi possível identificar crescimento significativo.")

        # Distribuição dos votos perdidos por município
        st.markdown("#### 🗺️ Municípios com maior base do candidato em 2018")
        st.dataframe(
            votos_cand_18.sort_values('votos_perdidos', ascending=False).head(15)
                .rename(columns={'nm_municipio': 'Município', 'votos_perdidos': 'Votos em 2018'}),
            use_container_width=True, hide_index=True,
            column_config={"Votos em 2018": st.column_config.NumberColumn(format="%d")}
        )

    with tab_entrou:
        if not entraram:
            st.info("Nenhum candidato novo em 2022 identificado.")
            return

        cand_novo = st.selectbox("Selecione o candidato que entrou:", entraram, key="transf_entrou")

        votos_novo = df_b22[df_b22['nm_votavel'] == cand_novo].groupby('nm_municipio')['qt_votos'].sum().reset_index()
        votos_novo.columns = ['nm_municipio', 'votos_22']
        total_novo = int(votos_novo['votos_22'].sum())

        st.metric(f"Total de votos de {cand_novo} em 2022", f"{total_novo:,}")

        muns_novo = votos_novo['nm_municipio'].tolist()
        df_18_muns = df_b18[df_b18['nm_municipio'].isin(muns_novo)]

        # Candidatos que encolheram nesses municípios
        queda = (
            df_b22[df_b22['nm_municipio'].isin(muns_novo) & (df_b22['nm_votavel'] != cand_novo)].groupby('nm_votavel')['qt_votos'].sum() -
            df_18_muns.groupby('nm_votavel')['qt_votos'].sum()
        ).reset_index()
        queda.columns = ['Candidato', 'Variação']
        queda = queda[queda['Variação'] < 0].sort_values('Variação')

        st.markdown("#### 📉 Candidatos que mais perderam votos nesses municípios")
        st.caption("Possíveis doadores de votos para o novo candidato.")

        if not queda.empty:
            queda['Votos Perdidos'] = queda['Variação'].abs()
            fig = px.bar(
                queda.head(15),
                x='Votos Perdidos', y='Candidato',
                orientation='h',
                color='Votos Perdidos',
                color_continuous_scale=["#ffd0d0", "#e74c3c"],
                title=f"Quem perdeu votos onde {cand_novo} foi forte?"
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
