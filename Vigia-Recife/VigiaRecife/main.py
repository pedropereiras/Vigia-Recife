# -*- coding: utf-8 -*-
"""
main.py
=======
Ponto de entrada único do projeto Vigia Recife. Executa a pipeline completa,
do dado bruto (data/raw/eventos.csv) aos indicadores finais (data/processed/
e outputs/), imprimindo o relatório consolidado no console.

Uso:
    python main.py

Todo o código de negócio vive em src/ — este arquivo apenas orquestra a
ordem de execução, sem conter lógica própria. Isso é o que garante que o
notebook (notebooks/VigiaRecife.ipynb), os testes (tests/) e este script
produzam sempre o mesmo resultado: todos chamam as mesmas funções.
"""

from src.config import (
    DATA_PROCESSED_DIR, FIGURES_DIR, OUTPUTS_DIR, RELATORIO_FILENAME,
    ensure_dirs,
)
from src.coleta import carregar_base_bruta
from src.limpeza import anonimizar_base, limpar_base
from src.tratamento import tratar_base
from src.features import criar_features_temporais
from src.estatisticas import (
    estatisticas_idade,
    idade_media_por_bairro,
    idade_media_por_tipo_ocorrencia,
    distribuicao_por_dia_semana,
)
from src.graficos import (
    grafico_bairro,
    perfil_temporal,
    grafico_genero,
    grafico_raca,
    grafico_raca_apenas_identificada,
    montar_piramide,
    plot_piramide,
    piramide_bairro,
    painel_top_bairros,
)
from src.clusterizacao import construir_perfil_bairros, clusterizar_bairros, resumo_por_cluster
from src.series_temporais import serie_mensal_completa, grafico_serie_mensal, grafico_media_movel, verificar_tendencia
from src.acao_policial import acao_por_bairro, acao_por_tipo, grafico_acao_por_tipo
from src.relatorio import ConstrutorRelatorio
from src.integracao_externa import integrar_bases, resumo_integracao
from src.mapa_interativo import criar_mapa_interativo
from src.painel_gestao import gerar_html_painel, _carregar_relatos as carregar_relatos_painel
from src.relato_cidadao import estatisticas_relatos


