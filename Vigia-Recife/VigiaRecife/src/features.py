import numpy as np
import pandas as pd

from src.config import MONTH_MAP, DAY_MAP, ORDEM_FAIXA_ETARIA


def _classificar_idade(idade: float) -> str:
    
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
