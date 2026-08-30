# -*- coding: utf-8 -*-
"""
series_temporais.py
====================
Evolução mensal das ocorrências, média móvel e teste estatístico formal de
tendência (regressão linear).

Por que um teste formal, e não só inspeção visual do gráfico
--------------------------------------------------------------
Oscilações visuais em uma série mensal (picos e vales) não implicam
tendência real de crescimento ou queda. A regressão linear com teste de
significância (scipy.stats.linregress) evita a armadilha comum de afirmar
uma tendência "porque o gráfico parece subir/descer", quando estatisticamente
essa variação pode não ser distinguível de ruído.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress

from src.config import COR_PRIMARIA, COR_SECUNDARIA


def serie_mensal_completa(df: pd.DataFrame, coluna_data: str = "data") -> pd.Series:
    """
    Série mensal de ocorrências, removendo o último mês se estiver
    incompleto (mês corrente na data de extração da base).
    """
    serie = df.set_index(coluna_data).resample("ME").size()

    if len(serie) == 0:
        return serie

    ultimo_mes_completo = pd.Timestamp.today().normalize().replace(day=1) - pd.Timedelta(days=1)
    return serie[serie.index <= ultimo_mes_completo]


def grafico_serie_mensal(serie: pd.Series, caminho=None):
    """Gráfico de linha da série mensal bruta."""
    plt.figure(figsize=(14, 5))
    plt.plot(serie, linewidth=2, color=COR_PRIMARIA)
    plt.title("Ocorrências Mensais")
    plt.tight_layout()
    if caminho:
        plt.savefig(caminho, dpi=110)
        plt.close()
    else:
        plt.show()


def grafico_media_movel(serie: pd.Series, janela: int = 6, caminho=None) -> pd.Series:
    """Série original sobreposta à média móvel (suaviza oscilações de curto prazo)."""
    media_movel = serie.rolling(janela).mean()

    plt.figure(figsize=(14, 5))
    plt.plot(serie, alpha=0.4, label="Original")
    plt.plot(media_movel, linewidth=3, label=f"Média móvel ({janela} meses)", color=COR_SECUNDARIA)
    plt.legend()
    plt.title("Tendência Temporal")
    plt.tight_layout()
    if caminho:
        plt.savefig(caminho, dpi=110)
        plt.close()
    else:
        plt.show()

    return media_movel


def verificar_tendencia(serie: pd.Series) -> dict:
    """
    Regressão linear sobre a série mensal completa.

    Returns
    -------
    dict com slope, p_valor, significativa (bool) e direcao (str ou None).

    Raises
    ------
    ValueError
        Se a série tiver menos de 3 meses de dados válidos.
    """
    serie_valida = serie.dropna()
    if len(serie_valida) < 3:
        raise ValueError("Série precisa de pelo menos tres meses de dados válidos para teste de tendência.")

    x = np.arange(len(serie_valida))
    resultado = linregress(x, serie_valida.values)

    if np.isnan(resultado.pvalue):
        significativa = False
        direcao = None
    else:
        significativa = bool(resultado.pvalue < 0.05)
        direcao = None
        if significativa:
            direcao = "crescimento" if resultado.slope > 0 else "queda"

    return {
        "slope": round(float(resultado.slope), 4),
        "p_valor": round(float(resultado.pvalue), 5) if not np.isnan(resultado.pvalue) else 1.0,
        "significativa": bool(significativa),
        "direcao": direcao,
    }
