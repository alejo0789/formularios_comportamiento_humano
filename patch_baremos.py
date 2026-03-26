import json

file_path = "backend/analisis/baremos.json"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

data["extralaboral"] = {
    "profesionales_directivos": {
        "total": {
            "Sin Riesgo": [0.0, 11.3],
            "Bajo": [11.4, 16.9],
            "Medio": [17.0, 22.6],
            "Alto": [22.7, 29.0],
            "Muy Alto": [29.1, 100]
        },
        "dimensiones": {
            "Balance entre la vida laboral y familiar": {
                "factor_transformacion": 16,
                "Sin Riesgo": [0.0, 6.3],
                "Bajo": [6.4, 25.0],
                "Medio": [25.1, 37.5],
                "Alto": [37.6, 50.0],
                "Muy Alto": [50.1, 100]
            },
            "Relaciones familiares": {
                "factor_transformacion": 12,
                "Sin Riesgo": [0.0, 8.3],
                "Bajo": [8.4, 25.0],
                "Medio": [25.1, 33.3],
                "Alto": [33.4, 50.0],
                "Muy Alto": [50.1, 100]
            },
            "Comunicación y relaciones interpersonales": {
                "factor_transformacion": 20,
                "Sin Riesgo": [0.0, 0.9],
                "Bajo": [1.0, 10.0],
                "Medio": [10.1, 20.0],
                "Alto": [20.1, 30.0],
                "Muy Alto": [30.1, 100]
            },
            "Situación económica del grupo familiar": {
                "factor_transformacion": 12,
                "Sin Riesgo": [0.0, 8.3],
                "Bajo": [8.4, 25.0],
                "Medio": [25.1, 33.3],
                "Alto": [33.4, 50.0],
                "Muy Alto": [50.1, 100]
            },
            "Características de la vivienda y de su entorno": {
                "factor_transformacion": 36,
                "Sin Riesgo": [0.0, 5.6],
                "Bajo": [5.7, 11.1],
                "Medio": [11.2, 13.9],
                "Alto": [14.0, 22.2],
                "Muy Alto": [22.3, 100]
            },
            "Influencia del entorno extralaboral sobre el trabajo": {
                "factor_transformacion": 12,
                "Sin Riesgo": [0.0, 8.3],
                "Bajo": [8.4, 16.7],
                "Medio": [16.8, 25.0],
                "Alto": [25.1, 41.7],
                "Muy Alto": [41.8, 100]
            },
            "Desplazamiento vivienda trabajo vivienda": {
                "factor_transformacion": 16,
                "Sin Riesgo": [0.0, 0.9],
                "Bajo": [1.0, 12.5],
                "Medio": [12.6, 25.0],
                "Alto": [25.1, 43.8],
                "Muy Alto": [43.9, 100]
            }
        }
    },
    "auxiliares_operativos": {
        "total": {
            "Sin Riesgo": [0.0, 12.9],
            "Bajo": [13.0, 17.7],
            "Medio": [17.8, 24.2],
            "Alto": [24.3, 32.3],
            "Muy Alto": [32.4, 100]
        },
        "dimensiones": {
            "Balance entre la vida laboral y familiar": {
                "factor_transformacion": 16,
                "Sin Riesgo": [0.0, 6.3],
                "Bajo": [6.4, 25.0],
                "Medio": [25.1, 37.5],
                "Alto": [37.6, 50.0],
                "Muy Alto": [50.1, 100]
            },
            "Relaciones familiares": {
                "factor_transformacion": 12,
                "Sin Riesgo": [0.0, 8.3],
                "Bajo": [8.4, 25.0],
                "Medio": [25.1, 33.3],
                "Alto": [33.4, 50.0],
                "Muy Alto": [50.1, 100]
            },
            "Comunicación y relaciones interpersonales": {
                "factor_transformacion": 20,
                "Sin Riesgo": [0.0, 5.0],
                "Bajo": [5.1, 15.0],
                "Medio": [15.1, 25.0],
                "Alto": [25.1, 35.0],
                "Muy Alto": [35.1, 100]
            },
            "Situación económica del grupo familiar": {
                "factor_transformacion": 12,
                "Sin Riesgo": [0.0, 16.7],
                "Bajo": [16.8, 25.0],
                "Medio": [25.1, 41.7],
                "Alto": [41.8, 50.0],
                "Muy Alto": [50.1, 100]
            },
            "Características de la vivienda y de su entorno": {
                "factor_transformacion": 36,
                "Sin Riesgo": [0.0, 5.6],
                "Bajo": [5.7, 11.1],
                "Medio": [11.2, 16.7],
                "Alto": [16.8, 27.8],
                "Muy Alto": [27.9, 100]
            },
            "Influencia del entorno extralaboral sobre el trabajo": {
                "factor_transformacion": 12,
                "Sin Riesgo": [0.0, 0.9],
                "Bajo": [1.0, 16.7],
                "Medio": [16.8, 25.0],
                "Alto": [25.1, 41.7],
                "Muy Alto": [41.8, 100]
            },
            "Desplazamiento vivienda trabajo vivienda": {
                "factor_transformacion": 16,
                "Sin Riesgo": [0.0, 0.9],
                "Bajo": [1.0, 12.5],
                "Medio": [12.6, 25.0],
                "Alto": [25.1, 43.8],
                "Muy Alto": [43.9, 100]
            }
        }
    }
}

data["total_general"] = {
    "forma_a": {
        "factor": 616,
        "Sin Riesgo": [0.0, 18.8],
        "Bajo": [18.9, 24.4],
        "Medio": [24.5, 29.5],
        "Alto": [29.6, 35.4],
        "Muy Alto": [35.5, 100]
    },
    "forma_b": {
        "factor": 512,
        "Sin Riesgo": [0.0, 19.9],
        "Bajo": [20.0, 24.8],
        "Medio": [24.9, 29.5],
        "Alto": [29.6, 35.4],
        "Muy Alto": [35.5, 100]
    }
}

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
