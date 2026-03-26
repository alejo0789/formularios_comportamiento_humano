import json
import os
import copy
from datetime import datetime, timedelta

DATA_DIR = "backend/data"
BASE_CEDULA = "1113783425"
CEDULAS = [f"11137834{i}" for i in range(26, 46)]

files_to_process = [
    ("responses_intralaborales-a.json", "intralaboral_a"),
    ("responses_extralaborales.json", "extralaboral"),
    ("responses_estres.json", "estres")
]

# Risk logic for questions:
# Estres (Max 3 points):
# Sin Riesgo: all 0. Bajo: mix 0 and 1. Medio: all 1. Alto: mix 1, 2. Muy Alto: all 3.
# Intra/Extra (Max 4 points):
# Direct: 0 pts = Nunca (5) if Intra/Extra, Siempre (1) for inverse.
# Inverse logic from scoring engine:
INVERSE_ITEMS = {
    "intralaboral_a": {
        8, 9, 10, 11, 12, 13, 14, 15, 16, 21, 22, 23, 24, 25, 26, 27, 28, 
        29, 39, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 60, 61, 62, 
        63, 64, 65, 66, 67, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88
    },
    "extralaboral": {
        22, 24, 25, 26, 27, 28, 29, 30, 31
    },
    "estres": set()
}

for filename, ftype in files_to_process:
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath): continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
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
        new_entry["submitted_at"] = (base_time - timedelta(minutes=i*10)).isoformat()
        
        # Risk levels 0 to 4 (0: Sin Riesgo, 1: Bajo, 2: Medio, 3: Alto, 4: Muy Alto)
        level = i % 5 
        
        for r in new_entry.get("responses", []):
            qid = int(r["question_id"])
            if ftype == "estres":
                # Escala 1(Siempre)=3pts ... 4(Nunca)=0pts
                # level=0 -> 4, level=1 -> mix(3,4), level=2 -> 3, level=3 -> 2, level=4 -> 1
                if level == 0: val = 4
                elif level == 1: val = 3 if qid % 2 == 0 else 4
                elif level == 2: val = 3
                elif level == 3: val = 2
                else: val = 1
            else:
                is_inverse = qid in INVERSE_ITEMS[ftype]
                # Direct points wanted:
                # level=0 -> 0 pts, level=1 -> 1 pt, level=2 -> 2 pts, level=3 -> 3 pts, level=4 -> 4 pts
                pts_wanted = level
                
                # Direct mapping: points = 5 - val => val = 5 - points
                # Inverse mapping: points = val - 1 => val = points + 1
                if is_inverse:
                    val = pts_wanted + 1
                else:
                    val = 5 - pts_wanted
                    
                # Boundary check just in case
                val = max(1, min(5, val))
                
            r["response_value"] = str(val)
            
        new_entries.append(new_entry)
        
    data.extend(new_entries)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Force-generated {len(new_entries)} deterministic entries for {filename}")
