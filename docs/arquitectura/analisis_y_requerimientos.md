# Análisis de Manuales y Requerimientos - Módulo Psicosocial

Este documento detalla el análisis realizado a los manuales de la Batería de Instrumentos para la Evaluación de Factores de Riesgo Psicosocial (MinTrabajo, 2010/2024) y los requerimientos funcionales extraídos para la implementación del sistema.

## 1. Análisis de Manuales

El sistema se basa en la metodología oficial colombiana para la evaluación del riesgo psicosocial. El análisis se centró en los siguientes instrumentos:
- **Cuestionario de Factores de Riesgo Psicosocial Intralaboral (Forma A y B):** Evaluación de condiciones internas al trabajo.
- **Cuestionario de Factores de Riesgo Psicosocial Extralaboral:** Evaluación de condiciones externas al entorno laboral.
- **Cuestionario para la Evaluación del Estrés:** Manifestaciones de síntomas de estrés en el trabajador.
- **Ficha de Datos Generales:** Información sociodemográfica y laboral necesaria para la segmentación y aplicación de baremos.

### Proceso de Calificación General
1. **Lectura de respuestas:** Valores de 1 a 5 (Intra/Extra) o 1 a 4 (Estrés).
2. **Normalización:** Conversión a escala 0-4 aplicando reglas de inversión cuando el ítem lo requiere.
3. **Cálculo de Puntajes Brutos:** Suma de valores por dimensión y dominio.
4. **Transformación:** Aplicación de fórmulas para llevar los puntajes a una escala de 0 a 100.
5. **Clasificación:** Consulta de tablas de baremos para asignar el nivel de riesgo (Sin Riesgo, Bajo, Medio, Alto, Muy Alto).

---

## 2. Requerimientos Funcionales

### RF-01 · Motor de Calificación por Ítem
El sistema debe calificar cada respuesta individual aplicando las reglas de escala directa e inversa.
- **Forma A:** 123 ítems.
- **Forma B:** 97 ítems.
- **Normalización:** Los valores 1-5 se convierten a 0-4 antes de la inversión.

### RF-02 · Cálculo de Puntajes por Dimensión
Para cada dimensión, el sistema calcula:
- **Puntaje Bruto:** Suma de ítems.
- **Puntaje Máximo Posible:** Número de ítems × 4.
- **Puntaje Transformado:** `(Puntaje Bruto / Puntaje Máximo) × 100`.

### RF-03 · Cálculo de Puntajes por Dominio
Suma de puntajes brutos de todas las dimensiones del dominio y cálculo del transformado sobre el máximo agregado.

### RF-04 · Clasificación de Nivel de Riesgo
Asignación de niveles según baremos normativos. El sistema debe soportar baremos dinámicos configurables.

### RF-05 · Análisis Individual
Consulta de resultados por número de cédula, incluyendo:
- Datos sociodemográficos.
- Puntajes y niveles de riesgo por cuestionario, dominio y dimensión.
- Forma aplicada (A o B) según personal a cargo.

### RF-06 · Análisis Grupal y por Segmento
Estadísticas agregadas filtrando por:
- Área / Departamento.
- Cargo / Tipo de cargo.
- Sexo, Antigüedad, etc.

### RF-07 · Dashboard Visual
Panel con indicadores KPI, gráficas de dona (distribución de riesgo), barras (comparativo de dominios), radar (perfil individual) y tablas resumen.

### RF-08 · Generación de Reportes PDF
Generación de documentos exportables organizados por secciones individuales y grupales.

### RF-09 · Calificación del Cuestionario de Estrés
Motor específico con calificación por grupos de ítems (Escalas A, B, C con valores 9/6/3, 6/4/2, 3/2/1) y ponderación por bloques. El puntaje transformado usa el divisor fijo **61.16**.

---

## 3. Estructura de Dimensiones y Dominios

### Forma A (Jefes, Profesionales, Técnicos)
| Dominio | Dimensiones | Ítems |
| :--- | :--- | :--- |
| **Control sobre el trabajo** | Claridad de rol, Capacitación, Participación, Uso de habilidades, Control/Autonomía | 1–26 |
| **Demandas del trabajo** | Ambientales, Emocionales, Cuantitativas, Influencia extra laboral, Carga mental, Consistencia de rol, Jornada | 27–80 |
| **Liderazgo y relaciones** | Características liderazgo, Relaciones sociales, Retroalimentación | 81–116 |
| **Recompensas** | Reconocimiento y compensación | 117–123 |

### Forma B (Auxiliares y Operarios)
| Dominio | Dimensiones | Ítems |
| :--- | :--- | :--- |
| **Control sobre el trabajo** | Claridad de rol, Capacitación, Participación, Uso de habilidades, Control/Autonomía | 1–25 |
| **Demandas del trabajo** | Ambientales, Emocionales, Cuantitativas, Influencia extra laboral, Carga mental, Jornada | 26–66 |
| **Liderazgo y relaciones** | Características liderazgo, Relaciones sociales, Retroalimentación | 67–97 |

### Extralaboral
Incluye 7 dimensiones: Balance vida-trabajo, Relaciones familiares, Comunicación, Situación económica, Vivienda y entorno, Influencia extra laboral sobre el trabajo, Desplazamiento.

---

## 4. Criterios de Aceptación (Resumen)
- **CA-01:** Calificación correcta de ítems Forma A (Tabla 21).
- **CA-11:** Calificación de Estrés por bloques con escalas correctas (9/6/3, etc).
- **CA-13:** Puntaje transformado de estrés con exactamente 1 decimal.
- **CA-19:** Factor de transformación total general (616 para A, 512 para B).
- **CA-20:** Selección de baremo extralaboral según nivel ocupacional.
