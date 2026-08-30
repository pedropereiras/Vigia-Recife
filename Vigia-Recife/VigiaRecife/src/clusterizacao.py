from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from src.config import COR_PRIMARIA, COR_SECUNDARIA, MIN_OCORRENCIAS_CLUSTER


def preparar_correlacao(df: pd.DataFrame) -> pd.DataFrame:
    
    dados = df.copy()
    encoder = LabelEncoder()

    for coluna in ["neighborhood", "main_reason", "genre", "race"]:
        dados[coluna] = encoder.fit_transform(dados[coluna].astype(str))

    dados["police_action"] = dados["police_action"].astype(int)
    return dados


def matriz_correlacao(df: pd.DataFrame, caminho=None) -> pd.DataFrame:
    
    import seaborn as sns

    dados = preparar_correlacao(df)
    colunas = ["hora", "neighborhood", "main_reason", "police_action", "age"]
    correlacao = dados[colunas].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(correlacao, annot=True, cmap="RdBu_r", center=0, linewidths=0.5)
    plt.title("Correlação entre Variáveis")
    plt.tight_layout()
    if caminho:
        plt.savefig(caminho, dpi=110)
        plt.close()
    else:
        plt.show()

    return correlacao


def construir_perfil_bairros(df: pd.DataFrame, min_ocorrencias: int = MIN_OCORRENCIAS_CLUSTER) -> pd.DataFrame:
   
    agg_volume = df.groupby("neighborhood").agg(
        ocorrencias=("id", "count"),
        idade_media=("age", "mean"),
        acao_policial=("police_action", "mean"),
        pct_fim_semana=("fim_semana", "mean"),
    )

    prop_periodo = pd.crosstab(df["neighborhood"], df["periodo"], normalize="index").add_prefix("periodo_")

    top_tipos = df["main_reason"].value_counts().head(5).index
    df_tipo = df.copy()
    df_tipo["main_reason_agrupado"] = df_tipo["main_reason"].where(df_tipo["main_reason"].isin(top_tipos), "OUTROS")
    prop_tipo = pd.crosstab(df_tipo["neighborhood"], df_tipo["main_reason_agrupado"], normalize="index").add_prefix("tipo_")

    perfil = agg_volume.join(prop_periodo, how="left").join(prop_tipo, how="left")
    perfil = perfil[perfil["ocorrencias"] >= min_ocorrencias]
    perfil = perfil.fillna(perfil.mean(numeric_only=True))

    return perfil


def escolher_k(X: np.ndarray, k_min: int = 2, k_max: int = 8, caminho=None) -> tuple[int, dict]:
   
    r visualmente o gráfico gerado antes de decidir.
    """
    k_range = range(k_min, k_max + 1)
    inercias, silhuetas = [], []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        inercias.append(km.inertia_)
        silhuetas.append(silhouette_score(X, labels))

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.plot(list(k_range), inercias, marker="o", color=COR_PRIMARIA, label="Inércia (cotovelo)")
    ax1.set_xlabel("Número de clusters (k)")
    ax1.set_ylabel("Inércia", color=COR_PRIMARIA)
    ax2 = ax1.twinx()
    ax2.plot(list(k_range), silhuetas, marker="s", color=COR_SECUNDARIA, label="Silhueta")
    ax2.set_ylabel("Coeficiente de silhueta", color=COR_SECUNDARIA)
    plt.title("Escolha de k — método do cotovelo + silhueta")
    fig.tight_layout()
    if caminho:
        plt.savefig(caminho, dpi=110)
        plt.close()
    else:
        plt.show()

    k_escolhido = list(k_range)[int(np.argmax(silhuetas))]
    detalhes = {
        "inercias": dict(zip(k_range, [round(i, 1) for i in inercias])),
        "silhuetas": dict(zip(k_range, [round(s, 3) for s in silhuetas])),
        "k_escolhido": k_escolhido,
    }
    return k_escolhido, detalhes


def clusterizar_bairros(perfil: pd.DataFrame, k: int | None = None, caminho_elbow=None, caminho_pca=None):
    
    scaler = StandardScaler()
    X = scaler.fit_transform(perfil)

    if k is None:
        k, detalhes_k = escolher_k(X, caminho=caminho_elbow)
    else:
        detalhes_k = {"k_escolhido": k}

    modelo = KMeans(n_clusters=k, random_state=42, n_init=10)
    perfil = perfil.copy()
    perfil["cluster"] = modelo.fit_predict(X)

    pca = PCA(n_components=2)
    componentes = pca.fit_transform(X)

    plt.figure(figsize=(9, 7))
    plt.scatter(
        componentes[:, 0], componentes[:, 1],
        c=perfil["cluster"], cmap="Set2", s=90, edgecolor="black", linewidth=0.5,
    )
    for i, bairro in enumerate(perfil.index):
        plt.text(componentes[i, 0], componentes[i, 1], bairro, fontsize=7)
    plt.title(f"Clusters de bairros (PCA) — variância explicada: {pca.explained_variance_ratio_.sum():.1%}")
    plt.xlabel("Componente 1")
    plt.ylabel("Componente 2")
    plt.tight_layout()
    if caminho_pca:
        plt.savefig(caminho_pca, dpi=110)
        plt.close()
    else:
        plt.show()

    return perfil, detalhes_k


def resumo_por_cluster(perfil_com_cluster: pd.DataFrame) -> pd.DataFrame:
    
    return perfil_com_cluster.groupby("cluster")[
        ["ocorrencias", "idade_media", "acao_policial", "pct_fim_semana"]
    ].mean().round(2)
