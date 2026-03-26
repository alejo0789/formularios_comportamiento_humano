import json
import os
import copy
from datetime import datetime, timedelta
import random

DATA_DIR = "backend/data"
BASE_CEDULA = "1113783425"
# Vamos a reescribir desde el 26 hasta el 45 con tendencias FIJAS por usuario
CEDULAS = [f"11137834{i}" for i in range(26, 46)]

files_to_process = [
    ("form_datos-generales.json", "datos-generales", None),
    ("responses_estres.json", "cuestionario", 4), # 1 to 4 
    ("responses_intralaborales-a.json", "cuestionario", 5), # 1 to 5
    ("responses_extralaborales.json", "cuestionario", 5)
]

# Tendencia por usuario para que no promedien hacia 50% y caigan casi todos en "Muy Alto"
# Los baremos normales suelen tener el percentil 50 muy abajo (ej. 25 puntos)
# Para forzar un riesgo BAJO/SIN RIESGO, casi todas las rtas deben ser 0 puntos (Nunca / Siempre dependiendo si es directo/inverso)
# Así que definimos la tendencia por usuario aquí:
user_tendencies = {}
for ced in CEDULAS:
    # 35% Sin Riesgo/Bajo, 35% Medio, 30% Alto/Muy Alto
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
        
    # Get base entry
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
        continue
        
    # Remove older generated entries to overwrite them cleanly
    if ftype == "datos-generales":
        data = [e for e in data if str(e.get("data", {}).get("numero_identificacion")) not in CEDULAS]
    else:
        data = [e for e in data if str(e.get("respondent_cedula")) not in CEDULAS]

    new_entries = []
    base_time = datetime.now()
    
    for cedula in CEDULAS:
        new_entry = copy.deepcopy(base_entry)
        jitter = timedelta(hours=random.randint(1, 48), minutes=random.randint(1, 60))
        new_time = (base_time - jitter).isoformat()
        
        tendencia = user_tendencies[cedula]
        
        if ftype == "datos-generales":
            new_entry["data"]["numero_identificacion"] = cedula
            new_entry["data"]["nombre_completo"] = f"Usuario {tendencia.replace('_', ' ').title()} {cedula[-2:]}"
            
            cargos = ["Ingeniero", "Técnico", "Auxiliar", "Coordinador", "Operario"]
            areas = ["TI", "Operaciones", "Mantenimiento", "Soporte", "Recursos Humanos"]
            sexos = ["M", "F", "F", "M"]
            
            new_entry["data"]["nombre_cargo"] = random.choice(cargos)
            new_entry["data"]["departamento_area"] = random.choice(areas)
            new_entry["data"]["sexo"] = random.choice(sexos)
            new_entry["submitted_at"] = new_time
        else:
            new_entry["respondent_cedula"] = cedula
            new_entry["submitted_at"] = new_time
            # Modify responses based on user tendency
            for r in new_entry.get("responses", []):
                # Scale mapping logic approx: 
                # Direct questions: 1=Siempre(worst), 5=Nunca(best) except for inverse.
                # To simulate risk properly, we usually want: 
                # muy_bajo -> answers 4 or 5 mostly
                # bajo -> answers 3 or 4 mostly
                # medio -> answers 2, 3, 4
                # alto -> answers 1, 2, 3
                # muy_alto -> answers 1 or 2
                if tendencia == "muy_bajo":
                    weights = [0, 5, 10, 35, 50]
                elif tendencia == "bajo":
                    weights = [5, 10, 25, 40, 20]
                elif tendencia == "medio":
                    weights = [10, 20, 40, 20, 10]
                elif tendencia == "alto":
                    weights = [25, 45, 20, 10, 0]
                else: # muy_alto
                    weights = [50, 40, 10, 0, 0]
                
                # If scale is 1 to 4:
                if max_val == 4:
                    # just collapse options 4 and 5
                    w4 = weights[:3] + [sum(weights[3:])]
                    options = [1, 2, 3, 4]
                    choice = random.choices(options, weights=w4, k=1)[0]
                else:
                    options = [1, 2, 3, 4, 5]
                    choice = random.choices(options, weights=weights, k=1)[0]
                    
                r["response_value"] = str(choice)
                
        new_entries.append(new_entry)
        
    data.extend(new_entries)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Re-generated {len(new_entries)} entries for {filename}")
