# -*- coding: utf-8 -*-
"""
graficos.py
===========
Todas as funções de visualização do projeto: distribuição por bairro,
evolução temporal, perfil demográfico (gênero, raça, pirâmide etária) e
densidade espacial.

Convenção: toda função de gráfico recebe o DataFrame de análise (df_analise)
e, opcionalmente, um `caminho` para salvar a figura em outputs/figures/.
Quando `caminho` é None, a figura é apenas exibida (plt.show()) — útil no
notebook interativo; quando informado, é salva em disco — usado por main.py.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import COR_PRIMARIA, COR_SECUNDARIA, COR_NEUTRA, COR_POSITIVA, ORDEM_FAIXA_ETARIA


def _finalizar(caminho: str | Path | None):
    """Salva ou exibe a figura corrente, e fecha a figura para liberar memória."""
    if caminho:
        plt.tight_layout()
        plt.savefig(caminho, dpi=110)
        plt.close()
    else:
        plt.tight_layout()
        plt.show()


def grafico_distribuicao_hora(hora_bruta: pd.Series, caminho=None):
    """
    Gráfico de barras da distribuição de ocorrências por hora, usando a hora
    BRUTA (sem tratamento) — usado especificamente na Seção 5 do notebook
    para evidenciar visualmente o artefato de horário padrão às 21h.
    """
    plt.figure(figsize=(12, 5))
    hora_bruta.plot(kind="bar", color="firebrick")
    plt.title("Distribuição das Ocorrências por Hora (dado bruto)")
    plt.xlabel("Hora")
    plt.ylabel("Quantidade")
    plt.grid(axis="y", alpha=0.3)
    _finalizar(caminho)


def grafico_bairro(df: pd.DataFrame, top: int = 10, caminho=None):
    """Top N bairros com maior número de ocorrências (barras horizontais)."""
    bairros = df["neighborhood"].value_counts().head(top).sort_values()

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(bairros.index, bairros.values, color=COR_PRIMARIA)
    ax.set_title(f"Top {top} bairros com maior número de ocorrências", fontsize=16, weight="bold")
    ax.set_xlabel("Quantidade de ocorrências")

    for barra in bars:
        largura = barra.get_width()
        ax.text(largura + 2, barra.get_y() + barra.get_height() / 2, f"{int(largura)}", va="center")

    _finalizar(caminho)
    return bairros


def perfil_temporal(df: pd.DataFrame, caminho=None) -> pd.Series:
    """Série anual de ocorrências (linha)."""
    serie = df.groupby("ano").size()

    plt.figure(figsize=(10, 5))
    plt.plot(serie.index, serie.values, marker="o", linewidth=3, color=COR_PRIMARIA)
    plt.title("Ocorrências por Ano", fontsize=16, weight="bold")
    plt.xlabel("Ano")
    plt.ylabel("Quantidade")
    plt.grid(alpha=0.3)
    _finalizar(caminho)

    return serie


def grafico_genero(df: pd.DataFrame, caminho=None):
    """Distribuição de vítimas por gênero, com rótulo percentual."""
    dados = df["genre"].value_counts()

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(dados.index, dados.values, color=COR_SECUNDARIA)
    total = dados.sum()

    for barra in bars:
        valor = barra.get_height()
        ax.text(barra.get_x() + barra.get_width() / 2, valor, f"{valor}\n({valor/total:.1%})", ha="center")

    plt.title("Distribuição por Gênero", fontsize=15, weight="bold")
    plt.xticks(rotation=20)
    _finalizar(caminho)


def grafico_raca(df: pd.DataFrame, caminho=None):
    """
    Distribuição por raça, incluindo "NÃO IDENTIFICADO" em cinza — deixa a
    subnotificação explícita no próprio gráfico, em vez de escondê-la.
    """
    dados = df["race"].fillna("NÃO INFORMADO").value_counts()
    cores = [COR_NEUTRA if cat in ("NÃO IDENTIFICADO", "NÃO INFORMADO") else COR_POSITIVA for cat in dados.index]

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(dados.index, dados.values, color=cores)
    total = dados.sum()

    for barra in bars:
        largura = barra.get_width()
        ax.text(largura + 2, barra.get_y() + barra.get_height() / 2, f"{largura} ({largura/total:.1%})", va="center")

    plt.title("Distribuição por Raça\n(cinza = não identificado / subnotificado)", fontsize=14, weight="bold")
    _finalizar(caminho)


def grafico_raca_apenas_identificada(df: pd.DataFrame, caminho=None):
    """Mesma distribuição de raça, mas filtrando apenas os casos identificados."""
    df_id = df[~df["race"].isin(["NÃO IDENTIFICADO"]) & df["race"].notna()]
    dados = df_id["race"].value_counts()

    if dados.empty:
        print("Não há dados de raça identificados para exibir.")
        return

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(dados.index, dados.values, color=COR_POSITIVA)
    total = dados.sum()

    for barra in bars:
        largura = barra.get_width()
        ax.text(largura + 2, barra.get_y() + barra.get_height() / 2, f"{largura} ({largura/total:.1%})", va="center")

    plt.title("Distribuição por Raça (Apenas Identificadas)", fontsize=14, weight="bold")
    _finalizar(caminho)


def perfil_bairro(df: pd.DataFrame, bairro: str) -> pd.DataFrame:
    """Ficha-resumo de um bairro: tipo predominante, gênero, faixa etária e dia crítico."""
    dados = df[df["neighborhood"] == bairro]

    return pd.DataFrame({
        "Bairro": [bairro],
        "Ocorrências": [len(dados)],
        "Tipo predominante": [dados["main_reason"].mode().iloc[0]] if not dados.empty else [None],
        "Gênero predominante": [dados["genre"].mode().iloc[0]] if not dados.empty else [None],
        "Faixa etária": [dados["ageGroup"].mode().iloc[0]] if not dados.empty else [None],
        "Dia crítico": [
            dados["dia_semana"].mode().iloc[0] if dados["dia_semana"].notna().any() else "N/D"
        ],
    })


def painel_top_bairros(df: pd.DataFrame, top: int = 5) -> pd.DataFrame:
    """Concatena o perfil-resumo dos N bairros com mais ocorrências."""
    top_bairros = df["neighborhood"].value_counts().head(top).index
    return pd.concat([perfil_bairro(df, b) for b in top_bairros], ignore_index=True)


# ---------------------------------------------------------------------------
# Pirâmide etária
# ---------------------------------------------------------------------------

def montar_piramide(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Monta a tabela cruzada faixa etária x gênero (homem cis / mulher cis)
    usada como base da pirâmide etária. Filtra localmente apenas para este
    gráfico — não remove "não identificado" da base geral do projeto.
    """
    base = df[df["genre"].isin(["HOMEM CIS", "MULHER CIS"]) & df["ageGroup"].isin(ORDEM_FAIXA_ETARIA)]
    if base.empty:
        return None
    return pd.crosstab(base["ageGroup"], base["genre"]).reindex(ORDEM_FAIXA_ETARIA, fill_value=0)


