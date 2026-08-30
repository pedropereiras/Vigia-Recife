import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress

from src.config import COR_PRIMARIA, COR_SECUNDARIA


def serie_mensal_completa(df: pd.DataFrame, coluna_data: str = "data") -> pd.Series:
    
    serie = df.set_index(coluna_data).resample("ME").size()

    if len(serie) == 0:
        return serie

    ultimo_mes_completo = pd.Timestamp.today().normalize().replace(day=1) - pd.Timedelta(days=1)
    return serie[serie.index <= ultimo_mes_completo]


def grafico_serie_mensal(serie: pd.Series, caminho=None):
    
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
