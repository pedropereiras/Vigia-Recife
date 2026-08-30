import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import OUTPUTS_DIR, DATA_PROCESSED_DIR


def _carregar_relatos() -> pd.DataFrame:
    caminho = DATA_PROCESSED_DIR / "relatos.json"
    if not caminho.exists():
        return pd.DataFrame()
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return pd.DataFrame(dados) if dados else pd.DataFrame()


def classificar_urgencia(df_relatos: pd.DataFrame) -> pd.DataFrame:
    if df_relatos.empty:
        return df_relatos

    df = df_relatos.copy()
    df["urgencia"] = "BAIXA"
    df.loc[df["prioridade"] == "CRITICA", "urgencia"] = "CRITICA"
    df.loc[(df["prioridade"] == "ALTA") | (df["confirmacoes"] >= 2), "urgencia"] = "ALTA"
    df.loc[(df["prioridade"] == "MEDIA") & (df["urgencia"] != "ALTA"), "urgencia"] = "MEDIA"
    df.loc[df["confirmacoes"] >= 3, "urgencia"] = "CRITICA"
    df.loc[df["contestacoes"] >= 3, "urgencia"] = "DESCARTAR"
    return df


def gerar_kpis(df_fc: pd.DataFrame, df_relatos: pd.DataFrame) -> dict:
    kpis = {}

    if not df_fc.empty:
        kpis["fc_total"] = len(df_fc)
        kpis["fc_bairros"] = df_fc["neighborhood"].nunique() if "neighborhood" in df_fc.columns else 0
        if "police_action" in df_fc.columns:
            kpis["fc_taxa_acao_policial"] = f"{df_fc['police_action'].mean() * 100:.1f}%"

    if not df_relatos.empty:
        kpis["relatos_total"] = len(df_relatos)
        kpis["relatos_abertos"] = len(df_relatos[df_relatos["status"] == "ABERTO"])
        kpis["relatos_confirmados"] = len(df_relatos[df_relatos["status"] == "CONFIRMADO"])
        if "confirmacoes" in df_relatos.columns:
            kpis["confirmacoes_total"] = int(df_relatos["confirmacoes"].sum())

    return kpis


def triagem_automatica(df_relatos: pd.DataFrame) -> pd.DataFrame:
    if df_relatos.empty:
        return pd.DataFrame()

    df = classificar_urgencia(df_relatos.copy())
    df["sugestao_acao"] = "ARQUIVAR"
    df.loc[df["urgencia"] == "MEDIA", "sugestao_acao"] = "ACOMPANHAR_COMUNIDADE"
    df.loc[df["urgencia"] == "ALTA", "sugestao_acao"] = "ENCAMINHAR_POLICIA"
    df.loc[df["urgencia"] == "CRITICA", "sugestao_acao"] = "ENCAMINHAR_POLICIA_IMEDIATO"

    urg_order = {"CRITICA": 0, "ALTA": 1, "MEDIA": 2, "BAIXA": 3, "DESCARTAR": 4}
    df["_urg_order"] = df["urgencia"].map(urg_order).fillna(5)
    df = df.sort_values(["_urg_order", "confirmacoes"], ascending=[True, False]).drop(columns=["_urg_order"])

    return df


