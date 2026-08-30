# Guia Terminal — Vigia Recife

Passo a passo de como executar cada etapa da pipeline pelo terminal.

---

## 0. Preparacao (uma unica vez)

```bash
# Navegar ate a pasta do projeto
cd C:\Users\pedro\OneDrive\Desktop\Vigia-Recife

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.venv\Scripts\activate

# Instalar dependencias
pip install -r VigiaRecife/requirements.txt
```

---

## 1. Gerar dados de exemplo (opcional)

Se voce nao tem o `eventos.csv` real, gere dados sinteticos:

```bash
cd VigiaRecife
python scripts/gerar_dados_exemplo.py
```

**O que faz:** Cria `data/raw/eventos.csv` com 2000 registros simulados
(25 bairros, 2018-2025, com coordenadas, tipos, genero, raca, idade).

**Saida esperada:**
```
Base de exemplo gerada: 2000 registros em C:\...\data\raw\eventos.csv
Bairros: 25
Periodo: 01/01/2018 01:47:20 a 28/12/2025 16:16:48
Tipos: {'HOMICIDIO/TENTATIVA': 674, 'DISPARO': 533, ...}
```

---

## 2. Rodar a pipeline completa

```bash
cd VigiaRecife
python main.py
```

**O que faz (14 etapas encadeadas):**

| Etapa | O que acontece | Arquivo gerado |
|-------|----------------|----------------|
| 1-2. Coleta | Le `data/raw/eventos.csv` | — |
| 3-4. Limpeza | Padroniza texto, remove duplicatas, checa coordenadas | — |
| 5-6. Tratamento | Converte datas, filtra idades, marca hora estimada (21h) | — |
| 7. Features | Cria: ano, mes, dia_semana, trimestre, periodo, ageGroup | — |
| 8. Estatisticas | Media, mediana, moda, desvio da idade | — |
| 9. EDA + Graficos | Top bairros, serie anual, genero, raca, piramide etaria | `outputs/figures/*.png` |
| 10. Clusterizacao | KMeans com escolha de k (cotovelo + silhueta) | `outputs/figures/elbow_silhueta.png`, `clusters_pca.png` |
| 11. Series Temporais | Serie mensal, media movel, teste de tendencia (linregress) | `outputs/figures/serie_mensal.png`, `media_movel.png` |
| 12. Acao Policial | % resposta policial por bairro e tipo | `outputs/figures/acao_por_tipo.png` |
| 13. Persistencia | Salva CSVs tratados e relatorio | `data/processed/eventos_tratados.csv`, `outputs/relatorio.txt` |
| 14. Integracao | Tenta cargar CTTU e SDS-PE (pula se nao existir) | `data/processed/base_integrada.csv` |
| 15. Mapa Interativo | Mapa Folium com marcadores e heatmap | `outputs/figures/mapa_interativo.html` |
| 16. Painel Gestao | Dashboard HTML com KPIs e triagem | `outputs/painel_gestao.html` |

**Saida no console:** O relatorio completo e impresso linha a linha.

**Saida em arquivos:**
```
data/processed/
  ├── eventos_tratados.csv      (base anonimizada)
  ├── bairros_cluster.csv       (clusters de bairros)
  ├── acao_policial_por_bairro.csv
  └── base_integrada.csv

outputs/
  ├── relatorio.txt             (relatorio consolidado)
  ├── painel_gestao.html        (dashboard HTML)
  └── figures/
      ├── top_bairros.png
      ├── ocorrencias_por_ano.png
      ├── genero.png
      ├── raca.png
      ├── raca_identificada.png
      ├── piramide_geral.png
      ├── piramide_[bairro].png
      ├── elbow_silhueta.png
      ├── clusters_pca.png
      ├── serie_mensal.png
      ├── media_movel.png
      ├── acao_por_tipo.png
      └── mapa_interativo.html
```

---

## 3. Rodar testes

```bash
cd VigiaRecife
python -m pytest tests/ -v
```

**O que faz:** Executa 48 testes automatizados cobrindo:
- `test_limpeza.py` — padronizacao de texto, duplicatas
- `test_tratamento.py` — datas, idades, hora estimada
- `test_series_temporais.py` — tendencia, series insuficientes
- `test_features.py` — classificacao de idade, periodo do dia, colunas criadas
- `test_estatisticas.py` — estatisticas de idade, distribuicao por bairro/dia
- `test_acao_policial.py` — filtro minimo, percentuais
- `test_relato_cidadao.py` — registro, consulta, verificacao, estatisticas
- `test_relatorio.py` — construcao, impressao, salvamento

**Saida esperada:**
```
48 passed, 4 warnings in 3.37s
```

---

## 4. Rodar um modulo individualmente

Cada modulo pode ser testado isoladamente via Python interativo ou script:

### 4.1 Coleta (carregar dados)
```bash
cd VigiaRecife
python -c "from src.coleta import carregar_base_bruta; df = carregar_base_bruta(); print(df.shape, df.columns.tolist())"
```

### 4.2 Limpeza
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
df = limpar_base(carregar_base_bruta())
print('Shape apos limpeza:', df.shape)
"
```

### 4.3 Tratamento
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
from src.tratamento import tratar_base, relatorio_nulos
df = tratar_base(limpar_base(carregar_base_bruta()))
print(relatorio_nulos(df))
"
```

