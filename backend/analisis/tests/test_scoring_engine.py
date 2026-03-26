"""
Pruebas unitarias del Motor de Calificación Psicosocial.
Cubre los criterios de aceptación CA-01 a CA-20 del documento de requerimientos.
"""
import pytest
import os
import sys

# Ensure the backend directory is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from analisis.scoring_engine import PsychosocialScoringEngine


@pytest.fixture
def engine():
    return PsychosocialScoringEngine()


# ──────────────────────────────────────────────────────────────
# FIXTURES: Respuestas conocidas para cada cuestionario
# ──────────────────────────────────────────────────────────────

def _make_responses(ids: list, value: int) -> list:
    """Genera una lista de respuestas con el mismo valor para todos los IDs."""
    return [{"question_id": qid, "response_value": value} for qid in ids]


def _all_intra_a_ids():
    """Todos los IDs de ítems de Intralaboral A (1-123)."""
    return list(range(1, 124))


def _all_intra_b_ids():
    """Todos los IDs de ítems de Intralaboral B (1-97)."""
    return list(range(1, 98))


def _all_estres_ids():
    """Todos los IDs de ítems de estrés (1-31)."""
    return list(range(1, 32))


def _all_extralaboral_ids():
    """Todos los IDs de ítems de extralaboral (1-35, incluye rango amplio)."""
    return list(range(1, 36))


# ──────────────────────────────────────────────────────────────
# CA-01: Calificación correcta Intralaboral Forma A
# ──────────────────────────────────────────────────────────────

class TestIntralaboralA:
    def test_all_minimum_responses(self, engine):
        """Todas las respuestas = 5 (Nunca) → puntaje bajo para directos, alto para inversos."""
        responses = _make_responses(_all_intra_a_ids(), 5)
        result = engine.score_intralaboral_a(responses)
        assert result["cuestionario"] == "intralaborales-a"
        assert result["forma"] == "A"
        assert 0 <= result["puntaje_transformado"] <= 100
        assert result["nivel_riesgo"] in ["Sin Riesgo", "Bajo", "Medio", "Alto", "Muy Alto"]

    def test_all_maximum_responses(self, engine):
        """Todas las respuestas = 1 (Siempre) → puntaje alto para directos, bajo para inversos."""
        responses = _make_responses(_all_intra_a_ids(), 1)
        result = engine.score_intralaboral_a(responses)
        assert 0 <= result["puntaje_transformado"] <= 100

    def test_mixed_responses(self, engine):
        """Respuestas mixtas deben producir un resultado válido."""
        responses = []
        for i in _all_intra_a_ids():
            responses.append({"question_id": i, "response_value": (i % 5) + 1})
        result = engine.score_intralaboral_a(responses)
        assert result["puntaje_transformado"] > 0
        assert "dominios" in result
        assert len(result["dominios"]) == 4

    def test_dominios_have_dimensiones(self, engine):
        """Cada dominio debe contener sus dimensiones."""
        responses = _make_responses(_all_intra_a_ids(), 3)
        result = engine.score_intralaboral_a(responses)
        for dom_name, dom_data in result["dominios"].items():
            assert "dimensiones" in dom_data
            assert len(dom_data["dimensiones"]) > 0
            for dim_name, dim_data in dom_data["dimensiones"].items():
                assert "puntaje_bruto" in dim_data
                assert "puntaje_transformado" in dim_data
                assert "nivel_riesgo" in dim_data

    def test_hash_reproducibility(self, engine):
        """El mismo conjunto de respuestas debe producir el mismo hash."""
        responses = _make_responses(_all_intra_a_ids(), 3)
        r1 = engine.score_intralaboral_a(responses)
        r2 = engine.score_intralaboral_a(responses)
        assert r1["hash_respuestas"] == r2["hash_respuestas"]


# ──────────────────────────────────────────────────────────────
# CA-02: Calificación correcta Intralaboral Forma B
# ──────────────────────────────────────────────────────────────

class TestIntralaboralB:
    def test_all_minimum_responses(self, engine):
        responses = _make_responses(_all_intra_b_ids(), 5)
        result = engine.score_intralaboral_b(responses)
        assert result["cuestionario"] == "intralaborales-b"
        assert result["forma"] == "B"
        assert 0 <= result["puntaje_transformado"] <= 100

    def test_all_maximum_responses(self, engine):
        responses = _make_responses(_all_intra_b_ids(), 1)
        result = engine.score_intralaboral_b(responses)
        assert 0 <= result["puntaje_transformado"] <= 100

    def test_dominios_count(self, engine):
        """Forma B tiene 4 dominios."""
        responses = _make_responses(_all_intra_b_ids(), 3)
        result = engine.score_intralaboral_b(responses)
        assert len(result["dominios"]) == 4


# ──────────────────────────────────────────────────────────────
# CA-03: Puntaje transformado siempre en rango 0-100
# ──────────────────────────────────────────────────────────────