def gerar_html_painel(
    df_fc: pd.DataFrame,
    df_relatos: pd.DataFrame,
    caminho_saida=None,
) -> str:
    if caminho_saida is None:
        caminho_saida = OUTPUTS_DIR / "painel_gestao.html"
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)

    kpis = gerar_kpis(df_fc, df_relatos)
    triagem = triagem_automatica(df_relatos)

    top_bairros_relatos = pd.DataFrame()
    if not df_relatos.empty and "bairro" in df_relatos.columns:
        top_bairros_relatos = df_relatos["bairro"].value_counts().head(10).reset_index()
        top_bairros_relatos.columns = ["bairro", "relatos"]

    top_bairros_fc = pd.DataFrame()
    if not df_fc.empty and "neighborhood" in df_fc.columns:
        top_bairros_fc = df_fc["neighborhood"].value_counts().head(10).reset_index()
        top_bairros_fc.columns = ["bairro", "ocorrencias"]

    html_parts = [f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vigia Recife - Painel de Gestao</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; color: #333; }}
  .header {{ background: linear-gradient(135deg, #B71C1C, #D32F2F); color: white; padding: 20px 30px; }}
  .header h1 {{ font-size: 24px; }}
  .header p {{ opacity: 0.85; margin-top: 4px; font-size: 13px; }}
  .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 25px; }}
  .kpi-card {{ background: white; border-radius: 8px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; }}
  .kpi-card .valor {{ font-size: 28px; font-weight: bold; color: #B71C1C; }}
  .kpi-card .label {{ font-size: 12px; color: #666; margin-top: 4px; }}
  .secao {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .secao h2 {{ font-size: 16px; color: #B71C1C; margin-bottom: 12px; border-bottom: 2px solid #ffcdd2; padding-bottom: 6px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ background: #fafafa; text-align: left; padding: 8px 10px; border-bottom: 2px solid #eee; font-weight: 600; }}
  td {{ padding: 7px 10px; border-bottom: 1px solid #f0f0f0; }}
  tr:hover {{ background: #fff8f8; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
  .badge-critica {{ background: #ffcdd2; color: #b71c1c; }}
  .badge-alta {{ background: #ffe0b2; color: #e65100; }}
  .badge-media {{ background: #fff9c4; color: #f57f17; }}
  .badge-baixa {{ background: #e8f5e9; color: #2e7d32; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  @media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>Vigia Recife - Painel de Gestao</h1>
  <p>Plataforma de Inteligencia Urbana para Seguranca Publica | Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
</div>
<div class="container">
"""]

    html_parts.append('<div class="kpis">')
    kpi_cards = [
        ("fc_total", "Fogo Cruzado - Total"),
        ("fc_bairros", "Bairros mapeados"),
        ("fc_taxa_acao_policial", "Taxa acao policial"),
        ("relatos_total", "Relatos cidadaos"),
        ("relatos_abertos", "Relatos abertos"),
        ("relatos_confirmados", "Relatos confirmados"),
        ("confirmacoes_total", "Confirmacoes comunitarias"),
    ]
    for chave, label in kpi_cards:
        valor = kpis.get(chave, "—")
        html_parts.append(f'<div class="kpi-card"><div class="valor">{valor}</div><div class="label">{label}</div></div>')
    html_parts.append('</div>')

    html_parts.append('<div class="secao"><h2>Triagem Automatica de Relatos</h2>')
    if not triagem.empty:
        html_parts.append('<table><tr><th>Protocolo</th><th>Bairro</th><th>Tipo</th><th>Confirm.</th><th>Urgencia</th><th>Sugestao</th></tr>')
        badge_map = {"CRITICA": "badge-critica", "ALTA": "badge-alta", "MEDIA": "badge-media", "BAIXA": "badge-baixa"}
        sugestao_map = {
            "ENCAMINHAR_POLICIA_IMEDIATO": "Encaminhar polícia (imediato)",
            "ENCAMINHAR_POLICIA": "Encaminhar polícia",
            "ACOMPANHAR_COMUNIDADE": "Acompanhar comunitariamente",
            "ARQUIVAR": "Arquivar",
        }
        for _, r in triagem.head(20).iterrows():
            urg = r.get("urgencia", "BAIXA")
            badge_cls = badge_map.get(urg, "badge-baixa")
            sug = sugestao_map.get(r.get("sugestao_acao", ""), "—")
            html_parts.append(
                f'<tr><td>{r.get("protocolo","")}</td><td>{r.get("bairro","")}</td>'
                f'<td>{r.get("tipo_ocorrencia","")}</td><td>{r.get("confirmacoes",0)}</td>'
                f'<td><span class="badge {badge_cls}">{urg}</span></td><td>{sug}</td></tr>'
            )
        html_parts.append('</table>')
    else:
        html_parts.append('<p style="color:#999">Nenhum relato registrado ainda.</p>')
    html_parts.append('</div>')

    html_parts.append('<div class="grid-2">')

    html_parts.append('<div class="secao"><h2>Top Bairros - Fogo Cruzado</h2>')
    if not top_bairros_fc.empty:
        html_parts.append('<table><tr><th>Bairro</th><th>Ocorrencias</th></tr>')
        for _, r in top_bairros_fc.iterrows():
            html_parts.append(f'<tr><td>{r["bairro"]}</td><td>{r["ocorrencias"]}</td></tr>')
        html_parts.append('</table>')
    else:
        html_parts.append('<p style="color:#999">Sem dados Fogo Cruzado.</p>')
    html_parts.append('</div>')

    html_parts.append('<div class="secao"><h2>Top Bairros - Relatos Cidadaos</h2>')
    if not top_bairros_relatos.empty:
        html_parts.append('<table><tr><th>Bairro</th><th>Relatos</th></tr>')
        for _, r in top_bairros_relatos.iterrows():
            html_parts.append(f'<tr><td>{r["bairro"]}</td><td>{r["relatos"]}</td></tr>')
        html_parts.append('</table>')
    else:
        html_parts.append('<p style="color:#999">Nenhum relato cidadao registrado.</p>')
    html_parts.append('</div>')

    html_parts.append('</div>')
    html_parts.append('</div></body></html>')

    html_completo = "\n".join(html_parts)
    Path(caminho_saida).write_text(html_completo, encoding="utf-8")
    print(f"Painel de gestao salvo em: {caminho_saida}")
    return str(caminho_saida)
