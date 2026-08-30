# -*- coding: utf-8 -*-
"""
relatorio.py
============
Consolida os resultados de todas as etapas da pipeline em um único relatório
de texto (outputs/relatorio.txt) — o mesmo conteúdo que alimenta a
documentação técnica e o relatório em PDF/DOCX do projeto.
"""

import json
from pathlib import Path

import numpy as np


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class ConstrutorRelatorio:
    """Acumula linhas de relatório e escreve o arquivo final de uma vez."""

    def __init__(self):
        self._linhas: list[str] = []

    def titulo(self, texto: str):
        self._linhas.append(f"\n=== {texto} ===")

    def linha(self, texto):
        if isinstance(texto, dict):
            self._linhas.append(json.dumps(texto, ensure_ascii=False, indent=2, cls=_NumpyEncoder))
        else:
            self._linhas.append(str(texto))

    def bloco(self, texto: str):
        self._linhas.append(str(texto))

    def salvar(self, caminho: str | Path):
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        Path(caminho).write_text("\n".join(self._linhas), encoding="utf-8")

    def imprimir(self):
        print("\n".join(self._linhas))

    @property
    def conteudo(self) -> str:
        return "\n".join(self._linhas)
