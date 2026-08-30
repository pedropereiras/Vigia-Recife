# -*- coding: utf-8 -*-
"""
features.py
===========
Engenharia de atributos derivados da coluna de data/hora: ano, mês, dia da
semana, trimestre, indicador de fim de semana e período do dia.

As variáveis derivadas de hora (`hora`, `periodo`) usam sempre a coluna
`hora_valida` (criada em src/tratamento.py), que já exclui os registros
com horário padrão do sistema — nunca a hora bruta.
"""

import numpy as np
import pandas as pd

from src.config import MONTH_MAP, DAY_MAP, ORDEM_FAIXA_ETARIA


def _classificar_idade(idade: float) -> str:
    """Classifica a idade em faixas etárias conforme ORDEM_FAIXA_ETARIA."""
    if pd.isna(idade):
        return "NAO IDENTIFICADO"
    if idade <= 12:
        return "CRIANCA"
    elif idade <= 17:
        return "ADOLESCENTE"
    elif idade <= 59:
        return "ADULTO"
    else:
        return "IDOSO"


def _periodo_do_dia(hora: float) -> str:
    if pd.isna(hora):
        return np.nan
    if hora < 6:
        return "MADRUGADA"
    elif hora < 12:
        return "MANHÃ"
    elif hora < 18:
        return "TARDE"
    else:
        return "NOITE"


def criar_features_temporais(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria as colunas: ano, mes, nome_mes, dia, dia_semana, trimestre,
    fim_semana, hora e periodo.

    A base resultante (`df_analise`) é a base de trabalho de todas as
    análises exploratórias e da clusterização do projeto. A base de entrada
    (`df_limpo`) permanece preservada para consultas futuras.
    """
    dados = df.copy()

    dados["ano"] = dados["data"].dt.year
    dados["mes"] = dados["data"].dt.month
    dados["nome_mes"] = dados["mes"].map(MONTH_MAP)
    dados["dia"] = dados["data"].dt.day
    dados["dia_semana"] = dados["data"].dt.day_name().map(DAY_MAP)
    dados["trimestre"] = dados["data"].dt.quarter
    dados["fim_semana"] = dados["dia_semana"].isin(["SÁBADO", "DOMINGO"])

    dados["hora"] = dados["hora_valida"]
    dados["periodo"] = dados["hora"].apply(_periodo_do_dia)
    dados["ageGroup"] = dados["age"].apply(_classificar_idade)

    return dados
