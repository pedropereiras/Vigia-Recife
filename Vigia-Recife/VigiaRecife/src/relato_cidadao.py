# -*- coding: utf-8 -*-
"""
Módulo de relato cidadão com verificação comunitária.
"""

import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import DATA_PROCESSED_DIR

_RELATOS_PATH = DATA_PROCESSED_DIR / "relatos.json"

_STATUS_ABERTO = "ABERTO"
_STATUS_VERIFICADO = "VERIFICADO"
_STATUS_CONFIRMADO = "CONFIRMADO"
_STATUS_DESCARTADO = "DESCARTADO"
_STATUS_EM_ANALISE = "EM_ANALISE"

PRIORIDADES = {
    "HOMICIDIO": "CRITICA",
    "TENTATIVA/HOMICIDIO": "CRITICA",
    "DISPARO": "ALTA",
    "TIRO": "ALTA",
    "AMEACA": "MEDIA",
    "BRIGA": "MEDIA",
    "ROUBO": "ALTA",
    "OUTRO": "BAIXA",
}


def _gerar_id() -> str:
    return hashlib.md5(uuid.uuid4().bytes).hexdigest()[:10]


def _carregar_relatos() -> list[dict]:
    if _RELATOS_PATH.exists():
        with open(_RELATOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _salvar_relatos(relatos: list[dict]):
    _RELATOS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_RELATOS_PATH, "w", encoding="utf-8") as f:
        json.dump(relatos, f, ensure_ascii=False, indent=2)


def registrar_relato(
    descricao: str,
    bairro: str,
    tipo_ocorrencia: str,
    data_hora: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    anonimo: bool = True,
    autor: Optional[str] = None,
) -> dict:
    if not descricao or not descricao.strip():
        raise ValueError("A descrição do relato não pode ser vazia.")
    if not bairro or not bairro.strip():
        raise ValueError("O bairro é obrigatório.")

    tipo_upper = tipo_ocorrencia.strip().upper()
    if tipo_upper not in PRIORIDADES:
        print(f"Aviso: tipo '{tipo_ocorrencia}' não reconhecido. Classificado como OUTRO.")
        tipo_upper = "OUTRO"

    if data_hora:
        try:
            dt = datetime.strptime(data_hora.strip(), "%d/%m/%Y %H:%M")
        except ValueError:
            try:
                dt = datetime.strptime(data_hora.strip(), "%d/%m/%Y")
            except ValueError:
                print(f"Aviso: data '{data_hora}' não pôde ser parseada. Usando data/hora atual.")
                dt = datetime.now()
    else:
        dt = datetime.now()

    relato_id = _gerar_id()
    protocolo = f"VR-{relato_id.upper()}"

    relato = {
        "id": relato_id,
        "protocolo": protocolo,
        "descricao": descricao.strip(),
        "bairro": bairro.strip().upper(),
        "tipo_ocorrencia": tipo_upper,
        "prioridade": PRIORIDADES.get(tipo_upper, "BAIXA"),
        "data_hora": dt.strftime("%d/%m/%Y %H:%M"),
        "latitude": lat,
        "longitude": lon,
        "status": _STATUS_ABERTO,
        "confirmacoes": 0,
        "contestacoes": 0,
        "verificado_por": [],
        "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "anonimo": anonimo,
        "autor": None if anonimo else autor,
    }

    relatos = _carregar_relatos()
    relatos.append(relato)
    _salvar_relatos(relatos)

    print(f"Relato registrado com sucesso!")
    print(f"  Protocolo: {protocolo}")
    print(f"  Status: {_STATUS_ABERTO}")
    print(f"  Prioridade: {relato['prioridade']}")
    return relato


def consultar_protocolo(protocolo: str) -> Optional[dict]:
    relatos = _carregar_relatos()
    for r in relatos:
        if r.get("protocolo", "").upper() == protocolo.upper():
            return r
    print(f"Protocolo '{protocolo}' não encontrado.")
    return None


def verificar_relato(
    protocolo: str,
    verificador_id: str,
    confirmar: bool = True,
    comentario: Optional[str] = None,
) -> Optional[dict]:
    relatos = _carregar_relatos()
    for r in relatos:
        if r.get("protocolo", "").upper() == protocolo.upper():
            if verificador_id in r.get("verificado_por", []):
                print(f"Verificador '{verificador_id}' já avaliou este relato.")
                return r

            r.setdefault("verificado_por", []).append(verificador_id)

            if confirmar:
                r["confirmacoes"] = r.get("confirmacoes", 0) + 1
            else:
                r["contestacoes"] = r.get("contestacoes", 0) + 1

            total_verificacoes = r["confirmacoes"] + r["contestacoes"]
            if r["confirmacoes"] >= 3:
                r["status"] = _STATUS_CONFIRMADO
            elif r["contestacoes"] >= 3:
                r["status"] = _STATUS_DESCARTADO
            elif total_verificacoes >= 1 and r["status"] == _STATUS_ABERTO:
                r["status"] = _STATUS_VERIFICADO

            if comentario:
                r.setdefault("comentarios", []).append({
                    "verificador": verificador_id,
                    "texto": comentario,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                })

            _salvar_relatos(relatos)
            acao = "CONFIRMADO" if confirmar else "CONTESTADO"
            print(f"Relato {protocolo} {acao} por {verificador_id}. Status: {r['status']}")
            return r

    print(f"Protocolo '{protocolo}' não encontrado.")
    return None


def listar_relatos(
    status: Optional[str] = None,
    bairro: Optional[str] = None,
    tipo: Optional[str] = None,
) -> pd.DataFrame:
    relatos = _carregar_relatos()
    if not relatos:
        return pd.DataFrame()

    df = pd.DataFrame(relatos)
    if status:
        df = df[df["status"] == status.upper()]
    if bairro:
        df = df[df["bairro"] == bairro.upper()]
    if tipo:
        df = df[df["tipo_ocorrencia"] == tipo.upper()]
    return df


def estatisticas_relatos() -> dict:
    relatos = _carregar_relatos()
    if not relatos:
        return {"total": 0}

    df = pd.DataFrame(relatos)
    return {
        "total": len(df),
        "por_status": df["status"].value_counts().to_dict(),
        "por_tipo": df["tipo_ocorrencia"].value_counts().to_dict(),
        "por_prioridade": df["prioridade"].value_counts().to_dict(),
        "confirmacoes_total": int(df["confirmacoes"].sum()),
        "contestacoes_total": int(df["contestacoes"].sum()),
    }
