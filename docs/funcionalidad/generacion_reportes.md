# Módulo de Generación de Reportes

El módulo de reportes es responsable de transformar los datos analizados en documentos visuales de alta calidad en formatos HTML y PDF.

## 1. Arquitectura del Generador

El generador de reportes se basa en el componente `ReportGenerator`, el cual utiliza las siguientes tecnologías:
- **Jinja2 (Lógica de Plantillas):** Para la construcción dinámica de las secciones PDF desde plantillas base.
- **Playwright (Motor de Exportación):** Utiliza un navegador Chromium embebido para renderizar el HTML y exportarlo a PDF con precisión tipográfica.
- **CSS3 Moderno:** Utiliza Flexbox y Grid para el diseño de los dashboards e indicadores visuales.

## 2. Reporte Individual

El reporte individual se genera para cada respondente y consta de las siguientes secciones:

### Estructura del Documento
- **Portada:** Datos básicos del trabajador (Nombre, Cédula, Cargo, Área).
- **Resumen Ejecutivo:** Tabla general con puntaje y nivel de riesgo por cada cuestionario.
- **Detalle de Cuestionarios:**
    - **Estrés:** Desglose del cálculo por bloques y niveles de estrés.
    - **Intralaboral (A o B):** Detalle por dominios y dimensiones con progreso visual.
    - **Extralaboral:** Desglose de las 7 dimensiones externas.
- **Pie de Página:** Cumplimiento de Ley 1581 (Habeas Data) y versión de baremos utilizada.

### Visualización de Riesgo
| Nivel | Color | Descripción Visual |
| :--- | :--- | :--- |
| **Muy Alto** | Morado (#8e44ad) | Requiere intervención inmediata. |
| **Alto** | Rojo (#e74c3c) | Requiere intervención prioritaria. |
| **Medio** | Naranja (#f39c12) | Indica riesgo que debe monitorearse. |
| **Bajo / Sin Riesgo** | Verde (#27ae60) | Niveles aceptables de exposición. |

---

## 3. Reporte Grupal

El reporte grupal permite el análisis de grandes grupos de población y segmentos específicos de la organización.

### Componentes Clave
1. **Caracterización Demográfica:** Distribución por sexo, área, cargo, nivel de estudios y antigüedad.
2. **Distribución de Riesgo:** Gráficas que muestran el porcentaje de población en cada nivel de riesgo para Intra, Extra y Estrés.
3. **Ranking de Dimensiones:** Lista de las 10 dimensiones con mayor riesgo (puntajes promedios más altos), permitiendo identificar focos de intervención.
4. **Desgloses Especializados:**
    - **Liderazgo:** Comparativa por área y tipo de cargo.
    - **Demandas:** Identificación de áreas con mayor carga mental o jornada extensa.
    - **Control:** Evaluación de la autonomía por cargos.

## 4. Uso Técnico

El generador se invoca desde el `AnalysisService` o directamente desde el router API:

```python
from backend.analisis.report_generator import ReportGenerator

generator = ReportGenerator()
pdf_bytes = await generator.generate_individual_pdf(analysis_data)
# Los bytes pueden enviarse como respuesta HTTP (StreamingResponse)
```
