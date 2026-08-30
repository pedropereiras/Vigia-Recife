# -*- coding: utf-8 -*-
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BAIRROS = {
    "IBURA": {"lat": -8.0820, "lon": -34.8920, "peso": 8},
    "COHAB": {"lat": -8.0650, "lon": -34.9050, "peso": 7},
    "VARZEA": {"lat": -8.0350, "lon": -34.9150, "peso": 9},
    "NOVA DESCOBERTA": {"lat": -8.0150, "lon": -34.8650, "peso": 7},
    "IPUTINGA": {"lat": -8.0280, "lon": -34.8930, "peso": 8},
    "CORDOARIA": {"lat": -8.0580, "lon": -34.8730, "peso": 5},
    "ESTACAO": {"lat": -8.0530, "lon": -34.8710, "peso": 4},
    "SAN MARTIN": {"lat": -8.0400, "lon": -34.8780, "peso": 5},
    "ALTO JOSE DO PINHO": {"lat": -8.0200, "lon": -34.8850, "peso": 6},
    "MANGABEIRA": {"lat": -8.0100, "lon": -34.8700, "peso": 5},
    "BREJO DA GUARDEIRA": {"lat": -8.0700, "lon": -34.9000, "peso": 4},
    "VASCO DA GAMA": {"lat": -8.0550, "lon": -34.8800, "peso": 3},
    "SANTO AMARO": {"lat": -8.0580, "lon": -34.8700, "peso": 4},
    "BOA VISTA": {"lat": -8.0500, "lon": -34.8750, "peso": 3},
    "AFLITOS": {"lat": -8.0450, "lon": -34.8720, "peso": 3},
    "ESPINHEIRO": {"lat": -8.0420, "lon": -34.8680, "peso": 3},
    "TOTOS": {"lat": -8.0380, "lon": -34.8650, "peso": 2},
    "POCO DA PANELA": {"lat": -8.0350, "lon": -34.8620, "peso": 2},
    "CASA AMARELA": {"lat": -8.0320, "lon": -34.8600, "peso": 3},
    "CAXANGA": {"lat": -8.0250, "lon": -34.9200, "peso": 4},
    "CURADO": {"lat": -8.0700, "lon": -34.9100, "peso": 5},
    "JARDIM SAO PAULO": {"lat": -8.0050, "lon": -34.8550, "peso": 4},
    "JAQUEIRA": {"lat": -8.0380, "lon": -34.8680, "peso": 2},
    "GRACO": {"lat": -8.0430, "lon": -34.8700, "peso": 2},
    "ROSARINHO": {"lat": -8.0400, "lon": -34.8650, "peso": 2},
}

TIPOS_OCORRENCIA = {
    "HOMICIDIO/TENTATIVA": 0.35,
    "DISPARO": 0.25,
    "TIRO": 0.15,
    "AMEACA": 0.10,
    "ROUBO": 0.08,
    "BRIGA": 0.05,
    "OUTRO": 0.02,
}

GENEROS = {"HOMEM CIS": 0.82, "MULHER CIS": 0.15, "NAO IDENTIFICADO": 0.03}
RACAS = {
    "NAO IDENTIFICADO": 0.55,
    "PRETA": 0.20,
    "PARDA": 0.15,
    "BRANCA": 0.08,
    "AMARELA": 0.02,
}

HORAS_DISTRIBUICAO = {
    0: 0.03, 1: 0.04, 2: 0.05, 3: 0.04, 4: 0.03, 5: 0.02,
    6: 0.02, 7: 0.01, 8: 0.01, 9: 0.01, 10: 0.02, 11: 0.02,
    12: 0.03, 13: 0.03, 14: 0.04, 15: 0.04, 16: 0.04, 17: 0.05,
    18: 0.06, 19: 0.07, 20: 0.07, 21: 0.15, 22: 0.07, 23: 0.05,
}

IDADES_DISTRIBUICAO = {
    "HOMEM CIS": {"media": 30, "std": 12, "min": 10, "max": 85},
    "MULHER CIS": {"media": 32, "std": 14, "min": 8, "max": 90},
    "NAO IDENTIFICADO": {"media": 28, "std": 10, "min": 15, "max": 70},
}

MESES_EXT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


def _escolher_opcao(distribuicao: dict) -> str:
    opcoes = list(distribuicao.keys())
    pesos = list(distribuicao.values())
    return random.choices(opcoes, weights=pesos, k=1)[0]


def _gerar_idade(genero: str) -> int:
    params = IDADES_DISTRIBUICAO.get(genero, IDADES_DISTRIBUICAO["HOMEM CIS"])
    idade = int(np.random.normal(params["media"], params["std"]))
    return max(params["min"], min(params["max"], idade))


def _gerar_data_inicio() -> pd.Timestamp:
    ano = random.choices(
        list(range(2018, 2026)),
        weights=[0.08, 0.10, 0.12, 0.13, 0.14, 0.15, 0.14, 0.14],
        k=1,
    )[0]
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    hora = random.choices(
        list(range(24)),
        weights=[HORAS_DISTRIBUICAO[h] for h in range(24)],
        k=1,
    )[0]
    minuto = random.randint(0, 59)
    segundo = random.randint(0, 59)
    return pd.Timestamp(year=ano, month=mes, day=dia, hour=hora, minute=minuto, second=segundo)


def _perturbar_coordenadas(lat: float, lon: float) -> tuple[float, float]:
    lat += np.random.normal(0, 0.003)
    lon += np.random.normal(0, 0.003)
    return round(lat, 6), round(lon, 6)


def gerar_base(n_registros: int = 2000, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)

    bairros_pesos = {b: info["peso"] for b, info in BAIRROS.items()}
    bairro_nomes = list(bairros_pesos.keys())
    bairro_pesos = list(bairros_pesos.values())

    registros = []
    for i in range(1, n_registros + 1):
        bairro = random.choices(bairro_nomes, weights=bairro_pesos, k=1)[0]
        info_bairro = BAIRROS[bairro]

        genero = _escolher_opcao(GENEROS)
        raca = _escolher_opcao(RACAS)
        tipo = _escolher_opcao(TIPOS_OCORRENCIA)
        idade = _gerar_idade(genero)
        data = _gerar_data_inicio()
        lat, lon = _perturbar_coordenadas(info_bairro["lat"], info_bairro["lon"])
        police_action = random.random() < 0.06

        registros.append({
            "id": f"FC-{i:05d}",
            "neighborhood": bairro,
            "age": idade,
            "data": data.strftime("%d/%m/%Y %H:%M:%S"),
            "latitude": lat,
            "longitude": lon,
            "main_reason": tipo,
            "race": raca,
            "genre": genero,
            "address": f"Rua {random.randint(1, 500)}, {bairro} - Recife/PE",
            "police_action": police_action,
        })

    return pd.DataFrame(registros)


def main():
    df = gerar_base()
    output_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "eventos.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Base de exemplo gerada: {len(df)} registros em {output_path}")
    print(f"Bairros: {df['neighborhood'].nunique()}")
    print(f"Periodo: {df['data'].min()} a {df['data'].max()}")
    print(f"Tipos: {df['main_reason'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
