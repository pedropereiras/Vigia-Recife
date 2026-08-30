# -*- coding: utf-8 -*-
"""
Protocolo de acompanhamento público de status de relato.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import DATA_PROCESSED_DIR

_RELATOS_PATH = DATA_PROCESSED_DIR / "relatos.json"

_STATUS_DESCRICOES = {
    "ABERTO": "Relato registrado e aguardando verificacao comunitaria.",
    "VERIFICADO": "Pelo menos um cidadao avaliou o relato.",
    "CONFIRMADO": "Relato confirmado por 3 ou mais cidadaos. Prioridade alta.",
    "DESCARTADO": "Relato contestado por 3 ou mais cidadaos. Encaminhado para revisao.",
    "EM_ANALISE": "Relato em analise por equipe de seguranca publica.",
}


def _carregar_relatos() -> list[dict]:
    if _RELATOS_PATH.exists():
        with open(_RELATOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _salvar_relatos(relatos: list[dict]):
    _RELATOS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_RELATOS_PATH, "w", encoding="utf-8") as f:
        json.dump(relatos, f, ensure_ascii=False, indent=2)


def consultar_por_protocolo(protocolo: str) -> Optional[dict]:
    relatos = _carregar_relatos()
    for r in relatos:
        if r.get("protocolo", "").upper() == protocolo.upper():
            return _formatar_para_cidadao(r)
    return None


def _formatar_para_cidadao(relato: dict) -> dict:
    return {
        "protocolo": relato.get("protocolo"),
        "status": relato.get("status"),
        "status_descricao": _STATUS_DESCRICOES.get(relato.get("status"), "Status desconhecido."),
        "bairro": relato.get("bairro"),
        "tipo_ocorrencia": relato.get("tipo_ocorrencia"),
        "data_registro": relato.get("data_hora"),
        "confirmacoes": relato.get("confirmacoes", 0),
        "contestacoes": relato.get("contestacoes", 0),
        "criado_em": relato.get("criado_em"),
    }


def gerar_timeline(protocolo: str) -> list[dict]:
    relatos = _carregar_relatos()
    for r in relatos:
        if r.get("protocolo", "").upper() == protocolo.upper():
            eventos = []
            eventos.append({
                "data": r.get("criado_em", ""),
                "tipo": "CRIACAO",
                "descricao": f"Relato registrado - {r.get('tipo_ocorrencia', 'N/D')} em {r.get('bairro', 'N/D')}",
            })
            if r.get("status") not in ("ABERTO",):
                eventos.append({
                    "data": r.get("criado_em", ""),
                    "tipo": "STATUS",
                    "descricao": f"Status alterado para: {r.get('status')}",
                })
            confirmacoes = r.get("confirmacoes", 0)
            contestacoes = r.get("contestacoes", 0)
            if confirmacoes > 0:
                eventos.append({
                    "data": "",
                    "tipo": "VERIFICACAO",
                    "descricao": f"{confirmacoes} cidadao(s) confirmaram o relato",
                })
            if contestacoes > 0:
                eventos.append({
                    "data": "",
                    "tipo": "VERIFICACAO",
                    "descricao": f"{contestacoes} cidadao(s) contestaram o relato",
                })
            return eventos
    return []


def listar_status_disponiveis() -> dict:
    return _STATUS_DESCRICOES.copy()


def exportar_protocolo_json(protocolo: str, caminho_saida=None) -> Optional[str]:
    relato = consultar_por_protocolo(protocolo)
    if relato is None:
        return None

    timeline = gerar_timeline(protocolo)
    resultado = {
        "consulta_protocolo": {
            "protocolo": protocolo,
            "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        },
        "relato": relato,
        "timeline": timeline,
    }

    if caminho_saida is None:
        caminho_saida = DATA_PROCESSED_DIR / f"protocolo_{protocolo.upper()}.json"
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"Protocolo exportado para: {caminho_saida}")
    return str(caminho_saida)


def atualizar_status(
    protocolo: str,
    novo_status: str,
    motivo: Optional[str] = None,
) -> Optional[dict]:
    transicoes_permitidas = {
        "ABERTO": ["VERIFICADO", "EM_ANALISE", "DESCARTADO"],
        "VERIFICADO": ["CONFIRMADO", "EM_ANALISE", "DESCARTADO", "ABERTO"],
        "CONFIRMADO": ["EM_ANALISE", "VERIFICADO"],
        "EM_ANALISE": ["CONFIRMADO", "DESCARTADO", "ABERTO"],
        "DESCARTADO": ["ABERTO"],
    }

    novo_upper = novo_status.upper()
    if novo_upper not in _STATUS_DESCRICOES:
        print(f"Status '{novo_status}' invalido. Validos: {list(_STATUS_DESCRICOES.keys())}")
        return None

    relatos = _carregar_relatos()
    for r in relatos:
        if r.get("protocolo", "").upper() == protocolo.upper():
            status_atual = r.get("status", "ABERTO")
            permitidos = transicoes_permitidas.get(status_atual, [])
            if novo_upper not in permitidos:
                print(f"Transicao nao permitida: {status_atual} -> {novo_upper}. Permitidos: {permitidos}")
                return None

            r["status"] = novo_upper
            r.setdefault("historico_status", []).append({
                "de": status_atual,
                "para": novo_upper,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "motivo": motivo,
            })

            _salvar_relatos(relatos)
            print(f"Protocolo {protocolo}: status atualizado {status_atual} -> {novo_upper}")
            return _formatar_para_cidadao(r)

    print(f"Protocolo '{protocolo}' nao encontrado.")
    return None
