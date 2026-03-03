import streamlit as st
import pandas as pd
from analysis.metrics import calcular_saldo, votos_por_local


def render(df_18, df_22, todos_dados, tipo_slug, selecionados_todos, mun_sel, ano_sel, mapa_cores):
    st.subheader("🔔 Comparação Rápida — Snapshots")
    st.caption("Salve a seleção atual como um snapshot e compare com outra seleção lado a lado.")

    if "snapshots" not in st.session_state:
        st.session_state.snapshots = []

    # --- Salvar snapshot atual ---
    col_salvar, col_limpar = st.columns([3, 1])
    with col_salvar:
        nome_snap = st.text_input("Nome do snapshot:", placeholder="Ex: Pedro Uczai — Estado — 2022")
    with col_limpar:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Limpar todos", key="limpar_snaps"):
            st.session_state.snapshots = []
            st.rerun()

    if st.button("💾 Salvar snapshot atual", key="salvar_snap"):
        if not selecionados_todos:
            st.warning("Selecione pelo menos um candidato ou partido antes de salvar.")
        elif not nome_snap.strip():
            st.warning("Digite um nome para o snapshot.")
        else:
            snap = {
                "nome": nome_snap.strip(),
                "ano": ano_sel,
                "mun": mun_sel,
                "selecionados": list(selecionados_todos),
                "dados": {}
            }
            df_atual = todos_dados[f"{tipo_slug}_{ano_sel}"]
            for item in selecionados_todos:
                saldo = calcular_saldo(df_18, df_22, item, mun_sel)
                v_atual = votos_por_local(df_atual, item, mun_sel)
                total = df_atual['qt_votos'].sum() if mun_sel == "TODOS" else \
                        df_atual[df_atual['nm_municipio'] == mun_sel]['qt_votos'].sum()
                share = (v_atual / total * 100) if total > 0 else 0
                snap["dados"][item] = {
                    "votos": int(v_atual),
                    "share": round(share, 2),
                    "dif": int(saldo["dif"]),
                    "perc": round(saldo["perc"], 1)
                }
            st.session_state.snapshots.append(snap)
            st.success(f"Snapshot '{nome_snap}' salvo!")
            st.rerun()

    st.divider()

    # --- Exibir snapshots ---
    snaps = st.session_state.snapshots
    if not snaps:
        st.info("Nenhum snapshot salvo ainda. Configure a seleção na sidebar e clique em **Salvar snapshot atual**.")
        return

    st.markdown(f"**{len(snaps)} snapshot(s) salvo(s)**")

    if len(snaps) == 1:
        _exibir_snapshot(snaps[0])
    else:
        # Comparação lado a lado dos dois últimos (ou escolha do usuário)
        opcoes = [s["nome"] for s in snaps]
        col1, col2 = st.columns(2)
        with col1:
            sel_a = st.selectbox("Snapshot A:", opcoes, index=0, key="snap_a")
        with col2:
            sel_b = st.selectbox("Snapshot B:", opcoes, index=min(1, len(opcoes)-1), key="snap_b")

        snap_a = next(s for s in snaps if s["nome"] == sel_a)
        snap_b = next(s for s in snaps if s["nome"] == sel_b)

        col_a, col_b = st.columns(2)
        with col_a:
            _exibir_snapshot(snap_a)
        with col_b:
            _exibir_snapshot(snap_b)

        # Tabela de diferenças entre snapshots
        itens_comuns = set(snap_a["dados"].keys()) & set(snap_b["dados"].keys())
        if itens_comuns:
            st.markdown("#### ⚖️ Diferença entre Snapshots")
            rows = []
            for item in itens_comuns:
                da = snap_a["dados"][item]
                db = snap_b["dados"][item]
                rows.append({
                    "Candidato/Partido": item,
                    f"Votos ({sel_a})": da["votos"],
                    f"Votos ({sel_b})": db["votos"],
                    "Δ Votos": db["votos"] - da["votos"],
                    f"Share ({sel_a})": da["share"],
                    f"Share ({sel_b})": db["share"],
                    "Δ Share (pp)": round(db["share"] - da["share"], 2)
                })
            df_diff = pd.DataFrame(rows)
            st.dataframe(df_diff, use_container_width=True, hide_index=True)


def _exibir_snapshot(snap: dict):
    st.markdown(f"**📌 {snap['nome']}**")
    st.caption(f"Ano: {snap['ano']} | Filtro: {snap['mun']}")
    rows = []
    for item, d in snap["dados"].items():
        rows.append({
            "Candidato/Partido": item,
            "Votos": d["votos"],
            "Share (%)": d["share"],
            "Δ vs 2018": f"{'▲' if d['dif'] > 0 else '▼'} {abs(d['dif']):,} ({d['perc']:+.1f}%)"
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                 column_config={"Votos": st.column_config.NumberColumn(format="%d"),
                                "Share (%)": st.column_config.NumberColumn(format="%.2f%%")})
