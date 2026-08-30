# -*- coding: utf-8 -*-
"""
Testes do módulo src/tratamento.py.

Executar com: pytest tests/ -v
"""

import numpy as np
import pandas as pd
import pytest

from src.tratamento import tratar_idades, tratar_hora_estimada, tratar_datas


def test_tratar_idades_remove_negativas():
    df = pd.DataFrame({"age": [-5, 20, 30]})
    resultado = tratar_idades(df)
    assert pd.isna(resultado.loc[0, "age"])
    assert resultado.loc[1, "age"] == 20


def test_tratar_idades_remove_acima_de_110():
    df = pd.DataFrame({"age": [111, 45, 200]})
    resultado = tratar_idades(df)
    assert pd.isna(resultado.loc[0, "age"])
    assert pd.isna(resultado.loc[2, "age"])
    assert resultado.loc[1, "age"] == 45


def test_tratar_idades_preserva_validas():
    df = pd.DataFrame({"age": [0, 1, 110]})
    resultado = tratar_idades(df)
    assert resultado["age"].tolist() == [0, 1, 110]


def test_tratar_hora_estimada_marca_21h_exatas():
    df = pd.DataFrame({
        "data": pd.to_datetime([
            "2024-01-01 21:00:00",
            "2024-01-01 21:00:01",  # não é exatamente 21:00:00 -> não deve ser marcada
            "2024-01-01 14:30:00",
        ])
    })
    resultado = tratar_hora_estimada(df)

    assert resultado.loc[0, "hora_estimada"] == True
    assert resultado.loc[1, "hora_estimada"] == False
    assert resultado.loc[2, "hora_estimada"] == False

    assert pd.isna(resultado.loc[0, "hora_valida"])
    assert resultado.loc[2, "hora_valida"] == 14


def test_tratar_datas_formato_invalido_vira_nat():
    df = pd.DataFrame({"data": ["não é uma data", "01/03/2024, 10:00:00"]})
    resultado = tratar_datas(df)
    assert pd.isna(resultado.loc[0, "data"])
    assert not pd.isna(resultado.loc[1, "data"])