def plot_piramide(pir: pd.DataFrame, titulo: str, caminho=None):
    """Renderiza a pirâmide etária (homens à esquerda, mulheres à direita)."""
    pir = pir.copy()
    pir["HOMEM CIS"] = -pir["HOMEM CIS"]
    limite = max(pir["MULHER CIS"].max(), abs(pir["HOMEM CIS"].min())) + 5

    plt.figure(figsize=(10, 6))
    plt.barh(pir.index, pir["HOMEM CIS"], color="#0F4C81", label="Homens")
    plt.barh(pir.index, pir["MULHER CIS"], color="#F28E2B", label="Mulheres")
    plt.axvline(0, color="black", linewidth=1)

    for i, v in enumerate(pir["HOMEM CIS"]):
        if v != 0:
            plt.text(v, i, str(abs(v)), ha="right", va="center", fontsize=9)
    for i, v in enumerate(pir["MULHER CIS"]):
        if v != 0:
            plt.text(v, i, str(v), ha="left", va="center", fontsize=9)

    plt.xlim(-limite, limite)
    ticks = np.linspace(-limite, limite, 7).astype(int)
    plt.xticks(ticks, [abs(t) for t in ticks])
    plt.title(titulo, fontsize=15, weight="bold")
    plt.xlabel("Quantidade de vítimas")
    plt.ylabel("Faixa etária")
    plt.grid(axis="x", linestyle="--", alpha=0.3)
    plt.legend()
    _finalizar(caminho)


def piramide_bairro(df: pd.DataFrame, bairro: str, caminho=None) -> pd.DataFrame | None:
    """Pirâmide etária filtrada para um único bairro — função reutilizável."""
    dados = df[df["neighborhood"] == bairro]
    pir = montar_piramide(dados)
    if pir is None:
        return None
    if caminho:
        plot_piramide(pir, f"Pirâmide Etária das Vítimas — {bairro}", caminho)
    return pir


# ---------------------------------------------------------------------------
# Densidade espacial
# ---------------------------------------------------------------------------

def grafico_densidade_espacial(df: pd.DataFrame, caminho=None):
    """Estimativa de densidade Kernel (KDE) das ocorrências, sobreposta a scatter dos pontos."""
    plt.figure(figsize=(9, 9))
    sns.kdeplot(data=df, x="longitude", y="latitude", fill=True, cmap="Reds", thresh=0.02)
    plt.scatter(df["longitude"], df["latitude"], s=4, color="black", alpha=0.3)
    plt.title("Densidade Espacial das Ocorrências")
    _finalizar(caminho)


def gerar_mapa_calor(df: pd.DataFrame, bairro: str | None = None):
    """
    Gera um mapa de calor interativo (Folium). Retorna o objeto `folium.Map`
    — quem chama decide se exibe (Jupyter) ou salva (`mapa.save("arquivo.html")`).

    Se `bairro` for informado, centraliza o mapa nesse bairro específico.
    """
    import folium
    from folium.plugins import HeatMap

    dados = df[["latitude", "longitude", "neighborhood"]].dropna()

    if bairro:
        dados = dados[dados["neighborhood"] == bairro]
        centro = [dados["latitude"].mean(), dados["longitude"].mean()]
        zoom = 14
    else:
        centro = [-8.0476, -34.8770]  # Recife
        zoom = 12

    mapa = folium.Map(location=centro, zoom_start=zoom, tiles="cartodbpositron")
    HeatMap(dados[["latitude", "longitude"]].values.tolist(), radius=10, blur=15, max_zoom=13).add_to(mapa)
    return mapa
