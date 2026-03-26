# Modelo de Datos y Persistencia

El sistema de Análisis Psicosocial utiliza un modelo de persistencia basado en archivos JSON para manejar la configuración estructural y los datos dinámicos.

## 1. La Estructura de Baremos (`baremos.json`)

`baremos.json` es el centro de la inteligencia del sistema. Define los puntos de corte por niveles de riesgo para cada cuestionario, dominio y dimensión.

### Ejemplo de Estructura:
```json
{
  "version": "1.0",
  "actualizado": "2024-03-17",
  "estres": {
    "forma_a": {
        "Muy Alto": 100,
        "Alto": 45.4,
        "Medio": 21,
        "Bajo": 11,
        "Sin Riesgo": 7.8
    },
    ...
  },
  "intralaboral": {
    "A": {
        "dominios": {
             "Control sobre el trabajo": {
                "puntos_de_corte": [7.8, 17.2, 28.1, 40.6],
                "niveles": ["Sin Riesgo", "Bajo", "Medio", "Alto", "Muy Alto"]
             }
        }
    }
  }
}
```

## 2. Los Datos de los Respondentes

Ubicación: `backend/data/`

### Ficha de Datos Generales (`form_datos-generales.json`):
Contiene la información sociodemográfica recolectada en la primera fase del cuestionario.
- `numero_identificacion`: Cédula (Llave primaria lógica).
- `nombre_completo`: Nombre del trabajador.
- `tipo_cargo`: Fundamental para determinar el baremo de estrés.
- `tiene_personal_cargo`: Determina si aplica Forma A o B automáticamente.

### Cuestionarios de Respuestas:
- `responses_estres.json`
- `responses_extralaborales.json`
- `responses_intralaborales-a.json`
- `responses_intralaborales-b.json`

Cada archivo guarda la serie de respuestas en el formato:
```json
{
  "submission_id": "GUID",
  "respondent_cedula": "12345678",
  "submitted_at": "ISO-TIMESTAMP",
  "responses": {
    "1": 3,
    "2": 5,
    ...
  }
}
```

---

## 3. Seguridad y Privacidad (Habeas Data)

La información recolectada se procesa siguiendo la Ley 1581 de 2012 de Colombia:
- **Almacenamiento Local:** Los datos no se envían a APIs de terceros durante el procesamiento.
- **Acceso Restringido:** El backend solo permite el acceso a datos individuales mediante consultas por cédula específica.
- **Auditoría:** Se recomienda implementar logs de acceso (Middleware) para producciones a gran escala.

---

## 4. Estructura de Dimensiones (Backend)

El motor utiliza diccionarios de mapeo (`PsychosocialScoringEngine`) para asociar el número de ítem con la dimensión que evalúa y su tipo de escala (directa/inversa). Esto permite una calificación rápida y precisa sin necesidad de consultas SQL constantes.
