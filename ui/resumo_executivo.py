import streamlit as st
from analysis.metrics import calcular_saldo, votos_por_local, filtrar_por_item


def render(df_atual, df_18, df_22, selecionados_todos, mun_sel, mapa_cores, ano_sel):
    """Painel fixo de KPIs antes das abas."""
    if not selecionados_todos:
        return

    st.markdown("### 📋 Resumo Executivo")

    for item in selecionados_todos:
        cor = mapa_cores.get(item, "#318ce7")
        v_atual = votos_por_local(df_atual, item, mun_sel)

        # Posição no ranking
        df_base = df_atual.copy()
        if mun_sel != "TODOS":
            df_base = df_base[df_base['nm_municipio'] == mun_sel]

        ranking = filtrar_por_item(df_base, item) if False else df_base  # placeholder
        ranking_cands = df_base.groupby('nm_votavel')['qt_votos'].sum().sort_values(ascending=False).reset_index()
        ranking_cands.index += 1
        try:
            posicao = ranking_cands[ranking_cands['nm_votavel'] == item].index[0]
        except (IndexError, KeyError):
            posicao = "-"

        # Municípios com votos
        df_item = filtrar_por_item(df_base, item)
        n_municipios = df_item['nm_municipio'].nunique() if 'nm_municipio' in df_item.columns else 0

        # Share total
        total_votos = df_base['qt_votos'].sum()
        share = (v_atual / total_votos * 100) if total_votos > 0 else 0

        # Comparativo 2018 vs 2022
        saldo = calcular_saldo(df_18, df_22, item, mun_sel)
        dif, perc = saldo["dif"], saldo["perc"]
        tendencia = f"{'▲' if dif > 0 else ('▼' if dif < 0 else '●')} {abs(int(dif)):,} ({perc:.1f}%)"
        color_tend = "#28a745" if dif > 0 else ("#dc3545" if dif < 0 else "#6c757d")

        st.markdown(f"""
        <div style='border-left: 5px solid {cor}; background: #f8f9fa; border-radius: 8px;
                    padding: 14px 20px; margin-bottom: 12px;'>
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;'>
                <div>
                    <span style='font-size:15px; font-weight:bold; color:{cor};'>{item}</span>
                    <span style='font-size:12px; color:gray; margin-left:8px;'>{ano_sel}</span>
                </div>
                <div style='display:flex; gap:28px; flex-wrap:wrap;'>
                    <div style='text-align:center;'>
                        <div style='font-size:22px; font-weight:bold;'>{int(v_atual):,}</div>
                        <div style='font-size:11px; color:gray;'>votos</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-size:22px; font-weight:bold;'>{share:.2f}%</div>
                        <div style='font-size:11px; color:gray;'>share</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-size:22px; font-weight:bold;'>{posicao}º</div>
                        <div style='font-size:11px; color:gray;'>posição</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-size:22px; font-weight:bold;'>{n_municipios}</div>
                        <div style='font-size:11px; color:gray;'>municípios</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-size:15px; font-weight:bold; color:{color_tend};'>{tendencia}</div>
                        <div style='font-size:11px; color:gray;'>vs 2018</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
