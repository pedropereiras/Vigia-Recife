# Vigia Recife

**Plataforma de Inteligência Urbana para Análise da Violência no Recife**

O Vigia Recife transforma dados públicos de segurança em informação estratégica
e acionável, conectando cidadãos, gestão pública e policiamento em um mesmo
ecossistema de dados. O objetivo é apoiar a tomada de decisão em segurança
pública com evidência, não com percepção.

---

## Estrutura do repositório

```
VigiaRecife/
├── main.py                  # ponto único de entrada — roda a pipeline completa
├── requirements.txt
├── LICENSE
│
├── src/                     # código-fonte modular (fonte da verdade da lógica)
│   ├── config.py              # caminhos, paleta de cores, constantes de domínio
│   ├── coleta.py               # leitura da base bruta
│   ├── limpeza.py               # padronização de texto, duplicatas, coordenadas
│   ├── tratamento.py            # datas, idades, artefato de horário (21h)
│   ├── features.py              # engenharia de atributos temporais
│   ├── estatisticas.py          # estatística descritiva
│   ├── graficos.py              # todas as visualizações, incl. pirâmide etária
│   ├── clusterizacao.py         # correlação + clusterização comportamental (KMeans)
│   ├── series_temporais.py      # série mensal, média móvel, teste de tendência
│   ├── acao_policial.py         # indicadores de resposta policial
│   ├── relatorio.py             # consolidação do relatório de saída
│   ├── integracao_externa.py    # integração com SDS-PE (CVLI) e CTTU (trânsito)
│   ├── mapa_interativo.py       # mapa Folium interativo com curva de risco por hora
│   ├── relato_cidadao.py        # relato cidadão com verificação comunitária
│   ├── painel_gestao.py         # painel HTML para prefeitura com triagem automática
│   └── protocolo_acompanhamento.py  # protocolo público de acompanhamento de relatos
│
├── notebooks/
│   └── VigiaRecife.ipynb    # notebook narrativo — importa de src/, não redefine lógica
│
├── data/                    # NUNCA versionado (ver .gitignore)
│   ├── raw/                   # eventos.csv original + bases externas (CTTU, SDS-PE)
│   └── processed/              # saída da pipeline (eventos_tratados.csv, relatos.json, etc.)
│
├── outputs/
│   ├── figures/                # todos os .png gerados + mapa_interativo.html
│   ├── painel_gestao.html      # painel de gestão da prefeitura
│   └── relatorio.txt
│
├── docs/
│   ├── metodologia.md          # decisões metodológicas documentadas e justificadas
│   ├── Vigia_Recife_Documentacao_Tecnica.docx
│   └── Vigia_Recife_Relatorio_Projeto.pdf
│
└── tests/
    ├── test_limpeza.py
    ├── test_tratamento.py
    └── test_series_temporais.py
```

**Regra de ouro do projeto:** toda lógica de negócio mora em `src/`. O notebook,
o `main.py` e os testes apenas *chamam* essas funções — nunca redefinem a
mesma lógica em mais de um lugar.

## Como executar

```bash

cd "C:\Users\pedro\OneDrive\Desktop\Vigia-Recife\VigiaRecife"
.\.venv\Scripts\python -m pytest tests/ -q

cd "C:\Users\pedro\OneDrive\Desktop\Vigia-Recife\VigiaRecife"
.\.venv\Scripts\activate.ps1
python main.py

cd "C:\Users\pedro\OneDrive\Desktop\Vigia-Recife\VigiaRecife"

C:\Users\pedro\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python scripts\gerar_dados_exemplo.py
python main.py

dir outputs
dir outputs\figures
start outputs\figures\top_bairros.png
start outputs\figures\serie_mensal.png
start outputs\figures\acao_por_tipo.png
outputs\figures\mapa_interativo.html
start outputs\figures\mapa_interativo.html
ii outputs\figures\mapa_interativo.html
outputs\painel_gestao.html
start outputs\painel_gestao.html
ii outputs\painel_gestao.html
ii outputs
ii outputs\figures
code outputs\figures


python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# coloque o CSV bruto em data/raw/eventos.csv, então:
python main.py
```

Isso gera, em `data/processed/` e `outputs/`, todos os indicadores tratados,
os gráficos e o relatório de texto — de forma 100% reproduzível.

Para rodar os testes automatizados:

```bash
pytest tests/ -v
```

## Fonte de dados

Coletados via **API do Fogo Cruzado** (`api.fogocruzado.org.br`), plataforma
que mapeia tiroteios e disparos de arma de fogo em Pernambuco desde 2018, com
verificação por equipe especializada.

> Antes de redistribuir dados tratados publicamente, confirme os termos de uso
> junto à equipe do Fogo Cruzado — ver `docs/metodologia.md`, seção 7.

**Bases planejadas para próximas integrações:** estatísticas oficiais da
SDS-PE (CVLI), acidentes de trânsito da CTTU e GeoJSON oficial de bairros do
Recife.

## Metodologia

Todas as decisões de tratamento de dados (artefato de horário, subnotificação
racial, escolha de k na clusterização, teste de tendência, limiares mínimos de
agregação) estão documentadas e justificadas em **[`docs/metodologia.md`](docs/metodologia.md)**.

## Principais achados (base 2018–2026)

- 5.889 registros analisados em 91 bairros do Recife
- Sem tendência estatisticamente significativa de crescimento ou queda no período (p ≈ 0,89)
- Apenas 5–6% das ocorrências têm ação policial registrada, com forte desigualdade entre bairros
- Clusterização comportamental revela perfis distintos de violência entre bairros com volume total semelhante

*(resultados completos em `outputs/relatorio.txt` após execução da pipeline)*

## Roadmap

- [x] Pipeline de dados modular, testada e reproduzível
- [x] EDA, clusterização orientada a dados (cotovelo + silhueta) e teste de tendência
- [x] Integração com dados oficiais da SDS-PE e CTTU
- [x] Mapa interativo por bairro/quadra com curva de risco por horário
- [x] Módulo de relato cidadão com verificação comunitária
- [x] Painel de gestão para a prefeitura com triagem automática de demandas
- [x] Protocolo de acompanhamento público de status de relato

## Considerações éticas

Este projeto lida com dados sensíveis de violência e vitimização. O desenho da
plataforma evita apresentar bairros inteiros como "zonas de perigo" de forma
estática — o foco está em padrões comportamentais, temporais e de resposta
institucional, para reduzir o risco de estigmatização territorial e reforçar
ação de gestão pública em vez de vigilância indiscriminada.

Antes de publicar qualquer dado tratado publicamente, ver as recomendações de
anonimização em `docs/metodologia.md`, seção 7.

## Autoria

Desenvolvido por Pedro Pereira — estudante de Banco de Dados com ênfase em
Data Science e IA (CESAR School, Recife).

## Licença

Código sob licença MIT (ver `LICENSE`). Os dados em `data/` seguem os termos
de uso da fonte original (API do Fogo Cruzado), não desta licença.