def main():
    try:
        ensure_dirs()
        relatorio = ConstrutorRelatorio()

        # 1-2. Coleta -------------------------------------------------------
        df = carregar_base_bruta()
        relatorio.titulo("BASE BRUTA")
        relatorio.linha(f"Registros: {df.shape[0]} | Colunas: {df.shape[1]}")

        # 3-4. Limpeza --------------------------------------------------------
        df_limpo = limpar_base(df)

        # 5-6. Tratamento (datas, idades, artefato de hora) --------------------
        df_limpo = tratar_base(df_limpo)

        # 7. Engenharia de atributos -------------------------------------------
        df_analise = criar_features_temporais(df_limpo)

        relatorio.titulo("RESUMO DA LIMPEZA E TRATAMENTO")
        relatorio.linha(f"Bairros únicos: {df_limpo['neighborhood'].nunique()}")
        relatorio.linha(f"Período: {df_limpo['data'].min()} até {df_limpo['data'].max()}")
        relatorio.linha(
            f"Registros com hora estimada (artefato 21h): "
            f"{df_limpo['hora_estimada'].sum()} ({df_limpo['hora_estimada'].mean():.1%})"
        )

        # 8. Estatística descritiva --------------------------------------------
        relatorio.titulo("ESTATÍSTICAS DE IDADE")
        relatorio.linha(estatisticas_idade(df_analise))

        # 9. EDA -----------------------------------------------------------------
        relatorio.titulo("TOP 15 BAIRROS COM MAIS OCORRÊNCIAS")
        top_bairros = grafico_bairro(df_analise, top=15, caminho=FIGURES_DIR / "top_bairros.png")
        relatorio.linha(top_bairros.to_string())

        relatorio.titulo("OCORRÊNCIAS POR ANO")
        serie_anual = perfil_temporal(df_analise, caminho=FIGURES_DIR / "ocorrencias_por_ano.png")
        relatorio.linha(serie_anual.to_string())

        grafico_genero(df_analise, caminho=FIGURES_DIR / "genero.png")
        grafico_raca(df_analise, caminho=FIGURES_DIR / "raca.png")
        grafico_raca_apenas_identificada(df_analise, caminho=FIGURES_DIR / "raca_identificada.png")

        relatorio.titulo("PAINEL — TOP 5 BAIRROS")
        relatorio.linha(painel_top_bairros(df_analise, top=5).to_string())

        relatorio.titulo("DISTRIBUIÇÃO POR DIA DA SEMANA")
        relatorio.linha(distribuicao_por_dia_semana(df_analise).to_string())

        # Pirâmide etária ---------------------------------------------------------
        pir_geral = montar_piramide(df_analise)
        if pir_geral is not None:
            plot_piramide(pir_geral, "Pirâmide Etária das Vítimas — Recife (geral)", FIGURES_DIR / "piramide_geral.png")
            relatorio.titulo("PIRÂMIDE ETÁRIA (GERAL)")
            relatorio.linha(pir_geral.to_string())

        if not top_bairros.empty:
            bairro_exemplo = top_bairros.index[-1]
            piramide_bairro(df_analise, bairro_exemplo, FIGURES_DIR / f"piramide_{bairro_exemplo}.png")

        # 10. Clusterização --------------------------------------------------------
        perfil = construir_perfil_bairros(df_analise)
        perfil_com_cluster = None
        if perfil.empty:
            print("Aviso: Nenhum bairro com ocorrências suficientes para clusterização.")
        else:
            perfil_com_cluster, detalhes_k = clusterizar_bairros(
                perfil,
                caminho_elbow=FIGURES_DIR / "elbow_silhueta.png",
                caminho_pca=FIGURES_DIR / "clusters_pca.png",
            )
            relatorio.titulo("ESCOLHA DE k (COTOVELO + SILHUETA)")
            relatorio.linha(detalhes_k)
            relatorio.titulo(f"RESUMO DOS CLUSTERS (k={detalhes_k['k_escolhido']})")
            relatorio.linha(resumo_por_cluster(perfil_com_cluster).to_string())

        # Séries temporais -------------------------------------------------------------
        serie = serie_mensal_completa(df_analise)
        grafico_serie_mensal(serie, caminho=FIGURES_DIR / "serie_mensal.png")
        grafico_media_movel(serie, caminho=FIGURES_DIR / "media_movel.png")
        try:
            tendencia = verificar_tendencia(serie)
            relatorio.titulo("TESTE DE TENDÊNCIA TEMPORAL")
            relatorio.linha(tendencia)
        except ValueError as e:
            print(f"Aviso: {e}")

        # 11. Ação policial ---------------------------------------------------------------
        tabela_bairro = acao_por_bairro(df_analise)
        tabela_tipo = acao_por_tipo(df_analise)
        grafico_acao_por_tipo(tabela_tipo, caminho=FIGURES_DIR / "acao_por_tipo.png")

        relatorio.titulo("TOP 10 BAIRROS — MAIOR % AÇÃO POLICIAL")
        relatorio.linha(tabela_bairro.head(10).to_string())
        relatorio.titulo("TOP 10 BAIRROS — MENOR % AÇÃO POLICIAL")
        relatorio.linha(tabela_bairro.tail(10).sort_values("pct_acao").to_string())
        relatorio.titulo("AÇÃO POLICIAL POR TIPO DE OCORRÊNCIA")
        relatorio.linha(tabela_tipo.to_string())

        # Persistência -----------------------------------------------------------------------
        anonimizar_base(df_analise).to_csv(
            DATA_PROCESSED_DIR / "eventos_tratados.csv", index=False
        )
        if perfil_com_cluster is not None:
            perfil_com_cluster.to_csv(DATA_PROCESSED_DIR / "bairros_cluster.csv")
        tabela_bairro.to_csv(DATA_PROCESSED_DIR / "acao_policial_por_bairro.csv")
        relatorio.salvar(OUTPUTS_DIR / RELATORIO_FILENAME)
        relatorio.imprimir()

        # 12. Integração com bases externas ------------------------------------
        df_integrado = integrar_bases(df_fc=df_analise)
        if not df_integrado.empty:
            resumo_int = resumo_integracao(df_integrado)
            relatorio.titulo("INTEGRAÇÃO COM BASES EXTERNAS")
            relatorio.linha(f"Total registros integrados: {len(df_integrado)}")
            if not resumo_int.empty:
                relatorio.linha(resumo_int.to_string())
            df_integrado.to_csv(DATA_PROCESSED_DIR / "base_integrada.csv", index=False)

        # 13. Mapa interativo --------------------------------------------------
        criar_mapa_interativo(
            df_analise,
            caminho_saida=FIGURES_DIR / "mapa_interativo.html",
        )

        # 14. Painel de gestão -------------------------------------------------
        df_relatos = carregar_relatos_painel()
        gerar_html_painel(
            df_fc=df_analise,
            df_relatos=df_relatos,
            caminho_saida=OUTPUTS_DIR / "painel_gestao.html",
        )
        stats_relatos = estatisticas_relatos()
        relatorio.titulo("RELATOS CIDADÃOS")
        relatorio.linha(f"Total de relatos: {stats_relatos.get('total', 0)}")
        if stats_relatos.get("total", 0) > 0:
            relatorio.linha(f"Por status: {stats_relatos.get('por_status', {})}")
            relatorio.linha(f"Por tipo: {stats_relatos.get('por_tipo', {})}")

        print(f"\nPipeline concluída. Saídas em: {OUTPUTS_DIR}")

    except FileNotFoundError as e:
        print(f"ERRO: Arquivo não encontrado — {e}")
        raise
    except ValueError as e:
        print(f"ERRO DE DADOS: {e}")
        raise
    except Exception as e:
        print(f"ERRO INESPERADO na pipeline: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    main()
