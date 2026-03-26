"""
Generador de Reportes HTML/PDF para el Módulo de Análisis Psicosocial.
Usa plantillas HTML embebidas y Playwright para exportar a PDF.
"""
import os
from datetime import datetime
from typing import Dict, Any


RISK_COLORS = {
    "Sin Riesgo": "#27ae60",
    "Bajo":       "#2ecc71",
    "Medio":      "#f39c12",
    "Alto":       "#e74c3c",
    "Muy Alto":   "#8e44ad",
}

RISK_BG = {
    "Sin Riesgo": "#eafaf1",
    "Bajo":       "#eafaf1",
    "Medio":      "#fef9e7",
    "Alto":       "#fdedec",
    "Muy Alto":   "#f4ecf7",
}


def _risk_badge(nivel: str) -> str:
    color = RISK_COLORS.get(nivel, "#95a5a6")
    bg = RISK_BG.get(nivel, "#f0f0f0")
    return (
        f'<span style="background:{bg};color:{color};border:1px solid {color};'
        f'padding:2px 8px;border-radius:12px;font-weight:600;font-size:11px;">'
        f'{nivel}</span>'
    )


def _progress_bar(score: float, color: str) -> str:
    w = min(100, max(0, score))
    return (
        f'<div style="background:#e0e0e0;border-radius:4px;height:10px;width:100%;">'
        f'<div style="width:{w}%;background:{color};border-radius:4px;height:10px;"></div>'
        f'</div>'
        f'<small style="color:#666;">{score}</small>'
    )


def _dominio_section(dominio: str, dom_data: Dict) -> str:
    nivel = dom_data.get("nivel_riesgo", "")
    score = dom_data.get("puntaje_transformado", 0)
    color = dom_data.get("color", "#95a5a6")
    dims_html = ""
    for dim_name, dim_data in dom_data.get("dimensiones", {}).items():
        d_score = dim_data.get("puntaje_transformado", 0)
        d_nivel = dim_data.get("nivel_riesgo", "")
        d_color = dim_data.get("color", "#95a5a6")
        dims_html += f"""
        <tr>
          <td style="padding:6px 8px;font-size:12px;color:#555;">{dim_name}</td>
          <td style="padding:6px 8px;text-align:center;font-size:12px;">{dim_data.get('puntaje_bruto','')}</td>
          <td style="padding:6px 8px;min-width:120px;">{_progress_bar(d_score, d_color)}</td>
          <td style="padding:6px 8px;text-align:center;">{_risk_badge(d_nivel)}</td>
        </tr>"""

    return f"""
    <div style="margin-bottom:24px;">
      <div style="background:{color};color:#fff;padding:8px 14px;border-radius:6px 6px 0 0;
                  display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:700;font-size:14px;">{dominio}</span>
        <span style="font-size:13px;">Puntaje: {score} — {_risk_badge(nivel)}</span>
      </div>
      <table style="width:100%;border-collapse:collapse;background:#fff;
                    border:1px solid #ddd;border-top:none;border-radius:0 0 6px 6px;">
        <thead>
          <tr style="background:#f5f5f5;">
            <th style="padding:7px 8px;text-align:left;font-size:11px;color:#888;">Dimensión</th>
            <th style="padding:7px 8px;font-size:11px;color:#888;">Bruto</th>
            <th style="padding:7px 8px;font-size:11px;color:#888;">Transformado</th>
            <th style="padding:7px 8px;font-size:11px;color:#888;">Nivel</th>
          </tr>
        </thead>
        <tbody>{dims_html}</tbody>
      </table>
    </div>"""


