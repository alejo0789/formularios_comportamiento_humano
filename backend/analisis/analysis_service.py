"""
Servicio de Análisis Psicosocial — Análisis individual y grupal.
Combina respuestas de múltiples cuestionarios y produce resultados completos.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

from .scoring_engine import PsychosocialScoringEngine

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, "data")


def _load_json(path: str) -> List:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _get_cedula_metadata(cedula: str) -> Dict:
    """Obtiene datos sociodemográficos del respondente desde datos-generales."""
    # Nuevo formato (form_datos-generales.json)
    path = os.path.join(DATA_DIR, "form_datos-generales.json")
    records = _load_json(path)
    for record in records:
        data = record.get("data", {})
        if str(data.get("numero_identificacion", "")) == str(cedula):
            return data
    return {}


def _find_responses_for_cedula(questionnaire_id: str, cedula: str) -> Optional[Dict]:
    """Busca las respuestas más recientes de un respondente en un cuestionario."""
    path = os.path.join(DATA_DIR, f"responses_{questionnaire_id}.json")
    records = _load_json(path)
    # Devuelve la más reciente
    matching = [r for r in records if str(r.get("respondent_cedula", "")) == str(cedula)]
    if not matching:
        return None
    return sorted(matching, key=lambda r: r.get("submitted_at", ""), reverse=True)[0]


class AnalysisService:
    """Servicio de análisis psicosocial individual y grupal."""

    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.engine = PsychosocialScoringEngine()

    # ──────────────────────────────────────────────────────────
    # ANÁLISIS INDIVIDUAL
    # ──────────────────────────────────────────────────────────

    def analyze_individual(self, cedula: str) -> Dict[str, Any]:
        """
        Calcula el análisis completo de un respondente.
        Retorna resultados de todos los cuestionarios que haya completado.
        """
        metadata = _get_cedula_metadata(cedula)
        tipo_cargo = metadata.get("tipo_cargo") or metadata.get("nombre_cargo")

        results: Dict[str, Any] = {
            "cedula":       cedula,
            "nombre":       metadata.get("nombre_completo", "Desconocido"),
            "cargo":        metadata.get("nombre_cargo", ""),
            "area":         metadata.get("departamento_area", ""),
            "tipo_cargo":   tipo_cargo,
            "calculado_en": datetime.now().isoformat(),
            "version_baremos": self.engine.baremos.get("version"),
            "cuestionarios": {},
            "total_general": None,
        }

        # ── Estrés ──
        estres_resp = _find_responses_for_cedula("estres", cedula)
        if estres_resp:
            results["cuestionarios"]["estres"] = self.engine.score_estres(
                estres_resp["responses"], tipo_cargo
            )

        # ── Determinar Forma (A o B) según datos generales ──
        personal_cargo = metadata.get("tiene_personal_cargo", "no")
        forma = "A" if personal_cargo == "si" else "B"
        intra_qid = "intralaborales-a" if forma == "A" else "intralaborales-b"

        # ── Intralaboral ──
        if forma == "A":
            intra_resp = _find_responses_for_cedula("intralaborales-a", cedula)
            if intra_resp:
                results["cuestionarios"]["intralaboral"] = self.engine.score_intralaboral_a(
                    intra_resp["responses"], tipo_cargo
                )
        else:
            intra_resp = _find_responses_for_cedula("intralaborales-b", cedula)
            if intra_resp:
                results["cuestionarios"]["intralaboral"] = self.engine.score_intralaboral_b(
                    intra_resp["responses"], tipo_cargo
                )

        # ── Extralaboral ──
        extra_resp = _find_responses_for_cedula("extralaborales", cedula)
        if extra_resp:
            extra_result = self.engine.score_extralaboral(extra_resp["responses"], tipo_cargo=tipo_cargo)
            results["cuestionarios"]["extralaboral"] = extra_result

            # ── Total General (si hay intra y extra sin error) ──
            intra_result = results["cuestionarios"].get("intralaboral")
            if intra_result and "error" not in extra_result and "puntaje_bruto_total" in intra_result:
                results["total_general"] = self.engine.compute_total_general(
                    intra_result["puntaje_bruto_total"],
                    extra_result["puntaje_bruto_total"],
                    forma,
                )

        return results

    # ──────────────────────────────────────────────────────────
    # ANÁLISIS GRUPAL
    # ──────────────────────────────────────────────────────────

    def analyze_group(
        self,
        filtro_area: Optional[str] = None,
        filtro_cargo: Optional[str] = None,
        filtro_sexo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Devuelve un análisis agregado de todos los respondentes, con filtros opcionales.
        """
        # Obtener todos los respondentes
        cedulas = self._get_all_cedulas()

        # Filtrar por metadatos
        filtered_cedulas = []
        for cedula in cedulas:
            meta = _get_cedula_metadata(cedula)
            if filtro_area and meta.get("departamento_area", "").lower() != filtro_area.lower():
                continue
            if filtro_cargo and meta.get("nombre_cargo", "").lower() != filtro_cargo.lower():
                continue
            if filtro_sexo and meta.get("sexo", "").lower() != filtro_sexo.lower():
                continue
            filtered_cedulas.append(cedula)

        results_by_q: Dict[str, List[Dict]] = defaultdict(list)
        for cedula in filtered_cedulas:
            individual = self.analyze_individual(cedula)
            for q_key, q_result in individual.get("cuestionarios", {}).items():
                if "error" not in q_result and "puntaje_transformado" in q_result:
                    results_by_q[q_key].append(q_result)

        # Agregar por cuestionario
        aggregated: Dict[str, Any] = {}
        for q_key, q_list in results_by_q.items():
            aggregated[q_key] = self._aggregate_questionnaire(q_list)

        # Ranking de dimensiones
        ranking = self._compute_dimension_ranking(results_by_q)

        # Distribución demográfica
        demografico = self._compute_demografico(filtered_cedulas)

        # Desglose por Área (solo para el reporte modular)
        area_breakdown = self._compute_area_breakdown(filtered_cedulas)

        # Desglose por Dimensión para el Dominio de Liderazgo (Página 12)
        leadership_breakdown = self._compute_domain_breakdown(filtered_cedulas, "Liderazgo y relaciones sociales")

        return {
            "total_respondentes": len(filtered_cedulas),
            "filtros":            {"area": filtro_area, "cargo": filtro_cargo, "sexo": filtro_sexo},
            "calculado_en":       datetime.now().isoformat(),
            "cuestionarios":      aggregated,
            "ranking_dimensiones": ranking,
            "demografico":        demografico,
            "area_breakdown":     area_breakdown,
            "leadership_breakdown": leadership_breakdown,
            "leadership_form_breakdown": self._compute_domain_by_form(filtered_cedulas, "Liderazgo y relaciones sociales"),
            "leadership_focus_areas": {
                "liderazgo": self._compute_dimension_by_area(filtered_cedulas, "Características del liderazgo"),
                "colaboradores": self._compute_dimension_by_area(filtered_cedulas, "Relación con los colaboradores"),
                "relaciones": self._compute_dimension_by_area(filtered_cedulas, "Relaciones sociales en el trabajo"),
                "retroalimentacion": self._compute_dimension_by_area(filtered_cedulas, "Retroalimentación del desempeño"),
            },
            "demands_breakdown": self._compute_domain_breakdown(filtered_cedulas, "Demandas del trabajo"),
            "demands_dist": self._compute_domain_total_dist(filtered_cedulas, "Demandas del trabajo"),
            "demands_area_breakdown": self._compute_domain_area_breakdown(filtered_cedulas, "Demandas del trabajo"),
            "demands_form_breakdown": self._compute_domain_by_form(filtered_cedulas, "Demandas del trabajo"),
            "control_breakdown": self._compute_domain_breakdown(filtered_cedulas, "Control sobre el trabajo"),
            "control_dist": self._compute_domain_total_dist(filtered_cedulas, "Control sobre el trabajo"),
            "control_area_breakdown": self._compute_domain_area_breakdown(filtered_cedulas, "Control sobre el trabajo"),
            "control_form_breakdown": self._compute_domain_by_form(filtered_cedulas, "Control sobre el trabajo"),
            "recompensas_breakdown": self._compute_domain_breakdown(filtered_cedulas, "Recompensas"),
            "recompensas_dist": self._compute_domain_total_dist(filtered_cedulas, "Recompensas"),
        }

    def _compute_domain_by_form(self, filtered_cedulas: List[str], domain_name: str) -> Dict[str, Any]:
        """Calcula distribución de niveles separando por Forma A y Forma B."""
        form_results = {"A": [], "B": []}
        for c in filtered_cedulas:
            meta = _get_cedula_metadata(c)
            forma = "A" if meta.get("tiene_personal_cargo", "no") == "si" else "B"
            
            indiv = self.analyze_individual(c)
            intra = indiv.get("cuestionarios", {}).get("intralaboral")
            if intra and "dominios" in intra:
                dom_data = intra["dominios"].get(domain_name)
                if dom_data and "nivel_riesgo" in dom_data:
                    form_results[forma].append(dom_data)

        breakdown = {}
        for f, res_list in form_results.items():
            if res_list:
                breakdown[f] = self._aggregate_questionnaire(res_list)["distribucion_pct"]
        return breakdown

    def _compute_domain_area_breakdown(self, filtered_cedulas: List[str], domain_name: str) -> Dict[str, Any]:
        """Calcula distribución de niveles por área específicamente para un dominio."""
        breakdown = {}
        cedulas_by_area = defaultdict(list)
        for c in filtered_cedulas:
            meta = _get_cedula_metadata(c)
            area = meta.get("departamento_area") or meta.get("area", "No especificado")
            cedulas_by_area[str(area)].append(c)

        for area, c_list in cedulas_by_area.items():
            dom_results = []
            for c in c_list:
                indiv = self.analyze_individual(c)
                intra = indiv.get("cuestionarios", {}).get("intralaboral")
                if intra and "dominios" in intra:
                    dom_data = intra["dominios"].get(domain_name)
                    if dom_data and "nivel_riesgo" in dom_data:
                        dom_results.append(dom_data)
            
            if dom_results:
                breakdown[area] = self._aggregate_questionnaire(dom_results)["distribucion_pct"]
        
        return breakdown

    def _compute_domain_total_dist(self, filtered_cedulas: List[str], domain_name: str) -> Dict[str, Any]:
        """Calcula la distribución agregada de niveles para un dominio completo."""
        results = []
        for c in filtered_cedulas:
            indiv = self.analyze_individual(c)
            intra = indiv.get("cuestionarios", {}).get("intralaboral")
            if intra and "dominios" in intra:
                dom_data = intra["dominios"].get(domain_name)
                if dom_data and "nivel_riesgo" in dom_data:
                    results.append(dom_data)
        
        if not results: return {}
        return self._aggregate_questionnaire(results)["distribucion_pct"]

    def _compute_dimension_by_area(self, filtered_cedulas: List[str], dimension_name: str) -> Dict[str, Any]:
        """Calcula distribución de niveles de una dimensión específica desglosada por área."""
        breakdown = {}
        cedulas_by_area = defaultdict(list)
        for c in filtered_cedulas:
            meta = _get_cedula_metadata(c)
            area = meta.get("departamento_area") or meta.get("area", "No especificado")
            cedulas_by_area[str(area)].append(c)

        for area, c_list in cedulas_by_area.items():
            dim_results = []
            for c in c_list:
                indiv = self.analyze_individual(c)
                intra = indiv.get("cuestionarios", {}).get("intralaboral")
                if intra and "dominios" in intra:
                    # Buscar la dimensión en cualquier dominio
                    found = False
                    for dom_data in intra["dominios"].values():
                        if dimension_name in dom_data.get("dimensiones", {}):
                            dim_results.append(dom_data["dimensiones"][dimension_name])
                            found = True
                            break
            
            if dim_results:
                breakdown[area] = self._aggregate_questionnaire(dim_results)["distribucion_pct"]
        
        return breakdown

    def _compute_domain_breakdown(self, filtered_cedulas: List[str], domain_name: str) -> Dict[str, Any]:
        """Calcula distribución de niveles para todas las dimensiones de un dominio específico."""
        dims_results = defaultdict(list)
        
        for c in filtered_cedulas:
            indiv = self.analyze_individual(c)
            intra = indiv.get("cuestionarios", {}).get("intralaboral")
            if intra and "dominios" in intra:
                dom_data = intra["dominios"].get(domain_name)
                if dom_data and "dimensiones" in dom_data:
                    for dim_name, dim_data in dom_data["dimensiones"].items():
                        dims_results[dim_name].append(dim_data)
        
        breakdown = {}
        for dim_name, results in dims_results.items():
            if results:
                breakdown[dim_name] = self._aggregate_questionnaire(results)["distribucion_pct"]
        
        return breakdown

    def _compute_area_breakdown(self, filtered_cedulas: List[str]) -> Dict[str, Any]:
        """Calcula distribución de niveles por área específicamente para Intra."""
        breakdown = {}
        # Agrupar cédulas por área
        cedulas_by_area = defaultdict(list)
        for c in filtered_cedulas:
            meta = _get_cedula_metadata(c)
            area = meta.get("departamento_area") or meta.get("area", "No especificado")
            cedulas_by_area[str(area)].append(c)

        for area, c_list in cedulas_by_area.items():
            intra_results = []
            for c in c_list:
                indiv = self.analyze_individual(c)
                q_res = indiv.get("cuestionarios", {}).get("intralaboral")
                if q_res and "error" not in q_res:
                    intra_results.append(q_res)
            
            if intra_results:
                breakdown[area] = self._aggregate_questionnaire(intra_results)["distribucion_pct"]
        
        return breakdown

    def _get_all_cedulas(self) -> List[str]:
        """Devuelve la lista de cédulas únicas de todos los respondentes."""
        path = os.path.join(self.data_dir, "form_datos-generales.json")
        records = _load_json(path)
        cedulas = set()
        for r in records:
            c = r.get("data", {}).get("numero_identificacion")
            if c:
                cedulas.add(str(c))

        # También recoger cédulas de los cuestionarios Likert
        for q in ["estres", "extralaborales", "intralaborales-a", "intralaborales-b"]:
            path2 = os.path.join(self.data_dir, f"responses_{q}.json")
            for r in _load_json(path2):
                c = r.get("respondent_cedula")
                if c:
                    cedulas.add(str(c))
        return list(cedulas)

    def _aggregate_questionnaire(self, q_list: List[Dict]) -> Dict:
        """Agrega resultados de múltiples respondentes para un cuestionario."""
        scores = [q["puntaje_transformado"] for q in q_list]
        promedio = round(sum(scores) / len(scores), 1) if scores else 0

        # Distribución de niveles
        dist: Dict[str, int] = {"Sin Riesgo": 0, "Bajo": 0, "Medio": 0, "Alto": 0, "Muy Alto": 0}
        for q in q_list:
            lvl = q.get("nivel_riesgo", "Sin Riesgo")
            if lvl in dist:
                dist[lvl] += 1

        n = len(q_list)
        dist_pct = {k: round(v / n * 100, 1) if n > 0 else 0 for k, v in dist.items()}

        # Agregar dimensiones si existen
        dims_agg: Dict[str, Dict] = {}
        for q in q_list:
            for dom_name, dom_data in q.get("dominios", {}).items():
                for dim_name, dim_data in dom_data.get("dimensiones", {}).items():
                    if dim_name not in dims_agg:
                        dims_agg[dim_name] = {"scores": [], "dominio": dom_name}
                    dims_agg[dim_name]["scores"].append(dim_data["puntaje_transformado"])

        dims_result = {}
        for dim_name, d in dims_agg.items():
            sc = d["scores"]
            avg = round(sum(sc) / len(sc), 1) if sc else 0
            dims_result[dim_name] = {
                "promedio_transformado": avg,
                "n":                     len(sc),
                "dominio":               d["dominio"],
            }

        return {
            "n":                     n,
            "promedio_transformado": promedio,
            "distribucion":          dist,
            "distribucion_pct":      dist_pct,
            "dimensiones":           dims_result,
        }

    def _compute_dimension_ranking(self, results_by_q: Dict[str, List[Dict]]) -> List[Dict]:
        """Retorna top 10 dimensiones con mayor puntaje promedio (mayor riesgo)."""
        all_dims: Dict[str, List[float]] = defaultdict(list)

        for q_list in results_by_q.values():
            for q in q_list:
                for dom_data in q.get("dominios", {}).values():
                    for dim_name, dim_data in dom_data.get("dimensiones", {}).items():
                        all_dims[dim_name].append(dim_data["puntaje_transformado"])

        ranking = []
        for dim_name, scores in all_dims.items():
            avg = round(sum(scores) / len(scores), 1)
            ranking.append({"dimension": dim_name, "promedio": avg, "n": len(scores)})

        ranking.sort(key=lambda x: x["promedio"], reverse=True)
        return ranking[:10]

    def _compute_demografico(self, cedulas: List[str]) -> Dict:
        """Calcula distribución demográfica del grupo."""
        counters: Dict[str, Dict[str, int]] = {
            "sexo": defaultdict(int),
            "area": defaultdict(int),
            "tipo_cargo": defaultdict(int),
            "nivel_estudios": defaultdict(int),
            "estado_civil": defaultdict(int),
            "ciudad_residencia": defaultdict(int),
            "estrato": defaultdict(int),
            "tipo_vivienda": defaultdict(int),
        }
        for cedula in cedulas:
            meta = _get_cedula_metadata(cedula)
            for field, counter in counters.items():
                val = meta.get(field) or meta.get({
                    "area": "departamento_area",
                    "tipo_cargo": "tipo_cargo",
                }.get(field, field), "No especificado")
                counter[str(val)] += 1

        return {k: dict(v) for k, v in counters.items()}

    # ──────────────────────────────────────────────────────────
    # MANEJO DE BAREMOS
    # ──────────────────────────────────────────────────────────

    def get_baremos(self) -> Dict:
        return self.engine.baremos

    def update_baremos(self, new_baremos: Dict) -> Dict:
        return self.engine.update_baremos(new_baremos)

    def reload_baremos(self) -> Dict:
        return self.engine.reload_baremos()
