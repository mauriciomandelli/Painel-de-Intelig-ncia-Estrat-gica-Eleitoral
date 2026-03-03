import pandas as pd

def filtrar_por_item(df: pd.DataFrame, item: str) -> pd.DataFrame:
    """Filtra o DataFrame por candidato ou partido."""
    if item.startswith("PARTIDO "):
        p_num = item.replace("PARTIDO ", "")
        return df[df['nr_partido'] == p_num]
    return df[df['nm_votavel'] == item]

def votos_por_local(df: pd.DataFrame, item: str, mun_sel: str) -> int:
    """Retorna total de votos de um item, com filtro opcional de município."""
    filtrado = filtrar_por_item(df, item)
    if mun_sel != "TODOS":
        filtrado = filtrado[filtrado['nm_municipio'] == mun_sel]
    return filtrado['qt_votos'].sum()

def calcular_saldo(df_18: pd.DataFrame, df_22: pd.DataFrame, item: str, mun_sel: str) -> dict:
    """Retorna votos 2018, votos 2022, diferença e variação percentual."""
    v_18 = votos_por_local(df_18, item, mun_sel)
    v_22 = votos_por_local(df_22, item, mun_sel)
    dif = v_22 - v_18
    perc = (dif / v_18 * 100) if v_18 > 0 else (100.0 if v_22 > 0 else 0.0)
    return {"v_18": v_18, "v_22": v_22, "dif": dif, "perc": perc}