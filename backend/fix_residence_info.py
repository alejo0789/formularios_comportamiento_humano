import json
import os
import random

DATA_DIR = "backend/data"
CEDULAS = [f"11137834{i}" for i in range(26, 56)]

filepath = os.path.join(DATA_DIR, "form_datos-generales.json")

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

ciudades = ["Cali", "Palmira", "Buga", "Jamundí", "Yumbo", "Popayán", "Santander de quilichao", "Puerto tejada", "Villarrica", "Miranda"]
estratos = ["1", "2", "3", "4", "5", "6"]
viviendas = ["Propia", "Arriendo", "Familiar", "Compartida"]

updated = 0
for entry in data:
    cedula = str(entry.get("data", {}).get("numero_identificacion"))
    if cedula in CEDULAS:
        entry["data"]["ciudad_residencia"] = random.choice(ciudades)
        entry["data"]["estrato"] = random.choice(estratos)
        entry["data"]["tipo_vivienda"] = random.choice(viviendas)
        updated += 1

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Updated residence info for {updated} entries.")
