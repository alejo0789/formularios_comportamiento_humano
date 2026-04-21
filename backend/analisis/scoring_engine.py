"""
Motor de Calificación Psicosocial
Implementa la calificación oficial de la Batería de Riesgo Psicosocial - MinTrabajo Colombia 2010.
"""
import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal, ROUND_HALF_UP

# ──────────────────────────────────────────────────────────────
# Configuración de ítems inversos por cuestionario
# ──────────────────────────────────────────────────────────────
# Escala DIRECTA:  Siempre=0, Casi siempre=1, A veces=2, Casi nunca=3, Nunca=4
# Escala INVERSA:  Siempre=4, Casi siempre=3, A veces=2, Casi nunca=1, Nunca=0

INVERSE_ITEMS = {
    "intralaboral_a": {
        4, 5, 6, 9, 12, 14, 32, 34, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
        53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72,
        73, 74, 75, 76, 77, 78, 79, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93,
        94, 95, 96, 97, 105
    },
    "intralaboral_b": {
        4, 5, 6, 9, 12, 14, 21, 23, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
        62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81,
        82, 96
    },
    # Extralaboral: ítems con escala INVERSA (relaciones positivas → menor puntaje = menos riesgo)
    "extralaboral": {14, 15, 16, 17, 22, 25, 27, 29, 30, 31, 24, 26, 28},
}

# ──────────────────────────────────────────────────────────────
# Estructura de dominios y dimensiones - Intralaboral A (123 ítems)
# ──────────────────────────────────────────────────────────────
INTRA_A_STRUCTURE = {
    # Tabla 23 Manual Intralaboral — Forma A
    "Demandas del trabajo": {
        "Demandas ambientales":                            [1,2,3,4,5,6,7,8,9,10,11,12],      # 12 ítems, factor 48
        "Demandas cuantitativas":                          [13,14,15,32,43,47],               # 6 ítems, factor 24
        "Demandas de carga mental":                        [16,17,18,20,21],                  # 5 ítems, factor 20
        "Demandas emocionales":                            [106,107,108,109,110,111,112,113,114], # 9 ítems, factor 36
        "Demandas de responsabilidad del cargo":           [19,22,23,24,25,26],               # 6 ítems, factor 24
        "Demandas de jornada de trabajo":                  [31,33,34],                        # 3 ítems, factor 12
        "Consistencia del rol":                            [27,28,29,30,52],                  # 5 ítems, factor 20
        "Influencia del trabajo sobre el entorno extralaboral": [35,36,37,38],               # 4 ítems, factor 16
    },
    "Control sobre el trabajo": {
        "Oportunidades para el uso y desarrollo de habilidades": [39,40,41,42],              # 4 ítems, factor 16
        "Control y autonomía sobre el trabajo":            [44,45,46],                        # 3 ítems, factor 12
        "Participación y manejo del cambio":               [48,49,50,51],                     # 4 ítems, factor 16
        "Claridad de rol":                                 [53,54,55,56,57,58,59],            # 7 ítems, factor 28
        "Capacitación":                                    [60,61,62],                        # 3 ítems, factor 12
    },
    "Liderazgo y relaciones sociales": {
        "Características del liderazgo":                   [63,64,65,66,67,68,69,70,71,72,73,74,75],          # 13 ítems, factor 52
        "Relaciones sociales en el trabajo":               [76,77,78,79,80,81,82,83,84,85,86,87,88,89],       # 14 ítems, factor 56
        "Retroalimentación del desempeño":                 [90,91,92,93,94],                  # 5 ítems, factor 20
        "Relación con los colaboradores":                  [115,116,117,118,119,120,121,122,123], # 9 ítems, factor 36
    },
    "Recompensas": {
        "Recompensas derivadas de la pertenencia a la organización": [95,102,103,104,105],   # 5 ítems, factor 20
        "Reconocimiento y compensación":                   [96,97,98,99,100,101],             # 6 ítems, factor 24
    },
}

