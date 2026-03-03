import pandas as pd
import streamlit as st

def normalizar_serie(series: pd.Series) -> pd.Series:
    return (series.str.normalize('NFKD')
                  .str.encode('ascii', errors='ignore')
                  .str.decode('utf-8')
                  .str.upper()
                  .str.strip())

def _carregar_arquivo(caminho: str) -> pd.DataFrame:
    try:
        df = pd.read_parquet(caminho)
        df['nm_votavel'] = df['nm_votavel'].astype(str).str.upper().str.strip()
        df['nm_municipio'] = df['nm_municipio'].astype(str).str.upper().str.strip()
        df['nr_votavel'] = df['nr_votavel'].astype(str)
        df['nr_partido'] = df['nr_votavel'].str[:2]
        df['nm_municipio_busca'] = normalizar_serie(df['nm_municipio'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {caminho}: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_todos() -> dict:
    dados = {}
    for cargo in ["federal", "estadual"]:
        for ano in ["2018", "2022"]:
            chave = f"{cargo}_{ano}"
            dados[chave] = _carregar_arquivo(f"dep{cargo}sc{ano}.parquet")
    return dados