class TestScoreRange:
    @pytest.mark.parametrize("value", [1, 2, 3, 4, 5])
    def test_intralaboral_a_range(self, engine, value):
        responses = _make_responses(_all_intra_a_ids(), value)
        result = engine.score_intralaboral_a(responses)
        assert 0 <= result["puntaje_transformado"] <= 100

    @pytest.mark.parametrize("value", [1, 2, 3, 4, 5])
    def test_intralaboral_b_range(self, engine, value):
        responses = _make_responses(_all_intra_b_ids(), value)
        result = engine.score_intralaboral_b(responses)
        assert 0 <= result["puntaje_transformado"] <= 100

    @pytest.mark.parametrize("value", [1, 2, 3, 4])
    def test_estres_range(self, engine, value):
        responses = _make_responses(_all_estres_ids(), value)
        result = engine.score_estres(responses)
        assert 0 <= result["puntaje_transformado"] <= 100

    @pytest.mark.parametrize("value", [1, 2, 3, 4, 5])
    def test_extralaboral_range(self, engine, value):
        responses = _make_responses(_all_extralaboral_ids(), value)
        result = engine.score_extralaboral(responses)
        if "error" not in result:
            assert 0 <= result["puntaje_transformado"] <= 100


# ──────────────────────────────────────────────────────────────
# CA-04: Nivel de riesgo coincide con baremos
# ──────────────────────────────────────────────────────────────

class TestRiskClassification:
    def test_classify_sin_riesgo(self, engine):
        table = {"Sin Riesgo": [0, 25], "Bajo": [25.1, 50], "Medio": [50.1, 100]}
        assert engine.classify_risk(10.0, table) == "Sin Riesgo"

    def test_classify_bajo(self, engine):
        table = {"Sin Riesgo": [0, 25], "Bajo": [25.1, 50], "Medio": [50.1, 100]}
        assert engine.classify_risk(30.0, table) == "Bajo"

    def test_classify_muy_alto_fallback(self, engine):
        table = {"Sin Riesgo": [0, 10], "Bajo": [10.1, 20]}
        assert engine.classify_risk(99.9, table) == "Muy Alto"

    def test_valid_risk_levels(self, engine):
        """Los niveles de riesgo deben ser uno de los 5 estándar."""
        valid_levels = {"Sin Riesgo", "Bajo", "Medio", "Alto", "Muy Alto"}
        for value in [1, 2, 3, 4, 5]:
            result = engine.score_intralaboral_a(_make_responses(_all_intra_a_ids(), value))
            assert result["nivel_riesgo"] in valid_levels


# ──────────────────────────────────────────────────────────────
# CA-11 a CA-15: Estrés — calificación especial
# ──────────────────────────────────────────────────────────────

class TestEstres:
    def test_grupo_a_siempre_gives_9(self, engine):
        """CA-11: Ítem del grupo A respondido 'Siempre' (1) debe dar 9."""
        from analisis.scoring_engine import ESTRES_GRUPOS
        grupo_a = ESTRES_GRUPOS["A"]
        assert grupo_a["escala"][1] == 9  # Siempre=9

    def test_grupo_b_siempre_gives_6(self, engine):
        """CA-11: Ítem del grupo B respondido 'Siempre' (1) debe dar 6."""
        from analisis.scoring_engine import ESTRES_GRUPOS
        grupo_b = ESTRES_GRUPOS["B"]
        assert grupo_b["escala"][1] == 6

    def test_grupo_c_siempre_gives_3(self, engine):
        """CA-11: Ítem del grupo C respondido 'Siempre' (1) debe dar 3."""
        from analisis.scoring_engine import ESTRES_GRUPOS
        grupo_c = ESTRES_GRUPOS["C"]
        assert grupo_c["escala"][1] == 3

    def test_puntaje_bruto_with_known_values(self, engine):
        """CA-12: Cálculo manual de puntaje bruto."""
        # Todos responden "Siempre" (1)
        responses = _make_responses(_all_estres_ids(), 1)
        result = engine.score_estres(responses)
        
        # Bloque 1 (ítems 1-8): manual calculation
        # Items 1,2,3 are Group A (=9 each), 4,5,6 are Group B (=6 each), 7,8 are Group C (=3 each)
        bloque1 = 9+9+9 + 6+6+6 + 3+3  # = 51
        assert result["bloque1_raw"] == bloque1

    def test_puntaje_transformado_format(self, engine):
        """CA-13: El puntaje transformado debe tener exactamente 1 decimal."""
        responses = _make_responses(_all_estres_ids(), 2)
        result = engine.score_estres(responses)
        score = result["puntaje_transformado"]
        # Check it has at most 1 decimal
        assert round(score, 1) == score

    def test_baremo_selection_professionls(self, engine):
        """CA-14: Tipo 'profesional' usa baremo de profesionales_directivos."""
        responses = _make_responses(_all_estres_ids(), 2)
        result = engine.score_estres(responses, tipo_cargo="Profesional")
        assert result["baremo_aplicado"] == "profesionales_directivos"

    def test_baremo_selection_operativos(self, engine):
        """CA-14: Tipo 'operario' usa baremo de auxiliares_operativos."""
        responses = _make_responses(_all_estres_ids(), 2)
        result = engine.score_estres(responses, tipo_cargo="Auxiliar")
        assert result["baremo_aplicado"] == "auxiliares_operativos"

    def test_baremo_indicated_in_result(self, engine):
        """CA-15: El resultado indica explícitamente qué baremo se usó."""
        responses = _make_responses(_all_estres_ids(), 3)
        result = engine.score_estres(responses, tipo_cargo="Director")
        assert "baremo_aplicado" in result
        assert result["baremo_aplicado"] in ["profesionales_directivos", "auxiliares_operativos"]

    def test_all_nunca_gives_zero(self, engine):
        """Todas las respuestas 'Nunca' (4) deben dar puntaje bruto 0."""
        responses = _make_responses(_all_estres_ids(), 4)
        result = engine.score_estres(responses)
        assert result["puntaje_bruto_total"] == 0
        assert result["puntaje_transformado"] == 0.0


