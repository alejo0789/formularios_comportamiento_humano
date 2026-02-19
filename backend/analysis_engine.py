from typing import List, Dict, Any, Counter
import json
import os
from scoring_config import INVERSE_QUESTIONS, INTRALABORAL_A_STRUCTURE, INTRALABORAL_B_STRUCTURE

class AnalysisEngine:
    def __init__(self, data_dir: str, questionnaires_dir: str):
        self.data_dir = data_dir
        self.questionnaires_dir = questionnaires_dir

    def load_responses(self, q_id: str) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, f"responses_{q_id}.json")
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_sociodemographic_stats(self) -> Dict[str, Any]:
        # Load legacy responses
        responses_legacy = self.load_responses("datos-generales")
        
        # Load new form responses
        path_new = os.path.join(self.data_dir, "form_datos-generales.json")
        responses_new = []
        if os.path.exists(path_new):
            try:
                with open(path_new, "r", encoding="utf-8") as f:
                    responses_new = json.load(f)
            except:
                responses_new = []

        stats = {
            "sexo": Counter(),
            "estado_civil": Counter(),
            "nivel_estudios": Counter(),
            "tipo_vivienda": Counter(),
            "tipo_cargo": Counter(),
            "ciudad_residencia": Counter(),
            "estrato": Counter(),
            "tipo_contrato": Counter(),
            "tipo_salario": Counter(),
            "horas_diarias": Counter(),
            "total": 0
        }

        # Process Legacy
        for resp in responses_legacy:
            stats["total"] += 1
            for r in resp.get("responses", []):
                q_id = r["question_id"]
                val = r["response_value"]
                if q_id in stats:
                    stats[q_id][val] += 1

        # Process New
        for resp in responses_new:
            stats["total"] += 1
            data = resp.get("data", {})
            for key, val in data.items():
                if key in stats:
                    stats[key][val] += 1

        # Convert counters to lists for Chart.js
        formatted = {}
        for key, counter in stats.items():
            if key == "total":
                formatted[key] = counter
                continue
            formatted[key] = {
                "labels": list(counter.keys()),
                "data": list(counter.values())
            }
        return formatted

    def calculate_score(self, q_id: str, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates transformed scores and risk levels"""
        if not responses:
            return {}

        inverse_ids = INVERSE_QUESTIONS.get(q_id, [])
        structure = None
        if q_id == "intralaborales-a":
            structure = INTRALABORAL_A_STRUCTURE
        elif q_id == "intralaborales-b":
            structure = INTRALABORAL_B_STRUCTURE
        
        participant_scores = []
        domain_raw_scores = {} # {domain: [scores]}
        dimension_raw_scores = {} # {dimension: [scores]}
        
        for resp in responses:
            raw_sum = 0
            count = 0
            
            # For domain/dimension calculation per participant
            # Original reading: val = r["response_value"] (1-5 range)
            # Subtract 1 to get 0-4 range for simpler math if needed, but let's be explicit
            resp_dict = {r["question_id"]: r["response_value"] for r in resp["responses"]}
            
            # Map of processed points (0-4) for structure calculation
            processed_points = {}

            for q_id_item, val in resp_dict.items():
                # Logic based on scoring_config.py comments:
                # Direct: Siempre(1)=4, Casi siempre(2)=3, A veces(3)=2, Casi nunca(4)=1, Nunca(5)=0
                # Inverse: Siempre(1)=0, Casi siempre(2)=1, A veces(3)=2, Casi nunca(4)=3, Nunca(5)=4
                
                points = 0
                if q_id_item in inverse_ids:
                    # Inverse Question
                    # Value 1 -> 0
                    # Value 5 -> 4
                    points = val - 1
                else:
                    # Direct Question
                    # Value 1 -> 4
                    # Value 5 -> 0
                    points = 5 - val
                
                # Clamp points between 0 and 4 just in case
                points = max(0, min(4, points))
                
                processed_points[q_id_item] = points
                raw_sum += points
                count += 1
            
            if count > 0:
                transformed = (raw_sum / (count * 4)) * 100
                participant_scores.append(transformed)

            # Domain/Dimension logic
            if structure:
                for domain, dimensions in structure.items():
                    if domain not in domain_raw_scores: domain_raw_scores[domain] = []
                    domain_sum = 0
                    domain_count = 0
                    
                    for dim, questions in dimensions.items():
                        if dim not in dimension_raw_scores: dimension_raw_scores[dim] = []
                        dim_sum = 0
                        dim_count = 0
                        
                        for q_idx in questions:
                            if q_idx in processed_points:
                                p = processed_points[q_idx]
                                dim_sum += p
                                dim_count += 1
                                domain_sum += p
                                domain_count += 1
                        
                        if dim_count > 0:
                            dimension_raw_scores[dim].append((dim_sum / (dim_count * 4)) * 100)
                    
                    if domain_count > 0:
                        domain_raw_scores[domain].append((domain_sum / (domain_count * 4)) * 100)
        
        if not participant_scores:
            return {}

        avg_score = sum(participant_scores) / len(participant_scores)
        
        # Risk levels distribution
        levels = {"Sin Riesgo": 0, "Bajo": 0, "Medio": 0, "Alto": 0, "Muy Alto": 0}
        for s in participant_scores:
            lvl = self.get_risk_level(s)
            levels[lvl] += 1
            
        result = {
            "average": round(avg_score, 1),
            "distribution": levels,
            "total_participants": len(participant_scores),
            "risk_level": self.get_risk_level(avg_score)
        }

        if domain_raw_scores:
            result["domains"] = {d: round(sum(scores)/len(scores), 1) for d, scores in domain_raw_scores.items() if scores}
            result["dimensions"] = {d: round(sum(scores)/len(scores), 1) for d, scores in dimension_raw_scores.items() if scores}

        return result

    def get_risk_level(self, score: float) -> str:
        if score < 25: return "Sin Riesgo"
        if score < 50: return "Bajo"
        if score < 70: return "Medio"
        if score < 85: return "Alto"
        return "Muy Alto"

    def get_global_report(self) -> Dict[str, Any]:
        report = {
            "sociodemographics": self.get_sociodemographic_stats(),
            "questionnaires": {}
        }
        
        for q_id in ["estres", "extralaborales", "intralaborales-a", "intralaborales-b"]:
            responses = self.load_responses(q_id)
            report["questionnaires"][q_id] = self.calculate_score(q_id, responses)
            
        return report
