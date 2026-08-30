# -*- coding: utf-8 -*-
"""Testes do modulo src/series_temporais.py."""

import pandas as pd
import pytest

from src.series_temporais import verificar_tendencia


@pytest.mark.parametrize("valores", [[], [1], [1, 1]])
def test_testar_tendencia_rejeita_series_insuficientes(valores):
    with pytest.raises(ValueError, match="pelo menos tres meses"):
        verificar_tendencia(pd.Series(valores))


def test_testar_tendencia_trata_serie_constante_como_sem_tendencia():
    resultado = verificar_tendencia(pd.Series([4, 4, 4]))

    assert resultado["p_valor"] == 1.0
    assert resultado["significativa"] is False
    assert resultado["direcao"] is None


def test_testar_tendencia_ignora_valores_ausentes():
    resultado = verificar_tendencia(pd.Series([1, None, 2, 3]))

    assert resultado["significativa"] == True
    assert resultado["direcao"] == "crescimento"
