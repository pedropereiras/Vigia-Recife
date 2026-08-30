# -*- coding: utf-8 -*-
"""
Mapa interativo por bairro/quadra com curva de risco por horário.

Gera um mapa Folium com:
  - Marcadores coloridos por volume de ocorrências (quartis)
  - Popup com perfil resumido do bairro
  - Gráfico inline de curva de risco por hora (top 10 bairros)
  - Camada de calor (heatmap) ativável
"""

from pathlib import Path

import pandas as pd
import folium
from folium.plugins import HeatMap

from src.config import CENTRO_RECIFE_LAT, CENTRO_RECIFE_LON, FIGURES_DIR


def _curva_risco_html(df_bairro: pd.DataFrame, bairro: str) -> str:
    horas = df_bairro["hora"].dropna()
    if horas.empty:
        return "<p style='color:#999'>Sem dados de horário</p>"

    contagem = horas.value_counts().sort_index()
    todos_horas = pd.Series(0, index=range(24))
    todos_horas.update(contagem)
    max_val = todos_horas.max()
    if max_val == 0:
        max_val = 1

    largura = 220
    altura = 60
    bar_w = largura / 24

    svg_parts = [f'<svg width="{largura}" height="{altura + 15}" xmlns="http://www.w3.org/2000/svg">']
    svg_parts.append(f'<text x="{largura//2}" y="10" text-anchor="middle" font-size="9" fill="#333">{bairro} — perfil por hora</text>')

    for h in range(24):
        val = todos_horas.get(h, 0)
        h_bar = (val / max_val) * altura if max_val > 0 else 0
        x = h * bar_w
        y = altura - h_bar
        cor = "#B71C1C" if val >= max_val * 0.7 else ("#FFA726" if val >= max_val * 0.4 else "#90CAF9")
        svg_parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w - 1:.1f}" height="{h_bar:.1f}" fill="{cor}" rx="1"/>')

    for h in [0, 6, 12, 18, 23]:
        svg_parts.append(f'<text x="{h * bar_w + bar_w/2:.1f}" y="{altura + 12}" text-anchor="middle" font-size="7" fill="#666">{h}h</text>')

    svg_parts.append("</svg>")
    return "".join(svg_parts)


def _cor_por_quartil(valor, limites):
    if valor <= limites[0]:
        return "#90CAF9"
    elif valor <= limites[1]:
        return "#FFA726"
    elif valor <= limites[2]:
        return "#FF7043"
    else:
        return "#B71C1C"


def _perfil_popup(df_bairro: pd.DataFrame) -> str:
    total = len(df_bairro)
    tipos = df_bairro["main_reason"].value_counts().head(3)
    tipo_str = "<br>".join([f"  {t}: {c}" for t, c in tipos.items()]) if not tipos.empty else "N/D"

    idade = df_bairro["age"].mean() if "age" in df_bairro.columns else None
    idade_str = f"{idade:.1f} anos" if pd.notna(idade) else "N/D"

    genero = df_bairro["genre"].mode()
    gen_str = genero.iloc[0] if not genero.empty else "N/D"

    pct_noite = (df_bairro["periodo"] == "NOITE").mean() * 100 if "periodo" in df_bairro.columns else 0

    return f"""
    <div style="font-family:Arial,sans-serif;font-size:12px;width:220px">
      <b style="font-size:14px;color:#B71C1C">{df_bairro['neighborhood'].iloc[0]}</b><br>
      <b>Total:</b> {total} ocorrências<br>
      <b>Idade média:</b> {idade_str}<br>
      <b>Gênero predominante:</b> {gen_str}<br>
      <b>% período noturno:</b> {pct_noite:.0f}%<br>
      <hr style="margin:4px 0">
      <b>Top tipos:</b><br>{tipo_str}
    </div>
    """


def criar_mapa_interativo(
    df: pd.DataFrame,
    caminho_saida=None,
    top_n_curva: int = 10,
    incluir_heatmap: bool = True,
) -> folium.Map:
    df_geo = df.dropna(subset=["latitude", "longitude", "neighborhood"]).copy()
    if df_geo.empty:
        print("Nenhum dado com coordenadas disponível para mapa interativo.")
        return folium.Map(location=[CENTRO_RECIFE_LAT, CENTRO_RECIFE_LON], zoom_start=12)

    mapa = folium.Map(
        location=[CENTRO_RECIFE_LAT, CENTRO_RECIFE_LON],
        zoom_start=12,
        tiles="cartodbpositron",
    )

    stats_bairros = (
        df_geo.groupby("neighborhood")
        .agg(
            ocorrencias=("id", "count"),
            lat=("latitude", "mean"),
            lon=("longitude", "mean"),
        )
        .query("ocorrencias >= 5")
    )

    if stats_bairros.empty:
        print("Nenhum bairro com ocorrências suficientes para mapa.")
        return mapa

    q25, q50, q75 = stats_bairros["ocorrencias"].quantile([0.25, 0.5, 0.75])
    limites = [q25, q50, q75]

    fg_bairros = folium.FeatureGroup(name="Bairros (volume)")

    for bairro, row in stats_bairros.iterrows():
        df_b = df_geo[df_geo["neighborhood"] == bairro]
        cor = _cor_por_quartil(row["ocorrencias"], limites)
        popup_html = _perfil_popup(df_b)

        if bairro in stats_bairros.nlargest(top_n_curva, "ocorrencias").index:
            popup_html += _curva_risco_html(df_b, bairro)

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=max(5, min(25, row["ocorrencias"] / 8)),
            color=cor,
            fill=True,
            fill_color=cor,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{bairro}: {row['ocorrencias']} ocorrências",
        ).add_to(fg_bairros)

    fg_bairros.add_to(mapa)

    legenda_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:white;padding:10px;border:1px solid #ccc;border-radius:5px;
                font-size:11px;font-family:Arial">
      <b>Volume de ocorrências</b><br>
      <span style="color:#90CAF9">&#9679;</span> &le; Q1 (baixo)<br>
      <span style="color:#FFA726">&#9679;</span> Q1-Q50<br>
      <span style="color:#FF7043">&#9679;</span> Q50-Q75<br>
      <span style="color:#B71C1C">&#9679;</span> &ge; Q75 (alto)
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(legenda_html))

    if incluir_heatmap:
        fg_heat = folium.FeatureGroup(name="Calor (heatmap)", show=False)
        heat_data = df_geo[["latitude", "longitude"]].values.tolist()
        HeatMap(heat_data, radius=12, blur=18, max_zoom=13).add_to(fg_heat)
        fg_heat.add_to(mapa)

    folium.LayerControl(collapsed=False).add_to(mapa)

    if caminho_saida is None:
        caminho_saida = FIGURES_DIR / "mapa_interativo.html"
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    mapa.save(str(caminho_saida))
    print(f"Mapa interativo salvo em: {caminho_saida}")

    return mapa