def _questionnaire_section(title: str, q_data: Dict) -> str:
    score = q_data.get("puntaje_transformado", 0)
    nivel = q_data.get("nivel_riesgo", "")
    color = q_data.get("color", "#95a5a6")
    dominios_html = ""
    for dom_name, dom_data in q_data.get("dominios", {}).items():
        dominios_html += _dominio_section(dom_name, dom_data)

    # Estrés no tiene dominios
    if not dominios_html and "bloque1_raw" in q_data:
        dominios_html = f"""
        <table style="width:100%;border-collapse:collapse;border:1px solid #ddd;border-radius:6px;">
          <tr><td style="padding:8px;font-size:12px;">Puntaje bruto bloque 1</td>
              <td style="padding:8px;font-size:12px;">{q_data.get('bloque1_raw','')}</td></tr>
          <tr style="background:#f9f9f9;"><td style="padding:8px;font-size:12px;">Paso b (ítems 9–12)</td>
              <td style="padding:8px;font-size:12px;">{q_data.get('paso_b','')}</td></tr>
          <tr><td style="padding:8px;font-size:12px;">Paso c (ítems 13–22)</td>
              <td style="padding:8px;font-size:12px;">{q_data.get('paso_c','')}</td></tr>
          <tr style="background:#f9f9f9;"><td style="padding:8px;font-size:12px;">Paso d (ítems 23–31)</td>
              <td style="padding:8px;font-size:12px;">{q_data.get('paso_d','')}</td></tr>
          <tr><td style="padding:8px;font-size:12px;font-weight:600;">Total bruto</td>
              <td style="padding:8px;font-size:12px;font-weight:600;">{q_data.get('puntaje_bruto_total','')}</td></tr>
        </table>"""

    return f"""
    <div style="page-break-inside:avoid;margin-bottom:32px;">
      <h2 style="font-size:16px;font-weight:700;color:#2c3e50;border-bottom:2px solid {color};
                 padding-bottom:6px;margin-bottom:12px;">{title}</h2>
      <div style="display:flex;gap:16px;margin-bottom:16px;align-items:center;">
        <div style="flex:1;background:{color};color:#fff;border-radius:8px;padding:14px;text-align:center;">
          <div style="font-size:28px;font-weight:800;">{score}</div>
          <div style="font-size:11px;opacity:.85;">Puntaje Transformado (0–100)</div>
        </div>
        <div style="flex:2;background:#f8f9fa;border-radius:8px;padding:14px;">
          <div style="font-size:13px;color:#666;margin-bottom:4px;">Nivel de Riesgo</div>
          <div style="font-size:18px;font-weight:700;color:{color};">{nivel}</div>
          {f"<div style='font-size:11px;color:#888;margin-top:4px;'>Baremo: {q_data.get('baremo_aplicado','')}</div>" if q_data.get('baremo_aplicado') else ''}
        </div>
      </div>
      {dominios_html}
    </div>"""