# ──────────────────────────────────────────────────────────────
# Estructura de dominios y dimensiones - Intralaboral B (97 ítems)
# ──────────────────────────────────────────────────────────────
INTRA_B_STRUCTURE = {
    # Tabla 23 Manual Intralaboral — Forma B
    "Demandas del trabajo": {
        "Demandas ambientales":                            [1,2,3,4,5,6,7,8,9,10,11,12],      # 12 ítems, factor 48
        "Demandas cuantitativas":                          [13,14,15],                        # 3 ítems, factor 12
        "Demandas de carga mental":                        [16,17,18,19,20],                  # 5 ítems, factor 20
        "Demandas emocionales":                            [89,90,91,92,93,94,95,96,97],      # 9 ítems, factor 36
        "Demandas de jornada de trabajo":                  [21,22,23,24,33,37],               # 6 ítems, factor 24
        "Influencia del trabajo sobre el entorno extralaboral": [25,26,27,28],               # 4 ítems, factor 16
    },
    "Control sobre el trabajo": {
        "Oportunidades para el uso y desarrollo de habilidades": [29,30,31,32],              # 4 ítems, factor 16
        "Control y autonomía sobre el trabajo":            [34,35,36],                        # 3 ítems, factor 12
        "Participación y manejo del cambio":               [38,39,40],                        # 3 ítems, factor 12
        "Claridad de rol":                                 [41,42,43,44,45],                  # 5 ítems, factor 20
        "Capacitación":                                    [46,47,48],                        # 3 ítems, factor 12
    },
    "Liderazgo y relaciones sociales": {
        "Características del liderazgo":                   [49,50,51,52,53,54,55,56,57,58,59,60,61], # 13 ítems, factor 52
        "Relaciones sociales en el trabajo":               [62,63,64,65,66,67,68,69,70,71,72,73],    # 12 ítems, factor 48
        "Retroalimentación del desempeño":                 [74,75,76,77,78],                  # 5 ítems, factor 20
    },
    "Recompensas": {
        "Recompensas derivadas de la pertenencia a la organización": [85,86,87,88],          # 4 ítems, factor 16
        "Reconocimiento y compensación":                   [79,80,81,82,83,84],               # 6 ítems, factor 24
    },
}

# ──────────────────────────────────────────────────────────────
# Estructura Extralaboral (31 ítems, 7 dimensiones)
# ──────────────────────────────────────────────────────────────
EXTRALABORAL_STRUCTURE = {
    "Balance entre la vida laboral y familiar":          {"items": [14, 15, 16, 17], "escala": "directa", "factor": 16},
    "Relaciones familiares":                             {"items": [22, 25, 27], "escala": "inversa", "factor": 12},
    "Comunicación y relaciones interpersonales":         {"items": [18, 19, 20, 21, 23], "escala": "directa", "factor": 20},
    "Situación económica del grupo familiar":            {"items": [29, 30, 31], "escala": "inversa", "factor": 12},
    "Características de la vivienda y de su entorno":   {"items": [5, 6, 7, 8, 9, 10, 11, 12, 13], "escala": "directa", "factor": 36},
    "Influencia del entorno extralaboral sobre el trabajo": {"items": [24, 26, 28], "escala": "inversa", "factor": 12},
    "Desplazamiento vivienda trabajo vivienda":          {"items": [1, 2, 3, 4], "escala": "directa", "factor": 16},
}
# Factor de transformación total extralaboral
EXTRALABORAL_TOTAL_FACTOR = 124

# Factor total evaluación general (Intra + Extra)
TOTAL_GENERAL_FACTOR = {"forma_a": 616, "forma_b": 512}

