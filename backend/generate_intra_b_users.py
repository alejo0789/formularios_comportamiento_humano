import json
import os
import random
import copy
from datetime import datetime, timedelta

DATA_DIR = "backend/data"
QUEST_DIR = "backend/questionnaires"
NEW_CEDULAS = [f"111378346{i}" for i in range(0, 10)]

def generate_intra_b_users():
    print("Starting generation of 10 users for Intralaboral Form B...")
    
    # 1. Load Questionnaire definitions to get item IDs
    with open(os.path.join(QUEST_DIR, "intralaborales-b.json"), "r", encoding="utf-8") as f:
        intra_b_quest = json.load(f)
    with open(os.path.join(QUEST_DIR, "extralaborales.json"), "r", encoding="utf-8") as f:
        extra_quest = json.load(f)
    with open(os.path.join(QUEST_DIR, "estres.json"), "r", encoding="utf-8") as f:
        estres_quest = json.load(f)
        
    intra_b_qids = [q["id"] for q in intra_b_quest["questions"]]
    extra_qids = [q["id"] for q in extra_quest["questions"]]
    estres_qids = [q["id"] for q in estres_quest["questions"]]
    
    # 2. Update form_datos-generales.json
    dg_path = os.path.join(DATA_DIR, "form_datos-generales.json")
    if os.path.exists(dg_path):
        with open(dg_path, "r", encoding="utf-8") as f:
            dg_data = json.load(f)
    else:
        dg_data = []
        
    base_time = datetime.now()
    cargos_b = ["Auxiliar de Oficina", "Operario de Planta", "Ayudante General", "Asistente Administrativo", "Mensajero"]
    areas = ["Producción", "Administración", "Logística", "Mantenimiento"]
    
    for i, cedula in enumerate(NEW_CEDULAS):
        if any(str(e.get("data", {}).get("numero_identificacion")) == cedula for e in dg_data):
            print(f"User {cedula} already exists in datos-generales, skipping dg creation.")
        else:
            new_entry = {
                "data": {
                    "numero_identificacion": cedula,
                    "nombre_completo": f"Demo Usuario B {i+1}",
                    "nombre_cargo": random.choice(cargos_b),
                    "tipo_cargo": "Auxiliar o asistente" if i % 2 == 0 else "Operario o ayudante",
                    "departamento_area": random.choice(areas),
                    "sexo": random.choice(["M", "F"]),
                    "edad": random.randint(20, 55),
                    "estado_civil": random.choice(["Soltero(a)", "Casado(a)", "Unión libre"]),
                    "nivel_estudios": random.choice(["Bachillerato completo", "Técnico/tecnólogo completo"]),
                    "antiguedad_empresa": random.choice(["Entre 1 y 5 años", "Más de 10 años"]),
                    "ciudad_residencia": "Cali",
                    "departamento_residencia": "Valle del Cauca"
                },
                "submitted_at": (base_time - timedelta(days=random.randint(0, 5))).isoformat()
            }
            dg_data.append(new_entry)
            
    with open(dg_path, "w", encoding="utf-8") as f:
        json.dump(dg_data, f, ensure_ascii=False, indent=2)
    print(f"Updated {dg_path} with 10 users.")

    # 3. Create/Update responses_intralaborales-b.json
    def generate_responses(cedula, qids, max_val=5):
        responses = []
        # Tendency for variety in the demo
        tendency = random.choice(["riesgo_bajo", "riesgo_medio", "riesgo_alto"])
        for qid in qids:
            if tendency == "riesgo_bajo":
                val = random.choice([4, 5]) if max_val == 5 else random.choice([3, 4])
            elif tendency == "riesgo_alto":
                val = random.choice([1, 2])
            else:
                val = random.randint(1, max_val)
            responses.append({"question_id": str(qid), "response_value": str(val)})
        return responses

    files = [
        ("responses_intralaborales-b.json", intra_b_qids, 5),
        ("responses_extralaborales.json", extra_qids, 5),
        ("responses_estres.json", estres_qids, 4)
    ]
    
    for filename, qids, max_val in files:
        path = os.path.join(DATA_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
            
        for i, cedula in enumerate(NEW_CEDULAS):
            if any(str(e.get("respondent_cedula")) == cedula for e in data):
                continue
                
            new_resp = {
                "respondent_cedula": cedula,
                "responses": generate_responses(cedula, qids, max_val),
                "submitted_at": (base_time - timedelta(days=random.randint(0, 5))).isoformat()
            }
            if filename == "responses_intralaborales-b.json":
                # Add conditional for customers
                new_resp["responses"].append({"question_id": "98", "response_value": "si"})
                
            data.append(new_resp)
            
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Updated {path} with 10 users.")

if __name__ == "__main__":
    generate_intra_b_users()
