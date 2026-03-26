import json
import os
import copy
from datetime import datetime, timedelta

DATA_DIR = "backend/data"
BASE_CEDULA = "1113783425"
CEDULAS = [f"11137834{i}" for i in range(26, 46)]

files_to_process = [
    ("responses_intralaborales-a.json", "intralaboral_a", 123),
    ("responses_extralaborales.json", "extralaboral", 31),
    ("responses_estres.json", "estres", 31)
]

INVERSE_ITEMS = {
    "intralaboral_a": {8, 9, 10, 11, 12, 13, 14, 15, 16, 21, 22, 23, 24, 25, 26, 27, 28, 29, 39, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 60, 61, 62, 63, 64, 65, 66, 67, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88},
    "extralaboral": {22, 24, 25, 26, 27, 28, 29, 30, 31},
    "estres": set()
}

# The sum of points needed for each risk level
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
    
    for i, cedula in enumerate(CEDULAS):
        new_entry = copy.deepcopy(base_entry)
        new_entry["respondent_cedula"] = cedula
        new_entry["submitted_at"] = (base_time - timedelta(minutes=i*10)).isoformat()
        
        level = i % 5 
        target = TARGET_PTS[ftype][level]
        points_assigned = 0
        
        # We sequentially assign points to match exactly target
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
                is_inverse = qid in INVERSE_ITEMS[ftype]
                if is_inverse: val = pt + 1
                else: val = 5 - pt
                
                if val < 1: val = 1
                elif val > 5: val = 5
                
            r["response_value"] = str(val)
            
        new_entries.append(new_entry)
        
    data.extend(new_entries)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Pinpoint target logic: {len(new_entries)} entries for {filename}")
