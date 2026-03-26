import json
import os
import copy
from datetime import datetime, timedelta
import random

DATA_DIR = "backend/data"
BASE_CEDULA = "1113783425"
NEW_CEDULAS = [f"11137834{i}" for i in range(46, 56)]

# 1. Generate base copies in all files
files_to_process = [
    ("form_datos-generales.json", "datos-generales"),
    ("responses_estres.json", "estres"),
    ("responses_intralaborales-a.json", "intralaboral_a"),
    ("responses_extralaborales.json", "extralaboral")
]

for filename, ftype in files_to_process:
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath): continue
        
    with open(filepath, "r", encoding="utf-8") as f: data = json.load(f)
        
    base_entry = None
    if ftype == "datos-generales":
        for entry in data:
            if str(entry.get("data", {}).get("numero_identificacion")) == BASE_CEDULA:
                base_entry = entry
                break
    else:
        matching = [e for e in data if str(e.get("respondent_cedula")) == BASE_CEDULA]
        if matching:
            matching.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
            base_entry = matching[0]

    if not base_entry: continue
        
    new_entries = []
    base_time = datetime.now()
    
    for i, new_cedula in enumerate(NEW_CEDULAS):
        if ftype == "datos-generales":
            exists = any(str(e.get("data", {}).get("numero_identificacion")) == new_cedula for e in data)
        else:
            exists = any(str(e.get("respondent_cedula")) == new_cedula for e in data)
            
        if exists: continue
            
        new_entry = copy.deepcopy(base_entry)
        new_time = (base_time - timedelta(minutes=i*10)).isoformat()
        
        if ftype == "datos-generales":
            new_entry["data"]["numero_identificacion"] = new_cedula
            new_entry["data"]["nombre_completo"] = f"Usuario Extra {new_cedula[-2:]}"
            new_entry["submitted_at"] = new_time
        else:
            new_entry["respondent_cedula"] = new_cedula
            new_entry["submitted_at"] = new_time
            
        new_entries.append(new_entry)
        
    if new_entries:
        data.extend(new_entries)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# 2. Fix Demographics for these 10 users
filepath = os.path.join(DATA_DIR, "form_datos-generales.json")
with open(filepath, "r", encoding="utf-8") as f: data = json.load(f)

tipos_cargo = ["Jefatura", "Profesional", "Técnico o tecnólogo", "Auxiliar o asistente", "Operario o ayudante"]
niveles_estudios = [
    "Bachillerato completo", "Técnico/tecnólogo completo", "Profesional completo", 
    "Postgrado completo", "Bachillerato incompleto", "Técnico/tecnólogo incompleto",
    "Profesional incompleto", "Postgrado incompleto"
]
estados_civiles = ["Soltero(a)", "Casado(a)", "Unión libre", "Separado(a)", "Divorciado(a)", "Viudo(a)"]

for entry in data:
    cedula = str(entry.get("data", {}).get("numero_identificacion"))
    if cedula in NEW_CEDULAS:
        entry["data"]["tipo_cargo"] = random.choice(tipos_cargo)
        entry["data"]["nivel_estudios"] = random.choice(niveles_estudios)
        entry["data"]["estado_civil"] = random.choice(estados_civiles)
        entry["data"]["sexo"] = random.choice(["F", "M"])

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 3. Rainbow Donuts for the questionnaires (randomized scaling)
import sys
sys.path.append(os.path.abspath("backend/analisis"))
try:
    from scoring_engine import INVERSE_ITEMS
except ImportError:
    INVERSE_ITEMS = {}

TARGET_PTS = {
    "intralaboral_a": [30, 85, 135, 190, 260],
    "extralaboral": [10, 25, 35, 45, 62],
    "estres": [6, 17, 28, 40, 55] 
}

for filename, ftype in [("responses_intralaborales-a.json", "intralaboral_a"), ("responses_extralaborales.json", "extralaboral"), ("responses_estres.json", "estres")]:
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f: data = json.load(f)
    
    inverse_set = INVERSE_ITEMS.get(ftype, set())
    num_items = 123 if ftype == "intralaboral_a" else 31
    if ftype == "estres": num_items = 31
    
    for entry in data:
        if str(entry.get("respondent_cedula")) in NEW_CEDULAS:
            level = random.randint(0, 4) # completely random this time
            target = TARGET_PTS[ftype][level]
            points_assigned = 0
            avg = target // num_items
            remainder = target % num_items
            
            # Shuffle response idx mapping, to not have exactly identical answers, just identical sums
            resp_idxs = list(range(len(entry.get("responses", []))))
            random.shuffle(resp_idxs)
            
            for list_idx, idx in enumerate(resp_idxs):
                r = entry["responses"][idx]
                qid = int(r["question_id"])
                
                if points_assigned < target:
                    pt = avg
                    if list_idx < remainder: pt += 1
                    points_assigned += pt
                else:
                    pt = 0
                    
                if ftype == "estres":
                    if pt >= 3: val = 1
                    elif pt == 2: val = 2
                    elif pt == 1: val = 3
                    else: val = 4
                else:
                    is_inverse = qid in inverse_set
                    if is_inverse: val = pt + 1
                    else: val = 5 - pt
                    
                    if val < 1: val = 1
                    elif val > 5: val = 5
                r["response_value"] = str(val)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print("10 extra users injected and randomized.")
