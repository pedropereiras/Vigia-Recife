import pandas as pd
import matplotlib.pyplot as plt

from src.config import COR_SECUNDARIA, MIN_OCORRENCIAS_BAIRRO, MIN_OCORRENCIAS_TIPO


def acao_por_bairro(df: pd.DataFrame, min_ocorrencias: int = MIN_OCORRENCIAS_BAIRRO) -> pd.DataFrame:
    
    tabela = (
        df.groupby("neighborhood")["police_action"]
        .agg(ocorrencias="count", pct_acao="mean")
        .query("ocorrencias >= @min_ocorrencias")
        .sort_values("pct_acao", ascending=False)
    )
    tabela["pct_acao"] = (tabela["pct_acao"] * 100).round(1)
    return tabela


def acao_por_tipo(df: pd.DataFrame, min_ocorrencias: int = MIN_OCORRENCIAS_TIPO) -> pd.DataFrame:
    
    tabela = (
        df.groupby("main_reason")["police_action"]
        .agg(ocorrencias="count", pct_acao="mean")
        .query("ocorrencias >= @min_ocorrencias")
        .sort_values("pct_acao", ascending=False)
    )
    tabela["pct_acao"] = (tabela["pct_acao"] * 100).round(1)
    return tabela


def grafico_acao_por_tipo(tabela_acao_por_tipo: pd.DataFrame, caminho=None):
   
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
