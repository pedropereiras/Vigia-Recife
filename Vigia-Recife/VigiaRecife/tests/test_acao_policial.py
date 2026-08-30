# -*- coding: utf-8 -*-
"""Testes do modulo src/acao_policial.py."""

import pandas as pd
import pytest

from src.acao_policial import acao_por_bairro, acao_por_tipo


def _df_base():
    return pd.DataFrame({
        "neighborhood": ["IBURA"] * 25 + ["COHAB"] * 25 + ["VARZEA"] * 5,
        "police_action": [True] * 5 + [False] * 20 + [True] * 10 + [False] * 15 + [True] * 1 + [False] * 4,
        "main_reason": ["TIRO"] * 25 + ["DISPARO"] * 25 + ["AMEACA"] * 5,
    })


def test_acao_por_bairro_filtro_minimo():
    df = _df_base()
    resultado = acao_por_bairro(df, min_ocorrencias=20)
    assert len(resultado) == 2
    assert "IBURA" in resultado.index
    assert "COHAB" in resultado.index
    assert "VARZEA" not in resultado.index


def test_acao_por_bairro_percentual():
    df = _df_base()
    resultado = acao_por_bairro(df, min_ocorrencias=20)
    assert resultado.loc["IBURA", "pct_acao"] == 20.0
    assert resultado.loc["COHAB", "pct_acao"] == 40.0


def test_acao_por_tipo():
    df = _df_base()
    resultado = acao_por_tipo(df, min_ocorrencias=5)
    assert "pct_acao" in resultado.columns
    assert len(resultado) == 3
