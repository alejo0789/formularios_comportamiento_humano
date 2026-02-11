from typing import List, Dict, Any, Counter
import json
import os
from scoring_config import INVERSE_QUESTIONS, INTRALABORAL_A_STRUCTURE

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
        responses = self.load_responses("datos-generales")
        if not responses:
            return {}

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
            "total": len(responses)
        }

        for resp in responses:
            for r in resp.get("responses", []):
                q_id = r["question_id"]
                val = r["response_value"]
                if q_id in stats:
                    stats[q_id][val] += 1

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
        structure = INTRALABORAL_A_STRUCTURE if q_id == "intralaborales-a" else None
        
        participant_scores = []
        domain_raw_scores = {} # {domain: [scores]}
        dimension_raw_scores = {} # {dimension: [scores]}
        
        for resp in responses:
            raw_sum = 0
            count = 0
            
            # For domain/dimension calculation per participant
            resp_dict = {r["question_id"]: r["response_value"] - 1 for r in resp["responses"]}
            
            for q_id_item, val in resp_dict.items():
                points = val
                if q_id_item in inverse_ids:
                    points = 4 - points
                
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
                            if q_idx in resp_dict:
                                p = resp_dict[q_idx]
                                if q_idx in inverse_ids: p = 4 - p
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
            result["domains"] = {d: round(sum(scores)/len(scores), 1) for d, scores in domain_raw_scores.items()}
            result["dimensions"] = {d: round(sum(scores)/len(scores), 1) for d, scores in dimension_raw_scores.items()}

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
        
        for q_id in ["estres", "extralaborales", "intralaborales-a"]:
            responses = self.load_responses(q_id)
            report["questionnaires"][q_id] = self.calculate_score(q_id, responses)
            
        return report
