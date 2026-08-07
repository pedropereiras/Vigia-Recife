# Vigia Recife

**Plataforma de Inteligência Urbana para Análise da Violência no Recife**

O Vigia Recife transforma dados públicos de segurança em informação estratégica e acionável, conectando cidadãos, gestão pública e policiamento em um mesmo ecossistema de dados. O objetivo é apoiar a tomada de decisão em segurança pública com evidência, não com percepção.

---

## Motivação

Recife registra recorrentemente zonas de risco variável, mas hoje esse conhecimento fica disperso: moradores ficam desprevenidos, o policiamento atua com noção aproximada em vez de dado consolidado, e a prefeitura recebe um volume grande de notificações sem um fluxo automatizado de triagem e resposta. O Vigia Recife nasce para fechar esse ciclo — coleta, análise, visualização e retorno — em uma única plataforma.

## O que o projeto faz hoje

Este repositório contém a camada de **ciência de dados** do projeto: uma pipeline completa de coleta, limpeza, tratamento, análise exploratória e modelagem que transforma registros brutos de ocorrências em indicadores por bairro.

- Importação e exploração de dados reais de violência armada em Recife
- Limpeza e padronização (texto, duplicatas, coordenadas, datas)
- Identificação e tratamento de artefatos de qualidade nos dados (ex.: horário padrão de sistema)
- Engenharia de atributos temporais (período do dia, dia da semana, sazonalidade)
- Estatística descritiva e análise exploratória (EDA)
- Visualizações geográficas (mapa de calor) e temporais
- Clusterização comportamental de bairros (K-Means + PCA) — agrupa por **padrão de violência**, não apenas volume
- Análise de série temporal com teste estatístico de tendência (regressão linear)
- Indicadores de resposta policial por bairro e por tipo de ocorrência

## Fonte de dados

Os dados utilizados são públicos e verificados, coletados via **API do Fogo Cruzado** (`api.fogocruzado.org.br`), plataforma que mapeia tiroteios e disparos de arma de fogo em Pernambuco desde 2018, com checagem por equipe especializada.

> Este repositório não redistribui os dados brutos além do necessário para reprodutibilidade do notebook. Para uso próprio, obtenha acesso via cadastro gratuito na API oficial.

**Bases planejadas para as próximas etapas:**
- SDS-PE — estatísticas oficiais de criminalidade (CVLI, boletins mensais)
- CTTU (Prefeitura do Recife) — acidentes de trânsito com e sem vítimas
- GeoJSON oficial de bairros do Recife (dados.recife.pe.gov.br)

## Metodologia e decisões de tratamento

Todas as decisões de limpeza e tratamento são documentadas no notebook para garantir transparência e reprodutibilidade:

- **Artefato de horário:** ~64% dos registros aparecem cravados às 21h, indicando valor padrão do sistema de origem quando o horário real não é informado. Esses registros são mantidos na base, mas sinalizados e excluídos apenas das análises que dependem de horário exato.
- **Idades inválidas** (< 0 ou > 110 anos) são tratadas como ausentes, não removidas.
- **Subnotificação demográfica:** a categoria "não identificado" em raça (~73% dos registros) é mantida e analisada separadamente — não deve ser lida como grupo predominante, e sim como lacuna de preenchimento nos boletins de origem.
- **Clusterização comportamental:** o agrupamento de bairros usa atributos de perfil (período do dia, tipo de ocorrência, ação policial, fim de semana), não apenas volume total — evita que bairros com contextos de violência muito diferentes sejam agrupados só por terem número parecido de ocorrências.

## Principais achados (base 2018–2026)

- 5.889 registros analisados em 91 bairros do Recife
- Sem tendência estatisticamente significativa de crescimento ou queda no período (p = 0,89)
- Apenas 5–6% das ocorrências têm ação policial registrada, com forte desigualdade entre bairros
- Clusterização revela perfis distintos de violência entre bairros com volume total semelhante

*(resultados completos em `out/relatorio.txt` após execução da pipeline)*

## Stack técnica

| Camada | Tecnologia |
|---|---|
| Coleta e tratamento | Python, Pandas, NumPy |
| Análise estatística | SciPy |
| Machine Learning | Scikit-learn (K-Means, PCA, StandardScaler) |
| Visualização | Matplotlib, Seaborn, Folium |
| Aplicação (em desenvolvimento) | React, TypeScript, Supabase |

## Como executar

```bash
pip install pandas numpy matplotlib seaborn scikit-learn scipy folium

python run_pipeline.py
```

Os resultados (CSVs tratados, clusters por bairro, ranking de ação policial e relatório em texto) são salvos em `out/`.

## Estrutura do repositório

```
vigia-recife/
├── notebooks/
│   └── analise_exploratoria.ipynb
├── run_pipeline.py
├── out/
│   ├── eventos_tratados.csv
│   ├── bairros_cluster.csv
│   ├── acao_policial_por_bairro.csv
│   ├── top_bairros.csv
│   └── relatorio.txt
└── README.md
```

## Roadmap

- [x] Coleta e tratamento de dados reais (Fogo Cruzado)
- [x] EDA, clusterização e análise de tendência
- [ ] Integração com dados oficiais da SDS-PE e CTTU
- [ ] Mapa interativo por bairro/quadra com curva de risco por horário
- [ ] Módulo de relato cidadão com verificação comunitária
- [ ] Painel de gestão para a prefeitura com triagem automática de demandas
- [ ] Protocolo de acompanhamento público de status de relato

## Considerações éticas

Este projeto lida com dados sensíveis de violência e vitimização. O desenho da plataforma evita apresentar bairros inteiros como "zonas de perigo" de forma estática — o foco está em padrões comportamentais, temporais e de resposta institucional, para reduzir o risco de estigmatização territorial e reforçar ação de gestão pública em vez de vigilância indiscriminada.

## Autoria

Desenvolvido por Pedro Pereira.

## Licença

Licença Pública Geral GNU v3.0
