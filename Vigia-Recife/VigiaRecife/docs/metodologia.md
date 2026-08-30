# Metodologia — Vigia Recife

Este documento consolida, em um único lugar citável, as decisões metodológicas
tomadas ao longo do desenvolvimento da pipeline. Cada decisão está implementada
no módulo indicado — em caso de dúvida sobre "por que o código faz X", a
resposta deve estar aqui.

## 1. Artefato do horário das 21h

**Achado:** ~64% dos registros têm horário cravado exatamente em 21:00:00 —
16x mais que a segunda hora mais frequente.

**Decisão:** tratado como valor padrão do sistema de origem (não horário
real). Os registros são mantidos na base e sinalizados via `hora_estimada`
(booleano); toda análise dependente de horário usa exclusivamente
`hora_valida` / `hora`, que é `NaN` para esses casos.

**Implementado em:** `src/tratamento.py::tratar_hora_estimada`

## 2. Idades biologicamente implausíveis

**Decisão:** idades `< 0` ou `> 110` anos tornam-se `NaN`. O registro
permanece na base para as demais variáveis — não é descartado por completo.

**Implementado em:** `src/tratamento.py::tratar_idades`

## 3. Subnotificação racial

**Achado:** 72,9% dos registros de `race` vêm como "NÃO IDENTIFICADO".

**Decisão:** a categoria é mantida e exibida separadamente em todos os
gráficos (nunca removida silenciosamente). Leituras sobre desigualdade racial
usam apenas o subconjunto identificado, com o tamanho da amostra sempre
reportado ao lado do percentual.

**Implementado em:** `src/graficos.py::grafico_raca`,
`grafico_raca_apenas_identificada`

## 4. Escolha de k na clusterização de bairros

**Decisão:** k é escolhido via método do cotovelo (inércia) combinado com
coeficiente de silhueta, testando k de 2 a 8 — não fixado arbitrariamente.

**Ressalva transparente:** a silhueta mais alta tende a indicar k=2
(agrupamento binário, mais separado estatisticamente), enquanto valores de k
maiores (ex.: k=4) preservam narrativa mais rica para o produto, ao custo de
menor separação estatística. Ambas as leituras devem ser comunicadas juntas
ao apresentar os clusters.

**Implementado em:** `src/clusterizacao.py::escolher_k`

## 5. Volume mínimo em agregações por bairro/tipo

**Decisão:** bairros/tipos com poucas ocorrências são excluídos de rankings e
da clusterização, para evitar que ruído estatístico de amostras pequenas
distorça a leitura.

| Contexto | Limiar mínimo | Constante |
|---|---|---|
| Clusterização de bairros | 10 ocorrências | `MIN_OCORRENCIAS_CLUSTER` |
| Ranking de ação policial por bairro | 20 ocorrências | `MIN_OCORRENCIAS_BAIRRO` |
| Ranking de ação policial por tipo | 10 ocorrências | `MIN_OCORRENCIAS_TIPO` |

**Implementado em:** `src/config.py`

## 6. Teste estatístico de tendência temporal

**Decisão:** a leitura de "crescimento" ou "queda" na série mensal nunca é
feita por inspeção visual do gráfico — sempre por regressão linear
(`scipy.stats.linregress`) com limiar de significância p < 0,05.

**Achado (base atual):** sem tendência estatisticamente significativa
(p ≈ 0,89) no período coberto.

**Implementado em:** `src/series_temporais.py::testar_tendencia`

## 7. Privacidade e risco de reidentificação

A base bruta contém endereço, coordenadas precisas, data completa, idade,
raça e gênero no mesmo registro — combinação que pode permitir identificar
vítimas em bairros pequenos. Antes de publicar qualquer dado tratado
publicamente:

- remover a coluna `address`;
- arredondar `latitude`/`longitude` para 3 casas decimais;
- nunca publicar o CSV bruto original (`data/raw/`) — apenas código e,
  quando necessário, uma versão anonimizada de `data/processed/`.
