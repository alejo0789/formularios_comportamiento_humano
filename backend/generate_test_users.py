import json
import os
import copy
from datetime import datetime, timedelta
import random

DATA_DIR = "backend/data"
BASE_CEDULA = "1113783425"
NEW_CEDULAS = [f"11137834{i}" for i in range(26, 36)]

files_to_process = [
    ("form_datos-generales.json", "datos-generales"),
    ("responses_estres.json", "cuestionario"),
    ("responses_intralaborales-a.json", "cuestionario"),
    ("responses_intralaborales-b.json", "cuestionario"),
    ("responses_extralaborales.json", "cuestionario")
]

for filename, ftype in files_to_process:
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Find base entry
    base_entry = None
    if ftype == "datos-generales":
        for entry in data:
            if str(entry.get("data", {}).get("numero_identificacion")) == BASE_CEDULA:
                base_entry = entry
                break
    else:
        # Get the most recent one
        matching = [e for e in data if str(e.get("respondent_cedula")) == BASE_CEDULA]
        if matching:
            matching.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
            base_entry = matching[0]

    if not base_entry:
        print(f"Base entry not found in {filename}")
        continue
        
    new_entries = []
    base_time = datetime.now()
    
    for i, new_cedula in enumerate(NEW_CEDULAS):
        # Check if already exists to avoid endless duplicates
        if ftype == "datos-generales":
            exists = any(str(e.get("data", {}).get("numero_identificacion")) == new_cedula for e in data)
        else:
            exists = any(str(e.get("respondent_cedula")) == new_cedula for e in data)
            
        if exists:
            print(f"Cedula {new_cedula} already exists in {filename}, skipping.")
            continue
            
        new_entry = copy.deepcopy(base_entry)
        jitter = timedelta(minutes=random.randint(1, 60))
        new_time = (base_time - jitter).isoformat()
        
        if ftype == "datos-generales":
            new_entry["data"]["numero_identificacion"] = new_cedula
            new_entry["data"]["nombre_completo"] = f"Usuario Prueba {new_cedula[-2:]}"
            new_entry["submitted_at"] = new_time
        else:
            new_entry["respondent_cedula"] = new_cedula
            new_entry["submitted_at"] = new_time
            # Option to slightly vary responses could go here, but doing identical for now as requested
            
        new_entries.append(new_entry)
        
    if new_entries:
        data.extend(new_entries)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Added {len(new_entries)} entries to {filename}")
