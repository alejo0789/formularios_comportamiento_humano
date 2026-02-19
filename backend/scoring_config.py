# Scoring configuration for Riesgo Psicosocial
# Direct: Siempre=4, Casi siempre=3, Algunas veces=2, Casi nunca=1, Nunca=0
# Inverse: Siempre=0, Casi siempre=1, Algunas veces=2, Casi nunca=3, Nunca=4

# Mapping of question IDs that are INVERSE for each questionnaire
INVERSE_QUESTIONS = {
    "estres": [], # All symptoms are direct (more frequency = more stress)
    "extralaborales": [
        # Questions about positive aspects of extra-laboral life
        # List of IDs (needs careful check)
    ],
    "intralaborales-a": [
        4, 5, 6, 9, 12, 14, 32, 34, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
        53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75,
        76, 77, 78, 79, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 105
    ],
    "intralaborales-b": [
        4, 5, 6, 9, 12, 14, 21, 23, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65,
        66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 96
    ]
}

# Domain and Dimension definitions for Intralaboral A
INTRALABORAL_A_STRUCTURE = {
    "Liderazgo y relaciones sociales": {
        "Características del liderazgo": [63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75],
        "Relaciones sociales en el trabajo": [76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89],
        "Retroalimentación del desempeño": [90, 91, 92, 93, 94],
        "Relación con los colaboradores": [115, 116, 117, 118, 119, 120, 121, 122, 123]
    },
    "Control sobre el trabajo": {
        "Claridad de rol": [53, 54, 55, 56, 57, 58, 59],
        "Capacitación": [60, 61, 62],
        "Participación y manejo del cambio": [48, 49, 50, 51, 52],
        "Oportunidades para el uso y desarrollo de habilidades": [39, 40, 41, 42],
        "Control y autonomía sobre el trabajo": [43, 44, 45, 46, 47]
    },
    "Demandas del trabajo": {
        "Demandas ambientales": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "Demandas cuantitativas": [13, 14, 15],
        "Demandas de carga mental": [16, 17, 18, 19, 20, 21],
        "Demandas emocionales": [106, 107, 108, 109, 110, 111, 112, 113, 114],
        "Demandas de responsabilidad del cargo": [22, 23, 24, 25, 26],
        "Demandas de jornada de trabajo": [31, 32, 33, 34],
        "Consistencia del rol": [27, 28, 29, 30],
        "Influencia del trabajo sobre el entorno extralaboral": [35, 36, 37, 38]
    },
    "Recompensas": {
        "Recompensas derivadas de la pertenencia a la organización": [95, 96, 97, 98, 99, 100, 101, 102],
        "Reconocimiento y compensación": [103, 104, 105]
    }
}

INTRALABORAL_B_STRUCTURE = {
    "Liderazgo y relaciones sociales": {
        "Características del liderazgo": [49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61],
        "Relaciones sociales en el trabajo": [62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73],
        "Retroalimentación del desempeño": [74, 75, 76, 77, 78]
    },
    "Control sobre el trabajo": {
        "Claridad de rol": [41, 42, 43, 44, 45],
        "Capacitación": [46, 47, 48],
        "Participación y manejo del cambio": [38, 39, 40],
        "Control y autonomía sobre el trabajo": [29, 30, 31, 32, 33, 34, 35, 36, 37]
    },
    "Demandas del trabajo": {
        "Demandas ambientales": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "Demandas cuantitativas": [13, 14, 15],
        "Demandas de carga mental": [16, 17, 18, 19, 20],
        "Demandas emocionales": [89, 90, 91, 92, 93, 94, 95, 96, 97],
        "Demandas de jornada de trabajo": [21, 22, 23, 24],
        "Influencia del trabajo sobre el entorno extralaboral": [25, 26, 27, 28]
    },
    "Recompensas": {
        "Recompensas derivadas de la pertenencia a la organización": [82, 83, 84, 85, 86, 87, 88],
        "Reconocimiento y compensación": [79, 80, 81]
    }
}

# (Baremos and further thresholds would go here)
