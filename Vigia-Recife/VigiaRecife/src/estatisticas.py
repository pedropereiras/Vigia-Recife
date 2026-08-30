# -*- coding: utf-8 -*-
"""
estatisticas.py
================
Estatística descritiva das variáveis centrais da base: idade, distribuição
por bairro, por tipo de ocorrência, por hora e por dia da semana.
"""

import pandas as pd

from src.config import ORDEM_DIAS_SEMANA


def resumo_estatistico(df: pd.DataFrame) -> pd.DataFrame:
    """Estatísticas descritivas padrão (describe()) das colunas numéricas."""
    return df.describe()


def estatisticas_idade(df: pd.DataFrame) -> dict:
    """Média, mediana, moda, desvio padrão e variância da idade das vítimas."""
    idade = df["age"].dropna()
    return {
        "media": round(idade.mean(), 2),
        "mediana": round(idade.median(), 2),
        "moda": idade.mode()[0] if not idade.mode().empty else None,
        "desvio_padrao": round(idade.std(), 2),
        "variancia": round(idade.var(), 2),
    }


def idade_media_por_bairro(df: pd.DataFrame, top: int = 10) -> pd.Series:
    """Bairros com maior idade média das vítimas."""
    return df.groupby("neighborhood")["age"].mean().sort_values(ascending=False).head(top)


def idade_media_por_tipo_ocorrencia(df: pd.DataFrame) -> pd.Series:
    """Idade média das vítimas por tipo de ocorrência (main_reason)."""
    return df.groupby("main_reason")["age"].mean().sort_values(ascending=False)


def distribuicao_por_hora(df: pd.DataFrame, verbose: bool = True) -> pd.Series:
    """
    Distribuição de ocorrências por hora — usa apenas `hora` (já filtrada
    de hora_valida em src/features.py), portanto exclui o artefato das 21h.
    """
    dist = df["hora"].value_counts().sort_index()
    if verbose:
        print(f"Registros com hora válida para análise: {int(dist.sum())} de {len(df)}")
    return dist


def distribuicao_por_dia_semana(df: pd.DataFrame) -> pd.Series:
    """Distribuição de ocorrências por dia da semana, em ordem de segunda a domingo."""
    return df["dia_semana"].value_counts().reindex(ORDEM_DIAS_SEMANA)
