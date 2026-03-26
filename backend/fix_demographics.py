import json
import os
import random

DATA_DIR = "backend/data"
CEDULAS = set([f"11137834{i}" for i in range(26, 46)])

filepath = os.path.join(DATA_DIR, "form_datos-generales.json")

with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

tipos_cargo = ["Jefatura", "Profesional", "Técnico o tecnólogo", "Auxiliar o asistente", "Operario o ayudante"]
niveles_estudios = [
    "Bachillerato completo", 
    "Técnico/tecnólogo completo", 
    "Profesional completo", 
    "Postgrado completo",
    "Bachillerato incompleto",
    "Técnico/tecnólogo incompleto",
    "Profesional incompleto",
    "Postgrado incompleto"
]
estados_civiles = ["Soltero(a)", "Casado(a)", "Unión libre", "Separado(a)", "Divorciado(a)", "Viudo(a)"]

updated = 0
for entry in data:
    cedula = str(entry.get("data", {}).get("numero_identificacion"))
    if cedula in CEDULAS:
        entry["data"]["tipo_cargo"] = random.choice(tipos_cargo)
        entry["data"]["nivel_estudios"] = random.choice(niveles_estudios)
        entry["data"]["estado_civil"] = random.choice(estados_civiles)
        updated += 1

if updated > 0:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Demographics fixed for {updated} entries.")
