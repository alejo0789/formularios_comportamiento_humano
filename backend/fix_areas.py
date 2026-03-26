import json
import os
import random

DATA_DIR = "backend/data"
CEDULAS = [f"11137834{i}" for i in range(26, 56)]

filepath = os.path.join(DATA_DIR, "form_datos-generales.json")

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

areas = [
    "Administrativo", "Auditoría", "Comercial", "Financiero", 
    "Gerencia-Riesgos", "Mercadeo", "Operaciones", "Tecnología"
]

updated = 0
for entry in data:
    cedula = str(entry.get("data", {}).get("numero_identificacion"))
    if cedula in CEDULAS:
        entry["data"]["departamento_area"] = random.choice(areas)
        updated += 1

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Updated areas for {updated} entries.")
