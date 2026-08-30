import pandas as pd


def padronizar_texto(df: pd.DataFrame) -> pd.DataFrame:
  
    dados = df.copy()
    colunas = dados.select_dtypes(include="object").columns

    for coluna in colunas:
        dados[coluna] = dados[coluna].astype(str).str.strip().str.upper()

    return dados


def remover_duplicatas(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    
    duplicados = df.duplicated().sum()

    if verbose:
        print(f"Registros duplicados encontrados: {duplicados}")

    dados = df.drop_duplicates()

    if verbose:
        print(f"Base após remoção: {dados.shape}")

    return dados


def checar_coordenadas(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
 
    invalidas = df[df["latitude"].isna() | df["longitude"].isna()]

    if verbose:
        print("Registros sem coordenadas:", len(invalidas))
        if len(invalidas) > 0:
            print(invalidas["neighborhood"].value_counts())

    return invalidas


def anonimizar_base(df: pd.DataFrame) -> pd.DataFrame:
  
    dados = df.copy()
    colunas_remover = [c for c in ["address"] if c in dados.columns]
    dados = dados.drop(columns=colunas_remover, errors="ignore")

    for col in ["latitude", "longitude"]:
        if col in dados.columns:
            dados[col] = dados[col].round(3)

    return dados


def limpar_base(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    
    dados = padronizar_texto(df)
    dados = remover_duplicatas(dados, verbose=verbose)
    checar_coordenadas(dados, verbose=verbose)
    return dados