### 4.4 Features (engenharia de atributos)
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
from src.tratamento import tratar_base
from src.features import criar_features_temporais
df = criar_features_temporais(tratar_base(limpar_base(carregar_base_bruta())))
print('Colunas:', df.columns.tolist())
print('ageGroup:', df['ageGroup'].value_counts().to_dict())
"
```

### 4.5 Estatisticas
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
from src.tratamento import tratar_base
from src.features import criar_features_temporais
from src.estatisticas import estatisticas_idade, distribuicao_por_dia_semana
df = criar_features_temporais(tratar_base(limpar_base(carregar_base_bruta())))
print('Idade:', estatisticas_idade(df))
print('Dias:', distribuicao_por_dia_semana(df).to_dict())
"
```

### 4.6 Graficos (salvar individualmente)
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
from src.tratamento import tratar_base
from src.features import criar_features_temporais
from src.graficos import grafico_bairro
df = criar_features_temporais(tratar_base(limpar_base(carregar_base_bruta())))
grafico_bairro(df, top=10, caminho='outputs/figures/teste_bairro.png')
print('Grafico salvo!')
"
```

### 4.7 Clusterizacao
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
from src.tratamento import tratar_base
from src.features import criar_features_temporais
from src.clusterizacao import construir_perfil_bairros, clusterizar_bairros, resumo_por_cluster
df = criar_features_temporais(tratar_base(limpar_base(carregar_base_bruta())))
perfil = construir_perfil_bairros(df)
perfil_c, detalhes = clusterizar_bairros(perfil)
print('k escolhido:', detalhes['k_escolhido'])
print(resumo_por_cluster(perfil_c))
"
```

### 4.8 Series Temporais + Tendencia
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
from src.tratamento import tratar_base
from src.features import criar_features_temporais
from src.series_temporais import serie_mensal_completa, verificar_tendencia
df = criar_features_temporais(tratar_base(limpar_base(carregar_base_bruta())))
serie = serie_mensal_completa(df)
print('Meses na serie:', len(serie))
print('Tendencia:', verificar_tendencia(serie))
"
```

### 4.9 Acao Policial
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
from src.tratamento import tratar_base
from src.features import criar_features_temporais
from src.acao_policial import acao_por_bairro, acao_por_tipo
df = criar_features_temporais(tratar_base(limpar_base(carregar_base_bruta())))
print('Por bairro:')
print(acao_por_bairro(df).head(5))
print('Por tipo:')
print(acao_por_tipo(df))
"
```

### 4.10 Mapa Interativo
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
from src.tratamento import tratar_base
from src.features import criar_features_temporais
from src.mapa_interativo import criar_mapa_interativo
df = criar_features_temporais(tratar_base(limpar_base(carregar_base_bruta())))
criar_mapa_interativo(df, caminho_saida='outputs/figures/meu_mapa.html')
print('Mapa salvo! Abra no navegador.')
"
```

### 4.11 Relato Cidadao
```bash
cd VigiaRecife
python -c "
from src.relato_cidadao import registrar_relato, consultar_protocolo, listar_relatos, estatisticas_relatos

# Registrar um relato
r = registrar_relato(descricao='Tiros na rua', bairro='IBURA', tipo_ocorrencia='TIRO')
print('Protocolo:', r['protocolo'])

# Consultar
print('Consulta:', consultar_protocolo(r['protocolo']))

# Listar todos
print('Total:', len(listar_relatos()))

# Estatisticas
print('Stats:', estatisticas_relatos())
"
```

### 4.12 Painel de Gestao
```bash
cd VigiaRecife
python -c "
from src.coleta import carregar_base_bruta
from src.limpeza import limpar_base
from src.tratamento import tratar_base
from src.features import criar_features_temporais
from src.painel_gestao import gerar_html_painel
import pandas as pd
df = criar_features_temporais(tratar_base(limpar_base(carregar_base_bruta())))
gerar_html_painel(df_fc=df, df_relatos=pd.DataFrame())
print('Painel salvo!')
"
```

---

## 5. Ver o relatorio completo

```bash
cd VigiaRecife
type outputs\relatorio.txt
```

Ou abra no editor de texto:
```bash
notepad outputs\relatorio.txt
```

---

## 6. Ver os graficos

```bash
# Listar todos os graficos gerados
dir outputs\figures\*.png

# Abrir um grafico (Windows)
start outputs\figures\top_bairros.png
start outputs\figures\piramide_geral.png
start outputs\figures\clusters_pca.png

# Abrir mapa interativo no navegador
start outputs\figures\mapa_interativo.html

# Abrir painel de gestao no navegador
start outputs\painel_gestao.html
```

---

## 7. Verificar arquivos gerados

```bash
cd VigiaRecife

# Dados processados
dir data\processed\

# Graficos
dir outputs\figures\

# Relatorio
dir outputs\relatorio.txt

# Painel
dir outputs\painel_gestao.html
```

---

## Resumo dos comandos mais usados

| Comando | O que faz |
|---------|-----------|
| `python main.py` | Roda a pipeline completa |
| `python -m pytest tests/ -v` | Roda todos os 48 testes |
| `python scripts/gerar_dados_exemplo.py` | Gera dados sinteticos |
| `type outputs\relatorio.txt` | Ve o relatorio |
| `start outputs\figures\mapa_interativo.html` | Abre o mapa |
| `start outputs\painel_gestao.html` | Abre o painel |
