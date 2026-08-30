# -*- coding: utf-8 -*-
"""
acao_policial.py
=================
Indicadores de resposta policial por bairro e por tipo de ocorrência.

Apenas 5-6% das ocorrências da base registram ação policial. Esse
percentual isolado diz pouco — o valor estratégico está em identificar
ONDE e QUANDO essa resposta se concentra ou falta, o que estes indicadores
tornam explícito e comparável.
"""

import pandas as pd
import matplotlib.pyplot as plt

from src.config import COR_SECUNDARIA, MIN_OCORRENCIAS_BAIRRO, MIN_OCORRENCIAS_TIPO


def acao_por_bairro(df: pd.DataFrame, min_ocorrencias: int = MIN_OCORRENCIAS_BAIRRO) -> pd.DataFrame:
    """% de ação policial por bairro, apenas bairros com volume mínimo de ocorrências."""
    tabela = (
        df.groupby("neighborhood")["police_action"]
        .agg(ocorrencias="count", pct_acao="mean")
        .query("ocorrencias >= @min_ocorrencias")
        .sort_values("pct_acao", ascending=False)
    )
    tabela["pct_acao"] = (tabela["pct_acao"] * 100).round(1)
    return tabela


def acao_por_tipo(df: pd.DataFrame, min_ocorrencias: int = MIN_OCORRENCIAS_TIPO) -> pd.DataFrame:
    """% de ação policial por tipo de ocorrência, apenas tipos com volume mínimo."""
    tabela = (
        df.groupby("main_reason")["police_action"]
        .agg(ocorrencias="count", pct_acao="mean")
        .query("ocorrencias >= @min_ocorrencias")
        .sort_values("pct_acao", ascending=False)
    )
    tabela["pct_acao"] = (tabela["pct_acao"] * 100).round(1)
    return tabela


def grafico_acao_por_tipo(tabela_acao_por_tipo: pd.DataFrame, caminho=None):
    """Barras horizontais do % de ação policial por tipo de ocorrência."""
    dados_plot = tabela_acao_por_tipo.sort_values("pct_acao")

    plt.figure(figsize=(10, 6))
    plt.barh(dados_plot.index, dados_plot["pct_acao"], color=COR_SECUNDARIA)
    plt.xlabel("% de ocorrências com ação policial")
    plt.title("Percentual de Ação Policial por Tipo de Ocorrência")
    plt.tight_layout()
    if caminho:
        plt.savefig(caminho, dpi=110)
        plt.close()
    else:
        plt.show()
