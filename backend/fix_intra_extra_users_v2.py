import json
import os
import copy
from datetime import datetime, timedelta
import random

DATA_DIR = "backend/data"
BASE_CEDULA = "1113783425"
CEDULAS = [f"11137834{i}" for i in range(26, 46)]

files_to_process = [
    ("responses_intralaborales-a.json", "cuestionario", 5),
    ("responses_extralaborales.json", "cuestionario", 5)
]

user_tendencies = {}
for ced in CEDULAS:
    user_tendencies[ced] = random.choices(
        ["muy_bajo", "bajo", "medio", "alto", "muy_alto"],
        weights=[30, 25, 20, 15, 10],
        k=1
    )[0]

for filename, ftype, max_val in files_to_process:
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    matching = [e for e in data if str(e.get("respondent_cedula")) == BASE_CEDULA]
    if matching:
        matching.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        base_entry = matching[0]

    if not base_entry:
        continue
        
    data = [e for e in data if str(e.get("respondent_cedula")) not in CEDULAS]

    new_entries = []
    base_time = datetime.now()
    
    for cedula in CEDULAS:
        new_entry = copy.deepcopy(base_entry)
        new_entry["respondent_cedula"] = cedula
        new_entry["submitted_at"] = (base_time - timedelta(minutes=random.randint(10, 500))).isoformat()
        
        tendencia = user_tendencies[cedula]
        
        for r in new_entry.get("responses", []):
            # En Intra y Extra, las directas son: Siempre(1)=4_puntos, Nunca(5)=0_puntos
            # Para "muy_bajo" riesgo, queremos la mayoría de preguntas en 0 puntos (Nunca=5)
            # Para "muy_alto" riesgo, queremos 4 puntos (Siempre=1).
            
            if tendencia == "muy_bajo":
                weights = [0, 0, 10, 30, 60] # Favor 5 (Nunca) = 0 pts
            elif tendencia == "bajo":
                weights = [0, 10, 20, 40, 30] # Favor 4 y 5 = 1 y 0 pts
            elif tendencia == "medio":
                weights = [10, 20, 40, 20, 10]
            elif tendencia == "alto":
                weights = [30, 40, 20, 10, 0] # Favor 1 y 2 = 4 y 3 pts
            else: # muy_alto
                weights = [60, 30, 10, 0, 0] # Favor 1 (Siempre) = 4 pts
                
            options = [1, 2, 3, 4, 5]
            choice = random.choices(options, weights=weights, k=1)[0]
                
            r["response_value"] = str(choice)
                
        new_entries.append(new_entry)
        
    data.extend(new_entries)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Re-generated entries for {filename}")
