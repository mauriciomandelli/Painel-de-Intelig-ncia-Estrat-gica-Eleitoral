import json
import unicodedata
import streamlit as st
from data.loader import carregar_todos
from analysis.metrics import calcular_saldo, votos_por_local
from auth.login import login, logout, is_premium, gate_premium
import ui.mapa
import ui.ganhos
import ui.performance
import ui.rankings
import ui.geral
import ui.evolucao
import ui.alertas
import ui.mapa_coropletico
import ui.comparacao
import ui.concentracao
import ui.coligacao
import ui.benchmark
import ui.resumo_executivo
import ui.snapshot
import ui.transferencia
import ui.simulador
import ui.relatorio

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Radar Eleitoral SC", layout="wide")

# --- AUTENTICAÇÃO ---
autenticado, nome, role = login()
if not autenticado:
    st.stop()

# Usuário autenticado — mostrar logout na sidebar
logout()


def normalizar_texto(texto):
    if not texto:
        return ""
    return "".join(c for c in unicodedata.normalize('NFKD', str(texto))
                   if unicodedata.category(c) != 'Mn').upper().strip()


@st.cache_data
def get_coords_map():
    with open("assets/coords_sc.json", "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def get_mesorregioes():
    with open("assets/mesorregioes_sc.json", "r", encoding="utf-8") as f:
        return json.load(f)


# --- CARREGAMENTO DE DADOS ---
todos_dados = carregar_todos()

# --- SIDEBAR ---
st.sidebar.header("🗳️ Configurações")
ano_sel  = st.sidebar.radio("Ano em exibição:", ["2018", "2022"])
cargo_sel = st.sidebar.radio("Cargo:", ["Federal", "Estadual"])

tipo_slug = "federal" if cargo_sel == "Federal" else "estadual"
df_atual = todos_dados[f"{tipo_slug}_{ano_sel}"]
df_18    = todos_dados[f"{tipo_slug}_2018"]
df_22    = todos_dados[f"{tipo_slug}_2022"]

st.sidebar.divider()

if not df_atual.empty:
    todos_cands   = sorted(df_atual['nm_votavel'].unique())
    cands_sel     = st.sidebar.multiselect("👤 Selecionar Candidatos:", todos_cands)

    todos_partidos = sorted(df_atual['nr_partido'].unique())
    partidos_sel   = st.sidebar.multiselect("🚩 Selecionar Partidos:", todos_partidos)

    mesorregioes    = get_mesorregioes()
    mesorregiao_sel = st.sidebar.selectbox(
        "🗺️ Filtro por Mesorregião:",
        ["TODAS"] + sorted(mesorregioes.keys())
    )

    todos_municipios = sorted(df_atual['nm_municipio'].unique())
    if mesorregiao_sel != "TODAS":
        municipios_da_regiao = {normalizar_texto(m) for m in mesorregioes[mesorregiao_sel]}
        todos_municipios = [m for m in todos_municipios if normalizar_texto(m) in municipios_da_regiao]
        if not todos_municipios:
            st.sidebar.warning("Nenhum município encontrado para essa mesorregião.")
            todos_municipios = sorted(df_atual['nm_municipio'].unique())

    mun_sel   = st.sidebar.selectbox("📍 Filtro de Cidade:", ["TODOS"] + todos_municipios)
    share_min = st.sidebar.slider("Exibir no mapa share acima de (%):", 0.0, 100.0, 0.0, step=0.1)

    selecionados_todos = cands_sel + [f"PARTIDO {p}" for p in partidos_sel]
    CORES_HEX  = ["#318ce7", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22"]
    mapa_cores = {item: CORES_HEX[i % len(CORES_HEX)] for i, item in enumerate(selecionados_todos)}

    loc_title = f"em {mun_sel}" if mun_sel != "TODOS" else "no Estado"
    st.title(f"📊 Radar Eleitoral SC — {cargo_sel}")

    # --- RESUMO EXECUTIVO (visível para todos) ---
    ui.resumo_executivo.render(df_atual, df_18, df_22, selecionados_todos, mun_sel, mapa_cores, ano_sel)

    st.divider()

    # --- ABAS ---
    # Abas gratuitas + abas premium (marcadas com ⭐)
    tabs = st.tabs([
        "🗺️ Mapa de Redutos",
        "🌈 Mapa Coroplético",
        "🌡️ Ganhos e Perdas",
        "📈 Evolução Temporal",
        "🏫 Performance Detalhada",
        "🏙️ Rankings",
        "📊 Comparação Direta",
        "🎯 Concentração",
        "🔗 Coligação",
        "📍 Benchmark Regional",
        "🔍 Alertas de Oportunidade",
        "⭐ Simulador 2026",
        "⭐ Transferência de Votos",
        "⭐ Relatório PDF",
        "⭐ Snapshots",
        "🏆 Ranking Geral",
    ])

    (tab_mapa, tab_corop, tab_ganhos, tab_evol, tab_perf, tab_rankings,
     tab_comp, tab_conc, tab_colig, tab_bench, tab_alertas,
     tab_sim, tab_transf, tab_rel, tab_snap, tab_geral) = tabs

    # --- ABAS GRATUITAS ---
    with tab_mapa:
        ui.mapa.render(df_atual, cands_sel, partidos_sel, mun_sel, share_min,
                       mapa_cores, get_coords_map(), normalizar_texto)

    with tab_corop:
        ui.mapa_coropletico.render(df_atual, cands_sel, partidos_sel,
                                   selecionados_todos, mun_sel, mapa_cores)

    with tab_ganhos:
        ui.ganhos.render(df_18, df_22, selecionados_todos, mun_sel)

    with tab_evol:
        ui.evolucao.render(df_18, df_22, selecionados_todos, mun_sel, mapa_cores)

    with tab_perf:
        ui.performance.render(df_atual, cands_sel, partidos_sel, selecionados_todos, mun_sel)

    with tab_rankings:
        ui.rankings.render(df_atual, selecionados_todos, mun_sel)

    with tab_comp:
        ui.comparacao.render(df_atual, selecionados_todos, mun_sel)

    with tab_conc:
        ui.concentracao.render(df_atual, selecionados_todos, mun_sel)

    with tab_colig:
        ui.coligacao.render(df_atual, selecionados_todos, mun_sel)

    with tab_bench:
        ui.benchmark.render(df_atual, selecionados_todos, mun_sel)

    with tab_alertas:
        ui.alertas.render(df_18, df_22, selecionados_todos, mun_sel)

    with tab_geral:
        ui.geral.render(df_atual, cands_sel, partidos_sel, mun_sel, loc_title)

    # --- ABAS PREMIUM ---
    with tab_sim:
        gate_premium()
        ui.simulador.render(df_18, df_22, selecionados_todos, mun_sel)

    with tab_transf:
        gate_premium()
        ui.transferencia.render(df_18, df_22, mun_sel)

    with tab_rel:
        gate_premium()
        ui.relatorio.render(df_atual, df_18, df_22, selecionados_todos,
                            mun_sel, ano_sel, cargo_sel)

    with tab_snap:
        gate_premium()
        ui.snapshot.render(df_18, df_22, todos_dados, tipo_slug,
                           selecionados_todos, mun_sel, ano_sel, mapa_cores)
