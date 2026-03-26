# Análisis Dinámico y Gestión de la Información

El sistema de Análisis Psicosocial se encarga de la orquestación de datos provenientes de múltiples cuestionarios para producir información procesable.

## 1. El Servicio de Análisis (`AnalysisService`)

El componente `AnalysisService` actúa como el corazón del backend, coordinando el flujo de información entre el motor de calificación (`ScoringEngine`) y las fuentes de datos persistentes.

### Tareas Principales
1. **Recolección de Datos:** Carga las respuestas más recientes de los archivos JSON (`form_datos-generales.json`, `responses_*.json`).
2. **Determinación de Forma:** Identifica automáticamente si un trabajador debe ser calificado con la **Forma A** (si tiene personal a cargo) o **Forma B** (si no lo tiene), según la ficha de datos generales.
3. **Calificación Individual:** Integra los resultados de Intra, Extra y Estrés para una cédula específica.
4. **Cómputo Total General:** Realiza el cálculo del puntaje transformado consolidado (Intralaboral + Extralaboral) aplicando factores de escala específicos para la Forma A (616) o Forma B (512).

---

## 2. Gestión de Datos Dinámicos

El sistema procesa la información de manera dinámica sin necesidad de una base de datos relacional pesada, utilizando estructuras JSON eficientes para:
- **Respuestas Crudas:** Salvadas tal como se reciben del formulario.
- **Baremos Configurables:** El archivo `baremos.json` permite actualizar los puntos de corte de riesgo sin modificar el código.
- **Metadatos de Seguimiento:** Fecha de cálculo, versión de baremos y forma aplicada se guardan con cada análisis.

## 3. Análisis Grupal y Segmentación

El sistema permite realizar análisis complejos sobre subgrupos de la población mediante filtros dinámicos.

### Filtros Soportados
- **Área:** Comparativa entre departamentos (Ej: Operaciones vs. Administrativo).
- **Cargo:** Identificación de riesgos específicos por nivel ocupacional.
- **Sexo:** Análisis de impacto diferenciado por género.

### Metodología de Agregación
1. **Filtrado:** Se seleccionan las cédulas que cumplen con los criterios.
2. **Cálculo Recursivo:** Se ejecuta el análisis individual para cada integrante del grupo.
3. **Estadísticas Agregadas:** Se computan medias, desviaciones (opcional) y distribuciones porcentuales de niveles de riesgo.
4. **Ranking de Dimensiones:** Ranking automatizado de las dimensiones con mayor riesgo promedio en el segmento seleccionado.

## 4. Análisis de Dominios Estratégicos

El servicio incluye funciones especializadas para analizar dominios de alta relevancia organizacional:

- **Desglose de Liderazgo:** Análisis detallado de las dimensiones del dominio "Liderazgo y Relaciones Sociales" desglosado por áreas.
- **Análisis de Demandas:** Vista granular de las demandas emocionales, cuantitativas y de carga mental por tipo de cargo.
- **Control sobre el trabajo:** Evaluación de la autonomía y participación en la toma de decisiones.

## 5. Integración API

El servicio expone sus capacidades a través de los siguientes endpoints (referencia):
- `GET /analisis/{cedula}`: Análisis completo individual.
- `GET /analisis-grupal`: Análisis agregado con filtros (query params).
- `GET /baremos`: Consulta de la configuración actual de baremos.
- `PUT /baremos`: Actualización dinámica de tablas normativas.