# ──────────────────────────────────────────────────────────────
# Grupos de escala para Estrés (ítems con numeración base 1)
# ──────────────────────────────────────────────────────────────
ESTRES_GRUPOS = {
    "A": {
        "items": {1, 2, 3, 9, 13, 14, 15, 23, 24},
        "escala": {1: 9, 2: 6, 3: 3, 4: 0},   # Siempre=9, CasiSiempre=6, Aveces=3, Nunca=0
    },
    "B": {
        "items": {4, 5, 6, 10, 11, 16, 17, 18, 19, 25, 26, 27, 28},
        "escala": {1: 6, 2: 4, 3: 2, 4: 0},   # Siempre=6, CasiSiempre=4, Aveces=2, Nunca=0
    },
    "C": {
        "items": {7, 8, 12, 20, 21, 22, 29, 30, 31},
        "escala": {1: 3, 2: 2, 3: 1, 4: 0},   # Siempre=3, CasiSiempre=2, Aveces=1, Nunca=0
    },
}
ESTRES_DIVISOR = 61.16  # Máximo teórico del instrumento (tercera versión)

# Ítems del bloque 1 (se suman directamente sin ponderación)
ESTRES_BLOQUE1 = {1, 2, 3, 4, 5, 6, 7, 8}


def _classify_tipo_cargo(tipo_cargo: Optional[str]) -> str:
    """Clasifica el tipo de cargo en uno de los dos grupos del baremo."""
    if not tipo_cargo:
        return "auxiliares_operativos"
    t = tipo_cargo.lower()
    if any(k in t for k in ["jefe", "director", "gerente", "coordinador", "profesional", "técnico"]):
        return "profesionales_directivos"
    return "auxiliares_operativos"


