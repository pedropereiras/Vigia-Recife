# -*- coding: utf-8 -*-
"""
Integração com bases de dados externas:
  - SDS-PE (Secretaria de Defesa Social de Pernambuco): estatísticas de CVLI
  - CTTU (Companhia de Transporte e Trânsito de Recife): acidentes de trânsito

Cada base externa é carregada a partir de um CSV em data/raw/, padronizada
para os campos comuns do projeto e concatenada à base principal do Fogo Cruzado.
"""

import pandas as pd
from pathlib import Path

from src.config import DATA_RAW_DIR


_CTTU_CSV = DATA_RAW_DIR / "cttu_acidentes.csv"
_SDSDPE_CSV = DATA_RAW_DIR / "sdsdpe_cvli.csv"


_COLUNAS_CTTU_MAP = {
    "data_hora": "data",
    "bairro": "neighborhood",
    "tipo_acidente": "main_reason",
    "vitimas": "vitimas_transito",
    "latitude": "latitude",
    "longitude": "longitude",
}

_COLUNAS_SDSPE_MAP = {
    "data": "data",
    "bairro": "neighborhood",
    "tipo_cvli": "main_reason",
    "natureza": "natureza_cvli",
    "vitimas": "vitimas_cvli",
}


def carregar_cttu(caminho=None, verbose=True) -> pd.DataFrame:
    caminho_final = Path(caminho or _CTTU_CSV)
    if not caminho_final.exists():
        if verbose:
            print(f"Base CTTU não encontrada em: {caminho_final}")
            print("Pulando integração com dados de trânsito.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(caminho_final, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_final, encoding="latin-1")

    if df.empty:
        if verbose:
            print("Base CTTU está vazia.")
        return pd.DataFrame()

    df = df.rename(columns={k: v for k, v in _COLUNAS_CTTU_MAP.items() if k in df.columns})

    for col in ["data", "neighborhood", "main_reason"]:
        if col not in df.columns:
            if verbose:
                print(f"Coluna '{col}' não encontrada na base CTTU. Pulando integração.")
            return pd.DataFrame()

    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df["neighborhood"] = df["neighborhood"].astype(str).str.strip().str.upper()
    df["main_reason"] = df["main_reason"].astype(str).str.strip().str.upper()
    df["fonte"] = "CTTU"

    if verbose:
        print(f"Base CTTU carregada: {len(df)} registros de trânsito.")
    return df


def carregar_sdsdpe(caminho=None, verbose=True) -> pd.DataFrame:
    caminho_final = Path(caminho or _SDSDPE_CSV)
    if not caminho_final.exists():
        if verbose:
            print(f"Base SDS-PE não encontrada em: {caminho_final}")
            print("Pulando integração com dados de CVLI.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(caminho_final, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_final, encoding="latin-1")

    if df.empty:
        if verbose:
            print("Base SDS-PE está vazia.")
        return pd.DataFrame()

    df = df.rename(columns={k: v for k, v in _COLUNAS_SDSPE_MAP.items() if k in df.columns})

    for col in ["data", "neighborhood", "main_reason"]:
        if col not in df.columns:
            if verbose:
                print(f"Coluna '{col}' não encontrada na base SDS-PE. Pulando integração.")
            return pd.DataFrame()

    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df["neighborhood"] = df["neighborhood"].astype(str).str.strip().str.upper()
    df["main_reason"] = df["main_reason"].astype(str).str.strip().str.upper()
    df["fonte"] = "SDS-PE"

    if verbose:
        print(f"Base SDS-PE carregada: {len(df)} registros de CVLI.")
    return df


def integrar_bases(df_fc: pd.DataFrame, verbose=True) -> pd.DataFrame:
    bases = [df_fc.copy()]
    bases[0]["fonte"] = "FOGO_CRUZADO"

    df_cttu = carregar_cttu(verbose=verbose)
    if not df_cttu.empty:
        bases.append(df_cttu)

    df_sds = carregar_sdsdpe(verbose=verbose)
    if not df_sds.empty:
        bases.append(df_sds)

    colunas_comuns = [
        "data", "neighborhood", "main_reason", "latitude", "longitude", "fonte",
    ]

    df_integrado = pd.concat(bases, ignore_index=True, sort=False)

    for col in colunas_comuns:
        if col not in df_integrado.columns:
            df_integrado[col] = pd.NA

    if verbose:
        total = len(df_integrado)
        por_fonte = df_integrado["fonte"].value_counts().to_dict()
        print(f"Base integrada: {total} registros totais — {por_fonte}")

    return df_integrado


def resumo_integracao(df_integrado: pd.DataFrame) -> pd.DataFrame:
    if df_integrado.empty:
        return pd.DataFrame()

    resumo = (
        df_integrado.groupby(["fonte", "main_reason"])
        .size()
        .reset_index(name="registros")
        .sort_values(["fonte", "registros"], ascending=[True, False])
    )
    return resumo
