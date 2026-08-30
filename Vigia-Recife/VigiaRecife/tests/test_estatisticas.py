# -*- coding: utf-8 -*-
"""Testes do modulo src/estatisticas.py."""

import numpy as np
import pandas as pd
import pytest

from src.estatisticas import (
    estatisticas_idade,
    idade_media_por_bairro,
    idade_media_por_tipo_ocorrencia,
    distribuicao_por_dia_semana,
)


def _df_base():
    return pd.DataFrame({
        "age": [25, 30, 35, 40, 10],
        "neighborhood": ["IBURA", "IBURA", "COHAB", "COHAB", "IBURA"],
        "main_reason": ["HOMICIDIO/TENTATIVA", "DISPARO", "HOMICIDIO/TENTATIVA", "TIRO", "DISPARO"],
        "dia_semana": ["SEGUNDA-FEIRA", "TERCA-FEIRA", "QUARTA-FEIRA", "SEGUNDA-FEIRA", "DOMINGO"],
    })


def test_estatisticas_idade_retorna_dict():
    resultado = estatisticas_idade(_df_base())
    assert isinstance(resultado, dict)
    assert "media" in resultado
    assert "mediana" in resultado
    assert "moda" in resultado
    assert "desvio_padrao" in resultado
    assert "variancia" in resultado


def test_estatisticas_idade_valores():
    resultado = estatisticas_idade(_df_base())
    assert resultado["media"] == 28.0
    assert resultado["mediana"] == 30.0


def test_idade_media_por_bairro():
    resultado = idade_media_por_bairro(_df_base())
    assert isinstance(resultado, pd.Series)
    assert len(resultado) > 0
    assert resultado.index[0] in ["IBURA", "COHAB"]


def test_idade_media_por_tipo():
    resultado = idade_media_por_tipo_ocorrencia(_df_base())
    assert isinstance(resultado, pd.Series)
    assert len(resultado) == 3


def test_distribuicao_por_dia_semana():
    resultado = distribuicao_por_dia_semana(_df_base())
    assert isinstance(resultado, pd.Series)
    assert resultado.loc["SEGUNDA-FEIRA"] == 2
    assert resultado.loc["DOMINGO"] == 1
