# -*- coding: utf-8 -*-
"""Testes do modulo src/features.py."""

import numpy as np
import pandas as pd
import pytest

from src.features import criar_features_temporais, _classificar_idade, _periodo_do_dia


def _df_base():
    return pd.DataFrame({
        "data": pd.to_datetime(["2024-03-15 10:30:00", "2024-07-20 21:00:00", "2024-12-05 03:15:00"]),
        "age": [25, 8, 70],
        "hora_valida": [10.0, np.nan, 3.0],
    })


def test_classificar_idade_crianca():
    assert _classificar_idade(5) == "CRIANCA"
    assert _classificar_idade(12) == "CRIANCA"


def test_classificar_idade_adolescente():
    assert _classificar_idade(13) == "ADOLESCENTE"
    assert _classificar_idade(17) == "ADOLESCENTE"


def test_classificar_idade_adulto():
    assert _classificar_idade(18) == "ADULTO"
    assert _classificar_idade(59) == "ADULTO"


def test_classificar_idade_idoso():
    assert _classificar_idade(60) == "IDOSO"
    assert _classificar_idade(90) == "IDOSO"


def test_classificar_idade_nan():
    assert _classificar_idade(np.nan) == "NAO IDENTIFICADO"


def test_periodo_do_dia_madrugada():
    assert _periodo_do_dia(3) == "MADRUGADA"


def test_periodo_do_dia_manha():
    assert _periodo_do_dia(8) == "MANHÃ"


def test_periodo_do_dia_tarde():
    assert _periodo_do_dia(15) == "TARDE"


def test_periodo_do_dia_noite():
    assert _periodo_do_dia(20) == "NOITE"


def test_periodo_do_dia_nan():
    assert _periodo_do_dia(np.nan) is np.nan


def test_criar_features_temporais_cria_colunas():
    df = _df_base()
    resultado = criar_features_temporais(df)

    colunas_esperadas = ["ano", "mes", "nome_mes", "dia", "dia_semana", "trimestre", "fim_semana", "hora", "periodo", "ageGroup"]
    for col in colunas_esperadas:
        assert col in resultado.columns, f"Coluna '{col}' ausente"


def test_criar_features_temporais_age_group():
    df = _df_base()
    resultado = criar_features_temporais(df)
    assert resultado["ageGroup"].tolist() == ["ADULTO", "CRIANCA", "IDOSO"]


def test_criar_features_temporais_preserva_dados_originais():
    df = _df_base()
    _ = criar_features_temporais(df)
    assert "ano" not in df.columns
