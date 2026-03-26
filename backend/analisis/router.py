"""
Router FastAPI — Módulo de Análisis Psicosocial
Todos los endpoints del módulo de análisis se registran aquí.
"""
import io
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .analysis_service import AnalysisService
from .report_generator import ReportGenerator

router = APIRouter(prefix="/api/analisis", tags=["Análisis Psicosocial"])
service = AnalysisService()
report_gen = ReportGenerator()


# ──────────────────────────────────────────────────────────────
# MODELOS
# ──────────────────────────────────────────────────────────────

class BaremosUpdate(BaseModel):
    baremos: Dict[str, Any]


# ──────────────────────────────────────────────────────────────
# ENDPOINTS INDIVIDUALES
# ──────────────────────────────────────────────────────────────

@router.get("/{cedula}")
async def get_individual_analysis(cedula: str):
    """
    Retorna el análisis psicosocial completo de un respondente por cédula.
    Incluye todos los cuestionarios completados, dominios, dimensiones y nivel de riesgo.
    """
    try:
        result = service.analyze_individual(cedula)
        if not result["cuestionarios"]:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron respuestas para la cédula {cedula}"
            )
        return {
            "success": True,
            "data": result,
            "meta": {
                "cedula":           cedula,
                "calculado_en":     result["calculado_en"],
                "version_baremos":  result.get("version_baremos"),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cedula}/reporte-pdf")
async def download_individual_report(cedula: str):
    """
    Genera y descarga el reporte PDF individual del respondente.
    """
    try:
        analysis = service.analyze_individual(cedula)
        if not analysis["cuestionarios"]:
            raise HTTPException(status_code=404, detail=f"No hay datos para {cedula}")

        pdf_bytes = await report_gen.generate_individual_pdf(analysis)
        filename = f"reporte_psicosocial_{cedula}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────
# ENDPOINTS GRUPALES
# ──────────────────────────────────────────────────────────────

@router.get("/grupo/resumen")
async def get_group_analysis(
    area:   Optional[str] = Query(None, description="Filtrar por área/departamento"),
    cargo:  Optional[str] = Query(None, description="Filtrar por nombre de cargo"),
    sexo:   Optional[str] = Query(None, description="Filtrar por sexo (M/F)"),
):
    """
    Retorna el análisis grupal agregado con distribución de niveles de riesgo
    por cuestionario y filtros opcionales.
    """
    try:
        result = service.analyze_group(
            filtro_area=area,
            filtro_cargo=cargo,
            filtro_sexo=sexo,
        )
        return {
            "success": True,
            "data": result,
            "meta": {"calculado_en": result["calculado_en"]}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grupo/ranking-dimensiones")
async def get_dimension_ranking(
    area:  Optional[str] = Query(None),
    cargo: Optional[str] = Query(None),
    sexo:  Optional[str] = Query(None),
):
    """
    Retorna el ranking de las 10 dimensiones con mayor puntaje promedio de riesgo.
    """
    try:
        group = service.analyze_group(filtro_area=area, filtro_cargo=cargo, filtro_sexo=sexo)
        return {
            "success": True,
            "data":    group["ranking_dimensiones"],
            "meta":    {"calculado_en": group["calculado_en"]}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grupo/reporte-pdf")
async def download_group_report(
    area:  Optional[str] = Query(None),
    cargo: Optional[str] = Query(None),
    sexo:  Optional[str] = Query(None),
):
    """
    Genera y descarga el reporte PDF grupal.
    """
    try:
        group_data = service.analyze_group(filtro_area=area, filtro_cargo=cargo, filtro_sexo=sexo)
        pdf_bytes = await report_gen.generate_group_pdf(group_data)
        filename = f"reporte_grupal_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────
# BAREMOS
# ──────────────────────────────────────────────────────────────

@router.get("/baremos/actual")
async def get_baremos():
    """Retorna los baremos actualmente en uso."""
    return {"success": True, "data": service.get_baremos()}


@router.put("/baremos/actualizar")
async def update_baremos(body: BaremosUpdate):
    """
    Actualiza los baremos en caliente (sin reiniciar el servicio).
    Persiste los cambios a baremos.json.
    """
    try:
        result = service.update_baremos(body.baremos)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/baremos/recargar")
async def reload_baremos():
    """Recarga los baremos desde el archivo JSON sin reiniciar."""
    result = service.reload_baremos()
    return {"success": True, "data": result}
