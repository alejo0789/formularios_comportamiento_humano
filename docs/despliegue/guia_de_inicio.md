# Guía de Inicio y Despliegue

Sigue esta guía para configurar el entorno de desarrollo y poner en marcha el proyecto de Análisis Psicosocial.

## 1. Requisitos del Sistema

- **Lenguaje:** Python 3.10+ (Recomendado 3.11).
- **Entorno Virtual:** Se recomienda el uso de `venv` para aislar las dependencias.
- **Navegador:** Chromium (para la generación de reportes PDF).

---

## 2. Instalación Paso a Paso

### Paso 1: Clonar y Preparar el Entorno
```powershell
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual (PowerShell)
.\venv\Scripts\Activate.ps1
```

### Paso 2: Instalar Dependencias del Backend
```bash
pip install -r backend/requirements.txt
```

### Paso 3: Configurar Playwright
Es necesario instalar las binarias de Chromium para que el generador de reportes PDF funcione:
```bash
playwright install chromium
```

---

## 3. Ejecución en Desarrollo

Para iniciar el servidor backend (FastAPI):
```bash
uvicorn app.main:app --reload --port 8000
```

### Acceso a la Interfaz:
- **Frontend:** Abre `docs/index.html` (o sirve la carpeta con un Live Server).
- **Documentación API (Swagger):** `http://localhost:8000/docs`
- **Análisis por Cédula (Ejemplo):** `http://localhost:8000/api/analisis/12345678`

---

## 4. Estructura de Carpetas

```text
/
├── backend/            # Lógica central del sistema
│   ├── analisis/       # Módulo psicosocial (Cálculos, Reportes, API)
│   ├── data/           # Repositorio de respuestas y ficha técnica (JSON)
│   └── main.py         # Punto de entrada de la aplicación FastAPI
├── frontend/           # Interfaces de usuario y chat conversacional
├── docs/               # Documentación técnica y funcional (Markdown)
└── README.md           # Descripción general del repositorio
```

---

## 5. Pruebas y Validación

Para asegurar que los cálculos de riesgo psicosocial sean correctos, el motor de calificación tiene una suite de pruebas incorporada.

### Ejecutar Pruebas Unitarias:
```bash
pytest backend/analisis/tests/
```
Esto validará la calificación automática de los cuestionarios Intra, Extra y Estrés contra los resultados esperados de los manuales.

---

## 6. Próximos pasos
- **Integración Azure:** Configuración de las variables de entorno para la comunicación con servicios cloud.
- **WhatsApp Bot:** Configuración de Webhooks para la captura automatizada de datos por mensajería instantánea.
