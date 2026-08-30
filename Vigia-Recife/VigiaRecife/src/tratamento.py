# -*- coding: utf-8 -*-
"""
tratamento.py
=============
Tratamento de inconsistências específicas identificadas na etapa de limpeza:
datas inválidas, idades biologicamente implausíveis e o artefato de horário
padrão do sistema de origem (registros cravados às 21h00min00s).

Decisões de tratamento documentadas
------------------------------------
- Datas que não seguem o formato esperado viram NaT (nulo de data),
  preservando o registro em vez de descartá-lo.
- Idades fora da faixa biologicamente plausível (< 0 ou > 110 anos) são
  tratadas como ausentes, não como erro que invalida o registro inteiro.
- Registros com horário exatamente às 21:00:00 são marcados como
  "hora_estimada" (valor padrão do sistema, não horário real) e excluídos
  apenas das análises que dependem de horário específico — nunca removidos
  da base principal.
"""

import numpy as np
import pandas as pd


def tratar_datas(df: pd.DataFrame, coluna_data: str = "data") -> pd.DataFrame:
    """Converte a coluna de data para datetime. Datas inválidas viram NaT."""
    dados = df.copy()
    dados[coluna_data] = pd.to_datetime(
        dados[coluna_data], dayfirst=True, errors="coerce"
    )
    return dados


def tratar_idades(df: pd.DataFrame, coluna: str = "age") -> pd.DataFrame:
    """Idades menores que 0 ou maiores que 110 anos tornam-se ausentes (NaN)."""
    dados = df.copy()
    dados.loc[(dados[coluna] < 0) | (dados[coluna] > 110), coluna] = np.nan
    return dados


def tratar_hora_estimada(df: pd.DataFrame, coluna_data: str = "data") -> pd.DataFrame:
    """
    Marca registros cujo horário é o valor padrão do sistema (21:00:00) e
    cria a coluna `hora_valida` (NaN nesses casos) para uso em qualquer
    análise que dependa da hora exata da ocorrência.

    Ver também: src/graficos.py -> grafico_distribuicao_hora, que evidencia
    visualmente por que esse tratamento é necessário.
    """
    dados = df.copy()

    dados["hora_estimada"] = (
        (dados[coluna_data].dt.hour == 21)
        & (dados[coluna_data].dt.minute == 0)
        & (dados[coluna_data].dt.second == 0)
    )

    dados["hora_valida"] = dados[coluna_data].dt.hour.astype("float")
    dados.loc[dados["hora_estimada"], "hora_valida"] = np.nan

    return dados


def relatorio_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Relatório de valores ausentes por coluna, ordenado do maior para o menor."""
    relatorio = df.isnull().sum().sort_values(ascending=False).to_frame("Valores Ausentes")
    relatorio["Percentual (%)"] = (relatorio["Valores Ausentes"] / len(df) * 100).round(2)
    return relatorio


def tratar_base(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Orquestra o tratamento completo: datas, idades e artefato de hora.
    Fonte da verdade única para "como a base é tratada" no projeto.
    """
    dados = tratar_datas(df)
    dados = tratar_idades(dados)
    dados = tratar_hora_estimada(dados)

    if verbose:
        print(
            "Registros com hora estimada (excluídos da análise de horário): "
            f"{dados['hora_estimada'].sum()} "
            f"({dados['hora_estimada'].mean():.1%})"
        )

    return dados
