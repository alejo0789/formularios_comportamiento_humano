import json
import os
import copy
from datetime import datetime, timedelta
import random

DATA_DIR = "backend/data"
BASE_CEDULA = "1113783425"
# Generar del 36 al 45
NEW_CEDULAS = [f"11137834{i}" for i in range(36, 46)]

files_to_process = [
    ("form_datos-generales.json", "datos-generales"),
    ("responses_estres.json", "cuestionario", 4), # 1 to 4 (Siempre, Casi Siempre, A veces, Nunca)
    ("responses_intralaborales-a.json", "cuestionario", 5), # 1 to 5
    ("responses_intralaborales-b.json", "cuestionario", 5), 
    ("responses_extralaborales.json", "cuestionario", 5)
]

for item in files_to_process:
    if len(item) == 2:
        filename, ftype = item
        max_val = None
    else:
        filename, ftype, max_val = item
        
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
        if ftype == "datos-generales":
            exists = any(str(e.get("data", {}).get("numero_identificacion")) == new_cedula for e in data)
        else:
            exists = any(str(e.get("respondent_cedula")) == new_cedula for e in data)
            
        if exists:
            print(f"Cedula {new_cedula} already exists in {filename}, skipping.")
            continue
            
        new_entry = copy.deepcopy(base_entry)
        jitter = timedelta(hours=random.randint(1, 48), minutes=random.randint(1, 60))
        new_time = (base_time - jitter).isoformat()
        
        if ftype == "datos-generales":
            new_entry["data"]["numero_identificacion"] = new_cedula
            new_entry["data"]["nombre_completo"] = f"Usuario Aleatorio {new_cedula[-2:]}"
            
            # Variar demograficos un poco
            cargos = ["Ingeniero", "Técnico", "Auxiliar", "Coordinador", "Operario"]
            areas = ["TI", "Operaciones", "Mantenimiento", "Soporte", "Recursos Humanos"]
            sexos = ["M", "F", "F", "M"]
            
            new_entry["data"]["nombre_cargo"] = random.choice(cargos)
            new_entry["data"]["departamento_area"] = random.choice(areas)
            new_entry["data"]["sexo"] = random.choice(sexos)
            new_entry["submitted_at"] = new_time
        else:
            new_entry["respondent_cedula"] = new_cedula
            new_entry["submitted_at"] = new_time
            # Variar respuestas
            for r in new_entry.get("responses", []):
                # Generamos una respuesta aleatoria dentro de la escala
                # Hacemos sesgos aleatorios para que hayan unos bien altos y otros medios
                tendencia = random.choice(["riesgo_alto", "riesgo_bajo", "neutral"])
                
                if tendencia == "riesgo_alto":
                    r["response_value"] = str(random.choice([1, 2]))  # Siempre, casi siempre (suele dar más puntos)
                elif tendencia == "riesgo_bajo":
                    r["response_value"] = str(random.choice([4, 5]) if max_val == 5 else random.choice([3, 4]))
                else:
                    r["response_value"] = str(random.randint(1, max_val))
                    
        new_entries.append(new_entry)
        
    if new_entries:
        data.extend(new_entries)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Added {len(new_entries)} entries to {filename}")
