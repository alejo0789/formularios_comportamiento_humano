# Documentación del Proyecto - Análisis Psicosocial

Bienvenido a la documentación técnica y funcional del proyecto de Análisis de Factores de Riesgo Psicosocial. Esta documentación está diseñada para ayudar tanto a desarrolladores como a analistas de talento humano a comprender y extender el sistema.

---

## 📁 Guía de Navegación

### 🏛️ Arquitectura y Normativa
- [Análisis de Manuales y Requerimientos](arquitectura/analisis_y_requerimientos.md): Base normativa de MinTrabajo, requerimientos funcionales y criterios de aceptación.
- [Modelo de Datos y Persistencia](arquitectura/modelo_de_datos.md): Esquemas JSON, baremos dinámicos y persistencia de las respuestas.

### ⚙️ Funcionalidad y Backend
- [Generación de Reportes](funcionalidad/generacion_reportes.md): Detalles sobre la exportación a PDF, diseño de dashboards y visualización de riesgo.
- [Análisis Dinámico e Información](funcionalidad/analisis_dinamico_y_informacion.md): Lógica del `AnalysisService`, segmentación grupal y gestión de baremos dinámicos.
- [API Endpoints](funcionalidad/api_endpoints.md): Referencia completa de los endpoints disponibles en el backend (FastAPI).

### 🎨 Frontend y Experiencia de Usuario
- [Frontend y Estética](funcionalidad/frontend_y_estetica.md): Arquitectura del chat conversacional, estilo visual premium y manejo del estado.

### 🚀 Despliegue y Operación
- [Guía de Inicio Rápido](despliegue/guia_de_inicio.md): Instalación de dependencias (Python, Playwright) y puesta en marcha del servidor.

---

## 🛠️ Tecnologías Utilizadas
- **Backend:** Python 3.10+, FastAPI.
- **Análisis:** Motor de calificación propio (`ScoringEngine`).
- **Reportes:** Playwright (Chromium), Jinja2, CSS3.
- **Persistencia:** Estructuras JSON optimizadas para datos dinámicos.

## 👥 Roles de Usuario
- **Administrador:** Gestión de baremos y visualización de reportes grupales.
- **Analista / Profesional:** Visualización de análisis individuales por cédula.
- **Respondente:** Trabajador que completa los cuestionarios (vía frontend o chat).

---

> [!TIP]
> **Privacidad:** La aplicación cumple con la Ley 1581 (Habeas Data) al procesar toda la información de manera local y segura. No se envían datos sensibles a servicios externos.

