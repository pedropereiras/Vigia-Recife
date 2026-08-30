# -*- coding: utf-8 -*-
"""
Testes do módulo src/limpeza.py.

Executar com: pytest tests/ -v
"""

import pandas as pd

from src.limpeza import padronizar_texto, remover_duplicatas


def test_padronizar_texto_remove_espacos_e_maiuscula():
    df = pd.DataFrame({"neighborhood": [" ibura", "IBURA ", "Ibura"]})
    resultado = padronizar_texto(df)
    assert resultado["neighborhood"].nunique() == 1
    assert resultado["neighborhood"].iloc[0] == "IBURA"


def test_padronizar_texto_nao_afeta_colunas_numericas():
    df = pd.DataFrame({"age": [10, 20, 30], "neighborhood": ["A", "B", "C"]})
    resultado = padronizar_texto(df)
    assert resultado["age"].tolist() == [10, 20, 30]


def test_remover_duplicatas():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    resultado = remover_duplicatas(df, verbose=False)
    assert len(resultado) == 2


def test_limpeza_nao_altera_dataframe_original():
    df = pd.DataFrame({"neighborhood": [" ibura "]})
    _ = padronizar_texto(df)
    # o DataFrame original não deve ser modificado in-place
    assert df["neighborhood"].iloc[0] == " ibura "
