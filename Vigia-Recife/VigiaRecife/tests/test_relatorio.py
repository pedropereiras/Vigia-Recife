# -*- coding: utf-8 -*-
"""Testes do modulo src/relatorio.py."""

from src.relatorio import ConstrutorRelatorio


def test_construtor_relatorio_adicionar_titulo():
    rel = ConstrutorRelatorio()
    rel.titulo("TESTE")
    rel.linha("linha 1")
    assert "TESTE" in rel._linhas[0]
    assert "linha 1" in rel._linhas[1]


def test_construtor_relatorio_imprimir(capsys):
    rel = ConstrutorRelatorio()
    rel.titulo("RELATORIO")
    rel.linha("dado importante")
    rel.imprimir()
    captured = capsys.readouterr()
    assert "RELATORIO" in captured.out
    assert "dado importante" in captured.out


def test_construtor_relatorio_salvar(tmp_path):
    rel = ConstrutorRelatorio()
    rel.titulo("TESTE")
    rel.linha("conteudo")
    caminho = tmp_path / "relatorio.txt"
    rel.salvar(caminho)
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    assert "TESTE" in texto
