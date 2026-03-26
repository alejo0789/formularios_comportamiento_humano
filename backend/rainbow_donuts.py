import json
import os
import copy
from datetime import datetime, timedelta
import random

DATA_DIR = "backend/data"
BASE_CEDULA = "1113783425"
CEDULAS = [f"11137834{i}" for i in range(26, 46)]

files_to_process = [
    ("responses_intralaborales-a.json", "intralaboral_a"),
    ("responses_extralaborales.json", "extralaboral"),
    ("responses_estres.json", "estres")
]

INVERSE_ITEMS = {
    "intralaboral_a": {8, 9, 10, 11, 12, 13, 14, 15, 16, 21, 22, 23, 24, 25, 26, 27, 28, 29, 39, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 60, 61, 62, 63, 64, 65, 66, 67, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88},
    "extralaboral": {22, 24, 25, 26, 27, 28, 29, 30, 31},
    "estres": set()
}

for filename, ftype in files_to_process:
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath): continue
    
    with open(filepath, "r", encoding="utf-8") as f: data = json.load(f)
        
    matching = [e for e in data if str(e.get("respondent_cedula")) == BASE_CEDULA]
    if not matching: continue
    matching.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
    base_entry = matching[0]
    
    data = [e for e in data if str(e.get("respondent_cedula")) not in CEDULAS]

    new_entries = []
    base_time = datetime.now()
    
    for i, cedula in enumerate(CEDULAS):
        new_entry = copy.deepcopy(base_entry)
        new_entry["respondent_cedula"] = cedula
        new_entry["submitted_at"] = (base_time - timedelta(minutes=i*20)).isoformat()
        
        level = i % 5 
        
        for r in new_entry.get("responses", []):
            qid = int(r["question_id"])
            if ftype == "estres":
                # Sin Riesgo(0-7.8), Bajo(7.9-12.6), Medio(12.7-17.7), Alto(17.8-25.0), Muy Alto(>25)
                # Escala pts: 0-3 (Nunca-Siempre)
                # target %: 5%, 10%, 15%, 21%, 35%
                targets = [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], # 10%
                    [0, 0, 0, 0, 1, 0, 0, 0, 0, 1], # 20%
                    [0, 0, 1, 0, 1, 0, 0, 1, 0, 0], # 30%
                    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0], # 50%
                    [2, 3, 2, 3, 2, 3, 3, 2, 3, 2]  # ~70-80%
                ]
                pt = targets[level][qid % 10]
                # Map pt to 1-4 scale where pt 0=4, 1=3, 2=2, 3=1
                val = 4 - pt 
                if val < 1: val = 1
                elif val > 4: val = 4
                
            else:
                is_inverse = qid in INVERSE_ITEMS[ftype]
                # Intra: Sin Riesgo(0-12), Bajo(12-22), Medio(22-33), Alto(33-44), Muy Alto(>44)
                # targets en pts (0 a 4) 
                targets = [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 0% (Sin Riesgo)
                    [0, 1, 0, 1, 0, 0, 1, 0, 1, 0], # ~10% (Bajo)
                    [1, 1, 1, 2, 1, 1, 1, 2, 1, 1], # ~30% (Medio)
                    [1, 2, 2, 1, 2, 2, 1, 2, 2, 1], # ~40% (Alto)
                    [2, 3, 3, 2, 4, 3, 2, 3, 3, 4]  # ~75% (Muy Alto)
                ]
                pt = targets[level][qid % 10]
                
                if is_inverse: val = pt + 1
                else: val = 5 - pt
                if val < 1: val = 1
                elif val > 5: val = 5
                
            r["response_value"] = str(val)
            
        new_entries.append(new_entry)
        
    data.extend(new_entries)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Baremos-targeted: 20 entries for {filename}")
