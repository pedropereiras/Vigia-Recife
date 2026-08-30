# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd


def tratar_datas(df: pd.DataFrame, coluna_data: str = "data") -> pd.DataFrame:
    
    dados = df.copy()
    dados[coluna_data] = pd.to_datetime(
        dados[coluna_data], dayfirst=True, errors="coerce"
    )
    return dados


def tratar_idades(df: pd.DataFrame, coluna: str = "age") -> pd.DataFrame:
   
    dados = df.copy()
    dados.loc[(dados[coluna] < 0) | (dados[coluna] > 110), coluna] = np.nan
    return dados


def tratar_hora_estimada(df: pd.DataFrame, coluna_data: str = "data") -> pd.DataFrame:
 
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
    
    relatorio = df.isnull().sum().sort_values(ascending=False).to_frame("Valores Ausentes")
    relatorio["Percentual (%)"] = (relatorio["Valores Ausentes"] / len(df) * 100).round(2)
    return relatorio


def tratar_base(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    
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