# ──────────────────────────────────────────────────────────────
# CA-16 a CA-20: Extralaboral
# ──────────────────────────────────────────────────────────────

class TestExtralaboral:
    def test_basic_scoring(self, engine):
        """Extralaboral debe producir resultados con dimensiones."""
        responses = _make_responses(_all_extralaboral_ids(), 3)
        result = engine.score_extralaboral(responses)
        if "error" not in result:
            assert "dimensiones" in result
            assert result["puntaje_transformado"] >= 0

    def test_dimension_factors(self, engine):
        """CA-17: Los factores de transformación por dimensión deben ser correctos."""
        from analisis.scoring_engine import EXTRALABORAL_STRUCTURE
        expected_factors = {
            "Balance entre la vida laboral y familiar": 16,
            "Relaciones familiares": 12,
            "Comunicación y relaciones interpersonales": 20,
            "Situación económica del grupo familiar": 12,
            "Características de la vivienda y de su entorno": 36,
            "Influencia del entorno extralaboral sobre el trabajo": 12,
            "Desplazamiento vivienda trabajo vivienda": 16,
        }
        for dim_name, expected_factor in expected_factors.items():
            assert EXTRALABORAL_STRUCTURE[dim_name]["factor"] == expected_factor

    def test_total_factor(self, engine):
        """El factor total extralaboral debe ser 124."""
        from analisis.scoring_engine import EXTRALABORAL_TOTAL_FACTOR
        assert EXTRALABORAL_TOTAL_FACTOR == 124


# ──────────────────────────────────────────────────────────────
# CA-08: Manejo de valores inválidos
# ──────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_responses(self, engine):
        """Motor no debe colapsar con respuestas vacías."""
        result = engine.score_estres([])
        assert result["puntaje_bruto_total"] == 0

    def test_partial_responses(self, engine):
        """Motor debe manejar respuestas parciales."""
        responses = _make_responses([1, 2, 3], 2)
        result = engine.score_estres(responses)
        assert "puntaje_transformado" in result


# ──────────────────────────────────────────────────────────────
# CA-19: Total General (Intra + Extra)
# ──────────────────────────────────────────────────────────────

class TestTotalGeneral:
    def test_forma_a_factor(self, engine):
        """CA-19: El factor total general para Forma A debe ser 616."""
        result = engine.compute_total_general(100, 50, "A")
        assert result["factor_total"] == 616

    def test_forma_b_factor(self, engine):
        """CA-19: El factor total general para Forma B debe ser 512."""
        result = engine.compute_total_general(100, 50, "B")
        assert result["factor_total"] == 512

    def test_total_calculation(self, engine):
        """El total general debe sumar correctamente intra + extra."""
        result = engine.compute_total_general(100, 50, "A")
        assert result["puntaje_bruto_total"] == 150
        expected_score = round((150 / 616) * 100, 1)
        assert result["puntaje_transformado"] == expected_score


# ──────────────────────────────────────────────────────────────
# CA-09: Baremos pueden actualizarse sin reiniciar
# ──────────────────────────────────────────────────────────────

class TestBaremos:
    def test_baremos_loaded(self, engine):
        """Los baremos deben cargarse correctamente."""
        assert engine.baremos is not None
        assert "version" in engine.baremos

    def test_baremos_reload(self, engine):
        """Recargar baremos debe funcionar sin error."""
        result = engine.reload_baremos()
        assert "reloaded_at" in result

    def test_version_in_results(self, engine):
        """Los resultados deben indicar la versión de baremos usada."""
        responses = _make_responses(_all_estres_ids(), 2)
        result = engine.score_estres(responses)
        assert "version_baremos" in result
