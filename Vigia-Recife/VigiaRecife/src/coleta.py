# -*- coding: utf-8 -*-
"""
coleta.py
=========
Leitura da base de dados bruta.

A base utilizada é coletada via API do Fogo Cruzado (https://api.fogocruzado.org.br),
que mapeia tiroteios e disparos de arma de fogo em Pernambuco com verificação por
equipe especializada. Este módulo apenas carrega o CSV já exportado; a integração
direta com a API é um próximo passo do roadmap (ver README).

Este módulo é o único ponto do projeto que sabe onde e como o dado bruto é lido —
se o formato de origem mudar (ex.: passar a vir direto da API em JSON), só este
arquivo precisa ser alterado.
"""

import pandas as pd

from src.config import RAW_CSV_PATH


def carregar_base_bruta(caminho: str | None = None) -> pd.DataFrame:
    """
    Carrega a base de dados bruta, sem qualquer modificação.

    Parameters
    ----------
    caminho : str, opcional
        Caminho alternativo para o CSV. Se omitido, usa RAW_CSV_PATH
        (data/raw/eventos.csv).

    Returns
    -------
    pd.DataFrame
        Base bruta, tal como extraída da fonte original.
    """
    caminho_final = caminho or RAW_CSV_PATH

    if not str(caminho_final).endswith(".csv"):
        raise ValueError("Este projeto atualmente só lê arquivos CSV.")

    df = pd.read_csv(caminho_final)
    return df


if __name__ == "__main__":
    base = carregar_base_bruta()
    print(f"Base carregada: {base.shape[0]} linhas, {base.shape[1]} colunas.")
