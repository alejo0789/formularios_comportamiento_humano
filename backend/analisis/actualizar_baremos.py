"""
Actualiza baremos.json con los valores oficiales de las Tablas 29-34
del Manual de Evaluación de Factores de Riesgo Psicosocial Intralaboral (MinTrabajo 2010).
Fuente: Tablas 29 (dims A), 30 (dims B), 31 (dominios A), 32 (dominios B), 33 (total), 34 (total general).
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE, "baremos.json")

with open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

def rng(a, b): return [a, b]

# ─────────────────────────────────────────────────────────────────────────────
# INTRALABORAL A
# ─────────────────────────────────────────────────────────────────────────────
data["intralaboral_a"]["total"] = {
    "Sin Riesgo": rng(0.0,  19.7),
    "Bajo":       rng(19.8, 25.8),
    "Medio":      rng(25.9, 31.5),
    "Alto":       rng(31.6, 38.0),
    "Muy Alto":   rng(38.1, 100),
}

data["intralaboral_a"]["dominios"] = {
    "Liderazgo y relaciones sociales": {
        "Sin Riesgo": rng(0.0,   9.1),
        "Bajo":       rng(9.2,  17.7),
        "Medio":      rng(17.8, 25.0),
        "Alto":       rng(25.1, 34.8),
        "Muy Alto":   rng(34.9, 100),
    },
    "Control sobre el trabajo": {
        "Sin Riesgo": rng(0.0,  10.7),
        "Bajo":       rng(10.8, 19.0),
        "Medio":      rng(19.1, 29.8),
        "Alto":       rng(29.9, 40.5),
        "Muy Alto":   rng(40.6, 100),
    },
    "Demandas del trabajo": {
        "Sin Riesgo": rng(0.0,  28.5),
        "Bajo":       rng(28.6, 35.0),
        "Medio":      rng(35.1, 41.5),
        "Alto":       rng(41.6, 47.5),
        "Muy Alto":   rng(47.6, 100),
    },
    "Recompensas": {
        "Sin Riesgo": rng(0.0,   4.5),
        "Bajo":       rng(4.6,  11.4),
        "Medio":      rng(11.5, 20.5),
        "Alto":       rng(20.6, 29.5),
        "Muy Alto":   rng(29.6, 100),
    },
}

data["intralaboral_a"]["dimensiones"] = {
    # Tabla 29 — Dimensiones Forma A
    "Características del liderazgo": {
        "Sin Riesgo": rng(0.0,   3.8),
        "Bajo":       rng(3.9,  15.4),
        "Medio":      rng(15.5, 30.8),
        "Alto":       rng(30.9, 46.2),
        "Muy Alto":   rng(46.3, 100),
    },
    "Relaciones sociales en el trabajo": {
        "Sin Riesgo": rng(0.0,   5.4),
        "Bajo":       rng(5.5,  16.1),
        "Medio":      rng(16.2, 25.0),
        "Alto":       rng(25.1, 33.9),
        "Muy Alto":   rng(34.0, 100),
    },
    "Retroalimentación del desempeño": {
        "Sin Riesgo": rng(0.0,  10.0),
        "Bajo":       rng(10.1, 25.0),
        "Medio":      rng(25.1, 40.0),
        "Alto":       rng(40.1, 55.0),
        "Muy Alto":   rng(55.1, 100),
    },
    "Relación con los colaboradores": {
        "Sin Riesgo": rng(0.0,  13.9),
        "Bajo":       rng(14.0, 25.0),
        "Medio":      rng(25.1, 33.3),
        "Alto":       rng(33.4, 47.2),
        "Muy Alto":   rng(47.3, 100),
    },
    "Claridad de rol": {
        "Sin Riesgo": rng(0.0,   0.9),
        "Bajo":       rng(1.0,  10.7),
        "Medio":      rng(10.8, 21.4),
        "Alto":       rng(21.5, 39.3),
        "Muy Alto":   rng(39.4, 100),
    },
    "Capacitación": {
        "Sin Riesgo": rng(0.0,   0.9),
        "Bajo":       rng(1.0,   8.3),
        "Medio":      rng(8.4,  16.7),
        "Alto":       rng(16.8, 37.5),
        "Muy Alto":   rng(37.6, 100),
    },
    "Participación y manejo del cambio": {
        "Sin Riesgo": rng(0.0,  12.5),
        "Bajo":       rng(12.6, 25.0),
        "Medio":      rng(25.1, 37.5),
        "Alto":       rng(37.6, 50.0),
        "Muy Alto":   rng(50.1, 100),
    },
    "Oportunidades para el uso y desarrollo de habilidades": {
        "Sin Riesgo": rng(0.0,   0.9),
        "Bajo":       rng(1.0,   6.3),
        "Medio":      rng(6.4,  18.8),
        "Alto":       rng(18.9, 31.3),
        "Muy Alto":   rng(31.4, 100),
    },
    "Control y autonomía sobre el trabajo": {
        "Sin Riesgo": rng(0.0,   8.3),
        "Bajo":       rng(8.4,  25.0),
        "Medio":      rng(25.1, 41.7),
        "Alto":       rng(41.8, 58.3),
        "Muy Alto":   rng(58.4, 100),
    },
    "Demandas ambientales": {
        "Sin Riesgo": rng(0.0,  14.6),
        "Bajo":       rng(14.7, 22.9),
        "Medio":      rng(23.0, 31.3),
        "Alto":       rng(31.4, 39.6),
        "Muy Alto":   rng(39.7, 100),
    },
    "Demandas emocionales": {
        "Sin Riesgo": rng(0.0,  16.7),
        "Bajo":       rng(16.8, 25.0),
        "Medio":      rng(25.1, 33.3),
        "Alto":       rng(33.4, 44.4),
        "Muy Alto":   rng(44.5, 100),
    },
    "Demandas cuantitativas": {
        "Sin Riesgo": rng(0.0,  25.0),
        "Bajo":       rng(25.1, 33.3),
        "Medio":      rng(33.4, 45.8),
        "Alto":       rng(45.9, 54.2),
        "Muy Alto":   rng(54.3, 100),
    },
    "Influencia del trabajo sobre el entorno extralaboral": {
        "Sin Riesgo": rng(0.0,  18.8),
        "Bajo":       rng(18.9, 31.3),
        "Medio":      rng(31.4, 43.8),
        "Alto":       rng(43.9, 56.3),
        "Muy Alto":   rng(56.4, 100),
    },
    "Demandas de responsabilidad del cargo": {
        "Sin Riesgo": rng(0.0,  37.5),
        "Bajo":       rng(37.6, 54.2),
        "Medio":      rng(54.3, 66.7),
        "Alto":       rng(66.8, 79.2),
        "Muy Alto":   rng(79.3, 100),
    },
    "Demandas de carga mental": {
        "Sin Riesgo": rng(0.0,  60.0),
        "Bajo":       rng(60.1, 70.0),
        "Medio":      rng(70.1, 80.0),
        "Alto":       rng(80.1, 90.0),
        "Muy Alto":   rng(90.1, 100),
    },
    "Demandas de jornada de trabajo": {
        "Sin Riesgo": rng(0.0,   8.3),
        "Bajo":       rng(8.4,  25.0),
        "Medio":      rng(25.1, 41.7),
        "Alto":       rng(41.8, 58.3),
        "Muy Alto":   rng(58.4, 100),
    },
    "Consistencia del rol": {
        "Sin Riesgo": rng(0.0,   8.3),
        "Bajo":       rng(8.4,  33.3),
        "Medio":      rng(33.4, 58.3),
        "Alto":       rng(58.4, 75.0),
        "Muy Alto":   rng(75.1, 100),
    },
    "Recompensas derivadas de la pertenencia a la organización": {
        "Sin Riesgo": rng(0.0,   0.9),
        "Bajo":       rng(1.0,   5.0),
        "Medio":      rng(5.1,  10.0),
        "Alto":       rng(10.1, 20.0),
        "Muy Alto":   rng(20.1, 100),
    },
    "Reconocimiento y compensación": {
        "Sin Riesgo": rng(0.0,   4.2),
        "Bajo":       rng(4.3,  16.7),
        "Medio":      rng(16.8, 25.0),
        "Alto":       rng(25.1, 37.5),
        "Muy Alto":   rng(37.6, 100),
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# INTRALABORAL B
# ─────────────────────────────────────────────────────────────────────────────
data["intralaboral_b"]["total"] = {
    "Sin Riesgo": rng(0.0,  20.6),
    "Bajo":       rng(20.7, 26.0),
    "Medio":      rng(26.1, 31.2),
    "Alto":       rng(31.3, 38.7),
    "Muy Alto":   rng(38.8, 100),
}

data["intralaboral_b"]["dominios"] = {
    "Liderazgo y relaciones sociales": {
        "Sin Riesgo": rng(0.0,   8.3),
        "Bajo":       rng(8.4,  17.5),
        "Medio":      rng(17.6, 26.7),
        "Alto":       rng(26.8, 38.3),
        "Muy Alto":   rng(38.4, 100),
    },
    "Control sobre el trabajo": {
        "Sin Riesgo": rng(0.0,  19.4),
        "Bajo":       rng(19.5, 26.4),
        "Medio":      rng(26.5, 34.7),
        "Alto":       rng(34.8, 43.1),
        "Muy Alto":   rng(43.2, 100),
    },
    "Demandas del trabajo": {
        "Sin Riesgo": rng(0.0,  26.9),
        "Bajo":       rng(27.0, 33.3),
        "Medio":      rng(33.4, 37.8),
        "Alto":       rng(37.9, 44.2),
        "Muy Alto":   rng(44.3, 100),
    },
    "Recompensas": {
        "Sin Riesgo": rng(0.0,   2.5),
        "Bajo":       rng(2.6,  10.0),
        "Medio":      rng(10.1, 17.5),
        "Alto":       rng(17.6, 27.5),
        "Muy Alto":   rng(27.6, 100),
    },
}

data["intralaboral_b"]["dimensiones"] = {
    # Tabla 30 — Dimensiones Forma B
    "Características del liderazgo": {
        "Sin Riesgo": rng(0.0,   3.8),
        "Bajo":       rng(3.9,  13.5),
        "Medio":      rng(13.6, 25.0),
        "Alto":       rng(25.1, 38.5),
        "Muy Alto":   rng(38.6, 100),
    },
    "Relaciones sociales en el trabajo": {
        "Sin Riesgo": rng(0.0,   6.3),
        "Bajo":       rng(6.4,  14.6),
        "Medio":      rng(14.7, 27.1),
        "Alto":       rng(27.2, 37.5),
        "Muy Alto":   rng(37.6, 100),
    },
    "Retroalimentación del desempeño": {
        "Sin Riesgo": rng(0.0,   5.1),
        "Bajo":       rng(5.2,  20.0),
        "Medio":      rng(20.1, 30.0),
        "Alto":       rng(30.1, 40.0),
        "Muy Alto":   rng(40.1, 100),
    },
    "Claridad de rol": {
        "Sin Riesgo": rng(0.0,   0.9),
        "Bajo":       rng(1.0,   5.0),
        "Medio":      rng(5.1,  15.0),
        "Alto":       rng(15.1, 30.0),
        "Muy Alto":   rng(30.1, 100),
    },
    "Capacitación": {
        "Sin Riesgo": rng(0.0,  16.7),
        "Bajo":       rng(16.8, 25.0),
        "Medio":      rng(25.1, 33.3),
        "Alto":       rng(33.4, 41.7),
        "Muy Alto":   rng(41.8, 100),
    },
    "Participación y manejo del cambio": {
        "Sin Riesgo": rng(0.0,  16.7),
        "Bajo":       rng(16.8, 33.3),
        "Medio":      rng(33.4, 44.4),
        "Alto":       rng(44.5, 58.3),
        "Muy Alto":   rng(58.4, 100),
    },
    "Oportunidades para el uso y desarrollo de habilidades": {
        "Sin Riesgo": rng(0.0,  12.5),
        "Bajo":       rng(12.6, 25.0),
        "Medio":      rng(25.1, 37.5),
        "Alto":       rng(37.6, 56.3),
        "Muy Alto":   rng(56.4, 100),
    },
    "Control y autonomía sobre el trabajo": {
        "Sin Riesgo": rng(0.0,  22.9),
        "Bajo":       rng(23.0, 31.3),
        "Medio":      rng(31.4, 39.6),
        "Alto":       rng(39.7, 47.9),
        "Muy Alto":   rng(48.0, 100),
    },
    "Demandas ambientales": {
        "Sin Riesgo": rng(0.0,  22.9),
        "Bajo":       rng(23.0, 31.3),
        "Medio":      rng(31.4, 39.6),
        "Alto":       rng(39.7, 47.9),
        "Muy Alto":   rng(48.0, 100),
    },
    "Demandas cuantitativas": {
        "Sin Riesgo": rng(0.0,  16.7),
        "Bajo":       rng(16.8, 33.3),
        "Medio":      rng(33.4, 41.7),
        "Alto":       rng(41.8, 50.0),
        "Muy Alto":   rng(50.1, 100),
    },
    "Demandas emocionales": {
        "Sin Riesgo": rng(0.0,  16.7),
        "Bajo":       rng(16.8, 33.3),
        "Medio":      rng(33.4, 44.4),
        "Alto":       rng(44.5, 55.6),
        "Muy Alto":   rng(55.7, 100),
    },
    "Influencia del trabajo sobre el entorno extralaboral": {
        "Sin Riesgo": rng(0.0,  12.5),
        "Bajo":       rng(12.6, 25.0),
        "Medio":      rng(25.1, 31.3),
        "Alto":       rng(31.4, 43.8),
        "Muy Alto":   rng(43.9, 100),
    },
    "Demandas de carga mental": {
        "Sin Riesgo": rng(0.0,  50.0),
        "Bajo":       rng(50.1, 65.0),
        "Medio":      rng(65.1, 75.0),
        "Alto":       rng(75.1, 85.0),
        "Muy Alto":   rng(85.1, 100),
    },
    "Demandas de jornada de trabajo": {
        "Sin Riesgo": rng(0.0,  25.0),
        "Bajo":       rng(25.1, 37.5),
        "Medio":      rng(37.6, 45.8),
        "Alto":       rng(45.9, 58.3),
        "Muy Alto":   rng(58.4, 100),
    },
    "Recompensas derivadas de la pertenencia a la organización": {
        "Sin Riesgo": rng(0.0,   0.9),
        "Bajo":       rng(1.0,   6.3),
        "Medio":      rng(6.4,  12.5),
        "Alto":       rng(12.6, 18.8),
        "Muy Alto":   rng(18.9, 100),
    },
    "Reconocimiento y compensación": {
        "Sin Riesgo": rng(0.0,   0.9),
        "Bajo":       rng(1.0,  12.5),
        "Medio":      rng(12.6, 25.0),
        "Alto":       rng(25.1, 37.5),
        "Muy Alto":   rng(37.6, 100),
    },
}

# total_general ya está correcto (Tabla 34) — no se modifica

data["version"] = "2.0"
data["fuente"] = "Tablas 29-34 Manual Evaluacion Factores Riesgo Psicosocial Intralaboral MinTrabajo 2010"

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("✅ baremos.json actualizado correctamente con Tablas 29-34 del manual oficial.")
print(f"   Guardado en: {PATH}")
