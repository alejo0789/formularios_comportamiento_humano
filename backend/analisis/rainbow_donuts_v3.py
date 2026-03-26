import json
import os
import copy
from datetime import datetime, timedelta

from scoring_engine import INVERSE_ITEMS

DATA_DIR = "backend/data"
BASE_CEDULA = "1113783425"
CEDULAS = [f"11137834{i}" for i in range(26, 46)]

files_to_process = [
    ("responses_intralaborales-a.json", "intralaboral_a", 123),
    ("responses_extralaborales.json", "extralaboral", 31),
    ("responses_estres.json", "estres", 31)
]

# TARGET points based strictly on percentages of domains/total
# To avoid domain variance, we just give ALL questions the exact same points (0, 1, 2, 3, 4)
# In Intralaboral:
# All 0s -> Sin Riesgo
# Average 0.7 -> Bajo
# Average 1.2 -> Medio
# Average 1.6 -> Alto
# Average 2+ -> Muy Alto
TARGET_PTS = {
    "intralaboral_a": [30, 85, 135, 190, 260],
    "extralaboral": [10, 25, 35, 45, 62],
    "estres": [6, 17, 28, 40, 55] 
}

for filename, ftype, num_items in files_to_process:
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
    
    inverse_set = INVERSE_ITEMS.get(ftype, set())

    for i, cedula in enumerate(CEDULAS):
        new_entry = copy.deepcopy(base_entry)
        new_entry["respondent_cedula"] = cedula
        new_entry["submitted_at"] = (base_time - timedelta(minutes=i*10)).isoformat()
        
        level = i % 5 
        target = TARGET_PTS[ftype][level]
        points_assigned = 0
        
        avg = target // num_items
        remainder = target % num_items
        
        for idx, r in enumerate(new_entry.get("responses", [])):
            qid = int(r["question_id"])
            if points_assigned < target:
                pt = avg
                if idx < remainder: pt += 1
                points_assigned += pt
            else:
                pt = 0
                
            if ftype == "estres":
                # scale: 1=3, 2=2, 3=1, 4=0
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
            
        new_entries.append(new_entry)
        
    data.extend(new_entries)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Precise Baremos: {len(new_entries)} entries for {filename}")
