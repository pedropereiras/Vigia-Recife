import pandas as pd

from src.config import RAW_CSV_PATH


def carregar_base_bruta(caminho: str | None = None) -> pd.DataFrame:
    
    caminho_final = caminho or RAW_CSV_PATH

    if not str(caminho_final).endswith(".csv"):
        raise ValueError("Este projeto atualmente só lê arquivos CSV.")

    df = pd.read_csv(caminho_final)
    return df


if __name__ == "__main__":
    base = carregar_base_bruta()
    print(f"Base carregada: {base.shape[0]} linhas, {base.shape[1]} colunas.")