def build_individual_html(analysis: Dict) -> str:
    """Construye el HTML completo para el reporte individual."""
    nombre = analysis.get("nombre", "Desconocido")
    cedula = analysis.get("cedula", "")
    cargo  = analysis.get("cargo", "")
    area   = analysis.get("area", "")
    fecha  = datetime.fromisoformat(analysis.get("calculado_en", datetime.now().isoformat()))
    fecha_str = fecha.strftime("%d/%m/%Y %H:%M")

    cuestionarios = analysis.get("cuestionarios", {})
    total_general = analysis.get("total_general")

    # Resumen
    summary_rows = ""
    labels = {
        "estres": "Cuestionario de Estrés",
        "intralaboral": "Cuestionario Intralaboral",
        "extralaboral": "Cuestionario Extralaboral",
    }
    for key, label in labels.items():
        if key in cuestionarios:
            q = cuestionarios[key]
            nivel = q.get("nivel_riesgo", "—")
            score = q.get("puntaje_transformado", "—")
            color = q.get("color", "#95a5a6")
            summary_rows += f"""
            <tr>
              <td style="padding:8px 12px;font-size:13px;">{label}</td>
              <td style="padding:8px 12px;text-align:center;font-size:13px;">{score}</td>
              <td style="padding:8px 12px;text-align:center;">{_risk_badge(nivel)}</td>
            </tr>"""

    if total_general:
        tg_score = total_general.get("puntaje_transformado", "")
        tg_nivel = total_general.get("nivel_riesgo", "")
        tg_color = total_general.get("color", "#95a5a6")
        summary_rows += f"""
        <tr style="background:#f0f4ff;">
          <td style="padding:8px 12px;font-size:13px;font-weight:700;">
            Total General (Intra + Extra — Forma {total_general.get('forma','')})
          </td>
          <td style="padding:8px 12px;text-align:center;font-size:13px;font-weight:700;">{tg_score}</td>
          <td style="padding:8px 12px;text-align:center;">{_risk_badge(tg_nivel)}</td>
        </tr>"""

    # Secciones detalladas por cuestionario
    sections_html = ""
    if "estres" in cuestionarios:
        sections_html += _questionnaire_section("Cuestionario de Estrés", cuestionarios["estres"])
    if "intralaboral" in cuestionarios:
        forma = cuestionarios["intralaboral"].get("forma", "")
        sections_html += _questionnaire_section(f"Cuestionario Intralaboral Forma {forma}", cuestionarios["intralaboral"])
    if "extralaboral" in cuestionarios:
        sections_html += _questionnaire_section("Cuestionario Extralaboral", cuestionarios["extralaboral"])

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <style>
    @page {{ size: letter; margin: 1.5cm 2cm; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; color: #2c3e50; background: white; }}
    .cover {{ page-break-after: always; display: flex; flex-direction: column; min-height: 26cm; justify-content: space-between; }}
    .cover-header {{ background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
                     color: white; padding: 40px; border-radius: 12px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th {{ background: #f4f6fb; color: #555; font-size: 11px; padding: 8px 12px; text-align: left; }}
  </style>
</head>
<body>

<!-- PORTADA -->
<div class="cover">
  <div class="cover-header">
    <div style="font-size:11px;opacity:.7;margin-bottom:8px;">MINISTERIO DE TRABAJO · COLOMBIA</div>
    <h1 style="font-size:22px;margin:0 0 8px 0;">Reporte de Resultados</h1>
    <h2 style="font-size:17px;margin:0;font-weight:400;opacity:.9;">
      Batería de Instrumentos para la Evaluación de Factores de Riesgo Psicosocial
    </h2>
  </div>
  <div style="padding:32px 0;">
    <table style="width:100%;border:1px solid #e0e0e0;border-radius:12px;overflow:hidden;">
      <tr><td style="padding:14px 20px;background:#f8f9fa;width:40%;font-weight:600;color:#555;">Nombre</td>
          <td style="padding:14px 20px;">{nombre}</td></tr>
      <tr><td style="padding:14px 20px;background:#f8f9fa;font-weight:600;color:#555;">Cédula</td>
          <td style="padding:14px 20px;">{cedula}</td></tr>
      <tr><td style="padding:14px 20px;background:#f8f9fa;font-weight:600;color:#555;">Cargo</td>
          <td style="padding:14px 20px;">{cargo}</td></tr>
      <tr><td style="padding:14px 20px;background:#f8f9fa;font-weight:600;color:#555;">Área / Departamento</td>
          <td style="padding:14px 20px;">{area}</td></tr>
      <tr><td style="padding:14px 20px;background:#f8f9fa;font-weight:600;color:#555;">Fecha del análisis</td>
          <td style="padding:14px 20px;">{fecha_str}</td></tr>
    </table>
  </div>
  <div style="text-align:center;color:#888;font-size:11px;padding-top:16px;">
    <em>Documento confidencial — Ley 1581 de 2012 (Habeas Data)</em>
  </div>
</div>

<!-- RESUMEN EJECUTIVO -->
<div style="page-break-after:always;">
  <h2 style="font-size:18px;font-weight:700;color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:8px;">
    Resumen Ejecutivo
  </h2>
  <table style="border:1px solid #ddd;border-radius:8px;overflow:hidden;">
    <thead>
      <tr>
        <th>Cuestionario</th>
        <th style="text-align:center;">Puntaje Transformado</th>
        <th style="text-align:center;">Nivel de Riesgo</th>
      </tr>
    </thead>
    <tbody>{summary_rows}</tbody>
  </table>
  <div style="margin-top:24px;padding:16px;background:#f0f4ff;border-radius:8px;font-size:12px;color:#555;">
    <strong>Interpretación:</strong> Los puntajes transformados van de 0 a 100; a mayor puntaje, mayor exposición al
    factor de riesgo. Los niveles de riesgo se clasifican según los baremos del manual de la Batería
    (MinTrabajo, 2010).
  </div>
</div>

<!-- SECCIONES DETALLADAS -->
{sections_html}

<!-- PIE DE PÁGINA -->
<div style="text-align:center;font-size:10px;color:#aaa;padding-top:24px;border-top:1px solid #eee;">
  Batería de Instrumentos para la Evaluación de Factores de Riesgo Psicosocial — MinTrabajo Colombia 2010 ·
  Versión baremos: {analysis.get('version_baremos','1.0')} · Generado: {fecha_str}
</div>

</body>
</html>"""


def build_group_html(group_data: Dict) -> str:
    """Construye el HTML para el reporte grupal."""
    n_total = group_data.get("total_respondentes", 0)
    calculado = group_data.get("calculado_en", "")
    try:
        fecha_str = datetime.fromisoformat(calculado).strftime("%d/%m/%Y %H:%M")
    except Exception:
        fecha_str = calculado

    filtros = group_data.get("filtros", {})
    filtros_str = " | ".join(f"{k}: {v}" for k, v in filtros.items() if v) or "Sin filtros"

    # Ranking dimensiones
    ranking = group_data.get("ranking_dimensiones", [])
    ranking_html = ""
    for i, dim in enumerate(ranking[:10], 1):
        color = "#e74c3c" if dim["promedio"] >= 70 else "#f39c12" if dim["promedio"] >= 50 else "#27ae60"
        bar_w = min(100, dim["promedio"])
        ranking_html += f"""
        <tr>
          <td style="padding:8px 12px;font-size:12px;font-weight:600;color:#555;">#{i}</td>
          <td style="padding:8px 12px;font-size:12px;">{dim['dimension']}</td>
          <td style="padding:8px 12px;min-width:200px;">
            <div style="background:#e0e0e0;border-radius:4px;height:12px;">
              <div style="width:{bar_w}%;background:{color};border-radius:4px;height:12px;"></div>
            </div>
          </td>
          <td style="padding:8px 12px;text-align:center;font-size:13px;font-weight:700;color:{color};">{dim['promedio']}</td>
          <td style="padding:8px 12px;text-align:center;font-size:11px;color:#888;">n={dim['n']}</td>
        </tr>"""

    # Distribución por cuestionario
    dist_html = ""
    labels_q = {"estres": "Estrés", "intralaboral": "Intralaboral", "extralaboral": "Extralaboral"}
    niveles_order = ["Sin Riesgo", "Bajo", "Medio", "Alto", "Muy Alto"]
    for q_key, q_label in labels_q.items():
        q_data = group_data.get("cuestionarios", {}).get(q_key)
        if not q_data:
            continue
        dist = q_data.get("distribucion", {})
        pct = q_data.get("distribucion_pct", {})
        n = q_data.get("n", 0)
        avg = q_data.get("promedio_transformado", 0)
        bars = ""
        for nivel in niveles_order:
            cnt = dist.get(nivel, 0)
            p = pct.get(nivel, 0)
            col = RISK_COLORS.get(nivel, "#95a5a6")
            bars += f"""
            <td style="padding:8px;text-align:center;">
              <div style="font-weight:700;font-size:14px;color:{col};">{cnt}</div>
              <div style="font-size:10px;color:#aaa;">{p}%</div>
            </td>"""
        dist_html += f"""
        <tr>
          <td style="padding:8px 12px;font-weight:600;font-size:13px;">{q_label}<br>
            <small style="font-weight:400;color:#888;">Promedio: {avg} | n={n}</small></td>
          {bars}
        </tr>"""

    # Demografía
    demo = group_data.get("demografico", {})
    demo_html = ""
    demo_labels = {"sexo": "Sexo", "area": "Área", "tipo_cargo": "Tipo de Cargo", "nivel_estudios": "Nivel de Estudios"}
    for field, field_label in demo_labels.items():
        counts = demo.get(field, {})
        if not counts:
            continue
        rows = ""
        for val, cnt in sorted(counts.items(), key=lambda x: -x[1])[:8]:
            pct_val = round(cnt / n_total * 100, 1) if n_total > 0 else 0
            rows += f"""
            <tr>
              <td style="padding:6px 10px;font-size:12px;">{val}</td>
              <td style="padding:6px 10px;text-align:center;font-size:12px;">{cnt}</td>
              <td style="padding:6px 10px;text-align:center;font-size:12px;">{pct_val}%</td>
            </tr>"""
        demo_html += f"""
        <div style="margin-bottom:20px;">
          <h4 style="font-size:13px;color:#555;margin-bottom:8px;">{field_label}</h4>
          <table style="border:1px solid #ddd;border-radius:6px;overflow:hidden;">
            <thead><tr>
              <th style="padding:7px 10px;text-align:left;font-size:11px;">Categoría</th>
              <th style="padding:7px 10px;font-size:11px;">N</th>
              <th style="padding:7px 10px;font-size:11px;">%</th>
            </tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <style>
    @page {{ size: letter landscape; margin: 1.5cm 2cm; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; color: #2c3e50; background: white; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th {{ background: #f4f6fb; color: #555; font-size: 11px; padding: 8px 12px; text-align: center; }}
  </style>
</head>
<body>

<!-- PORTADA -->
<div style="page-break-after:always;">
  <div style="background:linear-gradient(135deg,#1a237e,#3949ab);color:#fff;padding:40px;border-radius:12px;">
    <div style="font-size:11px;opacity:.7;margin-bottom:8px;">MINISTERIO DE TRABAJO · COLOMBIA</div>
    <h1 style="font-size:22px;margin:0 0 8px 0;">Reporte Grupal de Resultados</h1>
    <h2 style="font-size:16px;margin:0;font-weight:400;opacity:.9;">
      Batería de Instrumentos para la Evaluación de Factores de Riesgo Psicosocial
    </h2>
  </div>
  <div style="padding:32px 0;display:flex;gap:20px;">
    <div style="flex:1;padding:20px;background:#f8f9fa;border-radius:10px;text-align:center;">
      <div style="font-size:42px;font-weight:800;color:#1a237e;">{n_total}</div>
      <div style="color:#888;font-size:13px;">Respondentes analizados</div>
    </div>
    <div style="flex:2;padding:20px;background:#f8f9fa;border-radius:10px;">
      <div style="font-size:13px;font-weight:600;color:#555;margin-bottom:8px;">Filtros aplicados</div>
      <div style="font-size:13px;">{filtros_str}</div>
      <div style="font-size:12px;color:#888;margin-top:8px;">Fecha: {fecha_str}</div>
    </div>
  </div>
</div>

<!-- DEMOGRAFÍA -->
<div style="page-break-after:always;">
  <h2 style="font-size:18px;font-weight:700;color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:8px;">
    Caracterización del Grupo
  </h2>
  <div style="display:flex;flex-wrap:wrap;gap:20px;">{demo_html}</div>
</div>

<!-- DISTRIBUCIÓN DE RIESGO -->
<div style="page-break-after:always;">
  <h2 style="font-size:18px;font-weight:700;color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:8px;">
    Distribución de Niveles de Riesgo por Cuestionario
  </h2>
  <table style="border:1px solid #ddd;border-radius:8px;overflow:hidden;">
    <thead>
      <tr>
        <th style="text-align:left;">Cuestionario</th>
        {"".join(f'<th style="color:{RISK_COLORS.get(n,"#95a5a6")};">{n}</th>' for n in ["Sin Riesgo","Bajo","Medio","Alto","Muy Alto"])}
      </tr>
    </thead>
    <tbody>{dist_html}</tbody>
  </table>
</div>

<!-- RANKING DIMENSIONES -->
<div>
  <h2 style="font-size:18px;font-weight:700;color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:8px;">
    Ranking de Dimensiones con Mayor Riesgo
  </h2>
  <table style="border:1px solid #ddd;border-radius:8px;overflow:hidden;">
    <thead>
      <tr>
        <th style="width:40px;">#</th>
        <th style="text-align:left;">Dimensión</th>
        <th>Puntaje promedio</th>
        <th>Score</th>
        <th>N</th>
      </tr>
    </thead>
    <tbody>{ranking_html}</tbody>
  </table>
  <div style="margin-top:24px;padding:16px;background:#fff8e1;border-left:4px solid #f39c12;font-size:12px;">
    <strong>Nota:</strong> Las dimensiones con puntaje ≥70 requieren intervención prioritaria.
    Puntajes entre 50 y 69 indican riesgo medio que debe monitorearse.
  </div>
</div>

<div style="text-align:center;font-size:10px;color:#aaa;padding-top:24px;border-top:1px solid #eee;">
  Batería de Instrumentos para la Evaluación de Factores de Riesgo Psicosocial — MinTrabajo Colombia 2010 ·
  Confidencial — Generado: {fecha_str}
</div>

</body>
</html>"""


class ReportGenerator:
    """Genera reportes HTML y los exporta a PDF con Playwright."""

    async def _html_to_pdf(self, html: str, landscape: bool = False) -> bytes:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html, wait_until="networkidle")
            pdf_bytes = await page.pdf(
                format="Letter",
                landscape=landscape,
                margin={"top": "1.2cm", "bottom": "1.2cm", "left": "1.5cm", "right": "1.5cm"},
                print_background=True,
            )
            await browser.close()
        return pdf_bytes

    async def generate_individual_pdf(self, analysis: Dict) -> bytes:
        html = build_individual_html(analysis)
        return await self._html_to_pdf(html, landscape=False)

    async def generate_group_pdf(self, group_data: Dict) -> bytes:
        html = build_group_html(group_data)
        return await self._html_to_pdf(html, landscape=True)

    def get_individual_html(self, analysis: Dict) -> str:
        return build_individual_html(analysis)

    def get_group_html(self, group_data: Dict) -> str:
        return build_group_html(group_data)