class PsychosocialScoringEngine:
    """Motor de calificación oficial para la Batería de Riesgo Psicosocial."""

    def __init__(self, baremos_path: Optional[str] = None):
        if baremos_path is None:
            baremos_path = os.path.join(os.path.dirname(__file__), "baremos.json")
        self.baremos_path = baremos_path
        self._baremos: Optional[Dict] = None

    # ─── Baremos ───────────────────────────────────────────────

    @property
    def baremos(self) -> Dict:
        """Carga baremos desde archivo JSON (recargable en caliente)."""
        if self._baremos is None:
            self._reload_baremos()
        return self._baremos

    def _reload_baremos(self):
        with open(self.baremos_path, "r", encoding="utf-8") as f:
            self._baremos = json.load(f)

    def reload_baremos(self) -> Dict:
        """Fuerza recarga de baremos sin reiniciar el servicio."""
        self._reload_baremos()
        return {"version": self._baremos.get("version"), "reloaded_at": datetime.now().isoformat()}

    def update_baremos(self, new_baremos: Dict) -> Dict:
        """Actualiza los baremos en memoria y persiste a disco."""
        with open(self.baremos_path, "w", encoding="utf-8") as f:
            json.dump(new_baremos, f, ensure_ascii=False, indent=2)
        self._baremos = new_baremos
        return {"version": new_baremos.get("version"), "updated_at": datetime.now().isoformat()}

    # ─── Clasificación de riesgo ───────────────────────────────

    def classify_risk(self, score: float, table: Dict) -> str:
        """Clasifica un puntaje transformado usando la tabla de baremo dada."""
        for level, value in table.items():
            # Skip non-range entries like 'factor_transformacion'
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                continue
            lo, hi = value
            score_decimal = float(Decimal(str(score)).quantize(Decimal('.1'), rounding=ROUND_HALF_UP))
            if lo <= score_decimal <= hi:
                return level
        return "Muy Alto"

    def _get_risk_color(self, level: str) -> str:
        colors = {
            "Sin Riesgo": "#27ae60",
            "Bajo":       "#2ecc71",
            "Medio":      "#f39c12",
            "Alto":       "#e74c3c",
            "Muy Alto":   "#8e44ad",
        }
        return colors.get(level, "#95a5a6")

    # ─── Utilidades de calificación ───────────────────────────

    def _score_item(self, item_id: int, raw_value: int, cuestionario: str) -> int:
        """Aplica escala directa o inversa según el ítem. Retorna puntos 0-4."""
        inverse_set = INVERSE_ITEMS.get(cuestionario, set())
        if item_id in inverse_set:
            return raw_value - 1        # Inversa: 1→0, 2→1, 3→2, 4→3, 5→4
        else:
            return 5 - raw_value        # Directa: 1→4, 2→3, 3→2, 4→1, 5→0

    def _transformed_score(self, raw: float, max_raw: float) -> float:
        """Transforma puntaje bruto a escala 0-100."""
        if max_raw == 0:
            return 0.0
        # Utilizar redondeo de medio hacia arriba (ROUND_HALF_UP) oficial Ministerio
        val_str = str((raw / max_raw) * 100)
        return float(Decimal(val_str).quantize(Decimal('.1'), rounding=ROUND_HALF_UP))

    def _responses_to_dict(self, responses: List[Dict]) -> Dict[Any, Any]:
        """Convierte lista de respuestas a dict, manejando IDs no numéricos."""
        result = {}
        for r in responses:
            try:
                # Intentar convertir a int si es posible para el motor de calificación
                qid_raw = r["question_id"]
                val_raw = r["response_value"]
                
                # Si ambos son numéricos, los guardamos como int
                if str(qid_raw).isdigit() and str(val_raw).isdigit():
                    result[int(qid_raw)] = int(val_raw)
                else:
                    # De lo contrario, los guardamos como están (ej. 'atiende_clientes': 'si')
                    result[qid_raw] = val_raw
            except (KeyError, ValueError, TypeError):
                continue
        return result

    def _compute_hash(self, responses: List[Dict]) -> str:
        """Hash SHA256 del conjunto de respuestas para trazabilidad."""
        data_str = json.dumps(sorted(responses, key=lambda r: r["question_id"]), ensure_ascii=False)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    # ─── Scorer: Intralaboral A ────────────────────────────────

    def score_intralaboral_a(self, responses: List[Dict], tipo_cargo: Optional[str] = None) -> Dict:
        """Califica el Cuestionario Intralaboral Forma A (123 ítems)."""
        resp_dict = self._responses_to_dict(responses)
        cuestionario = "intralaboral_a"
        baremo_total = self.baremos["intralaboral_a"]["total"]
        baremo_dominios = self.baremos["intralaboral_a"]["dominios"]
        baremo_dims = self.baremos["intralaboral_a"]["dimensiones"]

        # Puntaje total
        total_raw = 0
        total_max = 0
        dominios_result = {}
        dimensiones_result = {}

        for dominio, dims in INTRA_A_STRUCTURE.items():
            dom_raw = 0
            dom_max = 0
            dims_calc = {}

            for dim_name, items in dims.items():
                dim_raw = 0
                dim_max = len(items) * 4
                for q in items:
                    if q in resp_dict:
                        dim_raw += self._score_item(q, resp_dict[q], cuestionario)

                dim_score = self._transformed_score(dim_raw, dim_max)
                baremo_dim = baremo_dims.get(dim_name, baremo_total)
                nivel = self.classify_risk(dim_score, baremo_dim)

                dims_calc[dim_name] = {
                    "puntaje_bruto":       round(dim_raw, 2),
                    "puntaje_maximo":      dim_max,
                    "puntaje_transformado": dim_score,
                    "nivel_riesgo":        nivel,
                    "color":               self._get_risk_color(nivel),
                }
                dom_raw += dim_raw
                dom_max += dim_max

            dom_score = self._transformed_score(dom_raw, dom_max)
            baremo_dom = baremo_dominios.get(dominio, baremo_total)
            dom_nivel = self.classify_risk(dom_score, baremo_dom)

            dominios_result[dominio] = {
                "puntaje_bruto":       round(dom_raw, 2),
                "puntaje_maximo":      dom_max,
                "puntaje_transformado": dom_score,
                "nivel_riesgo":        dom_nivel,
                "color":               self._get_risk_color(dom_nivel),
                "dimensiones":         dims_calc,
            }
            dimensiones_result.update(dims_calc)
            total_raw += dom_raw
            total_max += dom_max

        total_score = self._transformed_score(total_raw, total_max)
        total_nivel = self.classify_risk(total_score, baremo_total)

        return {
            "cuestionario":           "intralaborales-a",
            "forma":                  "A",
            "puntaje_bruto_total":    round(total_raw, 2),
            "puntaje_maximo_total":   total_max,
            "puntaje_transformado":   total_score,
            "nivel_riesgo":           total_nivel,
            "color":                  self._get_risk_color(total_nivel),
            "dominios":               dominios_result,
            "hash_respuestas":        self._compute_hash(responses),
            "version_baremos":        self.baremos.get("version"),
        }

    # ─── Scorer: Intralaboral B ────────────────────────────────

    def score_intralaboral_b(self, responses: List[Dict], tipo_cargo: Optional[str] = None) -> Dict:
        """Califica el Cuestionario Intralaboral Forma B (97 ítems)."""
        resp_dict = self._responses_to_dict(responses)
        cuestionario = "intralaboral_b"
        baremo_total = self.baremos["intralaboral_b"]["total"]
        baremo_dominios = self.baremos["intralaboral_b"]["dominios"]
        baremo_dims = self.baremos["intralaboral_b"]["dimensiones"]

        total_raw = 0
        total_max = 0
        dominios_result = {}

        for dominio, dims in INTRA_B_STRUCTURE.items():
            dom_raw = 0
            dom_max = 0
            dims_calc = {}

            for dim_name, items in dims.items():
                dim_raw = 0
                dim_max = len(items) * 4
                for q in items:
                    if q in resp_dict:
                        dim_raw += self._score_item(q, resp_dict[q], cuestionario)

                dim_score = self._transformed_score(dim_raw, dim_max)
                baremo_dim = baremo_dims.get(dim_name, baremo_total)
                nivel = self.classify_risk(dim_score, baremo_dim)

                dims_calc[dim_name] = {
                    "puntaje_bruto":       round(dim_raw, 2),
                    "puntaje_maximo":      dim_max,
                    "puntaje_transformado": dim_score,
                    "nivel_riesgo":        nivel,
                    "color":               self._get_risk_color(nivel),
                }
                dom_raw += dim_raw
                dom_max += dim_max

            dom_score = self._transformed_score(dom_raw, dom_max)
            baremo_dom = baremo_dominios.get(dominio, baremo_total)
            dom_nivel = self.classify_risk(dom_score, baremo_dom)

            dominios_result[dominio] = {
                "puntaje_bruto":       round(dom_raw, 2),
                "puntaje_maximo":      dom_max,
                "puntaje_transformado": dom_score,
                "nivel_riesgo":        dom_nivel,
                "color":               self._get_risk_color(dom_nivel),
                "dimensiones":         dims_calc,
            }
            total_raw += dom_raw
            total_max += dom_max

        total_score = self._transformed_score(total_raw, total_max)
        total_nivel = self.classify_risk(total_score, baremo_total)

        return {
            "cuestionario":           "intralaborales-b",
            "forma":                  "B",
            "puntaje_bruto_total":    round(total_raw, 2),
            "puntaje_maximo_total":   total_max,
            "puntaje_transformado":   total_score,
            "nivel_riesgo":           total_nivel,
            "color":                  self._get_risk_color(total_nivel),
            "dominios":               dominios_result,
            "hash_respuestas":        self._compute_hash(responses),
            "version_baremos":        self.baremos.get("version"),
        }

    # ─── Scorer: Extralaboral ──────────────────────────────────

    def score_extralaboral(self, responses: List[Dict], tipo_cargo: Optional[str] = None) -> Dict:
        """Califica el Cuestionario Extralaboral (31 ítems, 7 dimensiones)."""
        resp_dict = self._responses_to_dict(responses)
        tipo_grupo = _classify_tipo_cargo(tipo_cargo)
        baremo = self.baremos["extralaboral"][tipo_grupo]
        baremo_total = baremo["total"]
        baremo_dims = baremo["dimensiones"]

        total_raw = 0
        dimensiones_result = {}
        missing_dims = []

        for dim_name, config in EXTRALABORAL_STRUCTURE.items():
            items = config["items"]
            factor = config["factor"]
            escala = config["escala"]

            dim_raw = 0
            answered = 0

            for q in items:
                if q in resp_dict:
                    raw_val = resp_dict[q]
                    if escala == "inversa":
                        # Inversa: Siempre(1)=4, CasiSiempre(2)=3, Aveces(3)=2, CasiNunca(4)=1, Nunca(5)=0
                        pts = raw_val - 1
                    else:
                        # Directa: Siempre(1)=0 ... Nunca(5)=4
                        pts = 5 - raw_val
                    pts = max(0, min(4, pts))
                    dim_raw += pts
                    answered += 1

            if answered == 0:
                missing_dims.append(dim_name)
                continue

            dim_score = self._transformed_score(dim_raw, factor)
            baremo_dim = baremo_dims.get(dim_name, baremo_total)
            nivel = self.classify_risk(dim_score, baremo_dim)

            dimensiones_result[dim_name] = {
                "puntaje_bruto":       round(dim_raw, 2),
                "factor_transformacion": factor,
                "puntaje_transformado": dim_score,
                "nivel_riesgo":        nivel,
                "color":               self._get_risk_color(nivel),
            }
            total_raw += dim_raw

        if missing_dims:
            return {
                "cuestionario":  "extralaborales",
                "tipo_cargo_grupo": tipo_grupo,
                "baremo_aplicado": tipo_grupo,
                "error":         "Dimensiones sin respuesta — no se puede calcular el total",
                "missing_dims":  missing_dims,
                "dimensiones":   dimensiones_result,
                "version_baremos": self.baremos.get("version"),
            }

        total_score = self._transformed_score(total_raw, EXTRALABORAL_TOTAL_FACTOR)
        total_nivel = self.classify_risk(total_score, baremo_total)

        return {
            "cuestionario":           "extralaborales",
            "tipo_cargo_grupo":       tipo_grupo,
            "baremo_aplicado":        tipo_grupo,
            "puntaje_bruto_total":    round(total_raw, 2),
            "factor_total":           EXTRALABORAL_TOTAL_FACTOR,
            "puntaje_transformado":   total_score,
            "nivel_riesgo":           total_nivel,
            "color":                  self._get_risk_color(total_nivel),
            "dimensiones":            dimensiones_result,
            "hash_respuestas":        self._compute_hash(responses),
            "version_baremos":        self.baremos.get("version"),
        }

    # ─── Scorer: Estrés ────────────────────────────────────────

    def score_estres(self, responses: List[Dict], tipo_cargo: Optional[str] = None) -> Dict:
        """
        Califica el Cuestionario de Estrés (31 ítems).
        Usa 3 grupos de escala distintos y ponderaciones especiales en los pasos b, c, d.
        """
        resp_dict = self._responses_to_dict(responses)
        tipo_grupo = _classify_tipo_cargo(tipo_cargo)
        baremo = self.baremos["estres"][tipo_grupo]

        # Bloque 1: ítems 1–8 sin ponderación (solo primeros 8 ítems del bloque A/B/C según grupo)
        bloque1_raw = 0
        for q in ESTRES_BLOQUE1:
            if q in resp_dict:
                # Determinar el grupo del ítem
                for grupo_name, grupo_cfg in ESTRES_GRUPOS.items():
                    if q in grupo_cfg["items"]:
                        raw_val = resp_dict[q]
                        bloque1_raw += grupo_cfg["escala"].get(raw_val, 0)
                        break

        # Paso b: ítems 9–12 → promedio × 3
        paso_b_vals = []
        for q in [9, 10, 11, 12]:
            if q in resp_dict:
                for grupo_name, grupo_cfg in ESTRES_GRUPOS.items():
                    if q in grupo_cfg["items"]:
                        raw_val = resp_dict[q]
                        paso_b_vals.append(grupo_cfg["escala"].get(raw_val, 0))
                        break
        paso_b = (sum(paso_b_vals) / len(paso_b_vals) * 3) if paso_b_vals else 0

        # Paso c: ítems 13–22 → promedio × 2
        paso_c_vals = []
        for q in range(13, 23):
            if q in resp_dict:
                for grupo_name, grupo_cfg in ESTRES_GRUPOS.items():
                    if q in grupo_cfg["items"]:
                        raw_val = resp_dict[q]
                        paso_c_vals.append(grupo_cfg["escala"].get(raw_val, 0))
                        break
        paso_c = (sum(paso_c_vals) / len(paso_c_vals) * 2) if paso_c_vals else 0

        # Paso d: ítems 23–31 → promedio sin factor adicional
        paso_d_vals = []
        for q in range(23, 32):
            if q in resp_dict:
                for grupo_name, grupo_cfg in ESTRES_GRUPOS.items():
                    if q in grupo_cfg["items"]:
                        raw_val = resp_dict[q]
                        paso_d_vals.append(grupo_cfg["escala"].get(raw_val, 0))
                        break
        paso_d = (sum(paso_d_vals) / len(paso_d_vals)) if paso_d_vals else 0

        puntaje_bruto = bloque1_raw + paso_b + paso_c + paso_d
        val_str = str((puntaje_bruto / ESTRES_DIVISOR) * 100)
        puntaje_transformado = float(Decimal(val_str).quantize(Decimal('.1'), rounding=ROUND_HALF_UP))
        puntaje_transformado = max(0.0, min(100.0, puntaje_transformado))

        nivel = self.classify_risk(puntaje_transformado, baremo)

        return {
            "cuestionario":           "estres",
            "tipo_cargo_grupo":       tipo_grupo,
            "baremo_aplicado":        tipo_grupo,
            "bloque1_raw":            round(bloque1_raw, 2),
            "paso_b":                 round(paso_b, 2),
            "paso_c":                 round(paso_c, 2),
            "paso_d":                 round(paso_d, 2),
            "puntaje_bruto_total":    round(puntaje_bruto, 2),
            "divisor":                ESTRES_DIVISOR,
            "puntaje_transformado":   puntaje_transformado,
            "nivel_riesgo":           nivel,
            "color":                  self._get_risk_color(nivel),
            "hash_respuestas":        self._compute_hash(responses),
            "version_baremos":        self.baremos.get("version"),
        }

    # ─── Total General (Intra + Extra) ────────────────────────

    def compute_total_general(
        self,
        intra_bruto: float,
        extra_bruto: float,
        forma: str,  # "A" o "B"
    ) -> Dict:
        """Calcula el puntaje Total General (Intralaboral + Extralaboral)."""
        forma_key = f"forma_{forma.lower()}"
        factor = TOTAL_GENERAL_FACTOR.get(forma_key, 616)
        baremo = self.baremos["total_general"][forma_key]

        total_bruto = intra_bruto + extra_bruto
        total_score = self._transformed_score(total_bruto, factor)
        nivel = self.classify_risk(total_score, baremo)

        return {
            "forma":                   forma,
            "factor_total":            factor,
            "puntaje_bruto_intra":     round(intra_bruto, 2),
            "puntaje_bruto_extra":     round(extra_bruto, 2),
            "puntaje_bruto_total":     round(total_bruto, 2),
            "puntaje_transformado":    total_score,
            "nivel_riesgo":            nivel,
            "color":                   self._get_risk_color(nivel),
        }
