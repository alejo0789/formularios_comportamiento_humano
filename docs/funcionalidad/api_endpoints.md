# Documentación de la API (Backend)

El backend está construido con **FastAPI** y se organiza en el módulo de análisis psicosocial. Todos los endpoints tienen el prefijo `/api/analisis`.

## 📌 Endpoints Individuales

### 1. Obtener Análisis Individual
`GET /api/analisis/{cedula}`
- **Descripción:** Calcula y retorna el análisis completo de un respondente.
- **Respuesta Exitosa (200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "nombre": "Juan Pérez",
      "cuestionarios": {
        "estres": { ... },
        "intralaboral": { ... }
      },
      "total_general": { ... }
    }
  }
  ```

### 2. Descargar Reporte PDF Individual
`GET /api/analisis/{cedula}/reporte-pdf`
- **Descripción:** Genera un PDF profesional con los resultados del respondente.
- **Respuesta:** Stream de datos (`application/pdf`).

---

## 👥 Endpoints Grupales

### 3. Resumen Grupal
`GET /api/analisis/grupo/resumen`
- **Query Params (Opcionales):** `area`, `cargo`, `sexo`.
- **Descripción:** Retorna estadísticas agregadas y distribución de riesgo para el grupo seleccionado.

### 4. Ranking de Dimensiones
`GET /api/analisis/grupo/ranking-dimensiones`
- **Descripción:** Retorna el Top 10 de dimensiones con mayor riesgo promedio.

### 5. Descargar Reporte PDF Grupal
`POST /api/analisis/grupo/reporte-pdf`
- **Descripción:** Genera un PDF detallado con el análisis de clima y riesgo del grupo/segmento.

---

## ⚙️ Gestión de Baremos

### 6. Consultar Baremos Actuales
`GET /api/analisis/baremos/actual`

### 7. Actualizar Baremos
`PUT /api/analisis/baremos/actualizar`
- **Body:** `{ "baremos": { ... } }`
- **Descripción:** Permite modificar los puntos de corte de riesgo sin reiniciar el servidor.

### 8. Recargar Baremos
`POST /api/analisis/baremos/recargar`
- **Descripción:** Sincroniza el estado en memoria con el archivo `baremos.json`.

---

## 🛠️ Tecnologías Backend
- **Framework:** FastAPI.
- **Servicio:** `AnalysisService` califica en tiempo real.
- **Reportes:** `ReportGenerator` usa Playwright para renderizado PDF.
- **Validación:** Pydantic para modelos de datos.
