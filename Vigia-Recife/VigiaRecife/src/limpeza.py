# -*- coding: utf-8 -*-
"""
limpeza.py
==========
Funções de limpeza estrutural da base: padronização de texto, remoção de
duplicatas e verificação de integridade de coordenadas.

Todas as funções recebem um DataFrame e retornam uma cópia — nunca alteram
o DataFrame original in-place. Isso preserva a base bruta intacta para fins
de rastreabilidade, conforme a decisão metodológica documentada no projeto.
"""

import pandas as pd


def padronizar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove espaços nas extremidades e converte para maiúsculas todas as
    colunas de texto (dtype object).

    Evita que a mesma categoria apareça de formas diferentes na base
    (ex.: "Ibura", "IBURA ", "ibura" tratados como três bairros distintos).
    """
    dados = df.copy()
    colunas = dados.select_dtypes(include="object").columns

    for coluna in colunas:
        dados[coluna] = dados[coluna].astype(str).str.strip().str.upper()

    return dados


def remover_duplicatas(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Remove registros totalmente duplicados."""
    duplicados = df.duplicated().sum()

    if verbose:
        print(f"Registros duplicados encontrados: {duplicados}")

    dados = df.drop_duplicates()

    if verbose:
        print(f"Base após remoção: {dados.shape}")

    return dados


def checar_coordenadas(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Identifica registros sem latitude/longitude.

    Returns
    -------
    pd.DataFrame
        Subconjunto de registros com coordenadas ausentes (para inspeção).
        A base original não é alterada — a decisão de descartar ou não
        esses registros fica a cargo de quem chama a função.
    """
    invalidas = df[df["latitude"].isna() | df["longitude"].isna()]

    if verbose:
        print("Registros sem coordenadas:", len(invalidas))
        if len(invalidas) > 0:
            print(invalidas["neighborhood"].value_counts())

    return invalidas


def anonimizar_base(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove colunas sensíveis e arredonda coordenadas para reduzir risco
    de reidentificação (ver docs/metodologia.md, seção 7).

    Coluna `address` é removida; latitude/longitude são arredondadas
    para 3 casas decimais (~110m de precisão).
    """
    dados = df.copy()
    colunas_remover = [c for c in ["address"] if c in dados.columns]
    dados = dados.drop(columns=colunas_remover, errors="ignore")

    for col in ["latitude", "longitude"]:
        if col in dados.columns:
            dados[col] = dados[col].round(3)

    return dados


def limpar_base(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Orquestra a limpeza estrutural completa: padronização de texto,
    remoção de duplicatas e checagem (não remoção) de coordenadas ausentes.

    Esta é a função que main.py e o notebook devem chamar — a fonte da
    verdade única para "como a base é limpa" no projeto.
    """
    dados = padronizar_texto(df)
    dados = remover_duplicatas(dados, verbose=verbose)
    checar_coordenadas(dados, verbose=verbose)
    return dados
